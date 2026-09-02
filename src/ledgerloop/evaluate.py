"""Evaluation harness: metrics computation and reporting.

Two different units get counted in this file, and keeping them apart is the
whole trick:

  * a TRANSACTION is one line on the bank statement
  * a LINK is one (txn_id, invoice_id) connection the engine draws

They differ because a single payment can settle several invoices. Accuracy is
therefore measured per LINK: scored per transaction, a consolidated payment
where 2 of 3 invoices were found would collapse into a single "wrong" and hide
the detail. Rates like auto-match% and LLM-invocation% are per TRANSACTION,
because they answer "how much human work did we avoid", not "were we right".

Nothing here mutates state or calls the engine -- it reads the answer key,
reads a list of decisions, and returns numbers.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from .models import MatchDecision

logger = logging.getLogger(__name__)

# Truth rows at these difficulties are the ones the engine is *supposed* to
# give up on. Used to score whether an abstention was well-judged.
_HARD_DIFFICULTIES = {"HARD", "IMPOSSIBLE"}


# ---------------------------------------------------------------------------
# Small math helpers
# ---------------------------------------------------------------------------

def _precision(tp: int, total_pred: int) -> float:
    # A zero denominator is a normal state here, not an error: an all-abstain
    # run predicts nothing, and per-slice breakdowns routinely have empty
    # buckets (no predictions on IMPOSSIBLE is the *correct* behaviour).
    return tp / total_pred if total_pred else 0.0

def _recall(tp: int, total_truth: int) -> float:
    return tp / total_truth if total_truth else 0.0

def _f1(precision: float, recall: float) -> float:
    return (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0


# ---------------------------------------------------------------------------
# The core comparison -- every accuracy number in the report comes from here
# ---------------------------------------------------------------------------

def _link_metrics(
        decisions: list[MatchDecision],
        truth_links: set[tuple[str, str]],
        ) -> dict:
    """Score one set of decisions against one set of truth links.

    Deliberately takes its inputs as arguments rather than computing them,
    so it can be called repeatedly over *subsets*: all decisions, auto-matched
    only, one difficulty band, one link_type. That reuse is why the headline
    numbers and every breakdown row share identical maths.
    """
    pred_links = {(d.txn_id, inv) for d in decisions for inv in d.proposed_invoice_ids}

    # Set algebra is the entire comparison. A predicted link is either in the
    # answer key (true positive) or invented (false positive); a truth link
    # that was never predicted is a false negative.
    tp = pred_links & truth_links
    fp = pred_links - truth_links
    fn = truth_links - pred_links

    precision = _precision(len(tp), len(pred_links))
    recall = _recall(len(tp), len(truth_links))

    return {
        "n_pred_links": len(pred_links),
        "n_truth_links": len(truth_links),
        "tp": len(tp),
        "fp": len(fp),
        "fn": len(fn),
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        # The actual FP pairs, not just the count -- the caller needs them to
        # price the wrong matches in rupees. Not JSON-serialisable; the report
        # writer ignores it.
        "fp_links": fp,
    }


def _breakdown(
        truth_data: list[dict],
        decisions: list[MatchDecision],
        truth_links: set[tuple[str, str]],
        key: str,
        ) -> dict[str, dict]:
    """Re-score the batch one slice at a time, grouped by a truth field.

    Used for both the difficulty and link_type tables. The difficulty table
    answers "are we failing where we should be?"; the link_type table is where
    the README honestly admits which scenario is weakest.
    """
    groups: dict[str, set[str]] = defaultdict(set)
    for t in truth_data:
        groups[t[key]].add(t["txn_id"])

    out: dict[str, dict] = {}
    for name, txn_ids in sorted(groups.items()):
        slice_decisions = [d for d in decisions if d.txn_id in txn_ids]
        slice_truth = {(txn, inv) for (txn, inv) in truth_links if txn in txn_ids}
        row = _link_metrics(slice_decisions, slice_truth)
        row["n_txns"] = len(txn_ids)
        out[name] = row
    return out


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def evaluate_matches(
        truth_json_path: Path,
        match_result: list[MatchDecision],
        price_per_mtok: tuple[Decimal, Decimal] | None = None,
        elapsed_seconds: float | None = None,
        ) -> dict:
    """Score a batch of decisions against its answer key.

    price_per_mtok -- (input, output) rupees per million tokens. Passed in
    rather than read here so no pricing constant is hardcoded in this module
    (see CLAUDE.md: tunable policy belongs in config.yaml). None skips costing.
    elapsed_seconds -- real wall-clock from the caller, for throughput.
    """
    if not truth_json_path.exists():
        logger.error("Failed to load the truth file at path %s", truth_json_path.absolute())
        raise FileNotFoundError(truth_json_path)

    with truth_json_path.open("r", encoding="utf-8") as file:
        truth_data = json.load(file)

    # Lookup table: every "was this txn hard?" question below becomes a dict
    # hit instead of a scan over the whole answer key.
    truth_by_txn = {t["txn_id"]: t for t in truth_data}
    decisions_by_txn = {d.txn_id: d for d in match_result}

    # One truth row exists per bank transaction -- orphans included, carrying
    # an empty invoice_ids. So this is the real transaction count, and it is
    # the denominator for every *rate* below. Using len(match_result) instead
    # would quietly forgive an engine that dropped rows on the floor.
    n_txns = len(truth_data)

    unknown = set(decisions_by_txn) - set(truth_by_txn)
    if unknown:
        logger.warning("decisions reference %d txn_ids absent from truth", len(unknown))

    # Orphans and duplicates contribute no links at all: the `if t["invoice_ids"]`
    # guard drops them, which is what makes "correctly matched nothing" scoreable
    # as an abstention rather than as a recall miss.
    truth_links = {
        (t["txn_id"], inv)
        for t in truth_data if t["invoice_ids"]
        for inv in t["invoice_ids"]
    }

    overall = _link_metrics(match_result, truth_links)

    # A wrong AUTO_MATCHED link posts to the books with nobody looking; a wrong
    # NEEDS_REVIEW link costs a human two seconds to reject. Scoring them
    # together lets cheap errors mask expensive ones -- hence a separate, and
    # much higher, precision bar on this slice alone (spec: >=0.98).
    # Note its recall is measured against ALL truth links, so it reads as
    # "share of the batch we resolved automatically and correctly" -- coverage,
    # not a defect.
    auto = [d for d in match_result if d.outcome == "AUTO_MATCHED"]
    auto_metrics = _link_metrics(auto, truth_links)

    n_auto = len(auto)
    n_review = sum(1 for d in match_result if d.outcome == "NEEDS_REVIEW")
    n_exception = sum(1 for d in match_result if d.outcome == "EXCEPTION")
    n_llm = sum(1 for d in match_result if d.decided_by == "LLM")

    # Abstention precision -- the differentiator. When the engine gave up, was
    # it giving up on something genuinely hard? Bailing on an EASY transaction
    # is a failure even though it produces no wrong link, and no other metric
    # in this report would catch it.
    excepted = [d for d in match_result if d.outcome == "EXCEPTION"]
    good_abstentions = [
        d for d in excepted
        if truth_by_txn.get(d.txn_id, {}).get("difficulty") in _HARD_DIFFICULTIES
    ]
    abstention_precision = _precision(len(good_abstentions), len(excepted))

    # The expensive failure mode: posted automatically, and wrong. Compared as
    # whole sets because a consolidated payment is only correct if *every*
    # invoice in it is correct -- 2 of 3 is still a bad post.
    missed_escalations = [
        d for d in auto
        if set(d.proposed_invoice_ids)
        != set(truth_by_txn.get(d.txn_id, {}).get("invoice_ids", []))
    ]

    # Rupee weight of the wrong links: "we would have misposted Rs X". Uses the
    # amount the engine itself claimed to allocate, so this module stays
    # self-contained and never has to read bank.csv.
    false_match_value = Decimal("0")
    for txn_id, inv in overall["fp_links"]:
        d = decisions_by_txn.get(txn_id)
        if d is not None:
            false_match_value += Decimal(d.allocated.get(inv, 0))

    tokens_in = sum(d.llm_tokens_in or 0 for d in match_result)
    tokens_out = sum(d.llm_tokens_out or 0 for d in match_result)

    cost = cost_per_1k_txns = None
    if price_per_mtok is not None:
        price_in, price_out = price_per_mtok
        cost = (Decimal(tokens_in) / 1_000_000 * price_in
                + Decimal(tokens_out) / 1_000_000 * price_out)
        cost_per_1k_txns = (cost / n_txns * 1000) if n_txns else None

    # Prefer real wall-clock from the caller. The fallback sums per-decision
    # latency, which ignores concurrency and so *understates* throughput --
    # fine as a floor, not a number to quote as the headline.
    summed_latency_s = sum(d.latency_ms for d in match_result) / 1000
    seconds = elapsed_seconds if elapsed_seconds is not None else summed_latency_s
    throughput_per_min = (n_txns / seconds * 60) if seconds else None

    return {
        "n_txns": n_txns,
        "n_decisions": len(match_result),
        "overall": overall,
        "auto": auto_metrics,
        "outcomes": {
            "AUTO_MATCHED": n_auto,
            "NEEDS_REVIEW": n_review,
            "EXCEPTION": n_exception,
        },
        "auto_match_rate": n_auto / n_txns if n_txns else 0.0,
        "llm_invocation_rate": n_llm / n_txns if n_txns else 0.0,
        "abstention_precision": abstention_precision,
        "n_abstentions": len(excepted),
        "missed_escalation_rate": len(missed_escalations) / n_txns if n_txns else 0.0,
        "missed_escalation_txns": [d.txn_id for d in missed_escalations],
        "false_match_value": false_match_value,
        "by_difficulty": _breakdown(truth_data, match_result, truth_links, "difficulty"),
        "by_link_type": _breakdown(truth_data, match_result, truth_links, "link_type"),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost": cost,
        "cost_per_1k_txns": cost_per_1k_txns,
        "throughput_per_min": throughput_per_min,
        "wall_clock_seconds": elapsed_seconds,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt(value, spec: str = ".3f") -> str:
    """None-tolerant formatter -- cost and throughput are legitimately absent
    on a --no-llm run, and should read as '-' rather than crash the report."""
    return "-" if value is None else format(value, spec)


def _metrics_table(rows: dict[str, dict], label: str) -> list[str]:
    """Render one breakdown dict as a markdown table.

    n_pred and n_truth are shown deliberately: in the IMPOSSIBLE band there are
    no truth links at all, so precision/recall are structurally 0.0 and mean
    nothing -- the honest signal there is 'fp', i.e. how many links we invented
    for payments that matched nothing.
    """
    out = [
        f"| {label} | txns | pred | truth | TP | FP | FN | precision | recall | F1 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, m in rows.items():
        out.append(
            f"| {name} | {m.get('n_txns', '-')} | {m['n_pred_links']} | "
            f"{m['n_truth_links']} | {m['tp']} | {m['fp']} | {m['fn']} | "
            f"{_fmt(m['precision'])} | {_fmt(m['recall'])} | {_fmt(m['f1'])} |"
        )
    return out


def write_report(
        metrics: dict,
        batch_name: str,
        reports_dir: Path = Path("reports"),
        ) -> Path:
    """Write the metrics as a committed markdown file.

    Timestamped rather than overwritten on purpose: committing successive
    reports is what shows an improvement trajectory over the build, which is
    part of the credibility story, not just bookkeeping.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = reports_dir / f"eval_{batch_name}_{stamp}.md"

    o, a = metrics["overall"], metrics["auto"]
    lines = [
        f"# Eval — `{batch_name}`",
        "",
        f"Generated {datetime.now():%Y-%m-%d %H:%M:%S} · "
        f"{metrics['n_txns']} transactions · {o['n_truth_links']} truth links",
        "",
        "## Headline",
        "",
        "| Metric | Value | Target |",
        "|---|---|---|",
        f"| Auto-match rate | {_fmt(metrics['auto_match_rate'])} | ≥ 0.80 |",
        f"| Precision (auto only) | {_fmt(a['precision'])} | ≥ 0.98 |",
        f"| Recall (all outcomes) | {_fmt(o['recall'])} | ≥ 0.93 |",
        f"| Abstention precision | {_fmt(metrics['abstention_precision'])} | ≥ 0.70 |",
        f"| Missed-escalation rate | {_fmt(metrics['missed_escalation_rate'])} | ≤ 0.02 |",
        f"| LLM invocation rate | {_fmt(metrics['llm_invocation_rate'])} | ≤ 0.25 |",
        f"| False-match value | ₹{_fmt(metrics['false_match_value'], ',.2f')} | report |",
        f"| Cost per 1,000 txns | {_fmt(metrics['cost_per_1k_txns'], ',.2f')} | report |",
        f"| Throughput (txns/min) | {_fmt(metrics['throughput_per_min'], ',.1f')} | report |",
        "",
        "## Outcomes",
        "",
        "| Outcome | Count |",
        "|---|---|",
    ]
    for name, count in metrics["outcomes"].items():
        lines.append(f"| {name} | {count} |")

    lines += [
        "",
        "## Overall links",
        "",
        f"TP {o['tp']} · FP {o['fp']} · FN {o['fn']} · "
        f"precision {_fmt(o['precision'])} · recall {_fmt(o['recall'])} · F1 {_fmt(o['f1'])}",
        "",
        "## By difficulty",
        "",
        *_metrics_table(metrics["by_difficulty"], "difficulty"),
        "",
        "## By link type",
        "",
        *_metrics_table(metrics["by_link_type"], "link_type"),
        "",
        "## Tokens",
        "",
        f"in {metrics['tokens_in']:,} · out {metrics['tokens_out']:,}",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("wrote eval report", extra={"path": str(path), "batch": batch_name})
    return path
