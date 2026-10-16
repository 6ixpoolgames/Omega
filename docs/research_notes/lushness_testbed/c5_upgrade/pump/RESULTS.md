# C5 pump: results

Status: **complete**; 3/3 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| passive-loss0 | passive-loss0 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| extract-loss0 | passive-loss0 | +17.47918 | [+13.85008, +30.08419] | [+13.00142, +26.67381] | +0.024555 |
| donate-loss0 | passive-loss0 | +22.53808 | [+18.90084, +36.08937] | [+15.73339, +30.86629] | +0.026086 |

## Physical mechanism at T256

| Case | Net D transport | Net fuel charging bill | D owned energy | S owned energy | S function, time mean | Permanent loss probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| passive-loss0 | +0.000589 | +0.193913 | 1.401686 | 0.777365 | 0.566370 | 0.000000 |
| extract-loss0 | +0.056344 | +0.231708 | 1.413503 | 0.763826 | 0.563203 | 0.000000 |
| donate-loss0 | +0.177659 | +0.127962 | 1.422733 | 0.786224 | 0.561773 | 0.000000 |

Transport and charging are signed net quantities; reverse events and refunds remain in the full ledger. A mode name alone does not certify profit or help.

## Stationary flow and marginal-rate bounds at cadence 0.25

| Case | D transport / time | Fuel charging bill / time | D history rate bounds | S history rate bounds |
| --- | ---: | ---: | --- | --- |
| passive-loss0 | -0.000001084 | +0.000003757 | [1.456565, 1.465459] | [1.261985, 1.266608] |
| extract-loss0 | +0.000087517 | +0.000047991 | [1.481789, 1.501929] | [1.285247, 1.306797] |
| donate-loss0 | -0.000200122 | +0.000102883 | [1.480335, 1.500571] | [1.288080, 1.310124] |

Stationary flow can differ in direction from a finite cumulative flow. Marginal-rate intervals are hidden-Markov conditioning bounds in bits/time, not full-field rates or projected Markov estimates.

## Verification and scope

Maximum checked numerical/resource residual: 1.2e-09.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `e8774ec62e17d4e99369ef007f7012f3fb8b7dac0fff5602def2e01c32bedcb6`. Receipts verify imports, configurations, checksums and caps.
