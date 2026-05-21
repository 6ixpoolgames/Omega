# VAL0-G Neutral Grammar Stability Probe Spec

Second small probe after the first neutral-grammar geometry smoke

## Purpose

The first VAL0-G neutral grammar smoke passed the minimal bar:

```text
runner:
  completed cleanly

rows:
  74

errors:
  0

neutral_grammar_v1:
  50 seeds

guardrails:
  low_resolution_dense = 12 seeds
  brittle_peak = 12 seeds
```

The smoke produced multiple measured post-hoc geometry bins in neutral worlds:

```text
recoverable_basin_like:
  26 / 50 neutral rows

self_terminating:
  16 / 50 neutral rows

thin_ridge:
  6 / 50 neutral rows

deep_corridor_like:
  2 / 50 neutral rows
```

This is a useful first signal, but not a theory result.

The goal of this second probe is not scale and not validation. The goal is substrate sanity and forced-fit reduction.

Core question:

> Are the geometry regimes produced by `neutral_grammar_v1` stable under a larger sample and better measurement, or are they artifacts of thresholds, caps, signatures, or guardrail leakage?

## Current interpretation

The first smoke should be read as:

```text
positive:
  the neutral grammar can culture multiple geometry-like regimes

not established:
  these regimes are natural kinds
  these regimes are Omega-like
  recoverable_basin_like is actually recoverable
  thin_ridge is actually the right brittle analogue
```

The substrate is promising as a first neutral culture medium, but it is not yet the mature substrate.

## Why this probe is needed

The first smoke surfaced several risks.

### 1. Calibration / forced-fit risk

The initial pre-result smoke was too expansion-heavy and saturated depth-16 descendant mass. The grammar was then minimally revised to broaden lower-enable, higher-obstruction, decay, and capacity-pressure regimes.

That revision is reasonable for smoke calibration, but it creates forced-fit risk.

Therefore:

```text
Freeze neutral_grammar_v1 for this probe.
Do not tune generator parameters after seeing this run.
```

### 2. Classifier smuggling risk

The current class names are assigned by hand thresholds:

```text
self_terminating:
  terminal probability high or d16 very low

thin_ridge:
  cut sensitivity low and d16 nontrivial

recoverable_basin_like:
  survival AUC high, cut survival high, terminal probability low

deep_corridor_like:
  d16 greater than d1 and terminal probability low enough
```

These are acceptable smoke bins, but not discovered natural categories.

Therefore:

```text
Report neutral bin names alongside interpretive names.
Do not treat posthoc_class as ground truth.
```

Suggested neutral names:

```text
high_terminal_bin:
  provisional self_terminating

high_mass_low_cut_bin:
  provisional thin_ridge

high_mass_high_cut_bin:
  provisional recoverable_basin_like

depth_persistent_bin:
  provisional deep_corridor_like

mixed_or_noise_bin:
  unresolved
```

### 3. Cap artifact risk

Several rows hit the depth-16 state cap. If descendant mass equals `max_states_per_depth`, the metric may mean:

```text
measurement ceiling reached
```

rather than:

```text
large future-bearing task space
```

Therefore add explicit cap-hit fields.

### 4. Signature compression risk

The state contains `completed`, but the current `state_signature` omits completed history and keeps:

```text
enabled
disabled
irreversible
capacity
```

Because completed tasks affect future validity, this can merge histories that are dynamically different.

Therefore compare:

```text
coarse_signature:
  enabled, disabled, irreversible, capacity

full_signature:
  enabled, disabled, completed, irreversible, capacity
```

This is not a philosophical preference yet. It is a substrate-sensitivity test.

### 5. Shallow cut-sensitivity risk

The current cut metric removes one initially enabled task and recomputes horizon-16 mass.

That only tests initial-entry bottlenecks. It does not test downstream bottlenecks or bridge fragility inside the reachable graph.

Therefore add a downstream cut probe.

## 3P audit

### Principled

This probe remains grounded in the theory:

```text
distinction:
  different transition histories may or may not remain distinct under signature choice

asymmetry:
  different cuts, commitments, obstructions, and capacities have different continuation effects

relation:
  continuation geometry is a relation over task-repertoire states across depth
```

The probe tests whether observed geometries are real features of the transition system, not artifacts of labels or caps.

### Parsimonious

Do not add new theory machinery.

Do not add:

```text
R1 tuning
multifield
lineage
assembly-history
TDA
GPU
new large task counts
new named brittle/robust generators
```

Only add measurement safeguards:

```text
cap-hit fields
depth 32 if cheap
signature comparison
downstream cut sensitivity
neutral bin labels
```

### Predictive

Predictions:

```text
If the substrate is real enough:
  neutral_grammar_v1 should again produce multiple non-degenerate geometry bins

If the first smoke was cap/threshold artifact:
  classes should shift heavily or collapse after cap-hit and signature tests

If signature compression matters:
  coarse vs full signatures will disagree on descendant mass / class assignment

If cut sensitivity was too shallow:
  initial-cut robustness may remain high while downstream-cut robustness reveals bottlenecks
```

## Required implementation changes

### 1. Freeze grammar

Use the current committed `neutral_grammar_v1` without parameter retuning.

Allowed:

```text
bug fixes
reporting additions
measurement additions
```

Forbidden:

```text
changing regime probabilities to get prettier class counts
changing thresholds to preserve desired class counts
adding outcome-like labels
```

### 2. Add cap-hit fields

For each depth, report whether the depth enumeration reached the cap:

```text
cap_hit_d1
cap_hit_d2
cap_hit_d4
cap_hit_d8
cap_hit_d16
cap_hit_d32 optional
```

Definition:

```text
cap_hit_d = 1 if descendant_mass_d >= max_states_per_depth else 0
```

Also report cap-hit rates by family and class.

### 3. Add depth 32 if cheap

If runtime remains trivial, include depth 32:

```text
survival_d32
descendant_mass_d32
P_terminal_d32
cap_hit_d32
branching_B16
```

If depth 32 is too expensive, skip it and note why.

### 4. Add signature mode

Implement a signature mode parameter:

```text
signature_mode:
  coarse
  full
```

Where:

```text
coarse:
  enabled, disabled, irreversible, capacity

full:
  enabled, disabled, completed, irreversible, capacity
```

Run both modes on the same generated worlds.

Output paired fields or separate rows with:

```text
signature_mode
```

Primary comparison:

```text
class agreement rate between coarse and full signatures
relative descendant_mass_d16 difference
relative survival_auc difference
relative cut_sensitivity difference
```

### 5. Add downstream cut sensitivity

Keep current initial cut, but rename it clearly:

```text
initial_cut_sensitivity_k1
```

Add downstream cut sensitivity:

```text
downstream_cut_sensitivity_k1
```

Suggested first implementation:

```text
1. Build reachable states to depth 4 or 8.
2. Sample tasks that appear in enabled sets of sampled downstream states.
3. Globally disable or remove one sampled downstream task.
4. Recompute descendant_mass_d16 or d32.
5. Report ratio to base mass.
```

This does not need to be perfect. It only needs to test whether bottlenecks are being missed by initial cuts.

### 6. Report neutral bin labels

Keep `posthoc_class`, but also output:

```text
posthoc_bin_neutral
```

Suggested mapping:

```text
self_terminating -> high_terminal_bin
thin_ridge -> high_mass_low_cut_bin
recoverable_basin_like -> high_mass_high_cut_bin
deep_corridor_like -> depth_persistent_bin
lush_branching_like -> high_branching_low_terminal_bin
flat_dense -> flat_dense_bin
mixed_or_noise -> mixed_or_noise_bin
```

Summaries should lead with neutral bin names and put interpretive names second.

## Run shape

This should still be a small probe.

Recommended:

```text
neutral_grammar_v1:
  250 seeds

guardrails:
  low_resolution_dense = 50 seeds
  brittle_peak = 50 seeds

num_tasks:
  64

max_states_per_depth:
  512 initially

rollout_samples:
  128

cut_samples:
  4

workers:
  18

max_runtime_seconds:
  1800 to 3600
```

If runtime remains extremely low, increase neutral seeds to 500, not metrics complexity.

Do not run a full atlas yet.

## Optional cap-sensitivity mini grid

If cheap, run a small cap grid on the same seed subset:

```text
neutral_grammar_v1:
  50 seeds

max_states_per_depth:
  512, 1024, 2048
```

Purpose:

```text
estimate whether class assignments and survival metrics are stable under cap changes
```

Do not do this if it complicates the runner too much.

## Required outputs

Primary files:

```text
config.json
status.json
results.jsonl
results.csv
aggregate.csv
geometry_class_bins.csv
neutral_bin_summary.csv
parameter_regime_summary.csv
signature_comparison.csv
cap_hit_summary.csv
cut_sensitivity_summary.csv
summary.md
```

Minimum summary tables:

```text
1. family aggregate
2. neutral bin counts
3. interpretive class counts
4. cap-hit rate by family and bin
5. coarse vs full signature agreement
6. initial-cut vs downstream-cut comparison
7. parameter regime summary
```

## Analysis questions

The final summary should answer:

```text
1. Did the runner complete cleanly?
2. Did neutral_grammar_v1 again produce multiple geometry bins?
3. Did class/bin counts remain broadly stable compared to the first smoke?
4. How often did each depth hit the state cap?
5. Did adding depth 32 change interpretation?
6. Did coarse and full signatures agree?
7. Did downstream cuts reveal bottlenecks missed by initial cuts?
8. Did low_resolution_dense remain identifiable as dense/flat or cap-saturated?
9. Did brittle_peak become a better or worse thin-ridge guardrail under revised metrics?
10. Is the substrate safe enough for a larger atlas battery?
```

## Success criteria

### Minimal success

```text
no errors
multiple neutral geometry bins appear again
cap-hit reporting works
coarse/full signature comparison works
downstream cut reporting works
```

### Strong success

```text
bin separation remains visible after cap-hit and signature checks
self-termination-like rows remain high-terminal
high-mass/high-cut rows remain low-terminal
high-mass/low-cut rows remain distinguishable from high-mass/high-cut rows
```

### Best success

```text
class/bin assignments are reasonably stable under signature mode and cap sensitivity,
while downstream cut sensitivity adds useful bottleneck information.
```

This would justify a larger VAL0-G atlas run.

## Failure criteria

### Cap failure

```text
most high-survival or high-mass rows hit the cap at d16/d32
```

Interpretation:

```text
descendant mass is not trustworthy as a geometry measure yet
```

Action:

```text
replace capped mass with sampled survival/filter ratios or raise cap before scaling
```

### Signature failure

```text
coarse and full signatures disagree strongly on class/bin assignment
```

Interpretation:

```text
current coarse state geometry may be an artifact of history merging
```

Action:

```text
use full signature or explicitly justify coarse-grained abstraction before atlas scale
```

### Cut failure

```text
initial cut says robust but downstream cut finds strong fragility
```

Interpretation:

```text
previous cut sensitivity was too shallow
```

Action:

```text
use downstream bottleneck metrics going forward
```

### Classifier failure

```text
bin counts collapse or become dominated by threshold quirks
```

Interpretation:

```text
current post-hoc classifier is not stable
```

Action:

```text
switch to quantile/continuous reporting before interpretive class labels
```

## Interpretation guardrails

Do not claim:

```text
Omega validation
recoverable_basin_like is true recoverability
thin_ridge is true brittleness
self_terminating proves asymmetry dominance
```

Allowed claim if the probe succeeds:

```text
neutral_grammar_v1 continues to culture non-degenerate continuation geometries,
and the measurement stack is less vulnerable to cap, signature, and cut artifacts.
```

## Compute guidance

Stay CPU-first.

The first smoke ran in about four seconds, so compute is not currently the bottleneck.

Do not start GPU work until:

```text
metrics stabilize
state signatures are chosen
cap strategy is settled
geometry classes are meaningful enough to scale
```

## Next step after this probe

If successful:

```text
VAL0-G Atlas Battery v1:
  1000-3000 neutral seeds
  stable metrics
  neutral bins first, interpretive labels second
  no R1 tuning
```

If not successful:

```text
revise measurement substrate before more scale
```

## Bottom line

This probe is a forced-fit audit.

It should test whether the first neutral-grammar smoke found real substrate dynamics or merely produced appealing labels from capped, compressed, thresholded measurements.
