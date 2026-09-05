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


class ProviderConfig(_Section):
    """One row of llm.providers -- everything that changes when the wire does.

    Pricing lives here rather than in evaluate.py because it is a per-provider
    fact that moves without the code moving, and because a cost figure quoted
    from a constant nobody can find is not an auditable number.
    """
    model: str
    reasoning_effort: str | None = None
    max_tokens: int | None = None      # None -> fall back to llm.max_tokens
    price_in: Decimal                  # rupees per 1M input tokens
    price_out: Decimal                 # rupees per 1M output tokens


class LLMConfig(_Section):
    provider: str
    adjudicate: bool
    triage: bool
    temperature: float
    max_tokens: int
    max_candidates: int
    max_groups: int
    min_candidates: int
    confidence_ceiling: float
    cache_dir: str
    max_retries: int
    providers: dict[str, ProviderConfig]

    @property
    def active(self) -> ProviderConfig:
        try:
            return self.providers[self.provider]
        except KeyError:
            known = ", ".join(sorted(self.providers))
            raise ValueError(
                f"llm.provider is {self.provider!r} but only [{known}] are "
                "configured in config.yaml"
            ) from None

    @property
    def price_per_mtok(self) -> tuple[Decimal, Decimal]:
        """(input, output) rupees per million tokens, for evaluate_matches."""
        p = self.active
        return p.price_in, p.price_out


class Tolerances(_Section):
    amount_exact: Decimal
    tds_rates: list[Decimal]
    tds_tolerance: Decimal
    bank_charge_min: Decimal
    bank_charge_pct: Decimal
    overpay_max_ratio: Decimal


class Dates(_Section):
    max_days_gap: int


class Thresholds(_Section):
    auto_match: float
    exception: float


class Confidence(_Section):
    r1_exact: float
    r1_exact_with_ref: float
    r4_subset: float
    r4_subset_with_ref: float
    r3_tds: float
    r3_tds_with_ref: float
    r3_tds_unique: float
    r3_charges: float
    r3_charges_with_ref: float
    r6_overpaid_with_ref: float
    r6_overpaid_named: float
    r5_underpaid_with_ref: float
    r5_underpaid_named: float
    r7_split: float
    r7_split_with_ref: float


class Exceptions(_Section):
    max_per_batch: int
    llm_timeout: int


class Blocking(_Section):
    name_min: float
    name_strong: float
    date_back_days: int
    date_fwd_days: int
    amount_lo: Decimal
    amount_lo_corroborated: Decimal
    amount_hi: Decimal
    max_candidates: int
    max_ref_digits: int
    group_max_size: int
    group_max_results: int
    group_date_back_days: int
    split_max_days_gap: int


class Config(_Section):
    llm: LLMConfig
    tolerances: Tolerances
    dates: Dates
    thresholds: Thresholds
    confidence: Confidence
    exceptions: Exceptions
    blocking: Blocking


def load_config(path: Path | None = None) -> Config:
    path = path or DEFAULT_PATH
    if not path.exists():
        raise FileNotFoundError(f"no config at {path}")
    return Config.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
