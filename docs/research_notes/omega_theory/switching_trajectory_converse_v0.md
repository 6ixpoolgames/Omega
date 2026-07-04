# Switching Trajectory Converse v0

Status: Lean theorem note / B2 trajectory converse checkpoint
Scope: finite switching bad-prefix semantics for stationary ambiguity-family
robust viability
Claim boundary: switching-adversary possibilistic semantics only; not
fixed-world trajectory semantics, not stochastic, not a derivation that
persistence is required, not value, not agency, not valuerhood, not moral
standing, not Omega validation

## Compression

The trajectory converse is now formalized against the semantics that actually
matches `RVK`.

`RVK` is robust after every step: if any model can produce a successor, that
successor must again satisfy the same robust guarantee. The corresponding
trajectory semantics therefore allows the adversary to choose a model at each
finite transition.

The landed theorem is:

```text
StationaryGuarantees(policy, x)
  iff
SwitchingTrajectoryGuarantees(policy, x)
```

where `SwitchingTrajectoryGuarantees` means:

```text
no finite policy-following switching trace from x has:
  a state outside Constraint;
  a state outside Requirement;
  a state where the policy action is not Allowed;
  an endpoint deadlocked in any model.
```

Consequently:

```text
SwitchingTrajectoryGuarantees(policy, x)
  -> PolicyKernel(policy, x)
  -> RVK(x)
```

## Why Switching Semantics

A fixed-world reading is weaker. If model identity is fixed forever, a state may
look safe in each model separately while a successor reached in one model would
fail under another model. `RVK` intentionally rejects that state because the
ambiguity has not been discharged.

The switching finite-prefix semantics is the finite refutation form of the
shared-action robust corridor:

```text
exists one action
forall model choices now and later
no finite bad prefix appears
```

## Landed Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/TrajectoryConverse.lean
formal/lean/OmegaProper/Decision/TrajectoryConverseExamples.lean
```

Checked theorem surface:

```text
FiniteSwitchingPolicyTrace;
Deadlocked endpoint predicate;
BadFiniteSwitchingTrace;
SwitchingTrajectoryGuarantees as no finite bad prefix;
switching guarantee implies Constraint, Requirement, Allowed, and model-wise enabledness;
successor closure under any model step;
SwitchingTrajectoryGuarantee is postfixed for PolicyKernel;
SwitchingTrajectoryGuarantee -> PolicyKernel -> RVK;
PolicyKernel excludes all finite switching bad prefixes;
PolicyKernel iff SwitchingTrajectoryGuarantees.
```

## W1 Reading

The W1 witness remains the guardrail:

```text
ok:
  satisfies the switching trajectory guarantee under the extracted RVK policy.

start:
  satisfies each per-model corridor separately, but no policy satisfies the
  switching trajectory guarantee from start.
```

The problem at `start` is not memory, cleverness, or finite-prefix encoding. It
is the lack of a single action that survives the ambiguity family.

## Nonclaims

This note does not claim fixed-world trajectory equivalence. It does not select
the ambiguity family, requirement, allowed-action predicate, or constraint set.
It does not justify that persistence is required.

## Next Step

The B2 containment spine is now a coherent fixed-point and finite-prefix
trajectory package. The next prudent step is audit or consolidation, not another
semantic expansion.
