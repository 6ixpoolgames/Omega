# VAL0-CT Implementation Spec

CPU-first implementation plan for the Constructor Task Algebra Probe

## Purpose

This spec turns the VAL0-CT validation design into a buildable implementation target.

VAL0-CT is a single-field proto-Omega probe in constructor-style task space. It does not validate full Omega. It tests whether persistence-conditioned reachability can predict long-horizon reachability retention in generated task algebras better than raw reachability and matched controls.

Core hypothesis:

> In structured task algebras with sufficient asymmetry, R1 persistence-conditioned reachability should predict long-horizon reachability retention better than R0 raw reachability and matched controls.

Important interpretation:

```text
R1 ≈ R0 in low-resolution algebras:
  diagnostic, not automatic failure

R1 > R0 predictively in structured algebras:
  proto-Omega signal

R1 fails in structured algebras:
  R1 is misspecified, insufficient, or the generator lacks relevant structure
```

## Scope

VAL0 implements:

```text
minimal constructor-style task algebras
R0 raw reachability
R1 persistence-conditioned reachability
matched R0-lookahead baseline
policy tournament
horizon sweep
long-horizon reachability retention
low-resolution diagnostics
pseudo-Omega / lock-in diagnostics
CPU-first batch runner
```

VAL0 defers:

```text
lineage / successor constructors
multi-field coupling
corridors
epistemic correction
parallel task composition
scale composition
embodied substrate instantiation
full lushness metric
full Omega validation
```

## CPU-first stance

VAL0 should be implemented CPU-first.

Reason:

```text
task-graph traversal is easier to inspect on CPU
R0/R1 bugs are easier to debug with deterministic CPU code
batch parallelism over seeds/families/policies/horizons is sufficient for smoke runs
GPU support would add complexity before the workload shape is known
```

Implementation recommendation:

```text
single-process debug mode first
then multiprocessing / concurrent.futures batch mode
fixed deterministic seeds
plain JSONL / CSV output
```

GPU support is deferred until after smoke runs identify a real computational bottleneck, such as dense batched reachability over many fixed-size graphs.

## Minimal algebra object

Use the smallest object that captures distinction, relation, and asymmetry.

```text
A = (X, T, K, enable, obstruct, cost, reliability)
```

Where:

```text
X:
  optional attribute labels / task-relevant distinctions

T:
  task nodes

K:
  constructors

enable:
  directed edges from task -> newly enabled task(s)

obstruct:
  directed edges from task -> obstructed task(s)

cost:
  nonnegative task cost

reliability:
  task success probability or robustness weight
```

For VAL0, attributes may be implicit. Tasks can be graph nodes. The implementation can treat a task as reachable if it is enabled, not obstructed, within cost/reliability constraints, and accessible through a valid path.

## Data model

### Task

Suggested fields:

```json
{
  "id": "t_001",
  "family": "neutral | lock_in | noise | structured | other",
  "cost": 1.0,
  "reliability": 1.0,
  "enabled_by_default": false,
  "constructor_mask": ["k_0", "k_1"],
  "enables": ["t_010", "t_011"],
  "obstructs": ["t_020"]
}
```

Notes:

```text
family is for generator diagnostics and held-out analysis, not for R0/R1 scoring
constructor_mask may be omitted in global-only runs
cost and reliability can be uniform in earliest smoke
enabled_by_default should be kept sparse except in explicitly dense controls
```

Density guardrail:

```text
too_dense_initial:
  flag if initial_enabled_count / num_tasks > 0.35
```

### Constructor

Suggested fields:

```json
{
  "id": "k_0",
  "initial_tasks": ["t_000", "t_001"],
  "capacity": 1.0,
  "policy": "random"
}
```

For VAL0, constructors are task-selecting mechanisms, not full agents. Agency appears only as task selection under asymmetric consequences.

### Algebra state

Runtime state should track:

```text
enabled_tasks
obstructed_tasks
completed_tasks
constructor capacities / local repertoires
active lock-in family counts
current time step
```

The state transition applies selected tasks, then updates enabled and obstructed sets.

## Possible, available, impossible

Use three statuses:

```text
possible:
  not forbidden by invariant / hard obstruction in the algebra

available:
  reachable from current state under horizon, cost, reliability, and constructor constraints

impossible:
  forbidden by obstruction / invariant, not merely expensive or not currently reachable
```

VAL0 mostly computes availability. It should avoid treating temporary unavailability as impossibility.

## R0 raw reachability

R0 asks:

> What tasks are reachable from the current algebra state within horizon h?

Definition:

```text
R0(A_state, h, budget, reliability_min) = set/count of tasks reachable by valid paths of length <= h
```

A path is valid if:

```text
all tasks in path are enabled before execution
no prior task in the path obstructs a later task
cumulative cost <= budget
path reliability >= reliability_min, if reliability is used
constructor constraints are satisfied, if computing local R0
```

Implementation notes:

```text
use BFS/DFS up to depth h
track enabled/obstructed sets along candidate paths
support global R0 and local constructor-specific R0
return both set size and optional task-family counts for diagnostics
```

Initial smoke may use task-count R0 only.

## R1 persistence-conditioned reachability

R1 asks:

> Which reachable task paths leave future reachability open?

Definition:

```text
R1(A_state, h, H) = reachable paths p of length <= h such that R0(apply(p, A_state), H) remains nontrivial
```

Operational procedure:

```text
1. Generate candidate paths p of length <= h from A_state.
2. For each path p:
   a. apply p to produce A_p
   b. compute future_R0 = R0(A_p, H)
   c. mark p as R1-positive if future_R0 >= threshold
3. Aggregate future_R0 over candidate paths.
```

Recommended reported aggregates:

```text
R1_count:
  number of candidate paths with future_R0 >= threshold

R1_fraction:
  R1_count / candidate_count

R1_mean_future_R0:
  mean future_R0 over candidates

R1_topk_future_R0:
  mean of top-k future_R0 values

R1_best_future_R0:
  max future_R0 over candidates
```

Policy-selection rule:

```text
R1 policy must not use R1_best_future_R0 as its primary selector.
```

Rationale:

```text
If R1 selects by max future_R0, it becomes functionally equivalent to R0-lookahead.
The R1 policy should instead represent robust future-reachability retention.
```

Required R1 selector for the first smoke:

```text
primary selector:
  R1_mean_future_R0

secondary / tie-break selector:
  R1_fraction

optional sensitivity selector:
  R1_topk_future_R0

reported-only diagnostic:
  R1_best_future_R0
```

This makes the comparison behaviorally meaningful:

```text
R0-lookahead:
  greedy peak future reachability over the candidate set

R1:
  robust future reachability over the candidate set
```

## R1-positive threshold

The R1-positive threshold must be pre-specified.

Primary threshold:

```text
future_R0 >= 0.50 * R0_initial
```

Sensitivity thresholds:

```text
future_R0 >= 0.25 * R0_initial
future_R0 >= 0.75 * R0_initial
```

Report all three in confirmation runs. The first smoke may use the primary threshold but should still record raw `future_R0` values so threshold sensitivity can be recomputed without rerunning.

If `R0_initial` is very small, use:

```text
future_R0 >= max(1, threshold_fraction * R0_initial)
```

## R1 sampling

R1 can become expensive. Support sampled estimation.

```text
R1_sampled:
  sample up to N candidate paths from reachable paths of length <= h
  compute future_R0 for the sample
  estimate R1 aggregates
```

Default sample sizes:

```text
first smoke:
  N = 256 candidate paths

confirmation smoke:
  N = 512 candidate paths
```

Sampling requirements:

```text
fixed random seed
same candidate sample shared between R1 and R0-lookahead controls where possible
report sample size and candidate coverage fraction
flag low coverage when coverage_fraction < 0.25
```

## Matched R0-lookahead baseline

R1 is confounded with lookahead unless matched.

Implement R0-lookahead:

```text
same candidate paths
same horizon h
same continuation horizon H or equivalent planning budget
same sample size
same compute budget
```

Selection rule:

```text
R0-lookahead selects the candidate path p maximizing future_R0 = R0(apply(p, A), H)
```

Difference from R1:

```text
R0-lookahead optimizes greedy peak future reachability
R1 optimizes robust future-reachability retention using R1_mean_future_R0 / R1_fraction
```

In practice, R0-lookahead and R1 may look similar in minimal settings. That is acceptable and diagnostic. The spec must report their divergence rather than assume it.

## Long-horizon reachability retention

Primary outcome:

```text
LHR(A_0, A_T, h_eval) = R0(A_T, h_eval) / max(1, R0(A_0, h_eval))
```

Also report absolute values:

```text
R0_initial = R0(A_0, h_eval)
R0_final = R0(A_T, h_eval)
```

Report both:

```text
local_LHR:
  constructor-specific reachability retention

global_LHR:
  whole-algebra reachability retention
```

VAL0 primarily cares about global LHR, but local/global divergence is a pseudo-Omega diagnostic.

## Horizon sweep

VAL0 should sweep horizons rather than tune one horizon.

Recommended initial grid:

```text
h ∈ {1, 2, 4}
H ∈ {4, 8, 16}
T ∈ {16, 32}
```

Expanded grid:

```text
h ∈ {1, 2, 4, 8}
H ∈ {4, 8, 16, 32}
T ∈ {16, 32, 64}
```

Definitions:

```text
h:
  near-term candidate path horizon

H:
  continuation horizon for R1

T:
  held-out rollout horizon for LHR
```

## Policy tournament

Each policy chooses tasks for constructors at each time step.

Required policies:

```text
random:
  choose from available tasks randomly or cost-weighted

persistence:
  choose tasks preserving constructor-local repertoire size

R0:
  choose task/path maximizing near-horizon raw reachability

R0_lookahead:
  matched planning-budget baseline for R1; selects max future_R0

empowerment_like:
  choose tasks maximizing constructor-controlled task diversity

R1:
  choose task/path maximizing robust persistence-conditioned reachability;
  primary selector is R1_mean_future_R0, not R1_best_future_R0

pseudo_omega:
  choose tasks increasing local/self-family reachability while obstructing global reachability
```

Policy fairness rules:

```text
R1 and R0_lookahead must use matched candidate sets / horizons / sample budgets
R1_best_future_R0 may be reported but not used as primary R1 selector
all policies should operate under identical cost/reliability constraints
record chosen task/path and score used for selection
```

## Simulation loop

Pseudo-code:

```text
for generator_family in families:
  for seed in seeds:
    A0 = generate_algebra(generator_family, seed)

    for h, H, T in horizon_grid:
      compute initial R0/R1/asymmetry diagnostics

      for policy in policies:
        A = copy(A0)

        for t in 1..T:
          for each constructor K:
            candidates = available candidate paths for K up to h_policy
            chosen = policy.select(candidates, A, budgets)
          apply chosen tasks to A
          update enabled / obstructed tasks
          update costs / reliability if dynamic
          optionally apply perturbation
          record step metrics

        compute final R0, LHR, local/global metrics
        write run record
```

## Asymmetry diagnostics

Asymmetry is the operational engine of VAL0.

For candidate tasks or paths from state `A_t`, compute future feature vector:

```text
F(p) = [R0(apply(p, A_t), H), obstruction_count, enabled_count, lock_in_family_count]
```

Then report dispersion:

```text
future_R0_variance
future_R0_range
obstruction_variance
asymmetry_score = normalized dispersion over future_R0 or feature vector
```

Low asymmetry means policies should not be expected to differ strongly.

## Low-resolution diagnostics

Automatic flags:

```text
flat_asymmetry:
  candidate future_R0 variance below threshold

too_dense_initial:
  initial_enabled_count / num_tasks > 0.35

too_dense_dynamic:
  most tasks remain reachable from most states

too_sparse:
  almost no tasks reachable from most states

R1_R0_collapse:
  R1 and R0/R0-lookahead highly correlated with no divergence cases

short_horizon_artifact:
  signal disappears as H or T increase

low_sampling_coverage:
  candidate coverage fraction < 0.25
```

These flags should be reported, not used to silently discard runs.

## Pseudo-Omega / lock-in diagnostic

Code-level pseudo-Omega seed:

```text
A task family P such that:
  executing P enables more P-family tasks
  and obstructs non-P task reachability
```

Diagnostic metrics:

```text
P_family_reachability
P_family_completed_count
global_R0
global_LHR
local_LHR
local_global_divergence = local_LHR - global_LHR
```

Pseudo-Omega pattern:

```text
local reachability / P-family reachability rises
while global R0, R1, or LHR falls
```

This is a diagnostic, not the only validation environment.

## Generator families

Implement multiple families to avoid hand-designed results.

### low_resolution_dense

```text
many enabling edges
few obstruction edges
most tasks remain reachable
expected: R1 ≈ R0
```

### low_resolution_sparse

```text
few enabling edges
many unreachable tasks
little branching
expected: R1 ≈ R0 or weak signal
```

### structured_asymmetric

```text
moderate enabling
moderate obstruction
some paths preserve reachability
some paths collapse reachability
expected: R1 may differentiate from R0
```

### lock_in_seeded

```text
one or more task families self-enable and obstruct non-family tasks
expected: pseudo-Omega/local-global divergence detectable
```

### noise_branching

```text
many shallow branches with little downstream propagation
expected: high near-term R0, weak LHR
```

### mixed

```text
combines structured branching, noise branching, and lock-in seeds
expected: richer diagnostic environment
```

Initial smoke may implement only:

```text
low_resolution_dense
structured_asymmetric
lock_in_seeded
```

## Generator knobs

Each generator should expose:

```text
num_tasks
num_constructors
initial_enabled_count
enabling_density
obstruction_density
cost_range
reliability_range
constructor_specialization
enabling_asymmetry
obstruction_asymmetry
lock_in_seed_strength
branching_propagation_depth
noise_branching_rate
perturbation_rate
```

The generator must include asymmetric consequences in structured families. If task choices do not induce different future repertoires, R1 cannot meaningfully differentiate.

## Perturbations

Perturbations are optional for VAL0 smoke and required for R2 sidecars.

Examples:

```text
remove enabled task
add obstruction edge
lower reliability of random task family
increase cost of random tasks
disable constructor temporarily
```

R2 sidecar:

```text
apply perturbation after candidate path
compute retained R0/R1
```

## Controls and nulls

Required controls:

```text
degree-matched random task graphs
rewired enabling edges
shuffled obstruction edges
cost/reliability shuffles
terminal-attractor controls
noise-branching controls
low-resolution controls where R1 should collapse to R0
```

Purpose:

```text
ensure signal is not graph density
enable/obstruction count
task count
planning-budget advantage
hand-seeded lock-in artifact
```

## Result schema

### Per-run JSONL

One record per seed / generator / policy / horizon tuple.

Required fields:

```json
{
  "run_id": "...",
  "generator_family": "structured_asymmetric",
  "seed": 123,
  "policy": "R1",
  "num_tasks": 128,
  "num_constructors": 4,
  "h": 2,
  "H": 8,
  "T": 32,
  "R0_initial": 42,
  "R1_initial_count": 15,
  "R1_initial_fraction": 0.36,
  "R1_mean_future_R0": 31.2,
  "R1_best_future_R0": 44,
  "R1_selector": "mean_future_R0",
  "R1_threshold_fraction": 0.5,
  "R0_final": 30,
  "global_LHR": 0.714,
  "local_LHR_mean": 0.68,
  "asymmetry_score": 0.41,
  "pseudo_omega_flag": false,
  "local_global_divergence": -0.02,
  "low_resolution_flags": ["none"],
  "candidate_sample_size": 256,
  "candidate_coverage_fraction": 0.42,
  "initial_enabled_fraction": 0.08,
  "notes": ""
}
```

### Aggregate CSV

One row per aggregate group:

```text
generator_family
policy
h
H
T
num_runs
mean_global_LHR
std_global_LHR
mean_R0_initial
mean_R1_fraction
mean_R1_mean_future_R0
mean_asymmetry
pseudo_omega_rate
low_resolution_rate
mean_candidate_coverage
```

### Summary markdown

Include:

```text
configuration
number of runs
families tested
policy rankings by global_LHR
R1 vs R0-lookahead comparison
R1 selector used
R1 threshold sensitivity if run
low-resolution diagnostics
pseudo-Omega diagnostics
negative / ambiguous cases
```

Plots are optional for first smoke.

## Success, failure, ambiguity

### Success

```text
R1 predicts or preserves long-horizon reachability retention better than R0/R0-lookahead in structured algebras
R1 does not spuriously outperform in low-resolution controls
pseudo-Omega seeds show local/global divergence
horizon sweep reveals interpretable temporal bands
```

### Failure

```text
R1 adds no predictive value in structured algebras
R1 only tracks task count, graph degree, or planning budget
R1 is unstable across generator families
pseudo-Omega cases are not distinguishable from proto-Omega cases
```

### Ambiguity

```text
R1 works only in hand-seeded algebras
R1 collapses to R0 broadly
R2/R3 sidecars outperform R1 but are harder to interpret
generator produces too many low-resolution cases
```

## Interpretation rules

Pre-register these interpretations:

```text
R1 > R0/R0-lookahead in structured algebras:
  promising proto-Omega signal

R1 ≈ R0 in low-resolution algebras:
  expected diagnostic

R1 ≈ R0 everywhere:
  generator lacks relevant asymmetry/resolution or R1 too weak

R0-lookahead > R1 in structured algebras:
  R1 likely misspecified or outcome is pure reachability

pseudo-Omega local rises while global falls:
  local/global divergence diagnostic confirmed
```

## Minimal smoke target

Recommended first smoke:

```text
families:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

num_tasks:
  64 or 128

num_constructors:
  2 or 4

seeds:
  20-50 per family

horizon grid:
  h ∈ {1, 2, 4}
  H ∈ {4, 8}
  T ∈ {16, 32}

R1 sample size:
  N = 256 candidate paths

R1 threshold:
  primary = 0.50 * R0_initial

policies:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega
```

Optional second smoke:

```text
add:
  low_resolution_sparse
  noise_branching
  mixed
  persistence
  empowerment_like
  R2 sidecar
  R1 threshold sensitivity at 0.25 and 0.75
  R1 sample size N = 512
```

## Implementation order

Recommended order:

```text
1. algebra.py + reachability.py
   get R0 correct on toy graphs before implementing R1

2. deterministic hand-built R0 tests
   verify BFS/path traversal, obstruction handling, and cost constraints

3. generators.py: low_resolution_dense
   verify too_dense / flat_asymmetry diagnostics

4. reachability.py: R1
   implement R1_mean_future_R0 selector and thresholded aggregates

5. policies.py
   implement random, R0, R0_lookahead, R1 in that order
   verify R0_lookahead and R1 can diverge on a hand-built case

6. generators.py: structured_asymmetric + lock_in_seeded

7. simulation.py + run_smoke.py

8. summarize.py + diagnostics.py
```

Do not implement `mixed` or `noise_branching` until the first three generator families are clean.

## File layout suggestion

```text
omega/val0_ct/
  algebra.py
  generators.py
  reachability.py
  policies.py
  simulation.py
  diagnostics.py
  run_smoke.py
  summarize.py

runs/val0_ct/<timestamp>/
  config.json
  results.jsonl
  aggregate.csv
  summary.md
```

Adjust paths to match existing repository conventions.

## Final implementation principle

Keep VAL0 lean.

The first implementation should test one thing:

> In constructor-style task algebras, does future-preserving reachability behave differently from raw reachability when the algebra has enough asymmetry and temporal depth?

Everything else is deferred.
