# RFS-MB0 Horizon-Transport Spectral Response Repair Result

Date: 2026-05-30

## Executive Summary

Implemented the first horizon-transport spectral response repair instrument.
This is a conceptual reorientation, not a large theory pivot: it adds a
directional `horizon_transport` matrix family and enforces the new control
taxonomy:

```text
detector nulls test the detector;
perturbations describe candidate response geometry;
destructive response is not ordinary negative evidence.
```

Two tight validation smokes were run locally.

Underpowered-null contract:

```text
local output: results/local_runs/20260530_horizon_transport_repair_contract_smoke_v4_underpowered/
jobs_completed: 10
errors: 0
matrix_count: 140
manifest: 21 / 21 present
null_replicates: 2
readiness_level: not_ready_repair_required
next_action_fork: repair_transport_null_controls
blocking_reason: detector_null_replicates_underpowered
```

Powered contract:

```text
local output: results/local_runs/20260530_horizon_transport_repair_contract_smoke_v5_powered/
jobs_completed: 10
errors: 0
matrix_count: 140
detector_null_rows: 252
perturbation_response_rows: 112
manifest: 21 / 21 present
null_replicates: 3
readiness_level: ready_for_horizon_transport_smoke_expansion
next_action_fork: expand_horizon_transport_smoke
```

The key repair validation is that the underpowered smoke no longer overclaims.
The instrument blocks detector-null advancement when null replicates are below
the minimum, even if some null comparisons look favorable.

The powered validation suggests the new object is mechanically live enough for a
slightly larger smoke, but this is still instrumentation evidence only. It is
not Omega detection, agency detection, value detection, or graph-channel causal
evidence.

Artifact policy: generated CSV/JSON outputs remain local-only under
`results/local_runs/` and are not committed.

## Claim Boundary

This was an instrument repair and contract validation pass.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, valuer detection, value detection, or graph-level
causal evidence.

Counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## Control Taxonomy Compliance

Every matrix/response row now carries:

```text
intervention_class
intervention_family
intervention_name
intervention_strength
interpretation_role
allowed_claim_level
```

Observed taxonomy behavior:

```text
baseline:
  intervention_class: baseline
  interpretation_role: instrumentation_only
  allowed_claim_level: instrumentation_only

small nonlethal perturbations:
  intervention_class: nonlethal_perturbation
  interpretation_role: candidate_response_profile
  allowed_claim_level: response_profile_only
```

Detector-null outputs are separate from perturbation-response outputs:

```text
horizon_transport_detector_null_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv

horizon_transport_perturbation_manifest.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
```

## Horizon-Transport Matrix Construction

The runner builds rectangular directional matrices from existing
frontier-transform transition rows:

```text
matrix_family: horizon_transport
rows: source-side probe signatures at H_a
columns: target-side probe signatures at H_b
entries: transport counts
spectral method: SVD
```

Validation smoke matrix count:

```text
140
```

Required matrix outputs were present:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_row_item_manifest.csv
horizon_transport_column_item_manifest.csv
horizon_transport_coverage.csv
horizon_transport_matrix_summary.csv
```

## Detector-Null Results

Implemented first detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
label_shuffle_transport_interpretation_control
```

The underpowered validation confirms the repair guard:

```text
G0 horizon_transport_matrix_coverage: passed
G1 detector_null_sections_separate: passed
G2 structure_detector_null_separation: failed
G3 detector_null_replicate_power: failed

observed null_replicates: 2
blocking_reason: detector_null_replicates_underpowered
```

The powered validation confirms the normal path:

```text
G0 horizon_transport_matrix_coverage: passed
G1 detector_null_sections_separate: passed
G2 structure_detector_null_separation: passed
G3 detector_null_replicate_power: passed

observed null_replicates: 3
```

Read:

```text
The detector-null contract is now doing useful work: small plumbing tests can
validate outputs without silently becoming powered detector claims.
```

## Perturbation-Response Results

Powered contract response classes:

```text
transport_stable: 109
transport_control_equivalent: 3
```

Interpretation:

```text
Tiny nonlethal perturbations mostly left the transport response profile stable
at this small scale. This is response geometry only, not a detector-null claim.
```

## Horizon-Pair Comparison

The runner emits:

```text
horizon_transport_subspace_alignment.csv
```

This records baseline horizon-pair subspace alignments by probe and flow mode.
It is intended as a diagnostic for later narrowing/expansion, not a standalone
claim.

## Readiness Levels

Underpowered contract:

```text
ready_for_horizon_transport_smoke_expansion: 0
ready_for_fixture_horizon_transport_tests: 0
ready_for_direct_channel_diagnostics: 0
not_ready_repair_required: 1
```

Powered contract:

```text
ready_for_horizon_transport_smoke_expansion: 1
ready_for_fixture_horizon_transport_tests: 0
ready_for_direct_channel_diagnostics: 0
not_ready_repair_required: 0
```

## Next-Action Fork

For the repair step just completed:

```text
instrument repair validated
```

For the next empirical step:

```text
expand_horizon_transport_smoke
```

Recommended scope:

```text
slightly larger laptop-safe smoke;
keep detector nulls and response profiles separate;
retain null replicate power gate;
do not run graph perturbation;
do not promote candidate claims.
```

## Output Manifest

Local-only validation outputs:

```text
results/local_runs/20260530_horizon_transport_repair_contract_smoke_v4_underpowered/
results/local_runs/20260530_horizon_transport_repair_contract_smoke_v5_powered/
```

Key local files:

```text
horizon_transport_repair_status.json
horizon_transport_repair_output_manifest.json
horizon_transport_matrix_manifest.csv
horizon_transport_matrix_summary.csv
horizon_transport_svd_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
rfs_mb0_horizon_transport_spectral_response_repair_result.md
```
