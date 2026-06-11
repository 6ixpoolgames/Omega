# Validation

This repository has an observed-passing GitHub Actions workflow for the Lean
formal stack and a path-scoped Python workflow for the baseline witness smoke:

```text
workflow: Lean AlphaOmega
latest observed passing run:
https://github.com/6ixpoolgames/Omega/actions/runs/27317368267

workflow: Baseline Witness Smoke
latest observed passing run:
https://github.com/6ixpoolgames/Omega/actions/runs/27324231940
```

The workflow badge in the root README links to the public Actions history.

## What CI Checks

The Lean workflow checks:

```text
Elan installation
Mathlib cache fetch via lake exe cache get
AlphaOmega build
sorry / admit / axiom scan
git diff --check
```

The baseline witness workflow checks:

```text
Python 3.11 package installation with dev tools
baseline witness smoke
baseline smoke mutation tests
reachability nuisance-bit family tests
mutual-information nuisance-bit family tests
optimized-success coordinate-family tests
Ruff over baseline witness modules and focused tests
git diff --check
```

The workflow is intentionally path-scoped. It runs automatically for changes to:

```text
.github/workflows/lean-alphaomega.yml
formal/lean/**
scripts/setup/invoke_lake.ps1
```

The baseline witness workflow is also path-scoped. It runs automatically for
changes to:

```text
.github/workflows/baseline-witness-smoke.yml
omega/baseline_witnesses/**
omega/future_field_atlas/util.py
tests/test_mutual_information_declared_recovery_family.py
tests/test_optimized_success_declared_recovery_family.py
tests/test_reachability_declared_recovery_family.py
tests/test_same_*.py
scripts/validation/run_baseline_witness_smoke.ps1
results/baseline_witnesses/**
pyproject.toml
```

Docs-only pushes do not run the full Lean job automatically. Use the manual
`workflow_dispatch` entrypoint on GitHub when a full remote validation run is
wanted after non-Lean changes.

## Local Checks

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

For Python-side checks:

```powershell
pytest
ruff check .
```

## Reproducibility Smoke

The baseline witness batch has a one-command reproduction path:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1
```

It reruns the seven retained baseline witnesses, checks regenerated summary
digests against committed retained summaries, and runs the focused witness
tests. See [BASELINE_WITNESS_SMOKE.md](BASELINE_WITNESS_SMOKE.md).

The registry-first stochastic-channel branch has a separate reproduction path:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1
```

See [REPRODUCIBILITY_SMOKE.md](REPRODUCIBILITY_SMOKE.md).

## Claim Hygiene

For the current theorem/result/conjecture split, see
[CLAIMS_LEDGER.md](CLAIMS_LEDGER.md).

For the current reduction map and baseline-controlled witness obligations, see
[KNOWN_REDUCTIONS_AND_BASELINES.md](KNOWN_REDUCTIONS_AND_BASELINES.md).

## Connector Caveat

Some connector surfaces report no workflow runs or combined statuses for push
commits. That is not authoritative for this repository's CI state:

```text
GitHub Actions creates check runs, not necessarily classic commit statuses.
The available connector workflow-run helper filters to pull-request-triggered
runs, while normal repository validation currently runs on push events.
```

For external validation, use the GitHub Actions workflow page, README badge, or
the GitHub Actions/check-runs API.
