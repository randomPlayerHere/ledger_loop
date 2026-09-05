# Exception queue — `dev_final`

116 items · ₹6,258,251.74 unresolved · generated 2026-09-05 03:15

Every note below is written by a language model and is a **suggestion for a reviewer, never a decision**. No note moved money, and no note changed a match: the reconciliation in `reports/eval_*.md` is identical with triage on or off.

## By suggested action

| Action | Items | Value |
|---|---|---|
| NEEDS_MORE_DATA | 35 | ₹1,787,179.97 |
| CHECK_DUPLICATE | 24 | ₹1,675,862.87 |
| REQUEST_REMITTANCE | 35 | ₹1,286,282.21 |
| CONFIRM_MATCH | 14 | ₹1,059,118.14 |
| WRITE_OFF_SMALL | 5 | ₹313,666.66 |
| CHECK_REFUND | 3 | ₹136,141.89 |

## Queue

Ordered by money at stake.

### BNK-000158 — ₹283,019.55 · `CHECK_DUPLICATE`

*2026-07-17 · EXCEPTION · INB/300245327485/PAYMENT*

The credit of Rs 283,019.55 on 2026-07-17 exactly matches the outstanding amount of invoice INV-1145, but the system notes that INV-1145 was already settled by the prior transaction BNK-000157, suggesting this credit is a duplicate or unapplied payment.

- **Lead:** INV-1145
- **Certainty:** moderate -- amount matches invoice exactly and narration indicates a payment, but the invoice is already marked settled.
- **Rules said:** INV-1145 already settled by BNK-000157; suspected duplicate credit, left unapplied.
- **Considered:** INV-1145
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000056 — ₹273,031.34 · `CHECK_DUPLICATE`

*2026-06-12 · EXCEPTION · NEFT-REDDYPAC*

The credit of Rs 273,031.34 from NEFT-REDDYPAC exactly matches the gross amount of invoice INV-1039 (Reddy Packaging Ltd), but the rules indicate that INV-1039 was already settled by a prior credit (BNK-000055). This suggests the current credit is a duplicate or unapplied payment.

- **Lead:** INV-1039
- **Certainty:** moderate -- amount matches exactly and narration points to Reddy Packaging, but the invoice is already marked settled, so the credit is likely a duplicate.
- **Rules said:** INV-1039 already settled by BNK-000055; suspected duplicate credit, left unapplied.
- **Considered:** INV-1039, INV-1265, INV-1344, INV-1431, INV-1406, INV-1120, INV-1178, INV-1322, INV-1138, INV-1233, INV-1393, INV-1298
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000162 — ₹256,114.42 · `CONFIRM_MATCH`

*2026-07-14 · NEEDS_REVIEW · INB/600229982535/PAYMENT*

The bank credit of Rs 256,114.42 on 2026-07-14 matches invoice INV-1148 (gross Rs 284,571.58) less a Rs 28,457.16 TDS deduction, as indicated by the narration referencing UTR 600229982535 and the rule engine's shortfall note.

- **Lead:** INV-1148
- **Certainty:** strong -- amount gap exactly equals 10% TDS on the invoice, narration includes the UTR linking to the payment.
- **Rules said:** Short of INV-1148 by Rs28457.16, which is 10% TDS.
- **Considered:** INV-1148
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000216 — ₹244,444.03 · `NEEDS_MORE_DATA`

*2026-07-12 · EXCEPTION · IMPS-977754502752-RDDYPC*

A credit of Rs 244,444.03 arrived via IMPS on 2026-07-12 with narration 'IMPS-977754502752-RDDYPC', indicating a payment from an entity whose name includes 'Reddy'. None of the considered invoices match this amount; the closest are off by tens of thousands of rupees, and no TDS or other adjustments explain the gap.

- **Lead:** —
- **Certainty:** low -- narration hints at a Reddy counterparty but amount does not correspond to any invoice; insufficient data to infer purpose.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1204, INV-1261, INV-1489, INV-1275, INV-1039, INV-1086, INV-1029, INV-1290, INV-1444, INV-1265, INV-1132, INV-1042
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000008 — ₹187,883.12 · `NEEDS_MORE_DATA`

*2026-07-20 · EXCEPTION · INB/806584574469/PAYMENT*

The credit of Rs 187,883.12 on 2026-07-20 exactly equals the combined total of two open invoices from Iyer Textiles & Co (INV-1289 for Rs 182,897.99 and INV-1411 for Rs 4,985.13). The narration does not specify which invoices are being paid, and no single rule matched the amount.

- **Lead:** —
- **Certainty:** moderate -- amount equals sum of INV-1289 and INV-1411, but narration lacks detail to confirm which invoices are intended.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1289, INV-1411, INV-1462, INV-1228, INV-1152, INV-1168
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000255 — ₹178,961.53 · `CONFIRM_MATCH`

*2026-07-14 · EXCEPTION · RTGS KKBK234880394355 MEHTACHE*

The credit of Rs 178,961.53 on 2026-07-14 from Mehta Chemicals (UTR 234880394355) matches the net amount of invoice INV-1248 after applying the 2% TDS (gross Rs 182,613.81 less TDS Rs 3,652.28). The rule engine flagged it as a suspected duplicate, but the amount gap is fully explained by TDS.

- **Lead:** INV-1248
- **Certainty:** strong -- amount equals invoice gross minus 2% TDS exactly.
- **Rules said:** INV-1465 already settled by BNK-000009; suspected duplicate credit, left unapplied.
- **Considered:** INV-1248, INV-1276, INV-1350, INV-1385, INV-1019, INV-1195, INV-1386, INV-1363, INV-1307, INV-1044, INV-1055, INV-1296
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000145 — ₹152,118.78 · `CONFIRM_MATCH`

*2026-08-04 · NEEDS_REVIEW · BY TRANSFER-869586641435-*

The bank credit of Rs 152,118.78 on 2026-08-04 matches invoice INV-1130 for Iyer Textiles & Co except for a shortfall of Rs 3,104.46, which corresponds to a 2% TDS deduction. The narration only shows a UTR reference with no party name, so the match relies on the amount gap.

- **Lead:** INV-1130
- **Certainty:** moderate -- amount gap exactly equals expected 2% TDS on INV-1130, but narration lacks counterparty details.
- **Rules said:** Short of INV-1130 by Rs3104.46, which is 2% TDS.
- **Considered:** INV-1130
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000234 — ₹133,409.60 · `WRITE_OFF_SMALL`

*2026-05-30 · EXCEPTION · UPI/103398262106/mlhsl@okyesbbank*

The credit of Rs 133,409.60 on 2026-05-30 (UPI transaction mlhsl@okyesbbank) is Rs 17.35 short of the open invoice INV-1223 for Malhotra Solutions LLP (gross Rs 133,426.95, issued 2026-05-24). The narration does not name the counterparty, but the UPI ID suggests a payment from the same party; the small gap is typical of bank charges or rounding.

- **Lead:** INV-1223
- **Certainty:** moderate -- amount gap is tiny and plausible as a fee, but no explicit remittance details to confirm.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1223
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000421 — ₹124,889.71 · `CHECK_DUPLICATE`

*2026-07-28 · EXCEPTION · CMS/INV-1433/TriveEnt*

The credit of Rs 124,889.71 on 2026-07-28 exactly matches the gross amount of invoice INV-1433 (Trivedi Enterprises). The rule engine flagged it as a suspected duplicate because invoice INV-1433 was already settled by a prior credit (BNK-000420), leaving this amount unapplied.

- **Lead:** INV-1433
- **Certainty:** strong -- amount matches invoice exactly and narration references the same invoice number.
- **Rules said:** INV-1433 already settled by BNK-000420; suspected duplicate credit, left unapplied.
- **Considered:** INV-1433, INV-1148, INV-1106, INV-1232, INV-1410, INV-1089, INV-1030, INV-1399, INV-1284, INV-1012, INV-1452, INV-1060
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000159 — ₹111,619.36 · `CHECK_DUPLICATE`

*2026-07-10 · EXCEPTION · NEFT-CHTTTX*

A credit of Rs 111,619.36 arrived on 2026-07-10 from NEFT-CHTTTX. The amount is within a few hundred rupees of two open invoices from Chatterjee Textiles (INV-1357 and INV-1146), but the rule engine already flagged INV-1357 as settled by another credit (BNK-000353) and suspects this is a duplicate/unapplied credit.

- **Lead:** INV-1357
- **Certainty:** moderate -- amount close to INV-1357 and INV-1146, but rules indicate INV-1357 already settled, suggesting duplicate credit.
- **Rules said:** INV-1357 already settled by BNK-000353; suspected duplicate credit, left unapplied.
- **Considered:** INV-1357, INV-1146, INV-1317, INV-1448, INV-1164, INV-1264, INV-1488, INV-1408, INV-1070, INV-1367, INV-1280, INV-1364
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000250 — ₹106,605.73 · `REQUEST_REMITTANCE`

*2026-07-01 · EXCEPTION · INB/234493809683/PAYMENT*

The bank credit of Rs 106,605.73 on 2026-07-01 (UTR 234493809683) is Rs 46.88 less than the open invoice INV-1243 from Iyer Textiles & Co (gross Rs 106,652.61, issued 2026-06-20). The narration only contains a generic payment reference, so the shortfall cannot be explained by any discount, tax, or fee visible in the data.

- **Lead:** INV-1243
- **Certainty:** weak -- amount close to invoice but unexplained gap and narration lacks payer details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1243
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000249 — ₹106,551.49 · `CHECK_DUPLICATE`

*2026-05-30 · EXCEPTION · IMPS-581831446319-IYERPOL*

The credit of Rs 106,551.49 on 2026-05-30 (IMPS-581831446319-IYERPOL) exactly matches the outstanding amount of invoice INV-1242 for Iyer Polymers & Co, but the rule engine notes that INV-1242 was already settled by transaction BNK-000248, suggesting this credit is a duplicate or unapplied payment.

- **Lead:** INV-1242
- **Certainty:** strong -- amount matches invoice exactly, but flagged as suspected duplicate credit.
- **Rules said:** INV-1242 already settled by BNK-000248; suspected duplicate credit, left unapplied.
- **Considered:** INV-1242, INV-1219, INV-1065, INV-1075, INV-1428, INV-1103, INV-1457, INV-1090, INV-1175, INV-1193, INV-1111, INV-1310
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000146 — ₹100,701.80 · `WRITE_OFF_SMALL`

*2026-07-10 · EXCEPTION · BY TRANSFER-409971232353-*

A credit of Rs 100,701.80 arrived on 2026‑07‑10 from an unidentified transfer (UTR 409971232353). The amount is Rs 319.26 less than the open invoice INV‑1219 for Iyer Polymers & Co (gross Rs 101,021.06, issued 2026‑05‑16). No deterministic rule could explain this shortfall, so the payment appears to be a partial or under‑paid settlement.

- **Lead:** INV-1219
- **Certainty:** weak -- amount close to invoice but unexplained shortfall; no remittance details to confirm intent.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1219
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000002 — ₹98,788.48 · `CHECK_DUPLICATE`

*2026-08-06 · EXCEPTION · NEFT-IyerInf*

A credit of Rs 98,788.48 from Iyer Infotech (UTR 651318604571) arrived on 2026-08-06. No open invoice matches this amount; the rule engine flagged it as a possible duplicate of INV-1073, which was already settled by another transaction.

- **Lead:** —
- **Certainty:** weak -- narration points to Iyer Infotech but amount does not correspond to any open invoice; duplicate suspicion is the only clue.
- **Rules said:** INV-1073 already settled by BNK-000093; suspected duplicate credit, left unapplied.
- **Considered:** INV-1160, INV-1073, INV-1187, INV-1121, INV-1206, INV-1271, INV-1107, INV-1316, INV-1461, INV-1346, INV-1476, INV-1105
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000282 — ₹95,301.40 · `CONFIRM_MATCH`

*2026-07-21 · NEEDS_REVIEW · UPI/962770597493/nrnd@okkkbkbank*

The bank credit of Rs 95,301.40 on 2026-07-21 matches the gross amount of invoice INV-1274 (Rs 105,890.44) less a Rs 10,589.04 TDS deduction, as noted by the rule engine. The narration only shows a UPI reference with no counterparty name, so the payment cannot be directly linked to the invoice without confirming the TDS adjustment.

- **Lead:** INV-1274
- **Certainty:** moderate -- amount gap equals expected 10% TDS on INV-1274, but narration lacks payer details.
- **Rules said:** Short of INV-1274 by Rs10589.04, which is 10% TDS.
- **Considered:** INV-1274
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000035 — ₹89,702.60 · `REQUEST_REMITTANCE`

*2026-07-03 · EXCEPTION · BY TRANSFER-510093321841-*

The bank credit of Rs 89,702.60 on 2026-07-03 (UTR 510093321841) is Rs 47.03 short of the open invoice INV-1013 from Bose Industries for Rs 89,749.63. The narration only shows a transfer reference, giving no further clue about the shortfall.

- **Lead:** INV-1013
- **Certainty:** weak -- amount gap is small and could be a bank fee or rounding, but narration lacks details to confirm.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1013
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000505 — ₹88,163.93 · `CHECK_REFUND`

*2026-06-18 · EXCEPTION · REFUND/399694532718/GATEWAY*

The bank credit of Rs 88,163.93 on 2026‑06‑18 carries a narration indicating a refund (UTR 399694532718). Neither of the two open invoices matches the amount exactly; the closest is INV‑1360 (difference ‑Rs 124.08) and INV‑1404 (difference ‑Rs 405.53). The small gaps suggest a possible partial refund or adjustment, but the narration does not reference any specific invoice.

- **Lead:** —
- **Certainty:** weak -- narration mentions a refund but amount does not correspond precisely to any candidate invoice
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1404, INV-1360
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000493 — ₹86,928.45 · `NEEDS_MORE_DATA`

*2026-05-27 · EXCEPTION · REV-690921879434-FAILED TXN*

The bank shows a credit of Rs 86,928.45 on 2026-05-27 with narration 'REV-690921879434-FAILED TXN' and UTR 690921879434, indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be linked to any outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a failed‑transaction reversal but no invoice data exists to confirm.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000514 — ₹86,613.89 · `NEEDS_MORE_DATA`

*2026-05-02 · EXCEPTION · INT.PD:732069347976*

The bank credit of Rs 86,613.89 on 2026-05-02 is labelled as an interest payment (INT.PD) with UTR 732069347976. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the deterministic engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest but no matching invoice exists; cannot infer further without additional remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000230 — ₹82,346.37 · `CONFIRM_MATCH`

*2026-06-13 · EXCEPTION · INB/436516507468/PAYMENT*

The bank credit of Rs 82,346.37 on 2026-06-13 (UTR 436516507468) is very close to invoice INV-1218 for Rastogi Motors LLP (Rs 82,367.03), differing by only Rs 20.66. The narration contains only a UTR reference with no counterparty name, so the rule engine could not automatically confirm the match.

- **Lead:** INV-1218
- **Certainty:** weak -- amount gap is small (Rs 20.66) and dates align, but narration lacks identifying details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1218
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000515 — ₹79,983.21 · `CHECK_DUPLICATE`

*2026-07-26 · EXCEPTION · REV-661253583335-FAILED TXN*

A credit of Rs 79,983.21 on 2026-07-26 with narration 'REV-661253583335-FAILED TXN' (UTR 661253583335) does not match any open invoice; the rule engine notes that INV-1152 for the same party was already settled by another credit (BNK-000166) and treats this as a suspected duplicate credit left unapplied.

- **Lead:** —
- **Certainty:** weak -- narration indicates a failed/reversal transaction and no invoice amount aligns with the credit; the rule already flagged it as a suspected duplicate.
- **Rules said:** INV-1152 already settled by BNK-000166; suspected duplicate credit, left unapplied.
- **Considered:** INV-1391, INV-1152, INV-1143
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000414 — ₹79,290.77 · `NEEDS_MORE_DATA`

*2026-07-26 · EXCEPTION · INB/746460547403/PAYMENT*

A credit of Rs 79,290.77 was posted on 2026-07-26 with narration 'INB/746460547403/PAYMENT' and UTR 746460547403. No invoice in the ledger matches this amount, date, or counterparty, and the rule engine found no candidates.

- **Lead:** —
- **Certainty:** low -- no candidate invoices and narration provides no identifiable party or amount correlation.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000045 — ₹78,374.56 · `CHECK_DUPLICATE`

*2026-06-24 · EXCEPTION · IMPS-592789627535-IyerTex*

A credit of Rs 78,374.56 from IyerTex (UTR 592789627535) arrived on 2026-06-24. The amount is Rs 30.04 short of the open invoice INV-1008 (Rs 78,404.60) and the rules engine notes that INV-1008 was already settled by another transaction (BNK-000028), suggesting this credit may be a duplicate or an unapplied partial payment.

- **Lead:** INV-1008
- **Certainty:** weak -- amount close to INV-1008 but rules indicate it was already settled, so likely duplicate/unapplied.
- **Rules said:** INV-1008 already settled by BNK-000028; suspected duplicate credit, left unapplied.
- **Considered:** INV-1008, INV-1488, INV-1465, INV-1125, INV-1217, INV-1243, INV-1007, INV-1378, INV-1124, INV-1027, INV-1356, INV-1156
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000502 — ₹73,935.48 · `NEEDS_MORE_DATA`

*2026-07-22 · EXCEPTION · REV-800059737458-FAILED TXN*

A credit of Rs 73,935.48 appeared on 2026-07-22 with narration 'REV-800059737458-FAILED TXN', indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be linked to any known receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a reversal but no invoice fits the amount or details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000202 — ₹72,473.82 · `REQUEST_REMITTANCE`

*2026-07-22 · EXCEPTION · INB/178257150685/PAYMENT*

The bank credit of Rs 72,473.82 on 2026-07-22 (UTR 178257150685) is very close to invoice INV-1112 for Iyer Textiles & Co (gross Rs 72,504.46), differing by only Rs 30.64. No other invoice matches the amount, and the narration does not identify a counterparty.

- **Lead:** INV-1112
- **Certainty:** weak -- amount gap is small but unexplained; narration gives no party details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1112, INV-1187
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000131 — ₹72,417.02 · `REQUEST_REMITTANCE`

*2026-07-11 · EXCEPTION · UPI/628864035957/deshmste@okutibbank*

A UPI credit of Rs 72,417.02 arrived on 2026-07-11 from deshmste@okutibbank. The amount is Rs 87.44 less than invoice INV-1112 (Iyer Textiles & Co) for Rs 72,504.46, and no other candidate invoice matches within a reasonable tolerance.

- **Lead:** INV-1112
- **Certainty:** weak -- amount gap is small but narration points to Deshmukh Steels, not Iyer Textiles, so match is uncertain.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1112, INV-1251, INV-1101, INV-1114, INV-1196, INV-1016, INV-1352, INV-1026, INV-1197, INV-1165, INV-1036, INV-1235
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000106 — ₹72,015.23 · `REQUEST_REMITTANCE`

*2026-06-04 · EXCEPTION · UPI/403818855227/iyrlg@oksbinbank*

The bank credit of Rs 72,015.23 on 2026‑06‑04 (UPI transaction 403818855227) is very close to the open invoice INV‑1090 for Iyer Logistics Ltd (Rs 72,036.91), differing by only Rs 21.68. No other candidate invoice matches the amount, and the narration does not reveal a different counterparty.

- **Lead:** INV-1090
- **Certainty:** moderate -- amount gap is small and could be bank charges or rounding, but no rule explains it.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1090, INV-1139
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000270 — ₹71,206.74 · `REQUEST_REMITTANCE`

*2026-06-17 · EXCEPTION · IMPS-202898573344-CHATTTEX*

Bank credit of Rs 71,206.74 on 2026-06-17 from IMPS transfer to CHATTTEX (UTR 202898573344) does not exactly match any invoice; the closest is INV-1161 for Gokhale Textiles Pvt Ltd (gross Rs 71,253.60), leaving an unexplained shortfall of Rs 46.86.

- **Lead:** INV-1161
- **Certainty:** weak -- amount gap is small but unexplained; narration points to Chatterjee, yet best invoice is a different party.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1161, INV-1317, INV-1264, INV-1070, INV-1488, INV-1280, INV-1357, INV-1408, INV-1367, INV-1364, INV-1224, INV-1053
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000079 — ₹70,691.70 · `CHECK_DUPLICATE`

*2026-07-21 · EXCEPTION · INB/274622769790/PAYMENT*

A credit of Rs 70,691.70 arrived on 2026-07-21 with narration INB/274622769790/PAYMENT and UTR 274622769790. The amount exactly matches the open invoice INV-1058 for Sharma Packaging & Co, but the rule engine already marked INV-1058 as settled by a prior credit (BNK-000078) and flagged this as a suspected duplicate credit left unapplied.

- **Lead:** —
- **Certainty:** moderate -- amount matches INV-1058 exactly, but rules indicate it is a duplicate of an already settled payment.
- **Rules said:** INV-1058 already settled by BNK-000078; suspected duplicate credit, left unapplied.
- **Considered:** INV-1058
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000346 — ₹68,364.02 · `NEEDS_MORE_DATA`

*2026-08-06 · EXCEPTION · INB/107459751297/PAYMENT*

The bank credit of Rs 68,364.02 on 2026-08-06 (UTR 107459751297) does not exactly match any open invoice. The closest candidate is INV-1350 (Mehta Chemicals Ltd) which is only Rs 21.39 higher, but the narration provides no counterparty name and no rule explains this small gap.

- **Lead:** INV-1350
- **Certainty:** weak -- amount is very close to INV-1350 but the unexplained Rs 21.39 difference and lack of identifying details in the narration prevent a confident match.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1160, INV-1350
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000513 — ₹65,830.80 · `NEEDS_MORE_DATA`

*2026-05-10 · EXCEPTION · CHARGES GST @18%*

The bank credit of Rs 65,830.80 on 2026-05-10 is labelled as 'CHARGES GST @18%' with UTR 439076735839, indicating a GST charge rather than a payment against an invoice. No invoices in the ledger match this amount, date, or counterparty, so the transaction cannot be matched to any existing invoice.

- **Lead:** —
- **Certainty:** weak -- narration points to a GST charge, but without a related invoice or remittance advice we cannot determine the correct handling.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000479 — ₹65,189.90 · `CHECK_DUPLICATE`

*2026-05-22 · EXCEPTION · NEFT-DESHMSTE*

The credit of Rs 65,189.90 on 2026-05-22 (UTR 450464522328, narration NEFT-DESHMSTE) exactly matches the gross amount of invoice INV-1490 for Deshmukh Steels Pvt Ltd, which the rule engine already marked as settled by the prior transaction BNK-000478 and flagged as a suspected duplicate credit.

- **Lead:** INV-1490
- **Certainty:** strong -- amount matches INV-1490 exactly, but the system already considers it a duplicate of BNK-000478.
- **Rules said:** INV-1490 already settled by BNK-000478; suspected duplicate credit, left unapplied.
- **Considered:** INV-1490, INV-1070, INV-1259, INV-1212, INV-1115, INV-1157, INV-1306, INV-1279, INV-1273, INV-1186
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000510 — ₹63,821.47 · `NEEDS_MORE_DATA`

*2026-06-17 · EXCEPTION · REV-724397194389-FAILED TXN*

A credit of Rs 63,821.47 appears on 2026-06-17 with narration 'REV-724397194389-FAILED TXN' and UTR 724397194389, indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the money cannot be tied to a specific receivable.

- **Lead:** —
- **Certainty:** low -- narration suggests a failed transaction reversal but provides no party or invoice reference, and no candidate invoices exist.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000490 — ₹63,394.96 · `NEEDS_MORE_DATA`

*2026-07-22 · EXCEPTION · INT.PD:919023316095*

The bank credit of Rs 63,394.96 on 2026-07-22 is labelled as an interest payment (INT.PD) with UTR 919023316095. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest payment but no matching invoice exists; amount and date do not correspond to any recorded invoice.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000516 — ₹63,381.96 · `NEEDS_MORE_DATA`

*2026-06-24 · EXCEPTION · INT.PD:542917177775*

The bank credit of Rs 63,381.96 on 2026-06-24 is an interest payment (INT.PD) identified by UTR 542917177775. No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest but no matching invoice exists; need more context to decide.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000477 — ₹62,146.78 · `REQUEST_REMITTANCE`

*2026-06-06 · EXCEPTION · UPI/975889539105/chtttx@okaxisbank*

A UPI credit of Rs 62,146.78 from chtttx@okaxisbank on 2026-06-06 does not exactly match any open invoice; the nearest is INV-1070 for Chatterjee Textiles (Rs 65,352.88), leaving an unexplained shortfall of about Rs 3,206.

- **Lead:** INV-1070
- **Certainty:** weak -- amount close to INV-1070 but gap unexplained, no remittance details in narration.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1264, INV-1070, INV-1488, INV-1280, INV-1357, INV-1367, INV-1408, INV-1364, INV-1224, INV-1053, INV-1028
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000342 — ₹62,059.16 · `CONFIRM_MATCH`

*2026-07-02 · NEEDS_REVIEW · INB/815619666052/PAYMENT*

The bank credit of Rs 62,059.16 on 2026-07-02 matches invoice INV-1344 (gross Rs 68,954.62) less a Rs 6,895.46 TDS deduction, as indicated by the narration referencing UTR 815619666052. The rule engine flagged it as short by exactly the TDS amount, suggesting the payment is net of tax.

- **Lead:** INV-1344
- **Certainty:** strong -- amount gap equals 10% TDS of invoice, narration includes UTR, dates align.
- **Rules said:** Short of INV-1344 by Rs6895.46, which is 10% TDS.
- **Considered:** INV-1344
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000517 — ₹61,724.99 · `NEEDS_MORE_DATA`

*2026-07-07 · EXCEPTION · REV-367769996448-FAILED TXN*

A credit of Rs 61,724.99 appears on 2026-07-07 with narration 'REV-367769996448-FAILED TXN' and UTR 367769996448, indicating a reversed or failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be tied to any known receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a failed transaction but no invoice data exists to confirm purpose.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000032 — ₹60,232.20 · `CONFIRM_MATCH`

*2026-05-09 · NEEDS_REVIEW · BY TRANSFER-923232264034-*

The bank credit of Rs 60,232.20 on 2026-05-09 matches invoice INV-1011 (gross Rs 66,924.67) less the expected TDS of Rs 6,692.47, leaving the exact amount received. The narration only shows a UTR reference with no party name, so the match relies on the amount gap.

- **Lead:** INV-1011
- **Certainty:** moderate -- amount gap equals 10% TDS as noted by the rule engine, but narration lacks counterparty details.
- **Rules said:** Short of INV-1011 by Rs6692.47, which is 10% TDS.
- **Considered:** INV-1011
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000509 — ₹59,351.88 · `NEEDS_MORE_DATA`

*2026-05-20 · EXCEPTION · IMPS-625715384106-UNKNOWN REMITTER*

A credit of Rs 59,351.88 arrived on 2026-05-20 via IMPS from an unknown remitter (UTR 625715384106). The narration does not identify any counterparty, and no invoice in the ledger matches this amount, date, or party, leaving the source of the funds unclear.

- **Lead:** —
- **Certainty:** weak -- narration gives no identifiable party and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000512 — ₹57,389.35 · `REQUEST_REMITTANCE`

*2026-06-09 · EXCEPTION · IMPS-572242891228-UNKNOWN REMITTER*

The bank shows a credit of Rs 57,389.35 from an unknown remitter via IMPS on 2026-06-09. The only open invoice considered (INV-1407 for Venkat Industries Ltd) is for Rs 57,543.93, leaving an unexplained shortfall of Rs 154.58, which could be a bank fee or partial payment.

- **Lead:** INV-1407
- **Certainty:** weak -- amount close to INV-1407 but the gap is unexplained and the remitter is unknown
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1407
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000501 — ₹56,846.35 · `NEEDS_MORE_DATA`

*2026-05-10 · EXCEPTION · REV-383230503741-FAILED TXN*

A credit of Rs 56,846.35 appeared on 2026-05-10 with narration 'REV-383230503741-FAILED TXN' and UTR 383230503741, indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be tied to any outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- no invoice candidates match the amount, date or narration
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000224 — ₹54,899.86 · `CONFIRM_MATCH`

*2026-08-13 · NEEDS_REVIEW · INB/542488684437/PAYMENT*

The bank credit of Rs 54,899.86 on 2026-08-13 matches invoice INV-1211 for Nair Textiles LLP except for a shortfall of Rs 1,120.41, which corresponds to a 2% TDS deduction. The narration only contains a UTR reference and does not name the counterparty.

- **Lead:** INV-1211
- **Certainty:** high -- amount gap exactly equals expected 2% TDS on the invoice
- **Rules said:** Short of INV-1211 by Rs1120.41, which is 2% TDS.
- **Considered:** INV-1211
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000508 — ₹53,718.22 · `WRITE_OFF_SMALL`

*2026-07-10 · EXCEPTION · NEFT/KulkaMot/RETURN*

The bank credit of Rs 53,718.22 on 2026-07-10 (NEFT/KulkaMot/RETURN) closely matches invoice INV-1244 from Patel Enterprises LLP (gross Rs 53,836.88), leaving an unexplained shortfall of Rs 118.66. No other candidate invoice is within a reasonable range, and the narration does not reveal a clear counterparty beyond the generic 'KulkaMot' reference.

- **Lead:** INV-1244
- **Certainty:** moderate -- amount gap is small and the narration hints at a return, but the exact reason for the Rs 118.66 difference is not evident from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1244, INV-1199, INV-1459, INV-1495, INV-1201, INV-1468, INV-1333, INV-1067, INV-1330, INV-1396
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000425 — ₹52,059.86 · `REQUEST_REMITTANCE`

*2026-07-14 · EXCEPTION · CMS/INV-1437/IyerTex*

The credit of Rs 52,059.86 on 2026‑07‑14 references invoice INV‑1437 in the narration, but the amount does not match the invoice gross (Rs 83,295.77) nor any obvious TDS‑adjusted value; the difference is Rs ‑31,235.91, suggesting a partial or unexplained payment.

- **Lead:** INV-1437
- **Certainty:** weak -- narration points to INV‑1437 but the amount gap is large and unexplained
- **Rules said:** INV-1052 already settled by BNK-000070; suspected duplicate credit, left unapplied.
- **Considered:** INV-1437, INV-1347, INV-1162, INV-1137, INV-1112, INV-1228, INV-1381, INV-1169, INV-1124, INV-1497, INV-1156, INV-1096
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000489 — ₹51,117.37 · `CHECK_DUPLICATE`

*2026-07-30 · EXCEPTION · IMPS-190695225109-Chhxp*

A credit of Rs 51,117.37 arrived on 2026-07-30 via IMPS (UTR 190695225109) with narration 'Chhxp'. The amount exactly matches the open invoice INV-1499 (Chauhan Exports) for Rs 51,117.37, but the rule engine notes that INV-1499 was already settled by the prior transaction BNK-000488, suggesting this credit is a duplicate that was left unapplied.

- **Lead:** INV-1499
- **Certainty:** moderate -- amount matches INV-1499 exactly and rule flags suspected duplicate; however, without seeing BNK-000488 details we cannot confirm definitively.
- **Rules said:** INV-1499 already settled by BNK-000488; suspected duplicate credit, left unapplied.
- **Considered:** INV-1499, INV-1118, INV-1422, INV-1486
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000104 — ₹49,235.27 · `CHECK_DUPLICATE`

*2026-06-08 · EXCEPTION · CMS/INV-1088/IYERTEX*

The credit of Rs 49,235.25.27 matches the exact amount of invoice INV-1088 from Iyer Textiles & Co, but the rule engine notes that INV-1088 was already settled by transaction BNK-000103, suggesting this credit is a duplicate or unapplied payment.

- **Lead:** INV-1088
- **Certainty:** strong -- amount matches invoice exactly and narration references the same invoice; only uncertainty is whether it's truly a duplicate or a missed application.
- **Rules said:** INV-1088 already settled by BNK-000103; suspected duplicate credit, left unapplied.
- **Considered:** INV-1088, INV-1056, INV-1422, INV-1239, INV-1391, INV-1176, INV-1134, INV-1202, INV-1409, INV-1094, INV-1457, INV-1191
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000511 — ₹45,449.52 · `NEEDS_MORE_DATA`

*2026-06-29 · EXCEPTION · CHARGES GST @18%*

The bank credited Rs 45,449.52 on 2026-06-29 with narration 'CHARGES GST @18%', indicating a GST-related charge or refund. No invoices in the ledger match this amount, date, or any identifiable counterparty, so the transaction cannot be linked to any known invoice.

- **Lead:** —
- **Certainty:** low -- narration gives no party or invoice reference and no candidate invoices exist to compare against.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000097 — ₹43,404.58 · `REQUEST_REMITTANCE`

*2026-05-18 · EXCEPTION · BY TRANSFER-399189023133-*

A credit of Rs 43,404.58 arrived on 2026-05-18 via UTR 399189023133 with narration 'BY TRANSFER-399189023133-'. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** low -- no invoice matches the amount or narration; the transaction appears to be an unmatched bank credit needing remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000228 — ₹42,676.95 · `REQUEST_REMITTANCE`

*2026-08-17 · EXCEPTION · IMPS-844942570107-MalhoPol*

The bank credit of Rs 42,676.95 on 2026-08-17 (IMPS-844942570107-MalhoPol) does not exactly match any open invoice; the closest is INV-1162 for Iyer Textiles & Co (Rs 42,844.92), leaving a small unexplained gap of Rs -167.97. The narration mentions 'MalhoPol', which aligns with the counterparty name in INV-1162.

- **Lead:** INV-1162
- **Certainty:** moderate -- counterparty name matches and amount gap is small, but the exact reason for the Rs 167.97 difference is unclear from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1473, INV-1216, INV-1315, INV-1000, INV-1162, INV-1170, INV-1291, INV-1302, INV-1305, INV-1182, INV-1104, INV-1126
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000108 — ₹41,975.61 · `NEEDS_MORE_DATA`

*2026-05-19 · EXCEPTION · INB/248075879021/PAYMENT*

A credit of Rs 41,975.61 arrived on 2026-05-19 with narration INB/248075879021/PAYMENT. The two open invoices considered are INV-1092 (Rs 46,639.57) and INV-1319 (Rs 42,094.62); neither matches the amount, with gaps of Rs -4,663.96 and Rs -119.01 respectively.

- **Lead:** —
- **Certainty:** weak -- no invoice amount aligns; the narration does not reveal a counterparty or purpose.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1092, INV-1319
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000039 — ₹39,868.11 · `NEEDS_MORE_DATA`

*2026-07-01 · EXCEPTION · BY TRANSFER-870599136454-*

A bank credit of Rs 39,868.11 arrived on 2026-07-01 via UTR 870599136454 with narration 'BY TRANSFER-870599136454-'. The narration does not name a counterparty or invoice, and no ledger invoice matches the amount, date, or any identifiable party.

- **Lead:** —
- **Certainty:** low -- no counterparty or invoice details in narration and no close matches in ledger.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000034 — ₹39,018.97 · `CHECK_DUPLICATE`

*2026-06-25 · EXCEPTION · BY TRANSFER-782196862986-*

A credit of Rs 39,018.97 arrived on 2026-06-25 via UTR 782196862986 with narration 'BY TRANSFER-782196862986-'. The amount exactly matches the open invoice INV-1012 (Nair Industries LLP) for Rs 39,018.97, but the rule engine flagged it as a suspected duplicate because INV-1012 was already settled by the prior credit BNK-000033, leaving this credit unapplied.

- **Lead:** INV-1012
- **Certainty:** strong -- amount matches INV-1012 exactly and narration references the same UTR; the only issue is the prior settlement indicating a possible duplicate.
- **Rules said:** INV-1012 already settled by BNK-000033; suspected duplicate credit, left unapplied.
- **Considered:** INV-1012, INV-1134, INV-1183
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000462 — ₹38,990.82 · `CHECK_DUPLICATE`

*2026-07-21 · EXCEPTION · IMPS-634628497195-NAIRIND*

Credit of Rs 38,990.82 received on 2026-07-21 from Nair Industries (UTR 634628497195) is Rs 28.15 short of the gross amount of INV-1012 (Rs 39,018.97), which the rules engine already marked as settled by BNK-000033 and flagged as a suspected duplicate credit.

- **Lead:** INV-1012
- **Certainty:** moderate -- amount gap small and narration matches counterparty, but rules already indicate duplicate.
- **Rules said:** INV-1012 already settled by BNK-000033; suspected duplicate credit, left unapplied.
- **Considered:** INV-1012, INV-1192, INV-1118, INV-1376, INV-1474, INV-1452, INV-1097, INV-1062, INV-1134, INV-1151, INV-1402, INV-1102
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000379 — ₹38,290.11 · `REQUEST_REMITTANCE`

*2026-07-07 · EXCEPTION · UPI/721065037997/mhtch@okicicbank*

The bank credit of Rs 38,290.11 on 2026-07-07 (UPI transaction with UTR 721065037997) is close to invoice INV-1478 from Reddy Textiles LLP (gross Rs 38,465.57), leaving an unexplained shortfall of Rs 175.46. No other candidate invoice matches the amount within a reasonable tolerance.

- **Lead:** INV-1478
- **Certainty:** moderate -- amount gap is small and could be a bank fee or rounding, but the exact cause is not evident from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1386, INV-1478
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000203 — ₹38,112.96 · `NEEDS_MORE_DATA`

*2026-06-27 · EXCEPTION · RTGS AXIS892239961619 AGARWTEX*

The bank credit of Rs 38,112.96 on 2026-06-27 (RTGS from AXIS, UTR 892239961619, narration mentions AGARWTEX) does not match any invoice amount; the closest invoice (INV-1082 for Iyer Infotech) differs by only Rs 70.27 but the counterparty name does not agree with the narration.

- **Lead:** —
- **Certainty:** weak -- narration points to Agarwal but no invoice matches amount; the nearest amount belongs to a different party.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1329, INV-1072, INV-1117, INV-1082, INV-1188, INV-1345, INV-1166, INV-1464, INV-1129, INV-1301, INV-1214, INV-1297
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000168 — ₹37,186.71 · `NEEDS_MORE_DATA`

*2026-05-21 · EXCEPTION · INB/826871449481/PAYMENT*

A credit of Rs 37,186.71 arrived on 2026‑05‑21 with narration 'INB/826871449481/PAYMENT' and UTR 826871449481. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration gives no party name and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000036 — ₹36,454.06 · `REQUEST_REMITTANCE`

*2026-06-17 · EXCEPTION · UPI/734582145502/nairtex@okyesbbank*

The bank credit of Rs 36,454.06 on 2026-06-17 comes from a UPI transaction to nairtex@okyesbbank (likely Nair Textiles). The amount is closest to invoice INV-1120 (Reddy Packaging Ltd) which is Rs 25.39 higher; no other candidate matches within a reasonable tolerance, and the narration does not reference Reddy Packaging.

- **Lead:** INV-1120
- **Certainty:** weak -- amount close to INV-1120 but narration points to Nair Textiles, leaving the match uncertain.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1120, INV-1496, INV-1014, INV-1427, INV-1151, INV-1012, INV-1402, INV-1255, INV-1260, INV-1342, INV-1420, INV-1084
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000500 — ₹36,305.31 · `REQUEST_REMITTANCE`

*2026-05-21 · EXCEPTION · INT.PD:566529280853*

The bank credit of Rs 36,305.31 on 2026-05-21 (UTR 566529280853) is Rs 24.94 less than the open invoice INV-1003 for Iyer Traders LLP (gross Rs 36,330.25, issued 2026-05-09). The narration only shows an internal payment reference, with no clear counterparty or remittance details, making the small shortfall unexplained by the data.

- **Lead:** INV-1003
- **Certainty:** weak -- amount close to invoice but the Rs 24.94 gap lacks explanation; narration gives no payer info.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1003
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000308 — ₹35,496.25 · `CONFIRM_MATCH`

*2026-06-27 · NEEDS_REVIEW · INB/817447859849/PAYMENT*

The bank credit of Rs 35,496.25 on 2026-06-27 matches invoice INV-1305 (gross Rs 39,440.28) less a Rs 3,944.03 TDS deduction, which is exactly 10% of the invoice amount. The narration only contains a UTR reference and does not name the counterparty.

- **Lead:** INV-1305
- **Certainty:** strong -- amount gap equals 10% TDS on INV-1305, dates align, and rule engine flagged the same.
- **Rules said:** Short of INV-1305 by Rs3944.03, which is 10% TDS.
- **Considered:** INV-1305
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000183 — ₹35,293.46 · `CHECK_DUPLICATE`

*2026-07-27 · EXCEPTION · IMPS-477789298437-IYERTEX*

A credit of Rs 35,293.46 arrived on 2026-07-27 from Iyer Textiles & Co (UTR 477789298437). It is Rs 34.40 short of the open invoice INV-1169 (Rs 35,327.86) and the rules engine flagged it as a suspected duplicate of the earlier settlement BNK-000255, leaving it unapplied.

- **Lead:** INV-1169
- **Certainty:** moderate -- amount very close to INV-1169, narration matches counterparty, but small unexplained gap and duplicate flag suggest need to verify if this is a duplicate credit.
- **Rules said:** INV-1169 already settled by BNK-000255; suspected duplicate credit, left unapplied.
- **Considered:** INV-1169, INV-1185, INV-1336, INV-1497, INV-1381, INV-1394, INV-1037, INV-1228, INV-1162, INV-1347, INV-1446, INV-1096
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000133 — ₹34,827.30 · `CONFIRM_MATCH`

*2026-07-02 · NEEDS_REVIEW · NEFT/AgarwTex/1117/SBIN*

The credit of Rs 34,827.30 on 2026-07-02 comes from a NEFT payment referencing AgarwTex/1117, which matches invoice INV-1117 from Agarwal Textiles Pvt Ltd. The amount is only Rs 8.64 short of the invoice total, a difference that can be explained by rounding or minor bank charges, leaving no outstanding balance.

- **Lead:** INV-1117
- **Certainty:** strong -- narration explicitly cites invoice 1117 and the amount gap is minimal and plausibly due to rounding/charges.
- **Rules said:** Part payment against INV-1087 (the counterparty name matches and no other open invoice fits); Rs17409.15 still outstanding, with no TDS or charge explaining it.
- **Considered:** INV-1117, INV-1309, INV-1140, INV-1072, INV-1254, INV-1329, INV-1166, INV-1034, INV-1188, INV-1464, INV-1345, INV-1087
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000519 — ₹33,908.89 · `NEEDS_MORE_DATA`

*2026-05-22 · EXCEPTION · IMPS-249634121987-UNKNOWN REMITTER*

A credit of Rs 33,908.89 arrived on 2026-05-22 via IMPS from an unknown remitter (UTR 249634121987). The narration does not identify any counterparty, and no invoice in the ledger matches this amount, date, or party, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** weak -- narration provides no identifiable party and no invoice matches the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000117 — ₹33,389.41 · `REQUEST_REMITTANCE`

*2026-05-17 · EXCEPTION · UPI/148879334922/iyrpl@oksbinbank*

The bank credit of Rs 33,389.41 on 2026-05-17 (UPI transaction with UTR 148879334922) is close to the amount of invoice INV-1103 for Iyer Polymers & Co (Rs 33,415.24), differing by only Rs 25.83. No other invoice matches as closely, and the narration does not reveal a clear counterparty beyond the UPI ID.

- **Lead:** INV-1103
- **Certainty:** weak -- amount gap is small but unexplained; narration gives no further detail.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1103, INV-1231, INV-1061
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000296 — ₹33,090.45 · `REQUEST_REMITTANCE`

*2026-06-13 · EXCEPTION · RTGS UTIB391955247365 CHAUHLOG*

The bank credit of Rs 33,090.45 on 2026-06-13 (RTGS from Chauhan Logistics) does not exactly match any open invoice; the closest is INV-1288 for Chauhan Logistics LLP, which is only Rs 134.88 short of the payment.

- **Lead:** INV-1288
- **Certainty:** moderate -- amount gap is small and counterparty name matches, but the exact reason for the Rs 134.88 difference is unclear without remittance details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1309, INV-1076, INV-1288, INV-1414, INV-1377, INV-1485, INV-1139, INV-1001, INV-1429, INV-1099, INV-1066, INV-1348
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000504 — ₹32,972.34 · `NEEDS_MORE_DATA`

*2026-05-12 · EXCEPTION · INT.PD:684650796321*

Bank credit of Rs 32,972.34 on 2026-05-12 with narration 'INT.PD:684650796321' (UTR same) shows no matching invoice in the ledger; the amount and date do not correspond to any recorded transaction, and the narration does not reveal a counterparty.

- **Lead:** —
- **Certainty:** weak -- no invoice matches amount, date, or narration; cannot infer purpose without additional remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000331 — ₹30,210.32 · `NEEDS_MORE_DATA`

*2026-07-01 · EXCEPTION · IMPS-136522163791-KLKDS*

A bank credit of Rs 30,210.32 was received on 2026-07-01 via IMPS (UTR 136522163791). No invoice in the ledger matches this amount, date, or counterparty, so the transaction remains unmatched.

- **Lead:** —
- **Certainty:** weak -- no candidate invoices were found, so the correct action is to request more information.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000394 — ₹29,263.86 · `NEEDS_MORE_DATA`

*2026-06-19 · EXCEPTION · INB/307625384548/PAYMENT*

A credit of Rs 29,263.86 was received on 2026-06-19 with narration 'INB/307625384548/PAYMENT' and UTR 307625384548. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration provides only a UTR, no counterparty name, and no invoice matches the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000100 — ₹29,204.64 · `REQUEST_REMITTANCE`

*2026-06-12 · EXCEPTION · NEFT-NAIRIND*

A credit of Rs 29,204.64 arrived on 2026-06-12 from NEFT-NAIRIND (UTR 787461096985). The narration points to Nair Industries LLP, but none of the open invoices for that party match the amount; the closest is INV-1260 which is Rs 3,828.29 short.

- **Lead:** —
- **Certainty:** weak -- narration names Nair Industries but amount gap unexplained and no invoice fits.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1260, INV-1151, INV-1402, INV-1031, INV-1395, INV-1349, INV-1012, INV-1328, INV-1255, INV-1342, INV-1084, INV-1284
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000507 — ₹28,960.68 · `REQUEST_REMITTANCE`

*2026-05-22 · NEEDS_REVIEW · NEFT/IyerPol/RETURN*

The bank credit of Rs 28,960.68 on 2026-05-22 is labelled as a NEFT return from 'IyerPol'. The amount is close to several open invoices from Iyer group (e.g., INV-1286 differs by only Rs 46.58) but the narration suggests a return/refund rather than a regular payment, leaving the exact invoice unclear.

- **Lead:** INV-1286
- **Certainty:** moderate -- amount matches INV-1286 within Rs 50, but narration indicates a return, so certainty is limited.
- **Rules said:** Part payment against INV-1103 (the counterparty name matches and no other open invoice fits); Rs4454.56 still outstanding, with no TDS or charge explaining it.
- **Considered:** INV-1074, INV-1051, INV-1480, INV-1103, INV-1466, INV-1494, INV-1286, INV-1168, INV-1231, INV-1479, INV-1090, INV-1150
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000497 — ₹28,507.78 · `NEEDS_MORE_DATA`

*2026-07-28 · EXCEPTION · NEFT/RastoPac/RETURN*

A credit of Rs 28,507.78 arrived on 2026-07-28 with narration 'NEFT/RastoPac/RETURN', indicating a return/refund from a party likely related to Rastogi Packaging. No invoice in the list matches this amount exactly; the closest is INV-1302 (Malhotra Polymers) which is Rs 41.24 higher, and the narration does not reference that counterparty.

- **Lead:** —
- **Certainty:** weak -- narration points to Rastogi but amount does not correspond to any invoice; insufficient data to decide.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1302, INV-1147, INV-1323, INV-1063, INV-1189, INV-1136, INV-1453, INV-1238, INV-1424, INV-1313, INV-1292, INV-1133
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000484 — ₹28,192.36 · `REQUEST_REMITTANCE`

*2026-05-29 · EXCEPTION · NEFT-IyerTex*

The bank credit of Rs 28,192.36 from IyerTex (UTR 159292331857) on 2026-05-29 does not correspond to any of the open invoices for Iyer Textiles & Co; the closest invoice amounts differ by several thousand rupees and none match after considering applicable TDS.

- **Lead:** —
- **Certainty:** weak -- narration names the party but no invoice amount fits the credit within a reasonable tolerance.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1231, INV-1472, INV-1494, INV-1094, INV-1168, INV-1088, INV-1134, INV-1150, INV-1391, INV-1239, INV-1202, INV-1422
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000359 — ₹27,431.56 · `NEEDS_MORE_DATA`

*2026-06-10 · EXCEPTION · RTGS YESB400729201651 BSMT*

A Rs 27,431.56 credit arrived on 2026-06-10 via RTGS (UTR 400729201651) with narration 'RTGS YESB400729201651 BSMT'. No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** low -- no candidate invoices were even close on amount, date, or counterparty.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000520 — ₹26,772.28 · `NEEDS_MORE_DATA`

*2026-07-01 · EXCEPTION · IMPS-373499493785-UNKNOWN REMITTER*

A credit of Rs 26,772.28 arrived on 2026-07-01 via IMPS from an unknown remitter (UTR 373499493785). No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** low -- narration gives no counterparty and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000141 — ₹26,465.17 · `REQUEST_REMITTANCE`

*2026-06-06 · EXCEPTION · BY TRANSFER-439608402193-*

The bank credit of Rs 26,465.17 on 2026-06-06 (UTR 439608402193) is very close to invoice INV-1126 for Malhotra Solutions LLP, differing by only Rs 18.47. No other invoice matches the amount, and the narration does not identify a counterparty.

- **Lead:** INV-1126
- **Certainty:** weak -- amount gap is small but unexplained; narration gives no party name.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1126, INV-1031
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000120 — ₹26,193.89 · `REQUEST_REMITTANCE`

*2026-07-18 · EXCEPTION · RTGS AXIS106872386235 IYRINF*

The bank credit of Rs 26,193.89 on 2026-07-18 (UTR 106872386235, narration RTGS AXIS106872386235 IYRINF) is close to the gross amount of invoice INV-1173 (Iyer Solutions & Co, Rs 26,239.18) but is Rs 45.29 short. No rule could explain this small gap, and the narration does not reference any invoice number.

- **Lead:** INV-1173
- **Certainty:** moderate -- amount matches within ~0.2% and counterparty name appears in narration, but the exact shortfall is unexplained.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1091, INV-1173, INV-1322, INV-1337
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000182 — ₹25,441.26 · `CHECK_DUPLICATE`

*2026-05-28 · EXCEPTION · BY TRANSFER-723290823647-*

A credit of Rs 25,441.26 was received on 2026-05-28 via UTR 723290823647 with no counterparty name in the narration. The amount exactly matches the open invoice INV-1168 for Iyer Textiles & Co, but the rule engine already marked INV-1168 as settled by a prior credit (BNK-000181) and flagged this as a suspected duplicate credit.

- **Lead:** INV-1168
- **Certainty:** high -- amount matches INV-1168 exactly and the rule engine already flagged it as a duplicate of a settled invoice.
- **Rules said:** INV-1168 already settled by BNK-000181; suspected duplicate credit, left unapplied.
- **Considered:** INV-1168, INV-1257, INV-1020
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000499 — ₹25,326.92 · `CHECK_REFUND`

*2026-06-15 · EXCEPTION · REFUND/427025971044/GATEWAY*

A gateway refund of Rs 25,326.92 was received on 2026-06-15 (UTR 427025971044). The amount does not exactly match any open invoice; the closest is INV-1262 (difference Rs -17.37), suggesting a possible short‑payment or fee deduction.

- **Lead:** —
- **Certainty:** weak -- narration indicates a refund but no invoice matches the exact amount; only a small gap to the nearest candidate.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1262, INV-1260, INV-1010, INV-1168
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000072 — ₹24,614.48 · `CHECK_DUPLICATE`

*2026-05-17 · EXCEPTION · UPI/648395272101/chtttx@okutibbank*

A UPI credit of Rs 24,614.48 on 2026-05-17 matches the exact amount of invoice INV-1053 (Chatterjee Textiles), but the rule engine notes that INV-1053 was already settled by transaction BNK-000071, suggesting this credit is a duplicate or unapplied payment.

- **Lead:** INV-1053
- **Certainty:** moderate -- amount matches exactly and narration points to Chatterjee Textiles, but rule indicates prior settlement.
- **Rules said:** INV-1053 already settled by BNK-000071; suspected duplicate credit, left unapplied.
- **Considered:** INV-1053, INV-1133, INV-1030, INV-1224, INV-1364, INV-1488, INV-1280, INV-1028
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000099 — ₹24,475.45 · `REQUEST_REMITTANCE`

*2026-05-24 · EXCEPTION · UPI/531600975146/iyerinf@okutibbank*

A UPI credit of Rs 24,475.45 arrived on 2026-05-24 from iyerinf@okutibbank (UTR 531600975146). The narration points to Iyer Infotech, but none of the candidate invoices match this amount; the closest is INV-1395 (Nair Industries LLP) which is off by Rs 105.97 and involves a different party.

- **Lead:** —
- **Certainty:** weak -- narration suggests Iyer Infotech but no invoice amount fits; the nearest candidate is from a different vendor and still off by ~Rs 106.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1395, INV-1466, INV-1441, INV-1479, INV-1074, INV-1051, INV-1286, INV-1469, INV-1481, INV-1082, INV-1080, INV-1494
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000245 — ₹24,420.64 · `REQUEST_REMITTANCE`

*2026-06-28 · EXCEPTION · NEFT-RastoPac*

A credit of Rs 24,420.64 arrived via NEFT with narration 'NEFT-RastoPac'. The amount does not exactly match any open invoice; the closest is INV-1349 (Nair Industries LLP, Rs 24,457.71, difference –Rs 37.07), but the narration points to a Rastogi counterparty, making the match uncertain.

- **Lead:** INV-1133
- **Certainty:** weak -- narration suggests Rastogi Packaging, but amount gap (–Rs 303) remains unexplained and no clear tie to any invoice.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1349, INV-1238, INV-1424, INV-1313, INV-1292, INV-1133, INV-1020
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000475 — ₹23,106.23 · `CHECK_DUPLICATE`

*2026-06-11 · EXCEPTION · BY TRANSFER-194967664826-*

A credit of Rs 23,106.23 arrived on 2026-06-11 with UTR 194967664826 and narration 'BY TRANSFER-194967664826-'. The amount exactly matches open invoice INV-1485 (Chauhan Exports) but the rule engine already marked INV-1485 as settled by a prior credit (BNK-000474) and flagged this as a suspected duplicate credit.

- **Lead:** —
- **Certainty:** moderate -- amount matches INV-1485 exactly, but rules indicate it is a duplicate of an already settled payment.
- **Rules said:** INV-1485 already settled by BNK-000474; suspected duplicate credit, left unapplied.
- **Considered:** INV-1485
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000272 — ₹22,840.81 · `CHECK_DUPLICATE`

*2026-05-29 · EXCEPTION · UPI/787274668013/nairche@okyesbbank*

A UPI credit of Rs 22,840.81 on 2026-05-29 from nairche@okyesbbank does not match any open invoice; the rule engine notes that INV-1266 (Rs 37,753.40) was already settled by this transaction, suggesting a duplicate credit that was left unapplied.

- **Lead:** INV-1266
- **Certainty:** weak -- amount does not equal any invoice; only clue is the rule's duplicate‑credit flag for INV-1266.
- **Rules said:** INV-1266 already settled by BNK-000272; suspected duplicate credit, left unapplied.
- **Considered:** INV-1266, INV-1349, INV-1395, INV-1031, INV-1269, INV-1328, INV-1284, INV-1496, INV-1010, INV-1084, INV-1382, INV-1091
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000503 — ₹22,651.04 · `CHECK_REFUND`

*2026-07-17 · EXCEPTION · REFUND/560266060308/GATEWAY*

A credit of Rs 22,651.04 arrived on 2026-07-17 with narration indicating a refund (UTR 560266060308). The only open invoice considered is INV-1235 for Rs 22,705.01, leaving an unexplained shortfall of Rs 53.97. This most likely represents a partial refund of that invoice, perhaps after a small deduction or adjustment.

- **Lead:** INV-1235
- **Certainty:** moderate -- amount close to invoice but a small gap remains unexplained
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1235
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000430 — ₹22,441.41 · `NEEDS_MORE_DATA`

*2026-06-01 · EXCEPTION · INB/882724690983/PAYMENT*

A bank credit of Rs 22,441.41 was received on 2026-06-01 with narration 'INB/882724690983/PAYMENT' and UTR 882724690983. No invoice in the ledger matches this amount, date, or counterparty, leaving the transaction unresolved.

- **Lead:** —
- **Certainty:** weak -- no candidate invoices were close on amount, date, or counterparty.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000498 — ₹21,720.48 · `NEEDS_MORE_DATA`

*2026-05-06 · EXCEPTION · IMPS-767232262429-UNKNOWN REMITTER*

An IMPS credit of Rs 21,720.48 arrived on 2026-05-06 from an unknown remitter (UTR 767232262429). The narration does not identify any counterparty, and no invoice in the ledger matches this amount, date, or party, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** weak -- narration gives no identifiable party and no invoice candidate exists.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000310 — ₹20,148.14 · `REQUEST_REMITTANCE`

*2026-07-01 · EXCEPTION · UPI/331294064172/chhxp@oksbinbank*

A UPI credit of Rs 20,148.14 was received on 2026-07-01 from chhxp@oksbinbank (UTR 331294064172). The amount is Rs 81.02 less than the open invoice INV-1224 for Chatterjee Textiles (gross Rs 20,229.16, issued 2026-05-22, due 2026-06-21). No rule could explain this specific shortfall.

- **Lead:** INV-1224
- **Certainty:** weak -- amount close to invoice but unexplained Rs 81.02 difference; narration gives no remittance details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1224
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000319 — ₹19,817.90 · `REQUEST_REMITTANCE`

*2026-05-17 · EXCEPTION · INB/284740736556/PAYMENT*

Bank credit of Rs 19,817.90 on 2026-05-17 (UTR 284740736556) does not exactly match any open invoice; the closest is INV-1033 for Rs 19,824.34, leaving an unexplained shortfall of Rs 6.44. The narration only contains a generic payment reference with no counterparty name.

- **Lead:** INV-1033
- **Certainty:** weak -- amount gap is small but unexplained; narration gives no party details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1033, INV-1320
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000208 — ₹19,742.99 · `REQUEST_REMITTANCE`

*2026-06-11 · EXCEPTION · RTGS PUNB643109100172 MEHTACHE*

The credit of Rs 19,742.99 on 2026‑06‑11 comes from an RTGS to UTR 643109100172 with narration naming ‘MEHTACHE’, suggesting a payment from Mehta Chemicals. None of the candidate invoices match this amount; the closest is INV‑1033 (Iyer Textiles) which is off by Rs 81.35 and involves a different party.

- **Lead:** —
- **Certainty:** weak -- narration hints at Mehta Chemicals but no invoice amount fits; the nearest candidate is unrelated and still off by ~Rs 81.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1195, INV-1033, INV-1386, INV-1044, INV-1296, INV-1183, INV-1225
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000204 — ₹19,052.16 · `REQUEST_REMITTANCE`

*2026-08-11 · EXCEPTION · INB/614758923004/PAYMENT*

The bank credit of Rs 19,052.16 on 2026‑08‑11 (UTR 614758923004) does not exactly match any open invoice. The closest candidate is INV‑1189 (Rastogi Motors LLP, gross Rs 19,064.67), leaving an unexplained shortfall of Rs 12.51.

- **Lead:** INV-1189
- **Certainty:** moderate – amount is near INV‑1189 but the small gap lacks explanation (no TDS, discount, or fee noted).
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1316, INV-1189
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000130 — ₹17,803.93 · `CHECK_DUPLICATE`

*2026-07-15 · EXCEPTION · NEFT/IYERTEX/INV-1113/UTIB*

The credit of Rs 17,803.93 on 2026-07-15 from NEFT/IYERTEX/INV-1113/UTIB matches the exact gross amount of invoice INV-1113 (Iyer Textiles & Co). The rule engine flagged it as a suspected duplicate because INV-1113 was already settled by transaction BNK-000129.

- **Lead:** INV-1113
- **Certainty:** strong -- amount matches exactly but flagged as duplicate credit
- **Rules said:** INV-1113 already settled by BNK-000129; suspected duplicate credit, left unapplied.
- **Considered:** INV-1113, INV-1498, INV-1340, INV-1179, INV-1324, INV-1169, INV-1446, INV-1221, INV-1037, INV-1347, INV-1149, INV-1162
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000267 — ₹17,132.74 · `NEEDS_MORE_DATA`

*2026-05-24 · EXCEPTION · INB/864591805783/PAYMENT*

A credit of Rs 17,132.74 arrived on 2026-05-24 with the narration 'INB/864591805783/PAYMENT' and UTR 864591805783. No invoice in the ledger matches this amount, date, or counterparty, so the payment remains unidentified.

- **Lead:** —
- **Certainty:** weak -- no candidate invoices were close on amount, date or counterparty
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000192 — ₹17,122.14 · `CHECK_DUPLICATE`

*2026-07-24 · EXCEPTION · UPI/734298329757/iyertex@okaxisbank*

The credit of Rs 17,122.14 on 2026-07-24 from UPI transaction (UTR 734298329757) matches the exact amount of open invoice INV-1179 for Iyer Textiles & Co, but the rule engine notes that INV-1179 was already settled by another credit (BNK-000425), suggesting this is a duplicate or unapplied credit.

- **Lead:** INV-1179
- **Certainty:** strong -- amount matches invoice exactly and narration points to same counterparty; only uncertainty is whether it's truly a duplicate or a missed application.
- **Rules said:** INV-1179 already settled by BNK-000425; suspected duplicate credit, left unapplied.
- **Considered:** INV-1179, INV-1113, INV-1340, INV-1336, INV-1185, INV-1497, INV-1381, INV-1324, INV-1394, INV-1169, INV-1446, INV-1221
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000491 — ₹17,047.64 · `NEEDS_MORE_DATA`

*2026-07-08 · EXCEPTION · INT.PD:239893197000*

The bank credit of Rs 17,047.64 on 2026-07-08 is an interest payment (INT.PD) identified by UTR 239893197000. No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest payment but no invoice data to verify.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000518 — ₹16,145.87 · `REQUEST_REMITTANCE`

*2026-05-29 · EXCEPTION · REFUND/592234921273/GATEWAY*

A credit of Rs 16,145.87 was received on 2026-05-29 with narration 'REFUND/592234921273/GATEWAY' and UTR 592234921273, indicating a gateway refund. No invoice in the ledger matches this amount, date, or counterparty, so the transaction cannot be auto‑matched.

- **Lead:** —
- **Certainty:** weak -- narration suggests a refund but no corresponding invoice exists in the data.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000042 — ₹15,671.27 · `CONFIRM_MATCH`

*2026-06-15 · NEEDS_REVIEW · INB/446692166741/PAYMENT*

The bank credit of Rs 15,671.27 on 2026-06-15 (UTR 446692166741) matches invoice INV-1023 from Reddy Industries except for a Rs 319.82 shortfall, which corresponds to the 2% TDS that would be deducted on the gross invoice amount of Rs 15,991.09.

- **Lead:** INV-1023
- **Certainty:** moderate -- amount gap exactly equals expected TDS, narration contains only a UTR with no party name.
- **Rules said:** Short of INV-1023 by Rs319.82, which is 2% TDS.
- **Considered:** INV-1023
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000244 — ₹15,638.94 · `REQUEST_REMITTANCE`

*2026-08-02 · EXCEPTION · IMPS-564194073710-IyrLg*

The bank credit of Rs 15,638.94 on 2026-08-02 (IMPS transfer UTR 564194073710) does not exactly match any invoice; the closest candidate is INV-1448 for Rs 15,700.55, leaving an unexplained shortfall of Rs 61.61. The narration does not reveal a counterparty or purpose, so the mismatch likely stems from a bank charge, partial payment, or rounding difference.

- **Lead:** INV-1448
- **Certainty:** weak -- amount close to INV-1448 but the Rs 61.61 gap lacks explanation and the narration gives no clues.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1448
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000029 — ₹15,052.34 · `REQUEST_REMITTANCE`

*2026-07-23 · EXCEPTION · NEFT-AgarwInd*

Credit of Rs 15,052.34 received on 2026-07-23 from NEFT-AgarwInd (UTR 383281909609). No single invoice matches this amount; the closest candidates are INV-1403 (Rs 9,016.47) and INV-1207 (Rs 8,347.31), both leaving unexplained gaps of roughly Rs 6,000–6,700. The narration only indicates a generic Agarwal entity, so the payment could be a partial settlement of one or more invoices or a mis‑applied amount.

- **Lead:** —
- **Certainty:** weak -- narration names Agarwal but amount does not correspond to any invoice; likely partial payment needing remittance details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1009, INV-1312, INV-1198, INV-1403, INV-1166, INV-1034, INV-1072, INV-1329, INV-1117, INV-1188, INV-1345, INV-1207
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000273 — ₹14,912.59 · `CHECK_DUPLICATE`

*2026-07-01 · EXCEPTION · NEFT/NairChe/INV-1266/SBIN*

The bank credit of Rs 14,912.59 on 2026-07-01 references INV-1266 in the narration, but INV-1266 was already settled by transaction BNK-000272. The amount does not match any open invoice exactly; the closest is INV-1311 (Nair Industries LLP) which is Rs 213.30 lower.

- **Lead:** —
- **Certainty:** weak -- narration points to INV-1266 (already settled) and no invoice matches the amount; closest match is INV-1311 but the gap is unexplained.
- **Rules said:** INV-1266 already settled by BNK-000272; suspected duplicate credit, left unapplied.
- **Considered:** INV-1266, INV-1254, INV-1311, INV-1060, INV-1328, INV-1012, INV-1260, INV-1269, INV-1151, INV-1349, INV-1395, INV-1402
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000085 — ₹13,689.41 · `CONFIRM_MATCH`

*2026-05-29 · NEEDS_REVIEW · IMPS-859775523172-ChhLg*

The bank credit of Rs 13,689.41 on 2026-05-29 (IMPS-859775523172-ChhLg) is Rs 1,521.04 short of invoice INV-1066 (Chauhan Logistics LLP, gross Rs 15,210.45). The shortfall equals exactly 10% TDS, suggesting tax was deducted at source.

- **Lead:** INV-1066
- **Certainty:** strong -- amount gap matches 10% TDS on INV-1066
- **Rules said:** Short of INV-1066 by Rs1521.04, which is 10% TDS.
- **Considered:** INV-1066
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000201 — ₹13,249.71 · `CHECK_DUPLICATE`

*2026-06-04 · EXCEPTION · BY TRANSFER-846238055371-*

A credit of Rs 13,249.71 arrived on 2026-06-04 via UTR 846238055371 with narration 'BY TRANSFER-846238055371-'. The amount exactly matches open invoice INV-1186, but the rule engine already marked INV-1186 as settled by a prior credit (BNK-000200) and flagged this as a suspected duplicate credit that remains unapplied.

- **Lead:** —
- **Certainty:** moderate -- amount matches INV-1186 but rules indicate it's a duplicate of an already settled payment.
- **Rules said:** INV-1186 already settled by BNK-000200; suspected duplicate credit, left unapplied.
- **Considered:** INV-1186
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000047 — ₹13,143.44 · `WRITE_OFF_SMALL`

*2026-05-14 · EXCEPTION · INB/398051211124/PAYMENT*

Bank credit of Rs 13,143.44 on 2026-05-14 (UTR 398051211124) does not fully match invoice INV-1028 for Chatterjee Textiles, leaving a Rs 38.30 shortfall; the narration only shows a generic payment reference with no counterparty details.

- **Lead:** INV-1028
- **Certainty:** weak -- amount gap is small and could be a bank fee or rounding, but no evidence confirms it.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1028
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000185 — ₹12,693.60 · `WRITE_OFF_SMALL`

*2026-06-20 · EXCEPTION · INB/795291700490/PAYMENT*

The bank credit of Rs 12,693.60 on 2026-06-20 (UTR 795291700490) is very close to invoice INV-1200 for Venkat Distributors (gross Rs 12,714.70), differing by only Rs 21.10. No rule could explain this small gap, and the narration does not name a counterparty or reference any invoice.

- **Lead:** INV-1200
- **Certainty:** weak -- amount matches within a small Rs 21.10 gap, but no clear reason (e.g., fee, TDS) is evident from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1200, INV-1172
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000311 — ₹12,156.31 · `REQUEST_REMITTANCE`

*2026-07-01 · EXCEPTION · UPI/855500785939/nairind@okutibbank*

The bank credit of Rs 12,156.31 on 2026-07-01 from UPI transaction (UTR 855500785939) narrated as UPI/855500785939/nairind@okutibbank does not exactly match any open invoice for Nair Industries LLP; the closest is INV-1060 (Rs 13,099.41) leaving an unexplained shortfall of Rs 943.10.

- **Lead:** INV-1060
- **Certainty:** weak -- amount close to INV-1060 but gap unexplained, no remittance details provided.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1060, INV-1311, INV-1012, INV-1328, INV-1260, INV-1318, INV-1269, INV-1151, INV-1337, INV-1349, INV-1395, INV-1402
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000322 — ₹11,787.74 · `REQUEST_REMITTANCE`

*2026-07-31 · EXCEPTION · UPI/224647754147/iyertex@okyesbbank*

The bank credit of Rs 11,787.74 on 2026-07-31 from UPI transaction iyertex@okyesbbank does not exactly match any open invoice. The closest is INV-1005 (Iyer Textiles & Co, Rs 11,825.16) leaving a small unexplained difference of Rs 37.42.

- **Lead:** INV-1005
- **Certainty:** weak -- amount gap is small but unexplained; narration points to Iyer Textiles but no rule fits the exact amount.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1324, INV-1005, INV-1208, INV-1179, INV-1325, INV-1336, INV-1185, INV-1113, INV-1340, INV-1169, INV-1446, INV-1037
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000494 — ₹11,512.55 · `NEEDS_MORE_DATA`

*2026-06-10 · EXCEPTION · IMPS-298072407250-UNKNOWN REMITTER*

A credit of Rs 11,512.55 arrived on 2026-06-10 via IMPS from an unknown remitter (UTR 298072407250). No invoice in the ledger matches this amount, date, or counterparty, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** low -- narration provides no identifiable party and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000059 — ₹11,233.10 · `CONFIRM_MATCH`

*2026-06-24 · NEEDS_REVIEW · INB/441107346461/PAYMENT*

The bank credit of Rs 11,233.10 on 2026-06-24 (UTR 441107346461) matches invoice INV-1041 for Bose Infotech & Co after a 10% TDS deduction (Rs 1,248.12) from the invoice gross of Rs 12,481.22. The narration does not name a counterparty, but the UTR ties the payment to the invoice.

- **Lead:** INV-1041
- **Certainty:** strong -- amount gap equals exactly 10% TDS of the invoice, and the UTR references the payment.
- **Rules said:** Short of INV-1041 by Rs1248.12, which is 10% TDS.
- **Considered:** INV-1041
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000300 — ₹10,976.53 · `CHECK_DUPLICATE`

*2026-06-30 · EXCEPTION · NEFT-IyerInf*

The credit of Rs 10,976.53 on 2026-06-30 from NEFT-IyerInf exactly matches the outstanding amount of invoice INV-1295 (Iyer Infotech). However, the rule engine flagged it as a suspected duplicate because INV-1295 was already settled by another transaction (BNK-000160).

- **Lead:** INV-1295
- **Certainty:** strong -- amount matches invoice exactly, but already marked as settled/duplicate.
- **Rules said:** INV-1295 already settled by BNK-000160; suspected duplicate credit, left unapplied.
- **Considered:** INV-1295, INV-1208, INV-1401, INV-1447, INV-1426, INV-1240, INV-1256, INV-1469, INV-1267, INV-1479, INV-1074, INV-1051
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000329 — ₹10,742.57 · `REQUEST_REMITTANCE`

*2026-08-13 · EXCEPTION · IMPS-923305276913-BhttPl*

A credit of Rs 10,742.57 was received on 2026-08-13 via IMPS (UTR 923305276913) with narration referencing 'BhttPl', which appears to be a truncated reference to Bhatt Polymers & Co. None of the considered invoices from Bhatt Polymers or Bhatt Enterprises match this amount; the closest invoices differ by several thousand rupees.

- **Lead:** —
- **Certainty:** weak -- narration hints at Bhatt Polymers but amount gap is unexplained and no invoice fits.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1331, INV-1482, INV-1209, INV-1277, INV-1024, INV-1471, INV-1400, INV-1077
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000443 — ₹9,340.22 · `REQUEST_REMITTANCE`

*2026-08-04 · EXCEPTION · RTGS AXIS128993395393 REDDYIND*

The bank credit of Rs 9,340.22 on 2026-08-04 (RTGS from AXIS, UTR 128993395393, narration REDDYIND) does not fully match any open invoice. The closest is INV-1180 for Iyer Polymers & Co (Rs 9,379.92), leaving a small unexplained difference of Rs -39.70.

- **Lead:** INV-1180
- **Certainty:** moderate -- amount very close to INV-1180 with only a Rs 39.70 gap, suggesting a partial payment or rounding difference.
- **Rules said:** INV-1454 already settled by BNK-000442; suspected duplicate credit, left unapplied.
- **Considered:** INV-1454, INV-1180, INV-1300, INV-1450, INV-1444, INV-1241, INV-1042, INV-1250, INV-1463, INV-1178, INV-1406, INV-1138
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000220 — ₹9,116.20 · `REQUEST_REMITTANCE`

*2026-07-05 · EXCEPTION · INB/867364005611/PAYMENT*

The bank credit of Rs 9,116.20 on 2026-07-05 (UTR 867364005611) does not exactly match any open invoice. The closest is INV-1471 for Bhatt Enterprises LLP, which is Rs 9,124.77 – a shortfall of Rs 8.57. No other invoice is within a reasonable range.

- **Lead:** INV-1471
- **Certainty:** weak -- amount close to INV-1471 but the Rs 8.57 gap is unexplained; narration gives no counterparty details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1471, INV-1405
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000506 — ₹9,050.88 · `NEEDS_MORE_DATA`

*2026-07-02 · EXCEPTION · INT.PD:959444442469*

The bank credit of Rs 9,050.88 on 2026-07-02 is an interest payment (INT.PD) identified by UTR 959444442469. No invoice in the ledger matches this amount, date, or counterparty, so the transaction cannot be auto‑matched.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest, not an invoice; no candidate invoices exist.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000495 — ₹8,072.62 · `NEEDS_MORE_DATA`

*2026-05-05 · EXCEPTION · REV-325808253619-FAILED TXN*

The bank shows a credit of Rs 8,072.62 on 2026-05-05 with narration 'REV-325808253619-FAILED TXN', indicating a reversal of a failed transaction. No invoices in the ledger match this amount, date, or any identifiable counterparty, so the credit cannot be tied to an outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a reversal but no invoice data exists to confirm purpose.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000492 — ₹6,221.88 · `NEEDS_MORE_DATA`

*2026-07-02 · EXCEPTION · CHARGES GST @18%*

The bank credit of Rs 6,221.88 on 2026-07-02 is labeled as 'CHARGES GST @18%' with UTR 124484500082. No invoice in the ledger matches this amount, date, or any identifiable counterparty, suggesting it is a standalone GST charge or fee that was not tied to a specific sales invoice.

- **Lead:** —
- **Certainty:** weak -- narration indicates a GST charge but no invoice matches the amount or date, so the correct disposition cannot be determined from available data.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000415 — ₹6,167.09 · `CONFIRM_MATCH`

*2026-07-23 · NEEDS_REVIEW · INB/581936496811/PAYMENT*

The bank credit of Rs 6,167.09 on 2026-07-23 (UTR 581936496811) matches invoice INV-1426 for Iyer Infotech except for a Rs 685.23 shortfall, which corresponds to a 10% TDS deduction. The narration contains only a UTR reference and no additional payer details.

- **Lead:** INV-1426
- **Certainty:** moderate -- amount gap exactly equals 10% TDS of the invoice, strongly suggesting TDS deduction.
- **Rules said:** Short of INV-1426 by Rs685.23, which is 10% TDS.
- **Considered:** INV-1426
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000496 — ₹507.66 · `NEEDS_MORE_DATA`

*2026-07-24 · EXCEPTION · NEFT/BoseChe/RETURN*

A Rs 507.66 credit from a NEFT return (UTR 428591404943) dated 2026-07-24 with narration 'NEFT/BoseChe/RETURN' appears to be a refund or reversal, but no invoice in the ledger matches this amount, date, or counterparty.

- **Lead:** —
- **Certainty:** weak -- narration indicates a return/refund but no corresponding invoice found; cannot determine correct handling without additional remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b
