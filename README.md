# LedgerLoop

Autonomous bank-statement ↔ ledger reconciliation for the Razorpay AI Buildathon
(Track 04 — AI Finance Controller).

520 bank credits against a 500-invoice ledger. Four stages: candidate blocking →
deterministic rules → LLM → confidence routing. Every decision is auditable,
every unresolved item is queued with a reason, and every number below was
measured, not estimated.

---

## Results

`batch_holdout` was **never read during development** — no tuning, no debugging,
not once. It is the number that means anything, and it is reported here first
whatever it says.

| Metric | **holdout** | dev | stress | Target |
|---|---|---|---|---|
| Auto-match rate | **0.800** | 0.777 | 0.691 | ≥ 0.80 |
| **Precision on auto-matched** | **0.998** ✓ | 1.000 ✓ | 0.995 ✓ | ≥ 0.98 |
| Recall (all outcomes) | **0.889** | 0.874 | 0.808 | ≥ 0.93 |
| Missed escalation | **0.002** ✓ | 0.000 ✓ | 0.004 ✓ | ≤ 0.02 |
| Abstention precision | 0.511 | 0.680 | 0.699 | ≥ 0.70 |
| False-match value | ₹124,382 | ₹63,788 | ₹251,436 | report |
| Throughput | 10,259/min | 6,500/min | 8,133/min | report |
| Transactions | 504 | 520 | 520 | |

**The holdout beats the batch we developed against on both headline numbers.**
That is the result we care about most: nothing here is tuned to the data it was
measured on.

Auto-match on holdout is **0.7996 — two transactions short of target.** We are
reporting the miss rather than rounding it away. Precision on everything posted
unattended holds at 0.998 across all three batches, and 0.2% of transactions
posted wrong.

### How dev got there

| | baseline | + R7 split payments | + R7 completing pairs | + R3 unique-TDS |
|---|---|---|---|---|
| auto-match | 0.638 | 0.735 | 0.781 | **0.777** |
| precision (auto) | 1.000 | 1.000 | 1.000 | **1.000** |
| recall | 0.711 | 0.812 | 0.860 | **0.874** |
| true links | 355 | 405 | 429 | **436** |
| false positives | 2 | 2 | 2 | **2** |

**+81 correct links without a single new false positive.** Every step is a
committed report in [`reports/`](reports/).

---

## The AI judgment call

We built LLM adjudication — the model picks an invoice when the rules abstain —
with full guards, ran it over `batch_dev`, and scored every response against the
answer key.

| | committed answers | link precision |
|---|---|---|
| Groq `openai/gpt-oss-120b` | 44 | **0.432** |
| NVIDIA `nemotron-3-super-120b` | 9 | **0.556** |
| **Deterministic rules** | 357 | **0.994** |

Then we checked whether the models' confidence could filter good answers from
bad. It cannot: both claim ≥0.95 on nearly every answer, and precision *inside
that bucket* is 0.404. A floor at 0.99 keeps 4 answers of 52.

**So we turned it off.** `llm.adjudicate: false`. The code, its guards and its
tests all remain — flip the flag to reproduce those numbers.

The failure is structural, not promptable. We hand the model twelve
near-identical invoices and ask "which one?" when the answer is frequently *none
of them*, and models pick rather than abstain. The discriminating evidence in
reconciliation is arithmetic, not language.

### What the LLM does instead

It writes the **exception queue** — see
[`reports/exceptions_dev_final_*.md`](reports/). For every unresolved credit:
what the money probably is, what makes it unresolvable, one of eight suggested
actions, and a lead invoice for a human to check.

```
BNK-000158 — ₹283,019.55 · CHECK_DUPLICATE

The credit of ₹283,019.55 on 2026-07-17 exactly matches the outstanding
amount of invoice INV-1145, but INV-1145 was already settled by the prior
transaction BNK-000157, suggesting this credit is a duplicate or unapplied
payment.

  Lead: INV-1145
  Certainty: moderate — amount matches exactly, but the invoice is already settled
```

That is reading comprehension over amounts, dates and half-legible narrations —
the half of this problem a model is genuinely better at than a rule. It proposes
no links and mutates no decision, so **the reconciliation is identical with
triage on or off**. The LLM cannot move an accuracy number in either direction.

The `LLM invocation rate` of 0.000 above is therefore correct and deliberate: no
matching decision in this system was made by a model.

---

## What it gets wrong

**Recall is 0.874 against a 0.93 target — 63 links missing.** The breakdown:

| scenario | missing | why |
|---|---|---|
| `DISPUTED` | 19 | short payment with no explanation; a human genuinely must decide |
| `SHORT_PAID_CHARGES` | 12 | see below — we proved automating this unsafe |
| `OVERPAID` | 13 | excess over gross with no invoice number quoted |
| `CONSOLIDATED` | 5 | more than one valid subset; R4 abstains by design |
| `PARTIAL`, `CLEAN` | 7 | residual |

We could close much of this by loosening rules. We did not, because it costs
precision, and a wrong auto-post costs real money while a missed match costs a
human two minutes.

**We proved one tempting rule unsafe.** R1 posts on uniqueness alone — one
candidate matching to the paisa, nobody named. We measured whether R3 deserved
the same over 34 transactions:

| branch | correct | wrong | precision |
|---|---|---|---|
| TDS (exact 2% / 10% identity) | 12 | 0 | 1.000 |
| Bank charges (`≤ max(₹50, 0.5%)`) | 6 | 16 | **0.273** |

Every wrong answer came from the bank-charge side. An exact arithmetic identity
is a narrow target; a tolerance *range* catches whatever sits nearby. TDS gets
uniqueness; charges are refused outright.

**Abstention precision is our weakest number — 0.511 on holdout, and it fell
during development (0.766 → 0.680 on dev).** The fall is arithmetic, not decay:
R7 solved 50 genuinely hard cases that used to sit *correctly* in the exception
queue, so numerator and denominator both dropped by 50. The metric got worse
because the system got better.

But the holdout figure is worse still, and we will not explain that one away:
on unseen data, roughly half of what we escalate is a transaction rated EASY or
MEDIUM that we should have resolved. The queue is honest — every entry is a
genuine unknown to us — but it is longer than it needs to be, and that is real
work handed to a human that a better rule would have absorbed.

**Two false positives survive.** Both are `NEEDS_REVIEW`, so a human sees them
before anything posts. Neither is auto-matched.

**Our synthetic data is unintentionally hostile to LLMs.** 39 of 50 blocking
misses have no counterparty name in the narration at all
(`INB/600951639708/PAYMENT`). Real Indian bank narrations often do carry one,
which is exactly the messy-text problem a model beats `rapidfuzz` at. We did not
regenerate the data to flatter our own results.

---

## What broke while building it

Six substantial failures, written up with their measurements in
**[FAILURES.md](FAILURES.md)** — including a token budget that silently failed
42% of our calls, a broken run that burned an entire daily quota, NVIDIA's own
documented structured-output mechanism being silently ignored, correct answers
discarded over a currency symbol, and a precision regression we caused and
backed out.

---

## Quick start

```bash
make setup                  # venv + install
make demo                   # end-to-end on batch_dev, rules only, ~5s
make test                   # 141 tests
make eval BATCH=dev         # rules only, writes reports/
make eval-llm BATCH=dev     # adds LLM triage; needs a key in .env
make app                    # Streamlit reviewer UI
```

`make demo` needs no API key. Copy `.env.example` to `.env` and add a free
[NVIDIA NIM](https://build.nvidia.com) key for the triage stage.

---

## Guarantees

- **The holdout batch was never touched during development.** It is read once,
  at the end, behind an explicit `--allow-holdout` flag, and whatever it says is
  published.
- **The audit trail is append-only, enforced by SQLite triggers**, not by
  convention. A correction writes a new record carrying `supersedes`; both
  survive. `UPDATE` and `DELETE` on the decisions table abort.
- **Money is `Decimal` everywhere**, including through JSON and SQLite storage.
  No float ever touches a rupee.
- **Thresholds and tolerances live in `config.yaml`**, each carrying the
  measurement that set it. No magic numbers in `rules.py`.
- **The model may only return invoice ids it was shown.** A fabricated id forces
  `EXCEPTION` and is logged. Enforced in a pure function with must-not-pass
  tests that never open a network connection.
- **Reproducible data.** Fixed seeds; `manifest.json` records each batch's seed.

## Live demo

The reviewer UI deploys to Streamlit Community Cloud straight from `uv.lock` —
no Dockerfile, no `requirements.txt`. See **[DEPLOY.md](DEPLOY.md)**.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — the four-stage diagram and every
  design decision with its rationale
- **[FAILURES.md](FAILURES.md)** — what broke and what we did about it
- **[DEPLOY.md](DEPLOY.md)** — hosting the reviewer UI for free
- **[reports/](reports/)** — every eval run, in order, showing the trajectory
- **[config.yaml](config.yaml)** — every threshold with the measurement behind it
