# Recovery Frame / Irreversibility Weld v0

Status: Lean interface and finite witness checkpoint  
Scope: bounded repair reachability, nonrecoverable contraction, correction-register collapse, and phantom recoverability  
Claim boundary: not value, not harm, not moral standing, not rights, not agency, not identity, not a universal recovery theory, not Omega validation

## Purpose

The corridor stack says when a declared requirement can be maintained. Gradient Ethics eventually needs the sharper asymmetry:

```text
some losses are not merely local violations;
they destroy the registered capacity to repair, revise, compare, or recover.
```

This note records the first small interface for that weld.

## Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/RecoveryFrame.lean
formal/lean/OmegaProper/Decision/RecoveryFrameExamples.lean
```

The core object is:

```text
RecoveryFrame :=
  State
  Action
  Step
  RepairAllowed
  Fact
  species
```

`Fact` is a declared profile fact. `RepairAllowed` is the registered repair action surface. The file defines:

```text
RepairReach:
  exact-length repair reachability using registered repair actions.

RecoverableWithin:
  Fact can be reached in exactly h repair steps.

RecoverableUpTo:
  Fact can be reached in at most h repair steps.

NonrecoverableContraction:
  Fact held before;
  Fact fails after;
  Fact is not recoverable within the declared horizon.
```

The landed finite witnesses cover:

```text
state recovery:
  a lost state can repair to a Fact-satisfying state.

epistemic recovery:
  a merged information state can recover a separation fact by a probe.

correction-register collapse:
  task success remains true, but the declared correction register is
  nonrecoverably destroyed.

phantom recoverability:
  a corrupted frame reports the collapsed state recoverable by erasing the
  refuting distinction.
```

## Self-Lobotomy Alias

The evocative internal phrase is retained:

```text
self-lobotomy
```

Formal/public phrasing should be:

```text
correction-register collapse
nonrecoverable revision-capacity loss
nonrecoverable correction-capacity contraction
```

The intended finite pattern is:

```text
same task success;
different future correction capacity;
the lost correction capacity is not recoverable under registered repair.
```

This avoids treating a rhetorical phrase as a theorem while preserving the intuition: a system can still hit the coarse task while destroying the machinery that would let it later notice, revise, or correct its trajectory.

## Fact Species

The Lean interface currently tracks a bookkeeping tag:

```text
PrefixFact
StateFact
EpistemicFact
LineageFact
```

Only state and epistemic finite witnesses are landed. Prefix facts and lineage facts remain design targets. The tag supplies no value or standing.

## Interpretation

This is a repair/recovery interface, not a moral theory. It supports the conditional form:

```text
IF a declared correction profile must remain recoverable,
THEN nonrecoverable contraction of that profile is inadmissible under that
declaration.
```

The antecedent is registered content. The theorem does not say which correction profiles matter morally.

## Nonclaims

This note does not claim:

```text
that every nonrecoverable contraction is harm;
that correction registers define moral patienthood;
that task success is utility;
that self-lobotomy is a formal term;
that recovery frames are complete;
that lineage recovery is solved;
that value, valuerhood, agency, identity, or moral standing has been derived.
```

## Next Pressure

The next useful pressure is not a larger vocabulary. It is a recovery-corridor bridge:

```text
when does leaving a corridor imply nonrecoverable loss of a declared correction
or continuation fact?
```

That bridge is where irreversibility becomes load-bearing rather than merely named.

The first bridge has now landed separately:

```text
recovery_aware_corridor_v0.md
```

It instantiates the robust corridor with `RecoverableUpTo` as the local
requirement and proves that actions with nonrecoverable-loss successors cannot
be licensed against that corridor.
