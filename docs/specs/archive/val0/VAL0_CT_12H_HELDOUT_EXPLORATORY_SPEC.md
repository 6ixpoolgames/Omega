# VAL0-CT 12-Hour Held-Out Exploratory Probe Spec

Targeted use of a 12-hour wall-clock budget after R1 calibration and brittleness sidecar v1

## Purpose

This spec defines the best next exploratory run under a 12-hour wall-clock budget.

The current project state is:

```text
R1 calibration:
  positive signal in brittle_peak and structured_asymmetric_v2

H16/T32 confirmation:
  strongest current R1/R0-lookahead separation

H16/T64:
  generator-depth collapse boundary for current 64-task generators

brittleness sidecar v1:
  useful negative result; do not scale yet
```

Therefore this run should not scale the brittleness sidecar and should not retest T=64.

The best use of compute is a held-out generator generalization probe:

> Does R1 beat equal-budget R0-lookahead in new generator mechanisms, while low_resolution_dense remains matched?

This is an exploratory generalization run, not a final validation result.

## Main question

The run should answer:

```text
Is the R1 advantage limited to brittle_peak / structured_asymmetric_v2,
or does it survive changed brittle/robust failure mechanisms?
```

The most important anti-overfit target is `unlabeled_structural`, because it reduces direct researcher labeling of brittle vs robust branches.

## Do not scale brittleness sidecar v1

The first brittleness sidecar smoke produced useful negative evidence for the metric:

```text
low_resolution_dense:
  brittleness = 0.000, good control behavior

brittle_peak:
  R1 advantage reproduced
  chosen-brittleness gap slightly negative

structured_asymmetric_v2:
  R1 advantage reproduced
  chosen-brittleness gap slightly negative

correlation with R1 advantage:
  near zero or negative
```

Interpretation:

```text
The current brittleness proxy is not measuring the property that explains R1's advantage.
```

For this 12-hour run:

```text
preferred:
  disable brittleness sidecar entirely

acceptable:
  log brittleness v1 only on a tiny optional subset, clearly marked exploratory

forbidden:
  use brittleness to classify success
  use brittleness to filter runs
  change R1 based on brittleness
```

## Run budget

Recommended wall-clock allocation:

```text
Phase 0:
  30-60 minutes
  generator sanity checks

Phase 1:
  1-2 hours
  small calibration and runtime check

Phase 2:
  8-9 hours
  main held-out exploratory run

Phase 3:
  30-60 minutes
  summary, aggregation, and status note
```

Do not rely on external timeout as the primary stop mechanism. Use runner-owned wall-clock controls and checkpointing.

## Fixed policy and evaluation settings

Freeze the core comparison:

```text
R1:
  primary selector = R1_mean_future_R0
  secondary/tie-break = R1_fraction
  R1_best_future_R0 diagnostic only

R0-lookahead:
  equal candidate set
  equal h/H/sample/max_paths budget
  selects peak future_R0
```

Use the proven informative horizon band:

```text
h:
  1, 2

H:
  16

T:
  32
```

Use existing scale:

```text
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

Do not run T=64 in this probe.

## Generator families

### Primary held-out families

#### unlabeled_structural

Highest priority.

Purpose:

```text
test whether R1 advantage appears in structural regimes that are not explicitly
hand-labeled brittle/robust by the generator
```

Expected:

```text
R1 advantage should appear only in regimes with measured peak-vs-retention tension,
not uniformly across all generated regimes.
```

Do not cut this family first.

#### cost_brittle

Purpose:

```text
test whether R1 survives a brittle mechanism based on escalating cost barriers
rather than direct obstruction geometry
```

Expected:

```text
R0-lookahead overselects high immediate enabling.
R1 preserves more retained reachability if cost barriers create brittle peaks.
```

Include only if cost constraints are implemented meaningfully in R0/R1.

#### delayed_robust

Purpose:

```text
test whether R1 can favor branches whose robust structure appears after delay
rather than immediately
```

Expected:

```text
R1 advantage should be stronger at h = 2 than h = 1.
```

### Required controls

#### low_resolution_dense

Purpose:

```text
negative control where R1/R0-lookahead distinction should blur or collapse
```

Expected:

```text
R1 ≈ R0-lookahead
```

#### lock_in_seeded

Purpose:

```text
confirm destructive-lock-in / local-global divergence diagnostic
```

Expected:

```text
pseudo_omega has low global_LHR, high local_LHR, high pseudo-Omega flag rate
```

### Calibration anchors

Include small anchor samples only.

```text
brittle_peak:
  known positive calibration family

structured_asymmetric_v2:
  known positive calibration family
```

Purpose:

```text
verify previous signal reproduces under the same run harness
```

These are not the primary evidence for generalization.

### Deferred families

Defer unless already implemented cleanly and runtime is obviously under budget:

```text
reliability_brittle:
  only if reliability affects effective reachability meaningfully

decoy_R1:
  only if implementation is clean; otherwise save for a separate adversarial run
```

## Phase 0: generator sanity checks

Before the main run, execute tiny sanity checks for new generators.

Recommended:

```text
families:
  unlabeled_structural
  cost_brittle
  delayed_robust

seeds:
  3-5 per family

h:
  1, 2

H:
  16

T:
  32

policies:
  R1
  R0-lookahead
  random optional
```

Required checks:

```text
unlabeled_structural:
  produces nontrivial candidate variance / regime diversity

cost_brittle:
  cost barriers actually affect retained reachability

delayed_robust:
  robust branch becomes visible after delay
```

If a generator does not produce the intended structural regime, do not include it in Phase 2.

## Phase 1: small calibration and runtime check

Purpose:

```text
confirm known anchors reproduce and estimate runtime before the main batch
```

Suggested grid:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  unlabeled_structural
  cost_brittle
  delayed_robust

seeds:
  10-20 per family

h:
  1, 2

H:
  16

T:
  32

policies:
  random
  R0
  R0-lookahead
  R1
  pseudo_omega only where applicable
```

Proceed if:

```text
old positive anchors reproduce directionally
low_resolution_dense remains matched
unlabeled_structural produces nontrivial regime diversity
runtime projection fits the 12-hour budget
```

If anchors fail unexpectedly, inspect before launching the main run.

## Phase 2: main held-out exploratory run

Primary grid:

```text
families:
  unlabeled_structural
  cost_brittle
  delayed_robust
  low_resolution_dense
  lock_in_seeded
  brittle_peak
  structured_asymmetric_v2

h:
  1, 2

H:
  16

T:
  32

policies:
  random
  R0
  R0-lookahead
  R1
  pseudo_omega
```

Recommended seed counts:

```text
unlabeled_structural:
  150

cost_brittle:
  100

delayed_robust:
  100

low_resolution_dense:
  50

lock_in_seeded:
  50

brittle_peak anchor:
  40

structured_asymmetric_v2 anchor:
  40
```

If runtime is high, cut in this order:

```text
1. lock_in_seeded to 30
2. low_resolution_dense to 30
3. brittle_peak / structured_asymmetric_v2 anchors to 25 each
4. cost_brittle / delayed_robust to 75 each
5. do not cut unlabeled_structural first
```

If runtime is lower than expected, add:

```text
reliability_brittle:
  50-80 seeds, only if reliability is implemented meaningfully

or:
  increase unlabeled_structural seeds before increasing anchors
```

## Required result fields

The run should report existing fields:

```text
generator_family
policy
h
H
T
seed
R0_initial
R0_final
global_LHR
local_LHR
pseudo_omega_flag
same_choice_rate
score_gap
candidate_future_R0_variance
candidate_R1_fraction
local_global_divergence
```

For held-out generators, add if available:

```text
generator_variant
failure_mechanism
parameter_regime
structural_class
peak_retention_gap
terminal_depth_estimate
```

These should be diagnostic fields only. Do not silently filter runs based on them.

## Primary analyses

### 1. Policy means by family

Report:

```text
mean global_LHR for R1
mean global_LHR for R0-lookahead
R1_advantage = R1 - R0-lookahead
```

By:

```text
family
h
```

Do not report only family-averaged results. The h=1 vs h=2 split is important.

### 2. Held-out generalization

Primary question:

```text
Does R1 beat R0-lookahead in cost_brittle, delayed_robust, and/or unlabeled_structural?
```

### 3. Control behavior

Required checks:

```text
low_resolution_dense:
  R1 ≈ R0-lookahead

lock_in_seeded:
  pseudo_omega local/global divergence persists
```

### 4. Regime-specific unlabeled analysis

For `unlabeled_structural`, report by structural class if available:

```text
high peak_retention_gap
flat
collapsed
dense/no-difference
```

Expected:

```text
R1 advantage should appear in high peak_retention_gap regimes,
not uniformly everywhere.
```

## Success criteria

### Minimal useful success

```text
at least one held-out family shows R1 > R0-lookahead,
low_resolution_dense remains matched,
anchors reproduce directionally
```

### Strong success

```text
R1 > R0-lookahead in at least two held-out families,
low_resolution_dense remains matched,
lock_in_seeded retains destructive-lock-in diagnostic
```

### Best success

```text
unlabeled_structural shows R1 advantage specifically in high peak-retention
or high-variance regimes, not globally across every regime
```

This would meaningfully reduce overfit concern.

## Failure and ambiguity criteria

### Clear overfit warning

```text
R1 only wins in brittle_peak / structured_asymmetric_v2 anchors,
and fails in cost_brittle, delayed_robust, and unlabeled_structural
```

Interpretation:

```text
current R1 signal may be overfit to original calibration generator geometry
```

### Ambiguous result

```text
R1 wins in cost_brittle or delayed_robust,
but not in unlabeled_structural
```

Interpretation:

```text
R1 generalizes across researcher-shaped variants,
but not yet beyond explicit design families
```

### Control failure

```text
R1 strongly beats R0-lookahead in low_resolution_dense
```

Interpretation:

```text
possible uncontrolled artifact or metric/policy asymmetry
```

### Lock-in diagnostic failure

```text
pseudo_omega no longer produces local/global divergence in lock_in_seeded
```

Interpretation:

```text
inspect generator or diagnostic changes before trusting run
```

## Compute and workflow requirements

Use the hardened runner:

```text
first-completed collection
streaming results.jsonl
checkpointed aggregate.csv
checkpointed summary.md
status.json
runner-owned wall-clock controls
interleaved job ordering
```

Recommended max runtime:

```text
max_runtime_seconds:
  43200 minus shutdown reserve

shutdown_reserve_seconds:
  900
```

The run should be salvageable if interrupted.

## What not to do

Do not spend this 12-hour budget on:

```text
scaling brittleness sidecar v1
T = 64
multifield coupling
lineage
corridors
R3 / lushness
GPU work
large task counts
full reliability_brittle unless reliability is already meaningful
full decoy_R1 unless implementation is already clean
```

## Final target

This run should determine whether the current VAL0-CT R1 signal is best described as:

```text
positive calibration limited to designed brittle/robust generators
```

or:

```text
initial held-out generator generalization across multiple brittle/robust failure mechanisms
```

The second outcome would be the next major upgrade in project status.
