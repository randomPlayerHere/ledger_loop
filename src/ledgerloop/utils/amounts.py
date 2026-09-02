"""Money comparisons. Shared by Stage 0 blocking and R3 so the two can't drift."""

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:                        # type-only, so utils stays import-free
    from ..config import Tolerances


# never use == on an amount that's been through arithmetic
def close(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


# is `amount` inside [reference*lo, reference*hi]?
def within_ratio(amount: Decimal, reference: Decimal, lo: Decimal, hi: Decimal) -> bool:
    return reference * lo <= amount <= reference * hi


# |a - b| / b, capped at 1. 0 means identical -- for scoring and evidence dicts
def relative_gap(a: Decimal, b: Decimal) -> Decimal:
    return min(abs(a - b) / b, Decimal("1"))


# why is `paid` short of `gross`? returns a label for the audit trail, or None
def explain_shortfall(paid: Decimal, gross: Decimal, tol: "Tolerances") -> str | None:
    if close(paid, gross, tol.amount_exact):
        return "EXACT"

    delta = gross - paid
    if delta <= 0:
        return None                      # overpayment is a different scenario

    # TDS first: it's the more specific cause, and on small invoices a 2% cut
    # also fits under the bank-charge ceiling
    for rate in tol.tds_rates:
        if close(delta, gross * rate, tol.tds_tolerance):
            return f"TDS_{int(rate * 100)}PCT"

    # charges scale with the transfer but don't vanish on small ones -> floor too
    if delta <= max(tol.bank_charge_min, gross * tol.bank_charge_pct):
        return "BANK_CHARGES"

    return None                          # unexplained -> nobody may match on it
