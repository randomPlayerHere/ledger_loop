"""Stage 1: Deterministic matching rules (R1-R5).

Pure functions. A rule is handed a transaction and its shortlist and returns
either a RuleResult or None. It never reads a file, never looks at a clock,
never mints an id -- engine.py owns all of that, which is what keeps these
testable with a hand-built list of candidates.

None means "I cannot be sure", and that is a correct answer. Two candidates
that fit equally well is not a tie to be broken; it is a question for a human.
"""

from typing import Callable, Optional

from .config import Config
from .models import BankTransaction, Candidate, RuleResult
from .utils.dates import gap_days

# TODO: Implement remaining rules per §6
# - R2: Fuzzy counterparty + amount tolerance
# - R3: TDS/bank-charge adjusted amounts
# - R4: Invoice subset matching


def _evidence(txn: BankTransaction, c: Candidate) -> dict:
    """The four keys CLAUDE.md requires on every decision.

    amount_delta is signed: negative means underpaid, positive overpaid.
    """
    return {
        "amount_delta": txn.amount - c.invoice.gross_amount,
        "date_gap_days": gap_days(txn.value_date, c.invoice.issue_date),
        "name_similarity": c.name_similarity,
        "ref_hit": c.ref_hit,
    }


def r1_exact(txn: BankTransaction, candidates: list[Candidate],
             cfg: Config) -> Optional[RuleResult]:
    """R1: exactly one candidate matches the amount to the paisa."""
    exact = [c for c in candidates if c.shortfall == "EXACT"]

    # 0 -> not this rule's case.
    # 2+ -> the transaction genuinely cannot say which invoice it settles,
    #       so the only honest answer is to escalate rather than pick one.
    if len(exact) != 1:
        return None

    c = exact[0]
    inv_id = c.invoice.invoice_id
    cited = " and the narration cites it" if c.ref_hit else ""

    return RuleResult(
        rule_id="R1_EXACT",
        invoice_ids=[inv_id],
        allocated={inv_id: txn.amount},
        confidence=(cfg.confidence.r1_exact_with_ref if c.ref_hit
                    else cfg.confidence.r1_exact),
        reasoning=f"Amount matches {inv_id} exactly{cited}; no other candidate does.",
        evidence=_evidence(txn, c),
    )


# ordered most-confident first; the first rule to fire wins
RULES= [
    r1_exact,
]


def apply_rules(txn: BankTransaction, candidates: list[Candidate],
                cfg: Config) -> Optional[RuleResult]:
    for rule in RULES:
        result = rule(txn, candidates, cfg)
        if result is not None:
            return result
    return None
