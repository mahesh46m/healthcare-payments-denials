"""Denials & payments analysis: denial rate, Pareto of CARC reasons, payer
scorecard, first-pass acceptance, appeal recovery, days-to-pay.
Writes sample_output.md (a Power BI-style KPI summary).
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "payments.db"


def money(x: float) -> str:
    return f"${x:,.0f}"


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def main() -> None:
    if not DB.exists():
        import generate_data  # noqa: PLC0415 - sibling script

        generate_data.main()
    con = sqlite3.connect(DB)

    (n, billed_total) = con.execute(
        "SELECT COUNT(*), SUM(billed) FROM remittance_lines WHERE submission = 1"
    ).fetchone()
    (n_denied, denied_billed) = con.execute(
        "SELECT COUNT(*), SUM(billed) FROM remittance_lines "
        "WHERE submission = 1 AND denial_code IS NOT NULL").fetchone()
    (paid_total,) = con.execute(
        "SELECT SUM(paid) FROM remittance_lines").fetchone()
    first_pass_rate = 1 - n_denied / n

    by_carc = con.execute(
        "SELECT denial_code, COUNT(*), SUM(billed) FROM remittance_lines "
        "WHERE submission = 1 AND denial_code IS NOT NULL "
        "GROUP BY 1 ORDER BY 2 DESC").fetchall()
    by_payer = con.execute(
        "SELECT payer, COUNT(*), "
        "SUM(CASE WHEN denial_code IS NOT NULL THEN 1 ELSE 0 END), "
        "SUM(billed), SUM(paid), "
        "AVG(julianday(remit_date) - julianday(service_date)) "
        "FROM remittance_lines WHERE submission = 1 GROUP BY 1 ORDER BY 3.0/2 DESC"
    ).fetchall()

    monthly = con.execute(
        "SELECT substr(service_date, 1, 7), COUNT(*), "
        "SUM(CASE WHEN denial_code IS NOT NULL THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN denial_code IS NOT NULL THEN billed ELSE 0 END) "
        "FROM remittance_lines WHERE submission = 1 GROUP BY 1 ORDER BY 1"
    ).fetchall()

    # Root-cause worklist: payer x CARC cells ranked by billed dollars denied.
    worklist = con.execute(
        "SELECT payer, denial_code, COUNT(*), SUM(billed) "
        "FROM remittance_lines WHERE submission = 1 AND denial_code IS NOT NULL "
        "GROUP BY 1, 2 ORDER BY 4 DESC LIMIT 10"
    ).fetchall()

    # Appeals: claims denied on first pass with a later submission.
    (appealed,) = con.execute(
        "SELECT COUNT(DISTINCT claim_id) FROM remittance_lines WHERE submission = 2"
    ).fetchone()
    (appeal_won,) = con.execute(
        "SELECT COUNT(DISTINCT claim_id) FROM remittance_lines "
        "WHERE submission = 2 AND denial_code IS NULL").fetchone()
    (appeal_recovered,) = con.execute(
        "SELECT SUM(paid) FROM remittance_lines WHERE submission = 2").fetchone()
    (days_to_pay,) = con.execute(
        "SELECT AVG(julianday(remit_date) - julianday(service_date)) "
        "FROM remittance_lines WHERE submission = 1 AND denial_code IS NULL"
    ).fetchone()
    con.close()

    out = [
        "# Healthcare payments denials summary (synthetic data)",
        "",
        "Produced by `scripts/run_analysis.py`. All data is synthetic 835-style",
        "remittance service lines; no real payer, provider or patient data.",
        "",
        "## Headline KPIs",
        "",
        "| KPI | Value |",
        "|---|---|",
        f"| First-pass service lines | {n:,} |",
        f"| Billed (first pass) | {money(billed_total)} |",
        f"| First-pass denial rate | **{pct(n_denied / n)}** |",
        f"| First-pass acceptance rate | {pct(first_pass_rate)} |",
        f"| Denied billed at stake | {money(denied_billed)} |",
        f"| Total collected (incl. appeals) | {money(paid_total)} |",
        f"| Avg days service-to-payment (clean lines) | {days_to_pay:.1f} |",
        "",
        "## Denial reasons Pareto (CARC codes)",
        "",
        "| CARC | Lines | Share of denials | Billed denied | Cumulative |",
        "|---|---|---|---|---|",
    ]
    cum = 0.0
    for code, c, b in by_carc:
        cum += c / n_denied
        out.append(f"| {code} | {c} | {pct(c / n_denied)} | {money(b)} | {pct(cum)} |")
    out += [
        "",
        "## Payer scorecard (first pass)",
        "",
        "| Payer | Lines | Denial rate | Billed | Collected first pass | Avg days to pay |",
        "|---|---|---|---|---|---|",
        *[
            f"| {p} | {c} | {pct(d / c)} | {money(b)} | {money(pd)} | {dtp:.1f} |"
            for p, c, d, b, pd, dtp in by_payer
        ],
        "",
        "## Monthly denial trend (first pass, by service month)",
        "",
        "| Month | Lines | Denial rate | Denied billed |",
        "|---|---|---|---|",
        *[
            f"| {m} | {c} | {pct(d / c)} | {money(b)} |"
            for m, c, d, b in monthly
        ],
        "",
        "## Root-cause worklist (top payer x CARC cells)",
        "",
        "Ranked by billed dollars denied. Expected recovery applies the observed",
        "appeal win rate to each cell's denied dollars (an estimate, not a forecast).",
        "",
        "| Payer | CARC | Lines | Denied billed | Expected recovery |",
        "|---|---|---|---|---|",
        *[
            f"| {p} | {cd} | {c} | {money(b)} | {money(b * appeal_won / appealed)} |"
            for p, cd, c, b in worklist
        ],
        "",
        "## Appeals",
        "",
        "| KPI | Value |",
        "|---|---|",
        f"| First-pass denials | {n_denied:,} |",
        f"| Appealed (resubmitted) | {appealed:,} |",
        f"| Appeals won | {appeal_won:,} |",
        f"| Appeal win rate | {pct(appeal_won / appealed)} |",
        f"| Recovered via appeals | {money(appeal_recovered)} |",
        "",
    ]
    (ROOT / "sample_output.md").write_text("\n".join(out) + "\n")
    print("\n".join(out[:24]))


if __name__ == "__main__":
    main()
