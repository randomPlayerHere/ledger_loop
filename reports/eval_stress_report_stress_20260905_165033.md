# Eval — `stress_report_stress`

Generated 2026-09-05 16:50:33 · 531 transactions · 526 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.691 | ≥ 0.80 |
| Precision (auto only) | 0.995 | ≥ 0.98 |
| Recall (all outcomes) | 0.808 | ≥ 0.93 |
| Abstention precision | 0.699 | ≥ 0.70 |
| Missed-escalation rate | 0.004 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹251,436.44 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 4,093.5 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 367 |
| NEEDS_REVIEW | 11 |
| EXCEPTION | 153 |

## Overall links

TP 425 · FP 4 · FN 101 · precision 0.991 · recall 0.808 · F1 0.890

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 75 | 75 | 75 | 75 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| HARD | 319 | 294 | 345 | 291 | 3 | 54 | 0.990 | 0.843 | 0.911 |
| IMPOSSIBLE | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 106 | 60 | 106 | 59 | 1 | 47 | 0.983 | 0.557 | 0.711 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 51 | 51 | 51 | 51 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CONSOLIDATED | 37 | 86 | 91 | 86 | 0 | 5 | 1.000 | 0.945 | 0.972 |
| DISPUTED | 45 | 14 | 45 | 12 | 2 | 33 | 0.857 | 0.267 | 0.407 |
| DUPLICATE | 28 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 24 | 24 | 24 | 24 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NO_REF | 67 | 67 | 67 | 67 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| ORPHAN | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 26 | 7 | 26 | 6 | 1 | 20 | 0.857 | 0.231 | 0.364 |
| PARTIAL | 142 | 127 | 142 | 126 | 1 | 16 | 0.992 | 0.887 | 0.937 |
| SHORT_PAID_CHARGES | 43 | 26 | 43 | 26 | 0 | 17 | 1.000 | 0.605 | 0.754 |
| SHORT_PAID_TDS | 37 | 27 | 37 | 27 | 0 | 10 | 1.000 | 0.730 | 0.844 |

## Tokens

in 0 · out 0
