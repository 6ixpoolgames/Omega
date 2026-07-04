# Stationary Containment v0

Status: Lean theorem note / B2 stationary checkpoint
Scope: fixed-point stationary-policy containment for finite possibilistic
ambiguity-family robust viability
Claim boundary: not the full trajectory theorem, not stochastic, not a
derivation that persistence is required, not value, not agency, not
valuerhood, not moral standing, not Omega validation

## Compression

Given a finite ambiguity family and a declared constraint/requirement surface,
`RVK` is the shared-action robust viability kernel from the ambiguity-family
reduction note.

For any stationary policy:

```text
policy : State -> Action
```

the policy induces a closed-loop greatest fixed point:

```text
PolicyKernel(policy)
```

The landed theorem surface says:

```text
PolicyKernel(policy) <= RVK
```

So any state from which a fixed stationary policy guarantees continuation, in
the closed-loop fixed-point sense, is already inside the shared-action RVK.
Moreover, finite policy-reachable successors from such a state also remain
inside `RVK`.

Conversely, `RVK` itself supplies one stationary policy that guarantees from
every `RVK` state simultaneously, by choosing the RVK-preserving shared action
at each RVK state.

## Landed Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/Containment.lean
formal/lean/OmegaProper/Decision/ContainmentExamples.lean
```

Checked theorem surface:

```text
PolicyKernel for one stationary policy;
StationaryGuarantees as fixed-point membership;
PolicyKernel(policy) is contained in RVK;
policy successors and finite policy-reachable states remain inside RVK;
one extracted RVK policy guarantees from every RVK state;
stationary guarantee exists at a state iff that state lies in RVK.
```

The construction uses `Inhabited Action` only to make the extracted RVK policy
total outside the RVK. The theorem does not use that arbitrary default for RVK
states.

## W1 Reading

The W1 ambiguity-family witness now has the stationary reading:

```text
ok:
  has a stationary guarantee and lies in shared-action RVK.

start:
  lies in every per-model corridor but has no stationary guarantee,
  because no single action is safe across both models.
```

This is the finite fixed-point version of the yellow-paint principle: a policy
that genuinely guarantees continuation cannot get outside the shared-action
robust corridor.

## Nonclaims

This note does not prove trajectory-level infinite persistence. It does not
prove memoryless sufficiency for arbitrary history policies. It does not choose
the constraint, requirement, allowed-action predicate, or ambiguity family. It
does not justify the antecedent that persistence is required.

## Follow-On

The immediate follow-on landed as `history_policy_memorylessness_v0.md`:
finite-history-dependent policies do not enlarge the fixed-point guarantee
region beyond `RVK`. The remaining B2 bridge is explicit trajectory/maximality
semantics.
