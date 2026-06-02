# VAL0-CT 12-Hour Unlabeled Geometry Battery Spec

Scaling the reachable-neighborhood geometry signal under a 12-hour wall-clock budget

## Purpose

The reachable-neighborhood geometry smoke passed the minimum bar:

```text
runner:
  completed cleanly

anchors:
  brittle_peak and structured_asymmetric_v2 reproduced R1 advantage

dense control:
  low_resolution_dense remained matched

geometry:
  non-degenerate signal except terminal_depth
```

The smoke also showed that not every geometry metric is useful:

```text
keep:
  depth-profile d16 as anchor sanity diagnostic
  corridor d8 as unlabeled-structural triage signal
  dense control guardrail

revise/drop:
  terminal_depth, because it saturated
  first-pass re-entry overlap, because it did not explain anchors

defer:
  redundancy clustering
  component graph metrics
  GPU
```

This spec uses a 12-hour wall-clock budget to test whether the weak unlabeled-structural geometry signal from the smoke is real.

Core question:

> Does unlabeled_structural contain geometry-classifiable regimes where R1 approaches or beats equal-budget R0-lookahead?

This remains diagnostic/exploratory. Do not change R1, R0-lookahead, policies, or success criteria.

## Current evidence motivating this run

### Held-out exploratory result

The 12-hour held-out exploratory run found:

```text
anchors reproduced:
  brittle_peak:
    R1 0.547 vs R0-lookahead 0.176

  structured_asymmetric_v2:
    R1 0.571 vs R0-lookahead 0.277

controls behaved:
  low_resolution_dense:
    R1 0.534 vs R0-lookahead 0.535

  lock_in_seeded / pseudo_omega:
    global LHR 0.000
    local LHR 22.400
    pseudo-Omega flag 1.000

held-out families did not show broad R1 wins:
  cost_brittle:
    R1 0.576 vs R0-lookahead 0.664

  delayed_robust:
    R1 0.614 vs R0-lookahead 0.740

  unlabeled_structural:
    R1 0.398 vs R0-lookahead 0.440
```

Decision from that run:

```text
Do not claim held-out generator generalization yet.
Focus next on unlabeled structural regimes and post-hoc peak-retention / geometry classification.
```

### Geometry smoke result

The geometry smoke used:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  unlabeled_structural

seeds:
  24 per family

h:
  1, 2

H:
  16

T:
  32

rows:
  192

runtime:
  ~6 minutes
```

It found:

```text
brittle_peak:
  h=1 R1 advantage +0.319
  h=2 R1 advantage +0.555

structured_asymmetric_v2:
  h=1 R1 advantage +0.215
  h=2 R1 advantage +0.473

low_resolution_dense:
  h=1 R1 advantage -0.003
  h=2 R1 advantage +0.002

unlabeled_structural:
  h=1 R1 advantage -0.038
  h=2 R1 advantage +0.034
```

Most useful smoke hook:

```text
corridor d8 gap weakly stratified unlabeled_structural outcomes in the expected direction.
```

Median split in unlabeled rows:

```text
corridor d8 gap:
  low half mean R1 advantage  = -0.037
  high half mean R1 advantage =  0.033
```

This is not a theory result. It is a candidate triage signal that needs scale.

## 3P audit

### Principled

The object is task-space geometry, not generator labels.

This remains constructor-style / constructor-theory-compatible:

```text
task repertoire:
  reachable neighborhood

recoverability:
  ability to remain connected to future task repertoires

corridor:
  a passage through task space preserving future transformations

lock-in:
  local task repertoire persists while disconnecting from broader task space
```

The run asks whether measured reachable-neighborhood geometry predicts R1 advantage.

### Parsimonious

Do not add new theory layers or new policy objectives.

Keep only the metrics the smoke made plausible:

```text
corridor d8 gap
corridor d16 gap
depth-profile d16 gap
candidate_future_R0_variance
same_choice_rate
```

Do not scale terminal_depth or re-entry as explanatory metrics.

### Predictive

Prediction:

```text
If geometry matters, unlabeled_structural rows with stronger corridor d8 / variance / retained-depth geometry should show higher R1 advantage or higher R1 win rate.
```

Control prediction:

```text
low_resolution_dense should remain matched.
```

Anchor prediction:

```text
brittle_peak and structured_asymmetric_v2 should reproduce R1 advantage and depth-profile d16 gap.
```

## Budget allocation

Use the 12-hour wall-clock budget as follows:

```text
Phase 0:
  10-20 minutes
  smoke sanity / implementation check

Phase 1:
  8-9 hours
  large unlabeled_structural geometry-classification run

Phase 2:
  1-2 hours
  anchor/control guardrail batch

Phase 3:
  30-60 minutes
  summary, binning, aggregation
```

Use runner-owned wall-clock controls and checkpointing. Do not rely on external timeout as the primary stop mechanism.

## Fixed settings

Use the established informative band:

```text
h:
  1, 2

H:
  16

T:
  32

num_tasks:
  64

num_constructors:
  2

sample_size:
  256

max_paths:
  512

workers:
  18
```

Do not run T=64 in this battery.

Do not change R1 or R0-lookahead.

## Geometry settings

Recommended first settings:

```text
geometry_samples:
  32

geometry_depths:
  8, 16

corridor_depths:
  8, 16

reentry:
  disabled or logged as exploratory only

terminal_depth:
  disabled unless threshold definition is revised before run
```

If runtime is clearly under budget, increase:

```text
geometry_samples:
  64 for unlabeled_structural only
```

Do not add redundancy clustering or component graph metrics in this battery.

## Phase 0: sanity check

Run a small version first:

```text
families:
  unlabeled_structural
  brittle_peak
  low_resolution_dense

seeds:
  5-10 per family

h:
  1, 2

H:
  16

T:
  32
```

Proceed if:

```text
no errors
geometry fields non-degenerate
low_resolution_dense remains roughly matched
anchors directionally reproduce if included
runtime projection fits 12 hours
```

## Phase 1: main unlabeled structural geometry run

Primary family:

```text
unlabeled_structural
```

Seed target:

```text
800-1500 seeds
```

Choose seed count based on Phase 0 runtime projection.

Suggested default:

```text
unlabeled_structural:
  1200 seeds
```

If runtime is high:

```text
reduce to 800 seeds
```

If runtime is low:

```text
increase to 1500 seeds
or increase geometry_samples from 32 to 64
```

Policies:

```text
R1
R0-lookahead
R0
random
pseudo_omega optional if cheap
```

Required outputs:

```text
R1_advantage
R1_win
same_choice_rate
candidate_future_R0_variance
corridor_d8_gap
corridor_d16_gap
depth_profile_d16_gap
R1_global_LHR
R0lookahead_global_LHR
```

## Phase 2: guardrail batch

Run smaller guardrails:

```text
brittle_peak:
  100 seeds

structured_asymmetric_v2:
  100 seeds

low_resolution_dense:
  100 seeds

optional lock_in_seeded:
  50 seeds
```

Purpose:

```text
brittle_peak / structured_asymmetric_v2:
  confirm anchors still show R1 advantage and d16 depth signal

low_resolution_dense:
  confirm no spurious R1 advantage and no spurious geometry separation

lock_in_seeded:
  confirm destructive-lock-in diagnostic if cheap
```

If runtime is tight, cut in this order:

```text
1. optional lock_in_seeded
2. anchor seeds to 50 each
3. low_resolution_dense to 50
4. do not cut unlabeled_structural first
```

## Required analysis

Do not report only global means.

The purpose is regime discovery inside `unlabeled_structural`.

### Primary binning variables

Bin unlabeled rows by:

```text
corridor_d8_gap quintiles
candidate_future_R0_variance quintiles
depth_profile_d16_gap quintiles
same_choice_rate bins
h = 1 vs h = 2
```

### Primary table

For each bin, report:

```text
bin_label
n
mean_R1_advantage
R1_win_rate
mean_corridor_d8_gap
mean_candidate_variance
mean_depth_profile_d16_gap
mean_same_choice_rate
```

### Interaction table

Report at least one 2D interaction:

```text
corridor_d8_gap quintile × candidate_future_R0_variance quintile
```

For each cell:

```text
n
mean_R1_advantage
R1_win_rate
```

### h split

Always report separately:

```text
h = 1
h = 2
combined
```

The prior signal often differed by h.

## Success criteria

### Minimal useful success

```text
unlabeled_structural produces enough rows for stable bins
controls/anchors behave correctly
corridor_d8 / variance bins produce interpretable stratification
```

### Stronger success

```text
top corridor_d8_gap quintile has higher mean R1 advantage and higher R1 win rate
than bottom corridor_d8_gap quintile
```

### Best success

```text
top corridor_d8_gap + high candidate_variance interaction cell shows positive
mean R1 advantage or materially elevated R1 win rate
```

This would justify a targeted unlabeled regime-classification validation run.

## Failure criteria

### Geometry null

```text
no bin or interaction improves R1 advantage or R1 win rate
```

Interpretation:

```text
current geometry metrics are not finding the recoverable-neighborhood regimes,
or unlabeled_structural does not contain them under current parameters.
```

### Control failure

```text
low_resolution_dense shows strong R1 advantage or large geometry separation
```

Interpretation:

```text
possible geometry artifact or policy asymmetry
```

### Anchor failure

```text
brittle_peak / structured_asymmetric_v2 fail to reproduce
```

Interpretation:

```text
inspect implementation or run configuration before interpreting unlabeled results
```

## Interpretation rules

Pre-register:

```text
Global unlabeled_structural R1 mean may remain weak or negative.
That is not failure if geometry bins reveal coherent sub-regimes.
```

Also:

```text
Positive anchor families do not establish held-out generalization.
They are guardrails only.
```

And:

```text
A positive top-bin signal is not full Omega validation.
It would show that measured reachable-neighborhood geometry can identify
unlabeled regimes where R1 becomes useful.
```

## Compute guardrails

Do not run:

```text
T = 64
new named brittle generators
full re-entry redesign
terminal_depth unless revised
redundancy clustering
component graph metrics
GPU
multifield
lineage
R3 / lushness
large task counts
```

If runtime is high, cut in this order:

```text
1. lock_in_seeded
2. guardrail seed counts
3. geometry_samples from 64 to 32 if raised
4. unlabeled seeds from 1500 to 1200 to 800
5. do not cut h split
6. do not cut R1/R0-lookahead comparison
```

## GPU note

Do not use GPU for this run.

The current geometry sidecar is still CPU-shaped:

```text
sampled rollouts
state copying
Python graph traversal
sets / bitsets
per-seed heterogeneity
```

GPU becomes relevant only after a matrix/bitset backend exists.

## Expected final summary

The final summary should answer:

```text
1. Did the run complete cleanly?
2. Did anchors reproduce?
3. Did low_resolution_dense remain matched?
4. What was global unlabeled_structural R1 advantage?
5. Did corridor_d8_gap quintiles stratify R1 advantage?
6. Did candidate variance quintiles stratify R1 advantage?
7. Did corridor_d8 × variance interaction reveal a positive regime?
8. Did h=1 and h=2 behave differently?
9. Should the next run target a specific geometry-classified unlabeled regime?
```

## Final target

The battery should determine whether the smoke's weak unlabeled geometry hook is real:

```text
corridor_d8 / variance geometry can identify sub-regimes where R1 approaches
or beats greedy peak reachability
```

or whether it was just smoke noise.

If real, the next project status becomes:

```text
R1 calibration remains generator-specific globally,
but geometry-classified unlabeled regimes show recoverable-reachability structure.
```

If not real, revise the geometry diagnostics before further scaling.
