# C5 supplied-pump: results

Status: **complete**; 3/3 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| passive | passive | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract | passive | +22.70401 | [+19.21653, +36.00504] | [+17.04679, +32.40022] | +0.024555 |
| donate | passive | +19.01064 | [+14.57965, +30.51022] | [+15.55556, +30.38380] | +0.026086 |

## Physical mechanism at T256

| Case | Net D transport | Net fuel charging bill | D owned energy | S owned energy | S function, time mean | Permanent loss probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| passive | -0.001037 | +0.218644 | 1.443211 | 0.767779 | 0.548322 | 0.000000 |
| extract | -0.229957 | +0.124599 | 1.465741 | 0.755225 | 0.551907 | 0.000000 |
| donate | -0.206482 | +0.326002 | 1.439553 | 0.783885 | 0.554947 | 0.000000 |

Transport and charging are signed net quantities; reverse events and refunds remain in the full ledger. A mode name alone does not certify profit or help.

## Stationary flow and marginal-rate bounds at cadence 0.25

| Case | D transport / time | Fuel charging bill / time | D history rate bounds | S history rate bounds |
| --- | ---: | ---: | --- | --- |
| passive | -0.000001084 | +0.000003757 | [1.456565, 1.465459] | [1.261985, 1.266608] |
| extract | +0.000087517 | +0.000047991 | [1.481789, 1.501929] | [1.285247, 1.306797] |
| donate | -0.000200122 | +0.000102883 | [1.480335, 1.500571] | [1.288080, 1.310124] |

Stationary flow can differ in direction from a finite cumulative flow. Marginal-rate intervals are hidden-Markov conditioning bounds in bits/time, not full-field rates or projected Markov estimates.

## Verification and scope

Maximum checked numerical/resource residual: 1.28e-09.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `615ee36e2009fd762045c2a83939273b0be868654288037893bb678780e51335`. Receipts verify imports, configurations, checksums and caps.
