"""Audit trail tests.

The trail is the product, so the tests that matter are the ones asserting what
it *refuses* to do: it will not let a record be edited, it will not let one be
deleted, and it will not hand back a tidy final-state view that hides a
correction. A store that quietly permitted any of those would still pass a
happy-path test and would be worthless to an auditor.
"""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerloop.audit import AuditLog
from ledgerloop.config import load_config
from ledgerloop.engine import run_pipeline
from ledgerloop.loaders import Batch
from ledgerloop.models import BankTransaction, LedgerEntry, MatchDecision

CFG = load_config()


def _decision(decision_id: str, txn_id: str = "TXN-1", outcome: str = "AUTO_MATCHED",
              supersedes: str | None = None, **kw) -> MatchDecision:
    base = dict(
        decision_id=decision_id, txn_id=txn_id,
        proposed_invoice_ids=["INV-1"], allocated={"INV-1": Decimal("41250.55")},
        outcome=outcome, confidence=0.97, decided_by="RULE", rule_id="R1_EXACT",
        reasoning="Amount matches exactly.",
        evidence={"amount_delta": Decimal("0.00"), "ref_hit": True},
        candidates_considered=["INV-1", "INV-2"],
        llm_tokens_in=None, llm_tokens_out=None, latency_ms=3,
        created_at=datetime(2026, 9, 5, 12, 0, 0), supersedes=supersedes,
    )
    base.update(kw)
    return MatchDecision(**base)


@pytest.fixture
def log(tmp_path: Path):
    with AuditLog(tmp_path / "audit.db") as db:
        db.start_run("run-1", "dev", n_txns=1, use_llm=False)
        yield db


# --------------------------------------------------------------------------
# Append-only. The guarantees, not the conveniences.
# --------------------------------------------------------------------------

def test_a_record_cannot_be_edited(log):
    """Invariant 2. Enforced by the database, not by the discipline of callers."""
    log.record([_decision("d1")], "run-1", "dev")

    with pytest.raises(Exception, match="append-only"):
        log.conn.execute("UPDATE decisions SET outcome = 'EXCEPTION' "
                         "WHERE decision_id = 'd1'")


def test_a_record_cannot_be_deleted(log):
    log.record([_decision("d1")], "run-1", "dev")

    with pytest.raises(Exception, match="append-only"):
        log.conn.execute("DELETE FROM decisions WHERE decision_id = 'd1'")


def test_the_same_decision_id_cannot_be_written_twice(log):
    """Two records sharing one identity is a bug upstream, not a duplicate to
    silently collapse."""
    log.record([_decision("d1")], "run-1", "dev")

    with pytest.raises(Exception):
        log.record([_decision("d1", reasoning="different")], "run-1", "dev")


def test_a_correction_cannot_reference_a_record_that_never_happened(log):
    with pytest.raises(Exception):
        log.record([_decision("d2", supersedes="never-written")], "run-1", "dev")


# --------------------------------------------------------------------------
# What the trail is for
# --------------------------------------------------------------------------

def test_history_keeps_both_readings_in_order(log):
    """The question the trail exists to answer: not 'what do we think now' but
    'what did we think, when, and on what evidence'."""
    log.record([
        _decision("d1", outcome="EXCEPTION", confidence=0.0,
                  proposed_invoice_ids=[], allocated={},
                  rule_id=None, reasoning="No rule could explain the amount."),
        _decision("d2", supersedes="d1", rule_id="R7_SPLIT", confidence=0.96,
                  reasoning="Instalment of INV-1; paired with TXN-2."),
    ], "run-1", "dev")

    trail = log.history("TXN-1")

    assert [r["decision_id"] for r in trail] == ["d1", "d2"]
    assert trail[0]["rule_id"] is None
    assert trail[1]["supersedes"] == "d1"


def test_effective_view_returns_the_correction_not_the_original(log):
    log.record([
        _decision("d1", outcome="EXCEPTION", proposed_invoice_ids=[], allocated={}),
        _decision("d2", supersedes="d1"),
    ], "run-1", "dev")

    eff = log.effective_decisions("run-1")

    assert len(eff) == 1
    assert eff[0]["decision_id"] == "d2"
    assert [r["decision_id"] for r in log.superseded("run-1")] == ["d1"]


def test_money_survives_the_round_trip_as_decimal_not_float(log):
    """41250.55 must come back as 41250.55, not 41250.549999999996."""
    log.record([_decision("d1")], "run-1", "dev")

    got = log.history("TXN-1")[0]

    assert got["allocated"] == {"INV-1": "41250.55"}
    assert Decimal(got["allocated"]["INV-1"]) == Decimal("41250.55")
    assert got["evidence"]["amount_delta"] == "0.00"


def test_the_queue_is_ordered_by_money_at_stake(log):
    """A reviewer working top-down should retire the largest exposure first,
    not the alphabetically earliest transaction id."""
    log.record([
        _decision("d1", txn_id="TXN-A", outcome="EXCEPTION", confidence=0.0,
                  proposed_invoice_ids=[], allocated={},
                  evidence={"invoice_gross": Decimal("5000.00")}),
        _decision("d2", txn_id="TXN-B", outcome="NEEDS_REVIEW", confidence=0.72,
                  allocated={"INV-9": Decimal("250000.00")}),
        _decision("d3", txn_id="TXN-C", outcome="AUTO_MATCHED"),
    ], "run-1", "dev")

    queue = log.exceptions("run-1")

    assert [r["txn_id"] for r in queue] == ["TXN-B", "TXN-A"]   # d3 posted, not queued


# --------------------------------------------------------------------------
# Against the real pipeline
# --------------------------------------------------------------------------

def test_the_pipeline_writes_a_trail_that_outlives_its_corrections(tmp_path: Path):
    """R7 supersedes an abstention, and both survive in the trail while the
    effective view shows only the match. A store keeping just the final answer
    could not show that the credit was once unexplainable."""
    inv = LedgerEntry(
        invoice_id="INV-500", counterparty="Iyer Textiles", counterparty_id="CP-1",
        gross_amount=Decimal("69359.68"), tds_applicable=False,
        tds_rate=Decimal("0"), issue_date=date(2026, 1, 5),
        due_date=date(2026, 2, 4), status="OPEN")
    halves = [
        BankTransaction(txn_id="BNK-1", value_date=date(2026, 1, 20),
                        amount=Decimal("36483.19"), direction="CREDIT",
                        narration="INB/600951639708/PAYMENT", utr="X1",
                        balance_after=Decimal("1")),
        BankTransaction(txn_id="BNK-2", value_date=date(2026, 2, 14),
                        amount=Decimal("32876.49"), direction="CREDIT",
                        narration="INB/600951639709/PAYMENT", utr="X2",
                        balance_after=Decimal("1")),
    ]
    batch = Batch(name="split", bank=halves, ledger=[inv])

    effective, history = run_pipeline(batch, CFG, use_llm=False)

    with AuditLog(tmp_path / "audit.db") as db:
        db.start_run("r", "split", n_txns=2, use_llm=False)
        db.record(history, "r", "split")

        assert len(history) > len(effective)          # corrections were kept
        trail = db.history("BNK-1")
        assert len(trail) == 2
        assert trail[0]["proposed_invoice_ids"] == []
        assert trail[1]["rule_id"] == "R7_SPLIT"
        assert trail[1]["supersedes"] == trail[0]["decision_id"]

        [current] = [r for r in db.effective_decisions("r") if r["txn_id"] == "BNK-1"]
        assert current["decision_id"] == trail[1]["decision_id"]
        assert db.summary("r")["superseded"] == 2
