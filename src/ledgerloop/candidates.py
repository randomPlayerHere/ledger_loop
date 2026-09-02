"""Stage 0: Candidate blocking and generation.

Picks what's worth looking at, doesn't decide matches. A wrong candidate is
cheap (a rule rejects it); a dropped one can never be matched by anything.
"""

from typing import List

from .models import LedgerEntry, BankTransaction, MatchDecision
from .utils.amounts import explain_shortfall, relative_gap, within_ratio
from .utils.dates import gap_days, within_window
from .utils.narration import extract_refs, name_score


# blocking's date policy: an invoice is normally raised before the money lands
def _date_ok(txn, inv, cfg) -> bool:
    return within_window(inv.issue_date, txn.value_date,
                         cfg["date_back_days"], cfg["date_fwd_days"])


def _amount_ok(txn, inv, cfg) -> bool:
    # an overpayment is always worth a look, however far above gross it sits
    return (within_ratio(txn.amount, inv.gross_amount, cfg["amount_lo"], cfg["amount_hi"])
            or txn.amount >= inv.gross_amount)


#get the fincal score for an invoice for a given transaction
def _score(txn, inv, ns: float, ref_hit: bool, shortfall: str | None) -> float:
    closeness = 1 - relative_gap(txn.amount, inv.gross_amount)
    return (
        (200 if ref_hit else 0)
        # exact amount must outrank fuzzy name hits or max_candidates evicts it
        + (60 if shortfall == "EXACT" else 0)
        + ns
        + float(closeness) * 50
        - gap_days(txn.value_date, inv.issue_date) * 0.3
    )

# THE MAIN FUNCTION
def generate_candidates(txn: BankTransaction, ledger: list[LedgerEntry], cfg) -> list[LedgerEntry]:
    b = cfg["blocking"]
    tol = cfg["tolerances"]
    refs = extract_refs(txn.narration, txn.utr, b["max_ref_digits"])
    keep = []
    for inv in ledger:
        num = inv.invoice_id.split("-")[-1]
        ref_hit = num in refs
        if not ref_hit:
            if not _date_ok(txn, inv, b):
                continue
            if not _amount_ok(txn, inv, b):
                continue
        shortfall = explain_shortfall(txn.amount, inv.gross_amount, tol)
        ns = name_score(txn.narration, inv.counterparty)
        if not ref_hit and shortfall is None and ns < b["name_min"]:
            continue
        keep.append((_score(txn, inv, ns, ref_hit, shortfall), inv))
    keep.sort(key=lambda p: p[0], reverse=True)
    return [inv for _, inv in keep[: b["max_candidates"]]]
