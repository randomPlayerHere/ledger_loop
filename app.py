"""Streamlit reviewer UI.

Four views, and the third one is the reason the others exist. A reconciliation
that only shows you what it matched is a report; one that hands you the
leftovers with a reason attached, and lets you clear them, is a tool somebody
could actually run a month-end on.

Two ways in. **Generate** builds a synthetic statement and ledger from a seed,
and because the generator also writes the answer key, that path can show real
accuracy. **Upload** takes a bank.csv and a ledger.csv and runs the same
pipeline over them. Everything works except the accuracy table, which needs an
answer key nobody has for real data. That asymmetry is stated in the UI rather
than papered over: a reconciliation tool that reports a precision figure it
could not have computed is worse than one that reports none.

Reviewer actions are the same append-only writes the engine makes: accepting a
suggestion does not edit the record that proposed it, it writes a new record
carrying `supersedes` and `decided_by="HUMAN"`. Nothing in this file mutates an
audit record, because nothing anywhere is allowed to.
"""

import os
import time
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

import pandas as pd
import streamlit as st

from ledgerloop.audit import AuditLog
from ledgerloop.config import load_config
from ledgerloop.engine import run_pipeline
from ledgerloop.evaluate import evaluate_matches
from ledgerloop.loaders import load_batch
from ledgerloop.llm import ResponseCache
from ledgerloop.models import MatchDecision

ROOT = Path(__file__).parent
DB = ROOT / "audit.db"

# Streamlit Cloud puts dashboard secrets in st.secrets; the clients in llm.py
# read os.environ, because they also run from the CLI where Streamlit does not
# exist. Root-level secrets are documented to reach the environment on their
# own, but this makes the deployment independent of that promise.
for _k in ("NVIDIA_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY"):
    try:
        if _k not in os.environ and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
    except Exception:                      # noqa: BLE001 -- no secrets file at all
        pass

# Kept in step with .streamlit/config.toml, where the same three hues are
# registered as the theme's green/yellow/red. An outcome that reads one colour
# in a table and another in a badge is a small thing that makes a finance screen
# feel untrustworthy.
NAVY = "#0C2651"
BLUE = "#0D94FB"
OUTCOME_COLOUR = {
    "AUTO_MATCHED": "#1B7F3B",
    "NEEDS_REVIEW": "#B8860B",
    "EXCEPTION": "#A33333",
}

# Everything below is the vocabulary this screen assumes. A reviewer or a judge
# meeting the app for the first time should never have to open the source to
# find out what R7_SPLIT is or why 0.998 precision matters more than 0.80
# auto-match. A test asserts every rule the engine can emit appears here.

OUTCOME_MEANING = {
    "AUTO_MATCHED": ("Posted without a human. Confidence at or above 0.95, "
                     "reached only by rules whose measured precision earned it."),
    "NEEDS_REVIEW": ("A match is proposed, but the evidence identifies the "
                     "invoice without identifying the payer. A person confirms."),
    "EXCEPTION": ("Nothing could be explained, so it was escalated on "
                  "purpose. Abstaining is a correct answer here."),
}

RULE_MEANING = {
    "R1_EXACT": "Amount matches one invoice to the paisa, and no other candidate does",
    "R3_TOLERANCE": "Short by exactly TDS (2% or 10%) or by bank charges within ₹50 / 0.5%",
    "R4_SUBSET_SUM": "One credit clearing several of the same customer's invoices at once",
    "R5_UNDERPAID": "Short by an amount nothing explains, so it reads as a part payment",
    "R6_OVERPAID": "Credit exceeds the invoice; the excess is left unallocated",
    "R7_SPLIT": "Two credits that together settle one invoice exactly, an instalment pair",
    "DEDUP": "Same invoice paid twice; the later credit is left unapplied",
    "LLM_ADJUDICATION": "Model's suggestion. Off by default, measured at 0.43 precision",
    "REVIEW_ACCEPT": "A reviewer confirmed this match in the queue",
    "REVIEW_REJECT": "A reviewer rejected the proposal",
    "REVIEW_WRITE_OFF": "A reviewer wrote the difference off",
}

# The generator stamps every planted link with a difficulty band. These are the
# bands, in the generator's own terms, so the table can be read without opening
# generate.py.
DIFFICULTY_MEANING = {
    "EASY": "Amount and invoice number both line up.",
    "MEDIUM": "Off by something with a name: TDS, a bank fee, an advance.",
    "HARD": "The link is real, but the arithmetic does not announce it.",
    "IMPOSSIBLE": "No ledger counterpart exists. Linking nothing is the answer.",
}

# The situation each planted link represents. Written from the payer's side,
# because that is the thing a reviewer is actually reasoning about.
SCENARIO_MEANING = {
    "CLEAN": "Paid in full, on time, invoice number in the narration.",
    "LATE": "Paid in full, 20 to 60 days after the due date.",
    "SHORT_PAID_TDS": "Paid less TDS withheld at the statutory rate.",
    "SHORT_PAID_CHARGES": "Paid less a small bank fee, ₹5 to ₹60, taken in transit.",
    "OVERPAID": "Paid more than the invoice. The excess is an advance.",
    "DISPUTED": "Contested the bill and paid 55 to 85 per cent. No explanation.",
    "PARTIAL": "One invoice settled by two instalments, weeks apart.",
    "CONSOLIDATED": "One credit clearing several invoices at once.",
    "NO_REF": "Amount matches exactly, but no invoice number is quoted.",
    "DUPLICATE": "The same payment arriving twice. Only the first is real.",
    "ORPHAN": "A credit with no invoice behind it.",
}

METRIC_MEANING = {
    "Auto-match rate":
        "Share of the statement settled with no human involved. Coverage.",
    "Precision (auto only)":
        "Of the links posted automatically, how many were right. The number "
        "that must never slip, because a wrong auto-post moves real money.",
    "Recall (all outcomes)":
        "Share of all true invoice links the system found, in any outcome.",
    "Abstention precision":
        "When it gave up, how often the transaction was genuinely hard. "
        "Escalating an easy one wastes a person's time.",
    "Missed escalation":
        "Share of transactions posted automatically against the wrong "
        "invoices. The expensive failure.",
}

_ICON = ROOT / "assets" / "favicon.png"
st.set_page_config(page_title="LedgerLoop", layout="wide",
                   page_icon=str(_ICON) if _ICON.exists() else None,
                   initial_sidebar_state="expanded")

# Top-left of the sidebar, above everything Streamlit puts there. Same file as
# the tab icon, so the browser tab and the app agree on what this product is.
if _ICON.exists():
    st.logo(str(_ICON), size="large")

# The one thing the theme cannot express: a masthead. Everything else -- type,
# radii, the navy sidebar, chart palettes -- is config, not CSS overrides, so
# it survives a Streamlit upgrade.
st.markdown(f"""
<style>
  /* Streamlit's default top padding leaves the masthead floating; this pulls
     the page up so the first thing on screen is the product. */
  [data-testid="stMain"] .block-container {{ padding-top: 2.2rem; max-width: 1400px; }}

  .ll-head {{
      background: linear-gradient(100deg, {NAVY} 0%, #143A72 55%, {BLUE} 135%);
      color: #fff; padding: 1.15rem 1.5rem; border-radius: .6rem;
      margin-bottom: 1.35rem;
  }}
  .ll-head h1 {{
      margin: 0; font-size: 1.4rem; font-weight: 700; color: #fff;
      letter-spacing: -.012em;
  }}
  .ll-head p {{
      margin: .38rem 0 0; color: #C7DAF2; font-size: .855rem; font-weight: 400;
  }}
  .ll-pill {{
      display: inline-block; padding: .16rem .6rem; border-radius: 999px;
      background: rgba(255,255,255,.13); font-size: .735rem; color: #E8EFF9;
      letter-spacing: .01em; margin-right: .3rem; font-weight: 500;
  }}

  /* Scoped to the main pane on purpose: the sidebar is navy, so a navy metric
     value there is invisible against its own background. */
  [data-testid="stMain"] [data-testid="stMetricValue"] {{
      color: {NAVY}; letter-spacing: -.02em;
  }}
  [data-testid="stMain"] [data-testid="stMetricLabel"] p {{
      color: #5A6B85; font-size: .82rem; font-weight: 500;
      text-transform: uppercase; letter-spacing: .05em;
  }}
  [data-testid="stSidebar"] [data-testid="stMetricValue"] {{ color: #FFFFFF; }}
  [data-testid="stSidebar"] [data-testid="stMetricLabel"] p {{
      color: #A9C4E8; font-size: .8rem; font-weight: 500;
      text-transform: uppercase; letter-spacing: .05em;
  }}

  /* st.logo stops at size="large", which renders 30px. This mark is a square
     icon rather than a wordmark, so it needs more height than a wordmark would
     before it reads as a logo. The header grows with it, otherwise the taller
     image overflows onto the first control below. */
  [data-testid="stSidebarLogo"] {{
      height: 3.25rem; width: auto; max-width: none;
  }}
  [data-testid="stSidebarHeader"] {{ min-height: 4.75rem; }}

  h2 {{ letter-spacing: -.015em; }}
  h3 {{ font-size: 1.05rem !important; color: {NAVY}; }}
  [data-testid="stTabs"] button p {{ font-weight: 600; font-size: .93rem; }}
  [data-testid="stSidebar"] hr {{ border-color: #22467A; }}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------

@st.cache_resource
def config():
    return load_config()


@st.cache_data(show_spinner="Generating synthetic batch…")
def generate_batch(n_invoices: int, seed: int, days: int, profile: str,
                   start: str) -> str:
    """Build a batch on disk and return its directory.

    Written out rather than held in memory so the answer key lands beside the
    CSVs exactly as `make data` produces it, so the app scores a generated batch
    through the same `evaluate_matches` path the committed reports use, not a
    parallel one that might disagree with them.
    """
    from ledgerloop.generate import Generator

    out = Path(mkdtemp(prefix="ledgerloop-")) / f"batch_seed{seed}"
    g = Generator(n_invoices, seed, date.fromisoformat(start), days,
                  profile=profile)
    g.build_counterparties()
    g.build_ledger()
    g.emit()
    g.write(out)
    return str(out)


@st.cache_data(show_spinner="Reconciling…")
def reconcile_dir(batch_dir: str, _bust: str = ""):
    """Run the pipeline over a batch directory. Cached on the path."""
    cfg = config()
    d = Path(batch_dir)
    batch = load_batch(d)
    t0 = time.perf_counter()
    effective, history = run_pipeline(batch, cfg, use_llm=False)
    elapsed = time.perf_counter() - t0

    truth = d / "truth.json"
    metrics = (evaluate_matches(truth, effective, elapsed_seconds=elapsed)
               if truth.exists() else None)
    return batch, effective, history, metrics, elapsed


def _save_uploads(bank_file, ledger_file) -> str:
    out = Path(mkdtemp(prefix="ledgerloop-upload-"))
    (out / "bank.csv").write_bytes(bank_file.getvalue())
    (out / "ledger.csv").write_bytes(ledger_file.getvalue())
    return str(out)


def decisions_frame(batch, decisions) -> pd.DataFrame:
    txns = {t.txn_id: t for t in batch.bank}
    return pd.DataFrame([{
        "txn_id": d.txn_id,
        "date": txns[d.txn_id].value_date,
        "amount": float(txns[d.txn_id].amount),
        "outcome": d.outcome,
        "rule": d.rule_id or "-",
        "by": d.decided_by,
        "confidence": round(d.confidence, 3),
        "matched": ", ".join(d.proposed_invoice_ids) or "-",
        "narration": txns[d.txn_id].narration,
        "reasoning": d.reasoning,
    } for d in decisions])


def _review_record(prior: MatchDecision, action: str, note: str,
                   invoice_ids: list[str], amount: Decimal) -> MatchDecision:
    """A reviewer's decision, as a new record superseding the old one."""
    resolved = action == "ACCEPT"
    return MatchDecision(
        decision_id=str(uuid4()),
        txn_id=prior.txn_id,
        proposed_invoice_ids=invoice_ids if resolved else [],
        allocated={invoice_ids[0]: amount} if resolved and invoice_ids else {},
        outcome="AUTO_MATCHED" if resolved else "EXCEPTION",
        confidence=1.0 if resolved else 0.0,
        decided_by="HUMAN",
        rule_id=f"REVIEW_{action}",
        reasoning=note or f"Reviewer marked this {action.lower()}.",
        evidence={"reviewed_at": datetime.now().isoformat(),
                  "superseded_rule": prior.rule_id,
                  "superseded_outcome": prior.outcome,
                  "reviewer_action": action},
        candidates_considered=prior.candidates_considered,
        llm_tokens_in=None, llm_tokens_out=None, latency_ms=0,
        created_at=datetime.now(), supersedes=prior.decision_id,
    )


def _rate(value: float, denominator: int) -> str:
    """Format a rate, or say it is undefined.

    ORPHAN and DUPLICATE rows carry no true links by construction, and neither
    do IMPOSSIBLE transactions. Printing `0.000` in those cells reads as a
    failure when linking nothing was the correct answer, so they say `n/a`
    instead. A genuine zero, where the system did predict something and got it
    wrong, still prints as a zero.
    """
    return f"{value:.3f}" if denominator else "n/a"


def _table_height(n_rows: int) -> int:
    """Tall enough for every row, so the table does not scroll inside itself.

    These breakdowns are read as a whole: a row hidden behind an inner
    scrollbar is a scenario the reader never learns the engine was tested on.
    """
    return (n_rows + 1) * 35 + 3


# --------------------------------------------------------------------------
# Sidebar: choose a source
# --------------------------------------------------------------------------

st.sidebar.markdown("### LedgerLoop")
st.sidebar.caption("Reconciliation control")

source = st.sidebar.radio(
    "Input", ["Generate synthetic", "Upload CSVs"],
    help="Generated batches come with an answer key, so accuracy can be "
         "measured. Uploaded files cannot be scored, because nobody has the "
         "answers for real data.")

batch_dir = None
if source == "Generate synthetic":
    with st.sidebar.form("gen"):
        # 150 rather than 500: the default has to be a size whose exception
        # notes are already cached and committed, so a first-time visitor gets
        # the AI queue instantly and for free. Larger sizes still work; they
        # just cost live calls.
        n_invoices = st.slider("Invoices", 50, 500, 150, step=50)
        seed = st.number_input("Seed", 0, 999_999, 42, step=1,
                               help="Same seed, byte-identical batch.")
        profile = st.selectbox("Profile", ["standard", "stress"])
        days = st.slider("Statement window (days)", 30, 180, 90, step=15)
        start = st.text_input("Start date", "2026-05-01")
        go = st.form_submit_button("Generate & reconcile", type="primary",
                                   width='stretch')
    # Only on the button. Generating on first paint would mean the app opens
    # showing results for parameters nobody chose -- and a reconciliation screen
    # that displays numbers you did not ask it to compute is exactly the wrong
    # first impression for a tool whose whole argument is that it does not
    # assert things it cannot back up.
    if go:
        st.session_state.gen_dir = generate_batch(int(n_invoices), int(seed),
                                                  int(days), profile, start)
        st.session_state.reviews = {}
        st.session_state.notes = {}
    batch_dir = st.session_state.get("gen_dir")

else:
    bank_file = st.sidebar.file_uploader("bank.csv", type="csv")
    ledger_file = st.sidebar.file_uploader("ledger.csv", type="csv")
    st.sidebar.caption(
        "`bank.csv`: txn_id, value_date, amount, direction, narration, utr, "
        "balance_after · `ledger.csv`: invoice_id, counterparty, "
        "counterparty_id, gross_amount, tds_applicable, tds_rate, issue_date, "
        "due_date, status")
    if bank_file and ledger_file:
        key = f"{bank_file.name}-{bank_file.size}-{ledger_file.name}-{ledger_file.size}"
        if st.session_state.get("upload_key") != key:
            st.session_state.upload_key = key
            st.session_state.upload_dir = _save_uploads(bank_file, ledger_file)
            st.session_state.reviews = {}
        batch_dir = st.session_state.upload_dir

MASTHEAD = """
<div class="ll-head">
  <h1>LedgerLoop</h1>
  <p>Bank statement to ledger reconciliation &nbsp;·&nbsp;
     <span class="ll-pill">blocking</span>
     <span class="ll-pill">rules R1-R7</span>
     <span class="ll-pill">LLM triage</span>
     <span class="ll-pill">audit trail</span></p>
</div>
"""

st.markdown(MASTHEAD, unsafe_allow_html=True)

if batch_dir is None:
    if source == "Generate synthetic":
        st.subheader("Ready when you are")
        st.write("Choose a size, a seed and a difficulty profile in the "
                 "sidebar, then select **Generate & reconcile**. The generator "
                 "writes a statement, a ledger and an answer key, so this path "
                 "can report measured accuracy rather than only counts.")
    else:
        st.subheader("Waiting for two files")
        st.write("Upload a **bank.csv** and a **ledger.csv** in the sidebar. "
                 "The pipeline runs identically on real data, but nobody has an "
                 "answer key for a real statement, so accuracy cannot be "
                 "measured on that path.")

    st.divider()

    st.subheader("What this does")
    st.write("Money arrives in the bank. Invoices sit in the ledger. Someone "
             "has to say which paid which, and it is rarely obvious: customers "
             "pay late, pay half, deduct TDS, or clear five bills with one "
             "transfer. LedgerLoop settles what it can prove and queues the "
             "rest with a reason attached.")

    st.caption("HOW A PAYMENT BECOMES A DECISION")
    a, b, c, d = st.columns(4)
    a.markdown("**1 · Narrow it down**  \nAmount, date and name cut 500 "
               "invoices to the 20 worth checking.")
    b.markdown("**2 · Look for a reason**  \nSeven rules ask what explains the "
               "amount. If nothing does, nothing fires.")
    c.markdown("**3 · Write it up**  \nA model notes what the leftover money "
               "probably is and what to do next. It only suggests.")
    d.markdown("**4 · Decide who looks**  \nStrong evidence posts itself, weak "
               "evidence comes to you, the rest is queued. All of it recorded.")
    st.stop()

try:
    batch, decisions, history, metrics, elapsed = reconcile_dir(batch_dir)
except Exception as e:                                  # noqa: BLE001
    st.error(f"Could not read that batch: {e}")
    st.caption("Every column listed in the sidebar must be present. Dates are "
               "ISO (YYYY-MM-DD); amounts are plain decimals with no currency "
               "symbol or thousands separator.")
    st.stop()

df = decisions_frame(batch, decisions)
counts = {"AUTO_MATCHED": 0, "NEEDS_REVIEW": 0, "EXCEPTION": 0}
for d in decisions:
    counts[d.outcome] += 1
scored = metrics is not None

st.session_state.setdefault("reviews", {})
st.session_state.setdefault("notes", {})

st.sidebar.divider()
st.sidebar.metric("Auto-matched", counts["AUTO_MATCHED"])
st.sidebar.metric("Needs review", counts["NEEDS_REVIEW"])
st.sidebar.metric("Exceptions", counts["EXCEPTION"])
if not scored:
    st.sidebar.warning("No answer key, so accuracy cannot be measured for "
                       "uploaded data.")

run_tab, results_tab, queue_tab, metrics_tab = st.tabs(
    ["Run", "Results",
     f"Exception queue ({counts['EXCEPTION'] + counts['NEEDS_REVIEW']})",
     "Metrics"])


# --------------------------------------------------------------------------
# 1 · Run
# --------------------------------------------------------------------------

with run_tab:
    st.header("Run")
    st.caption(f"`{Path(batch_dir).name}` · "
               f"{'generated, answer key available' if scored else 'uploaded, unscored'}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", len(batch.bank))
    c2.metric("Invoices", len(batch.ledger))
    c3.metric("Auto-match rate", f"{counts['AUTO_MATCHED'] / len(batch.bank):.1%}")
    c4.metric("Throughput", f"{len(batch.bank) / elapsed * 60:,.0f}/min")

    st.progress(counts["AUTO_MATCHED"] / len(batch.bank),
                text=f"{counts['AUTO_MATCHED']} of {len(batch.bank)} settled "
                     f"without a human")

    st.subheader("Where the money went")
    allocated = sum((v for d in decisions for v in d.allocated.values()),
                    Decimal("0"))
    by_txn = {t.txn_id: t for t in batch.bank}
    queued = sum((by_txn[d.txn_id].amount for d in decisions
                  if not d.allocated), Decimal("0"))
    st.dataframe(pd.DataFrame([
        {"": "Allocated to invoices", "₹": f"{allocated:,.2f}"},
        {"": "Unallocated (queued for review)", "₹": f"{queued:,.2f}"},
    ]), hide_index=True, width='stretch')

    st.subheader("Which rule did the work")
    st.caption("Each rule answers one question about the money, and abstains "
               "rather than guess when it cannot.")
    fired = df[df["rule"] != "-"]["rule"].value_counts().reset_index()
    fired.columns = ["rule", "transactions"]
    fired["what it matched"] = fired["rule"].map(
        lambda r: RULE_MEANING.get(r, "-"))
    st.dataframe(fired[["rule", "what it matched", "transactions"]],
                 hide_index=True, width='stretch')

    st.info("Stage 2 adjudication is **off**. It measured 0.43 link precision "
            "against 0.994 for the rules. The model writes exception notes "
            "instead; generate them from the Exception queue tab.")


# --------------------------------------------------------------------------
# 2 · Results
# --------------------------------------------------------------------------

with results_tab:
    st.header("Results")
    st.markdown(" &nbsp; ".join(
        f"<span style='color:{OUTCOME_COLOUR[k]};font-weight:600'>■ {k}</span> "
        f"<span style='color:#5A6B85;font-size:.88rem'>{v}</span><br>"
        for k, v in OUTCOME_MEANING.items()), unsafe_allow_html=True)
    st.write("")

    chosen = st.multiselect("Outcome", sorted(df["outcome"].unique()),
                            default=sorted(df["outcome"].unique()))
    search = st.text_input("Search transaction id, invoice or narration", "")

    view = df[df["outcome"].isin(chosen)]
    if search:
        s = search.lower()
        view = view[view.apply(
            lambda r: s in str(r["txn_id"]).lower() or s in str(r["matched"]).lower()
            or s in str(r["narration"]).lower(), axis=1)]

    st.dataframe(
        view.style.map(
            lambda v: f"color: {OUTCOME_COLOUR.get(v, '')}; font-weight: 600",
            subset=["outcome"]),
        hide_index=True, width='stretch', height=420)
    st.download_button("Download results CSV", view.to_csv(index=False),
                       file_name="ledgerloop_results.csv", mime="text/csv")

    st.subheader("Audit record")
    pick = st.selectbox("Transaction", view["txn_id"].tolist() or ["none"])
    trail = [d for d in history if d.txn_id == pick]
    if trail:
        if len(trail) > 1:
            st.caption(f"{len(trail)} records. This transaction was reconsidered, "
                       "and earlier readings are kept rather than "
                       "overwritten.")
        for i, d in enumerate(trail):
            label = "current" if d is trail[-1] else "superseded"
            with st.expander(f"{i + 1}. {d.rule_id or 'no rule'} · {d.outcome} "
                             f"· {label}", expanded=(d is trail[-1])):
                st.write(d.reasoning)
                a, b = st.columns(2)
                a.json({"outcome": d.outcome, "confidence": d.confidence,
                        "decided_by": d.decided_by,
                        "proposed": d.proposed_invoice_ids,
                        "allocated": {k: str(v) for k, v in d.allocated.items()},
                        "latency_ms": d.latency_ms})
                b.json({"evidence": {k: str(v) for k, v in d.evidence.items()},
                        "candidates_considered": d.candidates_considered,
                        "supersedes": d.supersedes})


# --------------------------------------------------------------------------
# 3 · Exception queue: the view that makes this a product
# --------------------------------------------------------------------------

with queue_tab:
    st.header("Exception queue")
    st.caption("Ordered by money at stake. Accepting or rejecting writes a new "
               "audit record; it never edits the one it supersedes.")

    invs = {e.invoice_id: e for e in batch.ledger}
    queue = sorted([d for d in decisions
                    if d.outcome in ("EXCEPTION", "NEEDS_REVIEW")
                    and d.txn_id not in st.session_state.reviews],
                   key=lambda d: by_txn[d.txn_id].amount, reverse=True)

    done = len(st.session_state.reviews)
    if done:
        st.success(f"{done} item(s) cleared this session. {len(queue)} remaining.")

    exposure = sum((by_txn[d.txn_id].amount for d in queue), Decimal("0"))
    a, b = st.columns([2, 3])
    a.metric("Unresolved exposure", f"₹{exposure:,.2f}", f"{len(queue)} items")

    # Triage on demand. Every note is one API call, so the button says what it
    # will spend before it spends it -- an app that quietly bills per page load
    # is not one you leave open during a demo.
    # A public URL plus a button that spends an API quota is somebody else's
    # bill waiting to happen, so the cost is counted before it is incurred:
    # cached items are free and unlimited, live calls are capped per click.
    MAX_LIVE_CALLS = 40

    with b:
        from ledgerloop.triage import Triager

        cache = ResponseCache(Path(config().llm.cache_dir))
        probe = Triager(config(), client=None, cache=None)
        cached = [d for d in queue
                  if cache.get(probe._key(by_txn[d.txn_id], d)) is not None]
        live = [d for d in queue if d not in cached]
        capped = live[:MAX_LIVE_CALLS]

        if not live:
            st.caption(f"All {len(queue)} notes are already cached, so this is "
                       f"free, instant and reproducible from this repo "
                       f"without a key.")
        else:
            st.caption(
                f"{len(cached)} of {len(queue)} notes are cached. Writing the "
                f"rest costs **{len(capped)} live call"
                f"{'s' if len(capped) != 1 else ''}**"
                + (f" (capped from {len(live)})" if len(live) > len(capped) else "")
                + ". Cached results are reused, so a second run is free.")

        if st.button(f"Generate AI notes  ·  {len(cached) + len(capped)} items",
                     disabled=not queue, width='stretch'):
            from ledgerloop.triage import build_triager
            try:
                triager = build_triager(config())
            except (RuntimeError, ValueError) as e:
                st.error(f"{e}")
            else:
                todo = cached + capped
                ledger_map = {e.invoice_id: e for e in batch.ledger}
                bar = st.progress(0.0, text="Triaging…")
                for i, d in enumerate(todo, 1):
                    st.session_state.notes[d.txn_id] = triager.note(
                        by_txn[d.txn_id], d, ledger_map)
                    bar.progress(i / len(todo), text=f"Triaging {i}/{len(todo)}")
                bar.empty()
                st.rerun()

    for d in queue[:25]:
        t = by_txn[d.txn_id]
        note = st.session_state.notes.get(d.txn_id)
        with st.container(border=True):
            head, act = st.columns([3, 1])
            head.markdown(
                f"**{d.txn_id}** · ₹{t.amount:,.2f} · {t.value_date}  \n"
                f"<span style='color:{OUTCOME_COLOUR[d.outcome]}'>{d.outcome}</span> "
                f"· `{t.narration}`", unsafe_allow_html=True)
            head.caption(d.reasoning)

            if note:
                head.info(f"**{note.action}** · {note.summary}\n\n"
                          f"*{note.confidence_note}"
                          + (f" · lead: {note.likely_invoice}" if note.likely_invoice else "")
                          + f" · note by {note.written_by}*")

            options = d.proposed_invoice_ids or d.candidates_considered[:8]
            if note and note.likely_invoice in options:
                options = [note.likely_invoice] + [o for o in options
                                                   if o != note.likely_invoice]
            if options:
                choice = act.selectbox("Invoice", options, key=f"sel-{d.txn_id}",
                                       label_visibility="collapsed")
                rows = [{"invoice": i,
                         "counterparty": invs[i].counterparty,
                         "gross": f"₹{invs[i].gross_amount:,.2f}",
                         "difference": f"₹{t.amount - invs[i].gross_amount:,.2f}",
                         "status": invs[i].status}
                        for i in options if i in invs]
                if rows:
                    head.dataframe(pd.DataFrame(rows), hide_index=True,
                                   width='stretch')
            else:
                choice = None
                head.caption("No candidate invoice survived blocking. Nothing in "
                             "the ledger is close on amount, date or name.")

            reviewer_note = st.text_input("Reviewer note", key=f"note-{d.txn_id}",
                                          placeholder="optional")
            b1, b2, b3 = st.columns(3)
            if b1.button("Accept", key=f"a-{d.txn_id}", disabled=not choice,
                         width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "ACCEPT", reviewer_note, [choice], t.amount)
                st.rerun()
            if b2.button("Reject", key=f"r-{d.txn_id}", width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "REJECT", reviewer_note, [], t.amount)
                st.rerun()
            if b3.button("Write off", key=f"w-{d.txn_id}", width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "WRITE_OFF", reviewer_note, [], t.amount)
                st.rerun()

    if len(queue) > 25:
        st.caption(f"Showing the 25 largest of {len(queue)}.")

    if st.session_state.reviews:
        st.divider()
        st.subheader("Commit this session's reviews")
        st.caption("Appends the records below to the audit trail. The decisions "
                   "they supersede stay in the database.")
        if st.button("Write to audit trail", type="primary"):
            run_id = f"ui-{datetime.now():%Y%m%d-%H%M%S}"
            name = Path(batch_dir).name
            with AuditLog(DB) as log:
                log.start_run(run_id, name, n_txns=len(batch.bank),
                              use_llm=False, config_note="reviewer session")
                log.record(history, run_id, name)
                log.record(list(st.session_state.reviews.values()), run_id, name)
            n_written = len(st.session_state.reviews)
            st.success(f"Wrote {n_written} reviewer record"
                       f"{'' if n_written == 1 else 's'} to the audit trail "
                       f"as run `{run_id}`.")
            st.session_state.reviews = {}


# --------------------------------------------------------------------------
# 4 · Metrics
# --------------------------------------------------------------------------

with metrics_tab:
    st.header("Metrics")

    if not scored:
        st.warning("**This batch has no answer key, so accuracy cannot be "
                   "measured.** Precision and recall are comparisons against "
                   "known-correct links, and nobody has those for real bank "
                   "data, which is the whole reason reconciliation is a job. "
                   "Switch to **Generate synthetic** in the sidebar for a batch "
                   "that ships with one.")
        st.subheader("Operational summary")
        st.dataframe(pd.DataFrame([
            {"Measure": "Transactions", "Value": f"{len(batch.bank):,}"},
            {"Measure": "Invoices in ledger", "Value": f"{len(batch.ledger):,}"},
            {"Measure": "Settled without a human",
             "Value": f"{counts['AUTO_MATCHED']:,} "
                      f"({counts['AUTO_MATCHED'] / len(batch.bank):.1%})"},
            {"Measure": "Queued for review",
             "Value": f"{counts['EXCEPTION'] + counts['NEEDS_REVIEW']:,}"},
            {"Measure": "Value allocated", "Value": f"₹{allocated:,.2f}"},
            {"Measure": "Value queued", "Value": f"₹{queued:,.2f}"},
            {"Measure": "Throughput",
             "Value": f"{len(batch.bank) / elapsed * 60:,.0f} txns/min"},
        ]), hide_index=True, width='stretch')
    else:
        o, a = metrics["overall"], metrics["auto"]
        rows = [
            ("Auto-match rate", metrics["auto_match_rate"]),
            ("Precision (auto only)", a["precision"]),
            ("Recall (all outcomes)", o["recall"]),
            ("Abstention precision", metrics["abstention_precision"]),
            ("Missed escalation", metrics["missed_escalation_rate"]),
        ]
        st.caption("Accuracy is measured per **link**, meaning one "
                   "(transaction, invoice) pair, because a single payment can "
                   "settle several invoices. Scoring per transaction would "
                   "hide a consolidated payment that got 2 of 3 right. Rates are per "
                   "transaction, because those answer \"how much human work did "
                   "we avoid\".")
        # No target column here on purpose. The project's targets were set for
        # the 520-transaction committed batches and are reported against them in
        # reports/; pinning them to whatever size and seed a visitor happens to
        # generate would compare a number to a bar it was never set for, and
        # print "miss" beside a perfectly good result.
        st.dataframe(pd.DataFrame([
            {"Metric": n, "Value": f"{v:.3f}", "What it means": METRIC_MEANING[n]}
            for n, v in rows]), hide_index=True, width='stretch')

        c1, c2 = st.columns(2)
        c1.metric("Correct links", o["tp"],
                  help="Transaction-to-invoice links the system drew that the "
                       "answer key agrees with.")
        c1.metric("False links", o["fp"],
                  help="Links drawn that the answer key does not contain. Any "
                       "of these sitting in NEEDS_REVIEW cost a reviewer a "
                       "rejection; in AUTO_MATCHED they would cost money.")
        c2.metric("False-match value", f"₹{metrics['false_match_value']:,.2f}",
                  help="Rupees that would have been posted to the wrong "
                       "invoice. Zero means every wrong link allocated nothing.")
        c2.metric("Missed links", o["fn"],
                  help="True links the system never found, usually because it "
                       "abstained. That is the cheap failure.")

        st.subheader("By difficulty")
        st.caption("The generator stamps every link it plants with how hard it "
                   "meant that link to be, so this table separates the payments "
                   "anyone could match from the ones that are the actual job. "
                   "**TP** is a link drawn that the answer key agrees with, "
                   "**FP** one it does not contain, **FN** a true link never "
                   "found. Expect recall to fall as you read down the table; if "
                   "it does not, the difficulty labels are wrong, not the engine.")
        # The counts are two digits wide; the description is a sentence. Left to
        # share the width evenly, Streamlit truncates the sentence mid-word.
        _counts = {c: st.column_config.Column(width="small")
                   for c in ("txns", "TP", "FP", "FN", "precision", "recall")}

        st.dataframe(pd.DataFrame([
            {"difficulty": k,
             "what this band is": DIFFICULTY_MEANING.get(k, ""),
             "txns": v["n_txns"], "TP": v["tp"], "FP": v["fp"], "FN": v["fn"],
             "precision": _rate(v["precision"], v["tp"] + v["fp"]),
             "recall": _rate(v["recall"], v["tp"] + v["fn"])}
            for k, v in metrics["by_difficulty"].items()]),
            hide_index=True, width='stretch',
            height=_table_height(len(metrics["by_difficulty"])),
            column_config={"difficulty": st.column_config.Column(width="small"),
                           "what this band is": st.column_config.Column(width="large"),
                           **_counts})

        st.subheader("By scenario")
        st.caption("The same links, cut by the situation that produced them. "
                   "This is the table that says *where* the missing recall "
                   "lives, and it is never spread evenly. Two things to read "
                   "carefully: **TP can exceed txns**, because one consolidated "
                   "credit settles several invoices and each is its own link; "
                   "and **ORPHAN and DUPLICATE have no true links at all**, so "
                   "their rates show `n/a` rather than a zero. On those rows the "
                   "only way to score well is to link nothing, and a number in "
                   "the FP column is the failure to watch.")
        st.dataframe(pd.DataFrame([
            {"link type": k,
             "what the payer did": SCENARIO_MEANING.get(k, ""),
             "txns": v["n_txns"], "TP": v["tp"], "FP": v["fp"], "FN": v["fn"],
             "precision": _rate(v["precision"], v["tp"] + v["fp"]),
             "recall": _rate(v["recall"], v["tp"] + v["fn"])}
            for k, v in metrics["by_link_type"].items()]),
            hide_index=True, width='stretch',
            height=_table_height(len(metrics["by_link_type"])),
            column_config={"link type": st.column_config.Column(width="medium"),
                           "what the payer did": st.column_config.Column(width="large"),
                           **_counts})

        st.caption("Rules only. LLM adjudication measured 0.432 to 0.556 link "
                   "precision against 0.994 here, and is switched off. "
                   "See ARCHITECTURE.md.")
