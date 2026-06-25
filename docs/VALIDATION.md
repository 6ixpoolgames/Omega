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

For the finite recovery theorem spine, the focused Lean target is:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper.Recovery
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

The first controlled synthetic empirical pilot has its own retained-output path:

```bash
python -m omega.validation.finite_relational_adapter_empirical
```

The gridworld obstacle-insertion characterization has a separate retained-output path:

```bash
python -m omega.validation.finite_relational_grid_obstacle
```

The graph-pair transfer characterization has a separate retained-output path:

```bash
python -m omega.validation.finite_relational_graph_pair_transfer
```

The deterministic pre-stochastic finite relational layer has its own
retained-output path:

```bash
python -m omega.validation.finite_relational_deterministic_layer
```

The exact rational stochastic recovery characterization layer has its own
retained-output path:

```bash
python -m omega.validation.finite_relational_stochastic_recovery
```

The finite-horizon stochastic continuation-loss layer has its own
retained-output path:

```bash
python -m omega.validation.finite_relational_stochastic_continuation
```

The policy-conditioned finite stochastic dynamics layer has its own
retained-output path:

```bash
python -m omega.validation.finite_relational_policy_dynamics
```

The finite relational source-parity layer has its own retained-output path:

```bash
python -m omega.validation.finite_relational_source_parity
```

The operational-causal-diamond agency-layer pilot has its own retained-output
path:

```bash
python -m omega.validation.agency_diamond_midscale
```

This is a synthetic finite null battery for the agency-layer harness. It checks
whether the declared examples separate passive persistence, driven recurrence,
control without feedback advantage, feedback advantage over matched open-loop
replay, reflexive maintenance, and joint-continuation effect. It is not agency,
identity, value, valuerhood, or Omega validation.

Local PowerShell form:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp\finite_relational_adapter_smoke
```

It runs the low-level finite relational IR fixtures, derived graph fixtures, and
finite grid fixtures. It checks provenance completeness, verifies retained
digest/audit artifacts, exercises phantom reachability and hidden reachability
loss controls, runs non-factorization controls for simple-form, entropy, and
ordered-trace summaries, exercises bounded-recovery pass/fail controls, and
runs the focused adapter tests unless `--skip-pytest` is provided. The focused
tests now cover the shared source-contract helper: graph, grid, grid-obstacle,
and generated graph-pair sources may declare substrate-level syntax, but they
must not smuggle reserved finite relational IR fields such as predicates,
relations, functions, profiles, or audits.

The generated/adversarial path deterministically searches small finite cases
for adapter hardening witnesses, then retains each generated source, compiled
model, digests, audit results, and summary. These cases do not validate a real
substrate; they check that the adapter machinery can find and audit expected
finite failure modes without relying only on hand-written fixtures. The current
generated suite includes phantom reachability, hidden reachability loss, proxy
non-factorization, derived graph asymmetry, derived graph carrier
certification, finite grid asymmetry, and presentation/fact closure shrinkage
for a derived carrier pair plus generated reachability, viability, and
recovery-style target facts, stale/reflected reach-status facts, and
multi-presentation row/column fact intersections. The closure stress suite also
includes a crosscutting row/column/parity family where each presentation
preserves a different fact but the full family keeps only the constant target
and no ordered visible state pairs. The transport checks include graph-pair
source cases that compile source and target graphs separately before auditing
positive transfer and a missing-return negative control, plus transported
endpoint-role facts under a carrier-transfer contract and a failed-transfer
label-closure control.
The observed-word lifting controls check the finite process-coherence contract
needed before abstract observed-word counts can be trusted: a positive case
satisfies lifting and observation compatibility, while a negative case has
global edge projection exactness but fails path lifting and inflates abstract
observed words.

The fact generators behind these audits are split by theory surface
(`facts_dynamics.py`, `facts_language.py`, `facts_presentation.py`,
`facts_recovery.py`, and `facts_carrier.py`) while the public
`omega.adapters.finite_relational.facts` path remains a compatibility facade.
Adapter smoke should exercise the facade and the split modules together.

The closure-discovery path is distinct from the expectation-pinned
generated/adversarial closure fixtures:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_closure_discovery `
  --out-root .tmp\finite_relational_closure_discovery
```

It generates all small seed cases in three finite families, computes
presentation/fact derive closure, and classifies whether nonconstant surplus
facts appear without predeclaring expected surplus. The current retained sweep
covers predicate seeds, reachability-derived seeds, and viability-derived
seeds. It reports 136 total cases, with both nonconstant-surplus and collapse
controls.

The controlled empirical path enumerates fixed small finite families and reports
rates/frequencies for selected proxy failures:

```text
same observation histogram vs bounded recovery;
same unordered trace bag vs order-sensitive recovery;
stale abstraction hiding exact reachability loss;
endpoint forward reachability without recurrent carrier certification.
```

These are synthetic finite-substrate empirics. They are not external validation
of a real system.

The gridworld obstacle path declares finite grid interfaces, generates obstacle
insertions, compiles before/after/stale abstract transitions into finite
relational IR, audits hidden reachability loss, and checks presentation/fact
closure over source-reachability status. The current characterization covers a
3x3 orthogonal midline case, a 3x3 directed east/south diagonal case, and a 4x2
orthogonal rectangle case. Each study retains a hidden-loss representative and a
no-hidden-loss control. The retained representatives include reflected
after-reachability status that preserves `after_reachable_from_source` and a
stale/reflected presentation family whose common target facts drop that
after-reachability predicate. It is the first source-generator characterization beyond
low-level handwritten IR fixtures.

The graph-pair transfer path declares source and target graph interfaces plus
an endpoint correspondence, compiles both graphs separately into finite
relational IR, and audits carrier transfer over the compiled pair. The current
characterization covers a two-node target sweep and a three-node target
extension sweep. It reports how often the target graph preserves enough
recurrent carrier structure for transfer under the fixed correspondence, and it
retains controls where target forward endpoint reachability survives but
carrier transfer still fails.

The deterministic pre-stochastic path calibrates exact finite recovery before
probabilistic or approximate audits are added. It checks joint bounded recovery
failure, decoder-class strictness, observation-refinement monotonicity,
deterministic garbling non-improvement, minimal sufficient observations, and
reflected-versus-stale hidden loss.

The stochastic recovery characterization path uses exact rational finite
channels. It reports support ambiguity, support-exact recovery, optimized
worst-case deterministic decoder success, declared-versus-optimized decoder
gaps, deterministic coarsening behavior, failure localization,
marginal-versus-joint recovery, paired-decoder union-bound floors, declared
randomized decoder behavior, declared finite randomized-family optimization,
and robust randomized ambiguity-set behavior. It does not validate empirical
channel correctness or global randomized optimization.

The stochastic continuation path uses exact rational finite transition kernels
and finite-horizon hit probabilities. It checks stale-versus-reflected hidden
hit-probability loss, runs a presentation/fact closure audit over reflected
versus stale hit-status facts, and retains horizon profiles so one selected
probability does not stand in for the whole continuation surface.

The policy-conditioned path adds finite actions and deterministic policies over
exact rational transition kernels. It retains generated `facts.json` separately
from `hypotheses.json`, then checks stale/reflected policy loss and a
policy-conditioned presentation/fact closure case, a non-factorization witness
through a coarse support summary, and a declared policy-family robust hit
calculation. The current joint robustness stress case uses nominal and
correlated-shock kernels: target A and target B each have a robust declared
policy, but no declared policy robustly attains the joint target.

The source-parity path compiles equivalent derived-graph and finite-grid
sources into the same finite relational IR surface, then checks matching
relations, predicates, functions, and audit findings after declared state
renaming. Current cases cover strict asymmetry, recurrent carrier
certification, and source-derived observation-target closure.

Finite relational adapter changes are also protected by the
`Finite Relational Adapter Smoke` GitHub Actions workflow.

A retained example summary is available at
[finite_relational_adapter_validation_v0.md](research_notes/validation_results/finite_relational_adapter_validation_v0.md).
The bounded-useful-structure extension also retains a machine-readable summary
at
[finite_relational_adapter_useful_information_v0.json](research_notes/validation_results/finite_relational_adapter_useful_information_v0.json).
The first controlled empirical pilot retains a machine-readable summary at
[finite_relational_adapter_empirical_pilot_v0.json](research_notes/validation_results/finite_relational_adapter_empirical_pilot_v0.json).
The gridworld obstacle-insertion characterization retains a machine-readable
summary at
[finite_relational_grid_obstacle_pilot_v0.json](research_notes/validation_results/finite_relational_grid_obstacle_pilot_v0.json).
The graph-pair transfer characterization retains a machine-readable summary at
[finite_relational_graph_pair_transfer_v0.json](research_notes/validation_results/finite_relational_graph_pair_transfer_v0.json).
The deterministic pre-stochastic layer retains a machine-readable summary at
[finite_relational_deterministic_layer_v0.json](research_notes/validation_results/finite_relational_deterministic_layer_v0.json).
The stochastic recovery characterization layer retains a machine-readable
summary at
[finite_relational_stochastic_recovery_v0.json](research_notes/validation_results/finite_relational_stochastic_recovery_v0.json).
The stochastic continuation-loss layer retains a machine-readable summary at
[finite_relational_stochastic_continuation_v0.json](research_notes/validation_results/finite_relational_stochastic_continuation_v0.json).
The policy-conditioned stochastic dynamics layer retains a machine-readable
summary at
[finite_relational_policy_dynamics_v0.json](research_notes/validation_results/finite_relational_policy_dynamics_v0.json).
The finite relational source-parity layer retains a machine-readable summary at
[finite_relational_source_parity_v0.json](research_notes/validation_results/finite_relational_source_parity_v0.json).
The operational-causal-diamond agency-layer pilot retains a human-readable note
and machine-readable summary at
[agency_diamond_midscale_v0.md](research_notes/validation_results/agency_diamond_midscale_v0.md)
and
[agency_diamond_midscale_v0.json](research_notes/validation_results/agency_diamond_midscale_v0.json).

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
