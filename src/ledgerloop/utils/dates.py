"""Date windows and gaps. Takes plain dates, not models, so rules can reuse it."""

from datetime import date, timedelta


# is `target` inside the window around `anchor`? back/fwd are asymmetric because
# an invoice is normally raised before the money lands, rarely after
def within_window(target: date, anchor: date, back_days: int, fwd_days: int) -> bool:
    return anchor - timedelta(days=back_days) <= target <= anchor + timedelta(days=fwd_days)


# unsigned distance in days, for scoring and the evidence dict
def gap_days(a: date, b: date) -> int:
    return abs((a - b).days)
