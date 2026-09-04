"""End-to-end tests for the reconciliation engine (§13).

The rule tests upstream check each rule against a hand-built shortlist. Nothing
there notices if the engine stops calling one of them, drops a bank line on the
floor, or edits an audit record in place -- so this file runs the real pipeline
over real data and asserts the things that are only true of the whole.

The floor is the important part. It is not a target; it is a tripwire set just
under what the pipeline currently measures, so a change that quietly costs
accuracy fails the build instead of showing up three commits later in a report
nobody re-read. When a change earns better numbers, raise the floor in the same
commit -- that is the improvement trajectory the reports are meant to show.
"""

import json
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerloop.config import load_config
from ledgerloop.engine import NO_CANDIDATES, reconcile
from ledgerloop.evaluate import evaluate_matches
from ledgerloop.loaders import Batch, load_batch
from ledgerloop.models import BankTransaction

ROOT = Path(__file__).resolve().parents[1]
CFG = load_config()

# batch_holdout is deliberately absent: see CLAUDE.md invariant 1.
FIXTURE_BATCH = "dev"
FIXTURE_ROWS = 50

# Measured on the fixture (auto precision 1.000, auto-match 0.640, recall
# 0.762, missed escalation 0.000), then set a few transactions below -- one row
# out of fifty moves a rate by 0.02, and a tripwire that trips on noise gets
# raised until it stops meaning anything.
#
# The two coverage floors are set from what the pipeline does today; the other
# two are the spec's own bars, and those do not move. Precision on anything
# posted without a human is the one that must never slip: a wrong auto-match
# posts to the books, a missed one costs somebody two minutes.
FLOOR = {
    "auto_precision": 0.98,           # spec §12
    "auto_match_rate": 0.60,
    "recall": 0.72,
    "missed_escalation_rate": 0.02,   # spec §12; a maximum, not a minimum
}


@pytest.fixture(scope="module")
def batch() -> Batch:
    """The first 50 bank lines of batch_dev, against the whole ledger.

    Slicing the statement and not the ledger is deliberate: blocking has to do
    its real job of picking ~20 candidates out of 500, which is where a
    regression would actually show up. Fifty lines keeps `make test` quick and
    still covers every scenario the generator emits.
    """
    if not (ROOT / f"data/batch_{FIXTURE_BATCH}").exists():
        pytest.skip(f"batch_{FIXTURE_BATCH} not generated; run `make data`")
    full = load_batch(ROOT / f"data/batch_{FIXTURE_BATCH}")
    return Batch(name=f"{FIXTURE_BATCH}_fixture50",
                 bank=full.bank[:FIXTURE_ROWS], ledger=full.ledger)


@pytest.fixture(scope="module")
def decisions(batch):
    return reconcile(batch, CFG, use_llm=False)


@pytest.fixture(scope="module")
def metrics(batch, decisions, tmp_path_factory):
    """Score the fixture against its own slice of the answer key.

    evaluate.py divides rates by the number of truth rows, so the truth file
    has to be cut to the same 50 transactions -- handing it the full answer key
    would count 470 transactions the engine was never given as failures.
    """
    truth = json.loads((ROOT / f"data/batch_{FIXTURE_BATCH}/truth.json").read_text())
    keep = {t.txn_id for t in batch.bank}
    sliced = tmp_path_factory.mktemp("truth") / "truth.json"
    sliced.write_text(json.dumps([t for t in truth if t["txn_id"] in keep]))
    return evaluate_matches(sliced, decisions)


# ---------------------------------------------------------------------------
# The floor
# ---------------------------------------------------------------------------

def test_auto_matched_links_stay_above_the_precision_floor(metrics):
    """The expensive failure: posted automatically, and wrong."""
    got = metrics["auto"]["precision"]
    assert got >= FLOOR["auto_precision"], (
        f"auto precision fell to {got:.3f}, floor is {FLOOR['auto_precision']}. "
        "A precision regression is never an acceptable price for recall unless "
        "it is called out and justified -- see CLAUDE.md."
    )


def test_nothing_posts_automatically_on_a_partial_answer(metrics):
    """A consolidated payment with 2 of 3 invoices found is still a bad post,
    so this compares whole answers, not links."""
    got = metrics["missed_escalation_rate"]
    assert got <= FLOOR["missed_escalation_rate"], (
        f"missed-escalation rate rose to {got:.3f}, ceiling is "
        f"{FLOOR['missed_escalation_rate']}: {metrics['missed_escalation_txns']}"
    )


@pytest.mark.parametrize("name, path", [
    ("auto_match_rate", ("auto_match_rate",)),
    ("recall", ("overall", "recall")),
])
def test_coverage_stays_above_the_floor(metrics, name, path):
    got = metrics
    for key in path:
        got = got[key]
    assert got >= FLOOR[name], (
        f"{name} fell to {got:.3f}, floor is {FLOOR[name]}. Run "
        f"`make eval BATCH={FIXTURE_BATCH}` and compare against the last "
        "committed report in reports/."
    )


# ---------------------------------------------------------------------------
# Invariants of the pipeline itself -- true whatever the numbers say
# ---------------------------------------------------------------------------

def test_every_bank_line_produces_exactly_one_effective_decision(batch, decisions):
    """A dropped transaction raises nothing. It quietly inflates every rate in
    the report instead, because evaluate.py divides by the truth file's length
    and not by the number of decisions it was handed.
    """
    assert len(decisions) == len(batch.bank)
    assert {d.txn_id for d in decisions} == {t.txn_id for t in batch.bank}


def test_every_decision_carries_the_four_evidence_keys(decisions):
    """An unexplained match is a bug even when it is correct."""
    for d in decisions:
        if not d.proposed_invoice_ids:
            continue                       # an abstention explains itself in `reasoning`
        missing = {"amount_delta", "date_gap_days", "name_similarity", "ref_hit"} - set(d.evidence)
        assert not missing, f"{d.txn_id} ({d.rule_id}) is missing {missing}"
        assert d.reasoning


def test_every_proposal_comes_from_the_shortlist_it_was_offered(decisions):
    """Both shortlists, single-invoice and consolidated. A proposal from
    outside them is an invoice nothing ever surfaced -- the rule equivalent of
    the hallucination check invariant 3 puts on the LLM.
    """
    for d in decisions:
        outside = set(d.proposed_invoice_ids) - set(d.candidates_considered)
        assert not outside, f"{d.txn_id} ({d.rule_id}) proposed unlisted {outside}"


def test_an_auto_match_never_allocates_more_than_the_invoice_is_owed(batch, decisions):
    """Overpayments are the trap: the excess belongs nowhere, and allocating
    the whole credit would overstate what the invoice was worth."""
    gross = {e.invoice_id: e.gross_amount for e in batch.ledger}
    for d in decisions:
        if d.outcome != "AUTO_MATCHED":
            continue
        for inv_id, amount in d.allocated.items():
            assert amount <= gross[inv_id] + CFG.tolerances.amount_exact, (
                f"{d.txn_id} ({d.rule_id}) allocated {amount} to {inv_id}, "
                f"which is owed {gross[inv_id]}")


def test_confidence_and_outcome_never_disagree(decisions):
    """Routing is the engine's only judgement call, and it is arithmetic."""
    for d in decisions:
        if d.outcome == "AUTO_MATCHED":
            assert d.confidence >= CFG.thresholds.auto_match
        elif d.outcome == "NEEDS_REVIEW":
            assert CFG.thresholds.exception <= d.confidence < CFG.thresholds.auto_match
        else:
            assert not d.proposed_invoice_ids or d.confidence < CFG.thresholds.exception


def test_an_abstention_says_which_kind_it_is(decisions):
    """'What is this money' and 'which of these three' are different jobs for
    the reviewer, and the queue has to tell them apart from the record alone."""
    for d in decisions:
        if d.outcome != "EXCEPTION":
            continue
        assert d.reasoning
        if d.reasoning == NO_CANDIDATES:
            assert not d.candidates_considered


# ---------------------------------------------------------------------------
# The audit trail
# ---------------------------------------------------------------------------

def test_a_duplicate_credit_is_superseded_rather_than_edited(batch, decisions):
    """Invariant 2: corrections append a new record pointing back at the old one.

    Two identical credits for one invoice: whichever was physically real, the
    invoice is settled once and the other is left unapplied for a human. The
    engine cannot see this from inside a rule -- a rule is handed one
    transaction at a time -- which is why it is a second pass.
    """
    settled = {d.txn_id for d in decisions if d.outcome == "AUTO_MATCHED"}
    original = next(t for t in batch.bank if t.txn_id in settled)
    twin = BankTransaction(**{**original.model_dump(),
                              "txn_id": "BNK-TWIN",
                              "value_date": original.value_date + timedelta(days=1)})
    got = reconcile(Batch(name="dup", bank=[original, twin], ledger=batch.ledger),
                    CFG, use_llm=False)
    by_id = {d.txn_id: d for d in got}

    loser = by_id["BNK-TWIN"]
    assert loser.outcome == "EXCEPTION"
    assert loser.rule_id == "DEDUP"
    assert loser.proposed_invoice_ids == []
    assert loser.supersedes is not None          # the trail links back
    assert loser.evidence["settled_by"] == original.txn_id
    # the earlier record is untouched: the earliest credit keeps the invoice
    assert by_id[original.txn_id].outcome == "AUTO_MATCHED"


def test_a_legitimate_split_across_two_credits_is_not_flagged_as_duplicate(batch):
    """MUST NOT FIRE: two installments summing to the invoice are one payment
    in two parts, not one payment made twice. Only the *sum* can tell them
    apart, which is why the pass adds allocations rather than counting claims.
    """
    entry = next(e for e in batch.ledger if e.gross_amount > Decimal("1000"))
    half = (entry.gross_amount / 2).quantize(Decimal("0.01"))
    parts = [
        BankTransaction(
            txn_id=f"BNK-SPLIT{k}", value_date=entry.issue_date + timedelta(days=5 + k),
            amount=amount, direction="CREDIT",
            narration=f"NEFT/{entry.invoice_id.split('-')[-1]}/PARTPAY",
            utr=None, balance_after=Decimal("1000000"))
        for k, amount in enumerate([half, entry.gross_amount - half])
    ]
    got = reconcile(Batch(name="split", bank=parts, ledger=[entry]), CFG, use_llm=False)
    assert [d.rule_id for d in got] == ["R5_UNDERPAID", "R5_UNDERPAID"]
    assert sum(d.allocated[entry.invoice_id] for d in got) == entry.gross_amount
