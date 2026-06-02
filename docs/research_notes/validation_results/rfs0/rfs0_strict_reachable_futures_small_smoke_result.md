# RFS0 Strict Reachable Futures Small Smoke Result

Date: 2026-05-22

Status: complete.

Primary artifact:

```text
results/rfs0/20260522_strict_reachable_futures_small_smoke/summary.md
```

## Purpose

This was the first tiny-to-small smoke for the reachable-futures substrate
reset. The goal was prognostic, not confirmatory:

```text
Can a small exact finite transition substrate compute strict
recovery-conditioned viability objects, controls, capture basins, and
future-space contraction while preserving partial outputs under wall-clock caps?
```

No Omega-positive labels are used in the generator or result classes.

## Implementation

Added:

```text
omega/rfs0/substrate.py
omega/rfs0/exact.py
omega/rfs0/run_strict_batch.py
```

The runner writes checkpointed per-system JSONL, CSV summaries, status, and
`summary.md` after completed jobs. A timeout salvage test with a one-second cap
exited as `TIMED_OUT` and retained 13 completed rows plus summaries.

## Run Shape

Small smoke:

```text
regimes:
  balanced, permissive, harsh, repair_rich, commit_rich, capacity_tight

controls:
  structured
  dense_permissive_control
  dead_control
  random_edge_control
  shuffled_admissibility_control
  no_perturbation_control

seeds per regime:
  3

systems:
  108

state count per system:
  2250

workers:
  18

elapsed:
  about 6 seconds

errors:
  0
```

## Main Readout

Aggregate:

| n | K strict | Viab strict H16 | strict fraction | capture Hr4 | capacity recovery | integrity recovery | contraction | expansion |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 108 | 369.0 | 231.2 | 0.1028 | 1142.5 | 0.796 | 0.776 | 0.243 | 0.000 |

Structured substrate:

| n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction |
|---:|---:|---:|---:|---:|---:|
| 18 | 268.0 | 73.0 | 0.0324 | 785.0 | 0.541 |

Structured regimes:

| regime | Viab strict H16 | strict fraction | read |
|---|---:|---:|---|
| balanced | 18.0 | 0.0080 | sparse nonzero |
| repair_rich | 18.0 | 0.0080 | sparse nonzero |
| commit_rich | 18.0 | 0.0080 | sparse nonzero |
| permissive | 384.0 | 0.1707 | too large / permissive |
| harsh | 0.0 | 0.0000 | overfiltered or dead |
| capacity_tight | 0.0 | 0.0000 | overfiltered or dead |

Controls:

| control | Viab strict H16 | strict fraction | read |
|---|---:|---:|---|
| dead_control | 0.0 | 0.0000 | expected dead control |
| dense_permissive_control | 900.0 | 0.4000 | expected too-permissive control |
| random_edge_control | 38.6 | 0.0172 | nonzero; control risk |
| shuffled_admissibility_control | 266.3 | 0.1183 | strong control risk |
| no_perturbation_control | 109.5 | 0.0487 | shows recovery filter matters |

## Interpretation

Minimal success passed:

```text
exact computation completed
strict filter ladder is computable
K_strict differs from K0
Viab(K_strict, H16) can be zero, sparse, or large depending on regime
Capture(K_strict, Hr4) is nonempty in structured regimes
timeout salvage works
```

Strong success is not established:

```text
shuffled admissibility produces a large strict object
random-edge control remains nonzero
expansion events are absent under the current contraction metric
some structured regimes are identical, suggesting low parameter resolution
```

## Prognosis

RFS0 is promising as an exact measurement floor. It immediately separates
dead, permissive, and sparse strict-object regimes, and it gives a useful
filter-ladder diagnosis without outcome labels.

But the current substrate is not yet ready for a longer validation run as-is.
The next small probe should target control separation and contraction geometry:

```text
strengthen structured transition topology so random-edge and shuffled-label
controls do not mimic the object as easily
add a metric that distinguishes contraction from pure monotone shrinkage
increase parameter resolution so balanced, repair_rich, and commit_rich are not
nearly identical
keep the harsh strict filter; do not loosen it just to get positives
```

Current claim boundary:

```text
RFS0 can compute and expose a sparse strict recovery-conditioned viable-futures
object in some finite regimes.

It has not yet shown that this object is robustly distinguished from all nulls.
```
