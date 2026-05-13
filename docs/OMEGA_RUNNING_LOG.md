# Omega Running Log

This is the living operational log for the Omega validation workspace. Update it
after every meaningful theory-side decision, probe implementation, or compute
run.

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

- `probe_09_robust_fiber_reachability.py`

Primary output:

- `probe_09_robust_fiber_reachability_results/summary.json`
- `probe_09_robust_fiber_reachability_results/viable_propagation_summary.csv`

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

- `probe_10_com_viable_propagation_robustness.py`

Primary outputs:

- `probe_10_com_viable_propagation_robustness_extended_results/summary.json`
- `probe_10_com_targeted_fragility_refinement_results/summary.json`

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

- `probe_11_learned_predictive_kappa_revised.py`

Primary outputs:

- `probe_11_learned_predictive_kappa_revised_results/summary.json`
- `probe_11_learned_predictive_kappa_revised_results/learned_kappa_validation_loss.csv`
- `probe_11_learned_predictive_kappa_revised_results/learned_kappa_test_propagation.csv`
- `probe_11_learned_predictive_kappa_revised_results/learned_vs_com_comparison.csv`
- `probe_11_learned_predictive_kappa_revised_results/learned_label_anatomy.csv`

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

- `probe_12_batch_com_audit_learned_diagnosis.py`

Primary outputs:

- `probe_12_batch_results/batch_summary.json`
- `probe_12_batch_results/recommended_next_step.md`
- `probe_12a_com_formal_object_audit_results/summary.json`
- `probe_12b_learned_kappa_failure_diagnosis_results/summary.json`
- `probe_12c_improved_learner_smoke_results/summary.json`

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

- `omega_env.bat`
- `omega_env.ps1`

Verification:

```text
cupy arange/sum executed on NVIDIA GeForce RTX 4070 Ti
```

PowerShell note:

- direct `.\omega_env.ps1` may be blocked by Windows execution policy;
- use `powershell -ExecutionPolicy Bypass -File omega_env.ps1` or use
  `omega_env.bat`.

### CPU/GPU Concurrent Stress Probe

Added and ran:

- `gpu_cpu_concurrent_stress_probe.py`

Purpose:

- validate that the workflow can run CPU NumPy work and GPU CuPy work at the
  same time;
- measure rough sustained dense-array throughput for future probe planning.

Run:

- duration: `180s`
- CPU workload: NumPy matrix multiply, size `1400`
- GPU workload: CuPy matrix multiply, size `4096`
- environment: `omega_env.bat`

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

- script: `probe_T0_trajectory_space_branch_triage.py`
- result directory: `probe_T0_trajectory_space_branch_triage_results/`
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

- script: `probe_T1_viable_trajectory_geometry.py`
- result directory: `probe_T1_viable_trajectory_geometry_results/`
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

- script: `probe_T1F_ordered_trajectory_structure_atlas.py`
- result directory: `probe_T1F_ordered_trajectory_structure_atlas_results/`
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

- script: `probe_I0_invariant_stack_audit.py`
- result directory: `probe_I0_invariant_stack_audit_results/`
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

- script: `probe_I0b_invariant_threshold_dropout_audit.py`
- result directory: `probe_I0b_invariant_threshold_dropout_audit_results/`
- reused `probe_I0_invariant_stack_audit_results/estimator_report.csv`
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

- script: `probe_13b_fiber_transport_false_positive_refinement.py`
- result directory: `probe_13b_fiber_transport_false_positive_refinement_results/`
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
