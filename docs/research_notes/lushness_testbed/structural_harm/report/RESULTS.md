# Structural harm results

The primary ranking is complete-history entropy from the matched present root, separately at each horizon. Post-fault entropy and physical readouts are reported separately. Hardware loss removes local powered repair while basal recovery routes remain; it does not itself establish functional closure.

## Cases

| Mode | Hazard | Cadence | Policies | Canonical | Winner IDs by horizon |
|---|---:|---:|---:|---:|---|
| fast | 0.02 | 0.125 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: constant-service; T256: constant-service |
| fast | 0.02 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: reserve-3-mix25; T256: constant-service |
| fast | 0.02 | 0.5 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: reserve-3-mix25; T256: constant-service |
| fast | 0.04 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: constant-service; T256: constant-service |
| slow | 0.02 | 0.125 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: constant-mix25; T256: constant-service |
| slow | 0.02 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: constant-mix25; T256: reserve-3-mix25 |
| slow | 0.02 | 0.5 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: constant-mix25; T256: reserve-3-mix25 |
| slow | 0.04 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: reserve-3-mix25; T256: constant-service |
| hardware_loss | 0.02 | 0.125 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: reserve-3-mix25; T256: reserve-3-mix25 |
| hardware_loss | 0.02 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix25; T64: constant-mix25; T256: reserve-3-mix25 |
| hardware_loss | 0.02 | 0.5 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: constant-mix25; T256: reserve-3-mix25 |
| hardware_loss | 0.04 | 0.25 | 22 | 18 | T1: constant-export; T4: constant-mix75; T16: constant-mix50; T64: constant-mix25; T256: constant-service |

## Winner service partial order

The comparison uses common feasible local observations with active apparatus present. `strict` means every tied winner pair is nondecreasing and at least one is strictly more service-biased; `plateau` means all compared surfaces match; mixed or unresolved comparisons are labeled incomparable.

| Mode | Hazard | Horizon step | Finding | Pairwise orders |
|---|---:|---:|---|---|
| fast | 0.02 | 1→4 | strict | higher |
| fast | 0.02 | 4→16 | strict | higher |
| fast | 0.02 | 16→64 | strict | higher |
| fast | 0.02 | 64→256 | strict | higher |
| fast | 0.04 | 1→4 | strict | higher |
| fast | 0.04 | 4→16 | strict | higher |
| fast | 0.04 | 16→64 | strict | higher |
| fast | 0.04 | 64→256 | plateau | same |
| slow | 0.02 | 1→4 | strict | higher |
| slow | 0.02 | 4→16 | strict | higher |
| slow | 0.02 | 16→64 | strict | higher |
| slow | 0.02 | 64→256 | strict | higher |
| slow | 0.04 | 1→4 | strict | higher |
| slow | 0.04 | 4→16 | strict | higher |
| slow | 0.04 | 16→64 | strict | higher |
| slow | 0.04 | 64→256 | strict | higher |
| hardware_loss | 0.02 | 1→4 | strict | higher |
| hardware_loss | 0.02 | 4→16 | strict | higher |
| hardware_loss | 0.02 | 16→64 | plateau | same |
| hardware_loss | 0.02 | 64→256 | strict | higher |
| hardware_loss | 0.04 | 1→4 | strict | higher |
| hardware_loss | 0.04 | 4→16 | strict | higher |
| hardware_loss | 0.04 | 16→64 | strict | higher |
| hardware_loss | 0.04 | 64→256 | strict | higher |

## Consequence and hazard contrasts

Mode comparisons hold hazard and cadence fixed. Hazard comparisons hold mode and cadence fixed. Exposure is an alert readout, not a reward or ethical verdict.

| Contrast | Horizon | Result |
|---|---:|---|
| fast vs hardware_loss at h=0.02 | 1 | False (same) |
| fast vs hardware_loss at h=0.02 | 4 | False (same) |
| fast vs hardware_loss at h=0.02 | 16 | False (same) |
| fast vs hardware_loss at h=0.02 | 64 | True (lower) |
| fast vs hardware_loss at h=0.02 | 256 | True (lower) |
| fast vs hardware_loss at h=0.04 | 1 | False (same) |
| fast vs hardware_loss at h=0.04 | 4 | False (same) |
| fast vs hardware_loss at h=0.04 | 16 | True (lower) |
| fast vs hardware_loss at h=0.04 | 64 | True (lower) |
| fast vs hardware_loss at h=0.04 | 256 | False (same) |
| fast hazard 0.02→0.04 at dt=0.25 | 1 | stronger service somewhere: False (same) |
| fast hazard 0.02→0.04 at dt=0.25 | 4 | stronger service somewhere: False (same) |
| fast hazard 0.02→0.04 at dt=0.25 | 16 | stronger service somewhere: False (same) |
| fast hazard 0.02→0.04 at dt=0.25 | 64 | stronger service somewhere: True (higher) |
| fast hazard 0.02→0.04 at dt=0.25 | 256 | stronger service somewhere: False (same) |
| slow hazard 0.02→0.04 at dt=0.25 | 1 | stronger service somewhere: False (same) |
| slow hazard 0.02→0.04 at dt=0.25 | 4 | stronger service somewhere: False (same) |
| slow hazard 0.02→0.04 at dt=0.25 | 16 | stronger service somewhere: False (same) |
| slow hazard 0.02→0.04 at dt=0.25 | 64 | stronger service somewhere: True (higher) |
| slow hazard 0.02→0.04 at dt=0.25 | 256 | stronger service somewhere: True (higher) |
| hardware_loss hazard 0.02→0.04 at dt=0.25 | 1 | stronger service somewhere: False (same) |
| hardware_loss hazard 0.02→0.04 at dt=0.25 | 4 | stronger service somewhere: False (same) |
| hardware_loss hazard 0.02→0.04 at dt=0.25 | 16 | stronger service somewhere: False (lower) |
| hardware_loss hazard 0.02→0.04 at dt=0.25 | 64 | stronger service somewhere: False (same) |
| hardware_loss hazard 0.02→0.04 at dt=0.25 | 256 | stronger service somewhere: True (higher) |

## Frozen claims and adverse outcomes

| Claim | Status |
|---|---|
| H1_horizon_service_non_decrease | supported |
| C1_fast_vs_hardware_loss_response_differs | supported |
| R1_higher_hazard_stronger_service | supported |
| E1_stationary_exposure_increase | alert |
| S1_positive_to_negative_fixed_winner_lead | observed |

Full policy rows, including stock and recovery readouts, remain in `SUMMARY.json`. The report helper summarizes supplied frozen result files; it does not run simulations or alter scores.
