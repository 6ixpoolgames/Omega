# Bad Panel Taxonomy v0

Status: branch exploration note

This note names failure modes for declared continuation/consequence panels.
The point is not to add ontology. The point is to make the weakest hinge in
the current stack explicit:

```text
consequence claims are only as good as the declared evaluated panel and
comparison discipline.
```

Existing Lean neighbors:

```text
formal/lean/OmegaProper/Trajectory/ConsequenceDiscipline.lean
formal/lean/OmegaProper/Trajectory/ConsequenceComparison.lean
formal/lean/OmegaProper/Trajectory/ConsequencePanelDiscipline.lean
formal/lean/OmegaProper/Trajectory/ProfileAbstraction.lean
```

## Empty Evaluated Panel

Failure mode:

```text
no contexts are evaluated
```

False claim it creates:

```text
all fragments look compatible by vacuity
```

Existing formal neighbor:

```text
EvaluationVacuous
collapsed_of_no_evaluated_contexts
```

Future formal target:

```text
require declared nonempty evaluated panels before interpreting any positive
compatibility result
```

## Universal Comparison

Failure mode:

```text
every evaluated comparison succeeds
```

False claim it creates:

```text
no erasure is refused, so all quotienting appears safe
```

Existing formal neighbor:

```text
ComparisonUniversalOnEvaluated
collapsed_of_universal_compare
```

Future formal target:

```text
separate "not collapsed" from "meaningful"
```

## All-Refusing Comparison

Failure mode:

```text
every evaluated comparison fails, possibly including self-comparison
```

False claim it creates:

```text
the system has refusals, but the comparison is too pathological to support
ordinary identification claims
```

Existing formal neighbor:

```text
AllPairsSeparated
SelfSeparated
EvaluatedPanelNonpathological
```

Future formal target:

```text
make self-compatibility or an explicitly directional exception part of panel
health when the use case requires ordinary identification
```

## Post-Hoc Chosen Panel

Failure mode:

```text
contexts or comparisons are selected after seeing the desired separation
```

False claim it creates:

```text
the apparatus appears to discover structure that it was tuned to manufacture
```

Existing formal neighbor:

```text
admissibility/provenance notes and registry-first validation discipline
```

Registry-first artifacts are the empirical defense against this failure mode:
the declared instrument must be fixed before optimized or existence-style
recovery is interpreted.

Future formal target:

```text
DeclaredPanel records and no-post-hoc extension/restriction rules
```

## Under-Separating Panel

Failure mode:

```text
the panel omits contexts needed to distinguish consequence-bearing fragments
```

False claim it creates:

```text
unsound identifications look safe because the panel is too weak
```

Existing formal neighbor:

```text
universal-allow abstraction unsoundness when exact blocks exist
```

Future formal target:

```text
panel extension monotonicity for preserved refusals
```

## Over-Separating Panel

Failure mode:

```text
the panel or comparison refuses distinctions irrelevant to the declared target
```

False claim it creates:

```text
classes and quotients look invalid for reasons outside the declared consequence
question
```

Existing formal neighbor:

```text
BalancedContextPanel
EvaluatedPanelNonpathological
```

Future formal target:

```text
target-relative panel relevance and comparison provenance
```

## Decorative Primitive Predicates

Failure mode:

```text
the presentation contains fields named relation/distinction/asymmetry, but no
joint primitive witness
```

False claim it creates:

```text
primitive vocabulary is mistaken for primitive nondegeneracy
```

Existing formal neighbor:

```text
JointPrimitiveWitness
AsymmetryPrimitiveWitness
PrimitiveNondegenerate
```

Future formal target:

```text
require witnesses, not just predicate fields, before invoking primitive
non-collapse
```

## Disconnected Primitive Predicates

Failure mode:

```text
relation and separation exist somewhere, but not in contact over the same
relata/distinction
```

False claim it creates:

```text
separate primitive ingredients are treated as jointly instantiated
```

Existing formal neighbor:

```text
JointPrimitiveWitness
AsymmetryPrimitiveWitness.toJoint
```

Future formal target:

```text
state nondegeneracy as contact conditions, not independent existence claims
```

## Summary

The taxonomy separates three questions:

```text
1. Does the primitive presentation have real witnesses?
2. Does the consequence panel have teeth without pathology?
3. Was the panel declared in a way that can be audited?
```

Only after all three are addressed should compatibility, separation, quotient,
or proto-teleological claims be treated as meaningful.
