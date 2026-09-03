"""Where exactly are the unreachable links lost, and which knob rescues them?

Loss causes, and the fix each one implies:
  DATE     _date_ok rejected it            -> widen date_back_days / date_fwd_days
  AMOUNT   _amount_ok rejected it          -> conditional floor (1.1)
  NAME     passed filters, failed the      -> lower name_min, or better name_score
           shortlist gate (no ref, no
           explainable shortfall, weak name)
  EVICTED  passed everything, fell         -> raise max_candidates / fix _score (1.3)
           outside max_candidates

Run from the repo root:  .venv/bin/python ceiling.py
Writes reports/ceiling_dev.json and prints the delta against the previous run.
"""
import json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "src")
from ledgerloop.config import load_config
from ledgerloop.loaders import load_batch
from ledgerloop.candidates import _amount_ok, _date_ok, _score, generate_candidates
from ledgerloop.utils.amounts import explain_shortfall
from ledgerloop.utils.narration import extract_refs, name_score

cfg = load_config()
b, tol = cfg.blocking, cfg.tolerances
batch = load_batch(Path("data/batch_dev"))
truth = json.load(Path("data/batch_dev/truth.json").open())
by_txn = {t.txn_id: t for t in batch.bank}
inv_by = {i.invoice_id: i for i in batch.ledger}

SNAPSHOT = Path("reports/ceiling_dev.json")

# what a "strong" name would have to be for the 1.1 corroborated floor to rescue
# an amount-rejected link. Sizes the fix before you write it.
NAME_STRONG_PROBE = 75.0

# below this, a name is noise rather than a weak signal
NAME_FLOOR = 50.0


def has_signal(txn, inv, refs) -> bool:
    """Is there ANY handle on this pairing, ignoring every threshold?

    A link with no ref, no usable name, and an amount that needs an
    unexplainable delta cannot be blocked for at any setting -- widening the
    gate only buys noise. These are the honest exceptions, and they set the
    real ceiling. See invariant 5: abstention is correct behaviour.
    """
    if inv.invoice_id.split("-")[-1] in refs:
        return True
    if name_score(txn.narration, inv.counterparty) >= NAME_FLOOR:
        return True
    return explain_shortfall(txn.amount, inv.gross_amount, tol) is not None


def survivors(txn):
    """Mirror of generate_candidates, but reports *why* each invoice was dropped.

    Returns (scored_pool, capped_ids, reason_by_invoice_id).
    scored_pool is everything that passed the gate, best-first, before the cut.
    """
    refs = extract_refs(txn.narration, txn.utr, b.max_ref_digits)
    keep, reason = [], {}
    for inv in batch.ledger:
        ref_hit = inv.invoice_id.split("-")[-1] in refs
        ns = name_score(txn.narration, inv.counterparty)
        if not ref_hit:
            if not _date_ok(txn, inv, b):
                reason[inv.invoice_id] = ("DATE", ns)
                continue
            if not _amount_ok(txn, inv, b):
                reason[inv.invoice_id] = ("AMOUNT", ns)
                continue
        sf = explain_shortfall(txn.amount, inv.gross_amount, tol)
        if not ref_hit and sf is None and ns < b.name_min:
            reason[inv.invoice_id] = ("NAME", ns)
            continue
        keep.append((_score(txn, inv, ns, ref_hit, sf), inv.invoice_id))
    keep.sort(key=lambda p: p[0], reverse=True)
    return [i for _, i in keep], [i for _, i in keep[: b.max_candidates]], reason


REASONS = ("EVICTED", "DATE", "AMOUNT", "NAME")


def blank():
    d = {"links": 0, "found": 0, "txns": 0, "whole": 0, "nosig": 0}
    d.update({r: 0 for r in REASONS})
    return d


stat = defaultdict(blank)
pool, rescuable, drift = [], [], []

for t in truth:
    if not t["invoice_ids"]:
        continue
    txn = by_txn[t["txn_id"]]
    passed, capped, reason = survivors(txn)
    pool.append(len(passed))

    # drift guard: this script must agree with the real blocking path, or every
    # number below is a lie. Compare against generate_candidates itself.
    real = [c.invoice.invoice_id for c in generate_candidates(txn, batch.ledger, cfg)]
    if real != capped:
        drift.append(t["txn_id"])

    refs = extract_refs(txn.narration, txn.utr, b.max_ref_digits)
    s = stat[t["link_type"]]
    s["txns"] += 1
    hits = 0
    for inv in t["invoice_ids"]:
        s["links"] += 1
        if not has_signal(txn, inv_by[inv], refs):
            s["nosig"] += 1
        if inv in capped:
            s["found"] += 1
            hits += 1
        elif inv in passed:
            s["EVICTED"] += 1
        else:
            why, ns = reason[inv]
            s[why] += 1
            if why == "AMOUNT" and ns >= NAME_STRONG_PROBE:
                rescuable.append((t["link_type"], inv, ns,
                                  float(txn.amount / next(
                                      i.gross_amount for i in batch.ledger
                                      if i.invoice_id == inv))))
    # a CONSOLIDATED link is worthless unless *every* invoice is reachable
    if hits == len(t["invoice_ids"]):
        s["whole"] += 1

hdr = (f"{'link_type':<20} {'links':>6} {'found':>6} {'EVICT':>6} {'DATE':>5} "
       f"{'AMT':>5} {'NAME':>5} {'recall':>7} {'whole':>7} {'NOSIG':>6} {'max':>6}")
print(hdr)
print("-" * len(hdr))
tot = defaultdict(int)
for lt in sorted(stat):
    s = stat[lt]
    for k in ("links", "found", "txns", "whole", "nosig", *REASONS):
        tot[k] += s[k]
    print(f"{lt:<20} {s['links']:>6} {s['found']:>6} {s['EVICTED']:>6} "
          f"{s['DATE']:>5} {s['AMOUNT']:>5} {s['NAME']:>5} "
          f"{s['found']/s['links']:>7.3f} {s['whole']/s['txns']:>7.3f} "
          f"{s['nosig']:>6} {1 - s['nosig']/s['links']:>6.3f}")
print("-" * len(hdr))
print(f"{'TOTAL':<20} {tot['links']:>6} {tot['found']:>6} {tot['EVICTED']:>6} "
      f"{tot['DATE']:>5} {tot['AMOUNT']:>5} {tot['NAME']:>5} "
      f"{tot['found']/tot['links']:>7.3f} {tot['whole']/tot['txns']:>7.3f} "
      f"{tot['nosig']:>6} {1 - tot['nosig']/tot['links']:>6.3f}")

recall = tot["found"] / tot["links"]
whole = tot["whole"] / tot["txns"]
achievable = 1 - tot["nosig"] / tot["links"]
print(f"\nunreachable links: {tot['links'] - tot['found']}"
      f"   (EVICTED {tot['EVICTED']} at max_candidates={b.max_candidates}"
      f" | DATE {tot['DATE']} | AMOUNT {tot['AMOUNT']} | NAME {tot['NAME']})")
print(f"recall  (per invoice) {recall:.3f}")
print(f"recall  (whole link)  {whole:.3f}   <- the number a rule can actually act on")
print(f"ACHIEVABLE ceiling    {achievable:.3f}   "
      f"({tot['nosig']} links have no ref, no name >= {NAME_FLOOR:.0f}, and an "
      f"unexplainable delta")
print(f"                       -> nothing can block for them; they are honest "
      f"EXCEPTIONs, not misses)")
print(f"gap to close          {achievable - recall:+.3f}   "
      f"= {int(round((achievable - recall) * tot['links']))} rescuable links")
print(f"avg invoices passing the gate per txn: {sum(pool)/len(pool):.1f}"
      f"  max {max(pool)}  (cap is {b.max_candidates})")

if rescuable:
    ratios = sorted(r for *_, r in rescuable)
    print(f"\n1.1 sizing: {len(rescuable)} AMOUNT-rejected links have "
          f"name_similarity >= {NAME_STRONG_PROBE:.0f}")
    print(f"            paid/gross ratio spans {ratios[0]:.2f} .. {ratios[-1]:.2f}"
          f"  -> amount_lo_corroborated must sit below {ratios[0]:.2f}")
    seen = defaultdict(int)
    for lt, *_ in rescuable:
        seen[lt] += 1
    print("            by type: " + ", ".join(f"{k} {v}" for k, v in sorted(seen.items())))

if drift:
    print(f"\n!! DRIFT: this script disagrees with generate_candidates on "
          f"{len(drift)} txns (e.g. {drift[0]}). Numbers above are stale.")

# --- snapshot + delta -------------------------------------------------------
now = {"recall": recall, "whole": whole, "achievable": achievable,
       "by_type": {lt: s["found"] / s["links"] for lt, s in stat.items()},
       "losses": {r: tot[r] for r in REASONS}, "nosig": tot["nosig"]}
if SNAPSHOT.exists():
    prev = json.loads(SNAPSHOT.read_text())
    d = now["recall"] - prev["recall"]
    print(f"\nvs last run: recall {prev['recall']:.3f} -> {now['recall']:.3f} "
          f"({d:+.3f})   whole {prev['whole']:.3f} -> {now['whole']:.3f}")
    for lt in sorted(now["by_type"]):
        old, new = prev["by_type"].get(lt), now["by_type"][lt]
        if old is not None and abs(new - old) > 1e-9:
            print(f"    {lt:<20} {old:.3f} -> {new:.3f} ({new - old:+.3f})")
SNAPSHOT.parent.mkdir(exist_ok=True)
SNAPSHOT.write_text(json.dumps(now, indent=2))
