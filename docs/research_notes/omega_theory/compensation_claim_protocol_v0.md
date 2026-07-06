# CompensationClaim / NOLP Protocol v0

Status: preregistration / finite same-frame compensation protocol
Scope: same-frame contraction profiles, expansion profiles, certified cover, and refusal-first licensing
Claim boundary: not value, not standing, not aggregation, not population ethics, not patienthood, not cross-valuer compensation, not correct compensation order, not Omega validation

## Purpose

The repo now has:

```text
nonrecoverable-loss profiles;
expansion profiles;
order-sampling calibration;
ensemble span;
registered coupling;
joint recovery compatibility;
joint-tier reduction audit.
```

This protocol starts the compensation layer without opening cross-valuer
population ethics.

Question:

```text
When can a declared expansion claim certify compensation for a
nonrecoverable contraction in the same registered fact frame?
```

## Core Object

A v0 `CompensationClaim` has:

```text
contraction profile C;
expansion profile E;
cover relation cover : lost_fact -> expanded_fact;
certification flag / reflection condition.
```

Same-frame v0 validity:

```text
every down-closed fact in C is covered by some declared expansion fact in E.
```

Certified compensation:

```text
valid cover
and
cover relation reflects through the declared recovery/coupling frame.
```

In the Python v0 harness, the reflection condition is represented by an
explicit `certified` field. Lean/reflection integration remains a later proof
target.

Every v0 verdict carries a stability label:

```text
order_invariant;
order_dependent;
fragile;
pathological;
not_sampled.
```

The same-frame v0 examples are marked `not_sampled`; cross-order compensation
verdicts may not be promoted until they pass the order-sampling harness.

## NOLP v0

NOLP here means:

```text
No Omniscient License Presumption.
```

v0 reading:

```text
same-frame nonrecoverable contraction is refused unless a complete certified
compensation cover is registered.
```

This is not a claim that compensation is morally final. It is a claim that
uncertified compensation cannot defeat the recovery-aware refusal.

## Required Witnesses

```text
certified same-frame cover:
  complete and certified -> NOLP refusal is defeated in v0.

uncertified cover:
  complete but uncertified -> still refused.

incomplete cover:
  certified but missing a lost fact -> still refused.

phantom compensation:
  believed frame says covered;
  true frame has an uncovered nonrecoverable contraction;
  believed verdict licenses what true verdict refuses.
```

Kill conditions:

```text
if incomplete cover passes, fail;
if uncertified cover passes, fail;
if phantom compensation does not diverge, fail;
if same-frame and cross-frame claims are mixed, fail.
```

## Explicitly Out Of Scope

Do not implement in v0:

```text
cross-valuer compensation;
local/joint crossing compensation;
patienthood;
population aggregation;
standing;
stale certificates for self-extending registers;
universal value order;
order-sampling verdict authority;
large-deformer or quantum cases.
```

## Public Compression

Compensation is registered and certified, not assumed. In v0, a same-frame
nonrecoverable contraction is refused unless its declared loss profile is
completely covered by a certified expansion profile in the same fact frame.
