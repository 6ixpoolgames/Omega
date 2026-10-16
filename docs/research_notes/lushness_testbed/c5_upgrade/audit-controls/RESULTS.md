# C5 audit-controls: results

Status: **complete**; 7/7 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| idle | idle | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| blocking | idle | -13.63743 | [+4.84856, +14.05908] | [-25.77800, -14.17586] | -0.012192 |
| driven-debit | idle | +6.36724 | [+2.95706, +12.20487] | [-5.00073, +4.85660] | +0.010434 |
| ordinary | idle | +27.05549 | [+18.77714, +29.77626] | [-4.98049, +4.89629] | +0.089894 |
| movement-access | idle | -19.17434 | [+3.94238, +13.21044] | [-21.86361, -9.70753] | -0.015111 |
| movement-build | idle | -14.69461 | [+3.35619, +12.60980] | [-18.63619, -5.60870] | -0.015664 |
| movement-trap | idle | +29.13381 | [-0.07129, +7.28814] | [+23.84400, +34.23374] | +0.041704 |

## Physical mechanism at T256

| Case | D owned energy | S owned energy | Physical bill | Net receiver transfer | D time-mean function | S time-mean function |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| idle | 1.372388 | 1.070883 | 0.000000 | +0.000000 | 0.494413 | 0.588817 |
| blocking | 1.338288 | 1.037345 | 1.137197 | +0.000000 | 0.479360 | 0.576294 |
| driven-debit | 1.344522 | 1.070226 | 0.939118 | +0.000000 | 0.481994 | 0.588382 |
| ordinary | 1.525030 | 1.044724 | 0.000000 | +0.000000 | 0.519189 | 0.583316 |
| movement-access | 1.342098 | 1.041596 | 1.048307 | +0.000000 | 0.480831 | 0.579608 |
| movement-build | 1.341562 | 1.095345 | 1.078003 | +0.000000 | 0.479051 | 0.617849 |
| movement-trap | 1.367777 | 1.077379 | 0.385222 | +0.000000 | 0.490445 | 0.577777 |

Owned-energy columns are endpoint stocks. Per-family integrated changes independently close against them; source capture minus intervention bill is not substituted for that full balance. The driven-debit and ordinary apparatus arms use their declared physical mechanisms, not equal realized fuel or activity.

## Verification and scope

Maximum checked numerical/resource residual: 1.62e-09.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `06967ed1e590187d1df2d290a1424ebf9c4598596069ffbed78bfb5bbbfa9a77`. Receipts verify imports, configurations, checksums and caps.
