# Architecture

## The pipeline

```
 bank.csv (520 credits)          ledger.csv (500 invoices)
        │                                 │
        └────────────┬────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 0 · BLOCKING                    candidates.py │
   │ 500 invoices ─▶ ≤20 per transaction                 │
   │ two independent shortlists:                         │
   │   single   amount window · date window · name score │
   │   grouped  subsets of 2-4 invoices summing exactly  │
   └─────────────────────────────────────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 1 · DETERMINISTIC RULES              rules.py │
   │ per transaction, first match wins, pure functions   │
   │   R1  exactly one candidate matches to the paisa    │
   │   R4  a subset of invoices sums to the credit       │
   │   R3  shortfall = TDS 2%/10%, or bank charges       │
   │   R6  credit exceeds gross, excess left unapplied   │
   │   R5  short by an amount nothing explains           │
   │ batch pass, after the per-transaction rules:        │
   │   R7  two credits summing to one invoice gross      │
   │       ← 20% of the batch; no single-line rule can   │
   │         see it, so it is handed the whole statement │
   └─────────────────────────────────────────────────────┘
                     ▼  what no rule could explain
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 2 · LLM                        llm.py         │
   │   2a  adjudication   ── OFF, measured at 0.43       │
   │       precision vs 0.994 for rules. Code, guards    │
   │       and tests retained; `llm.adjudicate` flips it │
   │   2b  triage         ── ON            triage.py     │
   │       writes the exception queue. Proposes no       │
   │       links, so it cannot move any accuracy metric  │
   └─────────────────────────────────────────────────────┘
                     ▼
   ┌─────────────────────────────────────────────────────┐
   │ STAGE 3 · ROUTING & AUDIT           engine.py       │
   │   confidence ≥ 0.95  ─▶ AUTO_MATCHED                │
   │   confidence ≥ 0.50  ─▶ NEEDS_REVIEW                │
   │   otherwise          ─▶ EXCEPTION                   │
   │   dedup pass: one invoice paid twice is superseded  │
   └──────────┬──────────────────────────┬───────────────┘
              ▼                          ▼
    reports/eval_*.md            audit.db  (append-only)
    reports/exceptions_*.md      every decision ever made,
                                 superseded ones included
```

## Design decisions

### Why the rules run before the model, and mostly instead of it

We built Stage 2a as designed, ran it over `batch_dev`, and scored every answer
against the key. It reached **0.432** link precision (Groq `gpt-oss-120b`) and
**0.556** (NVIDIA `nemotron-3-super-120b`) against **0.994** for the
deterministic rules. Its self-reported confidence carried no usable signal:
both models claim ≥0.95 on nearly every answer, and precision inside that
bucket is 0.404.

So the model does not pick invoices here. It is not a limitation we are
apologising for — it is the measurement that shaped the architecture, and the
flag and the code to reproduce it are both in the repo.

The failure is structural rather than promptable. We hand the model twelve
near-identical invoices and ask "which one?" when the answer is frequently
*none of them*, and models pick rather than abstain. And the discriminating
evidence in reconciliation is arithmetic — exact sums, statutory TDS rates —
not language.

### Where the model does earn its place

Triage. Every unresolved credit gets a note saying what the money probably is,
what makes it unresolvable, and which of eight actions a reviewer should take.
That is reading comprehension over a mess of amounts, dates and half-legible
narrations, which is the half of this problem a model is genuinely better at
than a rule.

The safety property is structural, not a guard we had to write: triage
proposes no invoice links and mutates no decision, so the reconciliation is
byte-identical with triage on or off.

### Stage 0 keeps two shortlists, not one

A member of a consolidated payment is invisible to the single-invoice gate by
construction — ₹19,331 against a ₹58,762 credit looks wrong on every axis. The
group path searches per counterparty, which is both the business rule and what
makes the subset search affordable.

### R7 is the only rule handed the whole batch

An instalment is unidentifiable alone: ₹36,483.19 against a ₹69,359.68 invoice
is not the gross, not the gross less TDS, not a subset of anything. What
identifies it is a property of the *pair*. R7 searches only what Stage 1 left
unexplained, and abstains whenever two different pairings would work.

It also *completes* pairs rather than only creating them: often one half is
identifiable (R5 recognises the counterparty) while its sibling names nobody.
A member already matched to the same invoice is treated as corroboration; a
member matched to a *different* invoice is a contradiction, and the pair is
dropped.

### Confidence is measured, not chosen

Every value in `config.yaml`'s `confidence:` block is set from the precision
that tier actually measured on `batch_dev`, then placed deliberately either
side of the auto-match line. A tier scoring below the bar is a statement that a
human should look, not an accident of arithmetic. A test asserts no value sits
in the dead zone within 0.02 of the threshold, where a two-decimal edit would
silently flip a rule's outcome.

The LLM is capped at `confidence_ceiling: 0.94` — below `auto_match` — so no
model-authored answer can post unattended, whatever it claims about itself.

### The audit trail is append-only, enforced by the database

Nothing is ever updated or deleted. A correction writes a *new* record carrying
`supersedes`, and both survive. SQLite triggers abort any `UPDATE` or `DELETE`
on the decisions table, so the guarantee is a property of the schema rather
than a habit of the code.

This is what lets the system answer "why is this credit posted against
INV-1042" with the whole history: that R5 first read it as a part payment at
0.72, that R7 later found its sibling instalment and superseded that reading at
0.96, and what evidence each of them had.

Money and dates are stored as TEXT. SQLite would take a `Decimal` as a float
and hand back `41249.999999999993`; the storage layer is not where the
no-float-for-money rule gets quietly broken.

### Guards on the model, all enforced in pure functions

Testable without a network connection, and each has a must-not-pass test:

- **It may only return invoice ids it was shown** — validated against the exact
  shortlist that went into the prompt, not the wider blocking list. A
  fabricated id forces `EXCEPTION` and is logged as a hallucination.
- **It may not invent money** — allocations must be positive, name exactly the
  invoices selected, and sum to no more than the credit.
- **It may not certify itself** — confidence capped below the posting line.
- **It may not be guessed on behalf of** — a timeout or API failure is an
  `EXCEPTION`, never a fallback answer.
- **A setup failure stops the run** — a rejected key or exhausted quota fails
  identically for every transaction, so it raises rather than writing hundreds
  of fabricated exceptions and a report that looks like a hard day's work.

### Provider independence

`llm.provider` selects between NVIDIA NIM, Groq and Anthropic behind a
two-method client interface. Swapping models is a config edit, which is what
made the measured comparison between providers affordable in the first place.

## Module map

| module | role | pure? |
|---|---|---|
| `models.py` | pydantic schemas crossing every boundary | — |
| `config.py` | typed `config.yaml` loader; the only reader | — |
| `loaders.py` | CSV → models; cannot read `truth.json` | — |
| `candidates.py` | Stage 0, both shortlists | yes |
| `rules.py` | Stage 1, R1–R7 | yes |
| `llm.py` | Stage 2a: prompt, guards, cache, clients | prompt + validation pure |
| `triage.py` | Stage 2b: exception queue notes | prompt + parsing pure |
| `engine.py` | orchestration, routing, batch passes | no — owns clock and ids |
| `audit.py` | append-only SQLite trail | no |
| `evaluate.py` | scoring and reports; never calls the engine | yes |
| `utils/` | `amounts`, `dates`, `narration` | yes |
