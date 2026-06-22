# Robust Recovery Ambiguity Sets v0

Status: Lean theorem-spine checkpoint
Scope: deterministic worst-case finite recovery over declared ambiguity sets
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

## Lean Location

Main file:

```text
formal/lean/OmegaProper/Recovery/Robust.lean
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

## Claim Boundary

This layer does not claim:

```text
that Gamma is empirically correct;
that channels outside Gamma are impossible;
that tau is morally significant;
that robustness is a complete alignment criterion;
that decoder classes are natural unless supplied by an adapter/provenance layer;
Omega validation.
```

The result is conditional:

```text
given a declared ambiguity set and decoder class,
these are the exact finite laws for worst-case threshold recovery.
```
