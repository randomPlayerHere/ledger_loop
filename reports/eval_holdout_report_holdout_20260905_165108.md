# Eval — `holdout_report_holdout`

Generated 2026-09-05 16:51:08 · 504 transactions · 486 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.800 | ≥ 0.80 |
| Precision (auto only) | 0.998 | ≥ 0.98 |
| Recall (all outcomes) | 0.889 | ≥ 0.93 |
| Abstention precision | 0.511 | ≥ 0.70 |
| Missed-escalation rate | 0.002 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹124,382.49 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 5,768.0 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 403 |
| NEEDS_REVIEW | 13 |
| EXCEPTION | 88 |

## Overall links

TP 432 · FP 3 · FN 54 · precision 0.993 · recall 0.889 · F1 0.938

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 202 | 201 | 202 | 201 | 0 | 1 | 1.000 | 0.995 | 0.998 |
| HARD | 160 | 163 | 172 | 162 | 1 | 10 | 0.994 | 0.942 | 0.967 |
| IMPOSSIBLE | 30 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 112 | 70 | 112 | 69 | 1 | 43 | 0.986 | 0.616 | 0.758 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 150 | 150 | 150 | 150 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CONSOLIDATED | 14 | 32 | 34 | 32 | 0 | 2 | 1.000 | 0.941 | 0.970 |
| DUPLICATE | 8 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 52 | 51 | 52 | 51 | 0 | 1 | 1.000 | 0.981 | 0.990 |
| NO_REF | 42 | 40 | 42 | 40 | 0 | 2 | 1.000 | 0.952 | 0.976 |
| ORPHAN | 30 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 14 | 4 | 14 | 4 | 0 | 10 | 1.000 | 0.286 | 0.444 |
| PARTIAL | 96 | 91 | 96 | 90 | 1 | 6 | 0.989 | 0.938 | 0.963 |
| SHORT_PAID_CHARGES | 42 | 18 | 42 | 18 | 0 | 24 | 1.000 | 0.429 | 0.600 |
| SHORT_PAID_TDS | 56 | 48 | 56 | 47 | 1 | 9 | 0.979 | 0.839 | 0.904 |

## Tokens

in 0 · out 0
