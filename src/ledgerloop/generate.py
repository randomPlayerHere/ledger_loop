"""
Synthetic bank-statement / ledger generator for LedgerLoop.

Design principle: generate FORWARD from ground truth. We pick a payment
scenario first, then emit the ledger row, the bank row, and the truth link
together. The answer key is correct by construction, never inferred.

Usage:
    python -m src.ledgerloop.generate --invoices 500 --seed 42 --out data/batch_dev
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------

STEMS = [
    "Sharma", "Agarwal", "Reddy", "Iyer", "Patel", "Mehta", "Bose", "Nair",
    "Kulkarni", "Chauhan", "Bhatt", "Rastogi", "Malhotra", "Venkat", "Deshmukh",
    "Gokhale", "Sinha", "Trivedi", "Pillai", "Chatterjee",
]
SECTORS = [
    "Textiles", "Logistics", "Traders", "Industries", "Enterprises",
    "Solutions", "Polymers", "Agro", "Steels", "Packaging",
    "Infotech", "Chemicals", "Motors", "Exports", "Distributors",
]
SUFFIXES = ["Pvt Ltd", "LLP", "& Co", "Ltd", ""]
BANKS = ["HDFC", "ICIC", "SBIN", "AXIS", "KKBK", "UTIB", "PUNB", "YESB"]

NARRATION_TEMPLATES = [
    "NEFT/{cp}/{inv}/{bank}",
    "IMPS-{utr}-{cp}",
    "UPI/{utr}/{cp_low}@ok{bank_low}bank",
    "RTGS {bank}{utr} {cp_up}",
    "NEFT-{cp}",
    "BY TRANSFER-{utr}-",
    "CMS/{inv}/{cp}",
    "INB/{utr}/PAYMENT",
]
# Templates that carry no invoice reference at all
NO_REF_TEMPLATES = [
    "NEFT-{cp}",
    "BY TRANSFER-{utr}-",
    "INB/{utr}/PAYMENT",
    "IMPS-{utr}-{cp}",
]
ORPHAN_NARRATIONS = [
    "INT.PD:{utr}",
    "REFUND/{utr}/GATEWAY",
    "NEFT/{cp}/RETURN",
    "CHARGES GST @18%",
    "IMPS-{utr}-UNKNOWN REMITTER",
    "REV-{utr}-FAILED TXN",
]

# scenario -> (share of invoices, difficulty)
SCENARIOS = {
    "CLEAN":               (0.28, "EASY"),
    "LATE":                (0.10, "EASY"),
    "SHORT_PAID_TDS":      (0.10, "MEDIUM"),
    "SHORT_PAID_CHARGES":  (0.08, "MEDIUM"),
    "OVERPAID":            (0.03, "MEDIUM"),
    "DISPUTED":            (0.04, "HARD"),
    "PARTIAL":             (0.08, "HARD"),
    "CONSOLIDATED":        (0.10, "HARD"),
    "NO_REF":              (0.08, "HARD"),
    "DUPLICATE":           (0.02, "HARD"),
    "UNPAID":              (0.09, "EASY"),
}
# Hard-skewed mix, used for the failure demo in the pitch video.
STRESS_SCENARIOS = {
    "CLEAN":               (0.05, "EASY"),
    "LATE":                (0.05, "EASY"),
    "SHORT_PAID_TDS":      (0.10, "MEDIUM"),
    "SHORT_PAID_CHARGES":  (0.10, "MEDIUM"),
    "OVERPAID":            (0.05, "MEDIUM"),
    "DISPUTED":            (0.08, "HARD"),
    "PARTIAL":             (0.16, "HARD"),
    "CONSOLIDATED":        (0.20, "HARD"),
    "NO_REF":              (0.11, "HARD"),
    "DUPLICATE":           (0.05, "HARD"),
    "UNPAID":              (0.05, "EASY"),
}

ORPHAN_SHARE = 0.06  # of total bank lines

TWO_DP = Decimal("0.01")


def money(x) -> Decimal:
    return Decimal(str(x)).quantize(TWO_DP, rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

@dataclass
class Counterparty:
    counterparty_id: str
    name: str
    short: str


@dataclass
class LedgerEntry:
    invoice_id: str
    counterparty: str
    counterparty_id: str
    gross_amount: Decimal
    tds_applicable: bool
    tds_rate: Decimal
    issue_date: date
    due_date: date
    status: str = "OPEN"


@dataclass
class BankTransaction:
    txn_id: str
    value_date: date
    amount: Decimal
    direction: str
    narration: str
    utr: str | None
    balance_after: Decimal = Decimal("0")


@dataclass
class GroundTruthLink:
    txn_id: str
    invoice_ids: list[str]
    link_type: str
    allocated: dict[str, str]
    difficulty: str
    notes: str = ""


# --------------------------------------------------------------------------
# Generator
# --------------------------------------------------------------------------

class Generator:
    def __init__(self, n_invoices: int, seed: int, start: date, days: int,
                 profile: str = "standard"):
        self.rng = random.Random(seed)
        self.scenarios = STRESS_SCENARIOS if profile == "stress" else SCENARIOS
        self.profile = profile
        self.seed = seed
        self.n_invoices = n_invoices
        self.start = start
        self.days = days
        self.counterparties: list[Counterparty] = []
        self.ledger: list[LedgerEntry] = []
        self.bank: list[BankTransaction] = []
        self.truth: list[GroundTruthLink] = []
        self._txn_seq = 0

    # -- helpers ----------------------------------------------------------

    def _next_txn_id(self) -> str:
        self._txn_seq += 1
        return f"BNK-{self._txn_seq:06d}"

    def _utr(self) -> str:
        return f"{self.rng.randint(10**11, 10**12 - 1)}"

    def _corrupt(self, short: str) -> str:
        """Apply realistic narration corruption to a counterparty short name."""
        s = short
        if self.rng.random() < 0.20:  # drop vowels
            s = "".join(c for c in s if c.lower() not in "aeiou" or c == s[0])
        if self.rng.random() < 0.30:  # truncate
            s = s[:12]
        if self.rng.random() < 0.50:
            s = s.upper()
        return s.strip()

    def _narration(self, cp: Counterparty, invoice_id: str | None, utr: str) -> str:
        pool = NO_REF_TEMPLATES if invoice_id is None else NARRATION_TEMPLATES
        tpl = self.rng.choice(pool)
        inv_num = ""
        if invoice_id:
            inv_num = invoice_id
            if self.rng.random() < 0.40:            # strip the INV- prefix
                inv_num = invoice_id.split("-")[1]
            if self.rng.random() < 0.05:            # corrupt a digit -> should escalate
                digits = list(inv_num)
                idx = self.rng.randrange(len(digits))
                if digits[idx].isdigit():
                    digits[idx] = str((int(digits[idx]) + 1) % 10)
                inv_num = "".join(digits)
        bank = self.rng.choice(BANKS)
        short = self._corrupt(cp.short)
        return tpl.format(
            cp=short, cp_low=short.lower().replace(" ", ""), cp_up=short.upper(),
            inv=inv_num, utr=utr, bank=bank, bank_low=bank.lower(),
        )

    def _rand_date(self) -> date:
        return self.start + timedelta(days=self.rng.randrange(self.days))

    # -- build ------------------------------------------------------------

    def build_counterparties(self, n: int = 60) -> None:
        seen: set[str] = set()
        while len(self.counterparties) < n:
            stem = self.rng.choice(STEMS)
            sector = self.rng.choice(SECTORS)
            name = f"{stem} {sector} {self.rng.choice(SUFFIXES)}".strip()
            if name in seen:
                continue
            seen.add(name)
            short = f"{stem[:5]}{sector[:3]}"
            self.counterparties.append(
                Counterparty(f"CP-{len(self.counterparties):03d}", name, short)
            )

    def build_ledger(self) -> None:
        # Real ledgers are Pareto-shaped: a handful of clients drive most of
        # the invoice volume. This also makes consolidated payments form
        # naturally, since they require several open invoices per counterparty.
        n = len(self.counterparties)
        weights = [1.0 / (rank + 1) ** 0.8 for rank in range(n)]
        for i in range(self.n_invoices):
            cp = self.rng.choices(self.counterparties, weights=weights, k=1)[0]
            # log-normal-ish amounts, 2k to 800k
            amt = money(round(self.rng.lognormvariate(10.6, 0.9), 2))
            amt = money(min(max(amt, Decimal("2000")), Decimal("800000")))
            issue = self._rand_date()
            tds = self.rng.random() < 0.35
            rate = Decimal(str(self.rng.choice([0.02, 0.10]))) if tds else Decimal("0")
            self.ledger.append(LedgerEntry(
                invoice_id=f"INV-{1000 + i}",
                counterparty=cp.name,
                counterparty_id=cp.counterparty_id,
                gross_amount=amt,
                tds_applicable=tds,
                tds_rate=rate,
                issue_date=issue,
                due_date=issue + timedelta(days=self.rng.choice([15, 30, 45])),
            ))

    def assign_scenarios(self) -> dict[str, str]:
        """Assign a payment scenario to each invoice per the configured mix."""
        names, weights = zip(*[(k, v[0]) for k, v in self.scenarios.items()])
        picks = self.rng.choices(names, weights=weights, k=len(self.ledger))
        return {inv.invoice_id: s for inv, s in zip(self.ledger, picks)}

    def _cp_by_name(self, name: str) -> Counterparty:
        return next(c for c in self.counterparties if c.name == name)

    def emit(self) -> None:
        scenarios = self.assign_scenarios()
        by_id = {e.invoice_id: e for e in self.ledger}
        consumed: set[str] = set()

        # --- consolidated payments first (they claim multiple invoices) ---
        cons = [i for i, s in scenarios.items() if s == "CONSOLIDATED"]
        by_cp: dict[str, list[str]] = {}
        for inv_id in cons:
            by_cp.setdefault(by_id[inv_id].counterparty_id, []).append(inv_id)

        for cp_id, invs in by_cp.items():
            self.rng.shuffle(invs)
            while len(invs) >= 2:
                k = min(self.rng.randint(2, 4), len(invs))
                group = invs[:k]
                invs = invs[k:]
                entries = [by_id[i] for i in group]
                total = money(sum(e.gross_amount for e in entries))
                latest = max(e.issue_date for e in entries)
                cp = self._cp_by_name(entries[0].counterparty)
                utr = self._utr()
                # consolidated payments usually reference nothing useful
                narration = self._narration(cp, None, utr)
                txn = BankTransaction(
                    self._next_txn_id(),
                    latest + timedelta(days=self.rng.randint(3, 25)),
                    total, "CREDIT", narration, utr,
                )
                self.bank.append(txn)
                self.truth.append(GroundTruthLink(
                    txn.txn_id, group, "CONSOLIDATED",
                    {e.invoice_id: str(e.gross_amount) for e in entries},
                    "HARD", f"{k} invoices settled by one credit",
                ))
                consumed.update(group)

        # --- everything else, invoice by invoice ---
        for inv_id, scenario in scenarios.items():
            if inv_id in consumed:
                continue
            e = by_id[inv_id]
            cp = self._cp_by_name(e.counterparty)

            if scenario in ("UNPAID", "CONSOLIDATED"):
                # CONSOLIDATED leftovers (odd one out) simply go unpaid
                continue

            def make(amount: Decimal, gap_lo: int, gap_hi: int, with_ref: bool = True):
                utr = self._utr()
                narration = self._narration(cp, e.invoice_id if with_ref else None, utr)
                txn = BankTransaction(
                    self._next_txn_id(),
                    e.issue_date + timedelta(days=self.rng.randint(gap_lo, gap_hi)),
                    money(amount), "CREDIT", narration, utr,
                )
                self.bank.append(txn)
                return txn

            g = e.gross_amount
            diff = self.scenarios[scenario][1]

            if scenario == "CLEAN":
                t = make(g, 0, 5)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "CLEAN", {inv_id: str(g)}, diff))

            elif scenario == "LATE":
                t = make(g, 20, 60)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "LATE", {inv_id: str(g)}, diff,
                    "settled well after due date"))

            elif scenario == "SHORT_PAID_TDS":
                rate = e.tds_rate if e.tds_applicable else Decimal("0.10")
                net = money(g - (g * rate))
                t = make(net, 2, 30)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "SHORT_PAID_TDS", {inv_id: str(net)}, diff,
                    f"TDS deducted at {rate}"))

            elif scenario == "SHORT_PAID_CHARGES":
                # real NEFT/RTGS fees are single/double digits plus GST; the old
                # 18-590 band produced "charges" R3 can never explain
                chg = money(self.rng.uniform(5, 60))
                t = make(g - chg, 1, 20)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "SHORT_PAID_CHARGES",
                    {inv_id: str(money(g - chg))}, diff, f"bank charges {chg}"))

            elif scenario == "OVERPAID":
                extra = money(self.rng.uniform(50, 3000))
                t = make(g + extra, 1, 20)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "OVERPAID",
                    {inv_id: str(g)}, diff, f"advance/rounding excess {extra}"))

            elif scenario == "DISPUTED":
                # customer contests part of the bill and never pays the rest.
                # 0.55-0.85 keeps the gap clear of 2%/10% TDS and the charge
                # ceiling, so the shortfall is genuinely unexplainable -- the
                # engine should identify the invoice and refuse to auto-match
                frac = Decimal(str(round(self.rng.uniform(0.55, 0.85), 3)))
                paid = money(g * frac)
                t = make(paid, 1, 30)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "DISPUTED", {inv_id: str(paid)}, diff,
                    f"short by {money(g - paid)} with no explanation; "
                    "the balance never arrives"))

            elif scenario == "PARTIAL":
                frac = Decimal(str(round(self.rng.uniform(0.3, 0.7), 3)))
                first = money(g * frac)
                second = money(g - first)
                t1 = make(first, 1, 15)
                self.truth.append(GroundTruthLink(
                    t1.txn_id, [inv_id], "PARTIAL", {inv_id: str(first)}, diff,
                    "installment 1 of 2"))
                t2 = make(second, 20, 55)
                self.truth.append(GroundTruthLink(
                    t2.txn_id, [inv_id], "PARTIAL", {inv_id: str(second)}, diff,
                    "installment 2 of 2"))

            elif scenario == "NO_REF":
                t = make(g, 2, 30, with_ref=False)
                self.truth.append(GroundTruthLink(
                    t.txn_id, [inv_id], "NO_REF", {inv_id: str(g)}, diff,
                    "amount matches but narration carries no invoice number"))

            elif scenario == "DUPLICATE":
                t1 = make(g, 1, 10)
                self.truth.append(GroundTruthLink(
                    t1.txn_id, [inv_id], "CLEAN", {inv_id: str(g)}, "EASY"))
                # same amount, same day, but only the first one is real
                utr = self._utr()
                t2 = BankTransaction(
                    self._next_txn_id(), t1.value_date, g, "CREDIT",
                    self._narration(cp, e.invoice_id, utr), utr,
                )
                self.bank.append(t2)
                self.truth.append(GroundTruthLink(
                    t2.txn_id, [], "DUPLICATE", {}, "HARD",
                    f"duplicate of {t1.txn_id}; must not be matched again"))

        # --- orphan credits ---
        n_orphans = int(len(self.bank) * ORPHAN_SHARE / (1 - ORPHAN_SHARE))
        for _ in range(n_orphans):
            cp = self.rng.choice(self.counterparties)
            utr = self._utr()
            narration = self.rng.choice(ORPHAN_NARRATIONS).format(
                utr=utr, cp=self._corrupt(cp.short))
            txn = BankTransaction(
                self._next_txn_id(), self._rand_date(),
                money(self.rng.uniform(500, 90000)), "CREDIT", narration, utr,
            )
            self.bank.append(txn)
            self.truth.append(GroundTruthLink(
                txn.txn_id, [], "ORPHAN", {}, "IMPOSSIBLE",
                "no ledger counterpart exists"))

        # --- order by date, renumber, compute running balance ---
        self.bank.sort(key=lambda t: (t.value_date, t.txn_id))
        bal = Decimal("250000")
        for t in self.bank:
            bal = money(bal + t.amount)
            t.balance_after = bal

    # -- output -----------------------------------------------------------

    def write(self, out: Path) -> dict:
        out.mkdir(parents=True, exist_ok=True)

        with (out / "bank.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["txn_id", "value_date", "amount", "direction",
                        "narration", "utr", "balance_after"])
            for t in self.bank:
                w.writerow([t.txn_id, t.value_date.isoformat(), t.amount,
                            t.direction, t.narration, t.utr or "", t.balance_after])

        with (out / "ledger.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["invoice_id", "counterparty", "counterparty_id",
                        "gross_amount", "tds_applicable", "tds_rate",
                        "issue_date", "due_date", "status"])
            for e in self.ledger:
                w.writerow([e.invoice_id, e.counterparty, e.counterparty_id,
                            e.gross_amount, e.tds_applicable, e.tds_rate,
                            e.issue_date.isoformat(), e.due_date.isoformat(),
                            e.status])

        with (out / "truth.json").open("w") as f:
            json.dump([asdict(l) for l in self.truth], f, indent=2)

        # manifest: distribution stats, so the README can quote them
        dist: dict[str, int] = {}
        diff: dict[str, int] = {}
        for l in self.truth:
            dist[l.link_type] = dist.get(l.link_type, 0) + 1
            diff[l.difficulty] = diff.get(l.difficulty, 0) + 1
        manifest = {
            "profile": self.profile,
            "seed": self.seed,          # regenerating the batch needs this
            "n_invoices": len(self.ledger),
            "n_bank_txns": len(self.bank),
            "n_truth_links": len(self.truth),
            "unmatchable": sum(1 for l in self.truth if not l.invoice_ids),
            "link_type_distribution": dist,
            "difficulty_distribution": diff,
        }
        with (out / "manifest.json").open("w") as f:
            json.dump(manifest, f, indent=2)
        return manifest


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--invoices", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--start", type=str, default="2026-05-01")
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--profile", choices=["standard", "stress"], default="standard")
    a = p.parse_args()

    g = Generator(a.invoices, a.seed, date.fromisoformat(a.start), a.days,
                  profile=a.profile)
    g.build_counterparties()
    g.build_ledger()
    g.emit()
    m = g.write(a.out)

    print(f"wrote {a.out}")
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()