# Ambiguity-Family RVK Reduction v0

Status: Lean theorem note / B2 Batch A checkpoint
Scope: finite nonempty possibilistic ambiguity families with shared state,
action, and constraint sets under shared-action / switching robust semantics
Claim boundary: not the full containment theorem, not stochastic, not a
derivation that persistence is required, not value, not agency, not
valuerhood, not moral standing, not Omega validation

## Compression

An ambiguity-indexed robust viability kernel does not require a second fixed
point theory.

For a finite family of models with transitions `Step_i`, define:

```text
MergedStep x a y :=
  exists i, Step_i x a y

FamilyEnabledAllowed x a :=
  Allowed x a
  and forall i, exists y, Step_i x a y
```

Then the shared-action ambiguity kernel is exactly the existing robust corridor:

```text
RVK(F, Allowed, Requirement)
  =
RobustCorridor(mergedDecision(F), FamilyEnabledAllowed, Requirement)
```

The universal model quantifier is therefore represented as an admissibility
transformation: the action must be available and enabled in every model, while
the merged transition relation collects every possible successor from every
model.

## Semantic Boundary

This is the corridor for stepwise or switching ambiguity:

```text
one shared action must survive every declared model's possible successors.
```

It is not the adaptive corridor for an unknown-but-fixed model whose identity
can be learned over time. That fixed-world reading needs an information-state
kernel over `(state, remaining_models)`, recorded separately in
[`adaptive_fixed_world_corridor_b21.md`](adaptive_fixed_world_corridor_b21.md).

## Landed Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/AmbiguityFamily.lean
formal/lean/OmegaProper/Decision/AmbiguityFamilyExamples.lean
```

Checked theorem surface:

```text
ActionRobustKeepsAmb iff ActionRobustKeeps on the merged system;
RVK equals the merged robust corridor by definition;
RVK states satisfy the shared constraint and declared requirement;
RVK states admit one shared action enabled and safe in every model;
RVK is contained in each per-model robust corridor;
adding models through an exact embedding narrows RVK;
W1: intersection of per-model corridors can strictly overstate shared-action RVK.
```

## W1 Strictness

The retained witness has two models, two actions, and a start state:

```text
model 0: action a is safe, action b is fatal;
model 1: action b is safe, action a is fatal.
```

The start state lies in each per-model robust corridor, because each model has
some safe action. It is not in the shared-action RVK, because no single action
works across both models.

This blocks the tempting but wrong formalization:

```text
forall model, exists safe action
```

as a substitute for the robust shared-action condition:

```text
exists action, forall model, safe in that model
```

## Nonclaims

This note does not prove that any process should persist. It does not choose
the constraint set, requirement, allowed-action predicate, or ambiguity family.
It does not prove trajectory-level persistence/confinement yet. It only keeps
the ambiguity-family corridor inside the existing robust-corridor fixed-point
surface.

## Follow-On

The immediate follow-on landed as `stationary_containment_v0.md`: stationary
policy guarantee kernels are confined by this `RVK` without introducing another
operator. The remaining containment work is trajectory semantics and
history-policy memorylessness.
