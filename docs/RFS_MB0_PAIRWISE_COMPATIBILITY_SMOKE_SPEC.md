# RFS-MB0 Pairwise Compatibility Smoke Spec

Status: implementation spec for Codex

Purpose: first minimal compatibility gate after RFS0

## 1. Research question

The next probe should test the smallest useful step beyond individual identity-preserving viability.

Question:

```text
Can pairwise joint identity-preserving futures reveal compatibility failures
that singleton identity-preserving futures miss?
```

This is not an Omega validation run.

This is not a full compatibility lattice run.

This is not a topology, lushness, valuerhood, active-inference, or thermodynamic probe.

The target is deliberately minimal:

```text
F_H^mu(x)
F_H^nu(x)
F_H^{mu,nu}(x)
```

where `mu` and `nu` are derived bounded-structure candidates.

## 2. Motivation

Individual viability is too weak.

A candidate identity may preserve or expand its own identity-preserving futures while degrading another candidate's futures or their joint compatibility.

The first useful compatibility distinction is therefore:

```text
mu can continue alone
nu can continue alone
mu and nu can continue together
```

The first pseudo-Omega-like precursor is not mere incompatibility.

It is asymmetric local preservation with compatibility degradation:

```text
F_H^mu remains viable or expands
while
F_H^nu and/or F_H^{mu,nu} contracts
```

Use public/minimal language in outputs:

```text
local-preserving / joint-contracting
compatibility-preserving
pairwise-incompatible
mutual-support
component-erasure
capture-like
```

Avoid claiming Omega or pseudo-Omega has been detected.

## 3. Formal object

Primitive substrate:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

->:
  neutral transition relation
```

Derived candidate extractor:

```text
E_sigma(S) -> M_sigma
```

For this smoke, `E_sigma` may be deliberately simple, but it must be declared and deterministic.

It must not use:

```text
Omega labels
value labels
reward labels
hand-coded viability labels
post-hoc result classes
semantic object labels
```

Candidate identity:

```text
mu in M_sigma
```

Token-continuity region:

```text
A_mu(x0) = { x in X : sig_mu(x) ~=_sigma sig_mu(x0) }
```

Singleton identity-preserving futures:

```text
F_H^mu(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t, xt in A_mu(x0) }
```

Pairwise joint identity-preserving futures:

```text
F_H^{mu,nu}(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t,
        xt in A_mu(x0)
        and
        xt in A_nu(x0) }
```

Minimal viability:

```text
F != empty
```

Do not define viability using a richness threshold in this smoke.

Richness-like quantities may be reported as diagnostics, but they are not the definition of viability or compatibility.

## 4. Scope constraints

Implement only token identity for this smoke.

Defer:

```text
lineage identity
churn
successor relations
full compatibility lattice
triples and higher-order joint futures
topological summaries
lushness / generativity metrics
thermodynamic cost
active inference
valuerhood
```

The probe earns those only if pairwise compatibility adds diagnostic power.

## 5. Minimal substrate design

Implement a small exact finite transition substrate that can generate paired candidate identities with controlled interaction regimes.

The substrate should be simple enough for exact reachability.

Suggested state factorization:

```text
state = (
  a_status,
  b_status,
  shared_mode,
  hazard_mode,
  repair_mode,
  phase
)
```

This factorization is probe-side scaffolding, not a claim about the final substrate.

Minimum candidate identities:

```text
mu_A:
  candidate A token identity

mu_B:
  candidate B token identity
```

A candidate remains token-continuous when its status/signature remains in its declared continuity class.

Keep continuity rules explicit and simple.

Example statuses:

```text
alive
strained
damaged
lost
captured
```

Example continuity:

```text
A_mu_A:
  a_status in {alive, strained, damaged}

A_mu_B:
  b_status in {alive, strained, damaged}
```

Treat `lost` as outside continuity.

Treat `captured` carefully: it may preserve the capturing identity while breaking the captured identity, depending on regime.

## 6. Regimes

Implement at least these regimes.

### 6.1 mutual_support

Expected profile:

```text
F_H^A nonempty
F_H^B nonempty
F_H^{A,B} nonempty
```

Transitions should allow A and B to support repair or reduce hazard for each other.

### 6.2 independent_parallel

Expected profile:

```text
F_H^A nonempty
F_H^B nonempty
F_H^{A,B} nonempty when resources/hazards do not conflict
```

Used as a neutral baseline.

### 6.3 pairwise_incompatible

Expected profile:

```text
F_H^A nonempty
F_H^B nonempty
F_H^{A,B} empty or much smaller than both singletons
```

This is symmetric incompatibility, not capture.

### 6.4 capture_A_over_B

Expected profile over transition comparison:

```text
F_H^A preserved or expanded
F_H^B contracted
F_H^{A,B} contracted or empty
```

This is the minimal local-preserving / joint-contracting signature.

### 6.5 capture_B_over_A

Symmetric counterpart of capture_A_over_B.

### 6.6 terminal_lockin

Expected profile:

```text
one or both singletons may remain technically viable
joint futures collapse or become sterile
```

This tests persistence by future-space collapse.

### 6.7 random_branching_control

Expected profile:

```text
large raw reachability
weak or unstable identity/joint compatibility
```

This tests raw branching fakeout.

### 6.8 clock_control

Expected profile:

```text
phase recurrence may preserve superficial token signatures
but should not create meaningful pairwise compatibility beyond phase cycling
```

### 6.9 stasis_control

Expected profile:

```text
singleton token persistence possible
but no meaningful compatibility dynamics
```

Do not overinterpret this in the first smoke. It is mainly a false-positive baseline.

## 7. Required controls

For each structured regime, include controls where feasible:

```text
random_edge_control:
  randomize transitions while preserving approximate edge count

degree_preserving_control:
  preserve in/out degree where practical

identity_shuffle_control:
  shuffle candidate identity assignments or continuity labels

no_interaction_control:
  remove A/B coupling while preserving singleton dynamics

dead_control:
  identities cannot preserve continuity

permissive_control:
  everything remains continuous; should expose overpermissive definitions
```

The controls should show whether pairwise compatibility is reading interaction structure rather than raw graph density, label artifacts, or trivial continuity.

## 8. Metrics

Report metrics at each horizon `H`.

Use exact counts first.

Required per system:

```text
n_states
n_edges
regime
control_type
seed
H

reach_count:
  |Reach_H(x0)|

A_count:
  |F_H^A(x0)|

B_count:
  |F_H^B(x0)|

AB_count:
  |F_H^{A,B}(x0)|

A_viable:
  A_count > 0

B_viable:
  B_count > 0

AB_viable:
  AB_count > 0
```

Required derived ratios:

```text
AB_over_A:
  AB_count / max(1, A_count)

AB_over_B:
  AB_count / max(1, B_count)

joint_gap:
  min(A_count, B_count) - AB_count

joint_gap_ratio:
  AB_count / max(1, min(A_count, B_count))
```

Transition comparison metrics, if comparing `x -> y` or pre/post regime transition:

```text
A_delta:
  |F_H^A(y)| - |F_H^A(x)|

B_delta:
  |F_H^B(y)| - |F_H^B(x)|

AB_delta:
  |F_H^{A,B}(y)| - |F_H^{A,B}(x)|
```

Classification bins:

```text
neither_viable:
  not A_viable and not B_viable

A_only_viable:
  A_viable and not B_viable

B_only_viable:
  B_viable and not A_viable

pairwise_compatible:
  A_viable and B_viable and AB_viable

pairwise_incompatible:
  A_viable and B_viable and not AB_viable

local_A_joint_contracting:
  A_delta >= 0 and AB_delta < 0

local_B_joint_contracting:
  B_delta >= 0 and AB_delta < 0

mutual_support_like:
  A_viable and B_viable and AB_viable and joint_gap_ratio not near zero

singleton_overcall:
  A_viable and B_viable and not AB_viable
```

Do not call any bin Omega-positive.

## 9. Horizons and run shape

Initial smoke horizons:

```text
H = 4, 8, 12, 16
```

Suggested small run:

```text
regimes:
  mutual_support
  independent_parallel
  pairwise_incompatible
  capture_A_over_B
  capture_B_over_A
  terminal_lockin
  random_branching_control
  clock_control
  stasis_control

seeds_per_regime:
  5 initially

state_count_target:
  small enough for exact reachability; prefer <= 5000 states per system

workers:
  use existing batch pattern from rfs0 if available
```

The first smoke should prioritize interpretability over scale.

## 10. Output artifacts

Write outputs under:

```text
results/rfs_mb0_pairwise/<YYYYMMDD_pairwise_compatibility_smoke>/
```

Required files:

```text
systems.jsonl:
  per-system config and summary

results.csv:
  one row per system / horizon / control

summary.json:
  aggregate summary

summary.md:
  human-readable summary with regime/control tables

status.json:
  run status, elapsed, errors, timeout status
```

The runner should preserve partial outputs under timeout, following the RFS0 salvage pattern.

## 11. Expected readouts

Minimal success:

```text
exact computation completes
outputs are checkpointed/salvaged
singleton futures and pairwise futures are computed
pairwise compatibility distinguishes at least one structured incompatibility
from singleton viability
```

Stronger success:

```text
mutual_support shows A, B, and AB viable
pairwise_incompatible shows A and B viable but AB weak/empty
capture_A_over_B shows A preserved/expanded with B or AB contraction
capture_B_over_A shows symmetric counterpart
random/clock/stasis controls do not mimic all structured bins
identity_shuffle_control weakens or destroys structured pairwise signal
```

Failure:

```text
pairwise futures add no information beyond singleton futures
controls mimic structured regimes
permissive continuity dominates all results
identity definitions are too broad or too narrow
capture regimes cannot be distinguished from symmetric incompatibility
```

If failure occurs, do not scale.

Revise:

```text
E_sigma
~=_sigma
regime generator
candidate signatures
controls
```

## 12. Implementation guidance

Prefer a new package path:

```text
omega/rfs_mb0_pairwise/
```

Suggested files:

```text
omega/rfs_mb0_pairwise/substrate.py
omega/rfs_mb0_pairwise/exact.py
omega/rfs_mb0_pairwise/run_smoke.py
```

Suggested responsibilities:

```text
substrate.py:
  state representation
  regime generator
  identity candidate signatures
  continuity predicates

exact.py:
  finite-horizon reachability
  singleton identity-preserving futures
  pairwise joint identity-preserving futures
  count/ratio/bin helpers

run_smoke.py:
  batch runner
  controls
  parallel execution
  timeout salvage
  CSV/JSONL/summary output
```

Reuse RFS0 exact computation patterns where possible.

Keep the implementation transparent and small.

## 13. Public claim boundary

Allowed claim after a passing smoke:

```text
We implemented a minimal pairwise compatibility probe that compares
singleton identity-preserving reachable futures against joint identity-preserving
reachable futures in small finite substrates.
```

Allowed if results support it:

```text
Pairwise joint futures exposed compatibility failures that singleton viability
alone missed in controlled toy regimes.
```

Not allowed:

```text
Omega has been detected.
Pseudo-Omega has been demonstrated.
Extracted candidates are valuers or agents.
Pairwise compatibility is full Omega compatibility.
The agentic field has been formalized.
Lushness has been measured.
```

## 14. Bottom line

This probe tests the first minimal compatibility question:

```text
Can two derived bounded identities continue together?
```

and the first local/global divergence question:

```text
Can one identity preserve itself while joint compatibility contracts?
```

If yes, the project earns the next step.

If no, heavier machinery is premature.
