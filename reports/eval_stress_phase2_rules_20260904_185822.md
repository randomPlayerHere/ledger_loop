# Eval — `stress_phase2_rules`

Generated 2026-09-04 18:58:22 · 531 transactions · 526 truth links

## Headline

| Metric | Value | Target |
|---|---|---|
| Auto-match rate | 0.522 | ≥ 0.80 |
| Precision (auto only) | 0.994 | ≥ 0.98 |
| Recall (all outcomes) | 0.635 | ≥ 0.93 |
| Abstention precision | 0.784 | ≥ 0.70 |
| Missed-escalation rate | 0.004 | ≤ 0.02 |
| LLM invocation rate | 0.000 | ≤ 0.25 |
| False-match value | ₹251,436.44 | report |
| Cost per 1,000 txns | - | report |
| Throughput (txns/min) | 8,442.4 | report |

## Outcomes

| Outcome | Count |
|---|---|
| AUTO_MATCHED | 277 |
| NEEDS_REVIEW | 9 |
| EXCEPTION | 245 |

## Overall links

TP 334 · FP 4 · FN 192 · precision 0.988 · recall 0.635 · F1 0.773

## By difficulty

| difficulty | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| EASY | 75 | 75 | 75 | 75 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| HARD | 319 | 210 | 345 | 207 | 3 | 138 | 0.986 | 0.600 | 0.746 |
| IMPOSSIBLE | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| MEDIUM | 106 | 53 | 106 | 52 | 1 | 54 | 0.981 | 0.491 | 0.654 |

## By link type

| link_type | txns | pred | truth | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| CLEAN | 51 | 51 | 51 | 51 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| CONSOLIDATED | 37 | 88 | 91 | 88 | 0 | 3 | 1.000 | 0.967 | 0.983 |
| DISPUTED | 45 | 14 | 45 | 12 | 2 | 33 | 0.857 | 0.267 | 0.407 |
| DUPLICATE | 28 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| LATE | 24 | 24 | 24 | 24 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NO_REF | 67 | 67 | 67 | 67 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| ORPHAN | 31 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| OVERPAID | 26 | 7 | 26 | 6 | 1 | 20 | 0.857 | 0.231 | 0.364 |
| PARTIAL | 142 | 41 | 142 | 40 | 1 | 102 | 0.976 | 0.282 | 0.437 |
| SHORT_PAID_CHARGES | 43 | 26 | 43 | 26 | 0 | 17 | 1.000 | 0.605 | 0.754 |
| SHORT_PAID_TDS | 37 | 20 | 37 | 20 | 0 | 17 | 1.000 | 0.541 | 0.702 |

## Tokens

in 0 · out 0
