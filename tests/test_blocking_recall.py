"""Candidate-recall floor for Stage 0 (§13).

Everything downstream is capped by what blocking surfaces, and a recall
regression there is invisible in the rule metrics until a rule that would have
matched simply stops seeing its invoice. This pins the measured floor so the
build breaks instead.

Floors are set a little under the numbers ceiling.py reports, so ordinary noise
does not fail the build but a real regression does. Raise them when a change
earns it -- that is the improvement trajectory the reports are meant to show.
"""

import json
from functools import lru_cache
from pathlib import Path

import pytest

from ledgerloop.candidates import generate_candidates, generate_group_candidates
from ledgerloop.config import load_config
from ledgerloop.loaders import load_batch

ROOT = Path(__file__).resolve().parents[1]
CFG = load_config()

# batch_holdout is deliberately absent: see CLAUDE.md invariant 1.
FLOORS = {"dev": 0.89, "stress": 0.86}


@lru_cache(maxsize=None)
def reachable(batch_name: str) -> tuple[dict[str, tuple[int, int]], float]:
    """Per-link-type (found, total) plus overall recall, both paths combined."""
    root = ROOT / f"data/batch_{batch_name}"
    batch = load_batch(root)
    truth = json.loads((root / "truth.json").read_text())
    by_txn = {t.txn_id: t for t in batch.bank}

    per: dict[str, list[int]] = {}
    found = total = 0
    for link in truth:
        if not link["invoice_ids"]:
            continue
        txn = by_txn[link["txn_id"]]
        seen = {c.invoice.invoice_id
                for c in generate_candidates(txn, batch.ledger, CFG)}
        seen |= {i.invoice_id
                 for g in generate_group_candidates(txn, batch.ledger, CFG)
                 for i in g.invoices}
        row = per.setdefault(link["link_type"], [0, 0])
        for iid in link["invoice_ids"]:
            row[1] += 1
            total += 1
            if iid in seen:
                row[0] += 1
                found += 1
    return {k: tuple(v) for k, v in per.items()}, found / total


@pytest.fixture(scope="module")
def dev():
    return reachable("dev")


@pytest.mark.parametrize("batch_name", sorted(FLOORS))
def test_candidate_recall_floor(batch_name):
    if not (ROOT / f"data/batch_{batch_name}").exists():
        pytest.skip(f"batch_{batch_name} not generated; run `make data`")
    _, recall = reachable(batch_name)
    assert recall >= FLOORS[batch_name], (
        f"candidate recall on batch_{batch_name} fell to {recall:.3f}, "
        f"floor is {FLOORS[batch_name]}. Run `python ceiling.py {batch_name}` "
        f"for the per-link-type breakdown."
    )


def test_scenarios_with_a_clean_signal_stay_fully_reachable(dev):
    """A quoted reference or an explainable delta leaves no excuse for a miss.

    These four are the easy cases; if blocking drops one of them, a threshold
    has been widened or narrowed in a way that broke something basic.
    """
    per, _ = dev
    for link_type in ("CLEAN", "LATE", "SHORT_PAID_TDS", "SHORT_PAID_CHARGES"):
        got, want = per[link_type]
        assert got == want, f"{link_type}: only {got}/{want} reachable"


def test_consolidated_stays_fully_reachable(dev):
    """The group path solved this outright; a drop means it has been broken."""
    got, want = dev[0]["CONSOLIDATED"]
    assert got == want, f"CONSOLIDATED: only {got}/{want} reachable"
