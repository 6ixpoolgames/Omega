# Future Field Atlas Phase 0/1 Publication-Schema Smoke Result

Status: clean instrument-build smoke completed after publication-schema audit
Primary output: `results/future_field_atlas/20260601_phase0_1_publication_audit_h32/`
Runner: `omega.future_field_atlas.run_future_field_atlas`
Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
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
elapsed_seconds: 20.551
errors: 0
horizon_max: 32
frontier_node_rows: 30671
frontier_edge_rows: 107034
selection_operator_geometry_rows: 8
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
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

The smoke also emitted formal spec and condition identity manifests:

```text
formal_spec_manifest.csv
condition_identity_manifest.csv
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
weighted-mass composition status
```

Weighted mass is marked `not_defined_unit_edge_weights_only` in this smoke.
Composition rows include an explicit label-alignment policy so zero residual is
not used as a substitute for a skipped comparison.

## Reconstruction Audits

All required reconstruction audits passed:

```text
condition_identity_traceability: PASS
frontier_profile_reconstructs_from_node_and_edge_rows: PASS
rank_boundary_geometry_reconstructs_from_edge_rows: PASS
adjacent_transport_matrices_reconstruct_from_edge_rows: PASS
selection_operator_geometry_reconstructs_from_rank_boundary_rows: PASS
```

Completeness distribution:

```text
frontier_nodes_by_horizon.csv: complete, 30671 rows
frontier_edges_by_step.csv: complete, 107034 rows
frontier_profile_by_horizon.csv: complete, 264 rows
```

## Calibration Readout

As a calibration fixture, the atlas still expresses the known rank-boundary
split as continuous geometry:

```text
rank_prefix:m=3                            operator distance 0.000
rank_prefix:m=4                            operator distance 0.250
rank_prefix:m=5                            operator distance 0.400
rank_subset:m=4:retain=1|2|3:remove=4      operator distance 0.000
rank_subset:m=5:retain=1|2|3:remove=4|5    operator distance 0.000
rank_subset:m=4:retain=2|3|4:remove=1      operator distance 0.389
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
