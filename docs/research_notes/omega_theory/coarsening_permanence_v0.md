# Coarsening Permanence v0

Status: finite Lean theorem note
Scope: deterministic observation coarsening, restricted decoder classes, robust recovery, randomized recovery, and robust randomized recovery
Claim boundary: not empirical observation validity, not value, not agency, not identity, not Omega validation

## Purpose

Observation refinement says that if a coarse observation is computed from an
already available fine observation, then any coarse decoder can be simulated by
a fine decoder.

The contrapositive is the useful bridge fact:

```text
if recovery fails for the available fine observation,
then deterministic coarsening cannot restore that failed recovery claim.
```

This is the formal version of the narrow data-processing discipline used by
the recovery layer. Coarsening may make a variable more legible, stable, or
semantically aligned, but it does not create new recovery capacity for an
unrestricted decoder over an already available finer observation.

## Lean Surface

Main file:

```text
formal/lean/OmegaProper/Recovery/CoarseningPermanence.lean
```

Core theorem family:

```text
recoveryAt_failure_persists_under_coarsening
recoveryInAt_failure_persists_under_coarsening
supportExact_failure_persists_under_coarsening
robustRecoveryAt_failure_persists_under_coarsening
robustRecoveryInAt_failure_persists_under_coarsening
randomizedRecoveryAt_failure_persists_under_coarsening
randomizedRecoveryInAt_failure_persists_under_coarsening
robustRandomizedRecoveryAt_failure_persists_under_coarsening
robustRandomizedRecoveryInAt_failure_persists_under_coarsening
```

The unrestricted theorems need only a deterministic factorization:

```text
coarse = g after fine
```

The restricted decoder-class theorems also require an explicit lifting law:

```text
allowed coarse decoders lift to allowed fine decoders.
```

That extra hypothesis is intentional. Otherwise the decoder class can do the
work, and a coarsening theorem would silently assume away access restrictions.

## Bridge Role

This promotes the bridge claim:

```text
recovery failure persists under deterministic coarsening
```

from active target to landed finite theorem.

It does not say that coarse variables are useless. It says a deterministic
coarsening of an already available observation cannot recover a target that the
finer observation could not recover under the corresponding decoder class.

## Non-Claims

This note does not claim:

```text
that every useful abstraction is a deterministic coarsening;
that new measurements or side information cannot improve recovery;
that semantic coarse variables are unimportant;
that empirical observation maps are correct;
that recovery is value, agency, identity, or Omega.
```
