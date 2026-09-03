"""Stages 3 & 4: orchestration, confidence routing, exception handling.

The conveyor belt. It makes no matching judgements of its own -- it runs the
stages in order and records what came back. All the impurity lives here: the
clock, the ids, the ordering. That is what lets candidates.py and rules.py stay
pure functions testable with hand-built inputs.

Every bank line produces exactly one MatchDecision, including the ones nothing
could be done with. evaluate.py divides by the truth file's length, so a
transaction dropped on the floor here does not raise -- it quietly inflates the
auto-match rate instead.
"""

import logging
import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .candidates import generate_candidates
from .config import Config
from .loaders import Batch
from .models import BankTransaction, Candidate, MatchDecision, RuleResult
from .rules import apply_rules

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
            started: float) -> MatchDecision:
    outcome, reason = _route(result, cfg)

    # an exception with no candidates is a different job for the reviewer than
    # one with three plausible invoices, so the queue must be able to tell them
    # apart from the record alone
    if result is None and not candidates:
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
        candidates_considered=[c.invoice.invoice_id for c in candidates],
        llm_tokens_in=None,
        llm_tokens_out=None,
        latency_ms=int((time.perf_counter() - started) * 1000),
        created_at=datetime.now(),
    )


def reconcile(batch: Batch, cfg: Config, use_llm: bool = True) -> list[MatchDecision]:
    """Run the pipeline over one batch. One decision per bank line, in order."""
    decisions: list[MatchDecision] = []

    for txn in batch.bank:
        started = time.perf_counter()
        candidates = generate_candidates(txn, batch.ledger, cfg)
        result = apply_rules(txn, candidates, cfg)

        # TODO Stage 2: when result is None and use_llm, adjudicate with the LLM
        # and rebuild the decision with decided_by="LLM" plus token counts.

        decisions.append(_decide(txn, candidates, result, cfg, started))

    counts: dict[str, int] = {}
    for d in decisions:
        counts[d.outcome] = counts.get(d.outcome, 0) + 1
    logger.info("reconciled batch", extra={"batch": batch.name,
                                           "n_txns": len(batch.bank),
                                           "outcomes": counts})
    return decisions
