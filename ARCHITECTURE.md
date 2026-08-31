# Architecture

## Four-Stage Pipeline

```
Stage 0: Candidate Generation
    ↓
Stage 1: Deterministic Rules (R1–R5)
    ↓
Stage 2: LLM Adjudication
    ↓
Stage 3: Confidence Routing & Exceptions
```

### Stage 0: Candidate Blocking

Generate candidate invoice–transaction pairs.

### Stage 1: Deterministic Rules

- **R1**: Exact match on amount + date
- **R2**: Counterparty fuzzy match + amount within tolerance
- **R3**: TDS or bank-charge adjusted amounts
- **R4**: Invoice subset matching
- **R5**: Confidence routing

### Stage 2: LLM Adjudication

Resolve remaining ambiguous cases using Claude with validated prompt guards.

### Stage 3: Routing & Exceptions

Route low-confidence matches to exception queue for manual review.

## Design Decisions

<!-- TODO: Add decision rationale -->
