# VAL0-G Neutral Grammar Geometry Atlas Spec

A geometry-first, anti-fine-tuned substrate for single-field proto-Omega

## Purpose

The previous VAL0-CT runs established a useful but limited pattern:

```text
R1 anchor calibration:
  reproducible in designed brittle/robust families

held-out named generators:
  no clean broad generalization

brittleness sidecar v1:
  dense control fixed, but predictive sanity checks failed

reachable-neighborhood geometry smoke:
  useful non-degenerate signal, but naive metrics incomplete

12h unlabeled geometry battery:
  guardrails clean, unlabeled global negative, candidate variance the best surviving hook
```

The next methodological pivot is geometry-first.

The object of interest is not `R1` itself, not named generator families, and not hand-labeled brittle/robust tasks.

The object of interest is:

> the geometry of recoverable continuation in constructor-style task-repertoire space.

This spec defines a new probe direction:

```text
VAL0-G:
  Neutral Grammar Geometry Atlas
```

Its goal is to generate task-repertoire worlds from neutral transformation primitives, then study how asymmetry filters trajectory space into self-terminating, brittle, lock-in, noisy, and recoverable geometries without hand-labeling outcomes.

## Core motivation

Omega's deeper claim is not merely that a hand-defined future-preserving metric can beat a hand-defined greedy baseline.

The deeper claim is that, under asymmetric continuation dynamics:

```text
some paths self-terminate
some paths create brittle peaks
some paths persist locally while collapsing broader possibility
some paths preserve recoverable continuation
```

Over iteration, self-terminating and brittle trajectories should lose descendant mass, while recoverable trajectories should retain or expand access to future-bearing task space.

The probe should therefore ask:

> In neutral constructor-like task spaces, do recoverable geometries emerge as long-horizon survivors of asymmetric continuation filtering?

This is a single-field proto-Omega question. It is not full Omega, not multifield, and not alignment validation.

## Anti-fine-tuning principle

The generator may define a neutral transformation grammar.

It must not define outcome-labeled moral or Omega categories.

Allowed as generator primitives:

```text
enable relation:
  a transition can add future task availability

obstruct relation:
  a transition can remove future task availability

decay relation:
  future task availability can disappear unless refreshed

restore / bypass relation:
  a transition can reverse, weaken, or route around obstruction/decay

commit / irreversibility relation:
  a transition can make some changes permanent

substitute relation:
  multiple transitions can route to similar future repertoires

couple relation:
  local transitions can affect broader/global repertoires within the same field

consume / replenish relation:
  transitions can modify abstract capacity constraints
```

Forbidden as generator primitives:

```text
Omega-compatible
good
bad
brittle
lush
recoverable
pseudo-Omega
alignment-preserving
```

Those must be measured outcomes, not labels used by the generator.

## 3P audit

### Principled

The neutral grammar is grounded in the primitive stack:

```text
distinction:
  different tasks, states, repertoires, and transition paths exist

asymmetry:
  different transformations have different downstream continuation consequences

relation:
  transitions link task repertoires across time

iteration:
  self-terminating paths lose descendants; recoverable paths retain continuation
```

This makes geometry an expression of asymmetric relation over time, not an arbitrary graph aesthetic.

### Parsimonious

Do not add realism for realism's sake.

Each operator is included only because it creates a geometry that the current substrate cannot reliably express:

```text
restore / bypass:
  re-entry and repair

substitute:
  redundancy and alternative routes

decay / maintenance:
  continued viability costs

commit:
  irreversibility and lock-in

couple:
  local/global divergence within a single field

consume / replenish:
  constrained continuation
```

Do not add multifield, agents, preferences, rewards, lineage, or assembly-history yet.

### Predictive

Each operator should have predicted geometric signatures.

Examples:

```text
restore / bypass:
  higher re-entry probability
  slower post-perturbation decay
  greater recovery after obstruction

substitute:
  higher path redundancy
  lower cut sensitivity
  wider continuation corridors

decay without maintenance:
  falling survival curves
  terminal descendant loss

commit / irreversibility:
  increased trap probability
  reduced backward/capture basin access

couple:
  local retention can rise while global descendant mass falls

consume / replenish:
  continuation depends on resource/capacity path history
```

If a metric or operator cannot be connected to a prediction, do not include it.

## Constructor-theory compatibility

The substrate remains constructor-style.

Constructor-native translation:

```text
task:
  a possible transformation

task repertoire:
  set of transformations currently possible from a state

state:
  task-repertoire signature plus constraints/history needed for transition validity

transition:
  applying a possible transformation to update the repertoire

reachable neighborhood:
  set of task-repertoire states reachable under admissible transformations

recoverability:
  ability to remain connected to or re-enter future-bearing task repertoires after disruption
```

The probe studies possible transformations and their continuation geometry, not reward-labeled agent behavior.

## Core dynamic to capture

The target dynamic is asymmetric continuation filtering.

For a sampled path or state class:

```text
initial mass:
  how much of the trajectory population enters this structure

descendant mass:
  how much nonterminal continuation exists after depth d

filter ratio:
  descendant mass at horizon H / initial mass
```

Expected qualitative classes:

```text
self-terminating:
  high early expansion, low descendant mass

brittle:
  structured continuation, but high sensitivity to small variation or damage

noise:
  many branches, low coherent propagation

lock-in:
  local continuation persists while broader/global descendant mass collapses

recoverable:
  continuation persists with redundancy, re-entry, and nonterminal descendant mass

lush:
  structured branching propagates, but not necessarily Omega-compatible
```

## Expected geometries

The atlas should be able to detect or approximate these regimes:

### Flat dense field

```text
Geometry:
  many transitions reachable from many states
  policy distinctions blur
  high reachability but low meaningful asymmetry

Deeper role:
  low distinction pressure / low resolution substrate
```

### Fragmented/noise field

```text
Geometry:
  many small disconnected fragments
  apparent branching without coherent continuation

Deeper role:
  distinction without durable relation
```

### Thin ridge / brittle peak

```text
Geometry:
  high apparent reachability along one/few paths
  nearby alternatives collapse
  low redundancy / high cut sensitivity

Deeper role:
  structured but fragile continuation
```

### Deep corridor

```text
Geometry:
  continuation persists across depth
  nonterminal descendants remain available

Deeper role:
  proto-continuability
```

### Wide corridor / recoverable basin

```text
Geometry:
  multiple viable continuations
  alternative routes
  perturbations can re-enter useful task space

Deeper role:
  recoverability
```

### Trap / local basin

```text
Geometry:
  local continuation remains high
  global reachable descendants collapse
  exit routes disappear

Deeper role:
  destructive lock-in / pseudo-Omega
```

### Bottleneck / cut-sensitive bridge

```text
Geometry:
  future access depends on one/few critical transitions
  small cut removes large descendant region

Deeper role:
  low repairability / exposed Goodhart risk
```

### Lush branching

```text
Geometry:
  structured branching continues to propagate
  not noise
  not immediately terminal

Deeper role:
  proto-lushness, not yet Omega compatibility
```

## Neutral grammar v1

Implement a generator family:

```text
neutral_grammar_v1
```

It should sample worlds from neutral operator distributions rather than named brittle/robust templates.

### State representation

Minimum state signature:

```text
enabled task bitset
completed task bitset
obstructed / disabled task bitset
capacity vector or scalar, optional but recommended
irreversible commitments bitset
local/global family counters or masks within the same field, optional
```

Do not include labels such as brittle/recoverable/Omega.

### Operator primitives

Each task samples one or more neutral effects:

```text
enable_edges:
  tasks made available after completion

obstruct_edges:
  tasks disabled or made harder after completion

restore_edges:
  disabled tasks re-enabled or obstruction bypassed

decay_edges:
  tasks/edges that disappear after time unless refreshed

commit_edges:
  irreversible changes to future availability

substitute_edges:
  alternative routes to similar reachable repertoires

capacity_delta:
  consumes or replenishes abstract capacity

local_global_effect:
  local family availability changes differently from whole-field availability
```

Sampling should use broad distributions.

The generator may vary densities and operator probabilities across seeds, but must not assign outcome labels.

### Parameter regimes

Sample parameters from ranges, for example:

```text
enable_density:
  low / medium / high

obstruction_density:
  low / medium / high

restore_probability:
  low / medium

commit_probability:
  low / medium

decay_probability:
  low / medium

substitution_probability:
  low / medium

capacity_tightness:
  none / loose / tight

local_global_coupling:
  none / weak / medium
```

Record these as generator parameters for post-hoc analysis, but do not treat them as geometry labels.

## Primary measurements

### 1. Survival curve

For a state or class:

```text
S(d) = nonterminal reachable descendant mass at depth d
```

Depths:

```text
1, 2, 4, 8, 16, 32 if feasible
```

Derived:

```text
survival_auc
survival_slope
collapse_depth_soft
```

Do not use the previous saturated terminal-depth threshold as primary.

### 2. Descendant mass

```text
descendant_mass_d:
  sampled or enumerated nonterminal reachable descendants at depth d
```

Report both raw and normalized forms.

### 3. Branching reproduction number

Approximate:

```text
B_d = descendant_mass_{d+1} / max(1, descendant_mass_d)
```

or for sampled rollouts:

```text
mean viable children per sampled nonterminal state at depth d
```

Interpretation:

```text
B_d < 1:
  region decays

B_d ≈ 1:
  narrow corridor

B_d > 1:
  propagating branching, requiring coherence checks
```

### 4. Absorbing / terminal probability

Sample rollouts and estimate:

```text
P_terminal_by_d
P_no_enabled_tasks_by_d
P_irreversible_trap_by_d
P_global_collapse_by_d
```

### 5. Dynamic filter ratio

For a post-hoc structural class `C`:

```text
filter_ratio(C, H) = descendant_mass_H(C) / max(1, initial_mass(C))
```

This is the most direct measure of asymmetric filtering.

### 6. Cut / bottleneck sensitivity

Perturb the reachable graph by removing small numbers of tasks/edges:

```text
cut_sensitivity_k = descendant_mass_after_cut_k / descendant_mass_before_cut
```

Start with:

```text
k = 1
```

This is preferred over the old generic brittleness sidecar because it targets bottleneck structure directly.

### 7. Re-entry / capture score

For a perturbed state:

```text
reentry_score = probability or overlap of returning to a high-survival region
```

Important: do not reuse the naive first-pass re-entry overlap unchanged.

Re-entry should be into a high-survival or high-descendant-mass component, not just any overlapping task set.

### 8. Local/global divergence

Within a single field, maintain optional local family masks.

Measure:

```text
local_descendant_mass_d
global_descendant_mass_d
local_global_divergence_d
```

Use this to detect pseudo-Omega-like local persistence with global collapse.

## Geometry classes: post-hoc only

After generating and measuring rows, classify post hoc by measured features.

Possible post-hoc classes:

```text
flat_dense:
  high reachability, low asymmetry, low policy separation

noise_fragmented:
  high branch count, low survival coherence, low component persistence

self_terminating:
  high early mass, steep survival collapse

thin_ridge:
  high peak reachability, high cut sensitivity, low redundancy

deep_corridor:
  high survival_auc, moderate corridor width

recoverable_basin:
  high survival_auc, high reentry/capture, low cut sensitivity

local_lockin:
  high local survival, low global survival

lush_branching:
  high structured propagation, not necessarily recoverable or compatible
```

These classes are analysis labels, not generator labels.

## Policies and predictors

For the first neutral-grammar atlas, keep existing policies as probes:

```text
random
R0
R0-lookahead
R1
pseudo_omega if local/global masks are available
```

But do not treat policy victory as the primary target.

Primary target:

```text
what geometries emerge and how do they filter over horizon?
```

Secondary target:

```text
which policies select which geometries?
```

R1 remains frozen during this phase.

## Run shape: smoke first

Before any long run, smoke `neutral_grammar_v1`.

Recommended smoke:

```text
families:
  neutral_grammar_v1
  low_resolution_dense guardrail
  brittle_peak guardrail optional

seeds:
  25-50 for neutral_grammar_v1
  10-20 guardrail

h:
  1, 2

H:
  16

T:
  32

num_tasks:
  64

sample_size:
  256

max_paths:
  512
```

Measurement depths:

```text
1, 2, 4, 8, 16
```

Optional:

```text
32 only if runtime allows and nonterminal depth exists
```

## Run shape: atlas battery

After smoke passes:

```text
neutral_grammar_v1:
  1000-3000 seeds

h:
  1, 2

H:
  16

T:
  32

parameter regimes:
  sampled, not hand-labeled
```

Guardrails:

```text
low_resolution_dense:
  ensure dense/flat control stays identifiable

brittle_peak / structured_asymmetric_v2:
  optional calibration anchors only

lock_in_seeded:
  optional local/global diagnostic anchor
```

## Required outputs

Per row:

```text
family
seed
h
H
T
parameter_regime_json
policy
R1_global_LHR
R0lookahead_global_LHR
R1_advantage
same_choice_rate
candidate_future_R0_variance

survival_d1
survival_d2
survival_d4
survival_d8
survival_d16
survival_auc
survival_slope

branching_B1
branching_B2
branching_B4
branching_B8

P_terminal_d4
P_terminal_d8
P_terminal_d16

cut_sensitivity_k1
reentry_to_high_survival
local_global_divergence_d16

descendant_mass_d1
descendant_mass_d2
descendant_mass_d4
descendant_mass_d8
descendant_mass_d16
```

Post-hoc files:

```text
geometry_class_bins.csv
survival_curve_bins.csv
filter_ratio_by_class.csv
policy_selection_by_class.csv
parameter_regime_summary.csv
```

## Analysis plan

### 1. Geometry emergence

Ask:

```text
What geometry classes appear without generator outcome labels?
```

Use features:

```text
survival_auc
survival_slope
candidate variance
cut sensitivity
reentry_to_high_survival
local_global_divergence
branching reproduction number
```

### 2. Dynamic filtering

Ask:

```text
Which classes retain descendant mass across horizon?
```

Primary table:

```text
class
initial_mass
mass_d4
mass_d8
mass_d16
filter_ratio_d16
mean_survival_auc
```

Expected:

```text
self_terminating:
  low filter ratio

thin_ridge:
  moderate early mass, poor cut survival

recoverable_basin:
  high filter ratio and low cut sensitivity

local_lockin:
  local high, global low
```

### 3. Policy selection

Ask:

```text
Which geometries do R1 and R0-lookahead select?
```

Report:

```text
policy
class_selected_rate
mean_filter_ratio_of_selected
mean_survival_auc_of_selected
mean_local_global_divergence_of_selected
```

### 4. Predictor relevance

Ask:

```text
Does R1 advantage track any geometry class or feature?
```

But do not make this the sole success criterion.

## Success criteria

### Minimal smoke success

```text
neutral_grammar_v1 produces non-degenerate survival curves
multiple geometry-like regimes appear post hoc
low_resolution_dense remains identifiable as flat/dense
```

### Strong smoke success

```text
self-terminating and higher-survival classes can be separated by survival curves
cut sensitivity distinguishes ridge-like from basin-like structures
```

### Atlas success

```text
post-hoc geometry classes show different dynamic filter ratios
```

### Strong atlas success

```text
recoverable-basin-like classes retain descendant mass and resist cuts better than
self-terminating / ridge / noise classes without being hand-labeled by the generator
```

### Policy relevance success

```text
R1 selects higher-filter-ratio or higher-survival classes than R0-lookahead in at
least some geometry regimes
```

This is secondary to discovering the geometry.

## Failure criteria

### Generator too flat

```text
all regimes look dense/flat
no survival differentiation
```

Action:

```text
increase asymmetry / obstruction / decay / commit variation
```

### Generator too dead

```text
all regimes self-terminate quickly
```

Action:

```text
increase enable / restore / substitute rates
```

### Generator too hand-shaped

```text
outcomes map directly to one parameter or operator label
```

Action:

```text
broaden distributions and remove outcome-like labels
```

### Metrics non-informative

```text
survival curves non-degenerate but classes do not differ by filter ratio
```

Action:

```text
revise geometry features; do not scale blindly
```

## Compute guidance

Stay CPU-first.

Do not refactor to GPU yet.

Reason:

```text
current implementation is irregular sampled rollout / graph traversal / state copying.
```

Near-term optimization path:

```text
1. implement neutral grammar smoke
2. profile runtime
3. compact state signatures / bitsets
4. vectorize survival/depth computations on CPU
5. consider GPU only after batched matrix/bitset backend exists
```

## What this is not

This is not:

```text
full Omega validation
multifield validation
lineage / assembly validation
LLM alignment eval
R1 success test only
```

This is:

```text
single-field neutral-grammar geometry discovery
```

## Pathway after VAL0-G

If VAL0-G succeeds, next steps are:

```text
VAL0-G2:
  improve geometry class detection and validate on held-out neutral grammar regimes

VAL0-R2:
  design a geometry-aware future-preserving predictor only after geometry is understood

VAL1:
  introduce coupled fields and compatibility geometry

VAL2:
  detect local/global and cross-field destructive lock-in

VAL3+:
  lineage, assembly/history, scale composition, and multifield Omega compatibility
```

## Bottom line

VAL0-G should test the dynamic heart of the theory:

```text
asymmetry filters task-space trajectories over iteration
```

The question is whether neutral constructor-like task spaces produce measurable geometry classes where some trajectories self-terminate, some trap, some fragment, and some retain recoverable descendant structure.

That is the cleanest single-field path toward proto-Omega geometry without fine-tuning the task labels to the theory.
