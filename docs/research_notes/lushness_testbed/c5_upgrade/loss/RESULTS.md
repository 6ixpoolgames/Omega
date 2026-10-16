# C5 loss: results

Status: **complete**; 6/6 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| passive-loss0.01 | passive-loss0.01 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract-loss0.01 | passive-loss0.01 | +17.73074 | [+13.88014, +30.04775] | [+14.66476, +27.51950] | +0.025102 |
| donate-loss0.01 | passive-loss0.01 | +22.79933 | [+18.85692, +35.97021] | [+17.47033, +31.79019] | +0.024433 |
| passive-loss0.04 | passive-loss0.04 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract-loss0.04 | passive-loss0.04 | +17.93606 | [+13.94542, +30.07146] | [+15.90831, +28.35840] | +0.025102 |
| donate-loss0.04 | passive-loss0.04 | +22.86601 | [+18.81681, +35.87304] | [+18.70691, +32.61828] | +0.024433 |

## Physical mechanism at T256

| Case | Net D transport | Net fuel charging bill | D owned energy | S owned energy | S function, time mean | Permanent loss probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| passive-loss0.01 | +0.000210 | +0.194782 | 1.412439 | 0.386495 | 0.267178 | 0.683976 |
| extract-loss0.01 | +0.027902 | +0.219871 | 1.424504 | 0.378312 | 0.266189 | 0.681443 |
| donate-loss0.01 | +0.155763 | +0.137821 | 1.429680 | 0.404341 | 0.265512 | 0.679712 |
| passive-loss0.04 | -0.000010 | +0.195461 | 1.417037 | 0.308879 | 0.090464 | 0.926347 |
| extract-loss0.04 | +0.009530 | +0.212080 | 1.429439 | 0.301585 | 0.090348 | 0.925168 |
| donate-loss0.04 | +0.132547 | +0.148583 | 1.432144 | 0.327652 | 0.090109 | 0.922713 |

Transport and charging are signed net quantities; reverse events and refunds remain in the full ledger. A mode name alone does not certify profit or help.

## Stationary flow and marginal-rate bounds at cadence 0.25

| Case | D transport / time | Fuel charging bill / time | D history rate bounds | S history rate bounds |
| --- | ---: | ---: | --- | --- |
| passive-loss0.01 | -0.000002114 | +0.000003854 | [1.460158, 1.468828] | [1.096436, 1.096887] |
| extract-loss0.01 | +0.000040157 | +0.000025073 | [1.485628, 1.505745] | [1.121072, 1.141323] |
| donate-loss0.01 | -0.000215715 | +0.000110382 | [1.484367, 1.504627] | [1.121882, 1.142799] |
| passive-loss0.04 | -0.000002114 | +0.000003854 | [1.460158, 1.468828] | [1.096436, 1.096887] |
| extract-loss0.04 | +0.000040157 | +0.000025073 | [1.485628, 1.505745] | [1.121072, 1.141323] |
| donate-loss0.04 | -0.000215715 | +0.000110382 | [1.484367, 1.504627] | [1.121882, 1.142799] |

Stationary flow can differ in direction from a finite cumulative flow. Marginal-rate intervals are hidden-Markov conditioning bounds in bits/time, not full-field rates or projected Markov estimates.

## Verification and scope

Maximum checked numerical/resource residual: 9.58e-10.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `e8774ec62e17d4e99369ef007f7012f3fb8b7dac0fff5602def2e01c32bedcb6`. Receipts verify imports, configurations, checksums and caps.

The permanent sink removes S apparatus capability; S movement, banks and the environmental process continue. Residual history rates describe those surviving processes, not preservation of the lost capability.
Lower loss probability can arise from less time with vulnerable apparatus. Read it alongside functional uptime; it is not by itself evidence of stronger protection.
