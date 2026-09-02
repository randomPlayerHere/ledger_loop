"""Load and validate config.yaml. The only module that reads it.

Typed rather than a raw dict for two reasons: a misspelled key fails at
startup instead of deep inside a matching loop, and money settings arrive as
Decimal so callers never have to guess whether YAML handed them an int or a
float.
"""

from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

# src/ledgerloop/config.py -> repo root, so cwd doesn't matter
DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


class _Section(BaseModel):
    # extra="forbid" turns a typo'd YAML key into a startup error rather than
    # a setting that silently does nothing
    model_config = ConfigDict(extra="forbid", frozen=True)


class LLMConfig(_Section):
    model: str
    temperature: float
    max_tokens: int


class Tolerances(_Section):
    amount_exact: Decimal
    tds_rates: list[Decimal]
    tds_tolerance: Decimal
    bank_charge_min: Decimal
    bank_charge_pct: Decimal


class Dates(_Section):
    max_days_gap: int


class Thresholds(_Section):
    auto_match: float
    exception: float


class Exceptions(_Section):
    max_per_batch: int
    llm_timeout: int


class Blocking(_Section):
    name_min: float
    date_back_days: int
    date_fwd_days: int
    amount_lo: Decimal
    amount_hi: Decimal
    max_candidates: int
    max_ref_digits: int


class Config(_Section):
    llm: LLMConfig
    tolerances: Tolerances
    dates: Dates
    thresholds: Thresholds
    exceptions: Exceptions
    blocking: Blocking


def load_config(path: Path | None = None) -> Config:
    path = path or DEFAULT_PATH
    if not path.exists():
        raise FileNotFoundError(f"no config at {path}")
    return Config.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
