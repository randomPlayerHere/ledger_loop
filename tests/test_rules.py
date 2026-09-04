"""Tests for deterministic matching rules (§13).

Rules are pure functions over a hand-built shortlist, so nothing here touches
a file, a batch, or Stage 0 -- a rule test that had to arrange a narration
carefully enough for blocking to admit the right candidates would be testing
blocking, and would keep passing once the rule stopped working.

The must-not-fire cases are the point. A rule that fires on everything scores
perfect recall and posts wrong numbers to a customer's books; every abstention
below is a case where the honest answer is a human, and each one is here
because the alternative was measured and was worse.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ledgerloop.config import load_config
from ledgerloop.models import BankTransaction, Candidate, CandidateGroup, LedgerEntry
from ledgerloop.rules import (apply_rules, r1_exact, r3_tolerance, r4_subset_sum,
                              r5_underpaid, r6_overpaid)

CFG = load_config()
VALUE_DATE = date(2026, 3, 1)

STRONG = CFG.blocking.name_strong          # a name good enough to identify a payer
WEAK = CFG.blocking.name_strong - 10.0     # ...and one that is not


def inv(iid: str, amount: str, counterparty: str = "Nair Industries LLP",
        cp_id: str = "CP-001", issued_days_ago: int = 10,
        status: str = "OPEN") -> LedgerEntry:
    issued = VALUE_DATE - timedelta(days=issued_days_ago)
    return LedgerEntry(
        invoice_id=iid, counterparty=counterparty, counterparty_id=cp_id,
        gross_amount=Decimal(amount), tds_applicable=False,
        tds_rate=Decimal("0"), issue_date=issued,
        due_date=issued + timedelta(days=30), status=status,
    )


def cand(entry: LedgerEntry, ref: bool = False, name: float = 0.0,
         shortfall: str | None = None) -> Candidate:
    return Candidate(invoice=entry, ref_hit=ref, name_similarity=name,
                     shortfall=shortfall)


def txn(amount: str, narration: str = "NEFT/PAYMENT") -> BankTransaction:
    return BankTransaction(
        txn_id="BNK-TEST", value_date=VALUE_DATE, amount=Decimal(amount),
        direction="CREDIT", narration=narration, utr=None,
        balance_after=Decimal("1000000"),
    )


def group(*entries: LedgerEntry, name: float = 0.0,
          refs: list[str] | None = None) -> CandidateGroup:
    return CandidateGroup(
        invoices=list(entries),
        counterparty_id=entries[0].counterparty_id,
        total=sum(e.gross_amount for e in entries),
        name_similarity=name,
        ref_hits=refs or [],
    )


def auto(result) -> bool:
    """Would confidence routing post this without a human? Rules do not decide
    the outcome, so a rule test asserting AUTO_MATCHED has to ask the threshold."""
    return result.confidence >= CFG.thresholds.auto_match


# ---------------------------------------------------------------------------
# R1 -- exact amount
# ---------------------------------------------------------------------------

def test_r1_fires_on_a_single_exact_amount():
    c = cand(inv("INV-1004", "6663.78"), shortfall="EXACT")
    got = r1_exact(txn("6663.78"), [c], [], CFG)
    assert got.rule_id == "R1_EXACT"
    assert got.invoice_ids == ["INV-1004"]
    assert got.allocated == {"INV-1004": Decimal("6663.78")}
    assert auto(got)


def test_r1_scores_higher_when_the_narration_cites_the_invoice():
    e = inv("INV-1004", "6663.78")
    bare = r1_exact(txn("6663.78"), [cand(e, shortfall="EXACT")], [], CFG)
    cited = r1_exact(txn("6663.78"), [cand(e, ref=True, shortfall="EXACT")], [], CFG)
    assert cited.confidence > bare.confidence


def test_r1_must_not_fire_on_two_equally_exact_candidates():
    """MUST NOT FIRE: two invoices of the same size, one payment.

    Nothing in the transaction distinguishes them, so picking either is a coin
    flip dressed up as a decision.
    """
    cands = [cand(inv("INV-1004", "6663.78"), shortfall="EXACT"),
             cand(inv("INV-1009", "6663.78"), shortfall="EXACT")]
    assert r1_exact(txn("6663.78"), cands, [], CFG) is None


# ---------------------------------------------------------------------------
# R3 -- explainable shortfall
# ---------------------------------------------------------------------------

def test_r3_fires_on_tds_when_the_narration_cites_the_invoice():
    e = inv("INV-1006", "49414.96")
    got = r3_tolerance(txn("44473.46"), [cand(e, ref=True, shortfall="TDS_10PCT")],
                       [], CFG)
    assert got.rule_id == "R3_TOLERANCE"
    assert got.invoice_ids == ["INV-1006"]
    assert got.allocated == {"INV-1006": Decimal("44473.46")}   # net, not gross
    assert got.evidence["shortfall_reason"] == "TDS_10PCT"
    assert got.evidence["amount_delta"] < 0                     # signed: underpaid
    assert auto(got)


def test_r3_fires_on_bank_charges_identified_by_counterparty_name():
    e = inv("INV-1008", "78404.60")
    got = r3_tolerance(txn("78374.59"), [cand(e, name=STRONG, shortfall="BANK_CHARGES")],
                       [], CFG)
    assert got.evidence["shortfall_reason"] == "BANK_CHARGES"
    assert got.evidence["tier"] == "NAME"
    assert auto(got)


def test_r3_scores_tds_above_bank_charges():
    """A delta of exactly 2% or 10% of gross is a far narrower target to hit by
    accident than 'at most max(Rs50, 0.5%)', and the confidence says so."""
    e = inv("INV-1008", "78404.60")
    tds = r3_tolerance(txn("70564.14"), [cand(e, ref=True, shortfall="TDS_10PCT")],
                       [], CFG)
    chg = r3_tolerance(txn("78374.59"), [cand(e, ref=True, shortfall="BANK_CHARGES")],
                       [], CFG)
    assert tds.confidence > chg.confidence


def test_r3_must_not_fire_on_an_unexplainable_delta():
    """MUST NOT FIRE (required coverage): short by an amount nothing accounts for.

    This is invariant 4. The candidate is cited by name *and* number and is the
    only one in the shortlist -- the identification could hardly be stronger --
    and R3 still declines, because it has no account of where the money went.
    A '+/-2% tolerance' would take this match and manufacture the rest.
    """
    e = inv("INV-1009", "19029.51")
    c = cand(e, ref=True, name=STRONG, shortfall=None)
    assert r3_tolerance(txn("15052.34"), [c], [], CFG) is None


def test_r3_must_not_fire_on_an_explainable_delta_alone():
    """MUST NOT FIRE: no reference, no readable name, just a plausible gap.

    Measured at 0.516 precision over 31 transactions on batch_dev. A shortfall
    the right size to be TDS says nothing about *whose* TDS it is, and an
    anonymous narration leaves nothing else to go on.
    """
    c = cand(inv("INV-1006", "49414.96"), name=WEAK, shortfall="TDS_10PCT")
    assert r3_tolerance(txn("44473.46"), [c], [], CFG) is None


def test_r3_must_not_fire_when_two_named_candidates_are_both_explainable():
    """MUST NOT FIRE: same customer, two invoices, both deltas explainable."""
    cands = [cand(inv("INV-1006", "49414.96"), name=STRONG, shortfall="TDS_10PCT"),
             cand(inv("INV-1007", "44518.00"), name=STRONG, shortfall="BANK_CHARGES")]
    assert r3_tolerance(txn("44473.46"), cands, [], CFG) is None


def test_r3_must_not_fire_on_an_invoice_other_than_the_one_cited():
    """MUST NOT FIRE: the narration names an invoice this rule cannot explain.

    The payer said what they were paying. That it does not fit R3's arithmetic
    is a reason to escalate, not a licence to match the invoice next to it.
    """
    cands = [cand(inv("INV-1462", "69399.32"), ref=True, name=STRONG, shortfall=None),
             cand(inv("INV-1409", "48306.82"), name=STRONG, shortfall="BANK_CHARGES")]
    assert r3_tolerance(txn("48286.20"), cands, [], CFG) is None


def test_r3_must_not_fire_on_a_worse_named_counterparty():
    """MUST NOT FIRE: 'IYERTEX' scores 85.7 on Iyer Textiles and 72.7 on Iyer
    Infotech, and a bar of 70 admits both. The invoice R3 can explain belongs to
    Infotech; the payment plainly came from Textiles. Above the bar is not the
    same as the best available.
    """
    cands = [cand(inv("INV-1492", "48710.80", counterparty="Iyer Textiles & Co"),
                  name=85.7, shortfall=None),
             cand(inv("INV-1469", "17670.69", counterparty="Iyer Infotech",
                      cp_id="CP-002"), name=72.7, shortfall="BANK_CHARGES")]
    assert r3_tolerance(txn("17584.60"), cands, [], CFG) is None


# ---------------------------------------------------------------------------
# R4 -- consolidated subset sum
# ---------------------------------------------------------------------------

def test_r4_fires_on_a_single_subset_and_allocates_each_invoice_its_gross():
    invs = [inv("INV-1036", "19331.03", cp_id="CP-009"),
            inv("INV-1235", "22705.01", cp_id="CP-009"),
            inv("INV-1279", "16726.21", cp_id="CP-009")]
    got = r4_subset_sum(txn("58762.25"), [], [group(*invs)], CFG)
    assert got.rule_id == "R4_SUBSET_SUM"
    assert set(got.invoice_ids) == {"INV-1036", "INV-1235", "INV-1279"}
    # each bill settled in full -- not a pro-rata share of the payment
    assert got.allocated == {"INV-1036": Decimal("19331.03"),
                             "INV-1235": Decimal("22705.01"),
                             "INV-1279": Decimal("16726.21")}
    assert sum(got.allocated.values()) == Decimal("58762.25")
    assert auto(got)


def test_r4_must_not_fire_on_two_valid_subsets():
    """MUST NOT FIRE (required coverage): 10k+20k and 12k+18k both make 30k.

    Both readings are arithmetically perfect, so the arithmetic cannot choose.
    Ranking them by date or size would be inventing a preference the evidence
    does not support.
    """
    a = group(inv("INV-3001", "10000.00", cp_id="CP-009"),
              inv("INV-3002", "20000.00", cp_id="CP-009"))
    b = group(inv("INV-3003", "12000.00", cp_id="CP-009"),
              inv("INV-3004", "18000.00", cp_id="CP-009"))
    assert r4_subset_sum(txn("30000.00"), [], [a, b], CFG) is None


def test_r4_must_not_fire_without_a_group():
    assert r4_subset_sum(txn("30000.00"), [], [], CFG) is None


def test_r4_scores_higher_when_the_narration_cites_a_member():
    invs = [inv("INV-1036", "19331.03", cp_id="CP-009"),
            inv("INV-1235", "39431.22", cp_id="CP-009")]
    bare = r4_subset_sum(txn("58762.25"), [], [group(*invs)], CFG)
    cited = r4_subset_sum(txn("58762.25"), [],
                          [group(*invs, refs=["INV-1036"])], CFG)
    assert cited.confidence > bare.confidence


# ---------------------------------------------------------------------------
# R5 -- underpayment with no explanation (PARTIAL and DISPUTED together)
# ---------------------------------------------------------------------------

def test_r5_fires_on_a_cited_part_payment_and_records_the_residual():
    e = inv("INV-1002", "60805.32")
    got = r5_underpaid(txn("36483.19"), [cand(e, ref=True, shortfall=None)], [], CFG)
    assert got.rule_id == "R5_UNDERPAID"
    assert got.allocated == {"INV-1002": Decimal("36483.19")}   # only what arrived
    assert got.evidence["residual"] == Decimal("24322.13")
    assert got.evidence["tier"] == "REF"
    assert auto(got)


def test_r5_sends_a_name_only_match_to_a_human():
    """The invoice is identified by a fuzzy name and the amount is short by an
    amount nothing explains. Two soft signals do not add up to a hard one."""
    e = inv("INV-1002", "60805.32")
    got = r5_underpaid(txn("36483.19"), [cand(e, name=STRONG, shortfall=None)], [], CFG)
    assert got.evidence["tier"] == "NAME"
    assert not auto(got)
    assert got.confidence >= CFG.thresholds.exception   # reviewed, not discarded


def test_r5_must_not_fire_on_two_equally_good_counterparty_candidates():
    """MUST NOT FIRE (required coverage): one customer, two open invoices, a
    payment that is short of both. The name identifies the payer and not the
    invoice, which is exactly the question that needs answering.
    """
    cands = [cand(inv("INV-1002", "60805.32"), name=STRONG),
             cand(inv("INV-1003", "58120.00"), name=STRONG)]
    assert r5_underpaid(txn("36483.19"), cands, [], CFG) is None


def test_r5_must_not_fire_when_nothing_identifies_the_payer():
    """MUST NOT FIRE: an anonymous narration and an arbitrary fraction of gross.

    This is the honest exception the queue exists for -- and, since it reaches
    Stage 2 with its shortlist attached, what the LLM is asked to adjudicate.
    """
    c = cand(inv("INV-1002", "60805.32"), name=WEAK)
    assert r5_underpaid(txn("36483.19"), [c], [], CFG) is None


def test_r5_must_not_fire_on_a_settled_invoice():
    """MUST NOT FIRE: a paid invoice is not awaiting an installment."""
    c = cand(inv("INV-1002", "60805.32", status="PAID"), ref=True)
    assert r5_underpaid(txn("36483.19"), [c], [], CFG) is None


# ---------------------------------------------------------------------------
# R6 -- overpayment
# ---------------------------------------------------------------------------

def test_r6_allocates_the_invoice_total_and_leaves_the_excess_unapplied():
    """The invoice was for 19824.34 and 20396.60 arrived. The books get the
    invoice's own amount; the rest is money without a bill, and saying so is the
    whole point -- allocating the payment would overstate what was owed."""
    e = inv("INV-1033", "19824.34")
    got = r6_overpaid(txn("20396.60"), [cand(e, ref=True)], [], CFG)
    assert got.rule_id == "R6_OVERPAID"
    assert got.allocated == {"INV-1033": Decimal("19824.34")}
    assert got.evidence["unapplied_excess"] == Decimal("572.26")
    assert auto(got)


def test_r6_must_not_fire_when_the_excess_dwarfs_the_invoice():
    """MUST NOT FIRE: an excess of a few percent is a rounding habit; one of
    several hundred percent is a different transaction wearing the same name."""
    e = inv("INV-1033", "19824.34")
    beyond = Decimal("19824.34") * CFG.tolerances.overpay_max_ratio + Decimal("1")
    assert r6_overpaid(txn(str(beyond)), [cand(e, ref=True)], [], CFG) is None


def test_r6_must_not_fire_on_a_name_while_a_larger_invoice_is_in_view():
    """MUST NOT FIRE: 'overpaid the small one' and 'part-paid the big one' are
    the same bank line seen from two sides.

    Only a quoted invoice number tells them apart. Firing on the name alone was
    measured at 0.154 precision on batch_dev -- 11 wrong out of 13, nearly all
    of them installments against the larger bill.
    """
    cands = [cand(inv("INV-1319", "42094.62"), name=STRONG),      # exceeded
             cand(inv("INV-1462", "69399.32"), name=STRONG)]      # short of
    assert r6_overpaid(txn("46705.74"), cands, [], CFG) is None


def test_r6_fires_on_a_name_when_no_larger_invoice_competes():
    cands = [cand(inv("INV-1033", "19824.34"), name=STRONG),
             cand(inv("INV-1034", "9000.00"), name=STRONG)]
    got = r6_overpaid(txn("20396.60"), cands, [], CFG)
    assert got.invoice_ids == ["INV-1033"]
    assert got.evidence["tier"] == "NAME"
    assert not auto(got)


# ---------------------------------------------------------------------------
# Rule order and confidence calibration
# ---------------------------------------------------------------------------

def test_an_exact_match_outranks_a_part_payment_reading():
    """Both rules can speak to this line; the one that leaves nothing
    unexplained answers it."""
    cands = [cand(inv("INV-1004", "6663.78"), shortfall="EXACT"),
             cand(inv("INV-1005", "20000.00"), ref=True)]
    got = apply_rules(txn("6663.78"), cands, CFG)
    assert got.rule_id == "R1_EXACT"


def test_a_single_invoice_exact_match_outranks_a_consolidated_reading():
    exact = cand(inv("INV-1004", "30000.00"), shortfall="EXACT")
    g = group(inv("INV-3001", "10000.00", cp_id="CP-009"),
              inv("INV-3002", "20000.00", cp_id="CP-009"))
    got = apply_rules(txn("30000.00"), [exact], CFG, [g])
    assert got.rule_id == "R1_EXACT"


def test_apply_rules_abstains_rather_than_returning_a_weak_answer():
    c = cand(inv("INV-1002", "60805.32"), name=WEAK)
    assert apply_rules(txn("36483.19"), [c], CFG) is None


@pytest.mark.parametrize("name", sorted(CFG.confidence.model_dump()))
def test_every_confidence_lands_in_a_band_on_purpose(name):
    """2.5: a rule at 0.94 silently becomes NEEDS_REVIEW.

    Confidences and thresholds are set in the same file and are trivially
    knocked out of alignment. This does not assert which band a rule belongs in
    -- only that every value is either clearly above the auto-match line or a
    clear margin below it, never parked where a two-decimal edit flips a rule's
    outcome without anyone noticing.
    """
    auto_at = CFG.thresholds.auto_match
    value = getattr(CFG.confidence, name)
    assert CFG.thresholds.exception <= value <= 1.0, "would go straight to the queue"
    assert value >= auto_at or value <= auto_at - 0.02, "too close to the line to be a decision"


def test_a_quoted_reference_never_scores_below_the_same_rule_without_one():
    conf = CFG.confidence
    for bare, cited in [("r1_exact", "r1_exact_with_ref"),
                        ("r3_tds", "r3_tds_with_ref"),
                        ("r3_charges", "r3_charges_with_ref"),
                        ("r4_subset", "r4_subset_with_ref"),
                        ("r5_underpaid_named", "r5_underpaid_with_ref"),
                        ("r6_overpaid_named", "r6_overpaid_with_ref")]:
        assert getattr(conf, cited) > getattr(conf, bare), bare
