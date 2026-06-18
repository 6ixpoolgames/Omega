# Stochastic Recovery Characterization v0

Status: finite adapter validation note
Scope: exact rational finite channels, support ambiguity, decoder optimization, and coarsening checks
Claim boundary: synthetic finite characterization only; not stochastic dynamics, not MDP policy validation, not empirical substrate validation, not value, agency, alignment, or Omega validation

## Purpose

The first stochastic arm should not choose a moral threshold or a single
success criterion. It should characterize the recovery surface of a finite
stochastic channel:

```text
source states X;
outputs Y;
exact rational channel P(y | x);
declared source target d : X -> D;
declared observation o : Y -> O;
deterministic decoders delta : O -> D.
```

The current implementation computes exact finite facts:

```text
support ambiguity;
support-exact recoverability;
per-source success vector;
optimized worst-case deterministic decoder;
declared decoder versus optimized decoder gap;
deterministic coarsening/refinement behavior.
```

Worst-case recovery is the default aggregate because it does not require a
declared prior. Average-case recovery can be added later when a prior is
explicitly part of the adapter provenance.

## Implemented Families

The validation runner covers six exact rational finite families.

### Support Exactness Versus High Confidence

A channel can have high optimized worst-case success while failing exact
support recovery:

```text
exact channel:
  support-exact recoverable = true
  best worst-case success = 1

high-confidence noisy channel:
  support-exact recoverable = false
  best worst-case success = 99/100
```

This keeps exact support claims separate from probabilistic confidence claims.

### Same Support, Different Probabilities

Two channels can have the same positive-probability support and the same
support ambiguity, while their optimized worst-case recovery differs:

```text
high-confidence best worst-case success = 9/10
lower-confidence best worst-case success = 3/5
```

Support alone is not enough once probability matters.

### Declared Versus Optimized Decoder Gap

A declared decoder can perform badly even when an optimized deterministic
decoder performs well:

```text
declared worst-case success = 1/10
optimized worst-case success = 9/10
```

This preserves the repo's declared-versus-optimized discipline in the
stochastic layer.

### Coarsening Non-Improvement

If a coarse observation is a deterministic post-processing of a finer
observation, then unrestricted deterministic decoding from the fine observation
can simulate any coarse decoder.

In the sharp loss witness:

```text
fine best worst-case success = 1
coarse best worst-case success = 0
```

The safe claim is narrow:

```text
coarsening an already available observation does not add source information
under unrestricted deterministic decoders.
```

This does not say coarse variables are useless. Coarsening can improve
legibility, stability, inductive bias, or target alignment. It just does not
create information unavailable to a decoder that already has the fine
observation and can compute the coarse feature.

### Coarse Decoder Simulable By Fine

A target-aligned coarse decoder can be useful and legible. The adapter checks
the exact composition fact:

```text
coarse decoder success vector = fine-composed decoder success vector
```

This is how the layer handles emergent/macroscopic coarse properties without
claiming that coarsening creates information.

### Same Worst-Case, Different Failure Localization

Two optimized decoders can have the same worst-case score while failures are
localized differently:

```text
balanced success vector  = {x0: 4/5, x1: 4/5}
localized success vector = {x0: 1,   x1: 4/5}
```

So the characterization surface records vectors, not just a scalar.

## Reproduction

Run:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_stochastic_recovery `
  --out-root .tmp\finite_relational_stochastic_recovery
```

The retained result summary is:

```text
../validation_results/finite_relational_stochastic_recovery_v0.json
```

## Current Design Choices

```text
probability type:
  exact rational fractions

primary aggregate:
  optimized worst-case success

prior:
  none in this first layer

decoder class:
  all deterministic decoders unless a declared decoder is being contrasted

garbling/coarsening:
  deterministic post-processing of an available observation

thresholds:
  intentionally deferred
```

## Non-Claims

This layer does not claim:

```text
full stochastic dynamics;
MDP policy safety;
Bayesian or average-case value;
approximate empirical recovery;
that coarsening is semantically bad;
value, valuerhood, agency, alignment, or Omega.
```

It is a small exact characterization surface that prepares the adapter for
probabilistic and approximate claims without choosing the alignment criterion
prematurely.
