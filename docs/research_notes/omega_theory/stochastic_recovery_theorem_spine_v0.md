# Stochastic Recovery Theorem Spine v0

Status: finite theorem-spine note
Scope: exact rational stochastic recovery helper laws, Lean recovery theorems, and finite property checks
Claim boundary: theorem spine and adapter parity; not empirical validation, not value, not agency, not Omega validation

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
robust ambiguity-set recovery.
prior-relative expected recovery.
```

The Lean formalization now lives in:

```text
formal/lean/OmegaProper/Recovery/
```

The public compression is:

```text
Support-exact recovery is the zero-error endpoint of a source-indexed recovery
profile, not the whole recovery notion.
```

The focused test file:

```text
tests/test_stochastic_recovery_theorem_spine.py
```

checks these laws over small exact rational finite cases.

## Current Lean Laws

The Lean recovery layer proves:

```text
Support-exact recovery iff RecoveryExistsAt 1.
RecoveryExistsAt is monotone downward in threshold.
RecoveryExistsInAt is the explicit deterministic decoder-class form, with
  RecoveryExistsAt as its unrestricted specialization.
Success + FailureMass = 1.
Success <= 1.
Observation refinement preserves deterministic and randomized recovery.
Deterministic recovery embeds into randomized recovery.
Randomized success is nonnegative and bounded by 1.
RandomizedRecoveryInAt is the explicit randomized decoder-class form, with
  RandomizedRecoveryAt as its unrestricted specialization.
Randomized recovery is monotone downward in threshold.
RobustRecoveryAt is a uniform decoder guarantee over a declared ambiguity set.
RobustRecoveryInAt is the explicit deterministic decoder-class form for robust
  recovery.
Singleton ambiguity reduces to ordinary RecoveryExistsAt / RecoveryExistsInAt.
Robust recovery is monotone downward in threshold and monotone under
  ambiguity-set restriction.
Observation refinement preserves robust recovery under decoder-class lifting.
Prior-relative expected recovery is a declared-prior average-case axis.
Worst-case threshold recovery implies prior-relative expected threshold
  recovery under any declared prior.
Point-mass priors reduce expected success to source success at the selected
  source.
Joint recovery implies each marginal recovery.
Same-panel exact marginal recovery pairs into exact joint recovery.
Fixed-policy action kernels induce Markov kernels.
The induced policy kernel has a named validity theorem.
Finite-horizon hit probabilities are nonnegative, bounded by 1, and monotone
  in horizon.
Equal selected policy rows imply equal hit profiles.
```

The finite Lean examples prove:

```text
99/100 recovery need not be support-exact.
Positive support does not determine graded recovery.
Randomized recovery is a separate decoder axis.
Separate marginal panels need not recover the joint target.
Per-channel exact recovery does not imply robust exact recovery by one common
  decoder over the ambiguity set.
High expected recovery under a skewed prior does not imply worst-case recovery.
```

See [stochastic_recovery_formalization_v0.md](stochastic_recovery_formalization_v0.md).

## Current Python-Checked Laws

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
randomized robust recovery over ambiguity sets.
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
