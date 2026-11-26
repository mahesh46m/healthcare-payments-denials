"""Generate deterministic synthetic remittance (835-style) service lines.

All data is randomly generated with a fixed seed. It is not based on any
real payer, provider, patient or employer data, and the numbers are not
real-world metrics.

Model: first-pass lines are denied at payer-specific rates with CARC-coded
reasons. A share of denied lines is resubmitted/appealed; some of those are
then paid (recovery).
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

SEED = 31
N_LINES = 5000
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "payments.db"

# payer: (weight, first-pass denial rate)
PAYERS = [
    (0.20, "Aetna", 0.14),
    (0.22, "BCBS", 0.11),
    (0.14, "Cigna", 0.13),
    (0.20, "UnitedHealthcare", 0.17),
    (0.16, "Medicare", 0.07),
    (0.08, "Medicaid", 0.19),
]
# CARC: (weight among denials, code, description)
CARC = [
    (0.18, "16",  "Claim lacks information needed for adjudication"),
    (0.14, "4",   "Procedure code inconsistent with modifier"),
    (0.13, "18",  "Exact duplicate claim/service"),
    (0.11, "96",  "Non-covered charge(s)"),
    (0.10, "197", "Precertification/authorization absent"),
    (0.10, "29",  "Time limit for filing has expired"),
    (0.09, "50",  "Non-covered service (not deemed medical necessity)"),
    (0.08, "204", "Service not licensed for this provider"),
    (0.07, "97",  "Payment included in another service's allowance"),
]
CPTS = ["99213", "99214", "99232", "99285", "70553", "73721", "80053",
        "85025", "93000", "97110", "99203", "99291"]


def pick(rng, table):
    r = rng.random()
    acc = 0.0
    for row in table:
        acc += row[0]
        if r <= acc:
            return row
    return table[-1]


def main() -> None:
    rng = random.Random(SEED)
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "sql" / "schema.sql").read_text())
    con.execute("DELETE FROM remittance_lines")

    base = date(2026, 1, 1)
    lid = 0
    cid = 700000
    denied_queue = []
    for _ in range(N_LINES):
        cid += 1
        lid += 1
        _, payer, deny_rate = pick(rng, PAYERS)
        billed = round(rng.uniform(60, 2400), 2)
        allowed = round(billed * rng.uniform(0.45, 0.85), 2)
        svc = base + timedelta(days=rng.randint(0, 89))
        remit = svc + timedelta(days=rng.randint(7, 30))
        if rng.random() < deny_rate:
            _, code, _ = pick(rng, CARC)
            con.execute(
                "INSERT INTO remittance_lines VALUES (?, ?, 1, ?, ?, ?, NULL, 0, ?, ?, ?)",
                (f"RL{lid:06d}", f"C{cid}", payer, rng.choice(CPTS), billed,
                 code, str(svc), str(remit)),
            )
            denied_queue.append((f"C{cid}", payer, billed, svc, remit))
        else:
            paid = round(allowed * rng.uniform(0.85, 1.0), 2)
            con.execute(
                "INSERT INTO remittance_lines VALUES (?, ?, 1, ?, ?, ?, ?, ?, NULL, ?, ?)",
                (f"RL{lid:06d}", f"C{cid}", payer, rng.choice(CPTS), billed,
                 allowed, paid, str(svc), str(remit)),
            )

    # Appeals: 55% of denied lines are resubmitted; 62% of appeals get paid.
    for claim_id, payer, billed, svc, remit in denied_queue:
        if rng.random() >= 0.55:
            continue
        lid += 1
        appeal_remit = remit + timedelta(days=rng.randint(14, 45))
        allowed = round(billed * rng.uniform(0.45, 0.85), 2)
        if rng.random() < 0.62:
            paid = round(allowed * rng.uniform(0.85, 1.0), 2)
            con.execute(
                "INSERT INTO remittance_lines VALUES (?, ?, 2, ?, ?, ?, ?, ?, NULL, ?, ?)",
                (f"RL{lid:06d}", claim_id, payer, rng.choice(CPTS), billed,
                 allowed, paid, str(svc), str(appeal_remit)),
            )
        else:
            _, code, _ = pick(rng, CARC)
            con.execute(
                "INSERT INTO remittance_lines VALUES (?, ?, 2, ?, ?, ?, NULL, 0, ?, ?, ?)",
                (f"RL{lid:06d}", claim_id, payer, rng.choice(CPTS), billed,
                 code, str(svc), str(appeal_remit)),
            )

    con.commit()
    (n,) = con.execute("SELECT COUNT(*) FROM remittance_lines").fetchone()
    (d,) = con.execute("SELECT COUNT(*) FROM remittance_lines WHERE submission = 1 AND denial_code IS NOT NULL").fetchone()
    con.close()
    print(f"wrote {DB}: {n} lines; {d} first-pass denials")


if __name__ == "__main__":
    main()
