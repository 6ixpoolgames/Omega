# Omega Running Log

This is the living operational log for the Omega validation workspace. Update it
after every meaningful theory-side decision, probe implementation, or compute
run.

## 2026-05-22

### RFS0 Strict Reachable Futures Small Smoke

Implemented the first RFS0 exact finite reachable-futures substrate batch from
`docs/RFS0_STRICT_REACHABLE_FUTURES_BATCH_SPEC.md`.

Code changes:

- added `omega/rfs0/substrate.py`;
- added `omega/rfs0/exact.py`;
- added `omega/rfs0/run_strict_batch.py`;
- added exact reachable sets, finite-horizon viability kernels, capture basins,
  perturbation recovery rates, and strict-future contraction metrics;
- added checkpointed JSONL/CSV/status/summary output after completed jobs;
- added hard-cap timeout salvage that cancels unfinished work and writes partial
  summaries.

Primary result:

- `docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md`
- `results/rfs0/20260522_strict_reachable_futures_small_smoke/summary.md`

Run shape:

```text
systems:
  108

regimes:
  balanced, permissive, harsh, repair_rich, commit_rich, capacity_tight

controls:
  structured
  dense_permissive_control
  dead_control
  random_edge_control
  shuffled_admissibility_control
  no_perturbation_control

workers:
  18

elapsed:
  about 6 seconds

errors:
  0
```

Timeout salvage test:

```text
cap:
  1 second

completed rows:
  13

status:
  TIMED_OUT

artifact status:
  systems.jsonl, results.csv, summaries, status.json, and summary.md retained
```

Interpretation:

- exact computation is cheap at this scale;
- structured substrate produced sparse nonzero strict kernels in balanced,
  repair-rich, and commit-rich regimes;
- permissive regime and dense control are too large/trivial;
- harsh and capacity-tight regimes collapse to zero strict viability;
- random-edge and shuffled-admissibility controls remain too strong, so control
  separation is not yet adequate;
- contraction events exist, but expansion events are absent under the current
  metric.

Current read:

```text
RFS0 is promising as a measurement floor, but not ready for a longer validation
run as-is. Next small probe should improve control separation, contraction
geometry, and parameter resolution without loosening K_strict just to get more
positives.
```

## 2026-05-21

### VAL1-MF Interference Audit Smoke

Implemented the sampled counterfactual interference audit requested by
`docs/VAL1_MF_INTERFERENCE_AUDIT_SPEC.md`.

Code changes:

- added `omega/val1_mf/run_interference_audit.py`;
- reused the existing two-field generator;
- added coupling masks for uncoupled, full, enable-only, obstruct-only,
  restore-only, commit-only, and shared-capacity-only modes;
- made sampled alive / terminal deltas primary;
- retained raw joint enumeration only as a diagnostic.

Primary result:

- `docs/research_notes/validation_results/val1_mf_interference_audit_smoke_result.md`
- `results/val1_mf/20260521_interference_audit_smoke/summary.md`

Run shape:

```text
paired worlds:
  100

rollout_samples:
  256

horizon:
  d16

workers:
  18

elapsed:
  17.0 seconds

errors:
  0
```

Interpretation:

- sampled counterfactual measurement worked cleanly;
- full coupling improved mean joint alive probability from 0.734 to 0.816;
- `constructive_delta_bin` appeared in 22/100 rows;
- one provisional `A_local_dominance_bin` row appeared;
- no robust destructive or commit/obstruct-driven interference appeared;
- diagnostic enumeration still capped often, but it was no longer the primary
  evidence path.

Current read:

```text
VAL1-MF now has a viable sampled interference measurement pattern.
The visible object is constructive support/recovery, not yet destructive
pseudo-Omega-like interference. The next probe should target destructive
hazards with stricter alive/hazard metrics before scaling.
```

### VAL1-MF Two-Field Compatibility Smoke

Implemented the first minimal multifield compatibility smoke on top of VAL0-G.

Code changes:

- added `omega/val1_mf/coupled_grammar.py`;
- added `omega/val1_mf/metrics.py`;
- added `omega/val1_mf/run_smoke.py`;
- added joint-state enumeration, rollout terminal estimates, compatibility
  ratios, cap-hit reporting, and neutral compatibility bins.

Primary result:

- `docs/research_notes/validation_results/val1_mf_two_field_compatibility_smoke_result.md`
- `results/val1_mf/20260521_two_field_compatibility_smoke_cap4096/summary.md`

Run shape:

```text
paired worlds:
  150

workers:
  18

max_states_per_depth:
  4096

rollout_samples:
  128

elapsed:
  about 79 seconds

errors:
  0
```

Interpretation:

- the smoke completed cleanly and produced nondegenerate bins;
- `mutual_collapse_bin`, `joint_viable_bin`, and `uncoupled_parallel_bin`
  appeared in small non-censored counts;
- the dominant outcome was still `mixed_or_censored_bin`: 142/150 rows;
- aggregate joint cap hit rate was 0.947;
- naive two-field enumeration did not solve the cap problem and likely worsened
  it by multiplying reachable combinations.

Current read:

```text
Do not scale this exact two-field enumerator.
Multifield compatibility remains relevant, but the next probe should switch to
sampled or cap-aware compatibility estimates before a long run.
```

### VAL0-G Neutral Grammar Stability Probe

Implemented the second small VAL0-G forced-fit audit.

Code changes:

- added cap-hit fields through depth 32;
- added `coarse` and `full` signature modes;
- added downstream cut sensitivity alongside initial cut sensitivity;
- added neutral bin labels alongside interpretive class names;
- added signature, cap-hit, and cut-sensitivity summary outputs.

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_stability_probe_result.md`
- `results/val0_g/20260521_neutral_grammar_stability_probe_cap2048/summary.md`

Run shape:

```text
neutral_grammar_v1:
  250 seeds

guardrails:
  low_resolution_dense: 50 seeds
  brittle_peak: 50 seeds

signature modes:
  coarse
  full

rows:
  700

errors:
  0

max_states_per_depth:
  2048
```

Interpretation:

- multiple neutral bins appeared again;
- coarse/full signatures agreed at `0.996` for neutral rows;
- cap 512 vs 2048 did not collapse the neutral bin structure;
- high-mass classes remain heavily cap-censored at d16/d32;
- dense and brittle guardrails are cap-saturated and not semantically clean
  under the current classifier;
- downstream cut sensitivity adds useful information but should not yet be
  treated as an ontology-level metric.

Current read:

```text
VAL0-G remains on the right substrate.
The main risk is measurement censoring, not obvious generator fine-tuning.
Do not scale to a full atlas until cap-aware or sampled survival metrics are
added.
```

### VAL0-G Neutral Grammar Geometry Smoke

Implemented the first VAL0-G smoke substrate:

- `omega/val0_g/grammar.py`
- `omega/val0_g/metrics.py`
- `omega/val0_g/run_smoke.py`

Primary result:

- `docs/research_notes/validation_results/val0_g_neutral_grammar_smoke_result.md`
- `results/val0_g/20260521_neutral_grammar_smoke_v2/summary.md`

Run shape:

```text
neutral_grammar_v1:
  50 seeds

guardrails:
  low_resolution_dense: 12 seeds
  brittle_peak: 12 seeds

rows:
  74

errors:
  0
```

Interpretation:

- initial calibration was too expansion-heavy and saturated depth-16 descendant
  mass;
- a minimal v2 calibration broadened lower-enable, higher-obstruction, decay,
  and capacity-pressure regimes;
- v2 produced multiple post-hoc measured geometry classes:
  - `recoverable_basin_like`: 26 / 50 neutral rows;
  - `self_terminating`: 16 / 50 neutral rows;
  - `thin_ridge`: 6 / 50 neutral rows;
  - `deep_corridor_like`: 2 / 50 neutral rows.

Current read:

```text
VAL0-G passed minimal smoke.
It does not validate Omega.
It does justify a slightly larger stability probe with cap-hit reporting,
depth 32 if cheap, and a better brittle/thin-ridge guardrail.
```

### Public Reorientation Around VAL0-G

The public-facing repository orientation was updated after the VAL0-CT geometry
battery.

Current interpretation:

```text
VAL0-CT:
  useful first task-space calibration layer
  R1 anchor advantages reproduced
  dense controls remained clean
  broad held-out / unlabeled generalization not established

VAL0-G:
  current front edge
  neutral grammar geometry atlas
  asks whether recoverable-continuation geometries emerge without outcome labels
```

Reason for pivot:

- the 12h unlabeled geometry battery completed cleanly and preserved guardrails;
- corridor d8 did not survive scale as a robust predictor;
- candidate future-R0 variance was the best surviving weak hook;
- the project should now study geometry emergence directly rather than treating
  R1 victory as the object.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/research_notes/validation_design/README.md`
- `results/val0_ct/README.md`
- `results/val0_g/README.md`

Next implementation target:

```text
Implement neutral_grammar_v1 smoke:
  survival curves
  descendant mass
  branching reproduction
  terminal probability
  cut sensitivity k=1
  dense/flat guardrail
```

## 2026-05-17

### Root Script Cleanup

Moved historical root-level Python probe scripts into:

- `scripts/historical_probes/`

Added:

- `scripts/historical_probes/README.md`

Reason:

- keep the repository front page clean for public readers;
- make VAL0-CT docs the obvious entry point;
- preserve old scripts for provenance, reproducibility, and failure analysis.

Historical report and log references were updated to point at the new script
paths.

### Root Result Folder Cleanup

Moved tracked historical result folders into:

- `results/historical_probes/`

Moved ignored local smoke, calibration, stress, and scratch result folders into:

- `results/local_runs/`

Added:

- `results/README.md`
- `results/historical_probes/README.md`
- `results/val0_ct/README.md`

Future VAL0-CT outputs should be written under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Do not add new root-level `*_results` folders.

### Public Reorientation Around VAL0-CT

The public-facing repository orientation was updated to make the Constructor
Theory / VAL0-CT pivot explicit.

Updated entry points:

- `README.md`
- `docs/roadmaps/OMEGA_EXPERIMENTAL_ROADMAP.md`
- `docs/PUBLIC_RESULTS_INDEX.md`
- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/current_theory/README.md`
- `docs/research_notes/validation_design/README.md`

Current front-door statement:

```text
VAL0-CT is the current validation target.
It tests whether persistence-conditioned reachability, R1, predicts
long-horizon reachability retention better than raw reachability, R0, and
equal-budget R0-lookahead controls in structured task algebras.
```

Public framing decision:

- COM/fiber work is historical evidence for viable propagation and
  coarse-graining discipline, not the current validation center.
- Trajectory-space probes are negative constraints and fakeout anatomy.
- CA/DAR/DAX probes calibrate the primitive floor rather than validating Omega
  proper.
- DAX-G5's failed held-out prediction is one of the reasons the project moved
  to task-space validation.

Next implementation target:

```text
Implement VAL0-CT smoke, CPU-first, using:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

Compare:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega
```

## 2026-05-16

### Formal-Stack Recenter: Primitive Floor to Valuer-Level Omega

New theory notes were added under:

- `docs/research_notes/omega_theory/`
- `docs/research_notes/primitive_branch/`

New canonical entry points:

- `docs/research_notes/omega_theory/formal_stack_v0.md`
- `docs/research_notes/omega_theory/omega_glossary.md`
- `docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md`
- `docs/research_notes/omega_theory/regenerative_filtering_slack_and_parasitic_modes.md`
- `docs/research_notes/primitive_branch/relation_as_historical_binding.md`
- `docs/research_notes/primitive_branch/omega_meets_fep.md`
- `docs/research_notes/primitive_branch/valuerhood_as_recoverable_historical_identity.md`

Current working stack:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viability
-> Omega-compatible viability
-> lushness of value-bearing trajectory space
```

Core thesis now tracked in the manual:

```text
Omega is the asymptotic compatibility structure of value-bearing trajectory
space.
```

Interpretive update:

- Relation is now treated as causal continuity through transformation, not
  merely graph adjacency, neighbor dependence, coupling, or social relation.
- Identity is organized causal continuity through change.
- Recoverability is perturbation-continuability, not exact restoration.
- A valuer is a bounded historical identity for which different continuations
  asymmetrically affect recoverable continuability.
- Viability is a gate; nested, compatible, value-bearing trajectory richness is
  the target.

Consequence for prior executable work:

- COM fiber transport remains the strongest toy-substrate witness for viable
  propagation and coarse-graining discipline.
- Trajectory-space probes remain useful negative constraints and fakeout
  anatomy.
- CA, DAR, and DAX probes are now explicitly primitive-floor calibration unless
  they include minimal valuerhood and recoverable continuability.
- DAX-G5's failed held-out prediction is consistent with this boundary: it
  describes motif ecology in a primitive rule space, not a validation-ready
  Omega detector.

Roadmap decision:

```text
The next Omega-proper validation family should be a minimal valuer-world
benchmark, not another bare cellular or field-dynamics scale-up.
```

Probe V0 target:

- construct minimal self-maintaining valuers;
- include perturbation recovery, path consequence, and action or interaction
  channels;
- measure Omega-level predictors against survival, reward, reachability,
  empowerment, and local-viability baselines;
- include fakeout controls for stasis, clocks, lock-in, externally maintained
  persistence, and high reachability without self-maintenance.

## 2026-05-11

### Progenitor Drafts Added

Added the early theory-side papers to:

- `docs/progenitor_drafts/`

Status:

- drafts only;
- early theoretical provenance;
- not current validation results;
- not final claims about the formal object.

Included PDFs:

- `intelligent_agency_under_computational_irreducibility.pdf`
- `scaling_paper_v2.pdf`
- `telos_2_0_draft.pdf`
- `echo_rosetta_version.pdf`
- `gradient_ethics.pdf`
- `gradient_field_theory_of_value_v51.pdf`

### Current Theory And Trajectory-Space Notes Added

Added the current theory/status draft to:

- `docs/current_theory/omega_signature_v0_1.pdf`

Status:

- current draft artifact;
- not peer reviewed;
- not a validation result by itself;
- best current written entry point into the Omega claim ladder and COM witness.

Added trajectory-space branch notes to:

- `docs/research_notes/trajectory_space/trajectory_space_omega_research_note.pdf`
- `docs/research_notes/trajectory_space/trajectory_space_omega_triage_note.pdf`

Status:

- draft research notes;
- branch-selection/planning artifacts;
- not replacements for the current COM fiber-transport witness.

Framing decision:

- `Project_Omega.pdf` is treated as a current theory/status draft.
- The trajectory-space PDFs are treated as active research branch notes.
- The earlier PDFs remain under `docs/progenitor_drafts/` as historical
  provenance.

### Repository Setup

- Local repo pushed to GitHub:
  - https://github.com/6ixpoolgames/Omega
- Current pushed baseline before this log:
  - `cd0fe04 Initial Omega validation workspace`
  - `88d0fa3 Add Probe 10 COM robustness results`

### Current State

The strongest current toy-substrate object is:

```text
F,T attractive coupling
kappa = center_of_mass
alpha = 0.45, 0.50, 0.525
T = 900, 1500, 2400
object = multi-step viable propagation through certified fibers
```

Interpretive rule:

```text
Omega is viable propagation, not entropy.
Entropy/breadth are secondary diagnostics.
```

### Probe 09: Robust Fiber Reachability

Script:

- `scripts/historical_probes/probe_09_robust_fiber_reachability.py`

Primary output:

- `results/historical_probes/probe_09_robust_fiber_reachability_results/summary.json`
- `results/historical_probes/probe_09_robust_fiber_reachability_results/viable_propagation_summary.csv`

Configuration:

- `N_TRAJ=10000`
- `seed_count=160`
- `bootstrap_repeats=800`
- `workers=18`
- horizons `900,1500,2400`

Result:

- `center_of_mass` was viable-propagation-positive across all alpha/T rows.
- `joint_basin` and `basin_transition_profile` were mostly local transport
  artifacts.
- `boundary_v2_regime_sequence` remained pseudo-risk/control-like.

Key COM deltas versus shuffled:

```text
alpha=0.45:  T900 +0.0576, T1500 +0.0708, T2400 +0.0787
alpha=0.50:  T900 +0.0699, T1500 +0.0867, T2400 +0.0948
alpha=0.525: T900 +0.0752, T1500 +0.0954, T2400 +0.1014
```

Decision:

- Proceed to perturbation robustness focused on COM.

### Probe 10: COM Viable Propagation Robustness

Script:

- `scripts/historical_probes/probe_10_com_viable_propagation_robustness.py`

Primary outputs:

- `results/historical_probes/probe_10_com_viable_propagation_robustness_extended_results/summary.json`
- `results/historical_probes/probe_10_com_targeted_fragility_refinement_results/summary.json`

Contained run:

- `N_TRAJ=7500`
- `seed_count=80`
- `bootstrap_repeats=500`
- 2 perturbation variants per family
- all controls

Result:

- COM overall retention about `0.960`.
- Initial-location and sink-threshold perturbations retained at `1.000`.
- Noise and potential-shape perturbations were weakest.

Extended run:

- `N_TRAJ=10000`
- `seed_count=160`
- `bootstrap_repeats=800`
- 10 variants/family
- all controls
- runtime about `5.14h`

COM retention by family:

```text
initial_location:     1.000
noise:                0.878
potential_shape:      0.922
reference:            1.000
sink_threshold:       1.000
time_discretization:  0.944
overall:              0.950
```

Targeted fragility refinement:

- COM only
- families: `noise`, `potential_shape`, `time_discretization`
- 20 variants/family
- `N_TRAJ=10000`
- `seed_count=160`
- `bootstrap_repeats=800`
- runtime about `5.60h`

COM retention:

```text
noise mild:                   0.956
noise moderate:               0.800
potential_shape mild:         0.933
potential_shape moderate:     0.844
time_discretization mild:     0.933
time_discretization moderate: 0.956
reference:                    1.000
overall:                      0.905
```

Decision:

- COM viable propagation is robust enough in the current toy substrate to justify
  formalization.
- Weaknesses are mainly harder noise and potential-shape perturbations.
- Failures appear more tied to component preservation / lower-rank erasure than
  estimator instability.

### Current Recommended Next Step

Probe 11 was run as a learned predictive-kappa test before formalization.

### Probe 11: Learned Predictive Kappa

Script:

- `scripts/historical_probes/probe_11_learned_predictive_kappa_revised.py`

Primary outputs:

- `results/historical_probes/probe_11_learned_predictive_kappa_revised_results/summary.json`
- `results/historical_probes/probe_11_learned_predictive_kappa_revised_results/learned_kappa_validation_loss.csv`
- `results/historical_probes/probe_11_learned_predictive_kappa_revised_results/learned_kappa_test_propagation.csv`
- `results/historical_probes/probe_11_learned_predictive_kappa_revised_results/learned_vs_com_comparison.csv`
- `results/historical_probes/probe_11_learned_predictive_kappa_revised_results/learned_label_anatomy.csv`

Configuration:

- `N_TRAJ=3000`
- `seed_count=100`
- `bootstrap_repeats=300`
- `workers=18`
- train variants: `25`
- validation variants: `12`
- test variants: `24`
- alphas: train `0.45, 0.50`; test `0.525`
- horizons: train `900, 1500`; test `1500, 2400`
- runtime about `38.7m`

GPU note:

- CuPy is installed, but the local CUDA NVRTC runtime is unavailable
  (`nvrtc*.dll` missing), so this run used CPU multiprocessing.

Result:

- Best learned kappa by validation: `predictive_kmeans_k21`.
- Best learned validation total loss: `0.0129069`.
- Best learned COM association: `0.468`.
- Best learned mean test delta viable propagation vs shuffled: `-0.00228`.
- COM mean test delta viable propagation vs shuffled: `+0.08495`.
- Learned/COM viable-propagation ratio: about `-0.103`.
- `predictive_kmeans_k5` and `predictive_kmeans_k8` were tagged as learned
  propagation candidates in some rows, but the overall learned family remained
  weaker than COM.
- Higher-k learned quotients tended toward fragmentation and entropy-positive
  pseudo-risk behavior.

Decision:

- A simple learned predictive quotient can see part of the viable-propagation
  signal, but it does not replace COM.
- COM remains the strongest analytic coordinate in the current toy substrate.
- Learned quotient work should continue, but with a tighter object definition
  and less leakage-prone primitive target design.

### Current Recommended Next Step

### Probe 12: COM Formalization + Learned-Kappa Diagnosis

Script:

- `scripts/historical_probes/probe_12_batch_com_audit_learned_diagnosis.py`

Primary outputs:

- `results/historical_probes/probe_12_batch_results/batch_summary.json`
- `results/historical_probes/probe_12_batch_results/recommended_next_step.md`
- `results/historical_probes/probe_12a_com_formal_object_audit_results/summary.json`
- `results/historical_probes/probe_12b_learned_kappa_failure_diagnosis_results/summary.json`
- `results/historical_probes/probe_12c_improved_learner_smoke_results/summary.json`

Configuration:

- `N_TRAJ=3000`
- `seed_count=100`
- `bootstrap_repeats=300`
- `workers=18`
- alphas: `0.45, 0.50, 0.525`
- horizons: `900, 1500, 2400`
- runtime about `38.3m`

Probe 12A result:

- COM main-threshold viable propagation index: `0.2556`.
- COM delta viable propagation vs shuffled: `+0.0673`.
- COM component-B preservation: `0.7893`.
- COM lower-rank erasure: `0.1054`.
- COM singleton fraction: `0.4567`.
- COM threshold sensitivity was small:
  - loose `0.2569`
  - main `0.2556`
  - strict `0.2537`

Important control nuance:

- `boundary_v2_regime_sequence` and `joint_basin` can have larger absolute
  viable-propagation-index values in the 12A anatomy table, but their deltas vs
  shuffled are negative on average. COM remains the positive baseline-separated
  witness in this audit.

Probe 12B result:

- Simple predictive k-means failure modes:
  - fiber splitters: `predictive_kmeans_k13`, `predictive_kmeans_k21`,
    `predictive_kmeans_no_COM_k8`, `predictive_kmeans_no_COM_k13`;
  - fiber mergers: `predictive_kmeans_k5`, `predictive_kmeans_k8`,
    `predictive_kmeans_k13`, `predictive_kmeans_no_COM_k8`,
    `predictive_kmeans_no_COM_k13`;
  - validation winners/overfit risks: `predictive_kmeans_k21`,
    `predictive_kmeans_no_COM_k13`;
  - partial quotients: `predictive_kmeans_k5`, `predictive_kmeans_k8`.

Probe 12C result:

- Tested transition-aware balanced predictive clustering as a smoke test.
- Best smoke learner: `transition_balanced_k21`.
- Validation predictive loss: `4.26e-05`.
- Test COM association: `0.443`.
- Singleton and small-fiber fractions in the sampled-label smoke anatomy were
  `0.0`, but this was not a full propagation-scale replacement test.

Decision:

- COM remains the current formal witness.
- Learned-kappa work should not be scaled yet.
- The next step should formalize COM fiber transport and then revisit learned
  quotients with sequence/fiber-aware targets.

Large local-only files:

- Probe 12A generated full macro-node, transport-edge, certified-path, and
  component-projection tables. They are retained locally but not tracked because
  they are large generated anatomy files, including files above GitHub's normal
  file-size limits.

### GPU/CuPy Environment Fix

CuPy initially imported but failed to execute kernels because it could not find
`nvrtc*.dll`. The machine has a working NVIDIA driver and reports CUDA 13.0 via
`nvidia-smi`, but no system CUDA Toolkit directory was present.

Fix:

- use the CUDA 13 NVRTC DLLs bundled with Torch at
  `.venv\Lib\site-packages\torch\lib`;
- prepend that directory to `PATH`;
- set `CUPY_CACHE_DIR` to the workspace-local `.cupy-cache`.

This is now encoded in:

- `scripts/setup/omega_env.bat`
- `scripts/setup/omega_env.ps1`

Verification:

```text
cupy arange/sum executed on NVIDIA GeForce RTX 4070 Ti
```

PowerShell note:

- direct `.\scripts\setup\omega_env.ps1` may be blocked by Windows execution policy;
- use `powershell -ExecutionPolicy Bypass -File scripts\setup\omega_env.ps1` or use
  `scripts\setup\omega_env.bat`.

### CPU/GPU Concurrent Stress Probe

Added and ran:

- `scripts/historical_probes/gpu_cpu_concurrent_stress_probe.py`

Purpose:

- validate that the workflow can run CPU NumPy work and GPU CuPy work at the
  same time;
- measure rough sustained dense-array throughput for future probe planning.

Run:

- duration: `180s`
- CPU workload: NumPy matrix multiply, size `1400`
- GPU workload: CuPy matrix multiply, size `4096`
- environment: `scripts/setup/omega_env.bat`

Result:

```text
CPU NumPy: ~0.514 approximate TFLOP/s
GPU CuPy:  ~21.596 approximate TFLOP/s
GPU: NVIDIA GeForce RTX 4070 Ti
```

Interpretation:

- the GPU path is viable for dense array kernels and pairwise/linear algebra
  work;
- CPU and GPU workloads can overlap in the same workflow;
- simulation orchestration remains CPU/process-heavy unless explicitly rewritten
  for GPU kernels.

### Current Recommended Next Step

Probe T0 added a quotient-light trajectory-space branch triage. It does not
replace the COM object; it tells us which branch is worth probing if we explore
trajectory geometry directly.

Run:

- script: `scripts/historical_probes/probe_T0_trajectory_space_branch_triage.py`
- result directory: `results/historical_probes/probe_T0_trajectory_space_branch_triage_results/`
- 18 workers
- `15000` trajectories per condition/seed
- `180` seeds
- `200` bootstraps
- runtime: about `8.4` minutes
- GPU metric path used on `95.8%` of seed evaluations

Result:

```text
concentration_collapse:          12
component_balance:               12
predictive_temporal_dependence:  11
tube_thickness:                  11
kernel_hazard_erosion:           10
restoration:                     10
```

Interpretation:

- concentration-collapse is the best first geometry branch by the script's
  tie-break/recommendation logic;
- component-balance is nearly as important because it is less redundant with raw
  viability;
- kernel erosion and restoration are heavily correlated with raw viability in
  this setup, so they are useful diagnostics but weaker branch selectors;
- recommended trajectory-space follow-up: `Probe T1: Viable Trajectory
  Geometry`.

The main scientific trunk still needs formal COM fiber transport:

### Probe T1: Viable Trajectory Geometry

Probe T1 tested the T0-selected branch directly. It asked whether viable
trajectory geometry is non-degenerate, temporally structured, and
component-preserving beyond survival, endpoint spread, noise, and lower-rank
erasure.

Run:

- script: `scripts/historical_probes/probe_T1_viable_trajectory_geometry.py`
- result directory: `results/historical_probes/probe_T1_viable_trajectory_geometry_results/`
- 18 workers
- `15000` trajectories
- `180` seeds
- `300` bootstraps
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- runtime: about `24.7` minutes
- grouped GPU geometry batches: `72`
- GPU usage fraction: `100%`
- max GPU temperature observed by the script: `52 C`
- thermal throttle events: `0`

Result:

```text
geometry_branch_supported: false
correlation effective_rank vs p_viable_T: 0.271
component_balance_passed: false
temporal_fakeout_passed: false
strongest effective-rank null delta: +0.0017 vs independent_alpha0
```

False-positive controls:

```text
rigid_collapse: effective rank is nearly unchanged, exposing rank scale-invariance
noise_fakeout: effective rank scores much higher than coupled
single_component_erasure: correctly flags near-total component erasure
```

Interpretation:

- Simple effective-rank/collapse geometry is not a sufficient Omega-positive
  object.
- The branch is not reducible to raw viability, but it fails stricter controls.
- Time-shuffled/noise fakeouts show that geometry metrics can reward
  unstructured variance or segment disorder.
- Coupled runs show weak component balance, roughly `0.41-0.45` in the retained
  table.

Recommendation:

```text
Do not proceed to T2 scaling yet.
Build a trajectory-geometry failure-mode/component-erasure atlas first, or
return to the COM fiber-transport trunk as the stronger current object.
```

### Probe T1F: Ordered Trajectory Structure Atlas

Probe T1F pivoted from generic geometry to ordered distinction structure under
viability filtering. It tested whether early trajectory distinctions retain
later consequences without being explained by noise, time-shuffle,
endpoint-fakeout, rigid collapse, or one-component erasure.

Run:

- script: `scripts/historical_probes/probe_T1F_ordered_trajectory_structure_atlas.py`
- result directory: `results/historical_probes/probe_T1F_ordered_trajectory_structure_atlas_results/`
- 18 workers
- `15000` trajectories
- `180` seeds
- `300` bootstraps
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- runtime: about `25.2` minutes
- grouped GPU metric batches: `81`
- GPU usage fraction: `100%`
- max GPU temperature observed by the script: `49 C`
- thermal throttle events: `0`

Family scores:

```text
component_conditioned_temporal_continuity: 15
ordered_distinction_persistence:          14
conditional_temporal_dependence_proxy:    14
minimal_recoverable_continuation:         14
```

Guardrail result:

```text
component_continuity_passed: false
false_positive_rejection score for all families: 0
best metric correlation with p_viable_T: 0.442
```

Interpretation:

- Ordered readouts are more informative than raw effective-rank geometry, but
  they still do not pass the strict object criteria.
- Coupled ordered persistence averaged about `0.359`; time-shuffled averaged
  about `0.266`, and noise fakeout averaged near `0.000`, so the pivot did fix
  the T1 noise-fakeout problem.
- Endpoint fakeout averaged about `0.362`, and single-component erasure averaged
  about `0.417`, so the ordered persistence readout still admits important
  false positives.
- Coupled component continuity averaged about `0.658`, but the minimum fell
  below the required threshold, so the global component guardrail failed.

Recommendation:

```text
Demote trajectory-native branch for now.
Return to COM fiber-transport formalization, or pivot to an agent-relevant
distinction/control probe.
```

### Probe I0: Invariant Stack Audit

Probe I0 gave the trajectory-native branch a final longer validation pass. It
tested whether a cumulative stack of single-Omega-like invariants could recover
a stricter trajectory-native object without admitting the known T1/T1F
false-positive controls.

Run:

- script: `scripts/historical_probes/probe_I0_invariant_stack_audit.py`
- result directory: `results/historical_probes/probe_I0_invariant_stack_audit_results/`
- 18 workers
- `15000` trajectories
- `180` seeds
- `300` bootstraps
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- conditions: coupled, product, shuffled, time-shuffled, independent alpha-0
- known controls: rigid collapse, noise fakeout, single-component erasure,
  endpoint fakeout
- holdouts: delayed trap, component-swap fakeout
- runtime about `47.3` minutes
- GPU metric usage fraction `1.0`
- max GPU temperature `49 C`
- thermal throttle events `0`

Invariant scores:

```text
I1 viability:                           1
I2 ordered distinction persistence:     2
I3 component non-erasure:               3
I4 counterfactual affordance relevance: 2
I5 minimal recoverability:              1
I6 horizon coherence:                   1
```

Ablation result:

```text
S1 retention 0.444, known rejection 0.556, holdout rejection 0.556
S2 retention 0.111, known rejection 0.917, holdout rejection 0.833
S3 retention 0.111, known rejection 1.000, holdout rejection 0.833
S4 retention 0.000, known rejection 1.000, holdout rejection 0.944
S5 retention 0.000, known rejection 1.000, holdout rejection 1.000
S6 retention 0.000, known rejection 1.000, holdout rejection 1.000
```

Interpretation:

- The stack behaves like a rejection filter, not an object witness.
- Adding invariants monotonically improves false-positive rejection, but it also
  removes the coupled condition.
- The best apparent stack, S5, rejects all known controls and both holdouts, but
  has `0.0` coupled retention. That is not a pass; it is overconstraint.
- `I3_component_non_erasure` is the strongest individual invariant, but the
  cumulative stack still fails to preserve the target object.
- The holdouts are useful because they confirm the stack generalizes rejection,
  but they do not rescue coupled retention.

Decision:

```text
No trajectory-native invariant stack passed.
Demote trajectory-native work from candidate-object status.
Return to COM fiber-transport formalization.
```

### Probe I0b: Invariant Threshold and Dropout Audit

Probe I0b reused the existing Probe I0 estimator table and did not rerun
simulation. It asked whether I0 failed because the hard thresholds or strict AND
stacking were too severe.

Run:

- script: `scripts/historical_probes/probe_I0b_invariant_threshold_dropout_audit.py`
- result directory: `results/historical_probes/probe_I0b_invariant_threshold_dropout_audit_results/`
- reused `results/historical_probes/probe_I0_invariant_stack_audit_results/estimator_report.csv`
- runtime under one second for the analysis step

Key result:

```text
trajectory_branch_reopened: false
best hard stack: S5 under coupled_q10 thresholds
best hard coupled retention: 0.533
best hard known rejection: 0.722
best hard holdout rejection: 0.833
best hard balanced score: 0.321
best soft stack: I3 mandatory plus 1 of I2/I4/I5/I6
best soft coupled retention: 0.222
best soft known rejection: 0.806
best soft holdout rejection: 0.500
best soft balanced score: 0.090
```

Dropout:

```text
first zero-retention hard stack: S4
main dropout invariant: I2 ordered distinction persistence
```

Interpretation:

- Relaxed thresholds can recover coupled retention, but not enough
  known-control rejection.
- Soft stacks improve the tradeoff only weakly and miss the reopen retention
  criterion.
- Pareto profiles show partial separation, but not enough to treat the branch as
  a recovered object.
- I5 and I6 remain diagnostic only, not gate-ready.

Decision:

```text
Close trajectory-native invariant branch for now.
Proceed with Probe 13 formal fiber-transport audit.
```

### Probe 13 Smoke: Formal Fiber-Transport Audit

Probe 13 was implemented as a formal fiber-transport audit and smoke-tested
before a main run.

Smoke result:

```text
COM base-null positive: true
Probe 13 full pass: false
mean viable propagation index: 0.373
delta vs product: +0.163
delta vs shuffled: +0.166
delta vs time-shuffled: +0.043
component balance: 0.714
```

Loose thread exposed:

```text
component_B_only passed
time_shuffled_COM passed
rigid_collapse scored very high
endpoint_fakeout remained high
delayed_trap remained high
```

Decision:

```text
Do not treat Probe 13 smoke as a frozen formal object.
Run a targeted false-positive refinement before any main-scale formal audit.
```

### Probe 13b Smoke: Fiber-Transport False-Positive Refinement

Probe 13b added only refinements directly forced by the Probe 13 smoke failures:

- R1 bidirectional component necessity;
- R2 temporal edge-order integrity;
- R3 nondegenerate within-fiber realization diversity;
- R4 late-horizon transport retention.

Run:

- script: `scripts/historical_probes/probe_13b_fiber_transport_false_positive_refinement.py`
- result directory: `results/historical_probes/probe_13b_fiber_transport_false_positive_refinement_results/`
- smoke scale: `1000` trajectories, `8` seeds, `50` bootstraps
- alphas `{0.50}`
- horizons `{900}`
- 6 workers
- runtime about `36` seconds

Primary witness:

```text
base_signal_positive: true
refined_fiber_transport_positive: false
mean viable propagation index: 0.361
delta vs product: +0.154
delta vs shuffled: +0.147
delta vs time-shuffled: +0.022
component balance: 0.711
component necessity min: -0.404
edge order integrity: +0.068
within-fiber nondegeneracy delta: -0.649
late-to-early transport ratio: 1.283
```

Priority false positives:

```text
component_A_only: 0.002
component_B_only: 0.765
time_shuffled_COM: 0.334
endpoint_fakeout: 0.338
rigid_collapse: 0.999
delayed_trap: 0.333
```

Refinement pass rates:

```text
R1 component necessity: 0.0
R2 temporal edge-order: 1.0
R3 within-fiber nondegeneracy: 0.0
R4 late retention: 0.0
```

Interpretation:

- COM remains base-null positive.
- The refined formal object does not pass at smoke scale.
- R1 fails because component-B-only carries more VPI than full COM.
- R3 fails because the within-fiber diversity sketch is still more
  collapse-like than the refinement permits.
- R4 fails because delayed-trap vulnerability remains despite late/early
  retention looking superficially acceptable.

Decision:

```text
Do not run main-scale 13b as currently written.
Either design a narrower targeted refinement for the blockers or pivot to the
distinction/adjudication branch.
```

### Probe DA0 Smoke: Distinction / Asymmetry / Relation

Probe DA0 opened a new first-principles branch using tiny discrete stochastic
worlds. It intentionally avoided COM, kappas/fibers, learned representations,
agents, rewards, and path signatures.

Primitive mapping:

- distinction: local alphabet size and persistence of distinguishable symbols;
- asymmetry: directed transition bias/filtering;
- relation: stable or shuffled graph dependence between sites.

Run:

- script: `scripts/historical_probes/probe_DA0_distinction_asymmetry_relation.py`
- result directory: `results/historical_probes/probe_DA0_distinction_asymmetry_relation_results/`
- smoke scale: `2000` trajectories, `20` seeds
- horizons `{50, 100}`
- `16` sites
- 12 synthetic worlds from null/ablations through full DAR
- runtime about `53` seconds

Summary:

```text
best world: W7_full_DAR
full_DAR_best: true
full_DAR_top_metric_count: 1
null_control_top_metric_count: 2
distinction_required: false
asymmetry_required: true
relation_required: false
```

Full DAR profile:

```text
p_viable: 0.925
lineage_survival_depth: 0.268
lineage_branching_entropy: 3.193
time_reversal_asymmetry: 0.040
relational_excess: 8.854
relation_shuffle_delta: 0.096
structured_viable_richness: 17.346
```

Controls:

```text
noise_rich_control rejected: true
collapse_attractor_control rejected: true
relation_shuffled_control rejected: false
symmetric_transition_control rejected: true
independent_sites_control rejected: true
```

Interpretation:

- Full DAR is the best aggregate world in this smoke.
- The branch does not yet show a clean primitive conjunction effect.
- Relation is the weak link: the random-stepwise relation control is not
  rejected on relational nonfactorization.
- Asymmetry behaves as intended against the symmetric control.
- Noise/collapse controls are rejected on lineage survival, but some low
  viability warnings remain expected for null/noise/collapse worlds.

Decision:

```text
Do not scale DA0 main yet.
Tighten the relation/nonfactorization readout or design DA1 around the strongest
signal after inspecting DA0 profiles.
```

### Primitive-Branch Theory Addendum

Added:

- `docs/research_notes/primitive_branch/promising_connections_distinction_asymmetry_relation.md`

Working update:

```text
relation = persistent causal-history dependence
```

The addendum frames the primitive branch as connection-like transport of
distinctions through asymmetric relations, with closure and viable slack as the
next conceptual targets. It records the current negative controls:

- noise/underconstraint has distinctions without durable relational transport;
- rigid collapse/overconstraint has persistence without slack;
- random relation has dependence without stable causal-history identity;
- component-only channels can erase relational richness;
- endpoint fakeouts preserve outcomes without preserving local transport.

### Probe DA0b Smoke: Relational Connection and Closure

Probe DA0b refined relation from generic nonfactorization toward persistent
causal-history dependence.

Run:

- script: `scripts/historical_probes/probe_DA0b_relational_connection_closure.py`
- result directory: `results/historical_probes/probe_DA0b_relational_connection_closure_results/`
- smoke scale: `3000` trajectories, `30` seeds
- horizons `{50, 100}`
- `16` sites
- 16 relation-focused worlds
- 18 workers
- runtime about `3.6` minutes

Summary:

```text
best world: W18_relation_lock_in
random_stepwise_rejected: true
fixed_but_permuted_relation rejected: true
relation_lock_in rejected: false
symmetric_transition_control rejected: false
independent_sites_control rejected: false
stable_relation_advantage: 0.031
full_DAR_top_metric_count: 0
null_control_top_metric_count: 4
```

Full DAR profile:

```text
p_viable: 0.924
relation_identity_persistence: 0.000
connection_predictive_gain: 0.000
relation_shuffle_delta: 0.000
relation_lineage_survival_depth: 0.426
closure_rate: 0.249
recoverable_alternative_count: 2773.3
lock_in_index: 0.00036
closure_without_lock_in: 0.249
```

Interpretation:

- DA0b fixes one DA0 failure: random-stepwise relation is now rejected.
- The branch still does not pass because relation lock-in dominates closure and
  independent distinction dominates viable slack.
- Full DAR does not top any of the main R1-R4 metrics in this smoke.
- The connection-predictivity metric is too sparse/zeroed for the current
  worlds and needs revision before scaling.

Decision:

```text
Do not run DA0b main yet.
Revise viable slack and relation-conditioned lineage so lock-in and independent
distinction cannot win by cheap persistence.
```

### Probe DA1 Smoke: Viable Slack Phase Sweep

Probe DA1 tested the stronger phase hypothesis directly:

```text
underconstraint -> noisy richness
viable slack    -> relation-conditioned lineage plus closure plus alternatives
overconstraint  -> lock-in
```

Run:

- script: `scripts/historical_probes/probe_DA1_viable_slack_phase_sweep.py`
- result directory: `results/historical_probes/probe_DA1_viable_slack_phase_sweep_results/`
- smoke scale: `3000` trajectories, `30` seeds
- horizons `{50, 100}`
- `16` sites, `q=4`
- 19 phase points plus fixed controls
- 18 workers
- worker phase runtime about `4.4` minutes; output rebuild after aggregation
  fix took about `1.5` seconds

Best phase point:

```text
rho_relation_persistence: 1.0
alpha_asymmetry_strength: 1.0
lambda_constraint_pressure: 1.0
classification: viable_slack_candidate
```

Best profile:

```text
p_viable: 0.988
lineage_survival_depth: 0.259
relation_lineage_excess: 0.033
closure_rate: 0.376
recoverable_alternative_count: 2964.6
lock_in_index: 0.000005
```

Phase result:

```text
middle_regime_detected: false
best_point_is_extreme: true
relation_lineage_excess_positive: true
closure_without_lockin_detected: true
controls_in_expected_regions: false
```

Control classifications:

```text
noise_rich_control: mixed_or_inconclusive
collapse_attractor_control: underconstrained
independent_sites_control: mixed_or_inconclusive
symmetric_transition_control: viable_slack_candidate
random_stepwise_relation_control: mixed_or_inconclusive
relation_lock_in_control: viable_slack_candidate
```

Interpretation:

- DA1 found a real positive signal: relation-lineage excess can become positive
  while closure and alternatives remain nonzero.
- The phase hypothesis did not pass because the best point is an extreme
  `(1.0, 1.0, 1.0)`, not a middle regime.
- Controls are not classified correctly: relation lock-in and symmetric
  transition still look too good.
- The lock-in index is under-penalizing deterministic relational closure in the
  current world family.

Decision:

```text
Do not run the DA1 main grid yet.
Tighten lock-in/control classification or redesign the phase world before
scaling.
```

### Probe DA1b Smoke: Apparent Slack vs Viable Slack

Probe DA1b directly diagnosed DA1's false positives. It asked whether counted
alternatives were actually viable slack or merely apparent alternatives produced
by symmetry, lock-in, independent sites, or microstate multiplicity.

Run:

- script: `scripts/historical_probes/probe_DA1b_apparent_vs_viable_slack.py`
- result directory: `results/historical_probes/probe_DA1b_apparent_vs_viable_slack_results/`
- scale: `5000` trajectories, `50` seeds
- horizons `{50, 100}`
- `16` sites, `q=4`
- 13 diagnostic targets only, no broad phase grid
- 18 CPU workers
- runtime about `10.8` minutes

Best candidate:

```text
name: da1_extreme_best
rho_relation_persistence: 1.0
alpha_asymmetry_strength: 1.0
lambda_constraint_pressure: 1.0
classification: apparent_slack
```

Best profile:

```text
p_viable: 0.982
closure_rate: 0.317
raw_alternative_count: 4911.7
future_distinct_alternative_count: 4627.9
future_distinct_ratio: 0.942
asymmetric_slack_delta: -0.0148
relation_slack_excess: 0.0248
dynamic_lock_in_index: 0.00000001
post_perturbation_future_distinctness: 0.993
```

Diagnostic result:

```text
relation_lock_in_rejected: true
symmetric_transition_rejected: true
middle_candidate_beats_extreme: false
future_distinct_slack_detected: true
relation_slack_excess_positive: true
asymmetric_slack_delta_positive: false
```

Control classifications:

```text
collapse_attractor_control: underconstrained
independent_sites_control: apparent_slack
noise_rich_control: apparent_slack
random_stepwise_relation_control: apparent_slack
relation_lock_in_control: apparent_slack
symmetric_transition_control: apparent_slack
```

Interpretation:

- DA1b improved the diagnostic surface: the previous lock-in and symmetric
  false positives no longer pass as viable slack.
- The strongest point remains the DA1 extreme corner, not a middle regime.
- The extreme point has relation-conditioned signal and future-distinct
  alternatives, but its asymmetry load-bearing delta is negative.
- The current world family appears to create apparent slack more readily than
  principled viable slack.

Decision:

```text
Do not scale DA1/DA1b.
Revise the DA1 world design before running another grid. The next probe should
make asymmetry load-bearing by construction or explicitly reject the phase
hypothesis for this world family.
```

### Probe DA1c Smoke: Non-Commutative Relational History

Probe DA1c revised the world design so asymmetry meant consequential
non-equivalence across interaction history:

```text
A then B != B then A
```

The state was extended from visible distinctions `x_t` to `(x_t, h_t)`, where
`h_t` is local relational memory. The probe compared non-commutative relational
history against commutative, reversible, random-order, no-relation, lock-in,
noise, collapse, and bias-only controls.

Run:

- script: `scripts/historical_probes/probe_DA1c_noncommutative_relational_history.py`
- result directory: `results/historical_probes/probe_DA1c_noncommutative_relational_history_results/`
- scale: `5000` trajectories, `50` seeds
- horizons `{50, 100}`
- `16` sites, `q=4`, memory states `m=4`
- 12 worlds
- 18 CPU workers
- final valid runtime about `8.9` minutes

Implementation note:

- The first DA1c attempt was too expensive because every task ran full
  diagnostics for every ablation and timed out at 20 minutes.
- The implementation was revised so the base world keeps the full
  5000-trajectory diagnostic while AB/BA, random-order, erasure, and shuffle
  comparisons use coarse future-profile diagnostics.
- A CSV field-order bug in the first output pass was fixed before the final
  valid run; the retained result directory comes from the corrected run.

Best world:

```text
W6_noncommutative_no_relation_control
classification: history_fakeout
```

Best profile:

```text
p_viable: 0.9995
order_sensitivity: 1.000
history_mark_predictive_gain: 0.735
history_erasure_delta: 0.988
noncommutative_relation_lineage_excess: 0.000
commutative_delta: 0.694
random_order_delta: 0.651
asymmetric_slack_delta: -0.0093
future_distinct_ratio: 0.988
dynamic_lock_in_index: 0.000
```

Primary result:

```text
noncommutative_history_passed: false
asymmetry_load_bearing: false
relation_load_bearing: false
history_marks_load_bearing: false
future_distinct_slack_detected: true
lock_in_rejected: false
```

Control classifications:

```text
commutative_relation_history: history_fakeout
bias_asymmetry_only: underconstrained
noncommutative_no_relation_control: history_fakeout
reversible_history_control: history_fakeout
random_order_history_control: history_fakeout
lock_in_history_control: history_fakeout
noise_rich_control: history_fakeout
collapse_attractor_control: underconstrained
```

Interpretation:

- Non-commutative update order produces strong future distinction and history
  signals.
- The signal is not relation-conditioned: the no-relation non-commutative
  control ranks best.
- W5 does not show positive non-commutative relation lineage excess.
- Asymmetry is still not load-bearing by the probe's own criterion.

Decision:

```text
Do not run DA1c main scale.
Pause or redesign the DAR world family. The next move should not be more
sampling of this generator; it should either rethink the relation/history
implementation or return to formalization of the stronger COM/fiber witness.
```

### Probe DA2 Smoke: Relational Edge-Memory World

Probe DA2 redesigned the DAR world so memory lives on persistent directed
relations rather than on local nodes. The aim was to prevent the DA1c failure
mode where local/non-relational history faked distinction + asymmetry +
relation.

Run:

- script: `scripts/historical_probes/probe_DA2_relational_edge_memory_world.py`
- result directory: `results/historical_probes/probe_DA2_relational_edge_memory_world_results/`
- scale: `5000` trajectories, `50` seeds
- horizons `{50, 100}`
- `16` sites, `q=4`, edge memory states `m=4`
- 12 worlds
- 18 CPU workers
- valid runtime about `2.7` minutes after reducing diagnostic overhead

Implementation notes:

- An initial attempt exposed a shape bug in perturbation continuation for
  smaller sampled trajectories; fixed by drawing random masks using the current
  sample size rather than `cfg.n_traj`.
- A second attempt exceeded the 20-minute cap because ablation future-ratio
  calls were running full diagnostics. The simulation scale stayed at `5000`,
  but relation estimation was moved to a fixed subsample and ablation
  comparisons use coarse future-ratio diagnostics.

Initial smoke result:

```text
best_world: W6_commutative_edge_memory
full_relational_edge_memory_passed: false
distinction_required: true
relation_required: true
edge_memory_required: true
asymmetry_required: false
local_history_fakeout_rejected: true
commutative_fakeout_rejected: false
random_relation_fakeout_rejected: true
lock_in_rejected: false
```

Best profile:

```text
p_viable: 1.000
edge_memory_predictive_gain: 0.0991
edge_memory_erasure_delta: 0.9993
edge_memory_shuffle_delta: -0.0006
relation_slack_excess: 0.0040
order_sensitivity: 1.000
noncommutative_asymmetry_delta: 0.000
future_distinct_ratio: 0.9993
dynamic_lock_in_index: 0.000
```

Interpretation:

- DA2 did improve over DA1c by killing the local/no-relation fakeout family.
- The decisive failure was asymmetry: commutative edge memory ranked best, so
  order-dependence was not necessary.
- Edge-memory shuffle delta was slightly negative, meaning the current
  future-distinct readout does not care about edge identity strongly enough.

### Probe DA2 Revision: Two-Edge Relational Support

Per the run instruction, one revision was made and tested before closing DA2.
The revision changed only W8: its non-commutative update was made to require a
second stable incoming edge, so the full world depended on two-edge relational
support rather than a single edge channel.

Run:

- result directory: `results/historical_probes/probe_DA2_relational_edge_memory_world_revision_results/`
- same smoke scale and worker count
- runtime about `2.7` minutes

Revision result:

```text
best_world: W6_commutative_edge_memory
full_relational_edge_memory_passed: false
distinction_required: false
relation_required: false
edge_memory_required: false
asymmetry_required: false
local_history_fakeout_rejected: true
commutative_fakeout_rejected: false
random_relation_fakeout_rejected: false
lock_in_rejected: false
```

Interpretation:

- The revision did not rescue W8.
- W6 commutative edge memory still ranked best.
- The two-edge support change weakened the mutual-necessity profile rather than
  making relation/asymmetry cleaner.

Decision:

```text
Do not run DA2 main scale.
The current DAR edge-memory generator should pause. It rejects local history,
but still cannot make non-commutative relational asymmetry uniquely
load-bearing.
```

### DAX-R Smoke: Branching Connection Graph Validity

DAX-R reframed the primitive branch as a substrate-validity problem. The bridge
note added alongside the probe connects the primitive branch to the main Omega
object:

```text
I_T^C(s) = H(F_T(s) / C)
```

where `C` is only admissible if it preserves connection-like transport of
distinction-history through viable futures.

Run:

- bridge note:
  `docs/research_notes/primitive_branch/connection_like_relation_as_coarse_graining_admissibility.md`
- script: `scripts/historical_probes/probe_DAX_branching_connection_graph_validity_revised.py`
- result directory:
  `results/historical_probes/probe_DAX_branching_connection_graph_validity_revised_results/`
- scale: `5000` trajectories, `50` seeds
- horizons `{50, 100}`
- branch probabilities `{0.10, 0.25}`
- `16` nodes, `q=4`
- mean out-degree `3`
- lineage cap `5`
- 10 worlds
- 18 CPU workers
- simulation runtime about `6.9` minutes; output rebuild after aggregation fix
  took about `3` seconds

Implementation note:

- The initial simulation completed successfully but the first output aggregation
  failed because grouped output tables had not rebuilt the interpretation label.
  The labels were added to grouped outputs and the result artifacts were rebuilt
  from the completed raw rows.

Best world:

```text
W4_random_relation
```

Primary substrate result:

```text
connection_substrate_valid: false
relation_transport_load_bearing: false
path_specificity_passed: true
relation_ablation_passed: true
local_memory_fakeout_rejected: false
generic_coupling_fakeout_rejected: true
random_relation_fakeout_rejected: true
commutative_fakeout_rejected: true
lock_in_rejected: true
asymmetric_transport_passed: true
```

Best profile:

```text
transport_identity_accuracy: 1.000
transport_survival_to_horizon: 1.000
path_specificity_delta: -0.010
relation_ablation_delta: 0.020
transport_over_self_delta: 0.750
future_distinct_transport_ratio: 0.394
nontrivial_loop_closure_rate: 0.000
holonomy_diversity_proxy: 0.000
trivial_closure_rate: 1.000
lock_in_index: 0.156
forward_reverse_delta: 1.000
asymmetric_branch_differentiation: 1.000
transport_conflict_rate: 1.000
```

Important W8 behavior:

- W8 showed nonzero path-specificity and relation-ablation signal.
- W8 transport identity accuracy decayed strongly by `T=100`.
- W8 did not reject the local-memory/self-persistence fakeout.
- Loop closure remained trivial rather than nontrivial and diverse.
- Lineage cap hits were frequent, so estimator warnings apply broadly.

Decision:

```text
DAX-R does not establish substrate validity.
Do not proceed to viable-slack or adjudication tests on this substrate.
Next work should redesign the connection substrate, especially lineage-cap
handling, loop closure, and local-memory rejection.
```

### DAX-G0: Minimal DAR Rule-Space Persistence

DAX-G0 opened a more principled primitive-world route by exhaustively auditing
the elementary cellular automata rule space rather than hand-designing another
interesting substrate.

Run:

- research note:
  `docs/research_notes/primitive_branch/minimal_DAR_rule_space_persistence.md`
- script: `scripts/historical_probes/probe_DAX_G0_minimal_DAR_rule_space_persistence.py`
- result directory:
  `results/historical_probes/probe_DAX_G0_minimal_DAR_rule_space_persistence_results/`
- rule space: all `256` elementary cellular automata
- `q=2`, radius `1`
- ring size `256`
- horizon `T=256`
- six initial-condition families
- `64` seeds per initial-condition family
- final retained run used `18` CPU workers across rules
- runtime: about `65` seconds

Hardware note:

- The first completed G0 run was single-process and took about `501` seconds.
- The retained run uses rule-level multiprocessing with 18 workers, which is the
  appropriate hardware path for this workload.
- GPU was not used because ECA motif/component analysis is dominated by many
  small rule-level simulations and Python-side structure extraction, not dense
  tensor kernels.

Primary result:

```text
nontrivial_persistence_found: true
localized_persistence_rule_count: 4
transported_identity_rule_count: 142
emitter_or_generator_rule_count: 44
DAR_complete_enriched: true
DAR_asymmetric_enriched: true
metrics_select_static_or_chaos: false
```

Primitive enrichment:

```text
self_only_rules:                         -0.242 enrichment
neighbor_dependent_symmetric_rules:      -0.192 enrichment
neighbor_dependent_asymmetric_rules:     +0.070 enrichment
irreversible_neighbor_dependent_rules:   -0.014 enrichment
DAR_complete_rules:                      +0.032 enrichment
DAR_asymmetric_rules:                    +0.102 enrichment
```

Top candidate rules:

```text
145, 131, 62, 118, 109, 73, 230, 188, 54, 61, 163, 177
```

Best candidate profile:

```text
rule: 145
classification: localized_persistence
localized_component_lifetime_max: 260.0
recurrence_up_to_shift: 0.814
motif_material_turnover: 0.580
translation_velocity_estimate: -0.0023
future_distinct_descendant_count: 16
frozen_order_index: 0.063
chaos_index: 0.504
```

Interpretation:

- This is the first positive primitive-branch result after the DA/DAX custom
  world failures.
- The result is not that a handpicked rule works. The whole minimal ECA rule
  space was audited.
- Nontrivial persistence is enriched in DAR-complete and especially
  DAR-asymmetric rules.
- The metrics did not simply select static/frozen or chaotic controls.

Decision:

```text
Proceed to DAX-G1: Persistence Motif Anatomy and Robustness.
Treat G1 as diagnostic anatomy, not theory validation.
```

### DAX-G1: Persistence Motif Anatomy and Robustness

DAX-G1 took the G0 candidates and controls and asked whether the apparent
persistence is identity-through-transformation rather than frozen order, chaos,
collapse, or shift/identity triviality.

Run:

- script: `scripts/historical_probes/probe_DAX_G1_persistence_motif_anatomy_and_robustness.py`
- result directory:
  `results/historical_probes/probe_DAX_G1_persistence_motif_anatomy_and_robustness_results/`
- candidates: G0 localized, transported-identity, and emitter/generator rules
- controls: collapse, frozen/orderly, chaotic, identity/shift/complement rules
- horizons: `T=256,512,1024`
- ring sizes: `256,512`
- eight initial-condition families including two G0 motif-focused seeds
- `256` seeds per evaluation cell
- `18` CPU workers
- runtime: about `16.7` minutes

Hardware note:

- GPU was not used. This probe is dominated by many ECA simulations and
  motif/component bookkeeping rather than dense numeric kernels. Rule/evaluation
  multiprocessing is the correct path for this workload.

Primary result:

```text
confirmed_persistence_motif_count: 4
confirmed_rules: 169, 225, 73, 109
top_confirmed_rule: 169
stable_across_T: true
stable_across_ring_size: true
robust_to_light_perturbation: true
collapse_controls_rejected: true
frozen_controls_rejected: true
chaotic_controls_rejected: true
identity_shift_controls_rejected: true
```

Top confirmed profile:

```text
rule: 169
motif_type: emitter
recurrence_up_to_shift: 0.769
material_turnover_rate: 0.246
background_contrast: 1.000
post_perturbation_survival_rate: 1.000
future_distinct_descendant_count: 236
frozen_order_index: 0.070
chaos_index: 0.266
```

Primitive association after the stricter anatomy filter:

```text
DAR_complete_enriched_after_filter: false
DAR_asymmetric_enriched_after_filter: false
relation_dependent_enriched_after_filter: true
asymmetry_dependent_enriched_after_filter: false
```

Sidecars:

```text
recoverability robust motif count: 15
best post-perturbation survival rate: 1.000
relation-dependence positive ablations: 10
asymmetry-dependence positive ablations: 7
composition-positive interactions: 0
best stable product rate: 0.000
```

Interpretation:

- G1 confirms that G0 was not merely selecting static, chaotic, collapse, or
  identity/shift controls.
- The strongest survivors look like emitter-like persistence motifs with
  recurrence, turnover, contrast, and perturbation survival.
- The stricter anatomy filter narrows the primitive claim: relation-dependence
  remains weakly enriched, but DAR-complete and DAR-asymmetric enrichment do not
  survive as a clean filtered result.
- The interaction/composition sidecar is negative. At this stage the motifs are
  robust individual structures, not evidence for compositional motif algebra.

Decision:

```text
Proceed to DAX-G2 only as a phase-map/anatomy follow-up.
Do not claim that G1 validates Omega or that DAR asymmetry is established.
The live positive object is robust local persistence in minimal rule space;
the open problem is whether richer minimal spaces recover relation/asymmetry
load-bearing and composition.
```

### DAX-G2 Smoke: Persistence Phase Map Across Minimal Rule Spaces

DAX-G2 tested the smallest principled expansions beyond ECA:

```text
q=3, radius=1  -> more distinction richness
q=2, radius=2  -> more relation context
```

Run:

- script: `scripts/historical_probes/probe_DAX_G2_persistence_phase_map_minimal_rule_spaces.py`
- result directory:
  `results/historical_probes/probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results/`
- sampled rules:
  - `350` q=3/r=1 rules
  - `350` q=2/r=2 rules
  - `33` ECA anchors
- stage 1: `T=192`, ring `256`, `48` seeds
- stage 2: `T=512`, ring `256`, `64` seeds
- stage 2 cap: `90` rules
- `18` CPU workers
- runtime: about `3.1` minutes

Hardware note:

- GPU was not used. This workload is many small cellular automaton simulations
  plus motif bookkeeping; process-level CPU parallelism is the right path.

Primary smoke result:

```text
ECA_anchor confirmed motifs: 2
q3_radius1 confirmed motifs: 6
q2_radius2 confirmed motifs: 3

q3_radius1 relation positives: 4
q3_radius1 asymmetry positives: 5
q3_radius1 composition positives: 4

q2_radius2 relation positives: 2
q2_radius2 asymmetry positives: 1
q2_radius2 composition positives: 2
```

Best candidate:

```text
space: q3_radius1
rule_id: q3r1_s5_0016
stratum: S5_asymmetric_neighbor_dependent
confirmed_fraction: 0.75
recurrence_up_to_shift: 0.772
material_turnover_rate: 0.234
relation_dependence_delta: 0.0276
asymmetry_dependence_delta: 0.0785
post_perturbation_survival_rate: 1.000
composition_outcome: emission
frozen_order_index: 0.0157
chaos_index: 0.101
```

Guardrail failure:

```text
controls_rejected: false
q3_radius1 control leaks: 18
q2_radius2 control leaks: 16
```

Interpretation:

- The expanded spaces produced exactly the kind of missing-invariant hints G2
  was designed to look for: q=3/r=1 especially shows persistence plus
  relation/asymmetry positive deltas and nonzero interaction readouts.
- The result is not interpretable as a pass because symmetric and self/control
  strata leaked into persistence-positive classes.
- The likely issue is that the current persistence classifier is too permissive
  for expanded spaces; it allows symmetric transported/domain motifs to count
  before asymmetry/load-bearing filters are applied.
- The composition readout is also preliminary: several positives are broad
  `emission` outcomes, not yet stable compositional motif algebra.

Decision:

```text
Do not run the full G2 main pass yet.
Run a DAX-G2 metric guardrail revision first:
  tighten control rejection;
  separate persistence from load-bearing persistence;
  require control-adjusted relation/asymmetry deltas before composition claims;
  then rerun the q=3/r=1 branch if controls are clean.
```

### DAX-G2b: Control-Adjusted Primitive Load-Bearing Guardrail

DAX-G2b repaired the failed G2 control guardrail by comparing each target rule
against matched counterfactuals rather than raw persistence alone.

Run:

- script: `scripts/historical_probes/probe_DAX_G2b_control_adjusted_primitive_guardrail.py`
- result directory:
  `results/historical_probes/probe_DAX_G2b_control_adjusted_primitive_guardrail_results/`
- target rules: `50`
- matched controls: `765`
- scale: `T=512`, ring `256`, `128` seeds
- matched controls:
  - center-only projection
  - neighbor-removed projections
  - left/right symmetrized rule
  - q=3 symbol-phase-only control
  - output-distribution-matched random control
  - stratum-matched nulls
- `18` CPU workers
- runtime: about `14.6` minutes

Primary result:

```text
guardrail_passed: true
q3_control_leaks_resolved: true
control_adjusted_positive_count: 6
relation_adjusted_positive_count: 42
asymmetry_adjusted_positive_count: 30
local_phase_fakeout_rejected_count: 16
composition_adjusted_positive_count: 2
```

Leak resolution:

```text
symmetric_control_leaks_resolved: true
self_control_leaks_resolved: true
remaining_leaks: none
```

Clean q=3/r=1 survivor:

```text
rule_id: q3r1_s1_0002
stratum: S1_random_unbiased
raw_persistence_score: 0.1695
adjusted_persistence: 0.0734
relation_load_bearing_adjusted: 0.0755
asymmetry_load_bearing_adjusted: 0.1686
local_phase_fakeout_rejected: true
composition_adjusted_delta: 1.000
dominant_interaction_outcome: new_motif
reclassification: control_adjusted_positive
```

Important q=3/r=1 near miss:

```text
rule_id: q3r1_s5_0016
relation_load_bearing_adjusted: 0.1475
asymmetry_load_bearing_adjusted: 0.1253
local_phase_fakeout_rejected: true
composition_adjusted_delta: 0.000
dominant_interaction_outcome: emission
reclassification: emission_only
```

Interpretation:

- G2b resolves the main G2 worry: the q=3/r=1 symmetric/self leaks are now
  classified as fakeouts rather than positives.
- At least one q=3/r=1 candidate survives matched controls with relation and
  asymmetry load-bearing plus a non-emission composition readout.
- The earlier headline candidate `q3r1_s5_0016` should be retained as a
  load-bearing persistence candidate, but not as a composition candidate because
  its interaction behavior is emission-only.
- ECA anchors still look robust on persistence/relation, but they do not change
  the G2b decision because the target question was whether q=3/r=1 survives the
  expanded-space guardrail.

Decision:

```text
Proceed to a focused q=3/r=1 guardrailed phase map.
Do not broaden beyond q=3/r=1 yet.
Keep composition separate from persistence/load-bearing until more candidates
show non-emission interaction structure.
```

### DAX-G3: Focused q=3/r=1 Guardrailed Phase Map

DAX-G3 tested whether the G2b q=3/r=1 survivor was an isolated accident or part
of a reproducible class. It kept the G2b guardrails active from the start.

Run:

- script: `scripts/historical_probes/probe_DAX_G3_q3r1_guardrailed_phase_map.py`
- result directory: `results/historical_probes/probe_DAX_G3_q3r1_guardrailed_phase_map_results/`
- rule space: q=3, radius=1 only
- sampled rules: `2006`
- stage 2 candidates: `225`
- stage 1: `T=256`, ring `256`, `64` seeds
- stage 2 guardrail: `T=512`, ring `256`, `96` seeds
- stratum nulls per candidate: `4`
- workers: `18`
- runtime: about `48.5` minutes

Implementation note:

- A larger half-scale run was attempted first, but it exceeded the two-hour
  command cap near the end of guardrail evaluation. The retained run uses the
  spec fallback more aggressively: quarter sampling, Stage 2 cap `120` plus
  leaks/anchors, and `96` guardrail seeds.

Primary result:

```text
q3r1_trunk_reproduced: true
strong_pass: false
guardrails_remained_clean: true
control_adjusted_positive_count: 9
relation_adjusted_positive_count: 161
asymmetry_adjusted_positive_count: 145
local_phase_fakeout_rejected_count: 99
composition_adjusted_positive_count: 25
non_emission_composition_positive_count: 25
```

Control leak result:

```text
S7 symmetric control leaks evaluated: 81
S8 self-control leaks evaluated: 18
remaining leaks: none
```

Best control-adjusted candidate by adjusted persistence:

```text
rule_id: q3g3_s1_00108
stratum: S1_random_unbiased
adjusted_persistence: 0.1303
relation_load_bearing_adjusted: 0.1193
asymmetry_load_bearing_adjusted: 0.1881
local_phase_fakeout_rejected: true
composition_adjusted_delta: 0.000
dominant_interaction_outcome: collapse
reclassification: control_adjusted_positive
```

Reproduced G2b anchor:

```text
rule_id: q3r1_s1_0002
adjusted_persistence: 0.0167
relation_load_bearing_adjusted: 0.0744
asymmetry_load_bearing_adjusted: 0.1676
local_phase_fakeout_rejected: true
composition_adjusted_delta: 1.000
dominant_interaction_outcome: new_motif
reclassification: control_adjusted_positive
```

Important interpretation:

- q=3/r=1 did reproduce a guardrailed primitive-positive family.
- It did not reach the strong-pass threshold: there were 9
  control-adjusted-positive candidates, not 10, and only a smaller overlap of
  all desired properties.
- The largest adjusted-persistence rows were often emission-only or local-phase
  / self fakeouts. Raw adjusted persistence alone is not enough.
- Composition is present as a non-emission signal in the broader candidate set,
  but it is not yet cleanly unified with the strongest persistence candidates.

Decision:

```text
q=3/r=1 becomes the current primitive-branch trunk.
Next probe should be DAX-G4: q=3/r=1 motif ecology and mechanism anatomy.
Do not broaden rule space yet.
Keep composition separate from persistence/load-bearing until the overlap is
cleaner.
```

## 2026-05-15: Probe DAX-G4 q=3/r=1 Motif Ecology and Mechanism Anatomy

Script:

```text
scripts/historical_probes/probe_DAX_G4_q3r1_motif_ecology_mechanism.py
```

Result directory:

```text
results/historical_probes/probe_DAX_G4_q3r1_motif_ecology_mechanism_results/
```

G4 stayed inside q=3/r=1 and reused the G3 Stage 2 measurements. The new-motif
persistence check reused G3's T=512, ring=256, N=96 measurements, which exceed
the requested N=64 sanity check.

Primary result:

```text
analyzed_rule_count: 225
control_adjusted_positive_count: 9
motif_family_count: 11
families_identified: true
fertile_bands_identified: true
invariant_overlap_nonempty: true
composition_gap_explained: true
new_motif_outcomes_persistent: true
```

Invariant overlap:

```text
all_core_invariants_count: 3
persistence_relation_asymmetry_count: 34
composition_overlap_count: 3
```

Composition gap:

```text
new_motif_count: 7
new_motif_persistent_count: 4
strong_persistence_composition_overlap_count: 0
```

Interpretation:

- q=3/r=1 contains a real descriptive motif ecology, not only isolated hits.
- The 9 validation positives split across strong-persistence, weak-persistence,
  and composition-overlap families.
- Composition is not an emission-only artifact in this pass, but it is sparse
  and does not overlap the strongest persistence band.
- There are 25 near-validation persistence/relation/asymmetry rules that fail
  composition, which makes persistence/relation/asymmetry the cleaner next
  detector target.

Decision:

```text
Proceed to DAX-G5 detector freeze for q=3/r=1 persistence/relation/asymmetry.
Track composition as a secondary branch.
Do not promote composition into the primary validation claim yet.
```

## 2026-05-15: Probe DAX-G5 q=3/r=1 Detector Freeze and Held-Out Prediction

Script:

```text
scripts/historical_probes/probe_DAX_G5_q3r1_detector_freeze_heldout_prediction.py
```

Result directory:

```text
results/historical_probes/probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results/
```

G5 wrote the detector freeze and preregistration before held-out sampling:

```text
results/historical_probes/probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results/detector_freeze.json
docs/research_notes/primitive_branch/q3r1_detector_freeze_v1.md
docs/research_notes/primitive_branch/q3r1_G5_preregistration.md
```

Run:

```text
heldout rules: 5000
fertile rules: 3000
control rules: 2000
workers: 18
runtime: about 140.6 minutes
stage2 cap: 50 per band
```

Primary result:

```text
heldout_prediction_passed: false
fertile_primary_positive_count: 7
control_primary_positive_count: 4
fertile_primary_positive_rate: 0.00233
control_primary_positive_rate: 0.00200
fertile_vs_control_enrichment: 1.17x
control_leak_count: 4
fisher_exact_greater_p: 0.533
```

Band result:

```text
F1 G4 top S1 random-unbiased: 2 / 1000
F2 high relation/asymmetry: 3 / 1000
F3 near-validation PRA: 2 / 1000
B1 S7 symmetric control: 0 / 500
B2 S8 self-only control: 0 / 500
B3 output-distribution matched random: 0 / 500
B4 high-chaos/high-frozen barren: 4 / 500
```

Secondary composition:

```text
non_emission_composition_positive_count: 42
new_motif_persistent_count: 4
composition_overlap_with_primary_count: 0
```

Interpretation:

- The frozen detector found held-out positives in every fertile band, but not at
  a rate meaningfully above controls.
- S7, S8, and output-distribution matched controls stayed clean.
- The B4 high-chaos/high-frozen barren band produced 4 primary positives and
  blocks the predictive-detector claim.
- Composition remained secondary and did not overlap primary positives.

Decision:

```text
G5 fails as a held-out predictive detector.
Do not modify the frozen detector inside G5 to rescue the result.
Return to mechanism/ecology analysis or redesign the detector target.
```

```text
COM fiber transport object
certified viable fiber node
certified viable transport edge
component projection preservation
multi-step viable propagation
relationship between propagation and entropy
```

Then run one of:

1. revised learned-kappa recovery against the formal object;
2. independent toy substrate generalization;
3. targeted noise/potential dependence map.

### Open Questions

- Is `center_of_mass` an intrinsic object or a convenient proxy for a deeper
  transport coordinate?
- Can a constrained learning procedure rediscover COM-like propagation?
- Does the same object survive a genuinely different substrate?
- Can component preservation be made less heuristic than entropy-ratio
  preservation?
- What part of the older theoretical corpus corresponds exactly to this COM
  fiber transport object?

### Git Notes

Large raw files are intentionally ignored:

- virtual environments and caches;
- smoke/benchmark runs;
- per-seed raw CSVs beginning with `_`;
- massive Probe 09 graph node/edge CSVs.

Before pushing future work:

```powershell
git status --short
git diff --cached --name-only
git push
```

Use the repo URL:

```text
https://github.com/6ixpoolgames/Omega
```

## 2026-05-17 - VAL0-CT bounded smoke implementation

Implemented the first VAL0-CT constructor task algebra harness as
`omega.val0_ct` and ran a bounded CPU smoke batch.

Run artifact:

```text
results/val0_ct/20260517_223635/
```

Configuration:

```text
families: low_resolution_dense, structured_asymmetric, lock_in_seeded
policies: random, R0, R0_lookahead, R1, pseudo_omega
seeds: 20
h: 1, 2, 4
H: 4, 8
T: 16, 32
workers: 18
num_tasks: 64
sample_size: 256
max_paths: 512
rows: 3600
elapsed: 1778.7 seconds
```

Important workflow result:

```text
An unbounded/exact 20-seed attempt hit a one-hour timeout before producing
results. The completed run is therefore an explicitly bounded smoke, not an
exhaustive path enumeration.
```

Aggregate read:

- `low_resolution_dense` blurred R0/R1 as expected.
- `structured_asymmetric` did not yet separate `R1` from matched
  `R0_lookahead`; both averaged near 0.70 global LHR.
- `lock_in_seeded` produced the intended pseudo-Omega diagnostic: the
  `pseudo_omega` policy averaged low global LHR (~0.20), high local LHR
  (~22.1), and 100% pseudo-Omega flag rate.
- `R1` and `R0_lookahead` are currently almost indistinguishable, so the
  harness is working but the R1 operational distinction is not yet sharp.

Decision:

```text
Treat this as a workflow/harness validation and a successful pseudo-Omega
negative diagnostic, not as a positive proto-Omega result. Next revision should
focus on threshold calibration, R1 selector design, and structured generators
that can distinguish robust future reachability from greedy peak lookahead.
```

## 2026-05-18 - VAL0-CT overnight divergence prep and timeout

Pulled `docs/VAL0_CT_OVERNIGHT_BATCH_SPEC.md` and
`docs/VAL0_CT_RUNBOOK.md`, then implemented the overnight calibration harness:

- added `brittle_peak` and `structured_asymmetric_v2` generators;
- added deterministic hand-built cases;
- added R1/R0-lookahead same-choice, score-gap, candidate-variance, and
  local/global audit diagnostics;
- added per-family seed-count support to `run_smoke.py`;
- disabled stored per-step traces by default to keep overnight JSONL size
  manageable.

Deterministic gate:

```text
results/val0_ct/deterministic_cases_overnight_prep_v2/
```

The brittle-peak hand case passed:

```text
R1 task: 1
R0-lookahead task: 0
same_choice: 0
R1 global LHR: 0.929
R0-lookahead global LHR: 0.857
```

Local calibration:

```text
results/local_runs/val0_ct_overnight_calibration/
```

Calibration read:

- `brittle_peak`: R1 mean global LHR 0.477 vs R0-lookahead 0.416.
- `structured_asymmetric_v2`: R1 mean global LHR 0.528 vs R0-lookahead 0.504.
- `low_resolution_dense`: R1 and R0-lookahead remained nearly matched.
- `lock_in_seeded`: pseudo-Omega retained the local/global split.

Full overnight attempt:

```text
results/val0_ct/20260518_040447/
```

Attempted grid:

```text
brittle_peak=150 seeds
structured_asymmetric_v2=100 seeds
lock_in_seeded=50 seeds
low_resolution_dense=50 seeds
h = 1, 2, 4
H = 4, 8, 16
T = 16, 32, 64
workers = 18
sample_size = 256
max_paths = 512
```

Outcome:

```text
Timed out at the 10-hour cap before normal completion.
```

No analyzable rows were produced because the runner buffered rows in memory
until completion. This was a workflow defect. `run_smoke.py` has now been
patched to stream JSONL rows as they complete, so future interrupted runs leave
salvageable partial results.

Recommended next run:

```text
Split the overnight grid into smaller family/horizon batches, or drop T=64 and
H=16 for the main randomized sweep. Keep brittle_peak prioritized, because the
deterministic and local calibration results show the desired separation geometry.
```

## 2026-05-18 - VAL0-CT runner hardening

Fixed the long-run harness failure exposed by the timed-out overnight attempt.

Root cause:

```text
run_smoke.py used ordered result collection and normal-completion-only
aggregation. A timeout before normal completion could leave only config.json.
```

Implemented fixes:

- replaced ordered `executor.map` collection with bounded pending futures and
  first-completed collection;
- added `--max-runtime-seconds` and `--shutdown-reserve-seconds` so the runner
  exits on its own clock instead of relying on an external timeout;
- added streaming `results.jsonl` writes for every completed row;
- added periodic checkpoint aggregation to `aggregate.csv` and `summary.md`;
- added `status.json` with completed/submitted/cancelled/remaining counts;
- added `--max-pending-multiplier` to prevent the whole grid from being in
  flight at once;
- added `--job-order interleaved` as the default so partial runs cover families
  and horizons instead of only the first family in the submission order.

Validation probes:

```text
results/local_runs/runner_normal_completion_probe/
results/local_runs/runner_partial_exit_probe/
results/local_runs/runner_interleaved_partial_probe/
```

The forced partial-exit probe produced durable partial outputs:

```text
status: partial_time_budget_stop
completed rows: 67
result files: results.jsonl, aggregate.csv, summary.md, status.json
family coverage: brittle_peak, structured_asymmetric_v2, lock_in_seeded,
low_resolution_dense
```

Operational consequence:

```text
Future long runs should use the runner's own wall-clock controls, interleaved
job ordering, and checkpointing. External timeouts are now a last-resort guard,
not the primary shutdown mechanism.
```

## 2026-05-18 - VAL0-CT safe main breadth run

After hardening the runner, completed the scoped breadth run:

```text
results/val0_ct/20260518_safe_main_h4h8_t16t32/
```

Scope:

```text
families:
  brittle_peak=150 seeds
  structured_asymmetric_v2=100 seeds
  lock_in_seeded=50 seeds
  low_resolution_dense=50 seeds

h = 1, 2, 4
H = 4, 8
T = 16, 32
workers = 18
sample_size = 256
max_paths = 512
rows = 21000
elapsed = 16181.9 seconds
status = completed
```

Primary read:

- `brittle_peak`: R1 mean global LHR 0.471 vs R0-lookahead 0.383.
- `structured_asymmetric_v2`: R1 mean global LHR 0.496 vs R0-lookahead
  0.432.
- `low_resolution_dense`: R1 and R0-lookahead remained matched, as expected.
- `lock_in_seeded`: pseudo-Omega retained low global LHR, high local LHR, and
  1.000 pseudo-Omega flag rate.

Horizon dependence:

- R1 advantage concentrates at `h = 1` and `h = 2`.
- At `h = 4`, same-choice rates rise and the R1/R0-lookahead difference mostly
  collapses.

Decision:

```text
This is a successful VAL0-CT calibration result for the R1/R0-lookahead
distinction in generated brittle/robust task algebras. It remains a calibration
result, not full Omega validation.
```

## 2026-05-19 - VAL0-CT targeted horizon confirmations

After the safe breadth run, ran two targeted harder-horizon confirmations within
the corrected 15-hour budget.

### H16 T64 collapse-boundary run

```text
results/val0_ct/20260518_targeted_h16_t64/
```

Scope:

```text
h = 1, 2
H = 16
T = 64
rows = 2500
status = completed
elapsed = 2260.7 seconds
```

Read:

```text
Global LHR collapsed to zero for every family and policy.
```

Decision:

```text
Treat T = 64 as over-hard for the current 64-task generators. This is a
collapse-boundary diagnostic, not a useful R1/R0-lookahead comparison.
```

### H16 T32 confirmation run

```text
results/val0_ct/20260518_targeted_h16_t32/
```

Scope:

```text
h = 1, 2
H = 16
T = 32
rows = 2500
status = completed
elapsed = 1955.4 seconds
```

Primary read:

- `brittle_peak`: R1 mean global LHR 0.539 vs R0-lookahead 0.189.
- `structured_asymmetric_v2`: R1 mean global LHR 0.577 vs R0-lookahead
  0.289.
- `low_resolution_dense`: R1 0.534 vs R0-lookahead 0.535, matched as expected.
- `lock_in_seeded`: pseudo-Omega retained the destructive-lock-in diagnostic.

Band-level read:

- `brittle_peak`, `h=1`: R1 0.360 vs R0-lookahead 0.190.
- `brittle_peak`, `h=2`: R1 0.719 vs R0-lookahead 0.188.
- `structured_asymmetric_v2`, `h=1`: R1 0.412 vs R0-lookahead 0.313.
- `structured_asymmetric_v2`, `h=2`: R1 0.742 vs R0-lookahead 0.265.

Decision:

```text
This is the strongest current VAL0-CT calibration evidence that R1 can
outperform equal-budget greedy peak reachability in generated brittle/robust
task algebras. It remains calibration evidence, not full Omega validation.
```

## 2026-05-19 - VAL0-CT held-out Phase 1 scale probe

Pulled `docs/VAL0_CT_HELDOUT_GENERALIZATION_SPEC.md` and implemented a small
scale-readiness probe for held-out generator generalization.

Implemented generator variants:

- `cost_brittle`
- `delayed_robust`
- `unlabeled_structural`

Deferred:

```text
reliability_brittle
```

Reason:

```text
The current R0/R1 implementation does not yet use reliability weighting, so a
reliability_brittle run would be misleading unless reliability-sensitive
reachability is implemented first.
```

Important caveat:

```text
cost_brittle is currently a structural proxy. Task costs are populated, but
R0/R1 are not budget-aware yet, so the cost barrier is also encoded through
downstream obstruction/sinks.
```

Tiny local sanity:

```text
results/local_runs/heldout_generator_tiny_sanity/
```

Phase 1 scale probe:

```text
results/val0_ct/20260519_heldout_phase1_scale_probe/
```

Scope:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  cost_brittle
  delayed_robust
  unlabeled_structural

seeds: 20 per family
h = 1, 2
H = 16
T = 32
rows = 1200
elapsed = 1400.5 seconds
status = completed
```

Operational read:

```text
The hardened runner is ready to scale into a 12-hour run.
```

At observed throughput, a 5,000-7,000 row Phase 2 run should fit comfortably
inside 12 hours.

Scientific read:

- Known positive anchors reproduced:
  - `brittle_peak`: R1 0.551 vs R0-lookahead 0.183.
  - `structured_asymmetric_v2`: R1 0.563 vs R0-lookahead 0.282.
- Negative control remained matched:
  - `low_resolution_dense`: R1 0.532 vs R0-lookahead 0.531.
- Held-out variants are mixed:
  - `cost_brittle`: R1 0.582 vs R0-lookahead 0.662; R1 only wins at `h=2`.
  - `delayed_robust`: R1 0.620 vs R0-lookahead 0.748.
  - `unlabeled_structural`: R1 0.421 vs R0-lookahead 0.428 overall; weak R1 win at `h=2`.

Recommendation:

```text
Scale next, but do not distribute compute evenly across all new variants.
Prioritize anchors, low_resolution_dense, lock_in_seeded, and
unlabeled_structural with structural post-classification. Treat cost_brittle and
delayed_robust as generator-debug/calibration arms unless revised first.
```

## 2026-05-19 - VAL0-CT brittleness sidecar smoke

Pulled `docs/VAL0_CT_BRITTLENESS_SIDECAR_SPEC.md` and implemented a
diagnostic-only brittleness sidecar.

3P constraint:

```text
principled:
  brittleness = perturbation-sensitive structured reachability

parsimonious:
  sidecar only; no R1 or policy changes

predictive:
  test whether measured brittleness predicts R1 advantage
```

Implementation:

- added `omega/val0_ct/brittleness.py`;
- added `omega/val0_ct/run_brittleness_smoke.py`;
- sidecar computes candidate structuredness, perturbation sensitivity,
  candidate brittleness, R0-lookahead chosen brittleness, R1 chosen brittleness,
  and chosen-brittleness gap;
- stresses used: enabled drop, obstruction add, horizon extension;
- cost/reliability stresses remain deferred.

Important implementation correction:

```text
The first tiny smoke let low_resolution_dense look brittle because the metric
was too close to raw reachability. Added a density penalty to structuredness.
```

Smoke artifact:

```text
results/val0_ct/20260519_brittleness_sidecar_smoke_v2/
```

Scope:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  lock_in_seeded

seeds: 8
h = 1, 2
H = 16
T = 32
candidate sample = 32
stress samples = 4
rows = 64
elapsed = 1087.8 seconds
```

Result:

- `low_resolution_dense` brittleness was suppressed to 0.000, which is good.
- Positive anchors still showed R1 advantage:
  - `brittle_peak`: mean R1 advantage 0.408.
  - `structured_asymmetric_v2`: mean R1 advantage 0.322.
- The key predictive sanity check failed:
  - `brittle_peak` chosen-brittleness gap = -0.010.
  - `structured_asymmetric_v2` chosen-brittleness gap = -0.017.
  - brittleness/R1-advantage correlation was near zero or negative.

Decision:

```text
Do not scale the current brittleness sidecar. It is a useful negative result:
the present proxy does not yet explain R1's advantage over R0-lookahead.
Revise toward path-variation / retained-depth collapse diagnostics before
including brittleness in a held-out generalization run.
```

## 2026-05-19 - VAL0-CT 12-hour held-out exploratory run

Pulled `docs/VAL0_CT_12H_HELDOUT_EXPLORATORY_SPEC.md` and ran the scoped
held-out exploration without changing R1 or scaling the failed brittleness
sidecar.

Main artifact:

```text
results/val0_ct/20260519_12h_heldout_exploratory/
```

Scope:

```text
unlabeled_structural = 150 seeds
cost_brittle = 100 seeds
delayed_robust = 100 seeds
low_resolution_dense = 50 seeds
lock_in_seeded = 50 seeds
brittle_peak = 40 seeds
structured_asymmetric_v2 = 40 seeds
h = 1, 2
H = 16
T = 32
rows = 5300
elapsed = 5477.0 seconds
status = completed
```

Read:

- Anchors reproduced:
  - `brittle_peak`: R1 0.547 vs R0-lookahead 0.176.
  - `structured_asymmetric_v2`: R1 0.571 vs R0-lookahead 0.277.
- Controls behaved:
  - `low_resolution_dense`: R1 0.534 vs R0-lookahead 0.535.
  - `lock_in_seeded / pseudo_omega`: global LHR 0.000, local LHR 22.400,
    pseudo-Omega flag 1.000.
- Held-out families did not show broad R1 generalization:
  - `cost_brittle`: R1 0.576 vs R0-lookahead 0.664.
  - `delayed_robust`: R1 0.614 vs R0-lookahead 0.740.
  - `unlabeled_structural`: R1 0.398 vs R0-lookahead 0.440.

Additional unlabeled-only extension:

```text
results/val0_ct/20260519_unlabeled_structural_extension/
```

Scope:

```text
unlabeled_structural = 300 seeds
h = 1, 2
H = 16
T = 32
rows = 3000
elapsed = 1682.5 seconds
status = completed
```

Combined unlabeled analysis:

```text
h = 1:
  mean R1 advantage = -0.057
  win rate = 0.23

h = 2:
  mean R1 advantage = -0.031
  win rate = 0.26

highest candidate-variance quintiles:
  h = 1 mean R1 advantage = -0.027, win rate = 0.309
  h = 2 mean R1 advantage = -0.006, win rate = 0.346
```

Decision:

```text
Do not claim held-out generator generalization yet. The best new hook is that
candidate variance in unlabeled_structural moves R1 toward parity but not into a
clean win. Future probes should classify unlabeled regimes by measured
peak-retention / terminal-depth structure rather than adding more named
brittle/robust generators.
```
## 2026-05-23 - RFS-MB0 neutral transform reset smoke

Implemented the substrate reset from `docs/RFS_MB0_NEUTRAL_TRANSFORM_RESET_SPEC.md` as a new active MB0 branch:

```text
omega/rfs_mb0_neutral_transform/
```

This replaces continued development of the semantic `rfs_mb0_pairwise` toy substrate. The older branch remains workflow validation only.

Run:

```text
results/rfs_mb0_neutral_transform/20260523_neutral_transform_reset_smoke/
```

Shape:

```text
systems: 50
rows: 350
workers: 18
errors: 0
status: COMPLETED
```

Read:

- Neutral finite transform substrate implemented.
- Derived singleton and pairwise signature filtrations computed across `H = 0,1,2,4,8,12,16`.
- Phase/fixed/permissive/strict controls are identifiable.
- Structured neutral contraction appears in `shared_constraint_conflict` and `anti_correlated_block_transforms`.
- Random and degree-preserving controls still mimic contraction, so the scientific gate is not passed.

Next:

Improve control separation before scaling. Preserve neutrality; do not add cost/resource/semantic machinery yet.

## 2026-05-23 - RFS-MB0 future-landscape pattern smoke

Implemented the next substrate reset from `docs/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md`:

```text
omega/rfs_mb0_future_landscape/
```

This branch treats the object of interest as neutral deformation of reachable futures. It computes future-profile maps from finite states, neutral relations, exact frontiers, horizon reachability, and probe-signature distributions.

Run:

```text
results/rfs_mb0_future_landscape/20260523_future_landscape_smoke/
```

Shape:

```text
systems: 33
future profiles: 672
workers: 18
errors: 0
status: COMPLETED
elapsed: about 2.9 seconds
```

Read:

- Implementation and output schema passed.
- Graceful status/checkpoint behavior passed.
- Collapse, cycle, permissive, and strict controls separate cleanly.
- `structured_propagation` also labels random, degree-preserving, and coordinate-permutation controls.
- Scientific gate is not passed yet because the structured class boundary is too broad.

Next:

Do not scale this exact detector. Strengthen neutral matched controls and require structured-profile separation from those controls before spending larger compute.

## 2026-05-23 - RFS-MB0 future-landscape detector v1 smoke

Implemented the detector revision from `docs/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md`.

Updated branch:

```text
omega/rfs_mb0_future_landscape/
```

Run:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_smoke_conservative/
```

Shape:

```text
systems: 33
future profiles: 3696
workers: 18
errors: 0
status: COMPLETED
elapsed: about 44 seconds
```

Changes:

- Preserved v0 as `heuristic_profile_class_v0`.
- Added `control_relative_profile_class_v1`.
- Replaced hand-listed probes with mechanical `sigma = 2` probe generation.
- Added transition-level signature MI, conditional entropy, entropy-rate proxy, grammar-size proxy, and motif-reuse proxy.
- Added random / degree / probe-marginal null bundle outputs.
- Added saturation diagnostics and conservative saturation handling.

Read:

- Implementation gate passed.
- v1 correctly withholds saturated structured/relation families rather than calling them structured without saturation-matched nulls.
- Random relation control is no longer called structured in the conservative run.
- Degree-preserving control still produces 39 `structured_propagation` profiles.
- Scientific gate remains unpassed, now for a narrower matched-control reason.

Next:

Do not scale yet. Add frontier-size-preserving and saturation-matched nulls, then require degree-control separation at the family/probe-family level.

## 2026-05-23 - Public-facing status refresh

Updated the front-facing repo documentation after the RFS-MB0 future-landscape detector v1 smoke.

Files updated:

```text
README.md
docs/PUBLIC_RESULTS_INDEX.md
docs/OMEGA_PROJECT_MANUAL.md
docs/research_notes/omega_theory/public_terms_and_translations.md
docs/research_notes/omega_theory/omega_glossary.md
```

Current public posture:

```text
active branch: RFS-MB0 future-landscape detection
implemented detector: v1
implementation status: passed
scientific gate: not passed
main blocker: degree-preserving control false positives
next target: frontier-size and saturation-matched null repair
```

## 2026-05-23 - RFS-MB0 future-landscape detector v1.1 smoke

Implemented the code-audit hardening targets from:

```text
docs/RFS_MB0_FUTURE_LANDSCAPE_V1_1_CODE_TARGETS.md
```

Run:

```text
results/rfs_mb0_future_landscape/20260523_detector_v1_1_smoke/
```

Shape:

```text
systems: 33
future profiles: 3696
workers: 18
errors: 0
status: COMPLETED
elapsed: about 42 seconds
```

Changes:

- Added local-vs-aggregate classification split.
- Added `local_profile_class_v1_1`.
- Added `aggregate_family_class_v1_1`.
- Added `aggregate_probe_family_class_v1_1`.
- Added explicit `frontier_size` matched-null output.
- Added `aggregate_family_classes.csv`, `aggregate_probe_family_classes.csv`, `degree_control_false_positives.csv`, and `matched_null_summary.csv`.

Read:

- v1 still shows 39 local degree-control false positives.
- v1.1 prevents those local hits from promoting aggregate claims.
- Degree-control aggregate probe-family passes: 0.
- Aggregate structured family count: 0.
- Scientific gate remains not passed because no non-control, non-saturated family passes.

Next:

Keep v1.1 as the current detector discipline. Do not scale until there is either a non-saturating structured candidate family or stronger saturation/frontier-matched null machinery.

## 2026-05-23 - RFS-MB0 future-landscape long-horizon environment audit

Implemented the long-horizon audit from:

```text
docs/RFS_MB0_FUTURE_LANDSCAPE_LONG_HORIZON_ENVIRONMENT_AUDIT.md
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_future_landscape_long_horizon_environment_audit_result.md
```

Primary run:

```text
results/rfs_mb0_future_landscape/20260523_long_horizon_100x/
```

Shape:

```text
systems: 33
future profiles: 3696
workers: 18
horizon grid: 0 through 1024, sparse long-horizon schedule
errors: 0
status: COMPLETED
elapsed: about 381 seconds
```

Implementation changes:

- Added configurable horizon grids and custom horizons to the future-landscape runner.
- Propagated horizon grids through profile, null, and transition-summary code.
- Added horizon-local profile/null outputs, window summaries, saturation onset by family, viscosity diagnostics, and a compact long-horizon status file.

Read:

- Long horizons do not rescue the current substrate.
- Aggregate structured family count remains 0.
- Degree-preserving controls do not pass the aggregate gate.
- Nominal structured/expanding families are saturation dominated.
- The viscosity diagnostic does not support "H16 was simply too short"; transition information generally appears immediately.
- Window-local early/pre-saturation candidates exist, but controls also show window-local candidates, so they are diagnostic only.

Next:

Do not run a longer overnight batch on this exact substrate. Keep the long-horizon machinery as a diagnostic layer, but move next effort toward substrate/environment redesign or stronger window-level controls.

## 2026-05-23 - RFS-MB0 action-generated relation atlas v0 calibration

Implemented the action-generated relation substrate spec:

```text
docs/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md
```

Added:

```text
omega/rfs_mb0_future_landscape/relation_generator.py
omega/rfs_mb0_future_landscape/run_relation_atlas.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_action_generated_relation_atlas_v0_calibration_result.md
```

Primary run:

```text
results/rfs_mb0_relation_atlas/20260523_action_generated_v0_n5_calibration/
```

Shape:

```text
generated environments: 50
middle-regime environments: 28
future profiles: 8250
horizon grid: long_10x
workers: 18
errors: 0
status: COMPLETED
elapsed: about 289 seconds
atlas gate passes: 0
```

Read:

- The neutral relation atlas generator works.
- The generator produces a useful spread of environment classes without named positive families.
- The n=5 calibration found many middle-regime environments.
- No environment passed the aggregate atlas gate.
- Local/window-level structured candidates appear, but do not promote under matched-null discipline.

Operational note:

The initial mixed n5/n6 calibration used 18 workers but drained into long n6 stragglers, leaving lower CPU utilization near the end and hitting the time limit at 49/50 environments. The runner now supports `--coordinate-counts` and `--max-state-count`; the n=5 rerun completed cleanly in about 4.8 minutes.

Next:

Keep the relation atlas branch. Use n=5 batches for fast parameter calibration, then target n=6 only after parameter trends identify stable middle-regime regions. Do not treat local/window candidates as positives until window-level controls and confirmatory splits are in place.

## 2026-05-23 - RFS-MB0 relation atlas 5-hour batch

Ran the staged relation-atlas batch from:

```text
docs/RFS_MB0_RELATION_ATLAS_5H_BATCH_RUN_SPEC.md
```

Added/used:

```text
omega/rfs_mb0_future_landscape/run_relation_atlas_batch.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_relation_atlas_5h_batch_result.md
```

Local summary:

```text
results/rfs_mb0_relation_atlas/5h_batch_summary.md
```

Shape:

```text
wall clock used: about 8367 seconds
generated environments: 1140
middle-regime environments: 674
atlas gate passes: 0
errors: 0 across completed stages
```

Stages:

```text
A: existing trend mining
B: 200 broad n=5 environments, 120 middle-regime
C: 300 targeted fresh-seed n=5 environments, 162 middle-regime
D: 40 targeted n=6 environments, 24 middle-regime
E: 200 window/null stress rows, aggregate gate remains blocker
C2: 600 extra targeted n=5 environments, 368 middle-regime
```

Read:

- The relation atlas now has stable middle-regime parameter trend evidence.
- Stage B suggests out-degree 2 and reversibility fraction 0.25 are especially useful for middle-regime environment shape.
- Targeted fresh-seed n=5 runs reproduced middle-regime environments.
- Limited n=6 transfer also produced middle-regime environments.
- No generated environment passed the aggregate atlas gate.
- Window-level candidates remain diagnostics only.

Next:

Freeze a small environment-shape-selected parameter region and run a confirmatory fresh-seed split. Improve per-null window stress reporting before promoting any window-local candidate.

## 2026-05-23 - RFS-MB0 relation atlas repaired due-diligence batch

Implemented and ran the batch-runner repair spec:

```text
docs/RFS_MB0_RELATION_ATLAS_BATCH_RUNNER_REPAIR_SPEC.md
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_relation_atlas_repaired_batch_result.md
```

Local summary:

```text
results/rfs_mb0_relation_atlas/repaired_batch_summary.md
```

Repairs:

- Added `--parameter-region-mode any|core_only|all`.
- Added requested vs matched parameter/job counts to config and status.
- Added interaction trend mining.
- Added core and broad region files.
- Added per-null window kill table.
- Added localized candidate reproducibility diagnostics.

Run shape:

```text
wall clock used: about 8830 seconds
generated environments: 1040
middle-regime environments: 871
atlas gate passes: 0
errors: 0
```

Stage read:

```text
B broad n=5: 300 environments, 176 middle-regime
C core_only n=5: 660/672 jobs completed before time cutoff, 620 middle-regime
D core_only n=6: 80 environments, 75 middle-regime
E window/null stress: 200 candidate windows, 1200 null-specific rows
```

Null-kill read:

```text
degree_preserving_rewire: 200/200 candidate windows survived
out_degree_preserving_random: 200/200 survived
constraint_shuffled: 56/200 survived
asymmetry_shuffled: 37/200 survived
roughness_resampled: 56/200 survived
frontier_or_probe_marginal: 0/200 survived
```

Interpretation:

- Current window candidates are not merely degree/out-degree artifacts.
- They are still killed by frontier/probe-marginal diagnostics and often by constraint/asymmetry/roughness shuffles.
- Localized reproducibility remains 0 under repaired diagnostics.
- Scientific gate remains not passed.

Next:

Either refine the probe/frontier null if it is too blunt, or treat the current relation-atlas candidate windows as local artifacts and move to a new substrate/detector family. Keep the repaired runner as the standard due-diligence layer.

## 2026-05-25 - RFS-MB0 relation atlas breadth/null-repair smoke

Pulled and implemented the next relation-atlas repair spec:

```text
docs/RFS_MB0_RELATION_ATLAS_BREADTH_AND_NULL_REPAIR_SPEC.md
```

Primary smoke note:

```text
docs/research_notes/validation_results/rfs_mb0_relation_atlas_breadth_null_repair_smoke_result.md
```

Local smoke output:

```text
results/rfs_mb0_relation_atlas/20260525_breadth_null_repair_smoke/
```

Implementation repairs:

- Added the requested batch-runner flags for selection mode, stress sample count, confirmatory region files, held-out switches, null replicates, and perturbation switches.
- Renamed region outputs toward `exploratory_regions.json` and `confirmatory_regions_preregistered.json`.
- Replaced order-biased window stress slicing with stratified selection.
- Added decomposed frontier/probe diagnostic null labels.
- Added explicit output files for stage integrity, window stress selection, frontier/probe null decomposition, null-replicate status, held-out reproducibility, perturbation status, and unique coverage.
- Added a graceful short-budget path so missing source runs produce explicit empty regions instead of a crash.

Tiny smoke:

```text
workers: 6
wall-clock budget: 1200 seconds
wall-clock used: about 200 seconds
total environment evaluations: 12
middle-regime environments: 8
atlas gate passes: 0
candidate windows selected for Stage E: 12
```

Tiny-smoke null read:

```text
degree/out-degree survived: 12/12
constraint/asymmetry/roughness survived: 0/12
frontier_size_only survived: 12/12
probe_marginal_only survived: 12/12
frontier_size_plus_probe_marginal survived: 12/12
signature_support_matched survived: 0/12
horizon/window local frontier matched survived: 12/12
```

Interpretation:

The runner is now good enough for a small-to-medium real breadth/null-repair run. The smoke does not support a theory claim. Its useful result is that the former blunt frontier/probe blocker can now be decomposed; in the tiny sample, signature-support matching was the support-side blocker, not frontier size alone or probe marginals alone.

## 2026-05-25 - RFS-MB0 relation atlas ranked null-repair run

Implemented true null replicate ranking for the relation atlas:

```text
--null-replicates
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_relation_atlas_ranked_null_repair_result.md
```

Local run output:

```text
results/rfs_mb0_relation_atlas/20260525_breadth_null_repair_ranked_real/
```

Run shape:

```text
workers: 18
start_samples: 1
null_replicates: 5
wall-clock budget: 5400 seconds
wall-clock used: about 4915 seconds
total environment evaluations: 146
middle-regime environments: 109
atlas gate passes: 0
```

Stage read:

```text
Stage B broad n=5: 80 environments, 45 middle-regime, 0 gate passes
Stage C core n=5: 66 environments completed before cap, 64 middle-regime, 0 gate passes
Stage D n=6 transfer: skipped/deferred
Stage E window stress: 160 candidate windows, 1760 null-specific rows
```

Ranked null survival:

```text
degree_preserving_rewire: 0/160 survived
out_degree_preserving_random: 2/160 survived
constraint_shuffled: 0/160 survived
asymmetry_shuffled: 0/160 survived
roughness_resampled: 0/160 survived
frontier_size_only: 44/160 survived
probe_marginal_only: 160/160 survived
frontier_size_plus_probe_marginal: 63/160 survived
signature_support_matched: 77/160 survived
horizon_local_frontier_matched: 59/160 survived
window_local_frontier_matched: 62/160 survived
```

Localized reproducibility:

```text
localized candidate groups: 122
localized_reproducible_candidate: 0
```

Interpretation:

The ranked-null pass is stricter than the deterministic null smoke. Probe marginals alone are not the live blocker, but degree/out-degree replicate ranks, constraint/asymmetry/roughness shuffles, support matching, and localized reproducibility remain serious blockers. This branch remains calibration/falsification work, not evidence for a scientific gate pass.

## 2026-05-25 - RFS-MB0 candidate phenotype audit sanity sweep

Pulled and implemented:

```text
docs/RFS_MB0_RELATION_ATLAS_CANDIDATE_PHENOTYPE_AUDIT_SPEC.md
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_candidate_phenotype_audit_sanity_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_candidate_phenotype_audit_sanity/
```

Run shape:

```text
workers: 18
parameter_samples per start pass: 4
start_samples: 1, 3, 8
null_replicates: 1
wall-clock used: about 985 seconds
```

All three start-sample stages completed, each with 4/4 jobs, 4 middle-regime environments, and 0 atlas gate passes.

Candidate phenotype rows:

```text
41
```

Start coverage:

```text
environment_level: 33
basin_local: 6
start_fragile: 1
start_local: 1
```

Current phenotype classification:

```text
roughness_brittle_artifact: 41/41
```

Important technical tension:

```text
top-k near-tie rate: 0.200
roughness decisive selected-edge fraction: 0.114
dominance_class: constraint_dominated
```

Interpretation:

The start-sample audit suggests candidate windows are not mostly one-start accidents. However, the roughness-brittle classification conflicts with the score-term decomposition, which says the sampled edge selection is constraint-dominated and only modestly roughness-decisive. The next technical probe should split roughness into roughness-off replay, same-strength reseeding, strength sweep, and edge-selection flip rate rather than treating `roughness_resampled` as a single binary artifact label.

## 2026-05-25 - RFS-MB0 relation generator phenotype repair

Pulled and implemented:

```text
docs/RFS_MB0_RELATION_GENERATOR_PHENOTYPE_REPAIR_SPEC.md
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_relation_generator_phenotype_repair_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_relation_generator_phenotype_repair/
```

Run shape:

```text
workers requested: 18
parameter_samples per start pass: 8
start_samples: 1, 3, 8
null_replicates: 3
roughness_strengths: 0, 0.001, 0.003, 0.01, 0.03, 0.05
roughness_seed_replicates: 3
wall-clock used: about 3396 seconds
```

Worker-utilization caveat:

```text
Only 8 atlas jobs were available per stage, so the 18-worker executor could not
fully saturate the CPU. Future hardware-saturating runs should queue at least
18 jobs per stage or parallelize roughness replay.
```

All start-sample stages completed, each with 8/8 jobs, 8 middle-regime environments, and 0 atlas gate passes.

Candidate phenotype rows:

```text
88
```

Start coverage:

```text
environment_level: 75
basin_local: 10
start_local: 2
start_fragile: 1
```

Phenotype classes:

```text
constraint_dominated_roughness_sensitive: 62
roughness_edge_brittle_candidate: 25
confirmed_roughness_artifact: 1
```

Roughness strength profile:

```text
noise_tolerant: 69
noise_sensitive_smooth: 9
roughness_strength_brittle: 10
```

Score/term dominance:

```text
constraint_term_dominance: 2.739
asymmetry_term_dominance: 0.056
roughness_term_dominance: 0.005
dominance_class: constraint_dominated
```

Interpretation:

The roughness phenotype repair worked. The previous all-roughness-artifact label was too harsh. Most candidates are roughness-resample sensitive but edge-stable/noise-tolerant and constraint-dominated. The relation generator remains worth keeping for another focused diagnostic pass, preferably path/process-focused and with enough queued jobs to saturate available workers.

## 2026-05-25 - RFS-MB0 path metric calibration smoke

Pulled:

```text
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_SPEC.md
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_ADDENDUM_METRIC_CALIBRATION.md
docs/RFS_MB0_PATH_METRIC_CALIBRATION_SMOKE_TIGHTENING.md
```

Implemented:

```text
omega/rfs_mb0_future_landscape/run_path_metric_calibration.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_path_metric_calibration_smoke_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_path_metric_calibration_smoke/
```

Run shape:

```text
workers requested: 18
jobs queued: 32
jobs completed: 32
candidate rows: 14
matched-control rows: 14
same-environment window controls: 4
path_horizons: 4, 8
sample_paths_per_start: 256
path_null_replicates: 3
promotion_enabled: false
```

Headline:

```text
path_descriptive: 14/14 candidate rows
probe_collision_fakeout: 32 rows
support_ceiling_fakeout: 30 rows
matched_control_also_passes: 2 rows
mean probe_collision_rate: 0.963
```

Interpretation:

The calibration runner works, but the first path metrics are dominated by probe-collision and support-ceiling fakeouts. Candidate rows can beat matched controls and simple endpoint/unigram nulls while still being uninterpretable as path-process structure because the probe alphabet is too coarse. Do not scale this exact path metric setup until higher-resolution probes and low-outdegree/path-count controls are added.

## 2026-05-25 - RFS-MB0 probe resolution calibration smoke

Pulled:

```text
docs/RFS_MB0_PROBE_RESOLUTION_CALIBRATION_SPEC.md
```

Updated:

```text
omega/rfs_mb0_future_landscape/run_path_metric_calibration.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_probe_resolution_calibration_smoke_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_probe_resolution_calibration_smoke/
```

Run shape:

```text
workers requested: 18
jobs queued: 288
jobs completed: 288
errors: 0
candidate environments: 8
path_horizons: 4, 8
sample_paths_per_start: 256
path_null_replicates: 3
promotion_enabled: false
wall_clock_seconds: 5.0
```

Headline:

```text
probe_resolution_fail_collision: 57 candidate rows
probe_resolution_identity_like_only: 47 candidate rows
probe_resolution_pass: 24 candidate rows
probe_resolution_pass_but_control_also_passes: 13 candidate rows
probe_collision_fakeout: 114 rows
support_ceiling_fakeout: 106 rows
matched_control_also_passes: 56 rows
```

Interpretation:

The probe-resolution bottleneck is real. Existing low-resolution probes remain too collision-prone for path-language metrics. Medium-resolution coordinate/composite probes reduce collision enough to keep as calibrated diagnostics, but matched controls still frequently show the same path metrics. Recommendation: branch B, downgrade path-process for now and focus near-term empirical work on support/distribution deformation taxonomy.

## 2026-05-25 - RFS-MB0 support/distribution taxonomy smoke

Pulled:

```text
docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md
```

Added:

```text
omega/rfs_mb0_future_landscape/run_support_distribution_taxonomy.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_support_distribution_taxonomy_smoke_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_support_distribution_taxonomy_smoke/
```

Run shape:

```text
workers requested: 18
jobs requested: 288
jobs completed: 288
metric rows completed: 11088
errors: 0
candidate environments selected: 8
start_samples: 3, 8
horizons: 0, 1, 2, 4, 8, 12, 16
promotion_enabled: false
wall_clock_seconds: 30.5
```

Headline:

```text
matched_control_equivalent: 92 candidate summary rows
probe_collision_limited: 12
support_ceiling_limited: 7
mixed_support_distribution_candidate: 7
support_deformation_candidate: 2
identity_like_control: 4
underdetermined: 4
```

Interpretation:

The support/distribution taxonomy workflow is operational. Most rows are still explained by matched-control equivalence or probe/floor-ceiling limits, but a small set of support and mixed deformation candidates remains. Continue this branch by broadening parameter/regime coverage; keep path metrics as an open thread, not the current driver.

## 2026-05-25 - RFS-MB0 deformation detector upgrade and local sweep

Pulled:

```text
docs/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md
```

Added:

```text
omega/rfs_mb0_future_landscape/run_deformation_detector_sweep.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_deformation_detector_sweep_small_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_small/
```

Validation output:

```text
results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_validation/
```

Small pass shape:

```text
anchors: 12
fresh_seeds_per_variant: 2
start_samples: 3,8
horizons: 0,1,2,4,8,12,16,24
workers requested: 18
sweep jobs completed: 576
sweep rows completed: 25344
errors: 0
wall_clock_seconds: 77.7
promotion_enabled: false
```

Headline:

```text
candidate_stable_region: 3
fakeout_to_candidate_transition: 2
candidate_to_fakeout_transition: 7
saturation_boundary: 10
probe_resolution_boundary: 2
```

Interpretation:

The detector/sweep validation is green. The small scaled pass found local support/distribution transition geometry: candidate anchors are mostly knife-edge at whole-anchor level, but stable local candidate regions and fakeout-to-candidate transitions appear. Recommendation: proceed to a medium-breadth support/distribution atlas concentrated around the observed bands. Path metrics remain parked.

## 2026-05-26 - RFS-MB0 medium-breadth support/distribution atlas 10h

Pulled:

```text
docs/RFS_MB0_MEDIUM_BREADTH_SUPPORT_DISTRIBUTION_ATLAS_10H_SPEC.md
```

Updated:

```text
omega/rfs_mb0_future_landscape/run_deformation_detector_sweep.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_medium_breadth_support_distribution_atlas_10h_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260525_medium_breadth_support_distribution_atlas_10h/
```

Run shape:

```text
workers requested: 18
anchors selected: 16
fresh_seeds_per_variant: 5
start_samples: 3, 8, 16
horizons: 0, 1, 2, 4, 8, 12, 16, 24, 32
sweep jobs requested: 21840
sweep jobs completed: 21840
sweep rows completed: 1769040
rank/effect rows: 39424
errors: 0
wall_clock_seconds: 26700.2
promotion_enabled: false
```

Headline:

```text
near_miss_transition_band: 10
stable_fakeout_band: 6
stable_candidate_band: 0
saturation_boundary: 124
candidate_to_fakeout_transition: 78
probe_resolution_boundary: 6
```

Interpretation:

The 10h atlas was technically clean and used the hardware effectively, but it did not generalize the earlier local-sweep candidate signal into stable candidate bands. The result is a boundary/near-miss map: saturation and probe-resolution boundaries dominate, fakeout structure is recurrent, and candidate retention remains below stable-band thresholds. Limited n=6 transfer was not run by this implementation and remains a follow-up. Recommended next step: second local sweep focused on saturation/probe-resolution boundaries, or a measurement-limits note if we decide the current substrate/probe design is too lossy.

## 2026-05-26 - RFS-MB0 medium-breadth atlas runner repair smoke

Pulled:

```text
docs/RFS_MB0_MEDIUM_BREADTH_ATLAS_RUNNER_REPAIR_SPEC.md
```

Updated:

```text
omega/rfs_mb0_future_landscape/run_deformation_detector_sweep.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb0_medium_breadth_atlas_repair_smoke_result.md
```

Local output:

```text
results/rfs_mb0_relation_atlas/20260526_medium_breadth_atlas_repair_smoke/
```

Run shape:

```text
anchors selected: 6
fresh_seeds_per_variant: 2
start_samples: 3, 8
horizons: 0, 1, 2, 4, 8, 12, 16, 24, 32
workers requested: 18
sweep jobs requested: 720
sweep jobs completed: 720
sweep rows completed: 35640
rank/effect rows: 39424
errors: 0
wall_clock_seconds: 229.5
promotion_enabled: false
```

Headline:

```text
output_manifest.json: present
required_answer_provenance.csv: present
n6_transfer_summary.csv: transfer_status skipped_budget
fakeout_to_candidate_transition_graph_count: 1 / 30
fakeout_to_candidate_band_level_count: 4 / 6
stable_candidate_band: 0
```

Interpretation:

The repair smoke succeeded as a runner/reporting repair. It explicitly resolves fakeout-to-candidate provenance, makes n=6 transfer status unambiguous, and adds band, blocker, saturation, probe-resolution, margin, fresh-seed, and manifest audits. It is not a stronger science result. n=6 transfer was intentionally skipped for this smaller run and should remain a separately budgeted follow-up.

## 2026-05-26 - RFS-MB1 neutral coupled-landscape exploratory smoke

Implemented and ran the first small RFS-MB1 sandbox runner from:

```text
docs/RFS_MB1_NEUTRAL_COUPLED_LANDSCAPE_AUDIT_SPEC.md
```

Updated:

```text
omega/rfs_mb1/run_neutral_coupled_landscape_audit.py
```

Primary result note:

```text
docs/research_notes/validation_results/rfs_mb1_neutral_coupled_landscape_exploratory_smoke_result.md
```

Local output:

```text
results/rfs_mb1_coupled_landscape/20260526_exploratory_smoke/
```

Run shape:

```text
paired landscapes requested: 72
fresh seeds per pair: 1
coupling maps: frontier_signature, constraint_profile, asymmetry_profile
horizons: 4, 8, 16, 24, 32
start_samples: 3
probe_limit: 5
workers requested: 18
jobs requested: 2160
jobs completed: 2160
metric rows: 19440
errors: 0
wall_clock_seconds: 250.3
promotion_enabled: false
```

Headline:

```text
full A->B rows: 2160
mean full A->B deformation: 0.1214
specific non-fakeout full rows: 7
magnitude-only full-row fakeouts: 128
source-structure margin full rows: 44
target-specificity margin full rows: 167
directional imbalance full rows: 499
```

Interpretation:

The neutral coupled-landscape audit is operational and preserves the useful
VAL1-MF counterfactual pattern without reintroducing semantic action verbs.
However, the first smoke does not justify branch promotion. Specific
non-fakeout full A-to-B rows are sparse, and many apparent effects are explained
by magnitude, source-shuffle equivalence, target-shuffle equivalence, probe
collision, or saturation. Keep RFS-MB1 as an exploratory sandbox unless we
explicitly decide to spend a cycle repairing coupling-map specificity and
fresh-seed recurrence.
