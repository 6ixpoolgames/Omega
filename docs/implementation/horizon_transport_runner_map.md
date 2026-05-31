# Horizon-Transport Runner Map

Status: implementation maintenance note  
Scope: RFS-MB0 horizon-transport branch  
Claim boundary: code organization only; not a new validation result

## Live object

The current runner instruments:

```text
matched-marginal-separated horizon transport
with horizon-dependent perturbation response classes
```

It does not classify agents, valuers, identity, or Omega-compatible structure.

## Code map

```text
omega/rfs_mb0_future_landscape/horizon_transport_contracts.py
  Stable spec IDs, output filenames, horizon-pair defaults, detector-null family
  names, detector statistics, and run-kind naming.

omega/rfs_mb0_future_landscape/horizon_transport_response_taxonomy.py
  Fixture-backed response thresholds, response class constants, response flags,
  and classify_response().

omega/rfs_mb0_future_landscape/run_horizon_transport_spectral_response_repair.py
  Heavy orchestration runner. It builds jobs, collects matrices, applies nulls,
  computes response tables, writes reports, and handles graceful shutdown.

omega/rfs_mb0_future_landscape/run_stage_b2_spectral_future_field_geometry_smoke.py
  Upstream Stage B-2 matrix machinery and batch execution used by the
  horizon-transport runner.

omega/rfs_mb0_future_landscape/spectral_contracts.py
  Shared claim-boundary and artifact-policy metadata.
```

## Maintenance rules

1. Keep detector-null controls separate from perturbation-response profiles.
   Nulls test the instrument; perturbations map candidate response behavior.

2. Treat response-class thresholds as fixture-backed contracts. If a threshold
   changes, update the synthetic fixtures and run fixture smoke before any
   larger empirical run.

3. Keep claim language neutral in code and reports. The runner may say
   `transport_stable`, `transport_amplified_aligned`, `transport_weakened`,
   `transport_rerouted`, `transport_reopens`, `transport_collapses`, or
   `transport_control_equivalent`. It should not emit Omega, agency, identity,
   valuerhood, or promotion claims.

4. Preserve graceful exits. Long runs must write status, partial checkpoints,
   errors, manifests, and enough CSV data to diagnose interrupted runs.

5. Keep large generated artifacts under `results/local_runs/` unless a retained
   result note or curated public artifact is explicitly chosen for the repo.

## Minimal verification

After touching horizon-transport code, run at least:

```powershell
.venv\Scripts\python.exe -m py_compile omega\rfs_mb0_future_landscape\horizon_transport_contracts.py omega\rfs_mb0_future_landscape\horizon_transport_response_taxonomy.py omega\rfs_mb0_future_landscape\run_horizon_transport_spectral_response_repair.py omega\rfs_mb0_future_landscape\run_stage_b2_spectral_future_field_geometry_smoke.py
```

For response taxonomy changes, also run a fixture smoke:

```powershell
.venv\Scripts\python.exe -m omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair --out results\local_runs\maintenance_fixture_smoke --fixture-smoke --h128-scaleup --null-replicates 11
```
