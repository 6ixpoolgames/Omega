# Reserve batch results

All registered compact policy rows are retained in `SUMMARY.json`, including aliases, zeros, and failed/nonconverged entries. Ranking deduplicates by canonical policy ID. Primary scores are horizon-specific bits; asymptotic rate is secondary.

| Case | Law | Cadence | Policies | Canonical | Horizons with winners | Max residual |
|---|---|---:|---:|---:|---:|---:|
| reserve-r1-absorbing-dt0.25 | absorbing | 0.25 | 22 | 18 | 5 | 2.5760504840377507e-12 |
| reserve-r1-correlated_002-dt0.125 | correlated_002 | 0.125 | 22 | 18 | 5 | 2.8688162956314045e-13 |
| reserve-r1-correlated_002-dt0.25 | correlated_002 | 0.25 | 22 | 18 | 5 | 4.4586556668946287e-13 |
| reserve-r1-correlated_002-dt0.5 | correlated_002 | 0.5 | 22 | 18 | 5 | 4.578559753554146e-13 |
| reserve-r1-independent_002-dt0.25 | independent_002 | 0.25 | 22 | 18 | 5 | 3.8546943414985435e-13 |
| reserve-r1-independent_004-dt0.25 | independent_004 | 0.25 | 22 | 18 | 5 | 3.9257486150745535e-13 |
| reserve-r1-no_shock-dt0.125 | no_shock | 0.125 | 22 | 18 | 5 | 4.982680934517703e-13 |
| reserve-r1-no_shock-dt0.25 | no_shock | 0.25 | 22 | 18 | 5 | 4.4853010194856324e-13 |
| reserve-r1-no_shock-dt0.5 | no_shock | 0.5 | 22 | 18 | 5 | 5.004885395010206e-13 |

## Horizon winners

| Case | Horizon | Canonical winner IDs | Best bits |
|---|---:|---|---:|
| reserve-r1-absorbing-dt0.25 | 1 | constant-export | 10.928918 |
| reserve-r1-absorbing-dt0.25 | 4 | constant-mix75 | 43.926401 |
| reserve-r1-absorbing-dt0.25 | 16 | constant-mix25 | 165.84334 |
| reserve-r1-absorbing-dt0.25 | 64 | reserve-3-mix25 | 579.08688 |
| reserve-r1-absorbing-dt0.25 | 256 | constant-service | 1702.4651 |
| reserve-r1-correlated_002-dt0.125 | 1 | constant-export | 13.786893 |
| reserve-r1-correlated_002-dt0.125 | 4 | constant-mix75 | 55.504616 |
| reserve-r1-correlated_002-dt0.125 | 16 | constant-mix25 | 207.39196 |
| reserve-r1-correlated_002-dt0.125 | 64 | constant-service | 703.23277 |
| reserve-r1-correlated_002-dt0.125 | 256 | constant-service | 2159.3275 |
| reserve-r1-correlated_002-dt0.25 | 1 | constant-export | 11.041735 |
| reserve-r1-correlated_002-dt0.25 | 4 | constant-mix75 | 44.32099 |
| reserve-r1-correlated_002-dt0.25 | 16 | constant-mix25 | 165.56987 |
| reserve-r1-correlated_002-dt0.25 | 64 | constant-service | 562.59029 |
| reserve-r1-correlated_002-dt0.25 | 256 | constant-service | 1747.1871 |
| reserve-r1-correlated_002-dt0.5 | 1 | constant-export | 8.2916708 |
| reserve-r1-correlated_002-dt0.5 | 4 | constant-mix75 | 33.135823 |
| reserve-r1-correlated_002-dt0.5 | 16 | constant-mix25 | 123.72587 |
| reserve-r1-correlated_002-dt0.5 | 64 | reserve-3-mix25 | 421.65261 |
| reserve-r1-correlated_002-dt0.5 | 256 | constant-service | 1329.2912 |
| reserve-r1-independent_002-dt0.25 | 1 | constant-export | 11.05178 |
| reserve-r1-independent_002-dt0.25 | 4 | constant-mix75 | 44.499933 |
| reserve-r1-independent_002-dt0.25 | 16 | constant-mix25 | 166.88449 |
| reserve-r1-independent_002-dt0.25 | 64 | constant-service | 567.2415 |
| reserve-r1-independent_002-dt0.25 | 256 | constant-service | 1755.7082 |
| reserve-r1-independent_004-dt0.25 | 1 | constant-export | 11.16721 |
| reserve-r1-independent_004-dt0.25 | 4 | constant-mix75 | 45.003613 |
| reserve-r1-independent_004-dt0.25 | 16 | constant-mix25 | 167.01517 |
| reserve-r1-independent_004-dt0.25 | 64 | constant-service | 545.19196 |
| reserve-r1-independent_004-dt0.25 | 256 | constant-service | 1622.7709 |
| reserve-r1-no_shock-dt0.125 | 1 | constant-export | 13.653564 |
| reserve-r1-no_shock-dt0.125 | 4 | constant-mix75 | 55.09751 |
| reserve-r1-no_shock-dt0.125 | 16 | constant-mix25 | 208.63942 |
| reserve-r1-no_shock-dt0.125 | 64 | reserve-3-mix25 | 738.59888 |
| reserve-r1-no_shock-dt0.125 | 256 | constant-service | 2405.1079 |
| reserve-r1-no_shock-dt0.25 | 1 | constant-export | 10.928979 |
| reserve-r1-no_shock-dt0.25 | 4 | constant-mix75 | 43.932302 |
| reserve-r1-no_shock-dt0.25 | 16 | constant-mix25 | 166.10231 |
| reserve-r1-no_shock-dt0.25 | 64 | reserve-3-mix25 | 588.33128 |
| reserve-r1-no_shock-dt0.25 | 256 | constant-service | 1933.5484 |
| reserve-r1-no_shock-dt0.5 | 1 | constant-export | 8.201868 |
| reserve-r1-no_shock-dt0.5 | 4 | constant-mix75 | 32.778419 |
| reserve-r1-no_shock-dt0.5 | 16 | constant-mix25 | 123.62317 |
| reserve-r1-no_shock-dt0.5 | 64 | constant-mix25 | 438.56192 |
| reserve-r1-no_shock-dt0.5 | 256 | constant-service | 1457.8312 |

## Registered nonconstant-response comparisons

| Case | Horizon | Best constant bits | Best reachable nonconstant gain (bits) | Strict gain |
|---|---:|---:|---:|---|
| reserve-r1-correlated_002-dt0.25 | 1 | 11.041734975049128 | -0.3233526265510811 | False |
| reserve-r1-correlated_002-dt0.25 | 4 | 44.320989954087715 | -0.6783421577094586 | False |
| reserve-r1-correlated_002-dt0.25 | 16 | 165.5698684956204 | -2.2305182766387475 | False |
| reserve-r1-correlated_002-dt0.25 | 64 | 562.5902918187873 | -0.376513284560815 | False |
| reserve-r1-correlated_002-dt0.25 | 256 | 1747.1871240322748 | -6.093137330766467 | False |
| reserve-r1-independent_002-dt0.25 | 1 | 11.051779693567278 | -0.32376626142025167 | False |
| reserve-r1-independent_002-dt0.25 | 4 | 44.499932842966345 | -0.6789629829397228 | False |
| reserve-r1-independent_002-dt0.25 | 16 | 166.88448518921794 | -2.196448747210354 | False |
| reserve-r1-independent_002-dt0.25 | 64 | 567.2414990988017 | -0.08468597961780233 | False |
| reserve-r1-independent_002-dt0.25 | 256 | 1755.7081636282855 | -4.5481390127577015 | False |
| reserve-r1-independent_004-dt0.25 | 1 | 11.167210116117287 | -0.3216480479500703 | False |
| reserve-r1-independent_004-dt0.25 | 4 | 45.00361280332298 | -0.6525914803660555 | False |
| reserve-r1-independent_004-dt0.25 | 16 | 167.01516707974864 | -1.8019894887656847 | False |
| reserve-r1-independent_004-dt0.25 | 64 | 545.191956409573 | -0.670706899556194 | False |
| reserve-r1-independent_004-dt0.25 | 256 | 1622.7708772545286 | -3.4076966836603333 | False |

## Absorbing sentinel active64 prediction

| Horizon | Winner active64 difference interval | Prediction |
|---:|---:|---|
| 1 | [-0.029480717, -0.029480717] | fail |
| 4 | [-0.039170293, -0.039170293] | fail |
| 16 | [-0.061395687, -0.061395687] | fail |
| 64 | [-0.076917851, -0.076917851] | fail |
| 256 | [-0.077325067, -0.077325067] | fail |

The sentinel comparison uses different declared physical laws and does not isolate irreversibility.

## Exposure diagnostic

| Horizon | Stationary exposure difference, h=.04 minus h=.02 |
|---:|---:|
| 1 | [-0.090809371, -0.090809371] |
| 4 | [-0.099002146, -0.099002146] |
| 16 | [-0.12694714, -0.12694714] |
| 64 | [-0.16386246, -0.16386246] |
| 256 | [-0.16386246, -0.16386246] |

Exposure differences are diagnostic. Fixed-policy replay metrics and full policy rows are retained by case and canonical ID in `SUMMARY.json`.

## Fixed-policy cadence audit

Finding counts: no_certified_reversal=30, self_comparison=10.
Self-comparisons are labeled separately. Cadence changes address temporal resolution, not full grain robustness.

Exposure is a diagnostic and does not by itself establish harm. Cadence audits address temporal resolution only; they do not establish full grain robustness.
