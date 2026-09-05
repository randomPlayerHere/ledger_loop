"""Stage 2 tests. None of these opens a network connection.

That is the point of the split in llm.py: prompt construction and response
validation are pure functions, so every guarantee the spec calls hard -- the
model may only return ids it was shown, a timeout escalates, ambiguity is not
guessed at -- is testable against a hand-written string.

The valuable tests here are the ones asserting a *rejection*. A validator that
accepts good answers is easy; one that reliably refuses bad ones is the whole
reason Stage 2 is allowed to run unattended at all.
"""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerloop.config import load_config
from ledgerloop.engine import reconcile
from ledgerloop.llm import (ALLOCATION_INVALID, ALLOCATION_MISMATCH, API_ERROR,
                            CONFIDENCE_RANGE, DUPLICATE_ID, HALLUCINATED_ID,
                            LLM_TIMEOUT, MALFORMED_RESPONSE, OVER_ALLOCATED,
                            RULE_ID, Adjudicator, Completion, LLMTimeout,
                            ResponseCache, build_prompt, cache_key,
                            select_shown, shown_ids, validate_response)
from ledgerloop.loaders import Batch
from ledgerloop.models import BankTransaction, Candidate, LedgerEntry

CFG = load_config()


# --------------------------------------------------------------------------
# Fixtures: one credit, two plausible invoices
# --------------------------------------------------------------------------

def _inv(invoice_id: str, gross: str, name: str = "Meridian Textiles Pvt Ltd") -> LedgerEntry:
    return LedgerEntry(
        invoice_id=invoice_id, counterparty=name, counterparty_id="CP-001",
        gross_amount=Decimal(gross), tds_applicable=True, tds_rate=Decimal("0.10"),
        issue_date=date(2026, 1, 10), due_date=date(2026, 2, 9), status="OPEN",
    )


def _cand(invoice_id: str, gross: str, ref_hit: bool = False, ns: float = 88.0) -> Candidate:
    return Candidate(invoice=_inv(invoice_id, gross), ref_hit=ref_hit,
                     name_similarity=ns, shortfall=None)


TXN = BankTransaction(
    txn_id="TXN-0001", value_date=date(2026, 1, 20), amount=Decimal("41250.00"),
    direction="CREDIT", narration="NEFT/MERIDIAN TEXTILES/INV0042",
    utr="N026250012345", balance_after=Decimal("980000.00"),
)

CANDS = [_cand("INV-0042", "41250.00", ref_hit=True), _cand("INV-0043", "41250.00")]
ALLOWED = shown_ids(CANDS, [])


def _response(ids, allocs, confidence=0.9, reasoning="Invoice number quoted.") -> str:
    return json.dumps({
        "invoice_ids": ids,
        "allocations": [{"invoice_id": i, "amount": a} for i, a in allocs],
        "confidence": confidence,
        "reasoning": reasoning,
    })


# --------------------------------------------------------------------------
# The happy path, so the rejections below mean something
# --------------------------------------------------------------------------

def test_valid_response_becomes_a_rule_result():
    result, violation, _ = validate_response(
        _response(["INV-0042"], [("INV-0042", "41250.00")]), TXN, ALLOWED, CFG)

    assert violation is None
    assert result is not None
    assert result.rule_id == RULE_ID
    assert result.invoice_ids == ["INV-0042"]
    assert result.allocated == {"INV-0042": Decimal("41250.00")}
    # Decimal, not float -- money never round-trips through a JSON number here.
    assert isinstance(result.allocated["INV-0042"], Decimal)
    assert result.evidence["amount_delta"] == Decimal("0.00")


def test_confidence_is_capped_at_the_ceiling():
    """A model may claim 0.99. It does not get to auto-post on its own say-so."""
    result, violation, _ = validate_response(
        _response(["INV-0042"], [("INV-0042", "41250.00")], confidence=0.99),
        TXN, ALLOWED, CFG)

    assert violation is None
    assert result.confidence == CFG.llm.confidence_ceiling
    assert result.confidence < CFG.thresholds.auto_match
    assert result.evidence["confidence_capped"] is True
    assert result.evidence["llm_confidence_raw"] == 0.99


def test_multi_invoice_allocation_is_accepted():
    txn = TXN.model_copy(update={"amount": Decimal("82500.00")})
    result, violation, _ = validate_response(
        _response(["INV-0042", "INV-0043"],
                  [("INV-0042", "41250.00"), ("INV-0043", "41250.00")]),
        txn, ALLOWED, CFG)

    assert violation is None
    assert sum(result.allocated.values()) == Decimal("82500.00")


# --------------------------------------------------------------------------
# Must-not-pass. Invariant 3 and its neighbours.
# --------------------------------------------------------------------------

def test_hallucinated_id_is_rejected_and_logged():
    """Invariant 3. An id we never showed is fabricated, not merely wrong."""
    result, violation, evidence = validate_response(
        _response(["INV-9999"], [("INV-9999", "41250.00")]), TXN, ALLOWED, CFG)

    assert violation == HALLUCINATED_ID
    assert result is None
    assert evidence["hallucinated_ids"] == ["INV-9999"]
    assert evidence["candidates_shown"] == ALLOWED


def test_one_real_id_does_not_launder_one_invented_id():
    """The half-correct answer is the dangerous one: it looks like a match."""
    txn = TXN.model_copy(update={"amount": Decimal("82500.00")})
    result, violation, evidence = validate_response(
        _response(["INV-0042", "INV-9999"],
                  [("INV-0042", "41250.00"), ("INV-9999", "41250.00")]),
        txn, ALLOWED, CFG)

    assert violation == HALLUCINATED_ID
    assert result is None
    assert evidence["hallucinated_ids"] == ["INV-9999"]


def test_id_from_the_wider_blocking_list_is_still_a_hallucination():
    """Validation is against what the model was *shown*, not what blocking
    found. The top-k cut is part of the contract, not a display detail."""
    wide = CANDS + [_cand("INV-0044", "41250.00")]
    shown, _ = select_shown(wide, [], CFG.llm.model_copy(update={"max_candidates": 2}))
    allowed = shown_ids(shown, [])

    assert "INV-0044" not in allowed
    _, violation, _ = validate_response(
        _response(["INV-0044"], [("INV-0044", "41250.00")]), TXN, allowed, CFG)
    assert violation == HALLUCINATED_ID


def test_malformed_json_is_rejected():
    result, violation, evidence = validate_response(
        "I think this is invoice INV-0042.", TXN, ALLOWED, CFG)

    assert violation == MALFORMED_RESPONSE
    assert result is None
    assert "raw_response" in evidence


def test_schema_violation_is_rejected():
    _, violation, _ = validate_response(
        json.dumps({"invoice_ids": ["INV-0042"], "confidence": 0.9}),
        TXN, ALLOWED, CFG)
    assert violation == MALFORMED_RESPONSE


def test_duplicate_invoice_id_is_rejected():
    _, violation, _ = validate_response(
        _response(["INV-0042", "INV-0042"], [("INV-0042", "41250.00")]),
        TXN, ALLOWED, CFG)
    assert violation == DUPLICATE_ID


def test_allocation_that_does_not_cover_the_selection_is_rejected():
    txn = TXN.model_copy(update={"amount": Decimal("82500.00")})
    _, violation, _ = validate_response(
        _response(["INV-0042", "INV-0043"], [("INV-0042", "82500.00")]),
        txn, ALLOWED, CFG)
    assert violation == ALLOCATION_MISMATCH


def test_over_allocation_is_rejected():
    """Allocating more than the credit is money invented out of nothing."""
    _, violation, evidence = validate_response(
        _response(["INV-0042"], [("INV-0042", "99999.00")]), TXN, ALLOWED, CFG)

    assert violation == OVER_ALLOCATED
    assert evidence["total_allocated"] == Decimal("99999.00")


@pytest.mark.parametrize("amount", ["0", "-500.00", "about four thousand", "",
                                    "41250.00 rupees", "4,12,50.0.0", "1e5"])
def test_unusable_allocation_amounts_are_rejected(amount):
    _, violation, _ = validate_response(
        _response(["INV-0042"], [("INV-0042", amount)]), TXN, ALLOWED, CFG)
    assert violation == ALLOCATION_INVALID


@pytest.mark.parametrize("written", [
    "41250.00", "41,250.00", "Rs 41250.00", "Rs. 41,250.00", "rs41250.00",
    "INR 41,250.00", "₹41,250.00", "  41,250.00  ",
])
def test_currency_formatting_does_not_discard_a_correct_answer(written):
    """The prompt prints amounts as 'Rs 60,232.20', so the model writes them
    back that way. Measured on batch_dev: 7 of the first 26 adjudications were
    correct matches thrown away on exactly this. Normalising the presentation
    is not leniency about the value -- the rejections above still reject."""
    from ledgerloop.llm import parse_money

    assert parse_money(written) == Decimal("41250.00")

    result, violation, _ = validate_response(
        _response(["INV-0042"], [("INV-0042", written)]), TXN, ALLOWED, CFG)
    assert violation is None
    assert result.allocated == {"INV-0042": Decimal("41250.00")}


@pytest.mark.parametrize("confidence", [1.4, -0.2])
def test_confidence_outside_the_unit_interval_is_rejected(confidence):
    _, violation, _ = validate_response(
        _response(["INV-0042"], [("INV-0042", "41250.00")], confidence=confidence),
        TXN, ALLOWED, CFG)
    assert violation == CONFIDENCE_RANGE


def test_abstention_is_not_a_violation():
    """Invariant 5. Declining to guess is the behaviour we want, so it must not
    be recorded as a model failure -- the violation counters feed the report."""
    result, violation, evidence = validate_response(
        _response([], [], confidence=0.2, reasoning="Two invoices fit equally."),
        TXN, ALLOWED, CFG)

    assert violation is None
    assert result is None
    assert evidence["abstained"] is True
    assert evidence["llm_reasoning"] == "Two invoices fit equally."


# --------------------------------------------------------------------------
# Prompt
# --------------------------------------------------------------------------

def test_prompt_contains_every_shown_id_and_no_others():
    prompt = build_prompt(TXN, CANDS, [])
    for c in CANDS:
        assert c.invoice.invoice_id in prompt
    assert "INV-0044" not in prompt
    assert TXN.narration in prompt
    assert "41,250.00" in prompt


def test_shortlist_is_cut_to_the_configured_size():
    wide = [_cand(f"INV-{i:04d}", "41250.00") for i in range(20)]
    shown, _ = select_shown(wide, [], CFG.llm)

    assert len(shown) == CFG.llm.max_candidates
    # ranked order preserved -- Stage 0 already decided which eight are best
    assert [c.invoice.invoice_id for c in shown] == \
        [c.invoice.invoice_id for c in wide[: CFG.llm.max_candidates]]


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------

def test_cache_key_ignores_candidate_order_but_not_membership():
    a = cache_key(TXN, ["INV-0042", "INV-0043"], CFG)
    b = cache_key(TXN, ["INV-0043", "INV-0042"], CFG)
    c = cache_key(TXN, ["INV-0042"], CFG)

    assert a == b
    assert a != c


def test_cache_key_changes_with_the_model():
    other = CFG.model_copy(update={
        "llm": CFG.llm.model_copy(update={"provider": "anthropic"})})
    assert cache_key(TXN, ALLOWED, CFG) != cache_key(TXN, ALLOWED, other)


def test_cache_round_trip(tmp_path: Path):
    cache = ResponseCache(tmp_path)
    assert cache.get("missing") is None

    cache.put("k", Completion("body", 100, 20), {"txn_id": "TXN-0001"})
    got = cache.get("k")

    assert (got.text, got.tokens_in, got.tokens_out) == ("body", 100, 20)


# --------------------------------------------------------------------------
# Adjudicator: failure handling and the cache path
# --------------------------------------------------------------------------

class _ScriptedClient:
    """Returns queued responses; records how many times it was called."""
    name = "scripted"

    def __init__(self, *responses, raises: Exception | None = None):
        self.responses = list(responses)
        self.raises = raises
        self.calls = 0

    def complete(self, system, user, schema):
        self.calls += 1
        if self.raises:
            raise self.raises
        return Completion(self.responses.pop(0), 500, 50)


def test_timeout_escalates_and_never_guesses(tmp_path: Path):
    """3.4: exceptions.llm_timeout now has a reader, and its answer is EXCEPTION."""
    adj = Adjudicator(cfg=CFG, client=_ScriptedClient(raises=LLMTimeout("slow")),
                      cache=ResponseCache(tmp_path))
    verdict = adj.adjudicate(TXN, CANDS, [])

    assert verdict.violation == LLM_TIMEOUT
    assert verdict.result is None
    assert verdict.forced[0] == "EXCEPTION"
    assert adj.stats["violations"] == 1


def test_a_rejected_key_stops_the_run_instead_of_filling_the_queue(tmp_path: Path):
    """A setup failure is not a hard transaction.

    A bad key, or a model the account cannot reach, fails identically for every
    line on the statement. Swallowing it per-transaction would write 110
    EXCEPTION records and a report that reads like a difficult batch, which is
    the exact opposite of honest exception reporting.
    """
    from ledgerloop.llm import LLMUnavailable

    adj = Adjudicator(cfg=CFG,
                      client=_ScriptedClient(raises=LLMUnavailable("403 blocked")),
                      cache=ResponseCache(tmp_path))

    with pytest.raises(LLMUnavailable):
        adj.adjudicate(TXN, CANDS, [])
    assert adj.stats["violations"] == 0


def test_schema_failure_is_reported_as_itself(tmp_path: Path):
    """A budget too small to hold the answer must not read as 'the API failed'.

    Under strict structured output the provider returns an empty 400, so the
    only place this can be named is here. Reported generically it sends you
    debugging the network instead of llm.max_tokens -- which is what it cost
    on the first live run of batch_dev.
    """
    from ledgerloop.llm import LLMSchemaFailure, SCHEMA_UNSATISFIED

    adj = Adjudicator(cfg=CFG,
                      client=_ScriptedClient(raises=LLMSchemaFailure("json_validate_failed")),
                      cache=ResponseCache(tmp_path))
    verdict = adj.adjudicate(TXN, CANDS, [])

    assert verdict.violation == SCHEMA_UNSATISFIED
    assert verdict.violation != API_ERROR
    assert verdict.forced[0] == "EXCEPTION"


def test_api_failure_escalates(tmp_path: Path):
    adj = Adjudicator(cfg=CFG, client=_ScriptedClient(raises=ConnectionError("down")),
                      cache=ResponseCache(tmp_path))
    verdict = adj.adjudicate(TXN, CANDS, [])

    assert verdict.violation == API_ERROR
    assert verdict.forced[0] == "EXCEPTION"


def test_second_ask_of_the_same_question_is_not_re_billed(tmp_path: Path):
    body = _response(["INV-0042"], [("INV-0042", "41250.00")])
    client = _ScriptedClient(body, body)
    adj = Adjudicator(cfg=CFG, client=client, cache=ResponseCache(tmp_path))

    first = adj.adjudicate(TXN, CANDS, [])
    second = adj.adjudicate(TXN, CANDS, [])

    assert client.calls == 1
    assert first.cached is False and second.cached is True
    assert adj.stats["cache_hits"] == 1
    assert second.result.invoice_ids == ["INV-0042"]


# --------------------------------------------------------------------------
# End to end through the engine
# --------------------------------------------------------------------------

def _residual_batch() -> Batch:
    """Exactly the shape Stage 2 exists for.

    Two open invoices from the same customer for the identical amount, and a
    credit matching both to the paisa. R1 sees two exact matches and abstains
    (invariant 5); no other rule has anything to say. A human would read the
    narration and the dates -- which is the question the model is handed.
    """
    ledger = [_inv("INV-0042", "41250.00"), _inv("INV-0043", "41250.00")]
    txn = BankTransaction(
        txn_id="TXN-9001", value_date=date(2026, 1, 20), amount=Decimal("41250.00"),
        direction="CREDIT", narration="NEFT/MERIDIAN TEXTILES PVT LTD/PAYMENT",
        utr="N026250099999", balance_after=Decimal("900000.00"),
    )
    return Batch(name="residual", bank=[txn], ledger=ledger)


def test_engine_records_an_llm_decision_with_tokens():
    batch = _residual_batch()
    body = _response(["INV-0042"], [("INV-0042", "41250.00")],
                     confidence=0.8, reasoning="Counterparty named in narration.")
    adj = Adjudicator(cfg=CFG, client=_ScriptedClient(body), cache=None)

    [decision] = reconcile(batch, CFG, use_llm=True, adjudicator=adj)

    assert decision.decided_by == "LLM"
    assert decision.rule_id == RULE_ID
    assert decision.proposed_invoice_ids == ["INV-0042"]
    assert decision.llm_tokens_in == 500 and decision.llm_tokens_out == 50
    assert decision.outcome == "NEEDS_REVIEW"
    assert decision.evidence["llm_model"] == CFG.llm.active.model


def test_engine_escalates_a_hallucination_and_keeps_the_evidence():
    """The audit trail has to say *why* this landed in the queue."""
    batch = _residual_batch()
    body = _response(["INV-0099"], [("INV-0099", "41250.00")], confidence=0.97)
    adj = Adjudicator(cfg=CFG, client=_ScriptedClient(body), cache=None)

    [decision] = reconcile(batch, CFG, use_llm=True, adjudicator=adj)

    assert decision.outcome == "EXCEPTION"
    assert decision.decided_by == "LLM"
    assert decision.proposed_invoice_ids == []
    assert decision.confidence == 0.0
    assert decision.evidence["hallucinated_ids"] == ["INV-0099"]
    assert "outside the candidate list" in decision.reasoning


def test_adjudication_stays_off_when_the_config_says_so():
    """`llm.adjudicate: false` records a measured decision -- the model scored
    0.43 link precision against 0.994 for the rules. A run that builds an
    adjudicator anyway silently reverses that decision, which is how a config
    file stops describing the system it configures."""
    from ledgerloop.engine import run_pipeline

    off = CFG.model_copy(update={
        "llm": CFG.llm.model_copy(update={"adjudicate": False})})
    entry = _inv("INV-0042", "50000.00")
    txn = TXN.model_copy(update={"amount": Decimal("47300.00"),
                                 "narration": "NEFT/MERIDIAN TEXTILES/PAYMENT"})

    # use_llm=True and no adjudicator passed: the engine must not build one
    effective, _ = run_pipeline(Batch(name="off", bank=[txn], ledger=[entry]),
                                off, use_llm=True)

    assert all(d.decided_by == "RULE" for d in effective)


def test_rules_decisions_are_never_labelled_llm():
    """The invocation rate is computed from decided_by, so a rule that fired
    must not be counted as an LLM call just because Stage 2 was enabled."""
    entry = _inv("INV-0042", "41250.00")
    txn = TXN.model_copy(update={"narration": "NEFT/MERIDIAN TEXTILES/INV0042"})
    client = _ScriptedClient()
    adj = Adjudicator(cfg=CFG, client=client, cache=None)

    [decision] = reconcile(Batch(name="clean", bank=[txn], ledger=[entry]),
                           CFG, use_llm=True, adjudicator=adj)

    assert decision.decided_by == "RULE"
    assert decision.llm_tokens_in is None
    assert client.calls == 0


def test_no_candidates_means_no_call():
    """An empty shortlist is unanswerable, not hard -- asking would only give
    the model an opportunity to invent an id."""
    txn = TXN.model_copy(update={"amount": Decimal("3.00"),
                                 "narration": "ATM CASH WDL"})
    client = _ScriptedClient()
    adj = Adjudicator(cfg=CFG, client=client, cache=None)

    [decision] = reconcile(Batch(name="orphan", bank=[txn], ledger=[]),
                           CFG, use_llm=True, adjudicator=adj)

    assert client.calls == 0
    assert decision.decided_by == "RULE"
    assert decision.outcome == "EXCEPTION"
