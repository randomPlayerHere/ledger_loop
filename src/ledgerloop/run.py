"""CLI: run the pipeline over a batch, score it, write a report.

    python -m ledgerloop.run --batch dev --no-llm
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from .audit import AuditLog
from .config import load_config
from .engine import run_pipeline
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


def _stage2(adjudicator, cfg) -> str:
    """What Stage 2 actually did, printed next to the metrics.

    The violation breakdown is here rather than buried in logs because it is
    the honest half of the story: 'the model invented an id four times and we
    caught all four' is a result, and a table that only shows the wins is not
    an evaluation.
    """
    s = adjudicator.stats
    lines = [
        f"stage 2 - {cfg.llm.provider}:{cfg.llm.active.model}",
        "-" * 45,
        f"{'live calls':<22} {s['calls']:>7}",
        f"{'cache hits':<22} {s['cache_hits']:>7}",
        f"{'matched':<22} {s['matched']:>7}",
        f"{'abstained':<22} {s['abstentions']:>7}",
        f"{'violations':<22} {s['violations']:>7}",
    ]
    for name, count in sorted(adjudicator.violations.items()):
        lines.append(f"  {name.lower():<20} {count:>7}")
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
    p.add_argument("--no-audit", action="store_true",
                   help="skip writing the SQLite audit trail")
    p.add_argument("--audit-db", type=Path, default=Path("audit.db"))
    p.add_argument("--quiet", action="store_true",
                   help="suppress the per-transaction Stage 2 progress line")
    p.add_argument("--allow-holdout", action="store_true",
                   help="required to run against the holdout batch")
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")

    # Keys live in .env, never in config.yaml -- config.yaml is committed.
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

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

    # Imported unconditionally: LLMUnavailable is named in an except clause
    # below that a --no-llm run still has to be able to evaluate.
    from .llm import LLMUnavailable, build_adjudicator

    # Gated on the config flag, not just on --no-llm. Building the adjudicator
    # here unconditionally silently overrode `llm.adjudicate: false`, because
    # the engine only builds its own when it is handed none -- and a run that
    # ignores the setting that says "we measured this and turned it off" is
    # exactly the kind of quiet disagreement between config and behaviour that
    # makes a measured number untrustworthy.
    adjudicator = None
    if not a.no_llm and cfg.llm.adjudicate:
        try:
            adjudicator = build_adjudicator(cfg)
        except (RuntimeError, ValueError) as e:
            print(f"cannot start Stage 2: {e}", file=sys.stderr)
            return 2

        if not a.quiet:
            # Stage 2 over a full batch is ~20 minutes of network wait. Without
            # this the run prints nothing until it finishes, and a working run
            # is indistinguishable from a hung one.
            def _tick(txn_id: str, verdict) -> None:
                s = adjudicator.stats
                done = s["calls"] + s["cache_hits"]
                mark = ("!" if verdict.violation
                        else "-" if verdict.result is None else "+")
                print(f"  stage2 {done:>4} {mark} {txn_id}"
                      f"  matched {s['matched']} abstained {s['abstentions']}"
                      f" violations {s['violations']}", file=sys.stderr, flush=True)

            adjudicator.on_progress = _tick

    started = time.perf_counter()
    try:
        decisions, history = run_pipeline(batch, cfg, use_llm=not a.no_llm,
                                         adjudicator=adjudicator)
    except LLMUnavailable as e:
        # A rejected key fails identically for every transaction. Reporting a
        # batch of exceptions here would produce a table that looks like a hard
        # day's reconciliation and is actually a broken run.
        print(f"Stage 2 unavailable, no report written: {e}", file=sys.stderr)
        return 2
    elapsed = time.perf_counter() - started

    # Pricing comes from the active provider block in config.yaml, so the cost
    # line is always the cost of the model that actually ran. On --no-llm there
    # are no tokens, and a cost of zero would read as a claim; None prints "-".
    metrics = evaluate_matches(
        truth, decisions,
        price_per_mtok=None if a.no_llm else cfg.llm.price_per_mtok,
        elapsed_seconds=elapsed)

    print(f"\nbatch_{a.batch} - {metrics['n_txns']} transactions, "
          f"{metrics['overall']['n_truth_links']} truth links "
          f"({elapsed:.2f}s{', rules only' if a.no_llm else ''})\n")
    print(_summary(metrics))

    if adjudicator is not None:
        print("\n" + _stage2(adjudicator, cfg))

    if not a.no_report:
        name = f"{a.batch}_{a.label}" if a.label else a.batch
        path = write_report(metrics, name, reports_dir=a.reports_dir)
        print(f"\nwrote {path}")

    # Stage 2b. Runs after scoring, deliberately: the metrics above are
    # computed before a single note exists, which is the mechanical reason
    # triage cannot flatter them.
    notes = []
    if cfg.llm.triage and not a.no_llm:
        from .triage import build_triager, triage_queue, write_queue
        try:
            triager = build_triager(cfg)
        except (RuntimeError, ValueError) as e:
            print(f"cannot start triage: {e}", file=sys.stderr)
            return 2

        def _tick(note, done: int, total: int) -> None:
            if not a.quiet:
                print(f"  triage {done:>4}/{total} {note.action:<18} {note.txn_id}",
                      file=sys.stderr, flush=True)

        try:
            notes = triage_queue(decisions, batch, cfg, triager,
                                 on_progress=_tick)
        except LLMUnavailable as e:
            print(f"triage unavailable: {e}", file=sys.stderr)
            return 2

        s = triager.stats
        print(f"\ntriage: {len(notes)} queue items "
              f"({s['calls']} live, {s['cache_hits']} cached, "
              f"{s['degraded']} without a note)")
        if not a.no_report:
            md, csv_path = write_queue(notes, name, reports_dir=a.reports_dir)
            print(f"wrote {md}\nwrote {csv_path}")

    # The audit trail takes `history`, not `decisions`: `decisions` is the
    # effective view, and writing only that would discard exactly the records
    # that make the trail worth keeping -- the readings that were later
    # superseded, and the evidence they were based on.
    if not a.no_audit:
        run_id = f"{a.batch}-{datetime.now():%Y%m%d-%H%M%S}"
        with AuditLog(a.audit_db) as log:
            log.start_run(run_id, a.batch, n_txns=len(batch.bank),
                          use_llm=not a.no_llm,
                          llm_model=None if a.no_llm else cfg.llm.active.model,
                          config_note=a.label)
            written = log.record(history, run_id, a.batch)
            s = log.summary(run_id)
        print(f"audit: {written} records ({s['superseded']} superseded) "
              f"-> {a.audit_db} run {run_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
