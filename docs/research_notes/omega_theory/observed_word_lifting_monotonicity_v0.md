# Observed Word Lifting Monotonicity V0

Status: adapter theorem-probe note with Lean extraction
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
then every abstract observed viable word should have an exact realization.
```

This adapter probe has now been extracted into Lean as a finite language
inclusion theorem. The adapter remains the executable finite-substrate surface;
the Lean file records the contract in substrate-independent form.

## Lean Extraction

Lean location:

```text
formal/lean/OmegaProper/Trajectory/ObservedWordMonotonicity.lean
```

Main formal objects:

```text
ObservedSafePath
ObservedExtendableSafeWord
ObservedViablePathLift
StrongObservedWordTransport
EdgeImageExact
```

Main checked statements:

```text
strongObservedWordTransport_observedViablePathLift
observedLanguage_subset_of_observedViablePathLift
finiteObservedWordCount_mono_of_subset
edgeImageExact_does_not_imply_stepReflects
edgeImageExact_does_not_imply_pathLifting
```

The theorem structure is intentionally layered:

```text
minimal semantic condition:
  every abstract observed extendable safe word has an exact realization.

audit-friendly sufficient contract:
  safety reflects, representative-wise steps lift, and observations commute.

finite count corollary:
  once retained word sets are finite, language inclusion implies count
  monotonicity.
```

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
word-level abstract-minus-exact differences by horizon;
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

language_subset:
  every abstract observed word is realized by the exact system.

phantom_abstract_words_by_horizon:
  abstract observed words with no exact realization.

missing_exact_realizations:
  flattened horizon/word list of those unrealized abstract words.

not_inflated:
  abstract observed-word counts never exceed exact observed-word counts.
  This is a scalar diagnostic only.

monotone_under_contract:
  contract_holds and language_subset.
```

## Generated Controls

Three generated cases are retained.

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

```text
generated_observed_word_lifting_equal_count_language_mismatch:
  exact and abstract observed-word count profiles are both [1, 1, 1];
  observation compatibility fails;
  abstract words such as [A, C] replace exact words such as [A, B].
```

The negative controls show two distinct failures. Edge projection alone is not
enough for process truth: abstract histories can be stitched together from
exact pieces that no single exact trajectory realizes. Scalar counts are also
not enough: equal counts can conceal replacement of exact words by phantom
abstract words.

## Current Validation

The retained Batch G run reports:

```text
adapter smoke: PASS, 15 fixtures, focused pytest 109 passed
generated/adversarial validation: PASS, 36 cases
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

It only establishes the finite adapter probe and its matching Lean finite-word
transport theorem.
