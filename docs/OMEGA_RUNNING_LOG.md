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
