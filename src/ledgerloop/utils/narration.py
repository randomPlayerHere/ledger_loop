"""Reading bank narrations: invoice references and counterparty name matching.

Both live here because both parse the same messy free-text field. Roughly half
of real narrations carry neither signal ("BY TRANSFER-856796510678-").
"""

import re
from functools import lru_cache

from rapidfuzz import fuzz

# words that appear in narrations but are never counterparty names
_BANK_NOISE = {
    "NEFT", "IMPS", "RTGS", "UPI", "CMS", "INB", "BY", "TRANSFER",
    "PAYMENT", "AXIS", "HDFC", "ICICI", "SBI", "KOTAK",
}

_DIGITS = re.compile(r"\d+")


def _clean(text: str) -> str:
    return re.sub(r"[^A-Z0-9 ]", " ", text.upper())


# digit runs that could plausibly be invoice numbers
def extract_refs(narration: str, utr: str | None, max_digits: int) -> set[str]:
    refs = set()
    for run in _DIGITS.findall(narration):
        if len(run) > max_digits:      # UTRs are 12 digits
            continue
        if utr and run == utr:
            continue
        refs.add(run)
    return refs


# best fuzzy score between any narration word and the counterparty name (0-100)
#
# Blocking scores every transaction against every invoice, so this runs ~260k
# times a batch over only ~30k distinct (narration, counterparty) pairs. Pure
# function of its two arguments, so the cache is safe and the repeats are free.
@lru_cache(maxsize=200_000)
def name_score(narration: str, counterparty: str) -> float:
    cp = _clean(counterparty)
    chunks = [
        c for c in _clean(narration).split()
        if c and len(c) >= 4 and not c.isdigit() and c not in _BANK_NOISE
    ]
    if not chunks:
        return 0.0
    return max(
        max(fuzz.partial_ratio(c, cp), fuzz.token_set_ratio(c, cp))
        for c in chunks
    )
