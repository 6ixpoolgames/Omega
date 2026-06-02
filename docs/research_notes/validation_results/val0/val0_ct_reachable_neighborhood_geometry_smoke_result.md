# VAL0-CT Reachable-Neighborhood Geometry Smoke Result

Date: 2026-05-20

Status: diagnostic smoke complete.

Primary artifact:

```text
results/val0_ct/20260520_geometry_smoke_15min_n24/summary.md
```

Supporting files:

```text
results/val0_ct/20260520_geometry_smoke_15min_n24/config.json
results/val0_ct/20260520_geometry_smoke_15min_n24/aggregate.csv
results/val0_ct/20260520_geometry_smoke_15min_n24/results.csv
results/val0_ct/20260520_geometry_smoke_15min_n24/results.jsonl
results/val0_ct/20260520_geometry_smoke_15min_n24/status.json
```

## Purpose

This was the first validation pass for the reachable-neighborhood geometry sidecar.

The run intentionally froze policy behavior and measured geometry after the R1 and
R0-lookahead choices. It did not modify R1, R0-lookahead, the generators, or the
success criteria.

## Run Shape

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  unlabeled_structural

seeds:
  24 per family

h:
  1, 2

H:
  16

T:
  32

workers:
  18

geometry:
  depth profile
  terminal depth
  corridor width at d=8 and d=16
  re-entry overlap
```

Total rows: 192.

Errors: 0.

Wall clock: about 6 minutes inside a 15-minute cap.

## Aggregate Readout

| family | h | n | mean R1 advantage | same choice | terminal gap | d16 gap | corridor d8 gap | corridor d16 gap | re-entry gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 1 | 24 | 0.319 | 0.417 | 0.000 | 7.833 | -0.292 | 6.958 | -0.102 |
| brittle_peak | 2 | 24 | 0.555 | 0.042 | 0.000 | 13.708 | -3.583 | 10.167 | -0.196 |
| low_resolution_dense | 1 | 24 | -0.003 | 0.542 | 0.000 | -1.208 | 0.000 | 0.000 | 0.000 |
| low_resolution_dense | 2 | 24 | 0.002 | 0.250 | 0.000 | 0.417 | 0.000 | 0.000 | 0.003 |
| structured_asymmetric_v2 | 1 | 24 | 0.215 | 0.417 | 0.000 | 7.042 | -1.875 | -0.417 | -0.119 |
| structured_asymmetric_v2 | 2 | 24 | 0.473 | 0.083 | 0.000 | 12.792 | -6.167 | 1.542 | -0.189 |
| unlabeled_structural | 1 | 24 | -0.038 | 0.750 | 0.000 | -0.333 | 2.500 | -6.208 | -0.025 |
| unlabeled_structural | 2 | 24 | 0.034 | 0.417 | 0.000 | -0.500 | 2.792 | -1.333 | -0.017 |

## Interpretation

Minimal smoke success passed:

```text
the runner completed
partial/status artifacts were written
geometry fields were non-degenerate except terminal depth
anchor R1 advantage reproduced
low_resolution_dense remained approximately matched
```

The main positive signal is that anchor families again separate on R1 advantage,
and R1-selected states have higher depth-profile d16 counts in both anchor families.
This is consistent with the hypothesis that R1 is selecting states with more retained
future reachability in those designed regimes.

The main negative signal is that terminal depth was completely uninformative under
the first threshold definition. It was zero-gap across every aggregate row. That
metric should be revised or dropped before scale-up.

The re-entry metric also does not yet explain the anchor signal. R1 showed lower
mean re-entry overlap than R0-lookahead in the positive anchor families. That is
not fatal, but it means first-pass re-entry overlap is not the clean explanatory
variable.

The corridor metric is mixed:

```text
brittle_peak:
  corridor d16 favors R1

structured_asymmetric_v2:
  corridor d16 is weak/mixed

unlabeled_structural:
  corridor d8 favors R1, while corridor d16 does not
```

This suggests that a shorter-horizon corridor signal may exist in unlabeled
structural regimes, but it is not yet a robust recoverability claim.

## Unlabeled Structural Triage

Across unlabeled structural rows:

```text
h=1 positive R1-advantage rows:
  9 / 24

h=2 positive R1-advantage rows:
  7 / 24
```

Median-split exploratory checks across all unlabeled rows:

```text
re-entry gap:
  low half mean R1 advantage  = -0.012
  high half mean R1 advantage =  0.008

corridor d8 gap:
  low half mean R1 advantage  = -0.037
  high half mean R1 advantage =  0.033

corridor d16 gap:
  low half mean R1 advantage  =  0.002
  high half mean R1 advantage = -0.006

depth-profile d16 gap:
  low half mean R1 advantage  =  0.022
  high half mean R1 advantage = -0.026
```

This is not a theory result, but it is a useful next hook: corridor width at d=8
and perhaps re-entry gap weakly stratify unlabeled structural outcomes in the
expected direction, while d16/depth-profile gaps do not.

## Recommendation

Do not scale this exact sidecar unchanged.

Recommended next revision:

```text
keep:
  depth profile d16 as an anchor sanity diagnostic
  corridor width d8 for unlabeled triage
  dense control guardrail

revise:
  terminal depth threshold, because it saturated
  re-entry perturbation definition, because it does not explain anchors yet

defer:
  redundancy clustering
  component graph metrics
  GPU work
```

The next useful run should be a targeted unlabeled structural regime-classification
probe using corridor d8 / candidate variance bins, while preserving brittle_peak,
structured_asymmetric_v2, and low_resolution_dense as guardrails.
