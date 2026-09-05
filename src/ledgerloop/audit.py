"""The audit trail: every decision the engine ever made, in SQLite.

Append-only, and that is the entire design. A correction does not edit the
record it corrects -- it writes a new one carrying `supersedes`, and both stay
in the table forever. An auditor asking "why is this credit posted against
INV-1042" is entitled to the whole history: that R5 first read it as a part
payment at 0.72, that R7 later found its sibling instalment and superseded that
reading at 0.96, and what evidence each of them had. A table holding only the
final state cannot answer that, and a reconciliation you cannot interrogate is
not worth more than the spreadsheet it replaced.

Two consequences run through the file:

  * there is no UPDATE and no DELETE anywhere in it, and `decision_id` is the
    primary key, so a re-run cannot quietly rewrite history -- it collides
  * reads return the trail in the order it happened, never a deduplicated view,
    unless the caller explicitly asks for `effective_decisions()`

Everything money- or date-shaped is stored as TEXT. SQLite would happily take a
Decimal as a float and hand back 41249.999999999993; the whole project refuses
float for money, and the storage layer is not where that promise gets quietly
broken.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Iterator

from .models import MatchDecision

logger = logging.getLogger(__name__)

DEFAULT_DB = Path("audit.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    decision_id           TEXT PRIMARY KEY,
    run_id                TEXT NOT NULL,
    batch                 TEXT NOT NULL,
    txn_id                TEXT NOT NULL,
    proposed_invoice_ids  TEXT NOT NULL,   -- json array
    allocated             TEXT NOT NULL,   -- json object, amounts as strings
    outcome               TEXT NOT NULL,
    confidence            REAL NOT NULL,
    decided_by            TEXT NOT NULL,
    rule_id               TEXT,
    reasoning             TEXT NOT NULL,
    evidence              TEXT NOT NULL,   -- json object
    candidates_considered TEXT NOT NULL,   -- json array
    llm_tokens_in         INTEGER,
    llm_tokens_out        INTEGER,
    latency_ms            INTEGER NOT NULL,
    created_at            TEXT NOT NULL,
    supersedes            TEXT,
    written_at            TEXT NOT NULL,
    FOREIGN KEY (supersedes) REFERENCES decisions(decision_id)
);

CREATE INDEX IF NOT EXISTS idx_decisions_txn   ON decisions(txn_id);
CREATE INDEX IF NOT EXISTS idx_decisions_run   ON decisions(run_id);
CREATE INDEX IF NOT EXISTS idx_decisions_out   ON decisions(outcome);
CREATE INDEX IF NOT EXISTS idx_decisions_super ON decisions(supersedes);

CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    batch       TEXT NOT NULL,
    started_at  TEXT NOT NULL,
    n_txns      INTEGER NOT NULL,
    use_llm     INTEGER NOT NULL,
    llm_model   TEXT,
    config_note TEXT
);

-- Nothing in this module updates or deletes. These triggers make that a
-- property of the database rather than a habit of the code that writes to it,
-- so a future caller with a good reason and a bad idea still cannot mutate the
-- trail through this file's schema.
CREATE TRIGGER IF NOT EXISTS decisions_are_immutable
BEFORE UPDATE ON decisions
BEGIN
    SELECT RAISE(ABORT, 'audit records are append-only: supersede, never update');
END;

CREATE TRIGGER IF NOT EXISTS decisions_are_permanent
BEFORE DELETE ON decisions
BEGIN
    SELECT RAISE(ABORT, 'audit records are append-only: they are never deleted');
END;
"""


def _encode(value) -> str:
    """JSON with Decimal and date rendered as strings, never as floats."""
    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, set):
            return sorted(o)
        return str(o)
    return json.dumps(value, default=default, sort_keys=True)


class AuditLog:
    """Append-only store for MatchDecisions.

    Usable as a context manager; the connection is closed on exit. Writing the
    same decision twice raises rather than overwriting -- a duplicate id means
    two different decisions were minted with one identity, which is a bug in
    the caller and not something to paper over.
    """

    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def __enter__(self) -> "AuditLog":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    # -- writing ---------------------------------------------------------

    def start_run(self, run_id: str, batch: str, n_txns: int, use_llm: bool,
                  llm_model: str | None = None,
                  config_note: str | None = None) -> None:
        self.conn.execute(
            "INSERT INTO runs (run_id, batch, started_at, n_txns, use_llm, "
            "llm_model, config_note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, batch, datetime.now().isoformat(), n_txns,
             int(use_llm), llm_model, config_note))
        self.conn.commit()

    def record(self, decisions: Iterable[MatchDecision], run_id: str,
               batch: str) -> int:
        """Append decisions in the order given. Returns how many were written.

        Order matters and is preserved: `supersedes` points backwards, so a
        superseding record inserted before the one it corrects would fail the
        foreign key. That is a feature -- it means the table cannot hold a
        correction to something that never happened.
        """
        rows = [(
            d.decision_id, run_id, batch, d.txn_id,
            _encode(d.proposed_invoice_ids),
            _encode({k: str(v) for k, v in d.allocated.items()}),
            d.outcome, d.confidence, d.decided_by, d.rule_id, d.reasoning,
            _encode(d.evidence), _encode(d.candidates_considered),
            d.llm_tokens_in, d.llm_tokens_out, d.latency_ms,
            d.created_at.isoformat(), d.supersedes,
            datetime.now().isoformat(),
        ) for d in decisions]

        self.conn.executemany(
            "INSERT INTO decisions (decision_id, run_id, batch, txn_id, "
            "proposed_invoice_ids, allocated, outcome, confidence, decided_by, "
            "rule_id, reasoning, evidence, candidates_considered, "
            "llm_tokens_in, llm_tokens_out, latency_ms, created_at, "
            "supersedes, written_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        self.conn.commit()
        logger.info("audit records written", extra={"run_id": run_id,
                                                    "batch": batch,
                                                    "count": len(rows)})
        return len(rows)

    # -- reading ---------------------------------------------------------

    def history(self, txn_id: str) -> list[dict]:
        """Every record ever written for one transaction, oldest first.

        This is the question the trail exists to answer. A transaction that was
        read one way and then another returns both readings, in order, each
        with the evidence that produced it.
        """
        cur = self.conn.execute(
            "SELECT * FROM decisions WHERE txn_id = ? ORDER BY written_at, rowid",
            (txn_id,))
        return [_row_to_dict(r) for r in cur.fetchall()]

    def effective_decisions(self, run_id: str) -> list[dict]:
        """The decision that stands per transaction, for one run.

        A record is superseded if some other record in the same run names it.
        Everything else is current. Derived at read time rather than stored,
        because storing it would mean writing to a row after the fact.
        """
        cur = self.conn.execute(
            "SELECT * FROM decisions WHERE run_id = :run "
            "AND decision_id NOT IN ("
            "  SELECT supersedes FROM decisions "
            "  WHERE run_id = :run AND supersedes IS NOT NULL) "
            "ORDER BY txn_id", {"run": run_id})
        return [_row_to_dict(r) for r in cur.fetchall()]

    def exceptions(self, run_id: str) -> list[dict]:
        """The queue: what a human still has to deal with, worst first.

        Ordered by the money at stake, because a reviewer working top-down
        should be retiring the largest exposure first, not the alphabetically
        earliest transaction id.
        """
        rows = [r for r in self.effective_decisions(run_id)
                if r["outcome"] in ("EXCEPTION", "NEEDS_REVIEW")]
        return sorted(rows, key=_exposure, reverse=True)

    def superseded(self, run_id: str) -> list[dict]:
        """Records that were later corrected -- the part of the trail a
        final-state table would have thrown away."""
        cur = self.conn.execute(
            "SELECT * FROM decisions WHERE run_id = :run AND decision_id IN ("
            "  SELECT supersedes FROM decisions "
            "  WHERE run_id = :run AND supersedes IS NOT NULL) "
            "ORDER BY txn_id", {"run": run_id})
        return [_row_to_dict(r) for r in cur.fetchall()]

    def runs(self) -> list[dict]:
        cur = self.conn.execute("SELECT * FROM runs ORDER BY started_at DESC")
        return [dict(r) for r in cur.fetchall()]

    def latest_run_id(self, batch: str | None = None) -> str | None:
        sql = "SELECT run_id FROM runs"
        args: tuple = ()
        if batch:
            sql += " WHERE batch = ?"
            args = (batch,)
        row = self.conn.execute(sql + " ORDER BY started_at DESC LIMIT 1",
                                args).fetchone()
        return row["run_id"] if row else None

    def summary(self, run_id: str) -> dict:
        eff = self.effective_decisions(run_id)
        counts: dict[str, int] = {}
        for r in eff:
            counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
        return {
            "run_id": run_id,
            "decisions_written": self.conn.execute(
                "SELECT COUNT(*) c FROM decisions WHERE run_id = ?",
                (run_id,)).fetchone()["c"],
            "effective": len(eff),
            "superseded": len(self.superseded(run_id)),
            "outcomes": counts,
        }


def _exposure(row: dict) -> Decimal:
    """Rupees this row puts at risk: what it allocated, or the invoice it could
    not decide about. An exception allocating nothing still has a size."""
    allocated = row.get("allocated") or {}
    if allocated:
        return sum((Decimal(v) for v in allocated.values()), Decimal("0"))
    ev = row.get("evidence") or {}
    for key in ("invoice_gross", "total_allocated"):
        if key in ev:
            try:
                return abs(Decimal(str(ev[key])))
            except Exception:                      # noqa: BLE001
                pass
    return Decimal("0")


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("proposed_invoice_ids", "allocated", "evidence",
                "candidates_considered"):
        d[key] = json.loads(d[key])
    return d


def iter_decisions(db: AuditLog, run_id: str) -> Iterator[dict]:
    yield from db.effective_decisions(run_id)
