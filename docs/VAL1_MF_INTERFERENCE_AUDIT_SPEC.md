# VAL1-MF Interference Audit Spec

Counterfactual sampled audit for destructive and constructive field interaction

## Purpose

The first VAL1-MF two-field compatibility smoke was a useful workflow result but a mostly negative scientific result for the exact substrate and measurement method.

It showed:

```text
runner:
  completed cleanly

pairs:
  150

errors:
  0

elapsed:
  about 79 seconds

main issue:
  joint enumeration became more cap-prone, not less

mixed_or_censored_bin:
  142 / 150 rows

aggregate joint cap hit rate:
  0.947
```

Therefore, do not scale the exact joint enumerator.

The next probe should ask a more targeted question:

> Are destructive and constructive interference dynamics actually present in the two-field toy substrate, and can we detect them without outcome-labeling the generator?

This spec defines a small counterfactual interference audit.

## Theory rationale

### Why multifield alone was insufficient

The first two-field smoke tested whether coupling fields would prune the high-mass single-field object enough to reveal compatibility structure.

It did not. Naive joint-state enumeration multiplied reachable states faster than minimal cross-field coupling pruned them.

So the problem is not simply:

```text
add another field
```

The problem is:

```text
measure how fields change each other's continuation geometry
```

That is interference.

### Constructive interference

Constructive interference means the coupled system preserves or improves recoverable continuation compared with an uncoupled baseline.

Toy-substrate signatures:

```text
coupled survival >= uncoupled survival
terminal probability does not increase
recovery / restore paths remain available
field A and field B both retain continuation
joint survival is meaningful without cap-only interpretation
```

Interpretive alignment analogy:

```text
systems interact in a way that preserves correction, recovery, and mutual option-space
```

### Destructive interference

Destructive interference means the coupled system loses recoverable continuation relative to uncoupled baselines.

Toy-substrate signatures:

```text
A alone viable
B alone viable
uncoupled parallel viable
coupled system collapses one or both fields
cross-obstruct / cross-commit effects drive terminality or exclusion
```

Interpretive alignment analogy:

```text
local optimization degrades another field's recoverability or the joint system's future options
```

### Pseudo-Omega as local destructive interference

Pseudo-Omega-like behavior is not just collapse.

It is asymmetric local survival with broader collapse:

```text
A survives locally
B degrades
joint recoverability degrades
A's continuation is purchased by cross-field exclusion, obstruction, commitment, or capacity consumption
```

This is the Goodhart-shaped alignment risk:

```text
local success / persistence
but loss of oversight, correction, reversibility, or other-field recoverability
```

### Why counterfactual ablations

To avoid hand-building examples, use the same generated pair under multiple coupling modes:

```text
A alone
B alone
uncoupled parallel
full coupling
cross-enable only
cross-obstruct only
cross-restore only
cross-commit only
shared-capacity only if implemented
```

Then measure deltas.

The goal is not to label tasks as constructive or destructive. The goal is to ask whether neutral cross-field operators produce measurable effects on continuation geometry.

## 3P audit

### Principled

Interference follows directly from relation and asymmetry:

```text
distinction:
  coupled and uncoupled trajectories differ

asymmetry:
  different cross-field effects have unequal consequences

relation:
  one field's transformations alter another field's future possible transformations
```

### Parsimonious

Do not add new theory machinery.

Use the current VAL1-MF two-field substrate, but change measurement method:

```text
from:
  raw joint enumeration

to:
  sampled / cap-aware counterfactual survival deltas
```

Do not add:

```text
new outcome-labeled generator families
R1/R2 tuning
multifield atlas scale
lineage
assembly
TDA
GPU
```

### Predictive

If the substrate contains the relevant dynamics, then the same generated pair should show different survival/recovery geometry under different coupling modes.

Expected examples:

```text
cross-obstruct-only:
  increases destructive interference / terminality

cross-restore-only:
  may increase recovery or mutual compatibility

cross-enable-only:
  may increase expansion, but may also increase cap pressure

cross-commit-only:
  may increase irreversible exclusion / local dominance

full coupling:
  mixture of constructive and destructive effects
```

If all modes look the same, the substrate or estimator is not resolving interference.

## Core methodological change

Do not make raw joint enumeration the primary estimator.

Primary estimator should be sampled/cap-aware.

Recommended primary quantities:

```text
sampled_survival_probability_d16
sampled_survival_probability_d32
sampled_terminal_probability_d16
sampled_terminal_probability_d32
sampled_A_alive_probability
sampled_B_alive_probability
sampled_joint_alive_probability
```

Use enumeration only as diagnostic:

```text
cap_hit_d16
cap_hit_d32
enumerated_mass_d16
enumerated_mass_d32
```

## Coupling modes

For each generated pair, evaluate these modes.

### A_alone

Field A without field B.

Purpose:

```text
baseline A viability
```

### B_alone

Field B without field A.

Purpose:

```text
baseline B viability
```

### uncoupled_parallel

A and B evolve together but cross-field effects are disabled.

Purpose:

```text
baseline joint survival without interaction
```

### full_coupling

All sampled cross-field effects active.

Purpose:

```text
actual coupled dynamics
```

### cross_enable_only

Only cross-enable effects active.

Purpose:

```text
expansion/support without direct obstruction
```

### cross_obstruct_only

Only cross-obstruct effects active.

Purpose:

```text
destructive interference stress
```

### cross_restore_only

Only cross-restore effects active.

Purpose:

```text
repair / re-entry stress
```

### cross_commit_only

Only cross-commit effects active.

Purpose:

```text
irreversible exclusion stress
```

### shared_capacity_only optional

Only shared capacity effects active.

Purpose:

```text
resource interference stress
```

Include only if shared capacity is already implemented cleanly.

## Metrics

### Baseline survival metrics

For each pair and mode:

```text
A_alive_d16
B_alive_d16
joint_alive_d16
A_alive_d32 optional
B_alive_d32 optional
joint_alive_d32 optional

A_terminal_d16
B_terminal_d16
joint_terminal_d16
```

Definitions:

```text
A_alive:
  A has at least one valid continuation or nonterminal sampled state

B_alive:
  B has at least one valid continuation or nonterminal sampled state

joint_alive:
  both A and B alive in the same sampled trajectory/state
```

### Interference deltas

Use uncoupled_parallel as the main comparison baseline.

```text
constructive_interference_d16 =
  joint_alive_full_coupling_d16 - joint_alive_uncoupled_parallel_d16

destructive_interference_d16 =
  joint_alive_uncoupled_parallel_d16 - joint_alive_full_coupling_d16

A_harm_d16 =
  A_alive_uncoupled_parallel_d16 - A_alive_full_coupling_d16

B_harm_d16 =
  B_alive_uncoupled_parallel_d16 - B_alive_full_coupling_d16

A_help_d16 =
  A_alive_full_coupling_d16 - A_alive_uncoupled_parallel_d16

B_help_d16 =
  B_alive_full_coupling_d16 - B_alive_uncoupled_parallel_d16
```

Also compute these for each ablation mode.

### Pseudo-Omega candidate scores

Neutral diagnostic first:

```text
A_local_dominance_delta =
  A_alive_full_coupling_d16
  - B_alive_full_coupling_d16

A_exclusion_delta =
  B_alive_uncoupled_parallel_d16
  - B_alive_full_coupling_d16

A_pseudo_omega_candidate_score =
  max(0, A_alive_full_coupling_d16 - B_alive_full_coupling_d16)
  + max(0, B_alive_uncoupled_parallel_d16 - B_alive_full_coupling_d16)
  + max(0, joint_alive_uncoupled_parallel_d16 - joint_alive_full_coupling_d16)
```

Analogous for B.

Interpretive label:

```text
pseudo_omega_like_A:
  only if A remains alive, B/joint degrade, and this is not cap-only
```

### Mutual support candidate scores

```text
mutual_support_delta =
  min(A_alive_full_coupling_d16, B_alive_full_coupling_d16, joint_alive_full_coupling_d16)
  - min(A_alive_uncoupled_parallel_d16, B_alive_uncoupled_parallel_d16, joint_alive_uncoupled_parallel_d16)
```

Interpretive label:

```text
constructive_interference_like:
  full coupling improves or preserves joint survival relative to uncoupled baseline
```

### Operator footprint

Report cross-effect counts:

```text
cross_enable_edges_A_to_B
cross_enable_edges_B_to_A
cross_obstruct_edges_A_to_B
cross_obstruct_edges_B_to_A
cross_restore_edges_A_to_B
cross_restore_edges_B_to_A
cross_commit_edges_A_to_B
cross_commit_edges_B_to_A
shared_capacity_effect_count optional
```

These are explanatory fields only.

## Neutral bins

Use neutral bins first:

```text
constructive_delta_bin:
  full coupling improves joint alive probability relative to uncoupled baseline

destructive_delta_bin:
  full coupling lowers joint alive probability relative to uncoupled baseline

A_local_dominance_bin:
  A alive preserved, B harmed, joint harmed

B_local_dominance_bin:
  B alive preserved, A harmed, joint harmed

mutual_collapse_delta_bin:
  both A and B harmed relative to uncoupled baseline

no_detectable_interference_bin:
  coupled and uncoupled estimates similar

censored_or_low_confidence_bin:
  cap/censoring or sampling confidence too poor
```

Interpretive mapping:

```text
A_local_dominance_bin:
  provisional pseudo-Omega-like A

B_local_dominance_bin:
  provisional pseudo-Omega-like B

constructive_delta_bin:
  provisional constructive compatibility

destructive_delta_bin:
  destructive interference
```

## Confidence / censoring

Because the previous smoke was cap-dominated, every row must include confidence flags:

```text
cap_hit_any
cap_hit_joint
sample_count
standard_error_alive_estimates if easy
low_confidence_flag
```

If using sampled rollouts, include binomial standard error for alive/terminal probabilities when cheap:

```text
se = sqrt(p * (1 - p) / n)
```

Rows with high cap/censoring or large uncertainty should not be used as strong evidence.

## Run shape

Keep this small.

Recommended:

```text
paired neutral worlds:
  50-100 pairs

num_tasks per field:
  64

rollout_samples:
  256 if cheap
  128 acceptable for smoke

horizons:
  d16 primary
  d32 optional

max_states_per_depth:
  keep only for diagnostic enumeration; 1024 or 2048

workers:
  18

max_runtime_seconds:
  1800
```

No full atlas scale.

No GPU.

## Required outputs

Primary files:

```text
config.json
status.json
results.jsonl
results.csv
aggregate.csv
mode_summary.csv
interference_bins.csv
ablation_effects.csv
operator_footprint_summary.csv
summary.md
```

Per-row required fields:

```text
seed_pair
seed_A
seed_B
mode_results_json or flattened mode fields
coupling_parameter_json
rollout_samples

A_alive_uncoupled_d16
B_alive_uncoupled_d16
joint_alive_uncoupled_d16

A_alive_full_d16
B_alive_full_d16
joint_alive_full_d16

A_alive_enable_only_d16
B_alive_enable_only_d16
joint_alive_enable_only_d16

A_alive_obstruct_only_d16
B_alive_obstruct_only_d16
joint_alive_obstruct_only_d16

A_alive_restore_only_d16
B_alive_restore_only_d16
joint_alive_restore_only_d16

A_alive_commit_only_d16
B_alive_commit_only_d16
joint_alive_commit_only_d16

constructive_interference_d16
destructive_interference_d16
A_harm_d16
B_harm_d16
A_help_d16
B_help_d16
A_pseudo_omega_candidate_score
B_pseudo_omega_candidate_score
mutual_support_delta
neutral_bin
interpretive_label_optional
cap_hit_any
low_confidence_flag
```

## Analysis questions

The summary should answer:

```text
1. Did the runner complete cleanly?
2. Do different coupling ablations produce different survival geometry?
3. Are destructive and constructive interference deltas non-degenerate?
4. Are A/B local-dominance cases present without outcome labels?
5. Are mutual-support cases present without outcome labels?
6. Which operator footprints correlate with which deltas?
7. Are the results dominated by censoring or sampling uncertainty?
8. Is this substrate capable of hosting the dynamics we care about?
```

## Success criteria

### Minimal success

```text
runner completes
ablation modes produce non-identical survival estimates
interference deltas are non-degenerate
confidence/censoring fields are reported
```

### Stronger success

```text
cross-obstruct-only and/or cross-commit-only produces more destructive deltas than uncoupled or cross-restore-only
cross-restore-only produces at least some mutual-support or harm-reduction cases
full coupling produces a mix of constructive, destructive, and no-effect cases
```

### Best success

```text
A/B local-dominance bins appear without outcome-labeled generator design,
and these can be traced to neutral operator footprints rather than cap artifacts.
```

## Failure criteria

### No interference detected

```text
all modes look statistically identical
```

Interpretation:

```text
cross-field effects are too weak, ignored by transitions, or not being measured properly
```

### Everything collapses

```text
all coupled modes terminal quickly
```

Interpretation:

```text
coupling too destructive or capacity too tight
```

### Everything expands/caps

```text
all coupled modes cap or survive trivially
```

Interpretation:

```text
estimator still not resolving compatibility; use sampled hazards / stricter viability definitions
```

### Label smuggling

```text
constructive/destructive labels are produced directly by generator regimes rather than measured deltas
```

Interpretation:

```text
generator is too hand-shaped; return to neutral operator sampling
```

## Implementation notes for Codex

### Leeway boundaries

Implementation leeway is fine, but preserve these invariants:

```text
1. Same pair must be evaluated under multiple coupling modes.
2. Primary evidence is counterfactual delta between modes.
3. Neutral bins must be primary.
4. Interpretive labels must be provisional.
5. Do not tune generator probabilities to force pseudo-Omega counts.
6. Raw joint enumeration must not be the primary success measure.
7. Cap/censoring and sampling confidence must be surfaced.
```

### Suggested module shape

Either extend `omega/val1_mf` or add:

```text
omega/val1_mf/run_interference_audit.py
```

Recommended development order:

```text
1. Reuse two-field generator and coupled transition code.
2. Add coupling mode masks.
3. Implement sampled rollouts for each mode.
4. Compute mode deltas.
5. Add neutral bins.
6. Smoke 10 pairs.
7. Run 50-100 pairs if clean.
```

## What this probe can claim

Can claim if successful:

```text
the two-field toy substrate contains measurable destructive / constructive
interference dynamics under neutral cross-field operators.
```

Cannot claim:

```text
Omega validation
alignment validation
true multifield axiology
pseudo-Omega fully operationalized
```

## Bottom line

The previous VAL1-MF smoke showed that adding fields is not enough.

This audit asks the correct next question:

```text
Do neutral cross-field transformations actually change the survival and
recoverability geometry of coupled fields in measurable constructive or
destructive ways?
```

If yes, the toy can host the dynamics we care about.

If no, the substrate needs revision before further multifield scaling.
