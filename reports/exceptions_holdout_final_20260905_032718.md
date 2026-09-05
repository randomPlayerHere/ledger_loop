# Exception queue — `holdout_final`

101 items · ₹4,939,134.60 unresolved · generated 2026-09-05 03:27

Every note below is written by a language model and is a **suggestion for a reviewer, never a decision**. No note moved money, and no note changed a match: the reconciliation in `reports/eval_*.md` is identical with triage on or off.

## By suggested action

| Action | Items | Value |
|---|---|---|
| REQUEST_REMITTANCE | 38 | ₹2,059,875.63 |
| NEEDS_MORE_DATA | 23 | ₹929,266.56 |
| CONFIRM_MATCH | 14 | ₹896,447.15 |
| CHECK_DUPLICATE | 17 | ₹661,324.53 |
| WRITE_OFF_SMALL | 4 | ₹196,128.93 |
| CHECK_REFUND | 5 | ₹196,091.80 |

## Queue

Ordered by money at stake.

### BNK-000196 — ₹229,368.52 · `REQUEST_REMITTANCE`

*2026-07-21 · EXCEPTION · INB/569545761554/PAYMENT*

The bank credit of Rs 229,368.52 on 2026-07-21 (UTR 569545761554) is Rs 568.70 short of the open invoice INV-1200 for Bose Chemicals Pvt Ltd (gross Rs 229,937.22, issued 2026-07-04). The narration only contains a generic payment reference, so the shortfall is unexplained.

- **Lead:** INV-1200
- **Certainty:** weak -- amount close but the exact shortfall is not explained by any visible fee or discount.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1200
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000007 — ₹225,749.48 · `NEEDS_MORE_DATA`

*2026-07-15 · EXCEPTION · NEFT-IYERCHE*

The credit of Rs 225,749.48 on 2026-07-15 comes from a NEFT to Iyer Chemicals (narration 'NEFT-IYERCHE'), but none of the open invoices from Iyer Chemicals or related parties match this exact amount; the closest is INV-1095 for Rs 130,020.02, leaving a large unexplained gap.

- **Lead:** —
- **Certainty:** weak -- narration points to Iyer Chemicals but no single invoice fits the amount; could be a batch payment needing remittance advice.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1095, INV-1395, INV-1023, INV-1272, INV-1158, INV-1280, INV-1054, INV-1239, INV-1345, INV-1129, INV-1160, INV-1295
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000128 — ₹164,039.64 · `CONFIRM_MATCH`

*2026-08-01 · NEEDS_REVIEW · NEFT-ChattExp*

The credit of Rs 164,039.64 matches invoice INV-1122 (Chatterjee Exports) after deducting 10% TDS (Rs 18,226.63), leaving a net amount that equals the transaction. The narration 'NEFT-ChattExp' points to the same counterparty.

- **Lead:** INV-1122
- **Certainty:** strong -- amount gap exactly equals 10% TDS on INV-1122 and narration aligns with Chatterjee Exports.
- **Rules said:** Short of INV-1122 by Rs18226.63, which is 10% TDS.
- **Considered:** INV-1122, INV-1219, INV-1407, INV-1376, INV-1134, INV-1187, INV-1305, INV-1488, INV-1462, INV-1481, INV-1154, INV-1276
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000095 — ₹129,764.19 · `REQUEST_REMITTANCE`

*2026-07-05 · EXCEPTION · INB/628961692445/PAYMENT*

The bank credit of Rs 129,764.19 on 2026-07-05 (UTR 628961692445) does not exactly match any open invoice; the closest is INV-1095 for Iyer Chemicals, which is Rs 255.83 higher than the payment. The narration only contains a generic payment reference with no counterparty name, so the shortfall cannot be explained by discount, tax, or fees visible in the data.

- **Lead:** INV-1095
- **Certainty:** weak -- amount gap is small and could be bank charges, but narration gives no clue to confirm.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1095, INV-1088, INV-1237
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000339 — ₹125,725.43 · `CONFIRM_MATCH`

*2026-07-20 · NEEDS_REVIEW · INB/310432268977/PAYMENT*

The credit of Rs 125,725.43 matches invoice INV-1346 (gross Rs 139,694.92) minus a Rs 13,969.49 TDS deduction, which explains the shortfall. The narration and UTR do not reveal a counterparty, but the amount gap aligns with a 10% TDS withholding.

- **Lead:** INV-1346
- **Certainty:** moderate -- amount gap equals 10% TDS of the invoice, making the match plausible.
- **Rules said:** Short of INV-1346 by Rs13969.49, which is 10% TDS.
- **Considered:** INV-1346
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000303 — ₹112,168.49 · `CHECK_DUPLICATE`

*2026-06-11 · EXCEPTION · RTGS SBIN284849359148 DESHMPAC*

The credit of Rs 112,168.49 on 2026-06-11 via RTGS (UTR 284849359148) from DESHMPAC matches the exact amount of invoice INV-1306 issued to Deshmukh Packaging Ltd on 2026-06-08, but the rule engine flagged it as a suspected duplicate because INV-1306 was already settled by transaction BNK-000302.

- **Lead:** INV-1306
- **Certainty:** strong -- amount and counterparty (Deshmukh Packaging) match exactly; only uncertainty is whether BNK-000302 truly settled the invoice.
- **Rules said:** INV-1306 already settled by BNK-000302; suspected duplicate credit, left unapplied.
- **Considered:** INV-1306, INV-1413, INV-1447, INV-1189, INV-1127, INV-1237, INV-1139, INV-1452, INV-1483, INV-1438, INV-1014, INV-1300
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000242 — ₹110,725.48 · `REQUEST_REMITTANCE`

*2026-08-04 · EXCEPTION · UPI/452442243998/kulkasol@okicicbank*

Credit of Rs 110,725.48 received on 2026-08-04 from UPI ID kulkasol@okicicbank (UTR 452442243998). The amount does not exactly match any open invoice; the closest is INV-1246 for Kulkarni Solutions LLP (Rs 108,409.43), leaving an unexplained gap of Rs 2,316.05.

- **Lead:** INV-1246
- **Certainty:** weak -- amount close to INV-1246 but the residual difference is not explained by any visible tax or discount.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1246, INV-1373, INV-1319, INV-1036, INV-1433, INV-1471, INV-1173, INV-1003
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000187 — ₹108,793.22 · `REQUEST_REMITTANCE`

*2026-06-18 · EXCEPTION · RTGS HDFC917584674648 DSHMSL*

Credit of Rs 108,793.22 received via RTGS from HDFC (UTR 917584674648) narrated as 'DSHMSL' on 2026-06-18. The amount does not exactly match any open invoice; the closest is INV-1189 (Deshmukh Solutions Pvt Ltd, Rs 106,178.98) leaving an unexplained gap of Rs 2,614.24.

- **Lead:** INV-1189
- **Certainty:** weak -- narration hints at Deshmukh but amount gap not explained by TDS or other known deductions.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1306, INV-1447, INV-1127, INV-1189, INV-1357, INV-1237, INV-1014, INV-1497, INV-1139, INV-1452, INV-1438, INV-1156
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000282 — ₹100,565.26 · `REQUEST_REMITTANCE`

*2026-05-14 · EXCEPTION · BY TRANSFER-188163794590-*

The bank credit of Rs 100,565.26 on 2026‑05‑14 (UTR 188163794590) does not match the only candidate invoice INV‑1287 for Rs 100,773.75; the shortfall of Rs 208.49 cannot be explained by the noted 10% TDS or any other obvious adjustment.

- **Lead:** —
- **Certainty:** weak -- amount gap unexplained and narration provides no counterparty details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1287
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000138 — ₹92,787.85 · `CONFIRM_MATCH`

*2026-08-15 · NEEDS_REVIEW · RTGS KKBK355297515721 CHATTLOG*

The credit of Rs 92,787.85 matches the gross amount of INV-1134 (Rs 103,097.61) less a 10% TDS deduction of Rs 10,309.76, leaving exactly the settled amount. The narration references an RTGS transfer with UTR 355297515721 and no other party is named.

- **Lead:** INV-1134
- **Certainty:** strong -- amount gap equals 10% TDS on INV-1134, narration consistent with a payment to Chatterjee Logistics.
- **Rules said:** Short of INV-1134 by Rs10309.76, which is 10% TDS.
- **Considered:** INV-1134, INV-1061, INV-1461, INV-1376, INV-1219, INV-1407, INV-1297, INV-1475, INV-1259, INV-1013, INV-1073, INV-1498
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000464 — ₹92,151.42 · `CHECK_DUPLICATE`

*2026-07-12 · EXCEPTION · BY TRANSFER-375847496530-*

Bank credit of Rs 92,151.42 on 2026-07-12 matches the exact amount of open invoice INV-1487 (Bhatt Exports Ltd). The rule engine flagged it as a suspected duplicate because INV-1487 was already settled by another credit (BNK-000466), leaving this credit unapplied.

- **Lead:** INV-1487
- **Certainty:** moderate -- amount matches exactly but rule indicates possible duplicate settlement
- **Rules said:** INV-1487 already settled by BNK-000466; suspected duplicate credit, left unapplied.
- **Considered:** INV-1487, INV-1153, INV-1439
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000060 — ₹91,587.70 · `REQUEST_REMITTANCE`

*2026-07-02 · EXCEPTION · BY TRANSFER-202345912466-*

A credit of Rs 91,587.70 arrived on 2026-07-02 from an unidentified transfer (UTR 202345912466). The amount is close to, but not equal to, two open invoices (INV-1073 for Rs 91,898.70 and INV-1053 for Rs 92,005.96), leaving unexplained gaps of Rs -311.00 and Rs -418.26 respectively. No counterparty name is given in the narration, so the payment cannot be confidently linked to any specific invoice.

- **Lead:** INV-1073
- **Certainty:** weak -- amount is near INV-1073 but the Rs 311 shortfall lacks explanation and no payer details are provided.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1073, INV-1053
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000502 — ₹89,524.10 · `CHECK_REFUND`

*2026-05-18 · EXCEPTION · NEFT/BHATTSTE/RETURN*

The bank shows a credit of Rs 89,524.10 from Bhatt Steels labelled as a return (NEFT/BHATTSTE/RETURN) on 2026‑05‑18. None of the open invoices from Bhatt Steels (or related parties) have an amount close to this figure; the closest is INV‑1017 at Rs 45,712.34, leaving a large unexplained gap.

- **Lead:** —
- **Certainty:** moderate – narration clearly indicates a return/refund from Bhatt Steels, but no invoice matches the amount, so the exact source cannot be confirmed from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1017, INV-1089, INV-1066, INV-1249, INV-1432, INV-1146, INV-1496, INV-1380, INV-1392, INV-1391, INV-1215, INV-1032
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000458 — ₹88,568.81 · `CONFIRM_MATCH`

*2026-08-03 · NEEDS_REVIEW · INB/560536851089/PAYMENT*

The bank credit of Rs 88,568.81 on 2026-08-03 (UTR 560536851089) matches invoice INV-1479 for Deshmukh Packaging Ltd after applying the 2% TDS deduction (Rs 1,807.53) from the invoice gross of Rs 90,376.34. The narration only contains a payment reference, no counterparty name.

- **Lead:** INV-1479
- **Certainty:** moderate -- amount gap exactly equals 2% TDS on the invoice, narration lacks details but UTR aligns.
- **Rules said:** Short of INV-1479 by Rs1807.53, which is 2% TDS.
- **Considered:** INV-1479
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000500 — ₹87,208.44 · `NEEDS_MORE_DATA`

*2026-05-22 · EXCEPTION · CHARGES GST @18%*

The bank credit of Rs 87,208.44 on 2026-05-22 is labelled as 'CHARGES GST @18%' with UTR 919281931856, indicating a GST charge rather than a payment against an invoice. No invoices in the ledger match this amount, date, or any identifiable counterparty, so the transaction cannot be resolved automatically.

- **Lead:** —
- **Certainty:** weak -- narration points to a GST charge but no invoice data is available to confirm or refute.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000115 — ₹84,955.32 · `CHECK_DUPLICATE`

*2026-08-12 · EXCEPTION · CMS/1107/AGARWENT*

The credit of Rs 84,955.32 on 2026-08-12 matches the exact gross amount of invoice INV-1107 (Agarwal Enterprises LLP). The rule engine flagged it as a suspected duplicate because INV-1107 was already settled by another credit (BNK-000496), leaving this amount unapplied.

- **Lead:** INV-1107
- **Certainty:** strong -- amount matches invoice exactly and narration references the same invoice code.
- **Rules said:** INV-1107 already settled by BNK-000496; suspected duplicate credit, left unapplied.
- **Considered:** INV-1107, INV-1132, INV-1355, INV-1192, INV-1163, INV-1254, INV-1230, INV-1402, INV-1048, INV-1157, INV-1331, INV-1253
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000475 — ₹82,081.53 · `REQUEST_REMITTANCE`

*2026-07-10 · EXCEPTION · INT.PD:140655310597*

Bank credit of Rs 82,081.53 on 2026-07-10 (UTR 140655310597) does not fully match the open invoice INV-1102 for Agarwal Enterprises LLP (gross Rs 82,321.05), leaving a shortfall of Rs 239.52. The narration only contains the UTR, giving no counterparty or payment details.

- **Lead:** INV-1102
- **Certainty:** weak -- amount close but unexplained gap; narration lacks details to confirm.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1102
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000314 — ₹76,920.21 · `REQUEST_REMITTANCE`

*2026-07-04 · EXCEPTION · INB/579841829216/PAYMENT*

The bank credit of Rs 76,920.21 on 2026-07-04 (UTR 579841829216) is Rs 377.98 short of the open invoice INV-1341 from Bose Chemicals Pvt Ltd (gross Rs 77,298.19, due 2026-07-15). The narration only shows a generic INB payment reference, giving no clue about the shortfall, which could be TDS, bank charges, or a partial payment.

- **Lead:** INV-1341
- **Certainty:** weak -- amount gap unexplained, narration lacks details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1341
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000496 — ₹76,459.39 · `CONFIRM_MATCH`

*2026-06-26 · NEEDS_REVIEW · INT.PD:130389324016*

The bank credit of Rs 76,459.39 on 2026-06-26 (UTR 130389324016) matches invoice INV-1107 for Agarwal Enterprises LLP after a 10% TDS deduction of Rs 8,495.93 from the gross invoice amount of Rs 84,955.32. The narration only contains the UTR, with no additional party details.

- **Lead:** INV-1107
- **Certainty:** strong -- amount gap equals exactly 10% TDS, consistent with typical tax deduction.
- **Rules said:** Short of INV-1107 by Rs8495.93, which is 10% TDS.
- **Considered:** INV-1107
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000480 — ₹76,337.33 · `NEEDS_MORE_DATA`

*2026-06-07 · EXCEPTION · IMPS-914261596007-UNKNOWN REMITTER*

An IMPS credit of Rs 76,337.33 from an unknown remitter on 2026-06-07 could not be matched to any invoice; the ledger contains no candidate with a similar amount, date, or counterparty.

- **Lead:** —
- **Certainty:** weak -- narration provides no counterparty and no invoice matches the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000492 — ₹71,504.23 · `NEEDS_MORE_DATA`

*2026-06-18 · EXCEPTION · CHARGES GST @18%*

The bank credit of Rs 71,504.23 is labelled as 'CHARGES GST @18%', indicating it is a GST charge rather than payment against an invoice. Neither of the two candidate invoices matches the amount closely enough (differences of Rs -1.81 and Rs -159.03) to be explained by typical rounding or tax adjustments.

- **Lead:** —
- **Certainty:** weak -- narration points to a GST charge, and no invoice amount aligns within a reasonable tolerance.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1278, INV-1045
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000365 — ₹70,266.69 · `REQUEST_REMITTANCE`

*2026-08-07 · EXCEPTION · BY TRANSFER-226202640342-*

The bank credit of Rs 70,266.69 on 2026-08-07 (UTR 226202640342) is Rs 90.51 less than the open invoice INV-1373 for Kulkarni Industries LLP (gross Rs 70,357.20, issued 2026-07-26). The narration only shows a transfer reference, so the shortfall is unexplained but could be a bank fee, rounding, or partial payment.

- **Lead:** INV-1373
- **Certainty:** weak -- amount close but the exact Rs 90.51 gap lacks supporting evidence
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1373
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000025 — ₹70,215.43 · `WRITE_OFF_SMALL`

*2026-06-03 · EXCEPTION · IMPS-285753093615-Mlhnt*

The bank credit of Rs 70,215.43 on 2026-06-03 (IMPS transfer UTR 285753093615) is close to invoice INV-1274 from Deshmukh Packaging Ltd (gross Rs 70,394.16) but falls short by Rs 178.73. No counterparty name appears in the narration, and the amount gap cannot be explained by any rule.

- **Lead:** INV-1274
- **Certainty:** weak -- amount close but unexplained difference; narration lacks payer details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1274
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000482 — ₹70,128.69 · `REQUEST_REMITTANCE`

*2026-05-17 · EXCEPTION · REV-310166631363-FAILED TXN*

The bank credit of Rs 70,128.69 on 2026-05-17 (UTR 310166631363) is labelled as a failed transaction (REV-310166631363-FAILED TXN). The only invoice considered, INV-1274 for Deshmukh Packaging Ltd, is for Rs 70,394.16, leaving an unexplained shortfall of Rs 265.47. No other counterparty or invoice matches this amount.

- **Lead:** INV-1274
- **Certainty:** weak -- invoice name present but the amount gap of Rs 265.47 cannot be explained by the data given.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1274
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000503 — ₹66,755.24 · `CHECK_REFUND`

*2026-05-31 · EXCEPTION · NEFT/IyrPc/RETURN*

A NEFT return credit of Rs 66,755.24 was posted on 2026-05-31 with narration 'NEFT/IyrPc/RETURN' and UTR 236943911266. No invoice in the ledger matches this amount, date, or counterparty, suggesting it is a refund or reversal rather than a payment against an outstanding invoice.

- **Lead:** —
- **Certainty:** weak -- narration indicates a return but no invoice matches the amount or details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000488 — ₹64,728.26 · `NEEDS_MORE_DATA`

*2026-05-03 · EXCEPTION · INT.PD:714091211050*

The bank credit of Rs 64,728.26 on 2026-05-03 is labelled as an interest payment (INT.PD) with UTR 714091211050. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the transaction cannot be linked to any known receivable.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest but no matching invoice exists; cannot resolve without additional remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000325 — ₹64,144.22 · `CHECK_DUPLICATE`

*2026-07-17 · EXCEPTION · IMPS-296917403674-AGARWTRA*

Credit of Rs 64,144.22 on 2026-07-17 from IMPS transaction (UTR 296917403674) narrated as AGARWTRA matches the exact gross amount of INV-1331 (Agarwal Traders Pvt Ltd). The rule engine flagged it as a suspected duplicate because INV-1331 was already settled by BNK-000324.

- **Lead:** INV-1331
- **Certainty:** strong -- amount matches exactly, narration points to Agarwal Traders, but already marked as settled/duplicate.
- **Rules said:** INV-1331 already settled by BNK-000324; suspected duplicate credit, left unapplied.
- **Considered:** INV-1331, INV-1157, INV-1402, INV-1163, INV-1192, INV-1230, INV-1094, INV-1069, INV-1355, INV-1275, INV-1273, INV-1361
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000148 — ₹63,693.09 · `CONFIRM_MATCH`

*2026-06-02 · NEEDS_REVIEW · NEFT/ChattLog/INV-1146/AXIS*

The credit of Rs 63,693.09 matches invoice INV-1146 (Chatterjee Logistics) less a Rs 1,299.86 TDS deduction (2%), which aligns with the narration referencing INV-1146 and the UTR. No other invoice in the list fits the amount within a reasonable TDS range.

- **Lead:** INV-1146
- **Certainty:** strong -- amount gap equals exactly 2% TDS on INV-1146, narration cites the same invoice.
- **Rules said:** Short of INV-1146 by Rs1299.86, which is 2% TDS.
- **Considered:** INV-1146, INV-1475, INV-1432, INV-1423, INV-1245, INV-1314, INV-1473, INV-1380, INV-1209, INV-1242, INV-1248, INV-1391
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000225 — ₹63,436.63 · `REQUEST_REMITTANCE`

*2026-08-07 · EXCEPTION · UPI/818008975287/sinhatex@oksbinbank*

Credit of Rs 63,436.63 received on 2026-08-07 from UPI reference sinhatex@oksbinbank (UTR 818008975287). The amount is close to invoice INV-1227 (Sinha Textiles Pvt Ltd, Rs 63,963.12) but is Rs 526.49 lower, and no deterministic rule could explain this gap.

- **Lead:** INV-1227
- **Certainty:** weak -- amount near INV-1227 but unexplained shortfall; no other invoice matches closely.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1227, INV-1252, INV-1275, INV-1408, INV-1072, INV-1067, INV-1451
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000456 — ₹61,347.69 · `CHECK_DUPLICATE`

*2026-07-07 · EXCEPTION · NEFT/CHATTTEX/1477/SBIN*

A credit of Rs 61,347.69 arrived on 2026-07-07 from NEFT/CHATTTEX/1477/SBIN (UTR 196863233843). The narration points to Chatterjee Textiles, and the amount is almost identical to INV-1380 (Chatterjee Steels & Co) differing by only Rs 1.83, while the rule engine flagged it as a suspected duplicate of the already‑settled INV-1217.

- **Lead:** INV-1380
- **Certainty:** moderate – amount gap tiny and counterparty name matches narration, but duplicate flag suggests it may be an unapplied credit rather than a new invoice.
- **Rules said:** INV-1217 already settled by BNK-000213; suspected duplicate credit, left unapplied.
- **Considered:** INV-1477, INV-1489, INV-1380, INV-1304, INV-1114, INV-1498, INV-1186, INV-1252, INV-1259, INV-1039, INV-1317, INV-1217
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000392 — ₹61,045.96 · `REQUEST_REMITTANCE`

*2026-07-30 · EXCEPTION · BY TRANSFER-487995468351-*

The bank credit of Rs 61,045.96 on 2026-07-30 (UTR 487995468351) does not exactly match any open invoice; it is Rs 138.68 short of INV-1173 (Kulkarni Industries LLP) and Rs 303.56 short of INV-1380 (Chatterjee Steels & Co). The narration only shows a transfer reference, giving no counterparty clue.

- **Lead:** INV-1173
- **Certainty:** weak -- amount closest to INV-1173 but the gap is unexplained and no party is named in the narration.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1173, INV-1380
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000474 — ₹60,895.94 · `WRITE_OFF_SMALL`

*2026-08-01 · EXCEPTION · CMS/INV-1498/CHATTSTE*

The credit of Rs 60,895.94 on 2026-08-01 (UTR 741684686230, narration CMS/INV-1498/CHATTSTE) closely matches invoice INV-1498 for Chatterjee Steels & Co, which is for Rs 60,949.32 and remains open. The amount is Rs 53.38 lower than the invoice, a small gap that could be due to rounding, bank charges, or a minor TDS adjustment.

- **Lead:** INV-1498
- **Certainty:** moderate -- amount difference is small and narration references the same invoice number, but no explicit remittance details are provided.
- **Rules said:** INV-1463 already settled by BNK-000009; suspected duplicate credit, left unapplied.
- **Considered:** INV-1498, INV-1316, INV-1304, INV-1039, INV-1305, INV-1173, INV-1464, INV-1134, INV-1477, INV-1114, INV-1191, INV-1219
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000479 — ₹57,716.89 · `REQUEST_REMITTANCE`

*2026-05-06 · EXCEPTION · IMPS-424311269947-UNKNOWN REMITTER*

A credit of Rs 57,716.89 arrived on 2026-05-06 via IMPS from an unknown remitter (UTR 424311269947). No invoice in the ledger matches this amount, date, or counterparty, so the payment cannot be linked to any known receivable.

- **Lead:** —
- **Certainty:** weak -- narration provides no identifiable party and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000371 — ₹55,214.57 · `CONFIRM_MATCH`

*2026-05-29 · NEEDS_REVIEW · NEFT/CHATTSTE/INV-1380/ICIC*

The credit of Rs 55,214.57 matches invoice INV-1380 (Chatterjee Steels & Co) after deducting 10% TDS (Rs 6,134.95) from its gross amount of Rs 61,349.52. The narration references INV-1380 and the UTR corresponds to a NEFT payment.

- **Lead:** INV-1380
- **Certainty:** strong -- amount gap equals exactly 10% TDS on INV-1380, narration names the invoice.
- **Rules said:** Short of INV-1380 by Rs6134.95, which is 10% TDS.
- **Considered:** INV-1380, INV-1017, INV-1066, INV-1314, INV-1223, INV-1473, INV-1209, INV-1248, INV-1146, INV-1391, INV-1242, INV-1080
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000473 — ₹52,884.49 · `REQUEST_REMITTANCE`

*2026-08-10 · EXCEPTION · UPI/141189214352/deshmpac@okpunbbank*

The bank credit of Rs 52,884.49 on 2026-08-10 from UPI reference deshmpac@okpunbbank closely matches invoice INV-1378 (Deshmukh Motors & Co) for Rs 52,713.87, leaving a small unexplained difference of Rs 170.62. No other candidate invoice is within a reasonable range.

- **Lead:** INV-1378
- **Certainty:** moderate -- amount gap is small and counterparty name aligns, but the exact reason for the Rs 170.62 difference is not evident from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1495, INV-1167, INV-1182, INV-1364, INV-1450, INV-1404, INV-1212, INV-1479, INV-1235, INV-1022, INV-1281, INV-1378
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000369 — ₹51,659.59 · `CONFIRM_MATCH`

*2026-07-08 · NEEDS_REVIEW · BY TRANSFER-265928946102-*

The credit of Rs 51,659.59 on 2026-07-08 matches invoice INV-1378 (gross Rs 52,713.87) less a Rs 1,054.28 TDS deduction (2%). The narration shows a transfer with UTR 265928946102 and no counterparty name, but the amount gap exactly equals the expected TDS.

- **Lead:** INV-1378
- **Certainty:** strong -- amount difference equals 2% TDS on the invoice, narration indicates a transfer consistent with payment.
- **Rules said:** Short of INV-1378 by Rs1054.28, which is 2% TDS.
- **Considered:** INV-1378
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000269 — ₹49,637.41 · `REQUEST_REMITTANCE`

*2026-07-13 · EXCEPTION · RTGS PUNB845336214392 AGARWENT*

Credit of Rs 49,637.41 from Agarwal Enterprises (UTR 845336214392) on 2026-07-13. The amount is Rs 149.35 higher than invoice INV-1273 (Rs 49,488.06) and does not match any other invoice closely; the small difference could be bank charges or rounding.

- **Lead:** INV-1273
- **Certainty:** weak -- amount close to INV-1273 but unexplained Rs 149.35 gap
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1273, INV-1099, INV-1094, INV-1069, INV-1331, INV-1157, INV-1230, INV-1402, INV-1350, INV-1163, INV-1264, INV-1275
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000221 — ₹49,223.99 · `REQUEST_REMITTANCE`

*2026-05-31 · EXCEPTION · RTGS UTIB791959279048 CHATTTEX*

The bank credit of Rs 49,223.99 on 2026-05-31 (UTR 791959279048, narration RTGS UTIB791959279048 CHATTTEX) does not exactly match any invoice; the closest is INV-1473 for Chatterjee Logistics at Rs 49,014.98, leaving an unexplained difference of Rs 209.01.

- **Lead:** INV-1473
- **Certainty:** weak -- amount gap small but unexplained; narration only gives a generic counterparty hint.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1473, INV-1209, INV-1314, INV-1223, INV-1248, INV-1380, INV-1242, INV-1146, INV-1391, INV-1080, INV-1098, INV-1085
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000499 — ₹48,568.55 · `REQUEST_REMITTANCE`

*2026-06-18 · EXCEPTION · INT.PD:314585758421*

Bank credit of Rs 48,568.55 on 2026-06-18 with narration INT.PD:314585758421 (UTR same) does not match any invoice exactly; the closest invoice INV-1025 is Rs 51.02 higher and INV-1210 is Rs 170.88 higher, with no clear counterparty name in the narration.

- **Lead:** —
- **Certainty:** weak -- narration gives no party name and amount gaps are unexplained
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1025, INV-1210
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000486 — ₹47,686.88 · `NEEDS_MORE_DATA`

*2026-07-16 · EXCEPTION · INT.PD:237000908213*

A credit of Rs 47,686.88 was posted on 2026-07-16 with narration 'INT.PD:237000908213' (UTR 237000908213). No invoice in the ledger matches this amount, date, or counterparty, suggesting it may be an interest payment, bank charge, or other non‑invoice credit.

- **Lead:** —
- **Certainty:** low -- narration gives no clear counterparty and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000165 — ₹47,569.56 · `CONFIRM_MATCH`

*2026-07-05 · NEEDS_REVIEW · INB/415387945583/PAYMENT*

The bank credit of Rs 47,569.56 on 2026-07-05 matches invoice INV-1168 (gross Rs 52,855.07) less a Rs 5,285.51 TDS deduction, which is exactly 10% of the invoice amount. The narration only contains a UTR reference and does not name the payer.

- **Lead:** INV-1168
- **Certainty:** high -- amount gap equals expected 10% TDS on INV-1168
- **Rules said:** Short of INV-1168 by Rs5285.51, which is 10% TDS.
- **Considered:** INV-1168
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000102 — ₹47,517.65 · `REQUEST_REMITTANCE`

*2026-06-01 · EXCEPTION · UPI/427595236527/iyerche@okpunbbank*

Credit of Rs 47,517.65 from UPI transaction with counterparty iyerche@okpunbbank on 2026-06-01. The amount is closest to invoice INV-1365 (Iyer Polymers LLP, Rs 47,271.14) leaving an unexplained difference of Rs 246.51, which could be bank charges or a small fee.

- **Lead:** INV-1365
- **Certainty:** moderate -- amount gap is small (Rs 246.51) and counterparty name matches, but no rule explains the residual.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1096, INV-1054, INV-1041, INV-1345, INV-1136, INV-1149, INV-1293, INV-1081, INV-1365, INV-1201, INV-1271, INV-1126
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000481 — ₹46,002.35 · `REQUEST_REMITTANCE`

*2026-07-25 · EXCEPTION · NEFT/BHATTTEX/RETURN*

The bank credit of Rs 46,002.35 on 2026-07-25 (UTR 916605375424, narration NEFT/BHATTTEX/RETURN) is very close to invoice INV-1099 from Agarwal Exports Pvt Ltd (gross Rs 46,043.95), differing by only Rs 41.60. No other candidate invoice matches the amount within a reasonable tolerance, and the narration does not reveal a clear counterparty beyond the generic 'BHATTTEX' reference.

- **Lead:** INV-1099
- **Certainty:** moderate -- amount gap is small (Rs 41.60) and could be due to rounding, bank charges, or minor TDS adjustment, but the narration does not explicitly confirm the match.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1311, INV-1099, INV-1481, INV-1159, INV-1316, INV-1217, INV-1461, INV-1487, INV-1464, INV-1088, INV-1343, INV-1191
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000452 — ₹44,113.48 · `REQUEST_REMITTANCE`

*2026-06-14 · EXCEPTION · BY TRANSFER-694741487011-*

The bank credit of Rs 44,113.48 on 2026-06-14 (UTR 694741487011) does not exactly match any open invoice. The closest is INV-1085 for Chatterjee Textiles (Rs 44,278.00), leaving a small unexplained difference of Rs -164.52, which could be a bank charge or rounding.

- **Lead:** INV-1085
- **Certainty:** moderate -- amount close to INV-1085 but gap remains unexplained
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1473, INV-1085
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000427 — ₹43,996.01 · `REQUEST_REMITTANCE`

*2026-05-13 · EXCEPTION · INB/654561348384/PAYMENT*

A credit of Rs 43,996.01 arrived on 2026-05-13 with UTR 654561348384 and narration 'INB/654561348384/PAYMENT'. The only candidate invoice is INV-1440 for Rs 44,080.94, leaving an unexplained shortfall of Rs 84.93; no other invoice matches the amount or counterparty.

- **Lead:** INV-1440
- **Certainty:** weak -- amount gap of Rs 84.93 unexplained, narration gives no party name.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1440
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000117 — ₹42,853.54 · `REQUEST_REMITTANCE`

*2026-07-06 · EXCEPTION · INB/715742893632/PAYMENT*

The bank credit of Rs 42,853.54 on 2026-07-06 (UTR 715742893632) does not exactly match any invoice; the closest candidate is INV-1197 for Pillai Traders Ltd, which is Rs 109.75 higher than the payment. The narration only contains a generic UTR reference with no party name, so the shortfall cannot be explained by discount, tax, or fees visible in the data.

- **Lead:** INV-1197
- **Certainty:** weak -- amount close but unexplained gap; narration lacks counterparty details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1197
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000483 — ₹42,552.69 · `NEEDS_MORE_DATA`

*2026-05-06 · EXCEPTION · REV-653294527815-FAILED TXN*

The bank credit of Rs 42,552.69 on 2026-05-06 is labelled as a failed transaction (UTR 653294527815) with narration 'REV-653294527815-FAILED TXN'. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates a failed/reversal transaction but no invoice data is available to confirm purpose.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000493 — ₹42,184.69 · `NEEDS_MORE_DATA`

*2026-05-21 · EXCEPTION · CHARGES GST @18%*

The bank shows a credit of Rs 86,928.45 on 2026-05-27 with narration 'REV-690921879434-FAILED TXN' and UTR 690921879434, indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be linked to any outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a failed‑transaction reversal but no invoice data exists to confirm.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000171 — ₹40,844.84 · `CONFIRM_MATCH`

*2026-07-11 · EXCEPTION · NEFT/VENKAPAC/1174/SBIN*

The credit of Rs 40,844.84 matches invoice INV-1174 (Venkat Packaging & Co) for Rs 45,383.16 less a 10% TDS deduction, which explains the exact difference. The narration references NEFT/VENKAPAC/1174, aligning with the invoice number.

- **Lead:** INV-1174
- **Certainty:** strong -- amount fits invoice after 10% TDS, narration includes invoice number.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1174, INV-1363, INV-1252, INV-1072, INV-1196, INV-1067, INV-1195, INV-1303, INV-1084, INV-1064, INV-1262, INV-1110
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000158 — ₹40,097.07 · `CHECK_DUPLICATE`

*2026-06-27 · EXCEPTION · NEFT/BhattTex/INV-1159/HDFC*

A credit of Rs 40,097.07 was received from BhattTex with narration referencing INV‑1159, but that invoice was already settled by transaction BNK‑000105. No open invoice matches this amount within a reasonable tolerance, suggesting the credit may be a duplicate or mis‑applied payment.

- **Lead:** —
- **Certainty:** weak -- narration points to an already‑settled invoice and no open invoice fits the amount closely.
- **Rules said:** INV-1159 already settled by BNK-000105; suspected duplicate credit, left unapplied.
- **Considered:** INV-1159, INV-1249, INV-1329, INV-1343, INV-1487, INV-1088, INV-1084, INV-1013, INV-1108, INV-1490, INV-1324, INV-1191
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000122 — ₹39,370.57 · `NEEDS_MORE_DATA`

*2026-08-11 · EXCEPTION · UPI/653970158109/chattexp@okhdfcbank*

The bank credit of Rs 39,370.57 on 2026-08-11 (UPI reference chattexp@okhdfcbank) does not exactly match any open invoice. The closest amounts are INV-1060 (Rs 38,589.60, difference +Rs 780.97) and INV-1004 (Rs 38,364.98, difference +Rs 1,005.59), but none of the considered invoices explain the exact figure after typical TDS or other adjustments.

- **Lead:** —
- **Certainty:** weak -- no invoice matches the amount; only approximate near‑matches exist without clear justification.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1305, INV-1154, INV-1060, INV-1481, INV-1039, INV-1498, INV-1268, INV-1302, INV-1304, INV-1134, INV-1186, INV-1004
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000345 — ₹38,507.71 · `REQUEST_REMITTANCE`

*2026-07-04 · EXCEPTION · INB/251117107678/PAYMENT*

The bank credit of Rs 38,507.71 on 2026-07-04 (UTR 251117107678) does not match any invoice exactly; the closest candidate, INV-1060 for Chatterjee Textiles, is Rs 81.89 higher than the received amount. The narration only contains a generic payment reference with no counterparty name, so the shortfall cannot be explained by tax, discount, or fees visible in the data.

- **Lead:** INV-1060
- **Certainty:** weak -- amount gap is small but unexplained; narration gives no party details to confirm the match.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1060
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000192 — ₹37,191.74 · `CHECK_DUPLICATE`

*2026-07-21 · EXCEPTION · RTGS YESB226983628581 VENKAPAC*

A credit of Rs 37,191.74 arrived on 2026-07-21 from RTGS YESB226983628581 VENKAPAC. The amount exactly matches the gross of INV-1195 (Venkat Packaging & Co), but the rule engine notes that INV-1195 was already settled by the prior transaction BNK-000191, suggesting this credit is a duplicate or unapplied payment.

- **Lead:** INV-1195
- **Certainty:** moderate -- amount matches INV-1195 exactly and narration points to Venkat Packaging, but the invoice is already marked settled, so the credit is likely a duplicate.
- **Rules said:** INV-1195 already settled by BNK-000191; suspected duplicate credit, left unapplied.
- **Considered:** INV-1195, INV-1379, INV-1485, INV-1196, INV-1024, INV-1262, INV-1133, INV-1292, INV-1303, INV-1174, INV-1084, INV-1064
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000193 — ₹37,163.30 · `WRITE_OFF_SMALL`

*2026-07-31 · EXCEPTION · NEFT-VENKAPOL*

The credit of Rs 37,163.30 on 2026‑07‑31 from NEFT‑VENKAPOL closely matches invoice INV‑1195 (Venkat Packaging & Co) for Rs 37,191.74, leaving a small unexplained gap of Rs ‑28.44. No other candidate invoice is within a reasonable range.

- **Lead:** INV-1195
- **Certainty:** moderate – amount difference is tiny and could be rounding/TDS, but no explicit remittance advice is present.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1195, INV-1196, INV-1379, INV-1292, INV-1485, INV-1024, INV-1133, INV-1042, INV-1262, INV-1005, INV-1359, INV-1303
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000489 — ₹37,054.82 · `REQUEST_REMITTANCE`

*2026-05-08 · EXCEPTION · NEFT/CHATTTEX/RETURN*

A credit of Rs 37,054.82 arrived on 2026‑05‑08 with narration ‘NEFT/CHATTTEX/RETURN’, indicating a return or refund from Chatterjee Textiles. None of the open invoices from that party match this amount; the closest is INV‑1085 (Rs 44,278.00), which is Rs 7,223.18 higher.

- **Lead:** —
- **Certainty:** weak -- narration points to Chatterjee Textiles but no invoice amount fits the credit.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1085, INV-1080, INV-1077, INV-1391, INV-1146, INV-1075, INV-1415, INV-1164, INV-1019, INV-1419, INV-1496, INV-1249
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000478 — ₹36,458.48 · `NEEDS_MORE_DATA`

*2026-07-08 · EXCEPTION · IMPS-133616546492-UNKNOWN REMITTER*

A credit of Rs 36,458.48 arrived on 2026-07-08 via IMPS from an unknown remitter (UTR 133616546492). No invoice in the ledger matches this amount, date, or counterparty, so the transaction remains unresolved.

- **Lead:** —
- **Certainty:** low -- narration gives no counterparty and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000201 — ₹34,838.57 · `CHECK_DUPLICATE`

*2026-06-15 · EXCEPTION · NEFT-RDDYTX*

The credit of Rs 34,838.57 on 2026-06-15 (UTR 446329926627, narration NEFT-RDDYTX) exactly matches the gross amount of invoice INV-1205 from Reddy Textiles, but the rule engine notes that INV-1205 was already settled by transaction BNK-000200 and flags this as a suspected duplicate credit.

- **Lead:** INV-1205
- **Certainty:** strong -- amount matches INV-1205 exactly, but duplicate flag suggests it may already be settled.
- **Rules said:** INV-1205 already settled by BNK-000200; suspected duplicate credit, left unapplied.
- **Considered:** INV-1205, INV-1470, INV-1360, INV-1292, INV-1458, INV-1171, INV-1137, INV-1279, INV-1492, INV-1213, INV-1430, INV-1278
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000342 — ₹33,917.46 · `CONFIRM_MATCH`

*2026-08-05 · NEEDS_REVIEW · BY TRANSFER-667862014969-*

The bank credit of Rs 33,917.46 on 2026-08-05 matches the narration 'BY TRANSFER-667862014969-' and corresponds to invoice INV-1350 for Agarwal Logistics, but is short by Rs 3,768.61, which equals the 10% TDS that would have been deducted from the gross invoice amount of Rs 37,686.07.

- **Lead:** INV-1350
- **Certainty:** strong -- amount gap exactly equals expected TDS, narration shows a transfer with UTR matching the invoice party.
- **Rules said:** Short of INV-1350 by Rs3768.61, which is 10% TDS.
- **Considered:** INV-1350
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000477 — ₹33,635.66 · `REQUEST_REMITTANCE`

*2026-05-27 · EXCEPTION · INT.PD:465926998515*

The bank credit of Rs 33,635.66 on 2026-05-27 is labelled as an interest payment (INT.PD) with UTR 465926998515. It does not exactly match any open invoice; the closest candidate, INV-1190 for Rs 33,761.30, is short by Rs 125.64, suggesting the credit may be interest or a partial payment on that invoice.

- **Lead:** INV-1190
- **Certainty:** weak -- amount close but unexplained difference; narration indicates interest payment.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1190
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000504 — ₹33,221.92 · `NEEDS_MORE_DATA`

*2026-05-27 · EXCEPTION · CHARGES GST @18%*

Bank credit of Rs 32,972.34 on 2026-05-12 with narration 'INT.PD:684650796321' (UTR same) shows no matching invoice in the ledger; the amount and date do not correspond to any recorded transaction, and the narration does not reveal a counterparty.

- **Lead:** —
- **Certainty:** weak -- no invoice matches amount, date, or narration; cannot infer purpose without additional remittance details.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000021 — ₹31,610.90 · `REQUEST_REMITTANCE`

*2026-07-17 · EXCEPTION · BY TRANSFER-296044202288-*

The bank credit of Rs 31,610.90 on 2026‑07‑17 (UTR 296044202288) does not exactly match any open invoice. The closest candidate is INV‑1423 for Bhatt Logistics (gross Rs 31,719.94), leaving an unexplained shortfall of Rs 109.04. The narration only shows a generic transfer reference with no counterparty name.

- **Lead:** INV-1423
- **Certainty:** moderate -- amount is very close to INV‑1423 but the Rs 109 difference cannot be explained from the data.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1007, INV-1423
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000367 — ₹31,457.72 · `REQUEST_REMITTANCE`

*2026-08-05 · EXCEPTION · INB/900301871916/PAYMENT*

The credit of Rs 31,457.72 on 2026‑08‑05 (UTR 900301871916) is close to the open invoice INV‑1052 for Pillai Traders Ltd (Rs 31,591.10), differing by only Rs 133.38. No other candidate invoice matches the amount, and the narration does not name a counterparty.

- **Lead:** INV-1052
- **Certainty:** moderate -- amount gap is small and could be bank charges or rounding; narration lacks details.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1375, INV-1052
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000336 — ₹28,113.39 · `CONFIRM_MATCH`

*2026-06-19 · EXCEPTION · IMPS-714412988993-BhattExp*

The credit of Rs 28,113.39 on 2026-06-19 from BhattExp (UTR 714412988993) is Rs 521.57 short of the gross amount of INV-1343 (Bhatt Exports Ltd, Rs 28,634.96). The shortfall closely matches a 2% TDS deduction (≈Rs 573), suggesting the payment is the net amount after TDS.

- **Lead:** INV-1343
- **Certainty:** moderate -- amount gap aligns with expected 2% TDS on the invoice, though TDS not explicitly referenced in narration.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1343, INV-1490, INV-1487, INV-1249, INV-1496, INV-1159, INV-1108, INV-1013, INV-1344, INV-1423, INV-1454, INV-1260
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000105 — ₹28,000.64 · `REQUEST_REMITTANCE`

*2026-06-15 · NEEDS_REVIEW · IMPS-566761533894-ChattTex*

The credit of Rs 28,000.64 on 2026-06-15 comes from an IMPS transfer narrated as 'ChattTex', which points to a Chatterjee/Textiles counterparty, but none of the open invoices for that party match this amount exactly; the closest is INV-1082 (Nair Enterprises) differing by only Rs 0.50, yet the narration does not mention that name.

- **Lead:** —
- **Certainty:** weak -- narration suggests Chatterjee/Textiles but amount does not match any of their open invoices; the nearest invoice belongs to a different party and the narration does not support it.
- **Rules said:** Part payment against INV-1159 (the counterparty name matches and no other open invoice fits); Rs10289.50 still outstanding, with no TDS or charge explaining it.
- **Considered:** INV-1098, INV-1082, INV-1159, INV-1260, INV-1329, INV-1110, INV-1004, INV-1454, INV-1044, INV-1109, INV-1489, INV-1248
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000052 — ₹27,854.26 · `WRITE_OFF_SMALL`

*2026-06-23 · EXCEPTION · IMPS-993258882513-IYERDIS*

The bank credit of Rs 27,854.26 on 2026-06-23 (IMPS-993258882513-IYERDIS) closely matches invoice INV-1271 from Iyer Exports (gross Rs 27,896.58), leaving an unexplained shortfall of Rs 42.32. No other candidate invoice is within a reasonable range, and the narration does not reveal a different counterparty.

- **Lead:** INV-1271
- **Certainty:** weak -- amount gap is small but unexplained; name matches but reason for difference unclear.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1271, INV-1137, INV-1044, INV-1025, INV-1023, INV-1298, INV-1218, INV-1482, INV-1083, INV-1016, INV-1129, INV-1431
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000088 — ₹27,611.30 · `NEEDS_MORE_DATA`

*2026-06-09 · EXCEPTION · BY TRANSFER-295234922487-*

A credit of Rs 27,611.30 arrived on 2026-06-09 via UTR 295234922487 with narration 'BY TRANSFER-295234922487-'. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- no invoice matches the amount, date, or narration; further information from the payer is required.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000294 — ₹26,821.67 · `NEEDS_MORE_DATA`

*2026-07-17 · EXCEPTION · INB/485705998016/PAYMENT*

A credit of Rs 26,821.67 arrived on 2026-07-17 with narration 'INB/485705998016/PAYMENT' and UTR 485705998016. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration gives no counterparty name and no invoice matches the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000419 — ₹23,853.03 · `REQUEST_REMITTANCE`

*2026-06-18 · EXCEPTION · IMPS-947575584172-IyerExp*

The bank credit of Rs 23,853.03 on 2026-06-18 (IMPS transfer from IyerExp) does not exactly match any open invoice. The closest is INV-1126 (Iyer Exports, Rs 24,050.52), leaving an unexplained shortfall of Rs 197.49.

- **Lead:** INV-1126
- **Certainty:** weak -- amount gap is small but unexplained; narration points to Iyer Exports
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1218, INV-1431, INV-1271, INV-1126, INV-1291, INV-1232, INV-1169, INV-1083, INV-1044, INV-1023, INV-1129, INV-1442
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000126 — ₹23,202.32 · `NEEDS_MORE_DATA`

*2026-07-14 · EXCEPTION · INB/169341133199/PAYMENT*

A bank credit of Rs 23,202.32 was received on 2026-07-14 with narration 'INB/169341133199/PAYMENT' and UTR 169341133199. No invoice in the ledger matches this amount, date, or counterparty, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** weak -- no candidate invoices were close on amount, date, or counterparty.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000164 — ₹22,812.24 · `REQUEST_REMITTANCE`

*2026-06-22 · EXCEPTION · INB/366242515962/PAYMENT*

The bank credit of Rs 22,812.24 on 2026-06-22 (UTR 366242515962) is close to invoice INV-1291 from Iyer Polymers LLP (gross Rs 22,893.76), differing by only Rs 81.52. No other invoice matches the amount, and the narration does not name a counterparty.

- **Lead:** INV-1291
- **Certainty:** moderate -- amount gap is small and could be fees or rounding, but narration lacks detail.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1291, INV-1166
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000443 — ₹21,136.27 · `REQUEST_REMITTANCE`

*2026-07-28 · EXCEPTION · INB/255925254156/PAYMENT*

The bank credit of Rs 21,136.27 on 2026-07-28 (UTR 255925254156) does not exactly match any open invoice. The closest is INV-1334 from Agarwal Enterprises LLP (gross Rs 21,206.70), leaving a small unexplained difference of Rs -70.43. No other invoice or narration details explain the amount.

- **Lead:** INV-1334
- **Certainty:** moderate -- amount is very close to INV-1334 but the residual gap lacks explanation.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1459, INV-1334
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000079 — ₹20,877.50 · `CHECK_DUPLICATE`

*2026-05-25 · EXCEPTION · INB/214393309804/PAYMENT*

The credit of Rs 20,877.50 on 2026-05-25 (UTR 214393309804) exactly matches the outstanding amount of invoice INV-1075 from Chatterjee Exports, but the rule engine notes that INV-1075 was already settled by a prior credit (BNK-000078) and treats this as a suspected duplicate credit left unapplied.

- **Lead:** INV-1075
- **Certainty:** strong -- amount matches invoice exactly, but flagged as duplicate by rules
- **Rules said:** INV-1075 already settled by BNK-000078; suspected duplicate credit, left unapplied.
- **Considered:** INV-1075, INV-1410, INV-1437
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000497 — ₹20,836.40 · `CHECK_REFUND`

*2026-07-21 · EXCEPTION · NEFT/BHATTSTE/RETURN*

A credit of Rs 20,836.40 arrived from Bhatt Steels (NEFT/BHATTSTE/RETURN) on 2026-07-21. The amount does not match any open invoice; the closest candidate (INV-1075 for Chatterjee Exports) is off by Rs 41.10 and the narration points to a different party, suggesting this is a refund or return rather than a payment against an invoice.

- **Lead:** —
- **Certainty:** weak -- narration indicates Bhatt Steels return but no invoice matches the amount; the nearest invoice is for a different party and still off by Rs 41.10.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1075, INV-1316, INV-1464, INV-1311, INV-1108, INV-1191, INV-1159, INV-1454, INV-1481, INV-1344, INV-1297, INV-1461
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000494 — ₹20,131.54 · `NEEDS_MORE_DATA`

*2026-05-29 · EXCEPTION · REV-111802794634-FAILED TXN*

A credit of Rs 11,512.55 arrived on 2026-06-10 via IMPS from an unknown remitter (UTR 298072407250). No invoice in the ledger matches this amount, date, or counterparty, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** low -- narration provides no identifiable party and no invoice fits the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000468 — ₹19,975.62 · `CHECK_DUPLICATE`

*2026-07-15 · EXCEPTION · NEFT-BHATTEXP*

Credit of Rs 19,975.62 from NEFT-BHATTEXP matches the exact amount of open invoice INV-1490 (Bhatt Exports Ltd). The rule engine flagged it as a suspected duplicate because INV-1490 was already settled by transaction BNK-000121.

- **Lead:** INV-1490
- **Certainty:** strong -- amount exact match and narration counterparty align, but duplicate suspicion needs verification.
- **Rules said:** INV-1490 already settled by BNK-000121; suspected duplicate credit, left unapplied.
- **Considered:** INV-1490, INV-1049, INV-1481, INV-1343, INV-1297, INV-1244, INV-1464, INV-1316, INV-1311, INV-1276, INV-1461, INV-1321
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000190 — ₹18,333.69 · `CHECK_DUPLICATE`

*2026-05-26 · EXCEPTION · NEFT-IyrPc*

A credit of Rs 18,333.69 arrived on 2026-05-26 with narration NEFT-IyrPc and UTR 589818301607. The amount exactly matches the open invoice INV-1193 from Iyer Packaging (gross Rs 18,333.69, issued 2026-05-20), but the rule engine flagged it as a suspected duplicate because INV-1193 was already settled by the prior credit BNK-000189.

- **Lead:** INV-1193
- **Certainty:** moderate -- amount and counterparty name match, but duplicate flag suggests possible overpayment or error.
- **Rules said:** INV-1193 already settled by BNK-000189; suspected duplicate credit, left unapplied.
- **Considered:** INV-1193
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000441 — ₹18,315.45 · `REQUEST_REMITTANCE`

*2026-06-14 · EXCEPTION · IMPS-301352710919-BhattTex*

The credit of Rs 18,315.45 from BhattTex (UTR 301352710919) does not exactly match any open invoice; the nearest is INV-1366 for Chatterjee Textiles (Rs 18,052.37), leaving an unexplained Rs 263.08 difference. No other candidate invoice is within a reasonable range.

- **Lead:** INV-1366
- **Certainty:** weak -- amount close to INV-1366 but the small gap lacks explanation and the counterparty name differs.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1454, INV-1490, INV-1343, INV-1159, INV-1249, INV-1496, INV-1344, INV-1366, INV-1423, INV-1245, INV-1260, INV-1224
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000034 — ₹18,273.42 · `REQUEST_REMITTANCE`

*2026-06-10 · EXCEPTION · IMPS-679415533445-DeshmSol*

The bank credit of Rs 18,273.42 on 2026-06-10 from DeshmSol (UTR 679415533445) does not exactly match any open invoice; the closest is INV-1117 for Deshmukh Packaging Ltd (Rs 18,493.52), leaving a Rs 220.10 shortfall that could be a bank fee, TDS, or partial payment.

- **Lead:** INV-1117
- **Certainty:** weak -- amount gap small but unexplained; name matches narration partially.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1141, INV-1117, INV-1020, INV-1356, INV-1367, INV-1156, INV-1222, INV-1333, INV-1070, INV-1266, INV-1324, INV-1437
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000501 — ₹18,228.21 · `NEEDS_MORE_DATA`

*2026-07-15 · EXCEPTION · INT.PD:679589804681*

A credit of Rs 56,846.35 appeared on 2026-05-10 with narration 'REV-383230503741-FAILED TXN' and UTR 383230503741, indicating a reversal of a failed transaction. No invoice in the ledger matches this amount, date, or counterparty, so the money cannot be tied to any outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- no invoice candidates match the amount, date or narration
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000277 — ₹17,808.05 · `REQUEST_REMITTANCE`

*2026-08-09 · EXCEPTION · BY TRANSFER-518367687989-*

The bank credit of Rs 17,808.05 on 2026-08-09 (UTR 518367687989) does not match any invoice exactly; it is about Rs 50‑55 less than the open invoices INV-1284 (Rs 17,862.99) and INV-1124 (Rs 17,857.95). The narration only shows a transfer reference, with no counterparty name, so the shortfall is likely due to bank charges, TDS deduction, or a similar fee that the rule engine could not account for.

- **Lead:** INV-1284
- **Certainty:** moderate -- amount close to INV-1284 but the exact reason for the ~Rs 55 gap is unclear from the narration.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1284, INV-1124
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000130 — ₹17,530.67 · `REQUEST_REMITTANCE`

*2026-07-11 · EXCEPTION · RTGS UTIB775729128933 CHATTTEX*

The credit of Rs 17,530.67 matches Chatterjee Textiles invoice INV-1124 (gross Rs 17,857.95) but is short by Rs 327.28, which is close to the 2% TDS that would be deducted on that invoice. The narration indicates an RTGS from Chatterjee Textiles (UTR 775729128933) on 2026-07-11.

- **Lead:** INV-1124
- **Certainty:** moderate -- amount gap aligns with expected 2% TDS on INV-1124, but no remittance advice to confirm.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1124, INV-1244, INV-1321, INV-1276, INV-1460, INV-1060, INV-1311, INV-1268, INV-1454, INV-1154, INV-1155, INV-1260
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000476 — ₹17,285.12 · `REQUEST_REMITTANCE`

*2026-06-01 · EXCEPTION · IMPS-771987118879-UNKNOWN REMITTER*

The bank credit of Rs 17,285.12 on 2026‑06‑01 (UTR 771987118879) does not match any invoice exactly; the closest candidate, INV‑1222 for Deshmukh Solutions Pvt Ltd, is Rs 79.25 higher. The narration shows an IMPS transfer from an unknown remitter, giving no clear counterparty or payment reference.

- **Lead:** INV-1222
- **Certainty:** weak -- amount close to INV-1222 but unexplained Rs 79.25 gap and no remitter details
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1222
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000166 — ₹16,901.39 · `CONFIRM_MATCH`

*2026-07-03 · NEEDS_REVIEW · NEFT-IYRPL*

The bank credit of Rs 16,901.39 on 2026-07-03 (UTR 282895124217, narration NEFT-IYRPL) matches the gross amount of invoice INV-1169 (Rs 18,779.32) less an exact TDS deduction of Rs 1,877.93 (10%). The rule engine flagged it as short by that TDS amount, indicating the payment likely represents the net amount after tax withheld.

- **Lead:** INV-1169
- **Certainty:** strong -- amount gap equals 10% TDS of the invoice, narration points to Iyer Polymers LLP.
- **Rules said:** Short of INV-1169 by Rs1877.93, which is 10% TDS.
- **Considered:** INV-1169
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000125 — ₹16,252.56 · `CHECK_DUPLICATE`

*2026-05-15 · EXCEPTION · NEFT-AgarwEnt*

The credit of Rs 16,252.56 on 2026-05-15 from NEFT-AgarwEnt exactly matches the gross amount of invoice INV-1116 (Agarwal Enterprises LLP), which the rules indicate was already settled by a prior transaction (BNK-000124). This appears to be a duplicate credit that was left unapplied.

- **Lead:** INV-1116
- **Certainty:** strong -- amount matches invoice exactly and narration points to the same counterparty; rule already flagged as suspected duplicate.
- **Rules said:** INV-1116 already settled by BNK-000124; suspected duplicate credit, left unapplied.
- **Considered:** INV-1116, INV-1103, INV-1267, INV-1015, INV-1411, INV-1371, INV-1421, INV-1104
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000104 — ₹15,731.83 · `CHECK_DUPLICATE`

*2026-08-07 · EXCEPTION · IMPS-468854502485-DESHMPAC*

The credit of Rs 15,731.83 on 2026-08-07 exactly matches the gross amount of invoice INV-1097 (Deshmukh Packaging Ltd). The rule engine flagged it as a suspected duplicate because invoice INV-1097 was already settled by transaction BNK-000103, leaving this credit unapplied.

- **Lead:** INV-1097
- **Certainty:** strong -- amount matches invoice exactly, but already marked as settled/duplicate.
- **Rules said:** INV-1097 already settled by BNK-000103; suspected duplicate credit, left unapplied.
- **Considered:** INV-1097, INV-1043, INV-1033, INV-1092, INV-1463, INV-1401, INV-1167, INV-1199, INV-1236, INV-1450, INV-1203, INV-1427
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000485 — ₹15,416.35 · `CHECK_REFUND`

*2026-05-28 · EXCEPTION · NEFT/BHATTEXP/RETURN*

A credit of Rs 15,416.35 from Bhatt Exports (NEFT/BHATTEXP/RETURN) appears to be a return or refund, but none of the open invoices from Bhatt Exports or related parties match this amount; the closest invoices differ by several thousand rupees.

- **Lead:** —
- **Certainty:** moderate -- narration indicates a return from Bhatt Exports, but amount does not correspond to any listed invoice.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1249, INV-1496, INV-1344, INV-1423, INV-1245, INV-1066, INV-1017, INV-1089, INV-1417, INV-1410, INV-1366, INV-1109
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000495 — ₹14,973.76 · `NEEDS_MORE_DATA`

*2026-05-22 · EXCEPTION · INT.PD:315420512279*

The bank shows a credit of Rs 8,072.62 on 2026-05-05 with narration 'REV-325808253619-FAILED TXN', indicating a reversal of a failed transaction. No invoices in the ledger match this amount, date, or any identifiable counterparty, so the credit cannot be tied to an outstanding receivable.

- **Lead:** —
- **Certainty:** weak -- narration suggests a reversal but no invoice data exists to confirm purpose.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000033 — ₹13,313.61 · `REQUEST_REMITTANCE`

*2026-05-12 · EXCEPTION · IMPS-268346997804-ChattTex*

A credit of Rs 13,313.61 from ChattTex (UTR 268346997804) arrived on 2026-05-12. The amount does not exactly match any open invoice; the closest is INV-1419 for Chatterjee Textiles (Rs 13,127.13), leaving an unexplained excess of Rs 186.48.

- **Lead:** INV-1419
- **Certainty:** weak -- name matches but the amount gap is unexplained and could be fees, TDS, or partial payment.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1419, INV-1019, INV-1164, INV-1075, INV-1415, INV-1077, INV-1085, INV-1089, INV-1496, INV-1249
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000389 — ₹13,027.98 · `CHECK_DUPLICATE`

*2026-07-08 · EXCEPTION · UPI/613981994926/pillapol@okhdfcbank*

A UPI credit of Rs 13,027.98 arrived on 2026-07-08 from UPI ID pillapol@okhdfcbank. The amount does not exactly match any open invoice; the closest are INV-1486 (Rs 13,089.46, diff -Rs 61.48) and INV-1403 (Rs 13,042.31, diff -Rs 14.33). The narration does not clearly identify the counterparty, and the rule engine flagged this as a suspected duplicate credit that remains unapplied.

- **Lead:** —
- **Certainty:** weak -- amount is near two invoices but gaps remain unexplained and narration does not confirm payer
- **Rules said:** INV-1486 already settled by BNK-000463; suspected duplicate credit, left unapplied.
- **Considered:** INV-1486, INV-1403, INV-1459, INV-1399, INV-1353, INV-1197, INV-1409, INV-1226, INV-1052, INV-1152, INV-1470, INV-1068
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000153 — ₹12,081.88 · `REQUEST_REMITTANCE`

*2026-07-16 · EXCEPTION · IMPS-870818130396-CHATTSTE*

A credit of Rs 12,081.88 arrived on 2026-07-16 from an IMPS transfer narrated as 'CHATTSTE', suggesting a payment from a Chatterjee‑related party. No invoice matches this exact amount; the closest is INV-1155 (Chatterjee Steels & Co) for Rs 12,640.97, leaving an unexplained shortfall of Rs 559.09.

- **Lead:** INV-1155
- **Certainty:** moderate -- amount is near INV-1155 but the gap is not explained by any visible discount, tax, or fee.
- **Rules said:** Candidates found but no rule could explain the amount.
- **Considered:** INV-1244, INV-1340, INV-1488, INV-1276, INV-1155, INV-1124, INV-1224, INV-1321, INV-1460, INV-1154, INV-1328, INV-1060
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000090 — ₹11,185.61 · `CHECK_DUPLICATE`

*2026-08-01 · EXCEPTION · UPI/816379000545/iyerpol@okhdfcbank*

A UPI credit of Rs 11,185.61 on 2026-08-01 from iyerpol@okhdfcbank (UTR 816379000545) does not match any open invoice; the rule engine notes that INV-1061 (Bhatt Logistics) was already settled by BNK-000067 and suspects this is a duplicate credit left unapplied.

- **Lead:** —
- **Certainty:** weak -- narration points to Iyer Polymers but no invoice matches the amount; rule flags duplicate of already‑settled INV-1061.
- **Rules said:** INV-1061 already settled by BNK-000067; suspected duplicate credit, left unapplied.
- **Considered:** INV-1115, INV-1061, INV-1257, INV-1337, INV-1474, INV-1396, INV-1441, INV-1083, INV-1232, INV-1169, INV-1035, INV-1291
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000151 — ₹10,952.14 · `CONFIRM_MATCH`

*2026-06-02 · NEEDS_REVIEW · INB/125776369480/PAYMENT*

The bank credit of Rs 10,952.14 on 2026-06-02 (UTR 125776369480) matches the net amount of invoice INV-1149 after a 10% TDS deduction (gross Rs 12,169.04 less TDS Rs 1,216.90). The narration does not name a party, but the UTR and amount gap point to this invoice.

- **Lead:** INV-1149
- **Certainty:** moderate -- amount gap exactly equals 10% TDS on INV-1149, narration lacks details but UTR aligns.
- **Rules said:** Short of INV-1149 by Rs1216.90, which is 10% TDS.
- **Considered:** INV-1149
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000152 — ₹10,823.13 · `NEEDS_MORE_DATA`

*2026-05-19 · EXCEPTION · INB/912187525683/PAYMENT*

A credit of Rs 10,823.13 was received on 2026-05-19 via UTR 912187525683 with narration 'INB/912187525683/PAYMENT'. No invoice in the ledger matches this amount, date, or counterparty, and the rule engine found no candidates.

- **Lead:** —
- **Certainty:** weak -- narration provides only a UTR, no counterparty name, and no invoice matches the amount or date.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000317 — ₹9,961.76 · `CHECK_DUPLICATE`

*2026-07-12 · EXCEPTION · UPI/535432695935/chatttex@okkkbkbank*

A UPI credit of Rs 9,961.76 from chatttex@okkkbkbank on 2026-07-12 does not match any open invoice; the closest is INV-1340 (Chatterjee Textiles, Rs 9,801.24) leaving a Rs 160.52 gap. The narration names no party and the rules flag this as a suspected duplicate credit of an already‑settled invoice (INV-1454).

- **Lead:** —
- **Certainty:** weak -- narration gives no counterparty, amount gap unexplained, and duplicate‑credit suspicion lacks supporting evidence.
- **Rules said:** INV-1454 already settled by BNK-000227; suspected duplicate credit, left unapplied.
- **Considered:** INV-1340, INV-1124, INV-1244, INV-1155, INV-1321, INV-1276, INV-1460, INV-1328, INV-1454, INV-1260, INV-1366, INV-1417
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000465 — ₹9,083.46 · `CHECK_DUPLICATE`

*2026-08-11 · EXCEPTION · RTGS SBIN989052710628 CHATTTEX*

The bank credit of Rs 9,083.46 on 2026-08-11 (UTR 989052710628, narration RTGS SBIN989052710628 CHATTTEX) appears to be a payment from Chatterjee Textiles, but none of the open invoices for that party match this exact amount; the closest is INV-1488 (Rs 9,421.21), leaving a Rs 337.75 shortfall. The rule engine flagged it as a suspected duplicate of INV-1454, which was already settled by another credit.

- **Lead:** —
- **Certainty:** moderate -- narration points to Chatterjee Textiles and amount is near INV-1488, but the gap is unexplained and the system suspects a duplicate credit.
- **Rules said:** INV-1454 already settled by BNK-000227; suspected duplicate credit, left unapplied.
- **Considered:** INV-1488, INV-1340, INV-1276, INV-1244, INV-1124, INV-1155, INV-1321, INV-1460, INV-1328, INV-1454, INV-1260, INV-1366
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000390 — ₹7,139.17 · `NEEDS_MORE_DATA`

*2026-08-17 · EXCEPTION · BY TRANSFER-975926075646-*

A bank credit of Rs 7,139.17 was received on 2026-08-17 via UTR 975926075646; the narration only indicates a transfer with no counterparty or invoice reference, and no ledger invoice matches the amount, date, or party.

- **Lead:** —
- **Certainty:** low -- narration provides no identifiable party and no invoice candidate exists.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000498 — ₹6,583.53 · `NEEDS_MORE_DATA`

*2026-05-20 · EXCEPTION · REFUND/985921779195/GATEWAY*

An IMPS credit of Rs 21,720.48 arrived on 2026-05-06 from an unknown remitter (UTR 767232262429). The narration does not identify any counterparty, and no invoice in the ledger matches this amount, date, or party, leaving the transaction unexplained.

- **Lead:** —
- **Certainty:** weak -- narration gives no identifiable party and no invoice candidate exists.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000491 — ₹3,649.21 · `NEEDS_MORE_DATA`

*2026-06-03 · EXCEPTION · REFUND/631494301877/GATEWAY*

The bank credit of Rs 17,047.64 on 2026-07-08 is an interest payment (INT.PD) identified by UTR 239893197000. No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest payment but no invoice data to verify.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000484 — ₹3,559.71 · `CHECK_REFUND`

*2026-07-12 · EXCEPTION · REFUND/995665327270/GATEWAY*

A credit of Rs 3,559.71 arrived on 2026-07-12 with narration 'REFUND/995665327270/GATEWAY' and UTR 995665327270, indicating a gateway refund. No invoices in the ledger match this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** moderate -- narration clearly indicates a refund, but without a matching invoice we cannot confirm which transaction it relates to.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000487 — ₹2,184.35 · `NEEDS_MORE_DATA`

*2026-07-07 · EXCEPTION · INT.PD:683037221870*

The bank credit of Rs 2,184.35 on 2026-07-07 is an interest payment (INT.PD) identified by UTR 683037221870. No invoice in the ledger matches this amount, date, or counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest payment but no matching invoice exists in the data provided.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b

### BNK-000490 — ₹915.40 · `NEEDS_MORE_DATA`

*2026-05-18 · EXCEPTION · CHARGES GST @18%*

The bank credit of Rs 63,394.96 on 2026-07-22 is labelled as an interest payment (INT.PD) with UTR 919023316095. No invoice in the ledger matches this amount, date, or any identifiable counterparty, so the rule engine could not find a candidate.

- **Lead:** —
- **Certainty:** weak -- narration indicates interest payment but no matching invoice exists; amount and date do not correspond to any recorded invoice.
- **Rules said:** No candidate invoices survived blocking.
- **Considered:** nothing
- **Note by:** nim:nvidia/nemotron-3-super-120b-a12b
