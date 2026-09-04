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
from .rules import apply_rules
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
            groups: list[CandidateGroup] | None = None) -> MatchDecision:
    outcome, reason = _route(result, cfg)

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
    if result is None and not considered:
        reason = NO_CANDIDATES

    return MatchDecision(
        decision_id=str(uuid4()),
        txn_id=txn.txn_id,
        proposed_invoice_ids=result.invoice_ids if result else [],
        allocated=result.allocated if result else {},
        outcome=outcome,
        confidence=result.confidence if result else 0.0,
        # "RULE" even when nothing fired: the rules stage handled this txn, and
        # it handled it by declining. evaluate.py counts decided_by == "LLM" to
        # get the invocation rate, so an abstention must never be labelled LLM.
        decided_by="RULE",
        rule_id=result.rule_id if result else None,
        reasoning=result.reasoning if result else reason,
        evidence=result.evidence if result else {},
        candidates_considered=considered,
        llm_tokens_in=None,
        llm_tokens_out=None,
        latency_ms=int((time.perf_counter() - started) * 1000),
        created_at=datetime.now(),
    )


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


def reconcile(batch: Batch, cfg: Config, use_llm: bool = True) -> list[MatchDecision]:
    """Run the pipeline over one batch.

    Returns the *effective* decision per bank line -- one each, latest wins.
    `history` keeps every record including superseded ones; that is what the
    audit trail stores. Returning the history instead would double-count a
    corrected match, since evaluate.py reads links from every decision it is
    given.
    """
    history: list[MatchDecision] = []

    for txn in batch.bank:
        started = time.perf_counter()
        candidates = generate_candidates(txn, batch.ledger, cfg)
        # The consolidated path is a second, independent shortlist: a member of
        # a group is invisible to the single-invoice gate by construction, so
        # neither list is a subset of the other and R4 needs its own.
        groups = generate_group_candidates(txn, batch.ledger, cfg)
        result = apply_rules(txn, candidates, cfg, groups)

        # TODO Stage 2: when result is None and use_llm, adjudicate with the LLM
        # and rebuild the decision with decided_by="LLM" plus token counts.

        history.append(_decide(txn, candidates, result, cfg, started, groups))

    corrections = _supersede_duplicates(history, batch, cfg)
    history.extend(corrections)

    effective = list({d.txn_id: d for d in history}.values())

    counts: dict[str, int] = {}
    for d in effective:
        counts[d.outcome] = counts.get(d.outcome, 0) + 1
    logger.info("reconciled batch", extra={"batch": batch.name,
                                           "n_txns": len(batch.bank),
                                           "superseded": len(corrections),
                                           "outcomes": counts})
    return effective
