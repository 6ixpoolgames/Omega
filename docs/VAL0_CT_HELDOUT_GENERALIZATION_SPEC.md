# VAL0-CT Held-Out Generator Generalization Spec

Next validation run after the R1 calibration result

## Purpose

The current VAL0-CT result is a positive calibration signal:

> R1 robust future-preserving reachability can outperform equal-budget R0-lookahead greedy peak reachability in generated brittle/robust task algebras.

But the result is still vulnerable to generator overfit. The positive families, especially `brittle_peak`, are deliberately shaped around the distinction R1 is meant to detect.

This spec defines the next validation step:

> Freeze the R1 selector and test whether the signal survives held-out generator variation.

This is not a full Omega validation run. It is a generalization test for the current VAL0-CT proto-Omega predictor.

## Current result being extended

The strongest current calibration result is:

```text
H = 16
T = 32
h = 1, 2
```

Policy means:

```text
brittle_peak:
  R1 = 0.539
  R0-lookahead = 0.189

structured_asymmetric_v2:
  R1 = 0.577
  R0-lookahead = 0.289

low_resolution_dense:
  R1 = 0.534
  R0-lookahead = 0.535
```

Band-level read:

```text
brittle_peak, h = 1:
  R1 = 0.360
  R0-lookahead = 0.190

brittle_peak, h = 2:
  R1 = 0.719
  R0-lookahead = 0.188

structured_asymmetric_v2, h = 1:
  R1 = 0.412
  R0-lookahead = 0.313

structured_asymmetric_v2, h = 2:
  R1 = 0.742
  R0-lookahead = 0.265
```

Boundary result:

```text
H = 16, T = 64:
  global LHR collapsed to zero across current 64-task generators
```

Interpretation:

```text
H = 16, T = 32 is currently informative.
T = 64 requires deeper generators or larger task algebras.
```

## Core risk

The core overfit risk is:

```text
The generator may encode exactly the brittle/robust geometry that R1 was designed to exploit.
```

The current result is stronger than a hand-built sanity check, but still not enough for a generalization claim because the generator families were designed after identifying the needed separation geometry.

This run should therefore test variants where the same abstract prediction holds, but the concrete failure mechanism differs.

## Frozen objects

Before running held-out variants, freeze the following:

```text
R1 selector:
  primary = R1_mean_future_R0
  tie-break / secondary = R1_fraction
  R1_best_future_R0 remains diagnostic only

R0-lookahead baseline:
  equal candidate set
  equal h/H/sample budget
  selects peak future_R0

policies:
  random
  R0
  R0-lookahead
  R1
  pseudo_omega where applicable

diagnostics:
  same-choice rate
  score gap
  candidate future_R0 variance
  global_LHR
  local_LHR
  local/global divergence
  pseudo-Omega flag rate

primary horizon band:
  h = 1, 2
  H = 16
  T = 32

controls:
  low_resolution_dense
  lock_in_seeded
```

No selector changes should be made after seeing held-out results unless the run is explicitly demoted to calibration.

## Primary hypothesis

Held-out generalization hypothesis:

> Across held-out brittle/robust generator variants, R1 should outperform equal-budget R0-lookahead on global LHR specifically in regimes where peak reachability is brittle and robust retention structure exists.

Negative control expectation:

> In low-resolution dense controls, R1 and R0-lookahead should remain effectively matched.

Destructive-lock-in expectation:

> In lock-in controls, pseudo_omega should preserve or increase local reachability while degrading global reachability.

## Generator families

### Calibration anchors

Retain a small calibration anchor set for continuity, but do not let it dominate the run.

```text
brittle_peak:
  known positive calibration family

structured_asymmetric_v2:
  known positive calibration family

low_resolution_dense:
  expected R1/R0-lookahead collapse control

lock_in_seeded:
  destructive-lock-in diagnostic control
```

These are not the main evidence for generalization. They confirm the harness and previous result still reproduce.

### Held-out family 1: cost_brittle

Failure mechanism:

```text
brittle paths open many reachable tasks but impose escalating cost barriers.
```

Structure:

```text
brittle branch:
  high immediate enabling
  increasing path cost
  many future tasks become cost-inaccessible

robust branch:
  moderate enabling
  lower cumulative cost
  fewer peak options but higher retained access
```

Expected:

```text
R0-lookahead overselects high immediate enabling.
R1 favors lower-cost robust branch.
R1 global_LHR > R0-lookahead in nontrivial bands.
```

### Held-out family 2: reliability_brittle

Failure mechanism:

```text
brittle paths open many tasks whose reliability decays downstream.
```

Structure:

```text
brittle branch:
  high immediate future_R0
  downstream reliability decay
  low effective retained reachability

robust branch:
  lower peak future_R0
  stable reliability
  higher retained reachability
```

Expected:

```text
R1 advantage appears when reliability_min or reliability weighting is active.
```

If the current implementation does not yet use reliability strongly, this family should either be deferred or implemented as explicit reliability-weighted reachability.

### Held-out family 3: delayed_robust

Failure mechanism:

```text
robust paths do not look best immediately but unlock durable structure after a delay.
```

Structure:

```text
brittle branch:
  high near-term enabling
  shallow terminal depth

robust branch:
  lower near-term enabling
  delayed enabling at depth 2-3
  durable downstream plateau
```

Expected:

```text
R1 should benefit at h = 2 more than h = 1.
R0-lookahead should struggle if the peak path is shallow but attractive.
```

### Held-out family 4: unlabeled_structural

Failure mechanism:

```text
no explicit brittle/robust labels; structure emerges from sampled enable/obstruct/cost parameters.
```

Structure:

```text
sample task graph with parameter regimes:
  enabling density
  obstruction density
  cost profile
  depth profile
  branch variance

classify regimes only after generation by measured structure:
  high peak / low retention
  moderate peak / high retention
  flat
  collapsed
```

Expected:

```text
R1 advantage should appear only in empirically identified high-variance brittle/robust regimes.
R1 should not dominate globally across all regimes.
```

This is the most important held-out family because it reduces direct researcher labeling of the desired structure.

### Held-out family 5: decoy_R1

Adversarial control.

Failure mechanism:

```text
structure appears R1-positive over H but fails the held-out rollout outcome.
```

Structure:

```text
candidate paths maintain R0 over the continuation horizon H
but collapse just beyond H or under rollout dynamics
```

Expected:

```text
R1 should not be claimed successful if it overselects decoys and loses LHR.
```

Purpose:

```text
test whether R1 is merely gaming the chosen H horizon.
```

This is an adversarial control. A failure here does not automatically invalidate R1, but it exposes horizon-Goodhart risk.

## Deep generator extension for T = 64

The H16/T64 boundary run showed all global LHR collapsing to zero in current 64-task generators.

Do not retest T = 64 without deeper generators.

A T64-ready generator should increase:

```text
num_tasks:
  128 or 256

branching_propagation_depth:
  enough nonterminal depth for T = 64

robust plateau length:
  at least 64-step survival for some policies

terminal sink density:
  bounded so all policies do not collapse trivially
```

Recommended status for this spec:

```text
T = 64 is optional confirmation only.
Primary generalization test remains H = 16, T = 32.
```

## Run design

### Phase 0: implementation sanity

Before the main run, execute tiny sanity tests for each new generator.

Required checks:

```text
cost_brittle:
  cost barriers actually reduce reachable futures

reliability_brittle:
  reliability decay affects effective reachability

delayed_robust:
  robust branch becomes visible after delay

unlabeled_structural:
  generated regimes include nontrivial high-variance cases

decoy_R1:
  R1-looking paths can fail held-out LHR
```

If any generator does not produce the intended structural regime, do not include it in the main run.

### Phase 1: small calibration check

Purpose:

```text
confirm old result still reproduces and new generators are not broken
```

Suggested grid:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense
  cost_brittle
  delayed_robust
  unlabeled_structural

seeds:
  20 per family

h:
  1, 2

H:
  16

T:
  32
```

Proceed only if:

```text
known positive anchors still show R1 > R0-lookahead
low_resolution_dense remains matched
at least one held-out family shows nontrivial candidate variance
```

### Phase 2: main held-out run

Primary grid:

```text
families:
  cost_brittle
  delayed_robust
  unlabeled_structural
  low_resolution_dense
  lock_in_seeded

optional if implementation-ready:
  reliability_brittle
  decoy_R1

calibration anchors, reduced:
  brittle_peak
  structured_asymmetric_v2

num_tasks:
  64

num_constructors:
  2

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

Recommended seed counts:

```text
cost_brittle:
  100

delayed_robust:
  100

unlabeled_structural:
  150

low_resolution_dense:
  50

lock_in_seeded:
  50

brittle_peak calibration anchor:
  40

structured_asymmetric_v2 calibration anchor:
  40

reliability_brittle, if included:
  80

decoy_R1, if included:
  80
```

### Phase 3: optional deeper confirmation

Only run if Phase 2 succeeds and runtime allows.

Purpose:

```text
retest whether T = 64 becomes informative in deeper generators
```

Grid:

```text
families:
  delayed_robust_deep
  cost_brittle_deep
  unlabeled_structural_deep

num_tasks:
  128

h:
  1, 2

H:
  16

T:
  64

seeds:
  30-50 per family
```

Success condition:

```text
not all policies collapse to global_LHR = 0
```

If all collapse, record as deeper-generator boundary and stop.

## Required diagnostics

In addition to existing diagnostics, report:

```text
generator_variant
failure_mechanism
parameter_regime
structural_class
peak_retention_gap
cost_barrier_score
reliability_decay_score
delay_depth
terminal_depth_estimate
```

Definitions:

```text
peak_retention_gap:
  max future_R0 - mean future_R0 over candidate continuations

cost_barrier_score:
  difference between raw reachable tasks and cost-accessible reachable tasks

reliability_decay_score:
  difference between raw reachable tasks and reliability-weighted reachable tasks

delay_depth:
  minimum depth at which robust branch overtakes brittle branch by retained reachability

terminal_depth_estimate:
  approximate depth where global reachability collapses under random or R0 policy
```

## Success criteria

Primary success:

```text
R1 > R0-lookahead on mean global_LHR in at least two held-out generator families,
while low_resolution_dense remains matched.
```

Stronger success:

```text
R1 advantage appears specifically in measured high peak_retention_gap regimes,
not uniformly across all generated regimes.
```

Best success:

```text
unlabeled_structural shows R1 advantage only after post-hoc structural
classification identifies brittle/robust regimes, with no hand-labeled branch family.
```

Lock-in diagnostic success:

```text
lock_in_seeded / pseudo_omega continues to show high local_LHR,
low global_LHR, and high pseudo-Omega flag rate.
```

## Failure criteria

Clear failure:

```text
R1 fails to beat R0-lookahead in all held-out generator families,
while only the original brittle_peak / structured_asymmetric_v2 families remain positive.
```

Interpretation:

```text
current R1 signal is likely overfit to the calibration generator geometry.
```

Ambiguous failure:

```text
R1 beats R0-lookahead only in cost_brittle or delayed_robust,
but not in unlabeled_structural.
```

Interpretation:

```text
R1 may generalize across designed variants, but not yet beyond researcher-shaped families.
```

Adversarial failure:

```text
R1 overselects decoy_R1 paths and loses held-out LHR.
```

Interpretation:

```text
R1 is horizon-Goodhart-prone and needs perturbation or longer-horizon correction.
```

Control failure:

```text
R1 strongly beats R0-lookahead in low_resolution_dense.
```

Interpretation:

```text
possible metric artifact or uncontrolled policy asymmetry.
```

## Interpretation rules

Pre-register these interpretations:

```text
R1 wins in held-out brittle mechanisms:
  evidence of generator-variant generalization

R1 wins only in original families:
  calibration overfit likely

R1 wins in unlabeled structural regimes classified as high peak_retention_gap:
  strongest current evidence for nontrivial VAL0-CT generalization

R1 wins everywhere, including low-resolution dense:
  suspicious; likely uncontrolled artifact

R1 fails at T = 64 with 64-task algebras:
  expected generator-depth boundary

R1 fails at T = 64 with deeper generators:
  possible long-horizon limitation of current R1
```

## Compute plan

Keep CPU-first.

Use the hardened runner:

```text
first-completed collection
streaming JSONL
checkpointed aggregate.csv
checkpointed summary.md
status.json
runner-owned wall-clock controls
interleaved job ordering
```

Do not use external timeout as the primary stop mechanism.

Recommended wall-clock budget:

```text
Phase 0:
  under 30 minutes

Phase 1:
  under 1 hour

Phase 2:
  4-8 hours depending on included families

Phase 3 optional:
  2-4 hours
```

If runtime grows too high, cut in this order:

```text
1. optional Phase 3
2. decoy_R1
3. reliability_brittle
4. calibration anchor seeds
5. lock_in_seeded seeds
6. low_resolution_dense seeds
7. do not cut unlabeled_structural first
```

## Output expectations

Each run should produce:

```text
config.json
results.jsonl
aggregate.csv
summary.md
status.json
```

The final summary must answer:

```text
1. Did old positive anchors reproduce?
2. Did low_resolution_dense remain matched?
3. Did R1 win in cost_brittle?
4. Did R1 win in delayed_robust?
5. Did R1 win in unlabeled_structural high-variance regimes?
6. Did R1 overfit or fail on decoy_R1?
7. Did destructive lock-in replicate?
8. Which structural regimes predicted R1 advantage?
9. Is T = 64 testable with deeper generators yet?
```

## Do not broaden yet

Do not add:

```text
multifield coupling
lineage
corridors
R3 / lushness metric
embodied agents
GPU acceleration
large task counts except optional deep T64 confirmation
```

The next scientific question is generalization of R1 within single-field task algebras, not expansion to full Omega.

## Final target

The held-out generalization run should determine whether the current VAL0-CT signal is:

```text
a brittle_peak calibration artifact
```

or:

```text
a more general task-space pattern where robust future-preserving reachability
outperforms greedy peak reachability in regimes with brittle peaks and durable
retention structure.
```

If the latter holds, VAL0-CT earns a stronger status:

```text
positive held-out single-field proto-Omega signal
```

If not, the project should revise R1 or the generator assumptions before moving to VAL1/multifield work.
