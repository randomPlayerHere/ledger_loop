"""Stages 3 & 4: orchestration, confidence routing, exception handling.

The conveyor belt. It makes no matching judgements of its own -- it runs the
stages in order and records what came back. All the impurity lives here: the
clock, the ids, the ordering. That is what lets candidates.py and rules.py stay
pure functions testable with hand-built inputs.

Every bank line produces exactly one MatchDecision, including the ones nothing
could be done with. evaluate.py divides by the truth file's length, so a
transaction dropped on the floor here does not raise -- it quietly inflates the
auto-match rate instead.'/
"""

import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from .candidates import generate_candidates, generate_group_candidates
from .config import Config
from .loaders import Batch
from .models import (BankTransaction, Candidate, CandidateGroup, MatchDecision,
                     RuleResult)
from .rules import apply_rules, find_split_payments
from .utils.amounts import close

logger = logging.getLogger(__name__)

# reasons an exception happened, kept distinct because they need different
# human effort: one is "what is this money", the other is "which of these three"
NO_CANDIDATES = "No candidate invoices survived blocking."
NO_RULE = "Candidates found but no rule could explain the amount."
LOW_CONFIDENCE = "Best explanation scored below the exception threshold."


def _route(result: Optional[RuleResult], cfg: Config) -> tuple[str, str]:
    """Confidence -> outcome. Returns (outcome, reason-if-unresolved)."""
    if result is None:
        return "EXCEPTION", NO_RULE
    if result.confidence >= cfg.thresholds.auto_match:
        return "AUTO_MATCHED", ""
    if result.confidence >= cfg.thresholds.exception:
        return "NEEDS_REVIEW", ""
    return "EXCEPTION", LOW_CONFIDENCE


def _decide(txn: BankTransaction, candidates: list[Candidate],
            result: Optional[RuleResult], cfg: Config,
            started: float,
            groups: list[CandidateGroup] | None = None,
            *,
            decided_by: str = "RULE",
            tokens: tuple[int | None, int | None] = (None, None),
            forced: tuple[str, str] | None = None,
            extra_evidence: dict | None = None) -> MatchDecision:
    """Build the one audit record this transaction gets.

    The keyword arguments exist for Stage 2 and are inert for Stage 1. `forced`
    overrides confidence routing outright -- a hallucinated invoice id or a
    timeout is an EXCEPTION regardless of what the model claimed, and routing
    such a response on its own confidence would be trusting the thing that just
    proved untrustworthy.
    """
    outcome, reason = _route(result, cfg)
    if forced is not None:
        outcome, reason = forced

    # Everything the reviewer was entitled to consider, both shortlists. A group
    # member is invisible to the single-invoice path, so recording only
    # `candidates` would leave R4's own proposal absent from the list it was
    # supposedly chosen from -- an audit trail that contradicts itself.
    considered = [c.invoice.invoice_id for c in candidates]
    seen = set(considered)
    for g in groups or []:
        for inv in g.invoices:
            if inv.invoice_id not in seen:
                seen.add(inv.invoice_id)
                considered.append(inv.invoice_id)

    # an exception with no candidates is a different job for the reviewer than
    # one with three plausible invoices, so the queue must be able to tell them
    # apart from the record alone
    if result is None and not considered and forced is None:
        reason = NO_CANDIDATES

    # Evidence survives both paths: a rule's own dict, or -- when the record
    # exists precisely because something went wrong -- what the model said and
    # what the validator caught it on. An unexplained record is a bug even when
    # the record is an exception.
    evidence = dict(result.evidence) if result else {}
    if extra_evidence:
        evidence.update(extra_evidence)

    return MatchDecision(
        decision_id=str(uuid4()),
        txn_id=txn.txn_id,
        proposed_invoice_ids=result.invoice_ids if result else [],
        allocated=result.allocated if result else {},
        outcome=outcome,
        confidence=result.confidence if result else 0.0,
        # "RULE" even when nothing fired: the rules stage handled this txn, and
        # it handled it by declining. evaluate.py counts decided_by == "LLM" to
        # get the invocation rate, so a rules abstention must never be labelled
        # LLM -- only a transaction Stage 2 actually looked at carries that.
        decided_by=decided_by,
        rule_id=result.rule_id if result else None,
        reasoning=result.reasoning if (result and forced is None) else reason,
        evidence=evidence,
        candidates_considered=considered,
        llm_tokens_in=tokens[0],
        llm_tokens_out=tokens[1],
        latency_ms=int((time.perf_counter() - started) * 1000),
        created_at=datetime.now(),
    )


def _apply_splits(history: list[MatchDecision], batch: Batch,
                  cfg: Config) -> list[MatchDecision]:
    """R7's second pass: pair up instalments Stage 1 could not explain alone.

    Appends rather than edits, like every other correction in this file. The
    original abstention stays in the trail with its own reasoning, and the new
    record points back at it through `supersedes` -- so the audit shows that
    nothing was known about this credit until its sibling was found, which is
    the honest account of how the match was actually made.
    """
    # Only a match strong enough to post unattended counts as settled. A
    # decision below that bar is a proposal awaiting a human, and R7's evidence
    # -- two credits landing on the invoice total to the paisa, with no other
    # pair that does -- is stronger than any of the single-line readings that
    # land there. Treating a provisional guess as final let R3's lone-TDS
    # branch pre-empt three pairings R7 had better grounds for.
    settled = {d.txn_id: (set(d.proposed_invoice_ids)
                          if d.confidence >= cfg.thresholds.auto_match else set())
               for d in history}
    found = find_split_payments(batch.bank, batch.ledger, settled, cfg)
    if not found:
        return []

    prior = {d.txn_id: d for d in history}
    out: list[MatchDecision] = []
    for txn_id, result in found.items():
        was = prior[txn_id]
        outcome, _ = _route(result, cfg)
        out.append(MatchDecision(
            decision_id=str(uuid4()),
            txn_id=txn_id,
            proposed_invoice_ids=result.invoice_ids,
            allocated=result.allocated,
            outcome=outcome,
            confidence=result.confidence,
            decided_by="RULE",
            rule_id=result.rule_id,
            reasoning=result.reasoning,
            evidence=result.evidence,
            candidates_considered=was.candidates_considered,
            llm_tokens_in=None,
            llm_tokens_out=None,
            latency_ms=0,
            created_at=datetime.now(),
            supersedes=was.decision_id,
        ))

    logger.info("split payments paired", extra={"batch": batch.name,
                                                "transactions": len(out),
                                                "invoices": len(out) // 2})
    return out


def _supersede_duplicates(history: list[MatchDecision], batch: Batch,
                          cfg: Config) -> list[MatchDecision]:
    """Second pass: catch one invoice being paid twice.

    A rule sees one transaction at a time and so can never spot this. The
    signal is over-allocation -- more money assigned to an invoice than it is
    owed. Summing rather than counting matters: a partial payment legitimately
    claims the same invoice twice (15k + 25k against a 40k invoice), and only
    the sum can tell that apart from two full payments of 40k.

    Which claimant wins is not a coin flip. Whichever transaction was
    physically real, the outcome is identical: the invoice is settled once and
    one credit is left unapplied for a human to chase.
    """
    gross = {e.invoice_id: e.gross_amount for e in batch.ledger}
    date_of = {t.txn_id: t.value_date for t in batch.bank}

    claims: dict[str, list[MatchDecision]] = {}
    for d in history:
        for inv_id in d.proposed_invoice_ids:
            claims.setdefault(inv_id, []).append(d)

    corrections: list[MatchDecision] = []
    for inv_id, claimants in claims.items():
        if len(claimants) < 2:
            continue
        total = sum((d.allocated.get(inv_id, Decimal("0")) for d in claimants),
                    Decimal("0"))
        owed = gross.get(inv_id)
        # close() so a legitimate split that sums to the paisa isn't flagged
        if owed is None or total <= owed or close(total, owed, cfg.tolerances.amount_exact):
            continue

        # earliest credit settles the invoice; txn_id breaks same-day ties
        ordered = sorted(claimants, key=lambda d: (date_of[d.txn_id], d.txn_id))
        keeper, losers = ordered[0], ordered[1:]

        for d in losers:
            corrections.append(MatchDecision(
                decision_id=str(uuid4()),
                txn_id=d.txn_id,
                proposed_invoice_ids=[],
                allocated={},
                outcome="EXCEPTION",
                confidence=0.0,
                decided_by="RULE",
                rule_id="DEDUP",
                reasoning=(f"{inv_id} already settled by {keeper.txn_id}; "
                           "suspected duplicate credit, left unapplied."),
                evidence={
                    "superseded_rule": d.rule_id,
                    "invoice_id": inv_id,
                    "invoice_gross": owed,
                    "total_allocated": total,
                    "settled_by": keeper.txn_id,
                },
                candidates_considered=d.candidates_considered,
                llm_tokens_in=None,
                llm_tokens_out=None,
                latency_ms=0,
                created_at=datetime.now(),
                supersedes=d.decision_id,
            ))

    return corrections


def _worth_asking(candidates: list[Candidate], groups: list[CandidateGroup],
                  cfg: Config) -> bool:
    """Whether Stage 2 has a question to ask about this transaction.

    An empty shortlist is not a hard case, it is an unanswerable one: the
    model would be asked to choose from nothing and could only either abstain
    or invent an id. Both outcomes are already known before the call, so the
    call is not made. This gate is also what keeps the invocation rate near
    half of what the residual set would otherwise cost.
    """
    return len(candidates) + len(groups) >= cfg.llm.min_candidates


def reconcile(batch: Batch, cfg: Config, use_llm: bool = True,
              adjudicator: "Adjudicator | None" = None) -> list[MatchDecision]:
    """The effective decision per bank line. See `run_pipeline` for the trail."""
    return run_pipeline(batch, cfg, use_llm, adjudicator)[0]


def run_pipeline(batch: Batch, cfg: Config, use_llm: bool = True,
                 adjudicator: "Adjudicator | None" = None,
                 ) -> tuple[list[MatchDecision], list[MatchDecision]]:
    """Run the pipeline over one batch. Returns (effective, history).

    `effective` is one decision per bank line, latest wins -- what evaluate.py
    scores, since scoring the history instead would double-count a corrected
    match. `history` is every record ever produced, superseded ones included,
    and that is what audit.py stores: the trail is the product, and a trail
    that keeps only the final answer cannot say why the answer changed.

    `adjudicator` is injectable so tests can drive Stage 2 with a scripted
    client; left None with use_llm it is built from config, which fails loudly
    if the provider's key is missing rather than quietly reporting rules-only
    numbers under an LLM label.
    """
    history: list[MatchDecision] = []

    # `llm.adjudicate` is off by default and the reason is in config.yaml: the
    # model measured worse than the rules at choosing invoices. Stage 2's live
    # job is triage, which runs after this loop over the queue this loop
    # produces -- so a normal run builds no adjudicator at all.
    if use_llm and adjudicator is None and cfg.llm.adjudicate:
        from .llm import build_adjudicator     # local: keeps --no-llm import-free
        adjudicator = build_adjudicator(cfg)

    for txn in batch.bank:
        started = time.perf_counter()
        candidates = generate_candidates(txn, batch.ledger, cfg)
        # The consolidated path is a second, independent shortlist: a member of
        # a group is invisible to the single-invoice gate by construction, so
        # neither list is a subset of the other and R4 needs its own.
        groups = generate_group_candidates(txn, batch.ledger, cfg)
        result = apply_rules(txn, candidates, cfg, groups)

        # Stage 2. Only the residual reaches it: a rule that fired has already
        # explained the money in terms a human can check, and re-deciding it
        # with a model would trade an auditable reason for an opaque one.
        if (result is None and adjudicator is not None
                and _worth_asking(candidates, groups, cfg)):
            verdict = adjudicator.adjudicate(txn, candidates, groups)
            history.append(_decide(
                txn, candidates, verdict.result, cfg, started, groups,
                decided_by="LLM",
                tokens=(verdict.tokens_in, verdict.tokens_out),
                forced=verdict.forced,
                extra_evidence=verdict.evidence,
            ))
            continue

        history.append(_decide(txn, candidates, result, cfg, started, groups))

    # R7 runs here rather than inside the loop because its evidence is a
    # property of a pair of transactions, and no rule looking at one line at a
    # time can see it. It searches only what Stage 1 left unexplained, so it
    # can never contradict a rule that fired on better evidence.
    history.extend(_apply_splits(history, batch, cfg))

    corrections = _supersede_duplicates(history, batch, cfg)
    history.extend(corrections)

    effective = list({d.txn_id: d for d in history}.values())

    counts: dict[str, int] = {}
    for d in effective:
        counts[d.outcome] = counts.get(d.outcome, 0) + 1
    logger.info("reconciled batch", extra={"batch": batch.name,
                                           "n_txns": len(batch.bank),
                                           "superseded": len(corrections),
                                           "outcomes": counts,
                                           "stage2": adjudicator.stats
                                           if adjudicator else None})
    return effective, history
