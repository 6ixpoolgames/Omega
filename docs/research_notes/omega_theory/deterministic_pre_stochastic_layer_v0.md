# Deterministic Pre-Stochastic Layer v0

Status: finite adapter validation note
Scope: exact deterministic recovery, refinement, coarsening, and stale-loss controls
Claim boundary: synthetic finite validation only; not stochastic validation, not empirical substrate validation, not value, agency, or Omega validation

## Purpose

Before adding probabilistic or approximate audits, the finite relational adapter
needs a deterministic floor. The goal is to make the exact finite facts boring:

```text
observation recovers target iff target is constant on observation fibers;
finer observations recover at least what coarser observations recover;
deterministic garbling/coarsening cannot improve exact recovery;
minimal sufficient observations are target-fiber observations;
stale abstractions can hide loss that reflected abstractions expose.
```

This layer is pre-stochastic. It deliberately uses exact finite observations,
targets, and paths so later probabilistic versions have a clear baseline.

## Implemented Families

The validation runner covers six small deterministic families.

### Joint Bounded Recovery

Two separate observations can each recover their own binary target:

```text
first-bit observation  -> first-bit target
second-bit observation -> second-bit target
```

Neither observation alone recovers the joint target. This blocks the shortcut:

```text
individual exact recovery => joint exact recovery
```

### Decoder Class Strictness

The same observation and target can fail under a weak decoder class and succeed
under a richer decoder class. Exact recoverability is not only a property of
the observation and target; it is also a property of the declared decoder class.

### Observation Refinement Monotonicity

Identity observation refines first-bit observation over the four binary states.
Every binary target recoverable from the coarser observation remains recoverable
from the finer observation. In this example:

```text
first-bit recoverable binary targets: 4
identity recoverable binary targets: 16
```

### Deterministic Garbling Non-Improvement

First-bit observation is a deterministic garbling of identity observation. It
recovers only a subset of the exact binary targets recoverable from identity.
This is the deterministic support analogue of the later stochastic
data-processing discipline.

### Minimal Sufficient Observation

For a binary target, the target-fiber observation is the coarsest exact
observation sufficient for that target. The validation enumerates all `4^4`
observations from four states into four labels:

```text
enumerated observations: 256
target-recovering observations: 84
```

Every enumerated observation that recovers the target refines the target-fiber
observation.

### Reflected Versus Stale Hidden Loss

A before-transition has a path from `a` to `c`; an after-transition loses that
path. A stale abstraction that keeps reporting the before-transition hides the
loss. A reflected abstraction that tracks the after-transition does not.

This sharpens the hidden-loss story:

```text
stale abstraction:
  can hide exact loss

reflected abstraction:
  reports the loss rather than preserving the old path claim
```

## Reproduction

Run:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_deterministic_layer `
  --out-root .tmp\finite_relational_deterministic_layer
```

The retained result summary is:

```text
../validation_results/finite_relational_deterministic_layer_v0.json
```

## Why This Comes Before Stochasticity

The open stochastic arm will need choices about probability support, thresholds,
error budgets, and approximate soundness. This deterministic layer fixes the
exact concepts first:

```text
fiber purity;
decoder class dependence;
refinement monotonicity;
garbling non-improvement;
minimal sufficient observation;
stale versus reflected loss reporting.
```

Those are the deterministic facts that later stochastic and approximate
versions should relax carefully rather than replace by hand.

## Non-Claims

This layer does not claim:

```text
probabilistic recovery;
approximate recovery;
empirical correctness of any source abstraction;
value, valuerhood, agency, alignment, or Omega.
```

It is a finite exact bridge that makes the next stochastic design less
ambiguous.
