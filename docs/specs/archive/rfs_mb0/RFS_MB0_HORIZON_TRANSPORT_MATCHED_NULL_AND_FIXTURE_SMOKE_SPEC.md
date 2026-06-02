# RFS-MB0 Horizon-Transport Matched Null and Fixture Smoke Spec

Status: small instrumentation repair addendum
Extends: `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_SPECTRAL_RESPONSE_REPAIR_SPEC.md`
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. Purpose

Before any larger horizon-transport expansion, add matched marginal detector
nulls and tiny synthetic fixtures that test whether the instrument is measuring
transport association rather than row/column mass geometry with a spectral
wrapper.

This is smaller than an expansion run. It is a control and fixture repair.

## 1. Required Repair

Add detector-null families:

```text
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Add a detector statistic:

```text
marginal_residual_fraction
```

This statistic is the normalized residual between the observed transport matrix
and the independence matrix implied by its row and column marginals.

## 2. Required Fixture Smoke

The fixture smoke must include:

```text
block_transport_signal:
  true association beyond row/column marginals should separate

marginal_fakeout:
  pure row/column mass geometry should not pass the bimarginal matched null

corridor_stable_response:
  tiny nonlethal perturbation should classify as transport_stable

trap_collapse_response:
  collapse perturbation should classify as transport_collapses
```

The fixture smoke is a runner contract test. It is not empirical evidence.

## 3. Required Gates

The runner must report:

```text
G0 horizon_transport_matrix_coverage
G1 detector_null_sections_separate
G2 structure_detector_null_separation
G3 detector_null_replicate_power
G4 matched_marginal_detector_null_separation
G5 synthetic_fixture_contract
```

`G4` must require row, column, and bimarginal matched families to pass on
`marginal_residual_fraction` before the instrument can report readiness for a
larger horizon-transport smoke.

`G5` is required only when the synthetic fixture smoke is enabled.

## 4. Required Outputs

The runner must emit:

```text
horizon_transport_detector_null_summary.csv
horizon_transport_detector_null_anatomy.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_fixture_results.csv
horizon_transport_response_profile_summary.csv
horizon_transport_response_classification.csv
```

Generated CSV/JSON outputs remain local-only under `results/local_runs/`.

## 5. Decision Rule

If matched marginal nulls erase the empirical signal, repair again before any
larger smoke.

If fixtures fail, repair again before any larger smoke.

If matched marginal nulls pass and fixtures pass, the next step may be a
slightly larger horizon-transport smoke, still without candidate promotion or
graph-channel causal claims.
