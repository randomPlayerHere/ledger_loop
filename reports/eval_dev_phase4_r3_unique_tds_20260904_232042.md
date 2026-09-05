# Eval — `dev_phase4_r3_unique_tds`

Generated 2026-09-04 23:20:42 · 520 transactions · 499 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.798 | ≥ 0.80 |
| Precision (auto only) | 0.998 | ≥ 0.98 |
| Recall (all outcomes) | 0.876 | ≥ 0.93 |
| Abstention precision | 0.673 | ≥ 0.70 |
| Missed-escalation rate | 0.002 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹73,666.76 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 6,550.3 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 415 |
| NEEDS_REVIEW | 4 |
| EXCEPTION | 101 |

## Overall links

TP 437 · FP 3 · FN 62 · precision 0.993 · recall 0.876 · F1 0.931

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 184 | 182 | 184 | 182 | 0 | 2 | 1.000 | 0.989 | 0.995 |
| HARD | 203 | 186 | 213 | 185 | 1 | 28 | 0.995 | 0.869 | 0.927 |
| IMPOSSIBLE | 31 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 102 | 71 | 102 | 70 | 1 | 32 | 0.986 | 0.686 | 0.809 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 142 | 140 | 142 | 140 | 0 | 2 | 1.000 | 0.986 | 0.993 |
| CONSOLIDATED | 17 | 36 | 41 | 36 | 0 | 5 | 1.000 | 0.878 | 0.935 |
| DISPUTED | 20 | 1 | 20 | 1 | 0 | 19 | 1.000 | 0.050 | 0.095 |
| DUPLICATE | 14 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 42 | 42 | 42 | 42 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NO_REF | 48 | 48 | 48 | 48 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| ORPHAN | 31 | 1 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 16 | 3 | 16 | 3 | 0 | 13 | 1.000 | 0.188 | 0.316 |
| PARTIAL | 104 | 101 | 104 | 100 | 1 | 4 | 0.990 | 0.962 | 0.976 |
| SHORT_PAID_CHARGES | 43 | 31 | 43 | 30 | 1 | 13 | 0.968 | 0.698 | 0.811 |
| SHORT_PAID_TDS | 43 | 37 | 43 | 37 | 0 | 6 | 1.000 | 0.860 | 0.925 |

## Tokens

in 0 · out 0
