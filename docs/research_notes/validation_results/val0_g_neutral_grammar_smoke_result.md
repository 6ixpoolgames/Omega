# VAL0-G Neutral Grammar Geometry Smoke Result

Date: 2026-05-21

Status: first smoke complete.

Primary artifact:

```text
results/val0_g/20260521_neutral_grammar_smoke_v2/summary.md
```

Supporting files:

```text
results/val0_g/20260521_neutral_grammar_smoke_v2/config.json
results/val0_g/20260521_neutral_grammar_smoke_v2/status.json
results/val0_g/20260521_neutral_grammar_smoke_v2/aggregate.csv
results/val0_g/20260521_neutral_grammar_smoke_v2/geometry_class_bins.csv
results/val0_g/20260521_neutral_grammar_smoke_v2/parameter_regime_summary.csv
results/val0_g/20260521_neutral_grammar_smoke_v2/results.csv
results/val0_g/20260521_neutral_grammar_smoke_v2/results.jsonl
```

## Purpose

This was the first VAL0-G smoke after the pivot from direct R1 validation to
neutral-grammar geometry discovery.

The probe asks whether neutral constructor-like task worlds produce
non-degenerate recoverable-continuation geometries without hand-labeling
outcomes in the generator.

## Run Shape

```text
neutral_grammar_v1:
  50 seeds

guardrails:
  low_resolution_dense: 12 seeds
  brittle_peak: 12 seeds

num_tasks:
  64

max_states_per_depth:
  512

rollout_samples:
  128

cut_samples:
  4

workers:
  18
```

Total rows: 74.

Errors: 0.

Runtime: about 4 seconds.

## Note On Calibration

An initial pre-result smoke completed cleanly but saturated descendant mass at
depth 16 across all families. The neutral grammar was then minimally revised to
broaden lower-enable, higher-obstruction, decay, and capacity-pressure regimes.

The committed result is the calibrated v2 smoke.

## Aggregate Readout

| family | n | survival AUC | slope | mass d16 | P terminal d16 | cut k1 | B8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 12 | 156.000 | 34.000 | 512.000 | 0.000 | 1.000 | 1.000 |
| low_resolution_dense | 12 | 14.997 | 32.400 | 512.000 | 0.000 | 1.000 | 1.000 |
| neutral_grammar_v1 | 50 | 74.961 | 24.697 | 373.640 | 0.339 | 0.585 | 1.450 |

## Post-Hoc Geometry Classes

Across all rows:

| class | n | survival AUC | mass d16 | P terminal d16 | cut k1 |
|---|---:|---:|---:|---:|---:|
| deep_corridor_like | 14 | 24.924 | 512.000 | 0.002 | 0.940 |
| recoverable_basin_like | 38 | 107.545 | 512.000 | 0.010 | 1.000 |
| self_terminating | 16 | 11.873 | 79.625 | 0.979 | 0.131 |
| thin_ridge | 6 | 195.733 | 512.000 | 0.150 | 0.000 |

Neutral-only class counts:

```text
recoverable_basin_like:
  26 / 50

self_terminating:
  16 / 50

thin_ridge:
  6 / 50

deep_corridor_like:
  2 / 50
```

## Interpretation

Minimal smoke success passed:

```text
runner completed
no errors
neutral grammar produced multiple post-hoc geometry classes
terminal probability varied from 0 to 1
cut sensitivity varied from 0 to 1
descendant mass was no longer universally saturated
```

The most important positive signal is not that any class is "Omega-like." It is
that the neutral grammar produced separable geometry-like regimes using measured
features only:

```text
self_terminating:
  high terminal probability
  low depth-16 descendant mass
  low cut survival

thin_ridge:
  high descendant mass
  low cut survival

recoverable_basin_like:
  high descendant mass
  high cut survival
  low terminal probability

deep_corridor_like:
  persistent depth without the same high-AUC basin profile
```

This supports continuing VAL0-G as a geometry-discovery substrate.

## Caveats

The current classifier is heuristic and post hoc.

Several metrics still hit the depth-16 state cap in guardrails and in many
neutral worlds. That means larger follow-up runs should either:

```text
increase max_states_per_depth
add depth 32
or replace capped mass with sampled survival/filter ratios
```

The brittle guardrail is not yet a clean thin-ridge calibrator under these
metrics because it saturates descendant mass and cut survival at the current
cap. That should be improved before using it as a serious guardrail.

## Recommendation

Proceed to a second, still-small VAL0-G probe.

Recommended next probe:

```text
neutral_grammar_v1:
  200-300 seeds

changes:
  add depth 32 if runtime remains trivial
  raise max_states_per_depth or report cap-hit rates
  add explicit cap_hit_d fields
  improve brittle/thin-ridge guardrail

keep:
  no R1 tuning
  no full atlas scale yet
  no GPU
```

The question for the next run is whether the class separation remains stable
when the sample size increases and capped descendant mass is handled more
explicitly.
