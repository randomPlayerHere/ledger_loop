"""Stage 2b: the exception queue, written by the model.

This is the job the LLM keeps, and the reason it keeps it is measured rather
than assumed. Asked to *pick* an invoice from a shortlist it scored 0.432 and
0.556 against 0.994 for the rules (see config.yaml, `llm.adjudicate`). Asked to
*explain* a stuck credit it is doing the thing it is actually good at: reading
a mess of amounts, dates and half-legible narrations and saying, in a sentence
a human can act on, what this money probably is and what to do about it.

The safety property is structural, not a guard we had to write. Triage proposes
no invoice links and touches no MatchDecision, so it cannot move precision,
recall, or the auto-match rate in either direction. The worst a bad note can do
is waste a reviewer's attention -- which is why the note carries the evidence
that produced it, so the reviewer can see the model's working and disagree with
it.

Every note is attributable: the model that wrote it, the queue entry it
describes, and the fact that it is a suggestion rather than a decision. A note
is never the reason a rupee moved.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from .config import Config
from .llm import (CLIENTS, PROMPT_VERSION, Completion, LLMClient,
                  LLMSchemaFailure, LLMTimeout, LLMUnavailable, ResponseCache,
                  _strip_fences)
from .models import BankTransaction, LedgerEntry, MatchDecision

logger = logging.getLogger(__name__)

TRIAGE_VERSION = "t1"

# What a reviewer is actually allowed to do with a stuck credit. A closed set,
# because "suggested action" as free text is a paragraph nobody can filter,
# sort or count -- and the queue has to be workable, not just readable.
ACTIONS = [
    "CONFIRM_MATCH",       # a candidate looks right; a human need only agree
    "REQUEST_REMITTANCE",  # ask the customer which invoices this settles
    "CHECK_DUPLICATE",     # looks like the same money arriving twice
    "CHECK_REFUND",        # looks like money going back out, or a reversal
    "RAISE_INVOICE",       # payment against something never billed
    "WRITE_OFF_SMALL",     # difference too small to be worth a person's time
    "ESCALATE_DISPUTE",    # short payment that looks like a disagreement
    "NEEDS_MORE_DATA",     # nothing here is enough to say anything
]

SYSTEM_PROMPT = f"""\
You triage a reconciliation exception queue for an Indian business.

Each item is a bank credit that a deterministic rule engine could not match to \
an invoice. Your job is NOT to match it. That decision has already been made \
and you cannot change it. Your job is to tell the human who opens this queue \
what they are looking at and what to do about it.

For each item, write:

- `summary`: one or two plain sentences. What is this money, what makes it \
unresolvable, and what is the most likely explanation. Name the specific \
evidence: the amount gap and what it does or does not correspond to, the \
counterparty if the narration reveals one, the dates. Write for a finance \
person in a hurry, not for an engineer.
- `action`: exactly one of {', '.join(ACTIONS)}.
- `likely_invoice`: the single most plausible invoice id from the candidate \
list, or an empty string when nothing in the list is plausible. This is a \
lead for a human to check, never a match.
- `confidence_note`: a short phrase saying how sure you are and why, for \
example "weak: the name matches but the amount gap is unexplained".

HOW TO WRITE IT

Sound like someone on the accounts team leaving a note for whoever picks this \
up next. Plain, direct, slightly terse. The kind of sentence a person writes \
when they have forty of these to get through before lunch.

- Never use an em dash or an en dash, and never use a double hyphen in their \
place. Join clauses with a comma, a colon, a semicolon or a full stop.
- Skip openers like "This appears to be" or "It seems that". Say what it is.
- Avoid the "not X, but Y" construction, and do not finish on a tidy \
summarising flourish. Stop when the useful part is over.
- No bullet points, no headings, no bold. Sentences only.
- Use the words a finance team actually uses: short paid, part payment, \
remittance advice, on account, TDS deducted, written off.

Be honest about uncertainty. If the narration names nobody and no invoice fits \
the amount, say exactly that; it helps a reviewer more than a confident guess \
that sends them down the wrong path. Many of these genuinely cannot be \
resolved from the data available, and saying so plainly is the correct answer."""

RESPONSE_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "action", "likely_invoice", "confidence_note"],
    "properties": {
        "summary": {"type": "string",
                    "description": "One or two sentences for a finance reviewer."},
        "action": {"type": "string", "enum": ACTIONS},
        "likely_invoice": {"type": "string",
                           "description": "An invoice id from the candidate list, or \"\"."},
        "confidence_note": {"type": "string",
                            "description": "Short phrase: how sure, and why."},
    },
}


class _Note(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str
    action: str
    likely_invoice: str
    confidence_note: str


@dataclass
class ExceptionNote:
    """One queue entry, ready for a human. Never a decision."""
    txn_id: str
    amount: Decimal
    value_date: str
    narration: str
    outcome: str
    rule_reason: str
    candidates: list[str]
    summary: str
    action: str
    likely_invoice: str
    confidence_note: str
    written_by: str
    degraded: bool = False          # the model could not be reached

    def as_row(self) -> dict:
        return {
            "txn_id": self.txn_id,
            "amount": str(self.amount),
            "value_date": self.value_date,
            "outcome": self.outcome,
            "action": self.action,
            "likely_invoice": self.likely_invoice,
            "summary": self.summary,
            "confidence": self.confidence_note,
            "rule_reason": self.rule_reason,
            "candidates": " ".join(self.candidates),
            "narration": self.narration,
            "written_by": self.written_by,
        }


def build_prompt(txn: BankTransaction, decision: MatchDecision,
                 ledger: dict[str, LedgerEntry]) -> str:
    """Pure. What the reviewer would see, laid out for the model."""
    lines = [
        "EXCEPTION",
        f"  transaction {txn.txn_id}",
        f"  amount      Rs {txn.amount:,.2f} {txn.direction}",
        f"  date        {txn.value_date}",
        f"  narration   {txn.narration}",
        f"  utr         {txn.utr or '-'}",
        f"  outcome     {decision.outcome}",
        f"  rules said  {decision.reasoning}",
    ]
    if decision.proposed_invoice_ids:
        lines.append(f"  provisional {', '.join(decision.proposed_invoice_ids)} "
                     f"at confidence {decision.confidence:.2f}, a human must confirm")

    lines.append("")
    if decision.candidates_considered:
        lines.append(f"INVOICES CONSIDERED ({len(decision.candidates_considered)}):")
        for inv_id in decision.candidates_considered[:12]:
            e = ledger.get(inv_id)
            if e is None:
                continue
            delta = txn.amount - e.gross_amount
            lines.append(
                f"  {inv_id} | {e.counterparty} | gross Rs {e.gross_amount:,.2f} "
                f"| difference Rs {delta:,.2f} | issued {e.issue_date} "
                f"| due {e.due_date} | {e.status}"
                + (f" | TDS {e.tds_rate:.0%} applicable" if e.tds_applicable else ""))
    else:
        lines.append("INVOICES CONSIDERED: none. Nothing in the ledger was even "
                     "close on amount, date or counterparty.")

    lines += ["", "Triage this for the reviewer."]
    return "\n".join(lines)


def _fallback(txn: BankTransaction, decision: MatchDecision,
              reason: str) -> ExceptionNote:
    """A queue entry the model could not be reached for.

    Marked `degraded` rather than dropped: a queue that silently omits the
    items the API failed on is a queue that lies about how much work is left.
    """
    return ExceptionNote(
        txn_id=txn.txn_id, amount=txn.amount, value_date=str(txn.value_date),
        narration=txn.narration, outcome=decision.outcome,
        rule_reason=decision.reasoning,
        candidates=decision.candidates_considered[:12],
        summary=decision.reasoning,
        action="NEEDS_MORE_DATA", likely_invoice="",
        confidence_note=f"no model note ({reason})",
        written_by="rules", degraded=True,
    )


class Triager:
    """Cache -> client -> note. Same shape as the adjudicator, far fewer guards,
    because a note cannot post a rupee anywhere."""

    def __init__(self, cfg: Config, client: LLMClient,
                 cache: ResponseCache | None = None):
        self.cfg = cfg
        self.client = client
        self.cache = cache
        self.stats = {"calls": 0, "cache_hits": 0, "degraded": 0}

    def _key(self, txn: BankTransaction, decision: MatchDecision) -> str:
        import hashlib
        payload = json.dumps({
            "v": f"{PROMPT_VERSION}-{TRIAGE_VERSION}",
            "model": self.cfg.llm.active.model,
            "txn": txn.txn_id,
            "outcome": decision.outcome,
            "candidates": sorted(decision.candidates_considered),
        }, sort_keys=True)
        return "triage-" + hashlib.sha256(payload.encode()).hexdigest()[:26]

    def note(self, txn: BankTransaction, decision: MatchDecision,
             ledger: dict[str, LedgerEntry]) -> ExceptionNote:
        key = self._key(txn, decision)
        completion = self.cache.get(key) if self.cache else None
        if completion is not None:
            self.stats["cache_hits"] += 1
        else:
            try:
                completion = self.client.complete(
                    SYSTEM_PROMPT, build_prompt(txn, decision, ledger),
                    RESPONSE_SCHEMA)
            except LLMUnavailable:
                raise
            except (LLMTimeout, LLMSchemaFailure, Exception) as e:  # noqa: BLE001
                logger.warning("triage note unavailable",
                               extra={"txn_id": txn.txn_id, "error": repr(e)[:200]})
                self.stats["degraded"] += 1
                return _fallback(txn, decision, type(e).__name__)
            self.stats["calls"] += 1
            if self.cache:
                self.cache.put(key, completion, {
                    "txn_id": txn.txn_id, "kind": "triage",
                    "model": self.cfg.llm.active.model,
                    "written_at": datetime.now().isoformat()})

        try:
            parsed = _Note.model_validate(json.loads(_strip_fences(completion.text)))
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("triage note malformed",
                           extra={"txn_id": txn.txn_id, "error": str(e)[:200]})
            self.stats["degraded"] += 1
            return _fallback(txn, decision, "malformed response")

        # The one thing worth validating: a lead pointing at an invoice nobody
        # ever considered would send a reviewer looking for a record that has
        # no bearing on this credit. Same rule as invariant 3, lower stakes.
        lead = parsed.likely_invoice.strip()
        if lead and lead not in decision.candidates_considered:
            logger.warning("triage suggested an invoice outside the shortlist",
                           extra={"txn_id": txn.txn_id, "suggested": lead})
            lead = ""

        action = parsed.action if parsed.action in ACTIONS else "NEEDS_MORE_DATA"
        return ExceptionNote(
            txn_id=txn.txn_id, amount=txn.amount, value_date=str(txn.value_date),
            narration=txn.narration, outcome=decision.outcome,
            rule_reason=decision.reasoning,
            candidates=decision.candidates_considered[:12],
            summary=parsed.summary.strip(), action=action, likely_invoice=lead,
            confidence_note=parsed.confidence_note.strip(),
            written_by=f"{self.cfg.llm.provider}:{self.cfg.llm.active.model}",
        )


def build_triager(cfg: Config) -> Triager:
    provider = cfg.llm.provider
    if provider not in CLIENTS:
        raise ValueError(f"unknown llm.provider {provider!r}")
    return Triager(cfg, CLIENTS[provider](cfg),
                   ResponseCache(Path(cfg.llm.cache_dir)))


def triage_queue(decisions: list[MatchDecision], batch, cfg: Config,
                 triager: Triager | None = None,
                 on_progress=None) -> list[ExceptionNote]:
    """Write a note for every item a human still has to deal with.

    Ordered by money at stake, so the queue is worked in the order that retires
    the most exposure first -- and so the notes are generated in that order too,
    which matters when a run is interrupted partway.
    """
    ledger = {e.invoice_id: e for e in batch.ledger}
    txns = {t.txn_id: t for t in batch.bank}

    queue = [d for d in decisions if d.outcome in ("EXCEPTION", "NEEDS_REVIEW")]
    queue.sort(key=lambda d: txns[d.txn_id].amount, reverse=True)

    triager = triager or build_triager(cfg)
    notes: list[ExceptionNote] = []
    for d in queue:
        note = triager.note(txns[d.txn_id], d, ledger)
        notes.append(note)
        if on_progress:
            on_progress(note, len(notes), len(queue))
    return notes


# --------------------------------------------------------------------------
# Export -- the queue as something a person can actually work from
# --------------------------------------------------------------------------

def write_queue(notes: list[ExceptionNote], batch_name: str,
                reports_dir: Path = Path("reports")) -> tuple[Path, Path]:
    """Markdown to read, CSV to work. Returns both paths."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = reports_dir / f"exceptions_{batch_name}_{stamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(notes[0].as_row())) if notes else None
        if w:
            w.writeheader()
            w.writerows(n.as_row() for n in notes)

    by_action: dict[str, list[ExceptionNote]] = {}
    for n in notes:
        by_action.setdefault(n.action, []).append(n)
    exposure = sum((n.amount for n in notes), Decimal("0"))
    degraded = sum(1 for n in notes if n.degraded)

    md = [
        f"# Exception queue: `{batch_name}`",
        "",
        f"{len(notes)} items · ₹{exposure:,.2f} unresolved · "
        f"generated {datetime.now():%Y-%m-%d %H:%M}",
        "",
        "Every note below is written by a language model and is a **suggestion "
        "for a reviewer, never a decision**. No note moved money, and no note "
        "changed a match: the reconciliation in `reports/eval_*.md` is identical "
        "with triage on or off.",
        "",
    ]
    if degraded:
        md += [f"> {degraded} item(s) carry no model note. The call failed and "
               f"the rule's own reason is shown instead. They are listed rather "
               f"than dropped: a queue that hides what it could not process "
               f"misstates how much work is left.", ""]

    md += ["## By suggested action", "", "| Action | Items | Value |", "|---|---|---|"]
    for action, items in sorted(by_action.items(),
                                key=lambda kv: -sum(n.amount for n in kv[1])):
        md.append(f"| {action} | {len(items)} | "
                  f"₹{sum(n.amount for n in items):,.2f} |")

    md += ["", "## Queue", "", "Ordered by money at stake.", ""]
    for n in notes:
        md += [
            f"### {n.txn_id} · ₹{n.amount:,.2f} · `{n.action}`",
            "",
            f"*{n.value_date} · {n.outcome} · {n.narration}*",
            "",
            n.summary,
            "",
            f"- **Lead:** {n.likely_invoice or 'none'}",
            f"- **Certainty:** {n.confidence_note}",
            f"- **Rules said:** {n.rule_reason}",
            f"- **Considered:** {', '.join(n.candidates) or 'nothing'}",
            f"- **Note by:** {n.written_by}",
            "",
        ]

    md_path = reports_dir / f"exceptions_{batch_name}_{stamp}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    logger.info("exception queue written", extra={"items": len(notes),
                                                  "csv": str(csv_path),
                                                  "md": str(md_path)})
    return md_path, csv_path
