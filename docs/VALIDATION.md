# Validation

This repository has an always-on lightweight GitHub Actions router plus
path-scoped heavyweight workflows for the Lean formal stack and baseline witness
smoke:

```text
workflow: Validation Router
purpose:
  runs on every push and pull request to master;
  checks whitespace over the changed diff;
  reports whether changed paths fall under the Lean or baseline witness scopes.

workflow: Lean AlphaOmega
latest observed passing run:
https://github.com/6ixpoolgames/Omega/actions/runs/27317368267

workflow: Baseline Witness Smoke
latest observed passing run:
https://github.com/6ixpoolgames/Omega/actions/runs/27324231940
```

The workflow badge in the root README links to the public Actions history.

## What CI Checks

The Validation Router workflow checks:

```text
changed-file resolution for the pushed/PR diff
git diff --check over that diff
path routing summary for the heavyweight workflows
classic commit status publication for connector-readable validation
```

It is intentionally cheap and always-on. It exists so every pushed head has a
visible external check even when the full Lean or baseline witness workflows are
skipped by path filters. It also publishes a classic commit status named
`Validation Router` because some connector surfaces read classic statuses but do
not reliably expose GitHub Actions check runs.

The Lean workflow checks:

```text
Elan installation
Mathlib cache fetch via lake exe cache get
AlphaOmega build
sorry / admit / axiom scan
git diff --check
```

The baseline witness workflow runs on Windows, Ubuntu, and macOS and checks:

```text
Python 3.11 package installation with dev tools
baseline witness smoke
baseline witness family smoke
baseline smoke mutation tests
baseline witness adversarial search tests
chain-evidence class-soundness family tests
coarse-bisimulation consequence-profile family tests
compression-vs-soundness nuisance-bit family tests
control-reach declared-recovery family tests
entropy-profile nuisance-bit family tests
frontier-morphology loss-profile family tests
intervention-effect declared-recovery family tests
marginal-vs-joint nuisance-bit family tests
reachability nuisance-bit family tests
mutual-information nuisance-bit family tests
observation-rank nuisance-bit family tests
optimized-success coordinate-family tests
viability-kernel declared-recovery family tests
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
omega/validation/**
tests/test_chain_evidence_class_soundness_family.py
tests/test_coarse_bisimulation_consequence_profile_family.py
tests/test_compression_score_merge_soundness_family.py
tests/test_control_reach_declared_recovery_family.py
tests/test_entropy_recovery_profile_family.py
tests/test_frontier_morphology_loss_profile_family.py
tests/test_intervention_effect_declared_recovery_family.py
tests/test_marginal_success_joint_success_family.py
tests/test_mutual_information_declared_recovery_family.py
tests/test_observation_rank_declared_recovery_family.py
tests/test_optimized_success_declared_recovery_family.py
tests/test_reachability_declared_recovery_family.py
tests/test_viability_kernel_declared_recovery_family.py
tests/test_baseline_witness_family_smoke.py
tests/test_same_*.py
scripts/validation/run_baseline_witness_family_smoke.ps1
scripts/validation/run_baseline_witness_smoke.ps1
results/baseline_witnesses/**
pyproject.toml
```

Docs-only pushes do not run the full Lean job automatically. Use the manual
`workflow_dispatch` entrypoint on GitHub when a full remote validation run is
wanted after non-Lean changes. Docs-only pushes still run the Validation Router,
so they should no longer look externally unvalidated.

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

```bash
python -m omega.validation.baseline_witness_smoke
```

Windows PowerShell wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1
```

It reruns the thirteen retained baseline witnesses, checks regenerated summary
digests against committed retained summaries, and runs the focused witness
tests. See [BASELINE_WITNESS_SMOKE.md](BASELINE_WITNESS_SMOKE.md).

The parameterized baseline witness families have a separate one-command smoke:

```bash
python -m omega.validation.baseline_witness_family_smoke
```

Windows PowerShell wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1
```

It checks all thirteen parameterized families at the default `k = 1..5`, covers 165
finite family cases, and runs the focused family tests. See
[BASELINE_WITNESS_FAMILY_SMOKE.md](BASELINE_WITNESS_FAMILY_SMOKE.md).

The registry-first stochastic-channel branch has a separate reproduction path:

```bash
python -m omega.validation.registry_first_smoke
```

Windows PowerShell wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1
```

The finite relational adapter has a focused smoke path:

```bash
python -m omega.validation.finite_relational_adapter_smoke
```

Generated/adversarial adapter cases have a separate retained-output path:

```bash
python -m omega.validation.finite_relational_adapter_adversarial
```

Local PowerShell form:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp\finite_relational_adapter_smoke
```

It runs the low-level finite relational IR fixtures, derived graph fixtures, and
finite grid fixtures. It checks provenance completeness, verifies retained
digest/audit artifacts, exercises phantom reachability and hidden reachability
loss controls, and runs the focused adapter tests unless `--skip-pytest` is
provided.

The generated/adversarial path deterministically searches small finite cases
for adapter hardening witnesses, then retains each generated source, compiled
model, digests, audit results, and summary. These cases do not validate a real
substrate; they check that the adapter machinery can find and audit expected
finite failure modes without relying only on hand-written fixtures.

Finite relational adapter changes are also protected by the
`Finite Relational Adapter Smoke` GitHub Actions workflow.

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
