"""The UI's explanatory copy has to keep up with the engine.

A judge or a reviewer meeting this app for the first time reads `R7_SPLIT` in a
table and needs a sentence, not a grep. These tests fail when a rule is added
without one -- which is the only way that copy stays true, since nothing else
breaks when it goes stale.
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "ledgerloop"


def _app_dict(name: str) -> dict:
    """Read a literal dict out of app.py without importing Streamlit."""
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in app.py")


def _emitted_rule_ids() -> set[str]:
    """Every rule_id the engine can actually write to a decision."""
    found: set[str] = set()
    for path in list(SRC.glob("*.py")) + [ROOT / "app.py"]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.keyword) or node.arg != "rule_id":
                continue
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                found.add(node.value.value)
            elif isinstance(node.value, ast.JoinedStr):
                # rule_id=f"REVIEW_{action}" -- the reviewer actions
                found.update({"REVIEW_ACCEPT", "REVIEW_REJECT", "REVIEW_WRITE_OFF"})
    return found


def test_every_rule_the_engine_emits_has_a_plain_english_line():
    described = set(_app_dict("RULE_MEANING"))
    missing = _emitted_rule_ids() - described

    assert not missing, (
        f"these rule ids can reach the UI with no explanation: {sorted(missing)}. "
        "Add a line to RULE_MEANING in app.py.")


def test_rule_descriptions_are_sentences_not_restated_ids():
    for rule_id, text in _app_dict("RULE_MEANING").items():
        assert len(text) > 25, f"{rule_id}: too short to explain anything"
        assert rule_id.lower().replace("_", " ") not in text.lower(), \
            f"{rule_id}: the description just repeats the id"


def test_every_outcome_is_explained():
    from ledgerloop.models import MatchDecision

    outcomes = set(MatchDecision.model_fields["outcome"].annotation.__args__)
    assert outcomes == set(_app_dict("OUTCOME_MEANING"))


@pytest.mark.parametrize("metric", [
    "Auto-match rate", "Precision (auto only)", "Recall (all outcomes)",
    "Abstention precision", "Missed escalation",
])
def test_every_metric_shown_has_a_meaning(metric):
    """The metrics table is the first thing a judge reads. A row of numbers
    with no gloss is a row of numbers nobody can weigh."""
    meanings = _app_dict("METRIC_MEANING")
    assert metric in meanings
    assert len(meanings[metric]) > 30
