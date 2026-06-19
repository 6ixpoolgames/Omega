# Stochastic Recovery Theorem Spine v0

Status: finite theorem-spine note
Scope: exact rational stochastic recovery helper laws and finite property checks
Claim boundary: Python property checks and finite exact helper laws; not Lean theorem closure, not stochastic dynamics, not empirical validation

## Purpose

The stochastic recovery layer should not remain a collection of examples. The
current implementation is organized around a small theorem spine:

```text
support exactness;
optimized deterministic worst-case recovery;
declared-versus-optimized decoder comparison;
coarsening/refinement simulation;
joint versus marginal recovery;
randomized-decoder axis.
```

The focused test file:

```text
tests/test_stochastic_recovery_theorem_spine.py
```

checks these laws over small exact rational finite cases.

## Current Laws

### Support Exactness Implies Worst-Case One

If no observation label is reachable with positive probability from different
target classes, then a deterministic decoder can recover the target with
worst-case success `1`.

### Declared Decoder Success Is Bounded By Optimized Success

For a fixed finite channel, observation, and target, any declared deterministic
decoder has worst-case success no greater than the optimized deterministic
decoder over the same observation labels.

### Coarse Decoder Simulation

If a coarse observation factors through a fine observation, any coarse decoder
can be simulated by a fine decoder:

```text
fine output -> coarse output -> target
```

Therefore, under unrestricted deterministic decoders, coarsening an already
available observation cannot add source information. Coarsening may still be
semantically useful, more stable, more legible, or better target-aligned.

### Support Does Not Determine Probability

The same positive-probability support can have different optimized worst-case
recovery probabilities. Support is the exact floor; probabilities supply the
stochastic recovery surface.

### Worst-Case Scalar Does Not Determine Failure Localization

Two channels can share the same optimized worst-case success while having
different per-source success vectors. The adapter therefore retains the vector,
not only a scalar.

### Marginal Success Does Not Determine Joint Success

Two channels can share the same marginal worst-case success for each component
target while differing in joint target recovery. This is the stochastic bridge
to compatibility.

### Randomized Decoders Are A Separate Axis

A declared randomized decoder can outperform deterministic maximin in a
strictly ambiguous case. The current implementation records declared randomized
decoder success but does not yet implement a general randomized optimizer.

## Next Theorem Work

Possible next formalization steps:

```text
Lean theorem for support-exact recovery iff support disjointness;
Lean theorem for deterministic coarsening monotonicity;
exact randomized maximin via a small linear-programming surface or finite
  declared randomized decoder family;
prior-relative average success as a separate provenance-bearing axis.
```

## Non-Claims

This note does not claim:

```text
general randomized optimization;
Bayes-optimal policy validation;
MDP safety;
empirical correctness of stochastic adapters.
```

It records the exact finite recovery laws currently exercised by the adapter.
