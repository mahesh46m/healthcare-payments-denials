# Healthcare payments denials summary (synthetic data)

Produced by `scripts/run_analysis.py`. All data is synthetic 835-style
remittance service lines; no real payer, provider or patient data.

## Headline KPIs

| KPI | Value |
|---|---|
| First-pass service lines | 5,000 |
| Billed (first pass) | $6,121,129 |
| First-pass denial rate | **13.4%** |
| First-pass acceptance rate | 86.6% |
| Denied billed at stake | $827,404 |
| Total collected (incl. appeals) | $3,364,457 |
| Avg days service-to-payment (clean lines) | 18.4 |

## Denial reasons Pareto (CARC codes)

| CARC | Lines | Share of denials | Billed denied | Cumulative |
|---|---|---|---|---|
| 16 | 138 | 20.6% | $176,155 | 20.6% |
| 4 | 84 | 12.6% | $102,059 | 33.2% |
| 18 | 83 | 12.4% | $105,577 | 45.6% |
| 197 | 69 | 10.3% | $94,357 | 55.9% |
| 96 | 64 | 9.6% | $74,444 | 65.5% |
| 29 | 64 | 9.6% | $74,300 | 75.0% |
| 204 | 63 | 9.4% | $72,176 | 84.5% |
| 50 | 56 | 8.4% | $68,813 | 92.8% |
| 97 | 48 | 7.2% | $59,524 | 100.0% |

## Payer scorecard (first pass)

| Payer | Lines | Denial rate | Billed | Collected first pass | Avg days to pay |
|---|---|---|---|---|---|
| UnitedHealthcare | 976 | 16.2% | $1,195,364 | $599,484 | 18.1 |
| Medicare | 757 | 6.6% | $925,453 | $521,753 | 18.6 |
| Medicaid | 394 | 18.0% | $489,106 | $244,679 | 18.0 |
| Cigna | 757 | 13.1% | $913,271 | $480,784 | 18.6 |
| BCBS | 1112 | 12.4% | $1,388,794 | $735,183 | 18.6 |
| Aetna | 1004 | 15.2% | $1,209,141 | $624,483 | 18.7 |

## Monthly denial trend (first pass, by service month)

| Month | Lines | Denial rate | Denied billed |
|---|---|---|---|
| 2026-01 | 867 | 13.7% | $146,511 |
| 2026-02 | 805 | 15.0% | $151,825 |
| 2026-03 | 927 | 13.5% | $164,409 |
| 2026-04 | 804 | 12.3% | $117,135 |
| 2026-05 | 809 | 13.6% | $135,771 |
| 2026-06 | 788 | 12.1% | $111,753 |

## Root-cause worklist (top payer x CARC cells)

Ranked by billed dollars denied. Expected recovery applies the observed
appeal win rate to each cell's denied dollars (an estimate, not a forecast).

| Payer | CARC | Lines | Denied billed | Expected recovery |
|---|---|---|---|---|
| UnitedHealthcare | 16 | 42 | $52,137 | $30,095 |
| BCBS | 16 | 33 | $41,281 | $23,829 |
| Aetna | 16 | 30 | $37,014 | $21,366 |
| Aetna | 4 | 23 | $31,612 | $18,248 |
| UnitedHealthcare | 4 | 27 | $28,160 | $16,255 |
| Aetna | 18 | 18 | $24,761 | $14,293 |
| BCBS | 18 | 17 | $21,670 | $12,509 |
| UnitedHealthcare | 197 | 14 | $20,746 | $11,975 |
| UnitedHealthcare | 96 | 14 | $20,143 | $11,627 |
| Aetna | 197 | 18 | $19,571 | $11,297 |

## Appeals

| KPI | Value |
|---|---|
| First-pass denials | 669 |
| Appealed (resubmitted) | 369 |
| Appeals won | 213 |
| Appeal win rate | 57.7% |
| Recovered via appeals | $158,091 |
