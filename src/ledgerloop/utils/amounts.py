"""Money comparisons. Shared by Stage 0 blocking and R3 so the two can't drift."""

from decimal import Decimal


# never use == on an amount that's been through arithmetic
def close(a: Decimal, b: Decimal, tol: Decimal) -> bool:
    return abs(a - b) <= tol


# is `amount` inside [reference*lo, reference*hi]?
def within_ratio(amount: Decimal, reference: Decimal, lo: float, hi: float) -> bool:
    return reference * Decimal(str(lo)) <= amount <= reference * Decimal(str(hi))


# |a - b| / b, capped at 1. 0 means identical -- for scoring and evidence dicts
def relative_gap(a: Decimal, b: Decimal) -> Decimal:
    return min(abs(a - b) / b, Decimal("1"))


# why is `paid` short of `gross`? returns a label for the audit trail, or None
def explain_shortfall(paid: Decimal, gross: Decimal, tol: dict) -> str | None:
    if close(paid, gross, Decimal(str(tol["amount_exact"]))):
        return "EXACT"

    delta = gross - paid
    if delta <= 0:
        return None                      # overpayment is a different scenario

    # TDS first: it's the more specific cause, and on small invoices a 2% cut
    # also fits under the bank-charge ceiling
    for rate in tol["tds_rates"]:
        r = Decimal(str(rate))
        if close(delta, gross * r, Decimal(str(tol["tds_tolerance"]))):
            return f"TDS_{int(r * 100)}PCT"

    # charges scale with the transfer but don't vanish on small ones -> floor too
    ceiling = max(
        Decimal(str(tol["bank_charge_min"])),
        gross * Decimal(str(tol["bank_charge_pct"])),
    )
    if delta <= ceiling:
        return "BANK_CHARGES"

    return None                          # unexplained -> nobody may match on it
