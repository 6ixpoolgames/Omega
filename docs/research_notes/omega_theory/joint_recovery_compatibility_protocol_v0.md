# Joint Recovery Compatibility Protocol v0

Status: preregistration / finite recovery-grounded coupling protocol
Scope: finite individual recovery profiles, individual vector/span controls, joint recovery under coupling, and negative controls
Claim boundary: not value, not standing, not agency, not plurality theory, not moral aggregation, not patienthood, not population optimum, not Omega validation

## Purpose

This sprint tests whether a finite coupling can be grounded in recovery
behavior rather than treated only as a declared graph edge.

Question:

```text
Can two cases have the same individual recovery profiles, same full vector
census, same marginal summaries, and same pure span, while differing in joint
recovery under coupling?
```

This is a bridge sprint. It does not define value, standing, plurality,
patienthood, or moral aggregation.

## Relation To Relational Composability

Relational Composability v0 retained a registered compatibility-profile
instrument:

```text
same individual vectors + same pure span + different declared coupling
```

Joint Recovery Compatibility v0 asks for the next bridge:

```text
same individual vectors + same individual recovery + different joint recovery
```

This does not derive final compatibility. It tests whether a compatibility edge
can be backed by a finite recovery-preservation profile.

## Objects

The finite harness uses:

```text
RecoveryFact:
  a declared fact that a participant requires recoverably.

ParticipantRecovery:
  participant id;
  required facts;
  individually recovered facts.

CouplingMode:
  declared joint coupling mode and the facts recovered jointly under it.

JointRecoveryCase:
  participant vectors plus participant recovery profiles plus coupling mode.

RecoveryProfile:
  individual recovery success;
  joint recovered facts;
  missing joint facts;
  joint recovery success.
```

## Verdicts

```text
separated:
  matched marginal scalar controls, identical full vector census, equivalent
  pure span, identical individual recovery profiles, and different joint
  recovery under coupling.

reduces:
  apparent joint-recovery difference is already visible in individual recovery
  or vector/span controls.

ill-posed:
  joint recovery cannot be defined cleanly enough for the finite harness.
```

## Candidate Witness

Held-fixed individual vectors:

```text
vA = A
vB = B
```

Held-fixed individual recovery:

```text
vA individually recovers A_recovery_fact
vB individually recovers B_recovery_fact
```

Compatible coupling:

```text
joint recovered facts = {A_recovery_fact, B_recovery_fact}
joint recovery succeeds
```

Interfering coupling:

```text
joint recovered facts = {A_recovery_fact}
joint recovery fails because B_recovery_fact is missing
```

Expected separation:

```text
same individual recovery profiles;
same vector census;
same pure span;
different joint recovery.
```

## Negative Controls

Identical joint recovery control:

```text
same individual recovery + same joint recovery -> no separation
```

Individual-difference control:

```text
if an individual recovery profile changes, the case is not credited as a
joint-only separation
```

## Kill Condition

If the candidate pair separates by changing individual recovery, marginal
scalar controls, full vector census, or pure span, the sprint reports `reduces`
or `ill-posed`.

Do not claim recovery-grounded coupling unless the individual surfaces are held
fixed.

## Nonclaims

This protocol does not claim:

```text
value;
standing;
agency;
plurality theory;
moral aggregation;
patienthood;
population optimum;
Omega validation.
```

## Public Compression

Joint Recovery Compatibility v0 tests whether coupling can be backed by joint
recovery: same individual vectors and same individual recovery can still leave
joint recovery under coupling open. It is a bridge instrument, not plurality or
value theory.
