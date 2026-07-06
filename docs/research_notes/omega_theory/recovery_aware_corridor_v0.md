# Recovery-Aware Corridor v0

Status: Lean theorem checkpoint / ODT0 recovery-gate bridge  
Scope: robust corridors whose local requirement is bounded recoverability of a declared fact  
Claim boundary: not harm, not moral standing, not rights, not value, not agency, not identity, not universal recovery, not Omega validation

## Purpose

`RecoveryFrame` made nonrecoverable contraction explicit. This note records the next bridge:

```text
when bounded recoverability is a declared corridor requirement,
an action whose successor nonrecoverably contracts the declared fact
cannot be licensed against that corridor.
```

This turns recovery loss from a standalone witness into an ODT0 gate failure.

## Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/RecoveryAwareCorridor.lean
formal/lean/OmegaProper/Decision/RecoveryAwareCorridorExamples.lean
```

Definitions:

```text
RecoveryRequirement R h s :=
  RecoverableUpTo R h s

RecoveryAwareCorridor D R h Allowed :=
  RobustCorridor D Allowed (RecoveryRequirement R h)
```

The decision action type and repair action type are intentionally separate. The action that causes a transition need not itself be an admissible repair action.

## Main Theorem

The main theorem is:

```text
action_with_nonrecoverable_successor_not_licensed
```

Shape:

```text
D.Step x a y
NonrecoverableContraction R h source y
------------------------------------------------
not LicensedVia D (RecoveryAwareCorridor D R h Allowed) ... x a
```

Proof route:

```text
NonrecoverableContraction
  -> not RecoverableUpTo at the successor
  -> successor violates RecoveryRequirement
  -> successor is outside the robust corridor
  -> ODT0 corridor safety fails
  -> no license against that corridor
```

The theorem is deliberately conditional. It does not say that all systems must preserve the fact. It says that if bounded recoverability of that declared fact is the corridor requirement, then nonrecoverable contraction cannot be licensed.

## Witnesses

### Correction-Register Collapse

The recovery-aware `self-lobotomy` witness says:

```text
same coarse task success;
preserve action can be licensed;
collapse action cannot be licensed;
collapse nonrecoverably destroys the declared correction register.
```

Formal theorem:

```text
W_same_task_success_but_collapse_unlicensed
```

The formal public phrase remains:

```text
nonrecoverable revision-capacity loss
```

`self-lobotomy` is retained as an internal evocative alias only.

### Forbidden Probe

The forbidden-probe witness says:

```text
the reveal action is informative;
the wait action can be licensed;
the reveal action cannot be licensed because its only route causes
nonrecoverable loss of the declared fact.
```

Formal theorem:

```text
W_forbidden_probe
```

This is not a censorship theorem. It is a corridor theorem about acquisition routes:

```text
some information cannot be acquired through a route that remains inside the
declared recovery-aware corridor.
```

## Interpretation

The bridge supports the conditional form:

```text
IF bounded recoverability of a declared correction fact is required,
THEN actions that nonrecoverably contract that fact are not licensed by the
recovery-aware corridor.
```

That is stronger than a standalone warning and weaker than a moral theory.

## Nonclaims

This note does not claim:

```text
that the declared fact is morally mandatory;
that nonrecoverable contraction is always harm;
that forbidden probes are morally forbidden;
that all knowledge has a moral acquisition route;
that patienthood or standing has been identified;
that value, agency, identity, or Omega has been derived.
```

## Next Pressure

The next theorem seam is endogenous register update:

```text
when a system updates the register that defines recoverability or admissibility,
which updates preserve the certification conditions authorizing that update?
```

The recovery-aware corridor gives the object-level gate. Endogenous registers ask when the gate itself may be changed without laundering away its own defeaters.
