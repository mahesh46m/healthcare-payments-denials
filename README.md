# Healthcare Payments: Denials & Appeals Analysis

A portfolio project by **Mahesh M**: denial-rate, CARC-reason Pareto, payer scorecard and appeal-recovery analysis over synthetic 835-style remittance data - the kind of reporting that sits behind healthcare payments operations.

> **Demo project.** All data is synthetic and randomly generated (fixed seed). It is not based on any real payer, provider, patient or employer data, and the numbers are not real-world metrics.

## What it does

1. **Generate** (`scripts/generate_data.py`): 5,000 first-pass remittance service lines across 6 payers (each with its own denial rate) and 9 CARC denial reasons, plus resubmissions: 55% of denied lines are appealed and about 62% of appeals get paid.
2. **Analyze** (`scripts/run_analysis.py`): first-pass denial and acceptance rates, denied dollars at stake, denial-reason Pareto with cumulative share, per-payer scorecard (denial rate, collections, days to pay), and appeal funnel (appealed, won, recovered).

## Headline results (seed 31)

| KPI | Value |
|---|---|
| First-pass denial rate | 13.4% |
| Denied billed at stake | $827,404 |
| Appeal win rate | 57.7% |
| Avg days service-to-payment | 18.4 |

Full tables in [`sample_output.md`](sample_output.md).

## Run it

Requires Python 3.8+ only (built-in `sqlite3`, no installs).

```bash
python scripts/run_analysis.py   # builds payments.db on first run
```

## How I build these projects (AI, used honestly)

I use AI tools as a drafting partner: they help me sketch schemas, SQL and analysis structure quickly. Everything that ships here is then **verified by actually running it** - the numbers above come from executing the code, not from the AI's claims. Synthetic data keeps the whole workflow safe to share. That is how I use AI in my analytics work: fast drafts, machine-checked results, and domain judgment for what the metrics should mean.

## Layout

```
sql/schema.sql             remittance_lines table
scripts/generate_data.py   deterministic synthetic remittances + appeals
scripts/run_analysis.py    KPIs, Pareto, payer scorecard, appeal funnel
```

## Possible extensions

Denial trend by month, root-cause worklists (top CARC x payer cells by recoverable dollars), expected-reimbursement variance (paid vs allowed), and a Power BI dashboard over the same queries.

---
Author: Mahesh M. Released under the MIT License.
