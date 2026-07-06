# Static Compensation Certificate Staleness Protocol v0

Status: preregistration / NOLP extension protocol
Scope: static compensation certificates, soundly self-extending registers, and stale cover failure
Claim boundary: not theorem closure, not cross-valuer compensation, not final value, not standing, not aggregation, not patienthood, not moral authority, not Omega validation

## Purpose

CompensationClaim / NOLP v0 is same-frame and static:

```text
given a fixed fact frame, a nonrecoverable contraction is refused unless a
complete certified compensation cover is registered.
```

The next question is dynamic:

```text
Can a fixed compensation certificate remain valid across all sound
continuations of a self-extending register?
```

This protocol preregisters the staleness target before any theorem or witness
is built.

## Objects

```text
RegisterTrace : Nat -> Facts
  the declared facts visible at each time.

StaticCertificate
  a compensation cover over the facts known at t0.

SoundUpdate
  a register update that adds facts without fabricating or deleting the
  certification obligations governing the update.

GrowthWitness
  a sound continuation where RegisterTrace t1 strictly extends RegisterTrace t0.
```

## Expected Witness

```text
t0:
  certificate covers every relevant fact in the old domain.

t1:
  sound update adds a new relevant fact.

old certificate:
  has no cover row for the new fact.

therefore:
  the static certificate is stale for the t1 register.
```

## Target Theorem Shape

Finite, discrete, time-indexed:

```text
If a register has a sound growth continuation adding a relevant fact outside
the domain of a static compensation certificate, then that static certificate
is not valid across all sound continuations of the register.
```

Reading:

```text
no static certificate can certify compensation for facts it could not name.
```

## Kill Conditions

```text
if the new fact is not relevant to the compensation domain, the witness fails;
if the update is not sound, the witness is phantom-register corruption, not
  staleness;
if the certificate is allowed to update, the witness is no longer about static
  certificates;
if cross-valuer compensation enters, the v0 protocol is out of scope.
```

## Nonclaims

This protocol does not claim:

```text
that all compensation is impossible;
that no dynamic certificate can remain valid;
that cross-valuer compensation is defined;
that value, standing, patienthood, or moral authority has been derived.
```

## Public Compression

A static compensation certificate can only certify the facts it covers. If a
soundly self-extending register later adds a new relevant fact, the old
certificate is stale unless it is updated by a certified route.
