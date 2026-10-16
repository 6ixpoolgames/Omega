# C5 opportunity: results

Status: **complete**; 9/9 cases verified.

Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.
Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.

## T256 at cadence 0.25

| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |
| --- | --- | ---: | --- | --- | ---: |
| source0.02-field0 | source0.02-field0 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| source0.02-field1 | source0.02-field0 | +28.69091 | [-2.83701, +0.91845] | [+18.70773, +39.57704] | +0.010869 |
| source0.02-field3 | source0.02-field0 | +49.41219 | [-3.82154, +0.03336] | [+42.45591, +61.61705] | +0.002546 |
| source0.12-field0 | source0.12-field0 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| source0.12-field1 | source0.12-field0 | +29.23081 | [-2.78206, +0.92953] | [+21.76082, +38.64093] | -0.002580 |
| source0.12-field3 | source0.12-field0 | +53.45356 | [-3.75945, +0.05625] | [+49.65550, +65.42610] | -0.015765 |
| source0.6-field0 | source0.6-field0 | +0.00000 | [+0.00000, +0.00000] | [+0.00000, +0.00000] | +0.000000 |
| source0.6-field1 | source0.6-field0 | +31.11797 | [-2.73150, +0.93034] | [+27.69411, +36.92462] | -0.007994 |
| source0.6-field3 | source0.6-field0 | +61.94392 | [-3.70460, +0.06788] | [+62.01212, +71.24157] | -0.021503 |

## Physical mechanism at T256

| Case | Paid builds | Reverse builds | Thermal builds | Thermal losses | Access capture net | Upkeep net | Device at deadline | Device first arrival |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source0.02-field0 | 0.45621 | 0.21040 | 0.00666 | 0.00300 | +0.14886 | +0.24770 | 0.24947 | 0.31587 |
| source0.02-field1 | 0.44281 | 0.21377 | 0.00676 | 0.00274 | +0.12919 | +0.23259 | 0.23306 | 0.29783 |
| source0.02-field3 | 0.32652 | 0.15890 | 0.00707 | 0.00187 | +0.08836 | +0.16142 | 0.17283 | 0.22092 |
| source0.12-field0 | 0.41848 | 0.15594 | 0.00659 | 0.00320 | +0.83429 | +0.38652 | 0.26593 | 0.31600 |
| source0.12-field1 | 0.39944 | 0.15230 | 0.00668 | 0.00295 | +0.77278 | +0.35796 | 0.25087 | 0.29793 |
| source0.12-field3 | 0.29158 | 0.10940 | 0.00702 | 0.00203 | +0.54212 | +0.24752 | 0.18717 | 0.22100 |
| source0.6-field0 | 0.36537 | 0.07832 | 0.00649 | 0.00345 | +1.48302 | +0.49994 | 0.29008 | 0.31604 |
| source0.6-field1 | 0.34509 | 0.07427 | 0.00659 | 0.00319 | +1.38246 | +0.46337 | 0.27421 | 0.29797 |
| source0.6-field3 | 0.25175 | 0.05224 | 0.00696 | 0.00219 | +0.96927 | +0.32037 | 0.20427 | 0.22102 |

An independent packet source is present in every comparison arm. Source work is recorded in PHYSICAL.csv. Thermal births/losses follow from the gross thermal-event count and its signed unit device-energy change. The device is a passive coarse access structure with reversible construction, thermal assembly and bank-exchange overhead; paid builds do not certify exclusive ancestry of its capture.

## Verification and scope

Maximum checked numerical/resource residual: 1.95e-09.
COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.
The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.
Frozen numerical source: `e8774ec62e17d4e99369ef007f7012f3fb8b7dac0fff5602def2e01c32bedcb6`. Receipts verify imports, configurations, checksums and caps.
