# Order Sampling Harness Protocol v0

Status: preregistration / finite declared-order sensitivity harness
Scope: finite fact orders, loss/expansion/compensation verdict sensitivity, and pre-NOLP calibration
Claim boundary: not final value, not correct fact order, not aggregation, not arbitration, not standing, not agency, not identity, not moral standing, not Omega validation

## Purpose

Loss dominance, expansion dominance, and compensation claims all depend on a
declared fact order. That order is registered structure; it is not derived
value.

Before NOLP issues compensation verdicts, the repo needs a small harness that
classifies whether a verdict is stable across a declared order class.

## Verdict Classes

```text
invariant:
  every sampled/declared order gives the same verdict.

dependent:
  both verdicts occur across the declared order class.

fragile:
  a small declared perturbation changes the verdict.

pathological:
  an order makes a soundness or reflection contract fail; this is an adapter
  problem, not a moral verdict.
```

v0 implements the first two classes directly and records fragility/pathology as
explicit classes in the finite harness.

Kill conditions:

```text
if a verdict changes across sampled orders but is reported as invariant,
  the harness fails;

if an order induces an adapter/soundness violation,
  the verdict must be pathological, not dependent.
```

## Calibration Targets

Use known profile cases before pointing the harness at compensation:

```text
loss dominance:
  local-only vs joint-only should be order-dependent unless the register
  orders local and joint.

expansion dominance:
  task+revision should dominate task-only across every monotone order where
  task <= revision-enriched profile by inclusion.

compensation:
  same-frame cover claims should be invariant only when coverage is explicit
  in every declared order sampled.

fragility:
  local-vs-joint loss comparison should be marked fragile when an adjacent
  declared-order perturbation flips the verdict.

pathology:
  a declared order with a soundness-contract violation must be marked
  pathological rather than treated as moral disagreement.
```

## Out Of Scope

This protocol does not implement:

```text
the correct moral order;
cross-valuer order sampling;
population aggregation;
standing;
patienthood;
ODT2 authority;
NOLP verdicts without certified compensation.
```

## Public Compression

Order sampling prices declaration sensitivity: if a compensation, loss, or
expansion verdict flips across plausible declared fact orders, the verdict is
not a free fact of the system. It is order-content and must be registered.
