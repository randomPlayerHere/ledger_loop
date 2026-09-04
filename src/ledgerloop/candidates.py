"""Stage 0: Candidate blocking and generation.

Picks what's worth looking at, doesn't decide matches. A wrong candidate is
cheap (a rule rejects it); a dropped one can never be matched by anything.
"""

from collections import defaultdict
from decimal import Decimal
from typing import List

from .config import Blocking, Config
from .models import LedgerEntry, BankTransaction, Candidate, CandidateGroup
from .utils.amounts import close, explain_shortfall, relative_gap, within_ratio
from .utils.dates import gap_days, within_window
from .utils.narration import extract_refs, name_score


# blocking's date policy: an invoice is normally raised before the money lands
def _date_ok(txn, inv, b: Blocking) -> bool:
    return within_window(inv.issue_date, txn.value_date,
                         b.date_back_days, b.date_fwd_days)


def _amount_ok(txn, inv, b: Blocking, corroborated: bool) -> bool:
    """Is the amount plausible enough to shortlist?

    `corroborated` means something other than the amount already identifies the
    payer -- a quoted invoice number or a strong counterparty name. When it
    does, a part-payment is worth looking at however small; when it doesn't,
    the amount is the only evidence there is and has to be held to the
    stricter floor or the shortlist fills with noise.
    """
    lo = b.amount_lo_corroborated if corroborated else b.amount_lo
    # an overpayment is always worth a look, however far above gross it sits
    return (within_ratio(txn.amount, inv.gross_amount, lo, b.amount_hi)
            or txn.amount >= inv.gross_amount)


# Ranking weights, ordered by how strongly each signal identifies the payer.
#
# The ordering is the point. Raw closeness used to be worth 50 and a name only
# 100, so an unrelated invoice that happened to be the size of the payment
# outranked the counterparty actually named in the narration. A part-payment is
# far from its invoice *by definition* -- closeness is a tiebreak between
# equally-evidenced candidates, never evidence in its own right.
#
# These are ranking weights, not business tolerances, so they stay here rather
# than in config.yaml: no one reconciling accounts would ever set them.
_W_REF = 1000.0        # a quoted invoice number settles it outright
_W_EXACT = 200.0       # amount matches to the paisa
_W_EXPLAINED = 100.0   # amount is short, but by a known cause (TDS, charges)
_W_NAME = 2.0          # x name_score, so a perfect name (100) rivals an exact amount
_W_CLOSE = 20.0        # x closeness (0-1) -- tiebreak only
_W_DAY = 0.5           # x days between issue date and value date


#get the fincal score for an invoice for a given transaction
def _score(txn, inv, ns: float, ref_hit: bool, shortfall: str | None) -> float:
    closeness = 1 - relative_gap(txn.amount, inv.gross_amount)
    if shortfall == "EXACT":
        amount_evidence = _W_EXACT
    elif shortfall is not None:          # TDS or bank charges -- explained, so real
        amount_evidence = _W_EXPLAINED
    else:
        amount_evidence = 0.0
    return (
        (_W_REF if ref_hit else 0.0)
        + amount_evidence
        + ns * _W_NAME
        + float(closeness) * _W_CLOSE
        - gap_days(txn.value_date, inv.issue_date) * _W_DAY
    )

# THE MAIN FUNCTION
def generate_candidates(txn: BankTransaction, ledger: list[LedgerEntry],
                        cfg: Config) -> list[Candidate]:
    b, tol = cfg.blocking, cfg.tolerances
    refs = extract_refs(txn.narration, txn.utr, b.max_ref_digits)
    keep = []
    for inv in ledger:
        num = inv.invoice_id.split("-")[-1]
        ref_hit = num in refs
        # the name is a gate input now, not just evidence: it picks which amount
        # floor applies, so it has to be scored before the gates run
        ns = name_score(txn.narration, inv.counterparty)
        if not ref_hit:
            if not _date_ok(txn, inv, b):
                continue
            if not _amount_ok(txn, inv, b, ns >= b.name_strong):
                continue
        shortfall = explain_shortfall(txn.amount, inv.gross_amount, tol)
        if not ref_hit and shortfall is None and ns < b.name_min:
            continue
        keep.append((_score(txn, inv, ns, ref_hit, shortfall),ref_hit, shortfall,ns ,inv))
    keep.sort(key=lambda p: p[0], reverse=True)
    return [Candidate(invoice=inv,
                      ref_hit=ref_hit,
                      name_similarity=ns,
                      shortfall=shortfall)
                for _, ref_hit, shortfall, ns, inv in keep[: b.max_candidates]
    ]


# --------------------------------------------------------------------------
# Consolidated path: one credit settling several invoices at once
# --------------------------------------------------------------------------

def _subsets_summing(invs: list[LedgerEntry], target: Decimal, max_size: int,
                     tol: Decimal, limit: int) -> list[list[LedgerEntry]]:
    """Every subset of 2..max_size invoices whose gross amounts sum to `target`.

    Depth-first over amounts sorted high-to-low, with three prunes. They matter:
    one customer can have 85 open invoices, and C(85,4) is 2.1 million subsets,
    so an unpruned search costs more than the rest of the pipeline put together.

      * overshoot -- amounts are all positive, so once the running total passes
        the target no extension of this branch can come back down
      * unreachable -- if every invoice still available summed together still
        falls short, the branch is dead
      * out of reach in the picks left -- the sharp one. A branch may only add
        `max_size - len(chosen)` more invoices, and sorted descending, the best
        it can possibly do from position k is the next few largest. Once that
        best case falls short of the target the loop stops rather than
        continuing: every later k is smaller still, so nothing beyond it can
        reach either.

    Returns as soon as `limit` subsets are found. Hitting the limit is itself
    the signal that the transaction is ambiguous, not an invitation to rank.
    """
    invs = sorted(invs, key=lambda i: i.gross_amount, reverse=True)
    n = len(invs)

    # prefix[k] = total of invs[:k]. Gives both remaining-total (the
    # unreachable prune) and best-k-more (the picks-left prune) in O(1).
    prefix = [Decimal(0)] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + invs[k].gross_amount
    total = prefix[n]

    out: list[list[LedgerEntry]] = []

    def walk(start: int, chosen: list[LedgerEntry], running: Decimal) -> None:
        if len(chosen) >= 2 and close(running, target, tol):
            out.append(list(chosen))
            return                       # positive amounts: no superset can also hit
        if len(chosen) == max_size or running > target + tol:
            return
        if running + total - prefix[start] < target - tol:
            return
        picks = max_size - len(chosen)   # including the one about to be taken
        for k in range(start, n):
            if len(out) >= limit:
                return
            amount = invs[k].gross_amount
            if running + amount > target + tol:
                continue                 # this one overshoots; a smaller one may not
            best = running + prefix[min(n, k + picks)] - prefix[k]
            if best < target - tol:
                break                    # and every later k is smaller still
            chosen.append(invs[k])
            walk(k + 1, chosen, running + amount)
            chosen.pop()

    walk(0, [], Decimal(0))
    return out[:limit]


def generate_group_candidates(txn: BankTransaction, ledger: list[LedgerEntry],
                              cfg: Config) -> list[CandidateGroup]:
    """Stage 0, consolidated path. Runs alongside generate_candidates.

    A member of a consolidated group is invisible to the single-invoice gate by
    construction: Rs19,331 against a Rs58,762 credit looks like a bad match on
    every axis. The group is only identifiable as a group.

    The narration usually names nobody ("INB/266538204032/PAYMENT"), so the
    counterparty cannot be *read* -- but it can still be *required*: one credit
    from one customer settles that customer's own invoices. Testing each
    counterparty's invoices separately is both the business rule and what makes
    the subset search affordable.
    """
    b, tol = cfg.blocking, cfg.tolerances
    refs = extract_refs(txn.narration, txn.utr, b.max_ref_digits)

    # An invoice at or above the credit cannot be one of several parts of it,
    # and a settled invoice is not awaiting payment.
    by_cp: dict[str, list[LedgerEntry]] = defaultdict(list)
    for inv in ledger:
        if inv.status not in ("OPEN", "PARTIALLY_PAID"):
            continue
        if inv.gross_amount >= txn.amount:
            continue
        if not within_window(inv.issue_date, txn.value_date,
                             b.group_date_back_days, b.date_fwd_days):
            continue
        by_cp[inv.counterparty_id].append(inv)

    groups: list[CandidateGroup] = []
    for cp_id, invs in by_cp.items():
        if len(invs) < 2:
            continue
        if sum(i.gross_amount for i in invs) < txn.amount - tol.amount_exact:
            continue                     # this customer cannot cover the credit
        for subset in _subsets_summing(invs, txn.amount, b.group_max_size,
                                       tol.amount_exact, b.group_max_results):
            groups.append(CandidateGroup(
                invoices=subset,
                counterparty_id=cp_id,
                total=sum(i.gross_amount for i in subset),
                name_similarity=max(name_score(txn.narration, i.counterparty)
                                    for i in subset),
                ref_hits=[i.invoice_id for i in subset
                          if i.invoice_id.split("-")[-1] in refs],
            ))

    # Prefer corroborated and smaller groups: a named counterparty or a quoted
    # invoice number is real evidence, and a 2-invoice sum is far less likely to
    # be coincidence than a 4-invoice one.
    groups.sort(key=lambda g: (len(g.ref_hits), g.name_similarity, -len(g.invoices)),
                reverse=True)
    return groups[: b.group_max_results]
