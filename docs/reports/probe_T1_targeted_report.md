# Probe T1 Targeted Report: Viable Trajectory Geometry

Date: 2026-05-13

Status: completed. This report is a targeted interpretation artifact for the
Omega project record. It should be read alongside the retained machine outputs in
`probe_T1_viable_trajectory_geometry_results/`.

## Executive Decision

Probe T1 does not support scaling the simple trajectory-geometry branch yet.

The result is not a total failure of the trajectory-space idea. It is a useful
negative result for a specific proposed object: effective-rank/collapse-style
geometry over viable trajectory tensors is not sufficient as an Omega-positive
candidate. It is too permissive under false-positive controls and too weak on
component preservation.

Recommended next step:

```text
Do not proceed to T2 substrate scaling yet.
Build a trajectory-geometry failure-mode/component-erasure atlas, or return to
the COM fiber-transport trunk as the stronger current object.
```

## Run Configuration

Script:

- `probe_T1_viable_trajectory_geometry.py`

Result directory:

- `probe_T1_viable_trajectory_geometry_results/`

Scale:

- trajectories per condition/seed: `15000`
- seeds: `180`
- bootstraps: `300`
- workers: `18`
- alphas: `0.45, 0.50, 0.525`
- horizons: `900, 1500, 2400`
- base conditions: coupled, product, shuffled, time-shuffled,
  independent-alpha-0
- false-positive controls: rigid collapse, noise fakeout,
  single-component erasure

Hardware/workflow:

- CPU handled simulation and viability masks.
- GPU handled grouped geometry batches after local trajectory staging.
- GPU usage fraction: `1.0`
- GPU metric batches: `72`
- mean GPU batch time: `0.213s`
- max GPU temperature observed by the script: `52 C`
- thermal throttle events: `0`
- total runtime: `1481.692s`, about `24.7 min`

## Tested Claim

The intended T1 claim was:

```text
Among viable trajectories, the coupled system preserves structured geometric
richness that is not reducible to p_viable, endpoint spread, noise, temporal
disorder, or one-component erasure.
```

T1 operationalized this as:

- lead geometry metrics: effective rank, spectrum entropy, top-eigenvalue
  fraction, distance sketches, collapse score;
- temporal geometry metrics: early/middle/late rank and rank retention;
- component guardrails: A/B rank balance, A/B distance balance, component
  erasure score;
- null deltas against product, shuffled, time-shuffled, and independent-alpha-0;
- false-positive controls for rigid collapse, noise fakeout, and
  single-component erasure.

## Primary Summary

From `summary.json`:

```text
geometry_branch_supported: false
best_geometry_metric: effective_rank
correlation effective_rank vs p_viable_T: 0.271
component_balance_passed: false
temporal_fakeout_passed: false
strongest positive effective-rank null delta: +0.0017
```

The low correlation with `p_viable_T` is important: the geometry metric is not
merely raw survival. But that alone is not enough. The metric fails stricter
controls.

## Key Quantitative Findings

### 1. Coupled Effective Rank Is Not Strong Against Nulls

Coupled effective rank:

```text
min: 1.925
max: 3.148
avg: 2.488
```

Effective-rank deltas for coupled minus null:

```text
vs product:            avg -0.0526, positive in 0/9 cases
vs shuffled:           avg -0.0533, positive in 0/9 cases
vs time_shuffled:      avg -4.4271, positive in 0/9 cases
vs independent_alpha0: avg -0.0490, positive in 1/9 cases
```

The strongest positive effective-rank delta was only:

```text
alpha 0.45, T 900, vs independent_alpha0: +0.0017
```

This is not a robust branch-support signal. The coupled condition is generally
not richer by effective rank than the nulls.

### 2. Noise Fakeout Scores Too High

Noise-fakeout effective rank:

```text
min: 7.735
max: 8.674
avg: 8.203
```

This is much higher than coupled. That means unstructured variance can dominate
the lead metric. Effective rank rewards dimensional spread even when the spread
is not structured viable propagation.

This is a direct failure of the intended claim. A geometry-positive metric
cannot allow noise fakeout to look better than the candidate object.

### 3. Time Shuffling Scores Too High

Time-shuffled effective rank:

```text
min: 5.051
max: 8.564
avg: 6.915
```

Time-shuffled trajectories score far above coupled. This shows that the current
metric family is not sufficiently order-sensitive. It can reward segment
disorder as geometric richness.

This matters because Omega-relevant dynamics should not be just high-dimensional
trajectory variation. The temporal ordering of viable propagation is part of the
candidate object.

### 4. Rigid Collapse Exposes Scale-Invariance

Rigid-collapse effective rank:

```text
min: 1.925
max: 3.148
avg: 2.488
```

Rigid-collapse mean pairwise distance:

```text
min: 0.0367
max: 0.0419
avg: 0.0391
```

Rigid collapse shrinks distances severely but leaves effective rank almost
unchanged. This does not mean rigid collapse is Omega-positive; it means
effective rank is mostly scale-invariant and cannot stand alone.

Distance metrics catch the collapse. Rank metrics do not.

### 5. Component Balance Fails

Coupled component-rank balance:

```text
min: 0.413
max: 0.452
avg: 0.430
```

Coupled component-distance balance:

```text
min: 0.397
max: 0.448
avg: 0.426
```

These are too low for a component-preserving geometry claim. The AB trajectory
space has structure, but that structure is not balanced enough between
components under the current readout.

Single-component erasure was detected correctly:

```text
component_erasure_score avg: 0.987
```

So the guardrail works. It simply rejects the coupled condition under the
current metric definition.

## Interpretation

T1 should be treated as a falsification of this simple branch:

```text
effective-rank/collapse geometry over viable trajectory tensors
```

It should not be treated as a falsification of all trajectory-space approaches.
The failure is specific:

- effective rank is too insensitive to scale collapse;
- effective rank rewards unstructured variance;
- time-shuffled tensors can look richer than ordered trajectories;
- coupled geometry has weak component balance;
- null separation is not stable enough to support a positive claim.

The most constructive reading is:

```text
Trajectory geometry may still matter, but it needs a metric that is
temporal-order-sensitive, component-preserving, and robust to noise fakeout and
rigid collapse.
```

## Impact On Roadmap

Before T1, the T0 recommendation was:

```text
Probe T1: Viable Trajectory Geometry
```

After T1, the trajectory branch should be demoted from candidate object to
diagnostic/failure-mode work.

The stronger current scientific trunk remains:

```text
COM-like multi-step viable propagation through certified fibers
```

T1 strengthens the case for returning to formal COM fiber transport because the
simple quotient-light geometry route did not survive controls.

## Recommended Follow-Up Options

### Option A: Component-Erasure / Failure-Mode Atlas

This is the most direct follow-up if we want to continue trajectory-space work.

Purpose:

- map when rank, distance, entropy, and temporal readouts fail;
- explicitly separate noise richness, rigid collapse, temporal disorder, and
  one-component loss;
- define rejection tests before proposing a new geometry metric.

Candidate additions:

- scale-sensitive spectral metrics;
- temporal-order contrastive metrics;
- component-conditioned geometry;
- distance-normalized rank or rank-normalized distance;
- causal/ordered segment prediction constrained by component balance.

### Option B: Return To COM Fiber Transport

This is the more conservative theory-building move.

Purpose:

- formalize certified viable nodes and transport edges;
- make component projection preservation precise;
- separate object definition from estimator conventions;
- use T1 failure modes as guardrails against future learned or geometric
  proxies.

### Option C: Hybrid

Use T1 as a diagnostic suite for future COM or learned-kappa probes.

In this mode, T1 metrics are not candidate objects. They become tests that a
proposed object must pass:

- no noise-fakeout inflation;
- no rigid-collapse rank illusion;
- no time-shuffle geometry inflation;
- no hidden single-component erasure.

## Files To Inspect

Core retained outputs:

- `probe_T1_viable_trajectory_geometry_results/summary.json`
- `probe_T1_viable_trajectory_geometry_results/geometry_metrics.csv`
- `probe_T1_viable_trajectory_geometry_results/null_deltas.csv`
- `probe_T1_viable_trajectory_geometry_results/component_balance.csv`
- `probe_T1_viable_trajectory_geometry_results/temporal_geometry.csv`
- `probe_T1_viable_trajectory_geometry_results/gpu_timing_diagnostics.csv`

Useful plots:

- `probe_T1_viable_trajectory_geometry_results/effective_rank_by_condition.png`
- `probe_T1_viable_trajectory_geometry_results/component_balance_by_condition.png`
- `probe_T1_viable_trajectory_geometry_results/null_delta_forest_plot.png`
- `probe_T1_viable_trajectory_geometry_results/metric_correlation_matrix.png`

Local-only untracked intermediates:

- `probe_T1_viable_trajectory_geometry_results/_seed_manifest.csv`
- `probe_T1_viable_trajectory_geometry_results/_trajectory_samples/`

Those intermediates are intentionally not tracked because they are generated
workflow artifacts, not public-facing evidence.

## Bottom Line

T1 was worth running because it prevented a premature positive claim. The GPU
workflow is now strong enough to run large falsification probes quickly, and the
result shows the project is still behaving scientifically: the branch selected
by T0 was tested, failed important controls, and should be narrowed or demoted.

Current recommendation:

```text
Do not claim viable trajectory geometry as the object.
Use T1 as a guardrail and either build a failure-mode atlas or return to COM
fiber-transport formalization.
```
