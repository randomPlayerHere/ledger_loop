# Eval — `dev_phase1_blocking`

Generated 2026-09-04 14:08:40 · 520 transactions · 499 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.446 | ≥ 0.80 |
| Precision (auto only) | 1.000 | ≥ 0.98 |
| Recall (all outcomes) | 0.465 | ≥ 0.93 |
| Abstention precision | 0.646 | ≥ 0.70 |
| Missed-escalation rate | 0.000 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹0.00 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 32,588.6 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 232 |
| NEEDS_REVIEW | 0 |
| EXCEPTION | 288 |

## Overall links

TP 232 · FP 0 · FN 267 · precision 1.000 · recall 0.465 · F1 0.635

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 184 | 184 | 184 | 184 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| HARD | 203 | 48 | 213 | 48 | 0 | 165 | 1.000 | 0.225 | 0.368 |
| IMPOSSIBLE | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 102 | 0 | 102 | 0 | 0 | 102 | 0.000 | 0.000 | 0.000 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 142 | 142 | 142 | 142 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CONSOLIDATED | 17 | 0 | 41 | 0 | 0 | 41 | 0.000 | 0.000 | 0.000 |
| DISPUTED | 20 | 0 | 20 | 0 | 0 | 20 | 0.000 | 0.000 | 0.000 |
| DUPLICATE | 14 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 42 | 42 | 42 | 42 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NO_REF | 48 | 48 | 48 | 48 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| ORPHAN | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 16 | 0 | 16 | 0 | 0 | 16 | 0.000 | 0.000 | 0.000 |
| PARTIAL | 104 | 0 | 104 | 0 | 0 | 104 | 0.000 | 0.000 | 0.000 |
| SHORT_PAID_CHARGES | 43 | 0 | 43 | 0 | 0 | 43 | 0.000 | 0.000 | 0.000 |
| SHORT_PAID_TDS | 43 | 0 | 43 | 0 | 0 | 43 | 0.000 | 0.000 | 0.000 |

## Tokens

in 0 · out 0
