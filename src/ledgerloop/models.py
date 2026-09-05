from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal
from decimal import Decimal

class BankTransaction(BaseModel):
    txn_id: str
    value_date: date
    amount: Decimal = Field(gt=0)
    direction: Literal["CREDIT", "DEBIT"]
    narration: str
    utr: str | None
    balance_after: Decimal

class LedgerEntry(BaseModel):
    invoice_id: str
    counterparty: str
    counterparty_id: str
    gross_amount: Decimal
    tds_applicable: bool
    tds_rate: Decimal
    issue_date: date
    due_date: date
    status: Literal["OPEN", "PARTIALLY_PAID", "PAID", "WRITTEN_OFF"]

class GroundTruthLink(BaseModel):
    txn_id: str
    invoice_ids: list[str]
    link_type: Literal[
        "CLEAN", "SHORT_PAID_TDS", "SHORT_PAID_CHARGES",
        "LATE", "PARTIAL", "CONSOLIDATED", "OVERPAID",
        "DISPUTED", "ORPHAN", "DUPLICATE", "REVERSAL",
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
    # HUMAN is what a reviewer's accept/reject writes. It is a third kind of
    # author, not a flag on an existing record: the trail has to be able to say
    # that a person overrode a rule, and which person-shaped action it was.
    decided_by: Literal["RULE", "LLM", "HUMAN"]
    rule_id: str | None                # "R3_TOLERANCE_TDS"
    reasoning: str                     # human-readable, one sentence
    evidence: dict                     # amount_delta, date_gap, name_similarity, ref_hit
    candidates_considered: list[str]
    llm_tokens_in: int | None
    llm_tokens_out: int | None
    latency_ms: int
    created_at: datetime
    # set when this record corrects an earlier one. The earlier record is never
    # edited -- the trail is append-only, and this is the link back to it.
    supersedes: str | None = None

class RuleResult(BaseModel):
    rule_id: str                      
    invoice_ids: list[str]
    allocated: dict[str, Decimal]
    confidence: float
    reasoning: str
    evidence: dict

class Candidate(BaseModel):
    invoice: LedgerEntry
    ref_hit: bool
    name_similarity: float
    shortfall: str | None      # "EXACT" | "TDS_10PCT" | "BANK_CHARGES" | None


class CandidateGroup(BaseModel):
    """A set of invoices that together account for one credit.

    Emitted by the consolidated path, which is separate from the single-invoice
    path because the evidence is different in kind: no member looks like a good
    candidate on its own, and what identifies the group is that its members sum
    to the payment and share a counterparty.
    """
    invoices: list[LedgerEntry]
    counterparty_id: str
    total: Decimal
    name_similarity: float     # best score across members; 0 on a bare narration
    ref_hits: list[str]        # member invoice ids whose number is in the narration
