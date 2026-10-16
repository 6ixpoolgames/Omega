# C5 opportunity-active: results

Status: **complete**; 3/3 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| idle | idle | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| movement-steering | idle | +18.13402 | [-0.40703, +1.45755] | [+13.55722, +30.09360] | +0.020604 |
| blocking | idle | +17.45187 | [-0.40561, +1.45873] | [+10.50702, +27.01813] | +0.020303 |

## Physical mechanism at T256

| Case | Paid builds | Reverse builds | Thermal builds | Thermal losses | Access capture net | Upkeep net | Device at deadline | Device first arrival |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| idle | 0.42443 | 0.15756 | 0.00656 | 0.00326 | +0.84013 | +0.39501 | 0.27017 | 0.32032 |
| movement-steering | 0.35100 | 0.12642 | 0.00681 | 0.00260 | +0.67867 | +0.31625 | 0.22879 | 0.27005 |
| blocking | 0.35087 | 0.12638 | 0.00681 | 0.00260 | +0.67845 | +0.31614 | 0.22870 | 0.26995 |

An independent packet source is present in every comparison arm. Source work is recorded in PHYSICAL.csv. Thermal births/losses follow from the gross thermal-event count and its signed unit device-energy change. The device is a passive coarse access structure with reversible construction, thermal assembly and bank-exchange overhead; paid builds do not certify exclusive ancestry of its capture.

## Verification and scope

Maximum checked numerical/resource residual: 9.26e-10.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `615ee36e2009fd762045c2a83939273b0be868654288037893bb678780e51335`. Receipts verify imports, configurations, checksums and caps.
