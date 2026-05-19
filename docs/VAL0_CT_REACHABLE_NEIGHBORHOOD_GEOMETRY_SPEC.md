# VAL0-CT Reachable-Neighborhood Geometry Probe Spec

Geometry-native recoverability diagnostics for constructor-style task space

## Purpose

Recent VAL0-CT work established three useful facts:

```text
1. R1 calibration is reproducible in designed brittle/robust anchor families.
2. The current R1 selector does not yet show broad held-out generator generalization.
3. The first brittleness sidecar was a useful negative result: it kept dense controls clean,
   but did not explain R1's advantage.
```

The next probe should therefore stop treating generator labels or brittleness proxies as the main object.

The object of interest is the geometry of reachable task space.

This spec defines a small, CPU-first diagnostic sidecar for measuring the reachable-neighborhood geometry around selected candidate states.

Core question:

> Do R1-selected paths enter reachable neighborhoods with better depth, width, redundancy, and re-entry structure than equal-budget R0-lookahead-selected paths?

This is a diagnostic probe only. It should not change R1, R0-lookahead, policies, or success criteria.

## Context from prior results

### Positive calibration

R1 remains strongly positive in the designed calibration families:

```text
brittle_peak:
  R1 > R0-lookahead

structured_asymmetric_v2:
  R1 > R0-lookahead
```

The strongest prior confirmation band was:

```text
h = 1, 2
H = 16
T = 32
```

### Held-out limitation

The 12-hour held-out exploratory run reproduced anchors and controls but did not show broad R1 wins in the held-out families:

```text
cost_brittle:
  R1 < R0-lookahead

delayed_robust:
  R1 < R0-lookahead

unlabeled_structural:
  R1 < R0-lookahead
```

Decision from that run:

```text
Do not claim held-out generator generalization yet.
Focus next on unlabeled structural regimes and measured task-space structure.
```

### Brittleness sidecar v1 limitation

The first brittleness sidecar defined brittleness as perturbation-sensitive structured reachability and implemented enabled-drop / obstruction-add / horizon-extension stresses.

It produced a useful negative result:

```text
low_resolution_dense:
  brittleness = 0.000, good control behavior

brittle_peak and structured_asymmetric_v2:
  R1 advantage reproduced
  chosen-brittleness gap slightly negative
  brittleness/R1-advantage correlation near zero or negative
```

Decision:

```text
Do not scale brittleness sidecar v1.
Do not use it to classify held-out regimes.
```

This geometry probe is a replacement direction, not an extension of the failed brittleness proxy.

## 3P audit

### Principled

Constructor-style task space is naturally about possible transformations and task repertoires.

A scalar reachability count is only a projection of that structure. A geometry probe asks about the shape of the reachable transformation region:

```text
is it deep or shallow?
wide or narrow?
connected or fragmented?
redundant or single-ridge?
re-enterable after perturbation or cliff-like?
```

This is more native to the task-space object than named generator labels.

Primitive grounding:

```text
distinction:
  candidate futures differ

asymmetry:
  paths and perturbations have unequal downstream consequences

relation:
  reachable neighborhoods preserve or fail to preserve causal continuation structure

recoverability:
  perturbed or adjacent states can re-enter future-bearing task regions
```

### Parsimonious

Do not build a full topology engine.

The minimal object is:

```text
reachable neighborhood around a candidate state
```

The first probe measures only:

```text
depth profile
terminal depth
corridor width
path redundancy
re-entry overlap
component fraction
```

These should be reported separately. Do not collapse them into a single Omega score.

### Predictive

The predictive claim is:

```text
R1 advantage should appear when R1-selected paths enter better reachable-neighborhood geometry than R0-lookahead-selected paths.
```

Expected geometry gap:

```text
R1-selected neighborhoods:
  deeper retained profiles
  wider continuation corridors
  more redundant paths
  better re-entry after perturbation
  less terminal-depth collapse

R0-lookahead-selected neighborhoods:
  higher peak reachability may occur, but with narrower or more terminal geometry
```

Control expectation:

```text
low_resolution_dense:
  R1 and R0-lookahead geometry should be similar
```

Unlabeled expectation:

```text
unlabeled_structural:
  geometry should identify sub-regimes where R1 approaches or beats R0-lookahead,
  if such regimes exist at all.
```

## Constructor-theory compatibility

This remains constructor-style / constructor-theory-compatible.

Constructor-native translation:

```text
task repertoire:
  reachable neighborhood

constructor viability:
  ability to keep accessing task repertoires over time

recoverability:
  ability to re-enter or remain connected to future task repertoires after disturbance

corridor:
  a connected passage through task space preserving future transformations

lock-in:
  local task repertoire persists while disconnecting from broader task space
```

The probe studies the structure of possible task repertoires, not a hand-labeled agent variable.

## Keep policies frozen

Do not change:

```text
R1 selector:
  primary = R1_mean_future_R0
  secondary/tie-break = R1_fraction
  R1_best_future_R0 diagnostic only

R0-lookahead:
  equal candidate set
  equal h/H/sample/max_paths budget
  selects peak future_R0

policy set:
  random
  R0
  R0-lookahead
  R1
  pseudo_omega where applicable
```

This geometry sidecar is explanatory and diagnostic only.

## Core definitions

### Reachable neighborhood

For a state `A`, define:

```text
N_H(A):
  sampled set of task states / signatures reachable from A within horizon H
```

This can be approximated by rollout sampling rather than exhaustive enumeration.

### Candidate state

For candidate path `p` from state `A`:

```text
A_p = apply_path(A, p)
```

The geometry sidecar computes the reachable-neighborhood diagnostics around `A_p`.

### Geometry gap

For a diagnostic `G`:

```text
geometry_gap_G = G(R1_chosen_state) - G(R0lookahead_chosen_state)
```

Compare geometry gaps against:

```text
R1_advantage = R1_global_LHR - R0lookahead_global_LHR
```

## Minimal geometry diagnostics

### 1. Depth profile

Measure reachability across multiple depths:

```text
depth_profile(A):
  R0(A, 1), R0(A, 2), R0(A, 4), R0(A, 8), R0(A, 16)
```

Purpose:

```text
detect whether reachable structure decays slowly or collapses quickly
```

Derived fields:

```text
depth_profile_d1
depth_profile_d2
depth_profile_d4
depth_profile_d8
depth_profile_d16
```

### 2. Terminal depth estimate

Approximate the last depth where reachability remains above a threshold.

Example:

```text
terminal_depth(A) = max d such that R0(A, d) >= theta_depth * R0(A, 1)
```

Recommended initial threshold:

```text
theta_depth = 0.25
```

Use sensitivity later; do not tune during the first smoke.

### 3. Corridor width

Estimate how many distinct viable continuations remain at each depth.

Operational approximation:

```text
sample rollout prefixes to depth d
count distinct prefixes/signatures whose future_R0 >= theta_corridor * base_R0
```

Recommended initial threshold:

```text
theta_corridor = 0.50
```

Fields:

```text
corridor_width_d1
corridor_width_d2
corridor_width_d4
corridor_width_d8
corridor_width_d16
```

Purpose:

```text
wide corridor:
  many continuation routes preserve reachability

narrow corridor:
  only one/few ridges preserve reachability
```

### 4. Path redundancy

Estimate how many distinct paths lead to overlapping future task repertoires.

First-pass approximation:

```text
for sampled terminal signatures at depth d:
  group by reachable-task bitset similarity
  count average number of distinct prefixes per cluster
```

Simpler smoke fallback:

```text
redundancy_score = mean number of sampled prefixes reaching equivalent or high-overlap reachable sets
```

Purpose:

```text
recoverable regions should have alternative routes, not one fragile path.
```

### 5. Re-entry overlap

Perturb a candidate state and ask whether the perturbed state can reconnect to the same reachable future region.

```text
reentry_score =
  overlap(N_H(A_p), N_H(perturb(A_p))) / max(1, size(N_H(A_p)))
```

Use coarse signatures for overlap:

```text
enabled task bitset
reachable task bitset at h_eval
completed family counts if available
```

Recommended perturbations for smoke:

```text
enabled_drop:
  remove one enabled or reachable task

obstruction_add:
  add one obstruction into the downstream reachable set
```

Do not reuse the failed brittleness v1 score. This is a re-entry / overlap diagnostic, not a scalar brittleness score.

### 6. Component fraction

Build a sampled graph over reachable signatures:

```text
nodes:
  sampled reachable state signatures

edges:
  one-step task transitions observed during rollout sampling
```

Compute:

```text
giant_component_fraction = largest_component_size / total_sampled_nodes
component_count
component_entropy optional
```

Purpose:

```text
fragmented/noise-like future space:
  many small components

recoverable neighborhood:
  larger connected component with multiple routes

lock-in:
  may show local component strength but poor global continuation
```

## Implementation shape

Add:

```text
omega/val0_ct/geometry.py
omega/val0_ct/run_geometry_smoke.py
```

Do not modify policy selection files except to expose chosen candidate states/paths if needed.

The geometry sidecar should run after policy choice, not inside policy selection.

## Candidate states to analyze

Do not compute geometry for all 256 candidates in the smoke.

Analyze only:

```text
R1_chosen_state
R0lookahead_chosen_state
random_chosen_state
R0_chosen_state optional
pseudo_omega_chosen_state optional where applicable
```

Optional later:

```text
top_k_R0lookahead candidates
top_k_R1 candidates
```

But not in the first smoke unless runtime is trivial.

## Smoke run design

### Scope

```text
families:
  brittle_peak
  structured_asymmetric_v2
  unlabeled_structural
  low_resolution_dense

optional:
  lock_in_seeded

seeds:
  10-20 per family

h:
  1, 2

H:
  16

T:
  32

sample_size:
  256

max_paths:
  512

workers:
  18
```

### Geometry settings

```text
geometry_depths:
  1, 2, 4, 8, 16

rollout_samples_per_candidate_state:
  64 first smoke
  128 confirmation if runtime is fine

reentry_perturbations:
  enabled_drop
  obstruction_add

reentry_samples:
  4 per candidate state

signature:
  enabled bitset
  reachable bitset at h_eval
  optionally completed family counts
```

Keep this CPU-first.

## GPU note

Do not use GPU for this smoke.

Reason:

```text
the current implementation is likely irregular Python graph traversal,
state copying, sampled rollouts, sets/bitsets, and per-seed heterogeneity.
```

GPU may become useful later if the task algebra is rewritten as batched bitset/matrix propagation:

```text
enabled / obstructed / completed:
  boolean vectors

enable / obstruct relations:
  adjacency matrices or sparse tensors

R0 propagation:
  batched masked frontier expansion

neighborhood sampling:
  many candidate states evaluated in parallel
```

Near-term optimization path:

```text
1. CPU geometry smoke
2. profile runtime
3. add bitset representation if needed
4. vectorize R0/depth-profile computation
5. consider GPU only after matrix/bitset backend exists
```

## Required result fields

Per family / policy / h aggregate fields:

```text
mean_global_LHR
mean_R1_advantage
same_choice_rate
candidate_future_R0_variance
```

Geometry fields for each selected policy state:

```text
R1_depth_profile_d1
R1_depth_profile_d2
R1_depth_profile_d4
R1_depth_profile_d8
R1_depth_profile_d16
R1_terminal_depth
R1_corridor_width_d1
R1_corridor_width_d2
R1_corridor_width_d4
R1_corridor_width_d8
R1_corridor_width_d16
R1_reentry_score
R1_redundancy_score
R1_giant_component_fraction
R1_component_count

R0lookahead_depth_profile_d1
R0lookahead_depth_profile_d2
R0lookahead_depth_profile_d4
R0lookahead_depth_profile_d8
R0lookahead_depth_profile_d16
R0lookahead_terminal_depth
R0lookahead_corridor_width_d1
R0lookahead_corridor_width_d2
R0lookahead_corridor_width_d4
R0lookahead_corridor_width_d8
R0lookahead_corridor_width_d16
R0lookahead_reentry_score
R0lookahead_redundancy_score
R0lookahead_giant_component_fraction
R0lookahead_component_count
```

Derived gap fields:

```text
geometry_gap_terminal_depth
geometry_gap_reentry_score
geometry_gap_redundancy_score
geometry_gap_giant_component_fraction
geometry_gap_corridor_width_d8
geometry_gap_corridor_width_d16
geometry_gap_depth_profile_d16
```

Optional correlation fields:

```text
corr_geometry_gap_R1_advantage
corr_reentry_gap_R1_advantage
corr_terminal_depth_gap_R1_advantage
corr_corridor_width_gap_R1_advantage
```

## Analysis plan

### 1. Anchor sanity

Check known anchors:

```text
brittle_peak:
  R1 should still beat R0-lookahead on global LHR
  R1 should show better geometry than R0-lookahead if the geometry diagnostics are coherent

structured_asymmetric_v2:
  same expectation, possibly weaker
```

### 2. Dense control

Check:

```text
low_resolution_dense:
  R1 ≈ R0-lookahead on global LHR
  R1 geometry ≈ R0-lookahead geometry
```

If geometry strongly separates in dense control, inspect for artifact.

### 3. Unlabeled structural regime discovery

For `unlabeled_structural`, do not expect global R1 win.

Instead ask:

```text
Do geometry gaps identify sub-regimes where R1 advantage approaches or exceeds zero?
```

Report bins by:

```text
terminal_depth_gap
reentry_gap
corridor_width_gap
candidate_future_R0_variance
```

### 4. Predictive relationship

Main exploratory relationship:

```text
R1_advantage ~ geometry_gap
```

Expected:

```text
positive anchors:
  geometry gap should align with R1 advantage

low_resolution_dense:
  geometry gap should be small

unlabeled_structural:
  high geometry-gap bins should move R1 toward parity or positive advantage
```

## Success criteria

### Minimal useful success

```text
geometry diagnostics produce coherent non-degenerate values
anchors reproduce R1 advantage
low_resolution_dense remains matched
```

### Stronger success

```text
R1-selected states show better reachable-neighborhood geometry than R0-lookahead
in brittle_peak and structured_asymmetric_v2.
```

### Best success

```text
In unlabeled_structural, geometry-gap bins identify regimes where R1 advantage
approaches or exceeds zero, even if global unlabeled mean remains negative.
```

This would justify a larger unlabeled regime-classification run.

## Failure criteria

### Metric failure

```text
geometry diagnostics are degenerate or nearly identical across all families
```

Interpretation:

```text
implementation is not resolving neighborhood structure.
```

### Control failure

```text
low_resolution_dense shows large geometry gaps unrelated to LHR
```

Interpretation:

```text
geometry diagnostics may be density artifacts.
```

### Anchor failure

```text
anchors reproduce R1 advantage but geometry does not distinguish R1 from R0-lookahead
```

Interpretation:

```text
current geometry diagnostics do not explain the known R1 signal.
```

This is analogous to the brittleness sidecar v1 failure.

### Unlabeled null

```text
unlabeled_structural shows no relationship between geometry gaps and R1 advantage
```

Interpretation:

```text
unlabeled generator may not contain recoverable-neighborhood regimes,
or diagnostics are still missing the relevant structure.
```

## Compute guardrails

Do not enumerate full neighborhoods.

Do not compute geometry for all candidate paths.

Do not run T = 64.

Do not run large task counts.

Do not add multifield, lineage, corridors, or R3/lushness yet.

If runtime is high, cut in this order:

```text
1. optional lock_in_seeded
2. rollout_samples_per_candidate_state from 128 to 64
3. seeds from 20 to 10
4. random/R0 geometry diagnostics
5. do not cut R1 vs R0lookahead geometry comparison
```

## Next decision after smoke

If coherent:

```text
run a larger unlabeled_structural regime-classification probe using geometry bins
```

If not coherent:

```text
record geometry sidecar v1 as negative/insufficient and revise diagnostics
```

Do not modify R1 until the geometry diagnostics either explain or fail to explain the existing calibration signal.

## Final target

The geometry probe should move the project from:

```text
R1 wins in named brittle/robust generators
```

toward:

```text
R1 selects better recoverable reachable-neighborhood geometry,
and that geometry predicts when R1 should outperform greedy peak reachability.
```

That is the constructor-native form of recoverability detection for VAL0-CT.
