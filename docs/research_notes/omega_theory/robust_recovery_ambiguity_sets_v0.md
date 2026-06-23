# Robust Recovery Ambiguity Sets v0

Status: Lean theorem-spine checkpoint
Scope: deterministic and randomized worst-case finite recovery over declared ambiguity sets
Claim boundary: not empirical channel validity, not a prior, not value, not agency, not identity, not Omega validation

## Purpose

The finite recovery layer now distinguishes one exact channel from a declared
ambiguity set of possible channels.

The central definition is:

```text
RobustRecoveryAt Gamma target observe tau
```

meaning:

```text
there exists one deterministic decoder that reaches threshold tau
for every source state under every channel C in Gamma.
```

The restricted decoder-class form is:

```text
RobustRecoveryInAt Gamma target observe Allowed tau
```

This is the provenance-aligned form: the allowed decoder class is supplied
explicitly instead of being hidden inside unrestricted existence.

The randomized-decoder analogue is:

```text
RobustRandomizedRecoveryAt Gamma target observe tau
```

and its restricted form is:

```text
RobustRandomizedRecoveryInAt Gamma target observe Allowed tau
```

Those names mean that one randomized decoder, or one allowed randomized decoder,
must meet the same source-wise threshold for every channel in `Gamma`.

## Lean Location

Main file:

```text
formal/lean/OmegaProper/Recovery/Robust.lean
formal/lean/OmegaProper/Recovery/RobustRandomized.lean
```

Imported by:

```text
formal/lean/OmegaProper/Recovery.lean
```

## Proved Shape

The Lean layer proves:

```text
RobustRecoveryAt is monotone downward in threshold.
RobustRecoveryInAt is monotone downward in threshold.
Larger ambiguity sets are harder.
RobustRecoveryAt is the unrestricted RobustRecoveryInAt specialization.
Singleton ambiguity reduces to RecoveryExistsAt.
Singleton ambiguity with an allowed decoder class reduces to RecoveryExistsInAt.
Observation refinement preserves robust recovery.
Observation refinement preserves restricted robust recovery when lifted decoders
  remain in the allowed fine decoder class.
RobustRandomizedRecoveryAt is monotone downward in threshold.
RobustRandomizedRecoveryInAt is monotone downward in threshold.
Larger ambiguity sets are harder for robust randomized recovery.
RobustRandomizedRecoveryAt is the unrestricted
  RobustRandomizedRecoveryInAt specialization.
RobustRandomizedFamilyRecoveryAt names the declared randomized-decoder family
  surface and is equivalent to restricted robust randomized recovery over the
  family image.
Singleton ambiguity reduces to RandomizedRecoveryAt.
Singleton ambiguity with an allowed randomized decoder class reduces to
  RandomizedRecoveryInAt.
Deterministic robust recovery embeds into robust randomized recovery.
Observation refinement preserves robust randomized recovery.
Observation refinement preserves restricted robust randomized recovery when
  lifted randomized decoders remain in the allowed fine randomized-decoder
  class.
Robust randomized failure persists under deterministic coarsening.
```

The examples layer also proves the finite strictness witness:

```text
two channels can each be exactly recoverable on their own,
while no single deterministic decoder recovers the two-channel ambiguity set.
```

## Interpretation

Robust recovery is a uniform-decoder guarantee:

```text
same decoder;
all declared channels in Gamma;
all source states;
same threshold tau.
```

This is stricter than saying each channel separately has some successful
decoder. It is the finite worst-case version needed before prior-relative or
empirical recovery claims.

Robust randomized recovery has the same shape, but the shared decoder is a
declared randomized decoder. Declared randomized-decoder family recovery gives
an exact finite enumeration surface when an adapter supplies a finite family.
It is not a claim that the repo has solved global randomized maximin
optimization.

## Claim Boundary

This layer does not claim:

```text
that Gamma is empirically correct;
that channels outside Gamma are impossible;
that tau is morally significant;
that robustness is a complete alignment criterion;
that decoder classes are natural unless supplied by an adapter/provenance layer;
that global randomized maximin optimization has been solved;
Omega validation.
```

The result is conditional:

```text
given a declared ambiguity set and decoder class,
these are the exact finite laws for worst-case threshold recovery.
```
