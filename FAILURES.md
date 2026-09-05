# What broke, and what we did about it

Every item here cost real time and produced a real change to the system. They
are written up because a build log that contains only successes is not a build
log — and because several of these failures are the reason the architecture
looks the way it does.

---

## 1. We measured our own LLM and refused to ship it

**The plan** was the obvious one: rules handle what they can, an LLM adjudicates
the residual, and the LLM's answers post automatically above a confidence
threshold.

**What happened.** We built Stage 2 with full guards, ran it over `batch_dev`,
then scored every cached response against the answer key:

| | committed answers | link precision |
|---|---|---|
| Groq `openai/gpt-oss-120b` | 44 | **0.432** |
| NVIDIA `nemotron-3-super-120b` | 9 | **0.556** |
| Deterministic rules | 357 | **0.994** |

Then we checked whether the models' own confidence could filter the good
answers from the bad. It cannot. Both claim ≥0.95 on nearly every answer, and
precision *inside that bucket* is 0.404. A floor at 0.99 keeps 4 answers of 52.
There is no threshold that separates its right answers from its wrong ones.

**Why it fails.** Two reasons, both structural rather than fixable by prompting.
We hand the model twelve near-identical invoices and ask "which one?", when the
correct answer is frequently *none of them* — and models have strong
forced-choice bias, so they pick. And the discriminating evidence here is
arithmetic, not language: which invoice a credit settles is decided by exact
sums and statutory TDS rates, not by reading comprehension.

**What we did.** `llm.adjudicate: false`. The code, its guards and its tests all
remain in the repo — flip the flag to reproduce the numbers above. The LLM was
given the job it is actually good at instead: writing the exception queue
(`llm.triage: true`), where it proposes no links and therefore cannot move
precision in either direction.

**What we'd have done with more data.** The narrations in our generator mostly
carry no counterparty name at all — 39 of 50 blocking misses are
`INB/600951639708/PAYMENT`-shaped. Real Indian bank narrations often do carry
one, and that is exactly the messy-text problem an LLM beats `rapidfuzz` at. Our
synthetic data is unintentionally hostile to the thing LLMs are best at, and we
did not regenerate it to flatter our own results.

---

## 2. A 1,000-token budget silently failed 42% of our calls

**Symptom.** A full eval run finished with 46 of 110 adjudications recorded as
`API_ERROR`. The metrics table looked plausible. It was garbage.

**Cause.** `max_tokens: 1000`. On a reasoning model the completion budget is
shared with the reasoning the model does *before* it writes anything, and under
strict JSON-schema decoding a budget that runs out mid-object is not a truncated
answer you can inspect — the provider rejects the whole request and returns an
empty `400 json_validate_failed`. Every failure was one of the harder,
larger-shortlist cases; a typical adjudication spends ~900 output tokens and the
worst we measured spent 3,492.

**Fix.** `max_tokens: 4000`, with the measurement recorded in `config.yaml`.
Billing is on tokens used, so the unused ceiling costs nothing.

**The deeper fix.** Schema failures now report as `SCHEMA_UNSATISFIED`, not as a
generic `API_ERROR`. The two have different causes and different remedies, and
reporting one as the other sent us debugging the network for half an hour
instead of reading the config.

---

## 3. A broken run burned our entire daily quota

The failed run in §2 consumed ~198,000 of Groq's 200,000 free tokens per day —
about 57,000 of them on calls that returned nothing. The corrected re-run died
after four transactions.

**Fix, and it is a design fix.** A rejected key, a blocked model, or an exhausted
daily quota fails *identically for every transaction in the batch*. The original
code caught these per-transaction, which would have written 110 plausible-looking
`EXCEPTION` records and a report that read like a difficult day's reconciliation.
Setup failures now raise `LLMUnavailable`, stop the run, and write **no report at
all**. Only genuine per-transaction failures — a timeout, a transient error —
become exceptions.

An exception queue is only worth something if every entry in it is real.

---

## 4. NVIDIA's documented structured-output mechanism does not work

We moved to NVIDIA NIM because its free tier meters *requests* rather than
tokens, which is the constraint that stopped us in §3.

NVIDIA's documentation specifies constrained decoding via the `nvext` extension:
`extra_body: {"nvext": {"guided_json": schema}}`. We implemented that. It is
**silently ignored** on the hosted catalogue — no error, no warning. The model
invents its own field names (`invoices` for `invoice_ids`, a numeric
`allocation` where the schema requires a string) and every response dies in our
validator as `MALFORMED`.

We found it by testing three mechanisms against the same prompt and comparing
the returned field names:

```
nvext.guided_json            IGNORED (keys ['confidence', 'invoices', 'reasoning'])
response_format.json_schema  ENFORCED
extra_body.guided_json       IGNORED (keys ['confidence', 'invoices', 'reasoning'])
```

OpenAI-shaped `response_format` with `strict: true` is honoured exactly. The
`nvext` path is presumably correct for a self-hosted NIM container and wrong for
the hosted endpoint. The code carries a comment saying so, because the
documentation will keep suggesting otherwise.

**Also:** `openai/gpt-oss-120b` reached end-of-life on NIM on 2026-09-03, one day
before we tried to use it. Pinning a model is not the same as having one.

---

## 5. We threw away correct answers over a currency symbol

The model returned:

```json
{"invoice_ids": ["INV-1011"],
 "allocations": [{"invoice_id": "INV-1011", "amount": "Rs 60,232.20"}],
 "confidence": 0.99,
 "reasoning": "credit matches INV-1011 net of 10% TDS (66,924.67 - 6,692.47)"}
```

That is the **right answer**, rejected as `ALLOCATION_INVALID` because our parser
stripped commas but not the `Rs ` prefix. 7 of the first 26 adjudications were
correct matches discarded on formatting. The model learned that format from our
own prompt, which prints amounts as `Rs 60,232.20`.

**Fix.** `parse_money` normalises the currency prefix and digit grouping, and
still rejects `"41250.00 rupees"`, `"1e5"`, zero and negatives. Eight tests
cover the accepted forms and seven cover the refused ones. Normalising
presentation is not the same as being lenient about value.

---

## 6. We caused a precision regression and backed it out

R1 fires on uniqueness alone — one candidate matching the credit to the paisa,
nobody named, and it posts. We measured whether R3 deserved the same treatment.
Over the 34 transactions this would newly reach:

| branch | correct | wrong | precision |
|---|---|---|---|
| TDS (exact 2% / 10% identity) | 12 | 0 | **1.000** |
| Bank charges (`≤ max(₹50, 0.5%)`) | 6 | 16 | **0.273** |

Every wrong answer came from the bank-charge side. That is invariant 4 stated in
measurements rather than prose: an exact arithmetic identity is a narrow target,
a tolerance *range* catches whatever happens to sit nearby.

We shipped the TDS branch at auto-match confidence. It posted `BNK-000160`
against `INV-1295` — a part payment that lands exactly 10% below an unrelated
customer's gross. Auto-precision went 1.000 → 0.998 and one wrong match posted
unattended. The eval report showing the regression is committed as
`reports/eval_dev_phase4_r3_unique_tds_*.md`.

**Fix.** The tier keeps its recall and gives up its autonomy: scored below
`auto_match`, it proposes and a human confirms. The arithmetic identifies *which
invoice*; nothing in it identifies *who paid*.

**Our own tests caught this before the eval did.**
`test_r3_must_not_fire_on_an_explainable_delta_alone` failed the moment the
change landed — the must-not-fire tests doing precisely the job they exist for.
It has been rewritten to assert the refined contract (may propose, must never
auto-post), with two further must-not-fire cases added beside it.

---

## 7. A rule stole work from a better-evidenced rule

After adding R7 (split payments), the auto-match rate went *down* — 406 → 403.

R3's new lone-TDS branch fires during the per-transaction pass; R7 runs
afterwards, over what the rules left unexplained. R3's weak 0.92 guess was
claiming transactions before R7's much stronger evidence — two credits landing
on an invoice total to the paisa — ever got to look at them.

**Fix.** Only a match strong enough to post unattended counts as settled. Anything
below `auto_match` is a proposal, and R7 may supersede it. Ordering between
rules is not an implementation detail when the rules disagree.

---

## What we did not fix

- **Recall is 0.874 against a 0.93 target.** The remaining gap is mostly
  `DISPUTED` and `OVERPAID` transactions where abstaining is arguably correct
  behaviour. We could close it by loosening rules; that would cost precision,
  which is the number we are least willing to trade.
- **Abstention precision fell 0.766 → 0.680.** This is arithmetic, not decay:
  R7 solved 50 genuinely hard cases that used to sit *correctly* in the queue,
  so numerator and denominator dropped by the same 50. The metric got worse
  because the system got better. We are reporting it rather than removing it.
- **`SHORT_PAID_CHARGES` is 12 of the remaining missing links.** We proved
  automating it unsafe (§6) and left it for humans.
