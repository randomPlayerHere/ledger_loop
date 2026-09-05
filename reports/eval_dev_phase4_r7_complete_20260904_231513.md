# Eval — `dev_phase4_r7_complete`

Generated 2026-09-04 23:15:13 · 520 transactions · 499 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.781 | ≥ 0.80 |
| Precision (auto only) | 1.000 | ≥ 0.98 |
| Recall (all outcomes) | 0.860 | ≥ 0.93 |
| Abstention precision | 0.609 | ≥ 0.70 |
| Missed-escalation rate | 0.000 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹63,787.98 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 6,535.2 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 406 |
| NEEDS_REVIEW | 4 |
| EXCEPTION | 110 |

## Overall links

TP 429 · FP 2 · FN 70 · precision 0.995 · recall 0.860 · F1 0.923

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 184 | 183 | 184 | 183 | 0 | 1 | 1.000 | 0.995 | 0.997 |
| HARD | 203 | 187 | 213 | 187 | 0 | 26 | 1.000 | 0.878 | 0.935 |
| IMPOSSIBLE | 31 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 102 | 60 | 102 | 59 | 1 | 43 | 0.983 | 0.578 | 0.728 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 142 | 141 | 142 | 141 | 0 | 1 | 1.000 | 0.993 | 0.996 |
| CONSOLIDATED | 17 | 36 | 41 | 36 | 0 | 5 | 1.000 | 0.878 | 0.935 |
| DISPUTED | 20 | 1 | 20 | 1 | 0 | 19 | 1.000 | 0.050 | 0.095 |
| DUPLICATE | 14 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 42 | 42 | 42 | 42 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NO_REF | 48 | 48 | 48 | 48 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| ORPHAN | 31 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 16 | 3 | 16 | 3 | 0 | 13 | 1.000 | 0.188 | 0.316 |
| PARTIAL | 104 | 102 | 104 | 102 | 0 | 2 | 1.000 | 0.981 | 0.990 |
| SHORT_PAID_CHARGES | 43 | 31 | 43 | 30 | 1 | 13 | 0.968 | 0.698 | 0.811 |
| SHORT_PAID_TDS | 43 | 26 | 43 | 26 | 0 | 17 | 1.000 | 0.605 | 0.754 |

## Tokens

in 0 · out 0
