"""Tests for Stage 0 blocking (§13).

Blocking decides what the rules are ever allowed to see, so its failure mode is
silent: a dropped invoice produces no error, just a match that never happens.
The must-not-fire cases are the valuable ones here too -- a gate that admits
everything scores perfect recall and is worthless.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ledgerloop.candidates import generate_candidates, generate_group_candidates
from ledgerloop.config import load_config
from ledgerloop.models import BankTransaction, LedgerEntry

CFG = load_config()
VALUE_DATE = date(2026, 3, 1)


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


def txn(amount: str, narration: str, utr: str | None = None) -> BankTransaction:
    return BankTransaction(
        txn_id="BNK-TEST", value_date=VALUE_DATE, amount=Decimal(amount),
        direction="CREDIT", narration=narration, utr=utr,
        balance_after=Decimal("1000000"),
    )


def ids(candidates) -> set[str]:
    return {c.invoice.invoice_id for c in candidates}


# ---------------------------------------------------------------------------
# Single-invoice path: the conditional amount floor
# ---------------------------------------------------------------------------

def test_part_payment_shortlisted_when_narration_names_the_counterparty():
    """37% of gross is far below amount_lo, but the name identifies the payer."""
    ledger = [inv("INV-1004", "6663.78")]
    got = generate_candidates(txn("2472.26", "NEFT-NAIRIND"), ledger, CFG)
    assert ids(got) == {"INV-1004"}


def test_part_payment_dropped_when_narration_names_nobody():
    """MUST NOT FIRE: same amounts, anonymous narration.

    Without a name the amount is the only evidence there is, so the strict
    floor applies. Admitting this pairing would mean admitting every invoice in
    the window -- recall bought by making the shortlist meaningless.
    """
    ledger = [inv("INV-1004", "6663.78")]
    got = generate_candidates(txn("2472.26", "BY TRANSFER-852011843477-"), ledger, CFG)
    assert got == []


def test_corroborated_floor_still_has_a_bottom():
    """MUST NOT FIRE: a strong name does not make *any* amount admissible."""
    ledger = [inv("INV-1004", "6663.78")]
    # ~1.5% of gross, well under amount_lo_corroborated
    got = generate_candidates(txn("100.00", "NEFT-NAIRIND"), ledger, CFG)
    assert got == []


def test_quoted_invoice_number_bypasses_the_amount_and_date_gates():
    ledger = [inv("INV-1004", "6663.78", issued_days_ago=400)]
    got = generate_candidates(txn("2472.26", "NEFT/1004/PARTPAY"), ledger, CFG)
    assert ids(got) == {"INV-1004"}
    assert got[0].ref_hit is True


def test_utr_digits_are_not_read_as_an_invoice_number():
    """MUST NOT FIRE: a 12-digit UTR must never be mistaken for a reference.

    Amount and date are made to pass so the invoice is shortlisted either way --
    what is under test is `ref_hit`, which drives both the gate bypass and the
    largest ranking weight. Asserting the candidate is absent would pass for
    the wrong reason.
    """
    ledger = [inv("INV-852011", "6663.78")]
    got = generate_candidates(
        txn("6663.78", "BY TRANSFER-852011843477-", utr="852011843477"), ledger, CFG)
    assert ids(got) == {"INV-852011"}       # admitted on the exact amount alone
    assert got[0].ref_hit is False
    assert got[0].name_similarity == 0.0


def test_invoice_outside_the_date_window_is_dropped():
    """MUST NOT FIRE: right amount, right name, but far too old."""
    ledger = [inv("INV-1004", "6663.78",
                  issued_days_ago=CFG.blocking.date_back_days + 30)]
    got = generate_candidates(txn("6663.78", "NEFT-NAIRIND"), ledger, CFG)
    assert got == []


# ---------------------------------------------------------------------------
# Ranking and the cap
# ---------------------------------------------------------------------------

def test_quoted_reference_outranks_a_coincidental_exact_amount():
    """The bug the retiered _score exists to prevent.

    A same-sized unrelated invoice used to outrank the one actually cited in
    the narration, which then lost its slot to max_candidates.
    """
    ledger = [
        inv("INV-2000", "5000.00", counterparty="Reddy Packaging Ltd", cp_id="CP-002"),
        inv("INV-1004", "9000.00"),
    ]
    got = generate_candidates(txn("5000.00", "NEFT/1004/PAYMENT"), ledger, CFG)
    assert got[0].invoice.invoice_id == "INV-1004"


def test_shortlist_never_exceeds_max_candidates():
    ledger = [inv(f"INV-{3000 + k}", "5000.00") for k in range(60)]
    got = generate_candidates(txn("5000.00", "NEFT-NAIRIND"), ledger, CFG)
    assert len(got) == CFG.blocking.max_candidates


# ---------------------------------------------------------------------------
# Consolidated path
# ---------------------------------------------------------------------------

def test_group_found_when_three_invoices_sum_to_the_credit():
    ledger = [
        inv("INV-1036", "19331.03", cp_id="CP-009"),
        inv("INV-1235", "22705.01", cp_id="CP-009"),
        inv("INV-1279", "16726.21", cp_id="CP-009"),
    ]
    got = generate_group_candidates(
        txn("58762.25", "INB/266538204032/PAYMENT"), ledger, CFG)
    assert len(got) == 1
    assert {i.invoice_id for i in got[0].invoices} == {"INV-1036", "INV-1235", "INV-1279"}
    assert got[0].total == Decimal("58762.25")


def test_group_never_mixes_counterparties():
    """MUST NOT FIRE: the amounts sum perfectly, but to two different customers.

    One credit settles one customer's invoices. Without this the subset search
    would manufacture arithmetic coincidences across the whole ledger.
    """
    ledger = [
        inv("INV-1036", "19331.03", cp_id="CP-009"),
        inv("INV-1235", "22705.01", counterparty="Reddy Packaging Ltd", cp_id="CP-010"),
        inv("INV-1279", "16726.21", counterparty="Bose Industries", cp_id="CP-011"),
    ]
    got = generate_group_candidates(
        txn("58762.25", "INB/266538204032/PAYMENT"), ledger, CFG)
    assert got == []


def test_group_not_proposed_when_nothing_sums_to_the_credit():
    """MUST NOT FIRE: a near miss is a miss. Blocking does not round."""
    ledger = [
        inv("INV-1036", "19331.03", cp_id="CP-009"),
        inv("INV-1235", "22705.01", cp_id="CP-009"),
        inv("INV-1279", "16726.21", cp_id="CP-009"),
    ]
    got = generate_group_candidates(
        txn("58800.00", "INB/266538204032/PAYMENT"), ledger, CFG)
    assert got == []


def test_two_valid_subsets_are_both_returned_so_r4_can_abstain():
    """Ambiguity is surfaced, never resolved here.

    Blocking's job is to show both readings. Silently returning one would hide
    the ambiguity from R4, which is the layer required to refuse to fire.
    """
    ledger = [
        inv("INV-3001", "10000.00", cp_id="CP-009"),
        inv("INV-3002", "20000.00", cp_id="CP-009"),
        inv("INV-3003", "12000.00", cp_id="CP-009"),
        inv("INV-3004", "18000.00", cp_id="CP-009"),
    ]
    got = generate_group_candidates(txn("30000.00", "INB/999/PAYMENT"), ledger, CFG)
    subsets = {frozenset(i.invoice_id for i in g.invoices) for g in got}
    assert frozenset({"INV-3001", "INV-3002"}) in subsets
    assert frozenset({"INV-3003", "INV-3004"}) in subsets


def test_group_respects_max_size():
    """MUST NOT FIRE: five invoices sum to the credit, but the cap is four."""
    n = CFG.blocking.group_max_size + 1
    ledger = [inv(f"INV-{4000 + k}", "1000.00", cp_id="CP-009") for k in range(n)]
    got = generate_group_candidates(
        txn(str(n * 1000) + ".00", "INB/999/PAYMENT"), ledger, CFG)
    assert got == []


def test_group_reaches_further_back_than_the_single_invoice_window():
    """A backlog cleared in one transfer includes invoices too old for the
    single-invoice path, which is why the group path has its own window."""
    old = CFG.blocking.date_back_days + 10
    assert old < CFG.blocking.group_date_back_days
    ledger = [
        inv("INV-5001", "30000.00", cp_id="CP-009", issued_days_ago=old),
        inv("INV-5002", "28762.25", cp_id="CP-009", issued_days_ago=5),
    ]
    got = generate_group_candidates(txn("58762.25", "INB/999/PAYMENT"), ledger, CFG)
    assert len(got) == 1
    assert {i.invoice_id for i in got[0].invoices} == {"INV-5001", "INV-5002"}


def test_group_ignores_settled_invoices():
    """MUST NOT FIRE: the sum works only by including an already-paid invoice."""
    ledger = [
        inv("INV-6001", "30000.00", cp_id="CP-009"),
        inv("INV-6002", "28762.25", cp_id="CP-009", status="PAID"),
    ]
    got = generate_group_candidates(txn("58762.25", "INB/999/PAYMENT"), ledger, CFG)
    assert got == []


def test_single_invoice_is_never_returned_as_a_group():
    """MUST NOT FIRE: that is the single-invoice path's job, and R1's."""
    ledger = [inv("INV-7001", "58762.25", cp_id="CP-009")]
    got = generate_group_candidates(txn("58762.25", "INB/999/PAYMENT"), ledger, CFG)
    assert got == []
