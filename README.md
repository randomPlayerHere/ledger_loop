<div align="center">

# LedgerLoop

**An autonomous agent that reconciles a bank statement against an invoice ledger — and tells you honestly which rows it could not.**

Built for the Razorpay AI Buildathon · Track 04, AI Finance Controller

[![Live demo](https://img.shields.io/badge/Live_demo-Streamlit-0D94FB?style=for-the-badge&logo=streamlit&logoColor=white)](https://ledgerloop.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![uv](https://img.shields.io/badge/deps-uv-DE5FE9?style=for-the-badge)](https://github.com/astral-sh/uv)

![Auto-match](https://img.shields.io/badge/auto--match-80.0%25-1B7F3B)
![Precision](https://img.shields.io/badge/precision-0.998-1B7F3B)
![Tests](https://img.shields.io/badge/tests-149_passing-1B7F3B)

### **[Try the live demo →](https://ledgerloop.streamlit.app/)**

</div>

---

## What this is, in one paragraph

Every month a finance team gets a bank statement full of credits and a ledger
full of open invoices, and somebody has to say which paid which. It is rarely
one-to-one: customers pay two invoices in one transfer, deduct TDS, short-pay
by the bank's charges, split one invoice across two payments, or send money with
a narration like `INB/600951639708/PAYMENT` that names nobody. LedgerLoop takes
the two CSVs and does that matching — 520 credits against 500 invoices — posting
only what it can prove, and handing a human a written, prioritised queue of
everything else.

**It matches 80% of transactions unattended at 99.8% precision, and every
decision it makes is recorded in an append-only audit trail.**

---

## Results

`batch_holdout` was **never read during development** — not to tune, not to
debug, not once. It is the only number that means anything, so it is reported
first, whatever it says.

| Metric | **holdout** | dev | stress | Target |
|---|---|---|---|---|
| Auto-match rate | **0.800** | 0.777 | 0.691 | ≥ 0.80 |
| **Precision on auto-matched** | **0.998** | 1.000 | 0.995 | ≥ 0.98 |
| Recall (all outcomes) | **0.889** | 0.874 | 0.808 | ≥ 0.93 |
| Missed escalation | **0.002** | 0.000 | 0.004 | ≤ 0.02 |
| Abstention precision | 0.511 | 0.680 | 0.699 | ≥ 0.70 |
| False-match value | ₹124,382 | ₹63,788 | ₹251,436 | report |
| Throughput | 10,259/min | 6,500/min | 8,133/min | report |
| Transactions | 504 | 520 | 520 | |

**The holdout beats the batch we developed against on both headline numbers.**
Nothing here is tuned to the data it was measured on.

Auto-match on holdout is **0.7996 — two transactions short of target.** We are
reporting the miss rather than rounding it away.

<details>
<summary><b>How dev got there — every step is a committed report in <code>reports/</code></b></summary>

<br>

| | baseline | + R7 split payments | + R7 completing pairs | + R3 unique-TDS |
|---|---|---|---|---|
| auto-match | 0.638 | 0.735 | 0.781 | **0.777** |
| precision (auto) | 1.000 | 1.000 | 1.000 | **1.000** |
| recall | 0.711 | 0.812 | 0.860 | **0.874** |
| true links | 355 | 405 | 429 | **436** |
| false positives | 2 | 2 | 2 | **2** |

**+81 correct links without a single new false positive.**

</details>

---

## Quick start

```bash
git clone https://github.com/randomPlayerHere/ledger_loop.git
cd ledger_loop

make setup      # uv sync — venv + install
make demo       # end-to-end on batch_dev, ~5s, prints the metrics table
make app        # the Streamlit reviewer UI
```

**`make demo` needs no API key and no network.** The matching engine is
deterministic; the LLM is only used to write the exception queue.

| Command | What it does |
|---|---|
| `make setup` | Create the venv and install (uses [uv](https://github.com/astral-sh/uv)) |
| `make demo` | Full pipeline on `batch_dev`, rules only, prints metrics |
| `make test` | 149 tests |
| `make eval BATCH=dev` | Eval run, writes a timestamped report to `reports/` |
| `make eval-llm BATCH=dev` | Adds the LLM triage stage — needs a key in `.env` |
| `make data` | Regenerate all three batches from their fixed seeds |
| `make audit` | Inspect the append-only decision trail in `audit.db` |
| `make app` | Streamlit reviewer UI on `localhost:8501` |

For the triage stage, copy `.env.example` to `.env` and drop in a free
[Groq](https://console.groq.com/keys) or [NVIDIA NIM](https://build.nvidia.com)
key. Everything else runs without one.

---

## How it works

Four stages. Each one only passes on what the one before it could not explain.

```
 bank.csv (520 credits)          ledger.csv (500 invoices)
        └────────────┬────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 0 · BLOCKING                    candidates.py │
   │ 500 invoices ─▶ ≤20 plausible ones per transaction  │
   │   single   amount window · date window · name score │
   │   grouped  subsets of 2–4 invoices summing exactly  │
   └─────────────────────────────────────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 1 · DETERMINISTIC RULES              rules.py │
   │ pure functions, first match wins                    │
   │   R1  exactly one candidate matches to the paisa    │
   │   R4  a subset of invoices sums to the credit       │
   │   R3  shortfall = TDS 2%/10%, or bank charges       │
   │   R6  credit exceeds gross, excess left unapplied   │
   │   R5  short by an amount nothing explains           │
   │   R7  two credits summing to one invoice (batch)    │
   └─────────────────────────────────────────────────────┘
                     ▼  what no rule could explain
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 2 · LLM                     llm.py triage.py  │
   │   2a  adjudication  ── OFF, measured at 0.43 vs     │
   │                        0.994 precision for rules    │
   │   2b  triage        ── ON: writes the exception     │
   │                        queue, proposes no links     │
   └─────────────────────────────────────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 3 · ROUTING & AUDIT               engine.py   │
   │   confidence ≥ 0.95  ─▶ AUTO_MATCHED                │
   │   confidence ≥ 0.50  ─▶ NEEDS_REVIEW                │
   │   otherwise          ─▶ EXCEPTION                   │
   └──────────┬──────────────────────────┬───────────────┘
              ▼                          ▼
      reports/eval_*.md            audit.db (append-only)
```

Full rationale for every decision: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

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

Then we checked whether the models' own confidence could separate the good
answers from the bad. It cannot: both claim ≥0.95 on nearly every answer, and
precision *inside that bucket* is 0.404.

**So we turned it off.** `llm.adjudicate: false`. The code, its guards and its
tests all remain — flip the flag to reproduce those numbers yourself.

The failure is structural, not promptable. We hand the model twelve
near-identical invoices and ask "which one?" when the answer is frequently *none
of them* — and models pick rather than abstain. The discriminating evidence in
reconciliation is arithmetic, not language.

### So what does the LLM actually do?

It writes the **exception queue**. For every unresolved credit: what the money
probably is, what makes it unresolvable, a suggested action, and a lead invoice
for a human to check.

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
the half of this problem a model genuinely beats a rule at. It proposes no links
and mutates no decision, so **the reconciliation is byte-identical with triage
on or off.** The LLM cannot move an accuracy number in either direction.

The `LLM invocation rate` of 0.000 in the results table is therefore correct and
deliberate: **no matching decision in this system was made by a model.**

---

## What it gets wrong

**Recall is 0.874 against a 0.93 target — 63 links missing.**

| scenario | missing | why |
|---|---|---|
| `DISPUTED` | 19 | short payment with no explanation; a human must genuinely decide |
| `SHORT_PAID_CHARGES` | 12 | we proved automating this unsafe — see below |
| `OVERPAID` | 13 | excess over gross with no invoice number quoted |
| `CONSOLIDATED` | 5 | more than one valid subset; R4 abstains by design |
| `PARTIAL`, `CLEAN` | 7 | residual |

We could close much of this by loosening the rules. We did not, because it costs
precision — and **a wrong auto-post costs real money, while a missed match costs
a human two minutes.**

**We proved one tempting rule unsafe.** R1 posts on uniqueness alone. We
measured whether R3 deserved the same, over 34 transactions:

| branch | correct | wrong | precision |
|---|---|---|---|
| TDS (exact 2% / 10% identity) | 12 | 0 | **1.000** |
| Bank charges (`≤ max(₹50, 0.5%)`) | 6 | 16 | **0.273** |

Every wrong answer came from the bank-charge side. An exact arithmetic identity
is a narrow target; a tolerance *range* catches whatever happens to sit nearby.
TDS gets uniqueness; charges are refused outright.

**Abstention precision is our weakest number — 0.511 on holdout.** On unseen
data, roughly half of what we escalate is a transaction we should have resolved.
The queue is honest — every entry is a genuine unknown to us — but it is longer
than it needs to be, and that is real work handed to a human that a better rule
would have absorbed.

**Two false positives survive.** Both are routed `NEEDS_REVIEW`, so a human sees
them before anything posts. Neither is auto-matched.

**Our synthetic data is unintentionally hostile to LLMs.** 39 of 50 blocking
misses have no counterparty name in the narration at all. Real Indian bank
narrations often do carry one — exactly the messy-text problem a model beats
`rapidfuzz` at. We did not regenerate the data to flatter our own results.

---

## Guarantees

- **The holdout batch was never touched during development.** It is read once,
  at the end, behind an explicit `--allow-holdout` flag, and whatever it says is
  published.
- **The audit trail is append-only, enforced by SQLite triggers**, not by
  convention. A correction writes a new record carrying `supersedes`; both
  survive. `UPDATE` and `DELETE` on the decisions table abort.
- **Money is `Decimal` everywhere**, including through JSON and SQLite. No
  float ever touches a rupee.
- **Every threshold lives in [`config.yaml`](config.yaml)**, each carrying the
  measurement that set it. No magic numbers in `rules.py`.
- **The model may only return invoice IDs it was shown.** A fabricated ID
  forces `EXCEPTION` and is logged. Enforced in a pure function, with
  must-not-pass tests that never open a network connection.
- **Reproducible data.** Fixed seeds; `manifest.json` records each batch's.

---

## Repo layout

```
src/ledgerloop/
  candidates.py   Stage 0 — blocking. Pure.
  rules.py        Stage 1 — R1–R7. Pure, no I/O, no globals.
  llm.py          Stage 2a — adjudication (off) + provider clients & guards
  triage.py       Stage 2b — the exception queue writer
  engine.py       Stage 3 — routing, dedup, orchestration
  audit.py        append-only SQLite trail
  evaluate.py     the metrics harness — every number in this README
  generate.py     synthetic batch generator, fixed seeds
app.py            Streamlit reviewer UI (run · results · queue · metrics)
data/             batch_dev · batch_stress · batch_holdout
reports/          every eval run, in order, showing the trajectory
tests/            149 tests — one per rule, plus a must-not-fire case for each
```

---

## Documentation

| | |
|---|---|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | The four-stage design and the rationale behind every decision |
| **[reports/](reports/)** | Every eval run, in order |
| **[config.yaml](config.yaml)** | Every threshold, with the measurement behind it |
