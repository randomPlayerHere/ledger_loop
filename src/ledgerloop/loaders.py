"""Read a batch off disk. The only module that parses the input CSVs.

Deliberately cannot load truth.json. The engine is handed exactly what a real
deployment would have -- a statement and a ledger -- so there is no code path
by which the answer key can reach the matching logic. Loading truth stays in
evaluate.py, which is the only module allowed to see it.
"""

import csv
from pathlib import Path

from pydantic import BaseModel

from .models import BankTransaction, LedgerEntry


class Batch(BaseModel):
    name: str
    bank: list[BankTransaction]
    ledger: list[LedgerEntry]


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- run `make data` first")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_ledger(path: Path) -> list[LedgerEntry]:
    return [LedgerEntry(**row) for row in _rows(path)]


def load_bank(path: Path) -> list[BankTransaction]:
    out = []
    for row in _rows(path):
        row["utr"] = row["utr"] or None      # empty cell means absent, not ""
        out.append(BankTransaction(**row))
    return out


def load_batch(batch_dir: Path) -> Batch:
    return Batch(
        name=batch_dir.name.removeprefix("batch_"),
        bank=load_bank(batch_dir / "bank.csv"),
        ledger=load_ledger(batch_dir / "ledger.csv"),
    )
