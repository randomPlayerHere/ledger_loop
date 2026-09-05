"""Stage 2: LLM adjudication on the residual.

Reached only by transactions the rules could not explain, and only when
blocking left something to choose from. The easy cases never arrive here, so
everything this module sees is, by construction, a judgement call.

Layering, which is the point of the file:

    build_prompt / validate_response   pure -- data in, data out, no socket
    LLMClient (Groq, Anthropic)        the only code that touches the wire
    Adjudicator                        cache + client + validation + timeout

Every hard requirement in the spec is enforced in the pure layer, so every one
of them has a unit test that never opens a network connection. In particular
invariant 3 -- the model may only return invoice ids it was shown -- is a
function of two arguments, not a property of a live API call.

The provider is a config key. `LLMClient` is two methods wide on purpose: a
reconciliation request is one system prompt, one user prompt, and one JSON
object back, and nothing about that needs a provider-specific abstraction.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Callable, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from .config import Config, LLMConfig
from .models import (BankTransaction, Candidate, CandidateGroup, LedgerEntry,
                     RuleResult)

logger = logging.getLogger(__name__)

# Bumping this invalidates every cached answer. Change it whenever the prompt
# changes in a way that could change a verdict -- a cache hit against an old
# prompt is a stale answer wearing a fresh timestamp.
PROMPT_VERSION = "v1"

RULE_ID = "LLM_ADJUDICATION"

# --------------------------------------------------------------------------
# Violations. Each one forces EXCEPTION; none of them is ever recovered from
# by guessing. The distinction is kept because they mean different things to
# whoever reads the queue: a hallucination is a model failure, a timeout is an
# infrastructure failure, and the reviewer's next move differs.
# --------------------------------------------------------------------------

HALLUCINATED_ID = "HALLUCINATED_ID"
MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
DUPLICATE_ID = "DUPLICATE_ID"
ALLOCATION_MISMATCH = "ALLOCATION_MISMATCH"
ALLOCATION_INVALID = "ALLOCATION_INVALID"
OVER_ALLOCATED = "OVER_ALLOCATED"
CONFIDENCE_RANGE = "CONFIDENCE_OUT_OF_RANGE"
LLM_TIMEOUT = "TIMEOUT"
API_ERROR = "API_ERROR"
SCHEMA_UNSATISFIED = "SCHEMA_UNSATISFIED"

_VIOLATION_TEXT = {
    HALLUCINATED_ID: "Model proposed an invoice outside the candidate list; escalated.",
    MALFORMED_RESPONSE: "Model response did not match the required schema; escalated.",
    DUPLICATE_ID: "Model listed the same invoice twice; escalated.",
    ALLOCATION_MISMATCH: "Allocation did not cover exactly the invoices selected; escalated.",
    ALLOCATION_INVALID: "Allocation contained a non-positive or unparseable amount; escalated.",
    OVER_ALLOCATED: "Allocation exceeded the credit amount; escalated.",
    CONFIDENCE_RANGE: "Model returned a confidence outside 0-1; escalated.",
    LLM_TIMEOUT: "Adjudication timed out; escalated rather than guessed.",
    API_ERROR: "Adjudication call failed; escalated rather than guessed.",
    SCHEMA_UNSATISFIED: ("Model could not produce a valid answer within its "
                         "token budget; escalated."),
}


# --------------------------------------------------------------------------
# The response contract
# --------------------------------------------------------------------------

class _Allocation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invoice_id: str
    # A string, not a number. JSON numbers arrive as float, and this project
    # does not let float touch money even for the length of one parse.
    amount: str


class _Adjudication(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invoice_ids: list[str]
    allocations: list[_Allocation]
    confidence: float
    reasoning: str


# Mirrors _Adjudication. Written out rather than generated from the model
# because strict mode has requirements pydantic's exporter does not meet
# (every property required, additionalProperties false, no $defs indirection),
# and a schema the provider silently rejects is worse than a duplicated one.
# `allocations` is a list of pairs rather than an object keyed by invoice id
# for the same reason: strict mode forbids free-form object keys.
RESPONSE_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["invoice_ids", "allocations", "confidence", "reasoning"],
    "properties": {
        "invoice_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Invoice ids settled by this credit, from the candidate list only. Empty if none fit.",
        },
        "allocations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["invoice_id", "amount"],
                "properties": {
                    "invoice_id": {"type": "string"},
                    "amount": {"type": "string", "description": "Rupees, decimal digits only, e.g. 41250.00"},
                },
            },
            "description": "One entry per selected invoice. Empty if invoice_ids is empty.",
        },
        "confidence": {"type": "number", "description": "0.0-1.0, your probability the whole answer is correct."},
        "reasoning": {"type": "string", "description": "One sentence naming the evidence used."},
    },
}


SYSTEM_PROMPT = """\
You reconcile bank credits against open sales invoices for an Indian business.

A deterministic rule engine has already tried this payment and could not \
explain it. You are the second opinion, never the first: every easy case was \
settled before it reached you.

Decide which invoice, or which set of invoices, this one credit settles.

Hard rules:
1. Choose only from the numbered candidate list. An invoice id that is not in \
that list does not exist. There is no other ledger.
2. A short payment is a match only when the shortfall has a named cause: TDS \
withheld at 2% or 10% of invoice gross, or bank charges of at most max(Rs 50, \
0.5% of gross). A gap you cannot name is not a match.
3. When two different answers fit equally well, return an empty invoice list. \
Ambiguity goes to a human. A missed match costs somebody two minutes; a wrong \
match posts real money to the wrong account.
4. Allocations must be positive, must name exactly the invoices you selected, \
and must sum to no more than the credit amount.
5. `confidence` is your own probability that the entire answer is correct, not \
how plausible the best option looked relative to the others.
6. `reasoning` is one sentence naming the evidence you actually used -- the \
invoice number in the narration, the counterparty name, the exact TDS \
arithmetic. Do not restate the rules.

Returning an empty invoice list is a correct and expected answer whenever \
nothing in the list convincingly explains the credit. Roughly a third of what \
reaches you is a duplicate credit, a refund, or a payment against an invoice \
that was never raised."""


def _money(d: Decimal) -> str:
    return f"{d:,.2f}"


# "Rs 60,232.20" -- the shape a model echoes back because it is the shape the
# prompt uses. Anchored, and the remainder after the prefix must be a bare
# decimal, so this normalises presentation without loosening what counts as a
# number: "about four thousand" and "-500" still fail.
_MONEY_RE = re.compile(r"^(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)$", re.IGNORECASE)


def parse_money(raw: str) -> Decimal | None:
    """Decimal from a model-written amount, or None if it is not a number.

    Tolerating the currency prefix and the thousands separators is not leniency
    about the value -- it is refusing to throw away a correct answer over
    formatting the prompt itself taught the model to use. Measured on batch_dev:
    7 of the first 26 adjudications were correct matches discarded on exactly
    this, which is the difference between Stage 2 earning its place and not.
    """
    if not isinstance(raw, str):
        return None
    m = _MONEY_RE.match(raw.strip().replace(",", ""))
    return Decimal(m.group(1)) if m else None


def select_shown(candidates: list[Candidate], groups: list[CandidateGroup],
                 cfg: LLMConfig) -> tuple[list[Candidate], list[CandidateGroup]]:
    """Top-k cut of both shortlists. Both arrive ranked from Stage 0."""
    return candidates[: cfg.max_candidates], groups[: cfg.max_groups]


def shown_ids(candidates: list[Candidate], groups: list[CandidateGroup]) -> list[str]:
    """Every invoice id the model was shown, in display order, deduplicated.

    This -- not the full blocking shortlist -- is what invariant 3 validates
    against. The model cannot be held to a list it was never given, and must
    not be let off one it was.
    """
    out: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if c.invoice.invoice_id not in seen:
            seen.add(c.invoice.invoice_id)
            out.append(c.invoice.invoice_id)
    for g in groups:
        for inv in g.invoices:
            if inv.invoice_id not in seen:
                seen.add(inv.invoice_id)
                out.append(inv.invoice_id)
    return out


def _invoice_line(inv: LedgerEntry, txn: BankTransaction,
                  ns: float | None, ref_hit: bool | None,
                  shortfall: str | None) -> str:
    delta = txn.amount - inv.gross_amount
    gap = (txn.value_date - inv.issue_date).days
    bits = [
        f"{inv.invoice_id}",
        f"{inv.counterparty}",
        f"gross Rs {_money(inv.gross_amount)}",
        f"delta Rs {_money(delta)}",
        f"issued {inv.issue_date} ({gap:+d}d)",
        f"due {inv.due_date}",
        inv.status,
    ]
    if inv.tds_applicable:
        bits.append(f"TDS {inv.tds_rate:%} applicable")
    if ns is not None:
        bits.append(f"name match {ns:.0f}/100")
    if ref_hit:
        bits.append("INVOICE NUMBER QUOTED IN NARRATION")
    if shortfall:
        bits.append(f"gap explained by {shortfall}")
    return " | ".join(bits)


def build_prompt(txn: BankTransaction, candidates: list[Candidate],
                 groups: list[CandidateGroup]) -> str:
    """The user half of the request. Pure; `candidates`/`groups` are already cut.

    Deliberately dense. On a free-tier key the binding constraint is tokens per
    minute, not intelligence, and every field here has to earn its place by
    being something the model cannot derive from the others.
    """
    lines = [
        "BANK CREDIT",
        f"  id        {txn.txn_id}",
        f"  amount    Rs {_money(txn.amount)} {txn.direction}",
        f"  date      {txn.value_date}",
        f"  narration {txn.narration}",
        f"  utr       {txn.utr or '-'}",
        "",
        f"CANDIDATE INVOICES ({len(candidates)}) -- the only ids you may return:",
    ]
    if candidates:
        for i, c in enumerate(candidates, 1):
            lines.append(f"  {i}. " + _invoice_line(
                c.invoice, txn, c.name_similarity, c.ref_hit, c.shortfall))
    else:
        lines.append("  (none individually)")

    if groups:
        lines += [
            "",
            "COMBINATIONS that sum to the credit exactly (one payment settling "
            "several invoices):",
        ]
        for i, g in enumerate(groups, 1):
            members = ", ".join(inv.invoice_id for inv in g.invoices)
            lines.append(
                f"  {chr(64 + i)}. {members} -- total Rs {_money(g.total)}, "
                f"same counterparty, name match {g.name_similarity:.0f}/100"
                + (f", numbers quoted: {', '.join(g.ref_hits)}" if g.ref_hits else "")
            )
            for inv in g.invoices:
                lines.append("       " + _invoice_line(inv, txn, None, None, None))

    lines += [
        "",
        "Which invoices does this credit settle? Return an empty list if the "
        "honest answer is that a human should look.",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Validation -- invariant 3 and its neighbours
# --------------------------------------------------------------------------

def validate_response(raw: str | dict, txn: BankTransaction,
                      allowed_ids: list[str], cfg: Config,
                      ) -> tuple[RuleResult | None, str | None, dict]:
    """Turn a model response into a RuleResult, or into a violation.

    Returns (result, violation, evidence).

      result    None on a violation, and also on a clean abstention
      violation one of the constants above, or None
      evidence  always populated -- what the model said and what we checked

    A violation never degrades into a lower-confidence match. There is no
    partial credit here: an answer that broke the contract is an answer we
    cannot reason about, and the transaction goes to a human.
    """
    allowed = set(allowed_ids)

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None, MALFORMED_RESPONSE, {"raw_response": str(raw)[:500]}
    try:
        adj = _Adjudication.model_validate(raw)
    except ValidationError as e:
        return None, MALFORMED_RESPONSE, {"raw_response": json.dumps(raw)[:500],
                                          "schema_error": e.errors()[0]["msg"]}

    evidence: dict = {
        "llm_confidence_raw": adj.confidence,
        "llm_reasoning": adj.reasoning.strip(),
        "candidates_shown": allowed_ids,
        "llm_selected": adj.invoice_ids,
    }

    if not 0.0 <= adj.confidence <= 1.0:
        return None, CONFIDENCE_RANGE, evidence

    # Invariant 3. Checked before anything else about the answer's content,
    # because an id we did not show is not a wrong answer -- it is a fabricated
    # one, and the two must never be logged as the same kind of miss.
    invented = [i for i in adj.invoice_ids if i not in allowed]
    if invented:
        evidence["hallucinated_ids"] = invented
        logger.error("llm returned ids outside the candidate list",
                     extra={"txn_id": txn.txn_id, "invented": invented,
                            "shown": allowed_ids})
        return None, HALLUCINATED_ID, evidence

    if len(set(adj.invoice_ids)) != len(adj.invoice_ids):
        return None, DUPLICATE_ID, evidence

    # Clean abstention: nothing fit, and the model said so. Invariant 5 --
    # this is correct behaviour, not a failure, so it carries no violation.
    if not adj.invoice_ids:
        evidence["abstained"] = True
        return None, None, evidence

    alloc_ids = [a.invoice_id for a in adj.allocations]
    if set(alloc_ids) != set(adj.invoice_ids) or len(alloc_ids) != len(set(alloc_ids)):
        evidence["llm_allocated"] = alloc_ids
        return None, ALLOCATION_MISMATCH, evidence

    allocated: dict[str, Decimal] = {}
    for a in adj.allocations:
        amt = parse_money(a.amount)
        if amt is None or amt <= 0:
            evidence["bad_amount"] = a.amount
            return None, ALLOCATION_INVALID, evidence
        allocated[a.invoice_id] = amt

    total = sum(allocated.values(), Decimal("0"))
    if total > txn.amount + cfg.tolerances.amount_exact:
        evidence["total_allocated"] = total
        return None, OVER_ALLOCATED, evidence

    # The ceiling, applied here rather than in the engine so that no path
    # exists by which an unmoderated self-reported number reaches routing.
    confidence = min(adj.confidence, cfg.llm.confidence_ceiling)

    evidence.update({
        "amount_delta": txn.amount - total,
        "total_allocated": total,
        "confidence_ceiling": cfg.llm.confidence_ceiling,
        "confidence_capped": confidence < adj.confidence,
    })

    return RuleResult(
        rule_id=RULE_ID,
        invoice_ids=adj.invoice_ids,
        allocated=allocated,
        confidence=confidence,
        reasoning=adj.reasoning.strip(),
        evidence=evidence,
    ), None, evidence


# --------------------------------------------------------------------------
# Clients -- the only code here that touches the network
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Completion:
    text: str
    tokens_in: int
    tokens_out: int


class LLMTimeout(Exception):
    """Raised by a client when the provider did not answer in time."""


class LLMSchemaFailure(Exception):
    """The provider refused the response because it did not satisfy the schema.

    Under strict structured output this is what a completion budget running out
    mid-object looks like: not a truncated answer we could inspect, but a 400
    with nothing in it. Kept separate from a generic API error because the two
    have different fixes -- this one is llm.max_tokens, and a run that reports
    it as "the API failed" sends you looking at the network instead.
    """


class LLMUnavailable(Exception):
    """A setup failure, not a transaction failure -- a rejected key, a model the
    account cannot reach, an exhausted quota.

    Deliberately not caught by the adjudicator. A bad key applied per
    transaction turns into a hundred plausible-looking EXCEPTION records and a
    report that reads like a hard batch instead of a broken run. The whole
    point of the exception queue is that entries in it are real; anything that
    would fail identically for every transaction has to stop the run.
    """


class LLMClient(Protocol):
    """Two methods wide. Anything a provider needs beyond this belongs in
    config.yaml, not in a subclass hierarchy."""

    name: str

    def complete(self, system: str, user: str, schema: dict) -> Completion: ...


class GroqClient:
    """GroqCloud via the official SDK.

    Uses strict JSON-schema structured output, which is why the model in
    config.yaml is one of the few Groq serves that supports it: strict mode
    turns "the model wrote prose instead of JSON" from a runtime exception
    queue entry into a request the provider refuses to complete.
    """

    name = "groq"

    def __init__(self, cfg: Config):
        try:
            from groq import Groq  # noqa: PLC0415 -- optional dep, imported on use
        except ImportError as e:
            raise RuntimeError(
                "provider 'groq' needs the groq package -- run `uv sync`"
            ) from e

        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and fill it "
                "in, or run with --no-llm."
            )
        self._p = cfg.llm.active
        self._cfg = cfg.llm
        self._client = Groq(api_key=key, timeout=float(cfg.exceptions.llm_timeout),
                            max_retries=cfg.llm.max_retries)

    def complete(self, system: str, user: str, schema: dict) -> Completion:
        import groq  # noqa: PLC0415

        kwargs = {
            "model": self._p.model,
            "temperature": self._cfg.temperature,
            "max_tokens": self._p.max_tokens or self._cfg.max_tokens,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "adjudication", "strict": True,
                                "schema": schema},
            },
        }
        if self._p.reasoning_effort:
            kwargs["reasoning_effort"] = self._p.reasoning_effort

        try:
            resp = self._client.chat.completions.create(**kwargs)
        except groq.APITimeoutError as e:
            raise LLMTimeout(str(e)) from e
        except (groq.AuthenticationError, groq.PermissionDeniedError,
                groq.NotFoundError) as e:
            raise LLMUnavailable(f"{type(e).__name__}: {e}") from e
        except groq.BadRequestError as e:
            if "json_validate_failed" in str(e):
                raise LLMSchemaFailure(str(e)[:300]) from e
            raise
        except groq.RateLimitError as e:
            # Reached only after max_retries of backoff, which means a daily
            # quota rather than a minute's throttling. Every remaining
            # transaction would fail the same way, so this stops the run
            # instead of writing four hundred fabricated exceptions.
            raise LLMUnavailable(
                f"rate limit not cleared after {self._cfg.max_retries} retries "
                f"-- likely a daily token quota: {e}") from e

        usage = resp.usage
        return Completion(
            text=resp.choices[0].message.content or "",
            tokens_in=getattr(usage, "prompt_tokens", 0) or 0,
            tokens_out=getattr(usage, "completion_tokens", 0) or 0,
        )


class NIMClient:
    """NVIDIA's hosted NIM catalogue, via its OpenAI-compatible endpoint.

    Schema enforcement uses the same strict `response_format` as the Groq
    client. NVIDIA's own documentation points at the `nvext.guided_json`
    extension instead, and that is correct for a self-hosted NIM container --
    but measured against the hosted catalogue it is silently ignored: the model
    invents its own field names (`invoices` for `invoice_ids`, an `allocation`
    number where the schema says a string) and every answer dies in the
    validator as MALFORMED. The OpenAI-shaped form is honoured exactly. Left as
    a comment because the documentation will keep suggesting otherwise.
    """

    name = "nim"
    BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(self, cfg: Config):
        try:
            from openai import OpenAI  # noqa: PLC0415
        except ImportError as e:
            raise RuntimeError(
                "provider 'nim' needs the openai package -- run `uv sync`"
            ) from e

        key = os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise RuntimeError(
                "NVIDIA_API_KEY is not set. Get one free at build.nvidia.com, "
                "put it in .env, or run with --no-llm."
            )
        self._p = cfg.llm.active
        self._cfg = cfg.llm
        self._client = OpenAI(api_key=key, base_url=self.BASE_URL,
                              timeout=float(cfg.exceptions.llm_timeout),
                              max_retries=cfg.llm.max_retries)

    def complete(self, system: str, user: str, schema: dict) -> Completion:
        import openai  # noqa: PLC0415

        kwargs = {
            "model": self._p.model,
            "temperature": self._cfg.temperature,
            "max_tokens": self._p.max_tokens or self._cfg.max_tokens,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "adjudication", "strict": True,
                                "schema": schema},
            },
        }
        if self._p.reasoning_effort:
            # extra_body merges into the request body top level, which is where
            # the catalogue expects it -- not nested under nvext.
            kwargs["extra_body"] = {"reasoning_effort": self._p.reasoning_effort}

        try:
            resp = self._client.chat.completions.create(**kwargs)
        except openai.APITimeoutError as e:
            raise LLMTimeout(str(e)) from e
        except (openai.AuthenticationError, openai.PermissionDeniedError,
                openai.NotFoundError) as e:
            raise LLMUnavailable(f"{type(e).__name__}: {e}") from e
        except openai.RateLimitError as e:
            raise LLMUnavailable(
                f"rate limit not cleared after {self._cfg.max_retries} retries "
                f"-- likely an exhausted credit balance: {e}") from e

        usage = resp.usage
        return Completion(
            text=_strip_fences(resp.choices[0].message.content or ""),
            tokens_in=getattr(usage, "prompt_tokens", 0) or 0,
            tokens_out=getattr(usage, "completion_tokens", 0) or 0,
        )


class AnthropicClient:
    """The quality-ceiling comparison path.

    No `temperature`: current Claude models reject sampling parameters, and the
    determinism this project wants from temperature 0 comes from the cache and
    the validator, not from the decoder.
    """

    name = "anthropic"

    def __init__(self, cfg: Config):
        try:
            import anthropic  # noqa: PLC0415
        except ImportError as e:
            raise RuntimeError(
                "provider 'anthropic' needs the anthropic package -- run "
                "`uv sync --extra anthropic`"
            ) from e

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set. See .env.example.")
        self._p = cfg.llm.active
        self._cfg = cfg.llm
        self._client = anthropic.Anthropic(
            timeout=float(cfg.exceptions.llm_timeout), max_retries=1)

    def complete(self, system: str, user: str, schema: dict) -> Completion:
        import anthropic  # noqa: PLC0415

        instruction = (
            f"{user}\n\nReply with a single JSON object and nothing else, "
            f"matching this schema exactly:\n{json.dumps(schema)}"
        )
        try:
            resp = self._client.messages.create(
                model=self._p.model,
                max_tokens=self._p.max_tokens or self._cfg.max_tokens,
                system=system,
                messages=[{"role": "user", "content": instruction}],
            )
        except anthropic.APITimeoutError as e:
            raise LLMTimeout(str(e)) from e
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError,
                anthropic.NotFoundError) as e:
            raise LLMUnavailable(f"{type(e).__name__}: {e}") from e

        text = "".join(b.text for b in resp.content if b.type == "text")
        return Completion(text=_strip_fences(text),
                          tokens_in=resp.usage.input_tokens,
                          tokens_out=resp.usage.output_tokens)


def _strip_fences(text: str) -> str:
    """Peel a ```json fence if the model added one. Not a parser -- if this
    leaves anything that is not JSON, the validator says MALFORMED and the
    transaction is escalated, which is the correct outcome."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


CLIENTS = {"groq": GroqClient, "nim": NIMClient, "anthropic": AnthropicClient}


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------

def cache_key(txn: BankTransaction, allowed_ids: list[str], cfg: Config) -> str:
    """Identity of a question, not of a run.

    The candidate ids are sorted: the same shortlist in a different order is
    the same question. The model and prompt version are included because the
    same question asked of a different model is not the same answer, and a
    cache that pretends otherwise silently reports one model's numbers under
    another model's name.
    """
    payload = json.dumps({
        "prompt": PROMPT_VERSION,
        "provider": cfg.llm.provider,
        "model": cfg.llm.active.model,
        "txn": txn.txn_id,
        "amount": str(txn.amount),
        "candidates": sorted(allowed_ids),
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class ResponseCache:
    """One JSON file per question, under llm.cache_dir.

    A directory of files rather than a database because the cache is also a
    debugging artefact: when a verdict looks wrong, the exact response that
    produced it is one `cat` away.
    """

    def __init__(self, directory: Path):
        self.dir = directory
        self.dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Completion | None:
        path = self.dir / f"{key}.json"
        if not path.exists():
            return None
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            return Completion(d["text"], d["tokens_in"], d["tokens_out"])
        except (json.JSONDecodeError, KeyError):
            logger.warning("discarding unreadable cache entry",
                           extra={"path": str(path)})
            return None

    def put(self, key: str, completion: Completion, meta: dict) -> None:
        (self.dir / f"{key}.json").write_text(json.dumps({
            "text": completion.text,
            "tokens_in": completion.tokens_in,
            "tokens_out": completion.tokens_out,
            **meta,
        }, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# Adjudicator
# --------------------------------------------------------------------------

@dataclass
class Verdict:
    """What Stage 2 hands back to the engine."""
    result: RuleResult | None
    violation: str | None
    evidence: dict
    tokens_in: int | None = None
    tokens_out: int | None = None
    cached: bool = False

    @property
    def forced(self) -> tuple[str, str] | None:
        """(outcome, reasoning) when the engine must not route on confidence.

        A violation is an EXCEPTION whatever the model claimed. A clean
        abstention is also an EXCEPTION, but carries the model's own sentence,
        because the reviewer's first question is always "why is this here".
        """
        if self.violation:
            return "EXCEPTION", _VIOLATION_TEXT[self.violation]
        if self.result is None:
            return "EXCEPTION", self.evidence.get(
                "llm_reasoning", "Model found no convincing match; escalated.")
        return None


@dataclass
class Adjudicator:
    """Stage 2, wired: cache -> client -> validator.

    Holds counters rather than logging totals, so run.py can print a Stage 2
    line next to the metrics table and a cost figure can be reconciled against
    the number of calls that produced it.
    """
    cfg: Config
    client: LLMClient
    cache: ResponseCache | None = None
    # Called after each adjudication with (txn_id, verdict). Stage 2 over a
    # full batch runs for twenty minutes; a run that prints nothing for twenty
    # minutes is indistinguishable from one that has hung.
    on_progress: "Callable[[str, Verdict], None] | None" = None
    stats: dict = field(default_factory=lambda: {
        "calls": 0, "cache_hits": 0, "abstentions": 0,
        "violations": 0, "matched": 0,
    })
    violations: dict = field(default_factory=dict)

    def adjudicate(self, txn: BankTransaction, candidates: list[Candidate],
                   groups: list[CandidateGroup]) -> Verdict:
        shown_c, shown_g = select_shown(candidates, groups, self.cfg.llm)
        allowed = shown_ids(shown_c, shown_g)

        key = cache_key(txn, allowed, self.cfg)
        completion = self.cache.get(key) if self.cache else None
        cached = completion is not None

        if completion is None:
            user = build_prompt(txn, shown_c, shown_g)
            try:
                completion = self.client.complete(SYSTEM_PROMPT, user, RESPONSE_SCHEMA)
            except LLMTimeout:
                # Invariant: a timeout is an exception, never a guess.
                return self._count(Verdict(None, LLM_TIMEOUT,
                                           {"candidates_shown": allowed}),
                                   txn.txn_id)
            except LLMUnavailable:
                raise                                   # setup, not this txn
            except LLMSchemaFailure as e:
                logger.error("llm could not satisfy the response schema",
                             extra={"txn_id": txn.txn_id,
                                    "candidates": len(allowed),
                                    "max_tokens": self.cfg.llm.max_tokens,
                                    "error": str(e)})
                return self._count(Verdict(None, SCHEMA_UNSATISFIED,
                                           {"candidates_shown": allowed}),
                                   txn.txn_id)
            except Exception as e:                      # noqa: BLE001
                logger.error("llm call failed", extra={"txn_id": txn.txn_id,
                                                       "error": repr(e)})
                return self._count(Verdict(None, API_ERROR,
                                           {"candidates_shown": allowed,
                                            "error": repr(e)[:300]}),
                                   txn.txn_id)
            self.stats["calls"] += 1
            if self.cache:
                self.cache.put(key, completion, {
                    "txn_id": txn.txn_id, "candidates": allowed,
                    "model": self.cfg.llm.active.model,
                    "prompt_version": PROMPT_VERSION,
                    "cached_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
        else:
            self.stats["cache_hits"] += 1

        result, violation, evidence = validate_response(
            completion.text, txn, allowed, self.cfg)
        evidence["llm_cached"] = cached
        evidence["llm_model"] = self.cfg.llm.active.model

        return self._count(Verdict(result, violation, evidence,
                                   tokens_in=completion.tokens_in,
                                   tokens_out=completion.tokens_out,
                                   cached=cached), txn.txn_id)

    def _count(self, v: Verdict, txn_id: str = "") -> Verdict:
        if v.violation:
            self.stats["violations"] += 1
            self.violations[v.violation] = self.violations.get(v.violation, 0) + 1
        elif v.result is None:
            self.stats["abstentions"] += 1
        else:
            self.stats["matched"] += 1
        if self.on_progress is not None:
            self.on_progress(txn_id, v)
        return v


def build_adjudicator(cfg: Config) -> Adjudicator:
    """Construct Stage 2 from config. Raises with a usable message if the
    provider is unknown or its key is absent -- failing loudly beats a run that
    silently reports rules-only numbers under an LLM label."""
    provider = cfg.llm.provider
    if provider not in CLIENTS:
        raise ValueError(f"unknown llm.provider {provider!r}; "
                         f"known: {', '.join(sorted(CLIENTS))}")
    cfg.llm.active                      # raises early if the section is missing
    return Adjudicator(cfg=cfg,
                       client=CLIENTS[provider](cfg),
                       cache=ResponseCache(Path(cfg.llm.cache_dir)))
