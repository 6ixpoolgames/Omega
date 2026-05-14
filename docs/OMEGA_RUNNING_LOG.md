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

### Probe DA0 Smoke: Distinction / Asymmetry / Relation

Probe DA0 opened a new first-principles branch using tiny discrete stochastic
worlds. It intentionally avoided COM, kappas/fibers, learned representations,
agents, rewards, and path signatures.

Primitive mapping:

- distinction: local alphabet size and persistence of distinguishable symbols;
- asymmetry: directed transition bias/filtering;
- relation: stable or shuffled graph dependence between sites.

Run:

- script: `probe_DA0_distinction_asymmetry_relation.py`
- result directory: `probe_DA0_distinction_asymmetry_relation_results/`
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

- script: `probe_DA0b_relational_connection_closure.py`
- result directory: `probe_DA0b_relational_connection_closure_results/`
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

- script: `probe_DA1_viable_slack_phase_sweep.py`
- result directory: `probe_DA1_viable_slack_phase_sweep_results/`
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

- script: `probe_DA1b_apparent_vs_viable_slack.py`
- result directory: `probe_DA1b_apparent_vs_viable_slack_results/`
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

- script: `probe_DA1c_noncommutative_relational_history.py`
- result directory: `probe_DA1c_noncommutative_relational_history_results/`
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

- script: `probe_DA2_relational_edge_memory_world.py`
- result directory: `probe_DA2_relational_edge_memory_world_results/`
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

- result directory: `probe_DA2_relational_edge_memory_world_revision_results/`
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
- script: `probe_DAX_branching_connection_graph_validity_revised.py`
- result directory:
  `probe_DAX_branching_connection_graph_validity_revised_results/`
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
- script: `probe_DAX_G0_minimal_DAR_rule_space_persistence.py`
- result directory:
  `probe_DAX_G0_minimal_DAR_rule_space_persistence_results/`
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

- script: `probe_DAX_G1_persistence_motif_anatomy_and_robustness.py`
- result directory:
  `probe_DAX_G1_persistence_motif_anatomy_and_robustness_results/`
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

- script: `probe_DAX_G2_persistence_phase_map_minimal_rule_spaces.py`
- result directory:
  `probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results/`
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

- script: `probe_DAX_G2b_control_adjusted_primitive_guardrail.py`
- result directory:
  `probe_DAX_G2b_control_adjusted_primitive_guardrail_results/`
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

- script: `probe_DAX_G3_q3r1_guardrailed_phase_map.py`
- result directory: `probe_DAX_G3_q3r1_guardrailed_phase_map_results/`
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
probe_DAX_G4_q3r1_motif_ecology_mechanism.py
```

Result directory:

```text
probe_DAX_G4_q3r1_motif_ecology_mechanism_results/
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
