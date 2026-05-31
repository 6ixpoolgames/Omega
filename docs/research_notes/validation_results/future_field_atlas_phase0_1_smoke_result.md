# Future Field Atlas Phase 0/1 Publication-Schema Smoke Result

Status: clean instrument-build smoke completed after publication-schema repair
Primary output: `results/future_field_atlas/20260601_phase0_1_publication_schema_h32/`
Runner: `omega.future_field_atlas.run_future_field_atlas`
Spec: `docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
Glossary: `docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`

## Executive Summary

The Future Field Atlas Phase 0/1 smoke completed cleanly after another strict
schema pass. The goal of this pass was to make the formal atlas object lead and
make the rank-boundary result clearly secondary as a calibration fixture.

```text
status: COMPLETED
instrument_version: 0.3.0
workers: 4
conditions: 8
scans_completed: 8 / 8
elapsed_seconds: 18.58
errors: 0
horizon_max: 32
frontier_node_rows: 30461
frontier_edge_rows: 106431
selection_operator_geometry_rows: 8
```

This remains an instrument smoke, not a science result and not an Omega
validation result.

## Formal Object

The clean runtime now organizes every scan around first-class specs:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
FrontierScanSpec
```

Rows emitted by the scanner now carry state-space, law, observable, selection
operator, and frontier-scan identifiers. The object can be described without
the old top-m result:

```text
A Future Field Atlas scans a finite state space under lawful transformations,
records frontier topology over horizon, and emits reconstructible feature maps
of reachable-future geometry.
```

## What Changed

The runtime package now has zero hits for historical treatment-arm and response
terms such as:

```text
boundary_control
condition_role
known_mechanism
baseline_m3
drop_weakest
response_bearing
```

Primary artifact names were also changed:

```text
selection_operator_geometry_summary.csv
rank_boundary_geometry_by_horizon.csv
rank_boundary_geometry_by_horizon_summary.csv
rank_boundary_geometry_by_horizon_pair.csv
```

The previous rank-core-centered artifact names are no longer emitted.

## Artifact Semantics

Frontier node and edge rows now expose explicit artifact status and retention
policy:

```text
complete
lossless_compressed
sampled
truncated_noninterpretable
```

The H32 smoke emitted complete in-memory feature maps. CSV row artifacts still
carry retention-policy columns, so later larger runs can mark any truncation as
non-interpretable rather than silently treating sorted-prefix output as full
topology.

Transport composition now separates:

```text
support composition
path-count composition
weighted-flow composition status
```

Weighted flow is marked `not_defined_unit_edge_weights_only` in this smoke.

## Calibration Readout

As a calibration fixture, the atlas still expresses the known rank-boundary
split as continuous geometry:

```text
rank_prefix:m=3                            operator distance 0.000
rank_prefix:m=4                            operator distance 0.188
rank_prefix:m=5                            operator distance 0.300
rank_subset:m=4:retain=1|2|3:remove=4      operator distance 0.000
rank_subset:m=5:retain=1|2|3:remove=4|5    operator distance 0.000
rank_subset:m=4:retain=2|3|4:remove=1      operator distance 0.375
```

The calibration fixture is downstream of the formal atlas object. It is not the
definition of the instrument.

## Interpretation

The package is now closer to publication-clean as an instrument:

```text
state space
candidate successor rule
energy/scoring law
selection operator
frontier scan
observable map
transport composition readout
calibration view
```

The next expansion should preserve this order. New empirical patterns should
add formal specs or observables first, then optional human-facing labels.
