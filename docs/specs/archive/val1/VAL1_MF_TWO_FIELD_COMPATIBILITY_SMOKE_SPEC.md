# VAL1-MF Two-Field Compatibility Smoke Spec

First minimal multifield probe for constructor-style task-repertoire geometry

## Purpose

VAL0-G established a promising single-field neutral grammar substrate, but it also exposed a measurement blocker:

```text
single-field high-mass regimes are heavily cap-censored
```

In the stability probe, neutral geometry bins remained stable under cap increase and coarse/full signature agreement was very high, but high-mass/high-cut rows still hit the enumeration cap heavily at d16/d32. This suggests the single-field substrate is plausibly on-object, but raw descendant mass is too unconstrained in the regimes we most care about.

This spec defines the first minimal multifield smoke:

```text
VAL1-MF:
  Two-Field Compatibility Smoke
```

Core question:

> Do coupled task-repertoire fields prune high-mass single-field continuation into distinguishable joint-viable, pseudo-Omega-like, and mutually collapsing regimes?

This is a smoke and substrate test. It is not full Omega validation.

## Theory rationale

### Why multifield now?

Single-field VAL0-G asks:

```text
Does a trajectory preserve its own continuation geometry?
```

But Omega is not merely self-continuation. A local process can persist by consuming, obstructing, or locking out the broader field it depends on.

Multifield asks:

```text
Does local continuation remain compatible with other continuation fields?
```

This is where the distinction between Omega and pseudo-Omega becomes measurable.

### Omega vs pseudo-Omega

The principled distinction is:

```text
Omega-like:
  local continuation is compatible with broader recoverable continuation

pseudo-Omega-like:
  local continuation is purchased by broader recoverability collapse
```

In alignment terms, pseudo-Omega is the geometry of Goodharted agency:

```text
local objective success
self-preservation / local continuation
loss of oversight, correction, reversibility, or other-field recoverability
```

The two-field smoke should therefore measure not only whether a field survives, but what happens to the other field and to the joint field.

### Asymmetry as filter

The deeper theoretical claim is that asymmetric consequences filter trajectory space over iteration:

```text
some paths self-terminate
some paths create brittle local peaks
some paths preserve one local basin while collapsing the broader field
some paths preserve compatible recoverability
```

Single-field continuation can overgrow because compatibility constraints are absent. Coupling fields introduces the missing compatibility filter.

Expected effect:

```text
single-field high-mass regions:
  many branches survive alone

multifield coupling:
  some remain jointly viable
  some become pseudo-Omega-like local survival / other-field collapse
  some mutually collapse
  some form mutual-repair or compatibility regimes
```

This is the first test of whether multifield interaction prunes the object harder than single-field enumeration.

## 3P audit

### Principled

The probe remains grounded in constructor-style task repertoires:

```text
task:
  possible transformation

field:
  organized task-repertoire transition system

coupling:
  transformations in one field can alter possible transformations in another field

compatibility:
  joint continuation remains possible without collapsing either field's recoverability
```

Primitive grounding:

```text
distinction:
  A-field and B-field trajectories differ

asymmetry:
  cross-field effects have unequal consequences

relation:
  fields are linked through transformations that preserve or destroy continuation structure
```

### Parsimonious

Start with exactly two fields.

Use the existing frozen neutral grammar as the base field generator.

Add only minimal cross-field operators:

```text
cross_enable
cross_obstruct
cross_restore
cross_commit
shared_capacity_delta
```

Do not add agents, rewards, preferences, lineage, assembly, TDA, or LLM scenarios.

### Predictive

If multifield compatibility matters, we expect:

```text
1. Joint survival is more discriminating than single-field survival.
2. Some single-field high-mass rows become pseudo-Omega-like under coupling.
3. Some couplings preserve both fields and show high compatibility ratios.
4. Cap rates should fall or become less decisive under joint compatibility filtering.
5. Cross-obstruction / cross-commit regimes should show local/global divergence.
6. Cross-restore regimes should increase mutual recovery or compatibility.
```

If none of this happens, the coupling substrate is either too weak, too strong, or not measuring the right object.

## Substrate design

### Field structure

Generate two neutral grammar worlds:

```text
Field A:
  neutral_grammar_v1(seed_A)

Field B:
  neutral_grammar_v1(seed_B)
```

Each has its own:

```text
enabled
disabled
completed
irreversible
capacity
```

The joint state is:

```text
JointState =
  state_A
  state_B
  shared_capacity optional
  cross_irreversible commitments optional
  coupling_state optional
```

For the first smoke, keep coupling_state simple or omit it.

### Cross-field operators

For each task, sample sparse cross-field effects:

```text
A task may affect B:
  cross_enable_B
  cross_obstruct_B
  cross_restore_B
  cross_commit_B
  shared_capacity_delta

B task may affect A:
  cross_enable_A
  cross_obstruct_A
  cross_restore_A
  cross_commit_A
  shared_capacity_delta
```

Use neutral probabilities. Do not label tasks as cooperative, parasitic, Omega, or pseudo-Omega.

### Coupling regimes

Sample broad, neutral coupling regimes and record them as parameters only:

```text
coupling_density:
  none / sparse / medium

cross_effect_balance:
  enable_heavy / obstruct_heavy / restore_heavy / mixed

shared_capacity_pressure:
  none / loose / tight

cross_commit_probability:
  none / low / medium

symmetry:
  symmetric / A_heavier / B_heavier
```

These are not outcome labels. They are generator parameters for post-hoc analysis.

## Actions / transitions

At each step, a transition can apply one valid task from A or one valid task from B.

Recommended first semantics:

```text
valid joint task:
  task is valid in its own field
  shared capacity remains nonnegative if used

apply A task:
  update A by normal grammar rules
  apply sampled cross effects to B
  update shared capacity if applicable

apply B task:
  update B by normal grammar rules
  apply sampled cross effects to A
  update shared capacity if applicable
```

Do not require simultaneous A+B actions in the first smoke.

Optional later:

```text
paired actions
turn-taking constraints
adversarial vs cooperative schedules
coupling-state evolution
```

## Measurement goals

The first smoke should not rely on exact high-mass enumeration alone.

Measure both enumerated and sampled quantities.

### Single-field baselines

For each field alone:

```text
A_single_survival_curve
B_single_survival_curve
A_single_terminal_probability
B_single_terminal_probability
A_single_cap_hit_rate
B_single_cap_hit_rate
```

### Joint survival

For coupled dynamics:

```text
joint_survival_d4
joint_survival_d8
joint_survival_d16
joint_survival_d32 optional

joint_terminal_probability_d16
joint_terminal_probability_d32 optional

joint_cap_hit_d16
joint_cap_hit_d32 optional
```

### Field-specific survival under coupling

Within joint rollouts / joint reachable states, compute:

```text
A_coupled_survival_d16
B_coupled_survival_d16
A_coupled_terminal_probability_d16
B_coupled_terminal_probability_d16
```

### Compatibility ratios

Use cap-aware or sampled estimates where possible:

```text
A_filter_ratio = A_coupled_survival / max(epsilon, A_single_survival)
B_filter_ratio = B_coupled_survival / max(epsilon, B_single_survival)
joint_filter_ratio = joint_survival / max(epsilon, min(A_single_survival, B_single_survival))

compatibility_ratio = joint_filter_ratio / max(epsilon, min(A_filter_ratio, B_filter_ratio))
```

If exact masses are capped, report ratios as censored.

### Local/global divergence

For A-local dominance risk:

```text
local_global_divergence_A = A_filter_ratio - joint_filter_ratio
exclusion_ratio_A = A_filter_ratio - B_filter_ratio
```

For B:

```text
local_global_divergence_B = B_filter_ratio - joint_filter_ratio
exclusion_ratio_B = B_filter_ratio - A_filter_ratio
```

### Pseudo-Omega candidate score

Do not call this Omega validation. Use neutral fields first.

Suggested neutral diagnostic:

```text
A_local_dominance_score =
  high A_filter_ratio
  + low B_filter_ratio
  + low joint_filter_ratio
  + high cross-obstruct / cross-commit footprint

B_local_dominance_score analogous
```

Interpretive label:

```text
pseudo_omega_like_A:
  A survives locally while B/joint recoverability collapses
```

Use only as post-hoc diagnostic.

### Mutual compatibility candidate score

Suggested neutral diagnostic:

```text
mutual_compatibility_score =
  min(A_filter_ratio, B_filter_ratio, joint_filter_ratio)
  - penalty for terminal probability
  - penalty for irreversible cross-commitment
```

Interpretive label:

```text
joint_viable_like:
  both fields and joint field retain continuation
```

Again: diagnostic, not Omega validation.

## Class bins: neutral first

Post-hoc neutral bins should lead summaries:

```text
joint_viable_bin:
  A_filter high, B_filter high, joint_filter high

A_dominant_collapse_bin:
  A_filter high, B_filter low, joint_filter low

B_dominant_collapse_bin:
  B_filter high, A_filter low, joint_filter low

mutual_collapse_bin:
  A_filter low, B_filter low, joint_filter low

uncoupled_parallel_bin:
  A_filter and B_filter similar to single-field, joint_filter not restrictive

mixed_or_censored_bin:
  insufficient or cap-censored signal
```

Interpretive mapping:

```text
joint_viable_bin:
  provisional Omega-compatible / mutual recoverability

A_dominant_collapse_bin:
  provisional pseudo-Omega-like A

B_dominant_collapse_bin:
  provisional pseudo-Omega-like B

mutual_collapse_bin:
  interference / destructive coupling
```

## Cap and horizon strategy

The VAL0-G stability probe showed high-mass single-field regimes are capped at d16/d32. Do not ignore this.

For VAL1-MF, report:

```text
A_single_cap_hit_d16
B_single_cap_hit_d16
joint_cap_hit_d16
A_coupled_cap_hit_d16
B_coupled_cap_hit_d16
```

If joint coupling lowers cap-hit rates relative to single-field baselines, that supports the hypothesis that multifield interaction prunes the object harder.

If joint states remain capped, switch emphasis to sampled survival / terminal / filter-ratio estimates.

Recommended depths:

```text
4, 8, 16
```

Optional:

```text
32 if runtime remains low and cap reporting is in place
```

## Smoke run shape

Keep the first run small.

Recommended:

```text
paired neutral worlds:
  100-200 pairs

num_tasks per field:
  64

signature mode:
  full for first multifield smoke
  coarse optional only if cheap

max_states_per_depth:
  1024 or 2048

rollout_samples:
  128 or 256

cut_samples:
  0 or minimal in first smoke

workers:
  18

max_runtime_seconds:
  1800-3600
```

Use only `neutral_grammar_v1` fields in the first smoke.

Do not use brittle/dense guardrails as semantic proof yet, because VAL0-G showed the old guardrails are not clean under the new metrics.

Optional guardrails:

```text
uncoupled baseline:
  coupling_density = none

symmetric sparse baseline:
  low cross-effect density

strong obstruct baseline:
  intentionally high cross-obstruction as stress test, but label as stress baseline
```

## Required outputs

Primary files:

```text
config.json
status.json
results.jsonl
results.csv
aggregate.csv
coupling_regime_summary.csv
compatibility_bins.csv
cap_hit_summary.csv
filter_ratio_summary.csv
summary.md
```

Per row:

```text
seed_pair
seed_A
seed_B
coupling_parameter_json
num_tasks_A
num_tasks_B
signature_mode

A_single_survival_d16
B_single_survival_d16
joint_survival_d16
A_coupled_survival_d16
B_coupled_survival_d16

A_single_P_terminal_d16
B_single_P_terminal_d16
joint_P_terminal_d16
A_coupled_P_terminal_d16
B_coupled_P_terminal_d16

A_single_cap_hit_d16
B_single_cap_hit_d16
joint_cap_hit_d16
A_coupled_cap_hit_d16
B_coupled_cap_hit_d16

A_filter_ratio
B_filter_ratio
joint_filter_ratio
compatibility_ratio
local_global_divergence_A
local_global_divergence_B
exclusion_ratio_A
exclusion_ratio_B

cross_enable_edges_A_to_B
cross_enable_edges_B_to_A
cross_obstruct_edges_A_to_B
cross_obstruct_edges_B_to_A
cross_restore_edges_A_to_B
cross_restore_edges_B_to_A
cross_commit_edges_A_to_B
cross_commit_edges_B_to_A

neutral_bin
interpretive_label_optional
```

## Analysis questions

The summary should answer:

```text
1. Did the runner complete cleanly?
2. Did joint coupling reduce cap-hit rates relative to single-field baselines?
3. Did multiple compatibility bins appear?
4. Did local-dominance / pseudo-Omega-like rows appear without outcome labels?
5. Did joint-viable-like rows appear?
6. Which coupling parameters correlate with each bin?
7. Are results dominated by cap-censored mixed rows?
8. Are the diagnostic ratios stable enough for a larger probe?
```

## Success criteria

### Minimal success

```text
runner completes with zero errors
joint metrics are non-degenerate
cap-hit fields are reported
at least two compatibility bins appear
```

### Stronger success

```text
single-field high-mass/capped worlds separate under coupling into:
  joint_viable_bin
  A/B local-dominance bins
  mutual_collapse_bin or uncoupled_parallel_bin
```

### Best success

```text
joint coupling reduces cap-censoring and reveals pseudo-Omega-like local/global divergence
without using outcome labels in the generator.
```

## Failure criteria

### Coupling too weak

```text
most rows are uncoupled_parallel_bin
joint survival ≈ independent single-field survival
```

Action:

```text
increase coupling density or shared-capacity pressure slightly
```

### Coupling too strong

```text
most rows are mutual_collapse_bin
joint survival near zero
```

Action:

```text
lower cross-obstruct / cross-commit / shared-capacity pressure
```

### Measurement still capped

```text
joint_cap_hit_d16 remains high across most rows
```

Action:

```text
use sampled survival/filter estimates rather than raw descendant mass
```

### Label smuggling

```text
bins map trivially to an outcome-coded coupling regime
```

Action:

```text
broaden coupling distributions and keep neutral bins primary
```

## Implementation notes for Codex

### Leeway boundaries

Codex has implementation leeway, but should preserve these invariants:

```text
1. No outcome-labeled generator categories.
2. Cross-field effects are neutral transformations only.
3. Neutral bins are primary; interpretive labels are secondary.
4. Cap-hit/censoring must be surfaced explicitly.
5. Do not tune coupling after seeing desired pseudo-Omega counts.
6. This is a smoke, not full atlas scale.
```

### Recommended module shape

```text
omega/val1_mf/__init__.py
omega/val1_mf/coupled_grammar.py
omega/val1_mf/metrics.py
omega/val1_mf/run_smoke.py
```

Re-use from VAL0-G where practical:

```text
GrammarWorld
GrammarState
valid_tasks
apply_task
geometry_metrics ideas
neutral bin reporting
runner output/checkpoint style
```

But do not mutate VAL0-G code into an unreadable general-purpose module unless necessary.

### Suggested development order

```text
1. Implement JointWorld / JointState.
2. Implement cross-field effect sampling.
3. Implement joint apply_task for A or B action.
4. Implement sampled joint rollout terminal/filter estimates.
5. Implement capped enumeration only if cheap.
6. Implement neutral compatibility bins.
7. Smoke 10 pairs before running 100-200 pairs.
```

## What this probe can and cannot claim

Can claim if successful:

```text
minimal two-field neutral coupling produces non-degenerate compatibility regimes,
including local-dominance and joint-viability-like bins.
```

Cannot claim:

```text
full Omega validation
true multifield axiology
alignment solution
actual field ontology established
```

## Keeping open Omega as an actual field

This toy substrate represents a field as a finite task-repertoire transition system.

It does not assert that real Omega is merely a graph.

A safe ontology ladder:

```text
toy field:
  finite task-repertoire transition system

proto-Omega field:
  recoverability geometry over possible transformations

actual Omega field, if real:
  physically instantiated compatibility / continuation structure across scales
```

The smoke is only about the first level.

## Bottom line

VAL1-MF should test the first multifield hypothesis:

```text
Coupling fields prunes high-mass single-field continuation into more informative
compatibility regimes, including pseudo-Omega-like local survival with broader
collapse and joint-viable-like mutual recoverability.
```

If this smoke works, the next step is a larger two-field compatibility atlas with sampled/cap-aware estimators.
