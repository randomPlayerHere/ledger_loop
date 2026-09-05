"""Streamlit reviewer UI.

Four views, and the third one is the reason the others exist. A reconciliation
that only shows you what it matched is a report; one that hands you the
leftovers with a reason attached, and lets you clear them, is a tool somebody
could actually run a month-end on.

Reviewer actions are the same append-only writes the engine makes: accepting a
suggestion does not edit the record that proposed it, it writes a new record
carrying `supersedes` and `decided_by="HUMAN"`. Nothing in this file mutates an
audit record, because nothing anywhere is allowed to.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from ledgerloop.audit import AuditLog
from ledgerloop.config import load_config
from ledgerloop.engine import run_pipeline
from ledgerloop.evaluate import evaluate_matches
from ledgerloop.loaders import load_batch
from ledgerloop.models import MatchDecision

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DB = ROOT / "audit.db"

OUTCOME_COLOUR = {
    "AUTO_MATCHED": "#1b7f3b",
    "NEEDS_REVIEW": "#b8860b",
    "EXCEPTION": "#a33",
}

st.set_page_config(page_title="LedgerLoop", page_icon="🧾", layout="wide")


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

@st.cache_resource
def config():
    return load_config()


@st.cache_data(show_spinner=False)
def run_batch(batch_name: str):
    """Reconcile one batch. Cached so switching tabs does not re-run the engine.

    Returns (effective, history, metrics). `history` is what the audit trail
    stores -- superseded records included -- while `effective` is what the
    tables below show.
    """
    cfg = config()
    batch = load_batch(DATA / f"batch_{batch_name}")
    import time
    t0 = time.perf_counter()
    effective, history = run_pipeline(batch, cfg, use_llm=False)
    elapsed = time.perf_counter() - t0
    metrics = evaluate_matches(DATA / f"batch_{batch_name}" / "truth.json",
                               effective, elapsed_seconds=elapsed)
    return batch, effective, history, metrics


def decisions_frame(batch, decisions) -> pd.DataFrame:
    txns = {t.txn_id: t for t in batch.bank}
    return pd.DataFrame([{
        "txn_id": d.txn_id,
        "date": txns[d.txn_id].value_date,
        "amount": float(txns[d.txn_id].amount),
        "outcome": d.outcome,
        "rule": d.rule_id or "—",
        "by": d.decided_by,
        "confidence": round(d.confidence, 3),
        "matched": ", ".join(d.proposed_invoice_ids) or "—",
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


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

st.sidebar.title("🧾 LedgerLoop")
st.sidebar.caption("Bank statement ↔ ledger reconciliation")

available = sorted(p.name.replace("batch_", "") for p in DATA.glob("batch_*")
                   if p.name != "batch_holdout")
batch_name = st.sidebar.selectbox("Batch", available,
                                  index=available.index("dev") if "dev" in available else 0)
st.sidebar.caption("`batch_holdout` is deliberately absent — it is read once, "
                   "from the CLI, behind an explicit flag.")

batch, decisions, history, metrics = run_batch(batch_name)
df = decisions_frame(batch, decisions)

counts = metrics["outcomes"]
st.sidebar.metric("Auto-matched", counts.get("AUTO_MATCHED", 0))
st.sidebar.metric("Needs review", counts.get("NEEDS_REVIEW", 0))
st.sidebar.metric("Exceptions", counts.get("EXCEPTION", 0))

if "reviews" not in st.session_state:
    st.session_state.reviews = {}

run_tab, results_tab, queue_tab, metrics_tab = st.tabs(
    ["Run", "Results", f"Exception queue ({counts.get('EXCEPTION', 0) + counts.get('NEEDS_REVIEW', 0)})",
     "Metrics"])


# --------------------------------------------------------------------------
# 1 · Run
# --------------------------------------------------------------------------

with run_tab:
    st.header("Run")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", metrics["n_txns"])
    c2.metric("Invoices", len(batch.ledger))
    c3.metric("Auto-match rate", f"{metrics['auto_match_rate']:.1%}")
    c4.metric("Throughput", f"{metrics['throughput_per_min']:,.0f}/min")

    st.progress(metrics["auto_match_rate"],
                text=f"{counts.get('AUTO_MATCHED', 0)} of {metrics['n_txns']} "
                     f"settled without a human")

    st.subheader("Where the money went")
    settled = sum(float(v) for d in decisions for v in d.allocated.values())
    unsettled = sum(float(t.amount) for t in batch.bank
                    if not next(d for d in decisions if d.txn_id == t.txn_id).allocated)
    st.dataframe(pd.DataFrame([
        {"": "Allocated to invoices", "₹": f"{settled:,.2f}"},
        {"": "Unallocated (queued)", "₹": f"{unsettled:,.2f}"},
    ]), hide_index=True, width='stretch')

    st.info("Stage 2 adjudication is **off** — measured at 0.43 link precision "
            "against 0.994 for the rules. The LLM writes the exception queue "
            "instead; run `make eval-llm` to generate those notes.")


# --------------------------------------------------------------------------
# 2 · Results
# --------------------------------------------------------------------------

with results_tab:
    st.header("Results")
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

    st.subheader("Audit record")
    pick = st.selectbox("Transaction", view["txn_id"].tolist() or ["—"])
    trail = [d for d in history if d.txn_id == pick]
    if trail:
        if len(trail) > 1:
            st.caption(f"{len(trail)} records — this transaction was reconsidered. "
                       "Earlier readings are kept, never overwritten.")
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
# 3 · Exception queue  — the view that makes this a product
# --------------------------------------------------------------------------

with queue_tab:
    st.header("Exception queue")
    st.caption("Ordered by money at stake. Accepting or rejecting writes a new "
               "audit record — it never edits the one it supersedes.")

    txns = {t.txn_id: t for t in batch.bank}
    invs = {e.invoice_id: e for e in batch.ledger}
    queue = sorted([d for d in decisions
                    if d.outcome in ("EXCEPTION", "NEEDS_REVIEW")
                    and d.txn_id not in st.session_state.reviews],
                   key=lambda d: txns[d.txn_id].amount, reverse=True)

    done = len(st.session_state.reviews)
    if done:
        st.success(f"{done} item(s) cleared this session. "
                   f"{len(queue)} remaining.")

    exposure = sum(txns[d.txn_id].amount for d in queue)
    st.metric("Unresolved exposure", f"₹{exposure:,.2f}", f"{len(queue)} items")

    for d in queue[:25]:
        t = txns[d.txn_id]
        with st.container(border=True):
            head, act = st.columns([3, 1])
            head.markdown(
                f"**{d.txn_id}** · ₹{t.amount:,.2f} · {t.value_date}  \n"
                f"<span style='color:{OUTCOME_COLOUR[d.outcome]}'>{d.outcome}</span> "
                f"· `{t.narration}`", unsafe_allow_html=True)
            head.caption(d.reasoning)

            options = d.proposed_invoice_ids or d.candidates_considered[:8]
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
                head.caption("No candidate invoice survived blocking — nothing "
                             "in the ledger is close on amount, date or name.")

            note = st.text_input("Reviewer note", key=f"note-{d.txn_id}",
                                 placeholder="optional")
            b1, b2, b3 = st.columns(3)
            if b1.button("✓ Accept", key=f"a-{d.txn_id}", disabled=not choice,
                         width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "ACCEPT", note, [choice], t.amount)
                st.rerun()
            if b2.button("✗ Reject", key=f"r-{d.txn_id}", width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "REJECT", note, [], t.amount)
                st.rerun()
            if b3.button("⊘ Write off", key=f"w-{d.txn_id}", width='stretch'):
                st.session_state.reviews[d.txn_id] = _review_record(
                    d, "WRITE_OFF", note, [], t.amount)
                st.rerun()

    if len(queue) > 25:
        st.caption(f"Showing the 25 largest of {len(queue)}.")

    if st.session_state.reviews:
        st.divider()
        st.subheader("Commit this session's reviews")
        st.caption("Appends the records below to the audit trail. The decisions "
                   "they supersede stay in the database.")
        if st.button("Write to audit trail", type="primary"):
            run_id = f"{batch_name}-review-{datetime.now():%Y%m%d-%H%M%S}"
            with AuditLog(DB) as log:
                log.start_run(run_id, batch_name, n_txns=len(batch.bank),
                              use_llm=False, config_note="reviewer session")
                log.record(history, run_id, batch_name)
                log.record(list(st.session_state.reviews.values()), run_id, batch_name)
            st.success(f"Wrote {len(st.session_state.reviews)} reviewer records "
                       f"to {DB} as run `{run_id}`.")
            st.session_state.reviews = {}


# --------------------------------------------------------------------------
# 4 · Metrics
# --------------------------------------------------------------------------

with metrics_tab:
    st.header("Metrics")
    o, a = metrics["overall"], metrics["auto"]

    rows = [
        ("Auto-match rate", metrics["auto_match_rate"], "≥ 0.80"),
        ("Precision (auto only)", a["precision"], "≥ 0.98"),
        ("Recall (all outcomes)", o["recall"], "≥ 0.93"),
        ("Abstention precision", metrics["abstention_precision"], "≥ 0.70"),
        ("Missed escalation", metrics["missed_escalation_rate"], "≤ 0.02"),
    ]
    st.dataframe(pd.DataFrame([
        {"Metric": n, "Value": f"{v:.3f}", "Target": t,
         "": "pass" if (v >= float(t.split()[1]) if t.startswith("≥")
                        else v <= float(t.split()[1])) else "miss"}
        for n, v, t in rows]), hide_index=True, width='stretch')

    c1, c2 = st.columns(2)
    c1.metric("Correct links", o["tp"])
    c1.metric("False links", o["fp"])
    c2.metric("False-match value", f"₹{metrics['false_match_value']:,.2f}")
    c2.metric("Missed links", o["fn"])

    st.subheader("By difficulty")
    st.dataframe(pd.DataFrame([
        {"difficulty": k, "txns": v["n_txns"], "TP": v["tp"], "FP": v["fp"],
         "FN": v["fn"], "precision": round(v["precision"], 3),
         "recall": round(v["recall"], 3)}
        for k, v in metrics["by_difficulty"].items()]),
        hide_index=True, width='stretch')

    st.subheader("By scenario")
    st.dataframe(pd.DataFrame([
        {"link type": k, "txns": v["n_txns"], "TP": v["tp"], "FP": v["fp"],
         "FN": v["fn"], "precision": round(v["precision"], 3),
         "recall": round(v["recall"], 3)}
        for k, v in metrics["by_link_type"].items()]),
        hide_index=True, width='stretch')

    st.caption("Rules only. LLM adjudication measured at 0.432–0.556 link "
               "precision against 0.994 here, and is switched off — see "
               "ARCHITECTURE.md.")
