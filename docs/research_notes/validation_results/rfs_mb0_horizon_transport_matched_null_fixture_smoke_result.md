# RFS-MB0 Horizon-Transport Matched Null and Fixture Smoke Result

Date: 2026-05-30

## Executive Summary

Implemented the matched-null and fixture repair for the horizon-transport
instrument. The runner now tests whether transport spectra survive
row/column-marginal explanations, and it has a synthetic fixture mode that
checks both detector-null behavior and response-profile taxonomy.

This is an instrumentation result only. It is not holdout validation, Omega
detection, agency detection, identity detection, valuer detection, value
detection, candidate promotion, or graph-channel causal evidence.

Local-only outputs:

```text
results/local_runs/20260530_horizon_transport_matched_null_fixture_smoke/
results/local_runs/20260530_horizon_transport_matched_null_empirical_tiny_smoke/
results/local_runs/20260530_horizon_transport_matched_null_fixture_underpowered_guard/
```

Artifact policy: generated CSV/JSON outputs remain local-only under
`results/local_runs/` and are not committed.

## Repair Implemented

Added matched detector-null families:

```text
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Added detector statistic:

```text
marginal_residual_fraction
```

This measures residual association after subtracting the independence matrix
implied by the row and column marginals. It directly targets the concern that
horizon transport might only be seeing row/column mass geometry.

Added a new gate:

```text
G4 matched_marginal_detector_null_separation
```

Readiness for expansion now requires this gate to pass.

## Fixture Smoke

Command:

```powershell
C:\Users\paolo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair --fixture-smoke --out results/local_runs/20260530_horizon_transport_matched_null_fixture_smoke --null-replicates 5 --workers 1 --max-runtime-seconds 300 --shutdown-cushion-seconds 30
```

Result:

```text
status: COMPLETED
elapsed_seconds: 0.904
matrix_count: 6
detector_null_rows: 96
fixture_result_rows: 4
perturbation_response_rows: 2
errors: 0
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract_passed: 1
readiness_level: fixture_contract_passed
next_action_fork: run_empirical_matched_null_plumbing_smoke
```

Fixture contract:

```text
block_transport_signal: passed
marginal_fakeout: passed
corridor_stable_response: passed
trap_collapse_response: passed
```

Interpretation:

```text
The fixture mode accepts a true association-beyond-marginals case, rejects a
pure marginal fakeout under the bimarginal matched null, keeps a tiny corridor
perturbation stable, and classifies a trap collapse as collapse.
```

## Tiny Empirical Plumbing Smoke

Command:

```powershell
C:\Users\paolo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair --out results/local_runs/20260530_horizon_transport_matched_null_empirical_tiny_smoke --groups 2 --design-groups 1 --fresh-seeds-per-group 1 --start-samples-list 2 --probes constraint_profile_hash --small-edge-resample-strengths 0.0025 --asymmetric-edge-flip-strengths= --null-replicates 3 --workers 4 --job-batch-size 1 --checkpoint-every-jobs 4 --max-runtime-seconds 600 --shutdown-cushion-seconds 60
```

Result:

```text
status: COMPLETED
elapsed_seconds: 0.936
jobs_completed: 2
errors: 0
matrix_count: 28
detector_null_rows: 336
fixture_result_rows: 0
perturbation_response_rows: 14
matched_marginal_detector_null_gate_passed: 1
readiness_level: ready_for_horizon_transport_smoke_expansion
```

Matched marginal detector-null read:

```text
row_marginal_matched_transport_null / marginal_residual_fraction:
  pass_fraction: 0.7143

column_marginal_matched_transport_null / marginal_residual_fraction:
  pass_fraction: 0.7857

row_column_marginal_matched_transport_null / marginal_residual_fraction:
  pass_fraction: 0.9286
```

Interpretation:

```text
The empirical path still runs with the new stricter gate, and this tiny smoke
does not show immediate collapse under row/column-marginal controls. This is a
plumbing and readiness result only; the run is too small to carry scientific
weight.
```

## Underpowered Guard

The fixture mode was rerun with `null_replicates: 2`.

```text
readiness_level: not_ready_repair_required
detector_null_gate_passed: 0
detector_null_replicate_powered: 0
matched_marginal_detector_null_gate_passed: 0
blocking_reason: detector_null_replicates_underpowered
```

This confirms the earlier underpowered-null guard still blocks readiness after
the matched-null repair.

## Decision

The matched-null and fixture repair is complete enough to proceed to a slightly
larger horizon-transport smoke.

The next run should still be conservative: no graph perturbation, no candidate
promotion, no Omega/agency/value claims. The question is only whether the
horizon-transport signal remains interesting under matched marginal controls at
a larger but still laptop-safe scale.
