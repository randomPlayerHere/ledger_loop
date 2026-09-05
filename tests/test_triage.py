"""Stage 2b tests. No network.

Triage is the LLM's remaining job precisely because it cannot damage anything:
it proposes no invoice links and mutates no decision. The tests that matter are
the ones proving that claim rather than restating it -- that the reconciliation
is identical with triage on or off, that a failed call still produces a queue
entry rather than a silent gap, and that a note's "lead" cannot point at an
invoice nobody ever considered.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerloop.config import load_config
from ledgerloop.engine import run_pipeline
from ledgerloop.llm import Completion, LLMTimeout, ResponseCache
from ledgerloop.loaders import Batch
from ledgerloop.models import BankTransaction, LedgerEntry, MatchDecision
from ledgerloop.triage import (ACTIONS, Triager, build_prompt, triage_queue,
                               write_queue)

CFG = load_config()

INV = LedgerEntry(
    invoice_id="INV-1145", counterparty="Reddy Packaging LLP",
    counterparty_id="CP-7", gross_amount=Decimal("283019.55"),
    tds_applicable=False, tds_rate=Decimal("0"),
    issue_date=date(2026, 7, 1), due_date=date(2026, 7, 31), status="OPEN")

TXN = BankTransaction(
    txn_id="BNK-000158", value_date=date(2026, 7, 17),
    amount=Decimal("283019.55"), direction="CREDIT",
    narration="INB/300245327485/PAYMENT", utr="300245327485",
    balance_after=Decimal("900000.00"))

STUCK = MatchDecision(
    decision_id="d1", txn_id="BNK-000158", proposed_invoice_ids=[], allocated={},
    outcome="EXCEPTION", confidence=0.0, decided_by="RULE", rule_id=None,
    reasoning="INV-1145 already settled by BNK-000157; suspected duplicate.",
    evidence={}, candidates_considered=["INV-1145", "INV-1146"],
    llm_tokens_in=None, llm_tokens_out=None, latency_ms=1,
    created_at=datetime(2026, 9, 5))

LEDGER = {"INV-1145": INV}


def _note_json(**kw) -> str:
    body = {"summary": "Duplicate of BNK-000157.", "action": "CHECK_DUPLICATE",
            "likely_invoice": "INV-1145", "confidence_note": "moderate"}
    body.update(kw)
    return json.dumps(body)


class _Scripted:
    name = "scripted"

    def __init__(self, *responses, raises: Exception | None = None):
        self.responses, self.raises, self.calls = list(responses), raises, 0

    def complete(self, system, user, schema):
        self.calls += 1
        if self.raises:
            raise self.raises
        return Completion(self.responses.pop(0), 400, 90)


# --------------------------------------------------------------------------
# The safety claim
# --------------------------------------------------------------------------

def test_triage_cannot_change_the_reconciliation():
    """The whole justification for keeping the LLM. Triage runs over the
    decisions the engine produced; it takes them as input and returns notes.
    If this ever stopped being true, every accuracy number in the README would
    become a number an LLM had a hand in."""
    ledger = [INV]
    bank = [TXN]
    batch = Batch(name="t", bank=bank, ledger=ledger)

    before, _ = run_pipeline(batch, CFG, use_llm=False)
    triager = Triager(CFG, _Scripted(_note_json()), cache=None)
    notes = triage_queue(before, batch, CFG, triager)
    after, _ = run_pipeline(batch, CFG, use_llm=False)

    assert [(d.txn_id, d.outcome, d.proposed_invoice_ids) for d in before] == \
           [(d.txn_id, d.outcome, d.proposed_invoice_ids) for d in after]
    assert all(not hasattr(n, "proposed_invoice_ids") for n in notes)


def test_a_lead_outside_the_shortlist_is_dropped():
    """Invariant 3's reasoning at lower stakes: a lead pointing at an invoice
    nobody considered sends a reviewer looking for an irrelevant record."""
    triager = Triager(CFG, _Scripted(_note_json(likely_invoice="INV-9999")),
                      cache=None)

    note = triager.note(TXN, STUCK, LEDGER)

    assert note.likely_invoice == ""
    assert note.summary                       # the rest of the note survives


def test_an_invented_action_falls_back_rather_than_reaching_the_queue():
    triager = Triager(CFG, _Scripted(_note_json(action="DELETE_INVOICE")),
                      cache=None)

    note = triager.note(TXN, STUCK, LEDGER)

    assert note.action == "NEEDS_MORE_DATA"
    assert note.action in ACTIONS


# --------------------------------------------------------------------------
# Degradation is visible, never silent
# --------------------------------------------------------------------------

@pytest.mark.parametrize("failure", [LLMTimeout("slow"), ConnectionError("down")])
def test_a_failed_call_still_produces_a_queue_entry(failure):
    """A queue that silently omits what the API failed on misstates how much
    work is left, which is the one thing an exception list must not do."""
    triager = Triager(CFG, _Scripted(raises=failure), cache=None)

    note = triager.note(TXN, STUCK, LEDGER)

    assert note.degraded is True
    assert note.written_by == "rules"
    assert note.summary == STUCK.reasoning        # falls back to the rule's own
    assert triager.stats["degraded"] == 1


def test_a_malformed_note_degrades_rather_than_raising():
    triager = Triager(CFG, _Scripted("not json at all"), cache=None)

    note = triager.note(TXN, STUCK, LEDGER)

    assert note.degraded is True
    assert note.action == "NEEDS_MORE_DATA"


def test_notes_are_cached_so_a_rerun_does_not_re_bill(tmp_path: Path):
    client = _Scripted(_note_json(), _note_json())
    triager = Triager(CFG, client, cache=ResponseCache(tmp_path))

    triager.note(TXN, STUCK, LEDGER)
    triager.note(TXN, STUCK, LEDGER)

    assert client.calls == 1
    assert triager.stats["cache_hits"] == 1


# --------------------------------------------------------------------------
# Prompt and export
# --------------------------------------------------------------------------

def test_prompt_carries_the_evidence_a_reviewer_would_need():
    prompt = build_prompt(TXN, STUCK, LEDGER)

    assert TXN.narration in prompt
    assert "INV-1145" in prompt
    assert "Reddy Packaging LLP" in prompt
    assert "283,019.55" in prompt
    assert STUCK.reasoning in prompt


def test_prompt_says_plainly_when_nothing_was_considered():
    bare = STUCK.model_copy(update={"candidates_considered": []})
    assert "none" in build_prompt(TXN, bare, {}).lower()


def test_the_queue_export_states_that_notes_are_not_decisions(tmp_path: Path):
    """The disclaimer is load-bearing: a reviewer reading a confident-sounding
    paragraph needs to know a model wrote it and nothing acted on it."""
    triager = Triager(CFG, _Scripted(_note_json()), cache=None)
    notes = [triager.note(TXN, STUCK, LEDGER)]

    md_path, csv_path = write_queue(notes, "test", reports_dir=tmp_path)
    md = md_path.read_text(encoding="utf-8")

    assert "never a decision" in md
    assert "BNK-000158" in md and "CHECK_DUPLICATE" in md
    assert csv_path.exists()
    assert "txn_id" in csv_path.read_text(encoding="utf-8").splitlines()[0]


def test_the_queue_is_ordered_by_money_at_stake():
    small = TXN.model_copy(update={"txn_id": "BNK-2", "amount": Decimal("500.00")})
    big = TXN.model_copy(update={"txn_id": "BNK-3", "amount": Decimal("900000.00")})
    batch = Batch(name="t", bank=[small, big], ledger=[INV])
    decisions = [STUCK.model_copy(update={"decision_id": "a", "txn_id": "BNK-2"}),
                 STUCK.model_copy(update={"decision_id": "b", "txn_id": "BNK-3"})]

    triager = Triager(CFG, _Scripted(_note_json(), _note_json()), cache=None)
    notes = triage_queue(decisions, batch, CFG, triager)

    assert [n.txn_id for n in notes] == ["BNK-3", "BNK-2"]
