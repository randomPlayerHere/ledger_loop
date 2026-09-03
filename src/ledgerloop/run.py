"""CLI: run the pipeline over a batch, score it, write a report.

    python -m ledgerloop.run --batch dev --no-llm
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from .config import load_config
from .engine import reconcile
from .evaluate import evaluate_matches, write_report
from .loaders import load_batch

logger = logging.getLogger(__name__)

TARGETS = [
    ("auto-match rate", "auto_match_rate", ">= 0.80", 0.80, "min"),
    ("precision (auto)", None, ">= 0.98", 0.98, "min"),
    ("recall (all)", None, ">= 0.93", 0.93, "min"),
    ("abstention precision", "abstention_precision", ">= 0.70", 0.70, "min"),
    ("missed escalation", "missed_escalation_rate", "<= 0.02", 0.02, "max"),
    ("LLM invocation", "llm_invocation_rate", "<= 0.25", 0.25, "max"),
]


def _summary(m: dict) -> str:
    values = {
        "auto-match rate": m["auto_match_rate"],
        "precision (auto)": m["auto"]["precision"],
        "recall (all)": m["overall"]["recall"],
        "abstention precision": m["abstention_precision"],
        "missed escalation": m["missed_escalation_rate"],
        "LLM invocation": m["llm_invocation_rate"],
    }
    lines = [f"{'metric':<22} {'value':>7}  {'target':<9} ",
             "-" * 45]
    for label, _, target_txt, target, direction in TARGETS:
        v = values[label]
        ok = v >= target if direction == "min" else v <= target
        lines.append(f"{label:<22} {v:>7.3f}  {target_txt:<9} {'ok' if ok else 'MISS'}")
    lines += [
        "-" * 45,
        f"{'false-match value':<22} Rs {m['false_match_value']:,.2f}",
        f"{'throughput':<22} {m['throughput_per_min']:,.0f} txns/min",
        "",
        "outcomes: " + "  ".join(f"{k} {v}" for k, v in m["outcomes"].items()),
        f"links: TP {m['overall']['tp']}  FP {m['overall']['fp']}  FN {m['overall']['fn']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ledgerloop.run")
    p.add_argument("--batch", default="dev", help="dev | stress | holdout")
    p.add_argument("--data-dir", type=Path, default=Path("data"))
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--reports-dir", type=Path, default=Path("reports"))
    p.add_argument("--no-llm", action="store_true", help="rules only, skip Stage 2")
    p.add_argument("--no-report", action="store_true", help="print only, write nothing")
    p.add_argument("--label", default=None, help="report filename suffix")
    p.add_argument("--allow-holdout", action="store_true",
                   help="required to run against the holdout batch")
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")

    # Invariant 1: the holdout is not something you run by accident. Making it
    # an explicit flag means a holdout number is always a deliberate act.
    if a.batch == "holdout" and not a.allow_holdout:
        print("refusing to run against the holdout batch without --allow-holdout.\n"
              "A number you tuned against is not a metric. See CLAUDE.md invariant 1.",
              file=sys.stderr)
        return 2

    batch_dir = a.data_dir / f"batch_{a.batch}"
    truth = batch_dir / "truth.json"

    cfg = load_config(a.config)
    batch = load_batch(batch_dir)

    started = time.perf_counter()
    decisions = reconcile(batch, cfg, use_llm=not a.no_llm)
    elapsed = time.perf_counter() - started

    metrics = evaluate_matches(truth, decisions, elapsed_seconds=elapsed)

    print(f"\nbatch_{a.batch} - {metrics['n_txns']} transactions, "
          f"{metrics['overall']['n_truth_links']} truth links "
          f"({elapsed:.2f}s{', rules only' if a.no_llm else ''})\n")
    print(_summary(metrics))

    if not a.no_report:
        name = f"{a.batch}_{a.label}" if a.label else a.batch
        path = write_report(metrics, name, reports_dir=a.reports_dir)
        print(f"\nwrote {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
