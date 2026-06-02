# VAL0-CT 12h Unlabeled Geometry Battery Result

Date: 2026-05-20

Status: complete.

Primary artifact:

```text
results/val0_ct/20260520_12h_unlabeled_geometry_battery/summary.md
```

Supporting files:

```text
results/val0_ct/20260520_12h_unlabeled_geometry_battery/config.json
results/val0_ct/20260520_12h_unlabeled_geometry_battery/status.json
results/val0_ct/20260520_12h_unlabeled_geometry_battery/aggregate.csv
results/val0_ct/20260520_12h_unlabeled_geometry_battery/unlabeled_geometry_bins.csv
results/val0_ct/20260520_12h_unlabeled_geometry_battery/unlabeled_corridor_variance_interaction.csv
results/val0_ct/20260520_12h_unlabeled_geometry_battery/results.csv
results/val0_ct/20260520_12h_unlabeled_geometry_battery/results.jsonl
```

## Purpose

This battery tested whether the weak reachable-neighborhood geometry hook from the
first smoke run survived scale inside `unlabeled_structural`.

The target was not global R1 dominance. The target was regime discovery:

```text
Can corridor / variance / retained-depth geometry identify unlabeled rows where
R1 approaches or beats equal-budget R0-lookahead?
```

Policies remained frozen.

## Run Shape

```text
sanity:
  8 seeds

unlabeled_structural main:
  2500 seeds
  h = 1, 2
  5000 main rows

guardrails:
  brittle_peak: 150 seeds
  structured_asymmetric_v2: 150 seeds
  low_resolution_dense: 150 seeds

workers:
  18

geometry_samples:
  32

reentry_samples:
  0
```

Total rows: 5948.

Errors: 0.

Runtime: about 2 hours 8 minutes inside a 12-hour wall-clock cap.

## Aggregate Readout

| phase | family | h | n | mean R1 advantage | R1 win rate | R1 LHR | R0-lookahead LHR | same choice | corridor d8 gap | variance | depth d16 gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| unlabeled_main | unlabeled_structural | 1 | 2500 | -0.067 | 0.180 | 0.378 | 0.445 | 0.623 | -0.043 | 3.111 | -0.278 |
| unlabeled_main | unlabeled_structural | 2 | 2500 | -0.033 | 0.278 | 0.435 | 0.467 | 0.533 | 0.090 | 5.054 | -0.016 |
| guardrails | brittle_peak | 1 | 150 | 0.188 | 0.513 | 0.380 | 0.192 | 0.460 | -1.840 | 0.000 | 6.040 |
| guardrails | brittle_peak | 2 | 150 | 0.511 | 0.913 | 0.711 | 0.200 | 0.113 | -5.447 | 1.789 | 9.960 |
| guardrails | structured_asymmetric_v2 | 1 | 150 | 0.096 | 0.473 | 0.413 | 0.316 | 0.460 | -3.587 | 0.000 | 5.653 |
| guardrails | structured_asymmetric_v2 | 2 | 150 | 0.437 | 0.933 | 0.733 | 0.296 | 0.127 | -7.653 | 1.655 | 10.027 |
| guardrails | low_resolution_dense | 1 | 150 | -0.004 | 0.080 | 0.530 | 0.534 | 0.593 | 0.000 | 0.640 | 0.053 |
| guardrails | low_resolution_dense | 2 | 150 | -0.001 | 0.093 | 0.535 | 0.535 | 0.213 | 0.000 | 0.937 | -0.040 |

## Interpretation

The guardrails behaved correctly:

```text
brittle_peak and structured_asymmetric_v2:
  R1 advantage reproduced

low_resolution_dense:
  remained matched
```

The unlabeled global result remained negative:

```text
h=1:
  R1 advantage -0.067
  R1 win rate 0.180

h=2:
  R1 advantage -0.033
  R1 win rate 0.278
```

That is not surprising given earlier held-out work. The important question was
whether geometry bins reveal coherent positive regimes.

## Binning Result

The smoke-run corridor d8 hook did not survive scale as a strong predictor:

```text
combined corridor d8 q1:
  mean R1 advantage -0.052
  win rate 0.220

combined corridor d8 q5:
  mean R1 advantage -0.055
  win rate 0.228
```

Candidate future-R0 variance was the cleaner stratifier:

```text
combined variance q1:
  mean R1 advantage -0.084
  win rate 0.172

combined variance q5:
  mean R1 advantage -0.036
  win rate 0.268
```

By horizon:

```text
h=1 variance q1 -> q5:
  mean R1 advantage -0.097 -> -0.057
  win rate 0.159 -> 0.200

h=2 variance q1 -> q5:
  mean R1 advantage -0.058 -> -0.025
  win rate 0.219 -> 0.305
```

Depth-profile d16 gap did not stratify in the expected direction.

## Interaction Result

The best corridor d8 x candidate variance cell was:

```text
scope:
  h=2

corridor d8 quintile:
  q4

candidate variance quintile:
  q5

n:
  71

mean R1 advantage:
  -0.002

R1 win rate:
  0.408
```

This is near parity, not a positive-regime discovery.

## Conclusion

This battery is a disciplined partial negative.

It supports:

```text
R1 anchor calibration remains reproducible.
Dense controls remain clean.
Unlabeled h=2 is less unfavorable than h=1.
Candidate future-R0 variance identifies rows where R1 becomes less bad and more often wins.
```

It does not support:

```text
corridor d8 gap as a robust scaled predictor.
depth-profile d16 gap as an unlabeled regime classifier.
a clear positive unlabeled geometry regime under the current metrics.
```

## Recommendation

Do not scale this exact geometry classifier further.

The next useful move is to revise the geometry target rather than simply add more
seeds. The most promising retained hook is not corridor width by itself, but
high candidate variance plus `h=2` cases where R1 approaches parity.

Recommended next probe:

```text
target:
  h=2 unlabeled_structural

condition:
  high candidate_future_R0_variance

question:
  what structural feature distinguishes the near-parity / winning rows from the
  losing rows inside the same high-variance band?
```

That should be treated as mechanism discovery, not validation.
