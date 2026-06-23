# Observed Word Lifting Monotonicity V0

Status: adapter theorem-probe note
Scope: finite observed-word counts under process-coherent abstraction
Claim boundary: finite adapter-relative diagnostic; not entropy, lushness, value, agency, identity, or Omega

## Purpose

Earlier adapter repairs separated:

```text
global edge projection exactness
representative-wise path lifting
safe-prefix counts
extendable safe-prefix counts
observed extendable safe-word counts
```

Batch G combines those surfaces into the first monotonicity probe:

```text
If an abstraction has coherent finite path lifting,
and exact/abstract observations commute through the presentation,
then abstract observed viable words should not inflate exact observed words.
```

This is the adapter-side rehearsal for a later Lean theorem. It is deliberately
finite-horizon and contract-scoped.

## Audit

The new audit kind is:

```text
observed_word_lifting_monotonicity
```

Inputs:

```text
exact_transition
exact_safety
exact_observation
presentation
abstract_transition
abstract_safety
abstract_observation
horizon
optional exact_start_predicate
optional abstract_start_predicate
```

The audit computes:

```text
exact observed extendable safe-word profile;
abstract observed extendable safe-word profile;
edge-projection exactness;
finite path lifting;
observation compatibility;
start compatibility;
safety reflection;
viability-kernel reflection.
```

It reports:

```text
contract_holds:
  all required lifting/compatibility/reflection checks hold.

not_inflated:
  abstract observed-word profile never exceeds exact observed-word profile.

monotone_under_contract:
  contract_holds and not_inflated.
```

## Generated Controls

Two generated cases are retained.

```text
generated_observed_word_lifting_monotonicity:
  exact dynamics has duplicate representatives over a two-label recurrent
  process;
  path lifting and observation compatibility hold;
  exact and abstract observed-word profiles are both [2, 2, 2].
```

```text
generated_observed_word_lifting_inflation:
  global edge projection is exact;
  an abstract path splices incompatible exact representatives inside a merged
  fiber;
  path lifting fails;
  abstract observed-word profile [1, 1, 2] inflates exact profile [1, 1, 1].
```

The second case is the important negative control. It shows why edge projection
alone is not enough for process truth: abstract histories can be stitched
together from exact pieces that no single exact trajectory realizes.

## Current Validation

The retained Batch G run reports:

```text
adapter smoke: PASS, 15 fixtures, focused pytest 109 passed
generated/adversarial validation: PASS, 35 cases
```

## Non-Claims

This note does not claim:

```text
asymptotic entropy monotonicity;
topological entropy;
lushness;
value;
agency;
identity;
Omega;
empirical model validity.
```

It only establishes the finite adapter probe needed before a future formal
monotonicity theorem.
