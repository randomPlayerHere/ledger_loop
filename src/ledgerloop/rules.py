"""Stage 1: Deterministic matching rules (R1-R6).

Pure functions. A rule is handed a transaction, its shortlist and the
consolidated groups Stage 0 found, and returns either a RuleResult or None. It
never reads a file, never looks at a clock, never mints an id -- engine.py owns
all of that, which is what keeps these testable with a hand-built list of
candidates.

None means "I cannot be sure", and that is a correct answer. Two candidates
that fit equally well is not a tie to be broken; it is a question for a human.

Every rule here answers the same two questions in the same order:

  1. WHICH invoice is this? -- a quoted invoice number, else a counterparty name
     strong enough to stand alone. If neither singles out one candidate, abstain.
  2. WHY is the amount not the invoice total? -- exact (R1), sums across
     several invoices (R4), explained by TDS or bank charges (R3), an excess
     over the total (R6), or short by an amount nothing explains (R5).

The second question is what sets the confidence, and therefore whether the
match posts automatically or waits for a human.
"""

from typing import Callable, Optional

from .config import Config
from .models import BankTransaction, Candidate, CandidateGroup, RuleResult
from .utils.dates import gap_days

# shortfall labels that mean "the amount is short, and we know why"
_EXPLAINED = ("TDS", "BANK_CHARGES")


def _evidence(txn: BankTransaction, c: Candidate, **extra) -> dict:
    """The four keys CLAUDE.md requires on every decision, plus rule extras.

    amount_delta is signed: negative means underpaid, positive overpaid.
    """
    return {
        "amount_delta": txn.amount - c.invoice.gross_amount,
        "date_gap_days": gap_days(txn.value_date, c.invoice.issue_date),
        "name_similarity": c.name_similarity,
        "ref_hit": c.ref_hit,
        **extra,
    }


def _group_evidence(txn: BankTransaction, g: CandidateGroup, **extra) -> dict:
    """Same four keys for a group. The date gap is the *worst* member's: a
    consolidated payment is only as timely as the oldest invoice it clears."""
    return {
        "amount_delta": txn.amount - g.total,
        "date_gap_days": max(gap_days(txn.value_date, i.issue_date)
                             for i in g.invoices),
        "name_similarity": g.name_similarity,
        "ref_hit": bool(g.ref_hits),
        **extra,
    }


def _identify(subset: list[Candidate], candidates: list[Candidate],
              cfg: Config) -> tuple[Optional[Candidate], str]:
    """Which single candidate does the narration point at? Returns (cand, tier).

    `subset` is the candidates this rule can actually account for -- the ones
    with an explainable shortfall, or an excess, or whatever the caller needs.
    `candidates` is the whole shortlist, and it is passed in because both tiers
    below are decided by comparison against invoices the rule itself cannot use.
    Judging identity inside the subset alone is how a rule ends up confidently
    matching the one invoice it happens to be able to explain.

    Two tiers, in order of how much they are worth trusting:

      REF   -- exactly one invoice number in the whole shortlist appears in the
               narration, and it is one this rule can explain. The payer told
               us what they were paying.
      NAME  -- nothing is cited anywhere, and exactly one candidate in the
               subset carries the *best* counterparty score in the shortlist,
               which must itself clear `name_strong`.

    Three guards, all learned from measured false positives on batch_dev:

      * A reference the rule cannot explain is a veto, not a shrug. A payment
        narrated `CMS/INV-1462/IyerTex` that runs Rs22k short of INV-1462 is a
        part payment of INV-1462 -- not, as the overpayment rule first
        concluded, a settlement of some other invoice of theirs that happens to
        be smaller than the credit.
      * "Above the bar" is not the same as "the best available". `IYERTEX`
        scores 85.7 against Iyer Textiles and 72.7 against Iyer Infotech, and
        both clear a bar of 70. Taking whichever of them the rule could explain
        matched Iyer Infotech's invoice for a payment that plainly came from
        Iyer Textiles. The narration names one counterparty; the highest score
        is the closest thing we have to reading which.
      * A number and a name that disagree cancel out. Narrations are corrupted
        in transit, and a mangled digit run can land on a real invoice
        belonging to somebody else entirely.

    Anything else returns (None, ""). Two cited candidates is not a tie to
    break, and neither is two invoices from the same well-named customer --
    both are the ambiguity that invariant 5 says must escalate.
    """
    usable = {c.invoice.invoice_id for c in subset}
    best = max((c.name_similarity for c in candidates), default=0.0)
    readable_name = best >= cfg.blocking.name_strong

    # A quoted number belonging to a *worse-named* counterparty than the
    # shortlist's best is a corrupted digit run, not a citation:
    # `CMS/INV-1195/BoseChe` reaches Mehta Chemicals' INV-1195 while the
    # narration plainly says Bose. The number and the name disagree, so the
    # number is dropped and the name is left to decide.
    cited = [c for c in candidates
             if c.ref_hit and not (readable_name and c.name_similarity < best)]
    if cited:
        if len(cited) == 1 and cited[0].invoice.invoice_id in usable:
            return cited[0], "REF"
        return None, ""

    if not readable_name:
        return None, ""
    named = [c for c in subset if c.name_similarity >= best]
    if len(named) == 1:
        return named[0], "NAME"
    return None, ""


def r1_exact(txn: BankTransaction, candidates: list[Candidate],
             groups: list[CandidateGroup], cfg: Config) -> Optional[RuleResult]:
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


def r4_subset_sum(txn: BankTransaction, candidates: list[Candidate],
                  groups: list[CandidateGroup], cfg: Config) -> Optional[RuleResult]:
    """R4: one credit clearing several invoices from the same counterparty.

    Stage 0 has already done the searching -- it returns every subset of 2-4
    of one customer's open invoices whose gross amounts sum to the credit. This
    rule's entire job is to refuse when there is more than one such subset.

    That refusal is the rule. A sum landing on the paisa across three invoices
    is close to impossible by chance, which is what makes a single subset
    trustworthy; two subsets means the arithmetic cannot say which set of
    invoices the customer meant, and no amount of ranking can recover it.

    Allocation is each invoice's own gross, not a share of the payment: the
    customer paid three specific bills in full, and the books have to say so.
    """
    if len(groups) != 1:
        return None

    g = groups[0]
    inv_ids = [i.invoice_id for i in g.invoices]

    cited = (f"; the narration cites {', '.join(g.ref_hits)}" if g.ref_hits
             else "")
    return RuleResult(
        rule_id="R4_SUBSET_SUM",
        invoice_ids=inv_ids,
        allocated={i.invoice_id: i.gross_amount for i in g.invoices},
        confidence=(cfg.confidence.r4_subset_with_ref if g.ref_hits
                    else cfg.confidence.r4_subset),
        reasoning=(f"{len(inv_ids)} invoices from one counterparty sum to the "
                   f"credit exactly ({', '.join(inv_ids)}){cited}; "
                   "no other combination does."),
        evidence=_group_evidence(txn, g, group_size=len(g.invoices),
                                 counterparty_id=g.counterparty_id,
                                 group_total=g.total,
                                 ref_hit_ids=g.ref_hits),
    )


def r3_tolerance(txn: BankTransaction, candidates: list[Candidate],
                 groups: list[CandidateGroup], cfg: Config) -> Optional[RuleResult]:
    """R3: the payment is short, and the shortfall has a known cause.

    Two causes are admitted, both computed in `amounts.explain_shortfall` so
    blocking and this rule can never disagree about what "explainable" means:

      TDS          -- the delta is 2% or 10% of gross, the statutory rates
      BANK_CHARGES -- the delta is at most max(Rs50, 0.5% of gross)

    Anything else falls through untouched. This is invariant 4, and it is the
    whole difference between this rule and a "+/-2% tolerance" that would
    manufacture a match for every invoice that happens to sit near the payment.

    The invoice still has to be identified on its own evidence: a delta that
    *could* be TDS says nothing about *whose* TDS it is.
    """
    explained = [c for c in candidates
                 if c.shortfall is not None and c.shortfall.startswith(_EXPLAINED)]
    if not explained:
        return None

    c, tier = _identify(explained, candidates, cfg)
    # No reference, no readable name: the delta being a plausible size is not
    # identification. Firing here anyway was measured at 0.516 precision on
    # batch_dev -- across 31 transactions it matched the one invoice whose gross
    # happened to sit a TDS-shaped distance from a payment that was really a
    # part payment, a disputed bill, or a refund from nobody in the ledger.
    # That is precisely the manufactured match invariant 4 exists to prevent.
    if c is None:
        return None

    inv_id = c.invoice.invoice_id
    is_tds = c.shortfall.startswith("TDS")
    conf = cfg.confidence
    if is_tds:
        confidence = conf.r3_tds_with_ref if tier == "REF" else conf.r3_tds
        cause = f"{c.shortfall.replace('TDS_', '').replace('PCT', '%')} TDS"
    else:
        confidence = conf.r3_charges_with_ref if tier == "REF" else conf.r3_charges
        cause = "bank charges"

    return RuleResult(
        rule_id="R3_TOLERANCE",
        invoice_ids=[inv_id],
        allocated={inv_id: txn.amount},
        confidence=confidence,
        reasoning=(f"Short of {inv_id} by "
                   f"Rs{c.invoice.gross_amount - txn.amount}, which is {cause}."),
        evidence=_evidence(txn, c, shortfall_reason=c.shortfall, tier=tier),
    )


def r6_overpaid(txn: BankTransaction, candidates: list[Candidate],
                groups: list[CandidateGroup], cfg: Config) -> Optional[RuleResult]:
    """R6: the credit exceeds the invoice -- an advance, or a rounded-up transfer.

    The invoice is settled in full and the excess is *not* allocated anywhere;
    it is money the business has received and does not yet have a bill for, and
    the evidence dict says so. Allocating the whole payment would overstate what
    the invoice was worth and would make the duplicate pass below think the
    invoice had been paid twice.

    Bounded by `overpay_max_ratio` so a large credit cannot be parked against a
    small invoice: an excess of a few percent is a rounding habit, an excess of
    several hundred percent is a different transaction entirely.
    """
    tol = cfg.tolerances
    over = [c for c in candidates
            if txn.amount > c.invoice.gross_amount + tol.amount_exact
            and txn.amount <= c.invoice.gross_amount * tol.overpay_max_ratio
            and c.invoice.status in ("OPEN", "PARTIALLY_PAID")]
    if not over:
        return None

    c, tier = _identify(over, candidates, cfg)
    if c is None:
        return None

    # "Overpaid a small invoice" and "part-paid a big one" are the same bank
    # line seen from two sides, and only a quoted invoice number can tell them
    # apart. Where the customer has a larger open invoice that is named just as
    # well, this rule fired on the smaller one at 0.154 precision -- 11 wrong
    # matches out of 13, almost all of them installments against the bigger
    # bill. So a name alone is not enough while a larger invoice is in view.
    if tier == "NAME" and any(cc.invoice.gross_amount > txn.amount
                              and cc.name_similarity >= c.name_similarity
                              for cc in candidates):
        return None

    inv_id = c.invoice.invoice_id
    gross = c.invoice.gross_amount
    excess = txn.amount - gross

    return RuleResult(
        rule_id="R6_OVERPAID",
        invoice_ids=[inv_id],
        allocated={inv_id: gross},
        confidence=(cfg.confidence.r6_overpaid_with_ref if tier == "REF"
                    else cfg.confidence.r6_overpaid_named),
        reasoning=(f"Credit exceeds {inv_id} by Rs{excess}; the invoice is "
                   "settled in full and the excess is left unapplied."),
        evidence=_evidence(txn, c, unapplied_excess=excess, tier=tier),
    )


def r5_underpaid(txn: BankTransaction, candidates: list[Candidate],
                 groups: list[CandidateGroup], cfg: Config) -> Optional[RuleResult]:
    """R5: the payment is short and nothing explains the shortfall.

    This is the installment that has not finished arriving (PARTIAL) and the
    bill the customer is contesting (DISPUTED) -- deliberately one rule,
    because from a single bank line the two are indistinguishable. Whether the
    balance is coming next month or never is a fact about the future, and no
    amount of matching logic can read it off this transaction.

    So the rule answers only the question it can: *which* invoice is being paid
    against. It records the residual and lets confidence routing decide who
    looks at it. It fires last because every other rule can account for the
    amount and this one, by construction, cannot.

    Note what is *not* here: no floor on how short the payment may be. A 30%
    payment is as identifiable as a 90% one when the narration quotes the
    invoice number, and picking a cutoff would only mean guessing on one side
    of it.
    """
    short = [c for c in candidates
             if c.shortfall is None
             and txn.amount < c.invoice.gross_amount
             and c.invoice.status in ("OPEN", "PARTIALLY_PAID")]
    if not short:
        return None

    c, tier = _identify(short, candidates, cfg)
    if c is None:
        return None

    inv_id = c.invoice.invoice_id
    residual = c.invoice.gross_amount - txn.amount
    how = ("the narration cites it" if tier == "REF"
           else "the counterparty name matches and no other open invoice fits")

    return RuleResult(
        rule_id="R5_UNDERPAID",
        invoice_ids=[inv_id],
        allocated={inv_id: txn.amount},
        confidence=(cfg.confidence.r5_underpaid_with_ref if tier == "REF"
                    else cfg.confidence.r5_underpaid_named),
        reasoning=(f"Part payment against {inv_id} ({how}); Rs{residual} "
                   "still outstanding, with no TDS or charge explaining it."),
        evidence=_evidence(txn, c, residual=residual, tier=tier,
                           paid_fraction=round(
                               float(txn.amount / c.invoice.gross_amount), 4)),
    )


# Ordered most-confident first; the first rule to fire wins.
#
# The ordering is by how completely the rule accounts for the money, not by how
# often it fires. R1 and R4 explain the amount to the paisa; R3 explains the
# gap by a named cause; R6 explains the excess; R5 explains nothing about the
# amount at all and only claims to know whose invoice it is. A transaction that
# two rules can both speak to should always be answered by the one that leaves
# least unexplained.
RULES: list[Callable[..., Optional[RuleResult]]] = [
    r1_exact,
    r4_subset_sum,
    r3_tolerance,
    r6_overpaid,
    r5_underpaid,
]


def apply_rules(txn: BankTransaction, candidates: list[Candidate],
                cfg: Config,
                groups: list[CandidateGroup] | None = None) -> Optional[RuleResult]:
    groups = groups or []
    for rule in RULES:
        result = rule(txn, candidates, groups, cfg)
        if result is not None:
            return result
    return None
