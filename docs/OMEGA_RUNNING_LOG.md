# Omega Running Log

This is the living operational log for the Omega validation workspace. Update it
after every meaningful theory-side decision, probe implementation, or compute
run.

## 2026-05-11

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

Probe 12 should formalize the COM fiber transport object:

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
