# Omega Validation

This repository is the executable validation workspace for the Omega theory
project.

The current stance is deliberately modest:

> derive candidate mathematical objects, implement them, test them against
> controls, and record what fails.

## Current Pivot: VAL0-CT

The project has recently pivoted from bare field dynamics and cellular/rule
space probes toward a Constructor-Theory-style task-space validation layer.

Current working thesis:

```text
Omega is the compatibility structure of value-bearing trajectory space.
```

The current validation target is not full Omega. The next target is
**VAL0-CT**, a single-field proto-Omega probe in generated constructor-style
task algebras.

VAL0-CT asks:

```text
Does persistence-conditioned reachability, R1, predict long-horizon
reachability retention better than raw reachability, R0, and matched
R0-lookahead controls in structured task algebras?
```

This is intentionally narrower than the full theory. It tests whether reachable
task-space can remain future-bearing across horizons. If that fails, the current
proto-Omega operationalization is wrong or underspecified.

Start here for the current pivot:

- [VAL0-CT implementation spec](docs/research_notes/validation_design/val0_ct_implementation_spec.md)
- [VAL0-CT validation design](docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md)
- [Constructor Theory and Omega axiology](docs/research_notes/omega_theory/constructor_theory_and_omega_axiology.md)
- [Deriving Omega relevance from primitives](docs/research_notes/omega_theory/deriving_omega_relevance_from_primitives.md)
- [Current formal stack](docs/research_notes/omega_theory/formal_stack_v0.md)
- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)

## How To Read The Older Results

The older COM/fiber, trajectory-space, CA, DAR, and DAX probes are retained
because they document the path, controls, and failure modes that forced the
current pivot.

They should not be read as the current validation center.

Current interpretation:

- COM-like fiber transport is historical evidence for viable propagation and
  coarse-graining discipline.
- Trajectory-space probes are useful negative constraints and fakeout anatomy.
- CA/DAR/DAX probes calibrate the primitive floor: distinction, asymmetry, and
  causal continuity.
- DAX-G5 failed as a held-out predictive detector, which is part of why the
  project moved to task-space validation.

## Start Here

- [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
- [Running log](docs/OMEGA_RUNNING_LOG.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
- [Current theory draft](docs/current_theory/README.md)
- [Validation design notes](docs/research_notes/validation_design/README.md)
- [Omega theory notes](docs/research_notes/omega_theory/)
- [Primitive-branch notes](docs/research_notes/primitive_branch/README.md)
- [Progenitor drafts](docs/progenitor_drafts/README.md)

## Current Next Step

Implement the VAL0-CT smoke target, CPU-first:

```text
families:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

policies:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega

primary comparison:
  R1 vs R0 vs equal-budget R0_lookahead on long-horizon reachability retention
```

The first implementation should be lean. Get `R0` correct on toy graphs before
implementing `R1`. Do not add mixed generators, noise branching, embodied
agents, multifield coupling, or GPU acceleration until the first three
generator families are clean.

## Important Caveat

This repository does not prove Omega as a scientific theory. At present it
contains:

- theory notes and draft formalizations;
- historical toy-substrate probes;
- negative and ambiguous results;
- a current validation design for VAL0-CT.

The scientific value of the repo is in the controls and failure modes as much
as in any positive signal.

## Environment

Use the local virtual environment directly when working on the original machine:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

For CPU-heavy probes, the calibrated default is:

```text
18 worker processes
```

VAL0-CT should start CPU-first. GPU support is deferred until smoke runs show a
real dense batched reachability bottleneck.

For older GPU/CuPy work on the original machine, use `omega_env.bat` or run
`omega_env.ps1` with a PowerShell execution-policy bypass. The environment
scripts add Torch's bundled CUDA 13 NVRTC DLL directory to `PATH` and point
CuPy's kernel cache at `.cupy-cache/`.

## Historical Result Sets

The public tree keeps compact historical outputs that matter for provenance and
failure analysis. They are no longer the current center:

- `probe_09_robust_fiber_reachability_results/`
- `probe_10_com_viable_propagation_robustness_extended_results/`
- `probe_10_com_targeted_fragility_refinement_results/`
- `probe_11_learned_predictive_kappa_revised_results/`
- `probe_12_batch_results/`
- `probe_12a_com_formal_object_audit_results/`
- `probe_12b_learned_kappa_failure_diagnosis_results/`
- `probe_12c_improved_learner_smoke_results/`
- `probe_T0_trajectory_space_branch_triage_results/`
- `probe_T1_viable_trajectory_geometry_results/`
- `probe_T1F_ordered_trajectory_structure_atlas_results/`
- `probe_I0_invariant_stack_audit_results/`
- `probe_I0b_invariant_threshold_dropout_audit_results/`
- `probe_13b_fiber_transport_false_positive_refinement_results/`
- `probe_DA0_distinction_asymmetry_relation_results/`
- `probe_DA0b_relational_connection_closure_results/`
- `probe_DA1_viable_slack_phase_sweep_results/`
- `probe_DA1b_apparent_vs_viable_slack_results/`
- `probe_DA1c_noncommutative_relational_history_results/`
- `probe_DA2_relational_edge_memory_world_results/`
- `probe_DA2_relational_edge_memory_world_revision_results/`
- `probe_DAX_branching_connection_graph_validity_revised_results/`
- `probe_DAX_G0_minimal_DAR_rule_space_persistence_results/`
- `probe_DAX_G1_persistence_motif_anatomy_and_robustness_results/`
- `probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results/`
- `probe_DAX_G2b_control_adjusted_primitive_guardrail_results/`
- `probe_DAX_G3_q3r1_guardrailed_phase_map_results/`
- `probe_DAX_G4_q3r1_motif_ecology_mechanism_results/`
- `probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results/`

Historical scripts remain in the repository because they document how the
current state was reached. New work should normally start from the VAL0-CT
validation design unless deliberately revisiting an older branch.
