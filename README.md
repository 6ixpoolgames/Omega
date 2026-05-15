# Omega Validation

This repository contains the executable validation workspace for the Omega
theory project.

The current goal is modest and scientific:

> extract candidate mathematical objects, test them against controls, and record
> what survives.

The strongest current toy-substrate candidate is:

```text
COM-like multi-step viable propagation through certified fibers
```

In plain terms: coupled futures are interesting here not because they are
maximally entropic, but because viable structure can be propagated through
certified macro-fibers while preserving component information.

## Start Here

- [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
- [Running log](docs/OMEGA_RUNNING_LOG.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
- [Current theory draft](docs/current_theory/README.md)
- [Trajectory-space research notes](docs/research_notes/trajectory_space/README.md)
- [Primitive-branch research notes](docs/research_notes/primitive_branch/promising_connections_distinction_asymmetry_relation.md)
- [Progenitor drafts](docs/progenitor_drafts/README.md)

## Current Result Sets

The public tree keeps only the current/relevant compact results:

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

Older exploratory outputs are summarized in the docs but not exposed as result
folders in the current public tree.

The `docs/progenitor_drafts/` folder contains early theory-side draft papers.
They are included for provenance only and should not be read as current
validation results.

The `docs/current_theory/` folder contains the current Omega theory/status draft.
The `docs/research_notes/trajectory_space/` folder contains planning notes for a
possible quotient-light trajectory-space branch.

## Important Caveat

This repository does not prove Omega as a scientific theory. The current results
come from a local toy multifield substrate. They are evidence for a candidate
formal object and for a workflow that can reject weaker alternatives.

## Environment

Use the local virtual environment directly when working on the original machine:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

For CPU-heavy probes, the calibrated default is:

```text
18 worker processes
```

For GPU/CuPy work on the original machine, use `omega_env.bat` or run
`omega_env.ps1` with a PowerShell execution-policy bypass. The environment
scripts add Torch's bundled CUDA 13 NVRTC DLL directory to `PATH` and point
CuPy's kernel cache at `.cupy-cache/`.

## Main Scripts

- `probe_09_robust_fiber_reachability.py`
- `probe_10_com_viable_propagation_robustness.py`
- `probe_11_learned_predictive_kappa_revised.py`
- `probe_12_batch_com_audit_learned_diagnosis.py`
- `probe_T0_trajectory_space_branch_triage.py`
- `probe_T1_viable_trajectory_geometry.py`
- `probe_T1F_ordered_trajectory_structure_atlas.py`
- `probe_I0_invariant_stack_audit.py`
- `probe_I0b_invariant_threshold_dropout_audit.py`
- `probe_13_formal_fiber_transport_object_audit.py`
- `probe_13b_fiber_transport_false_positive_refinement.py`
- `probe_DA0_distinction_asymmetry_relation.py`
- `probe_DA0b_relational_connection_closure.py`
- `probe_DA1_viable_slack_phase_sweep.py`
- `probe_DA1b_apparent_vs_viable_slack.py`
- `probe_DA1c_noncommutative_relational_history.py`
- `probe_DA2_relational_edge_memory_world.py`
- `probe_DAX_branching_connection_graph_validity_revised.py`
- `probe_DAX_G0_minimal_DAR_rule_space_persistence.py`
- `probe_DAX_G1_persistence_motif_anatomy_and_robustness.py`
- `probe_DAX_G2_persistence_phase_map_minimal_rule_spaces.py`
- `probe_DAX_G2b_control_adjusted_primitive_guardrail.py`
- `probe_DAX_G3_q3r1_guardrailed_phase_map.py`
- `probe_DAX_G4_q3r1_motif_ecology_mechanism.py`
- `probe_DAX_G5_q3r1_detector_freeze_heldout_prediction.py`

Historical scripts remain in the repository because they document how the
current object was reached, but new work should normally start from Probe 09/10
or from the next formalization probe described in the manual.

## Current Next Step

Current latest probe:

```text
Probe DAX-G5: q=3/r=1 Detector Freeze and Held-Out Prediction
```

Probe DAX-G5 froze the q=3/r=1 DAR-persistence detector before held-out
sampling, then tested 5000 held-out q=3/r=1 rules across predeclared fertile and
control bands. It did not pass: fertile bands produced 7 primary positives,
controls produced 4, enrichment was only 1.17x, and the B4 barren/control band
leaked. This means the G3/G4 ecology is descriptive but not yet a predictive
validation detector.
