from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal
from decimal import Decimal

class BankTransaction(BaseModel):
    txn_id :str
    value_date: date
    amount : int = Field(gt=0)
    direction: Literal["CREDIT", "DEBIT"]
    narration: str | None
    utr: int
    balance_after: int

class LedgerEntry(BaseModel):
    invoice_id :str
    counterparty: str
    counterparty_id: str
    gross_amount: float
    tds_applicable: bool
    tds_rate: float
    issue_date: date
    due_date: date
    status: Literal["OPEN", "PARTIALLY_PAID", "PAID", "WRITTEN_OFF"]

class GroundTruthLink(BaseModel):
    txn_id: str
    invoice_ids: list[str]
    link_type: Literal[
        "CLEAN", "SHORT_PAID_TDS", "SHORT_PAID_CHARGES",
        "LATE", "PARTIAL", "CONSOLIDATED", "OVERPAID",
        "ORPHAN", "DUPLICATE", "REVERSAL",
    ]
    allocated: dict[str, str]
    difficulty: str

class MatchDecision(BaseModel):
    decision_id: str
    txn_id: str
    proposed_invoice_ids: list[str]
    allocated: dict[str, Decimal]
    outcome: Literal["AUTO_MATCHED", "NEEDS_REVIEW", "EXCEPTION"]
    confidence: float                  # 0.0 - 1.0
    decided_by: Literal["RULE", "LLM"]
    rule_id: str | None                # "R3_TOLERANCE_TDS"
    reasoning: str                     # human-readable, one sentence
    evidence: dict                     # amount_delta, date_gap, name_similarity, ref_hit
    candidates_considered: list[str]
    llm_tokens_in: int | None
    llm_tokens_out: int | None
    latency_ms: int
    created_at: datetime

