# Support Under Perturbation v0

Status: formal support-integrity note
Scope: finite support predicates carrying consequence distinctions
Claim boundary: not agency, not identity, not deformer theory, not alignment validation

This note records the next small step after support restriction and support
minimality.

Earlier support files established:

```text
DistinctionSupport:
  a support can carry a consequence-separated pair through internal paths

SupportRestriction:
  dropping either endpoint of a supported pair destroys support for that pair

SupportMinimality:
  minimal support is pair-relative, not object-relative
```

The new Lean file is:

```text
../../../formal/lean/OmegaProper/Trajectory/SupportUnderPerturbation.lean
```

It packages the same idea as a perturbation-style guardrail.

## Core Definitions

`SupportIntegrityUnder S Next C D x y` says:

```text
if support C carries the merge-separated pair x,y,
then changed support D also carries that same pair
```

`SupportDestroyedUnder S Next C D x y` says:

```text
C carries the merge-separated pair x,y,
but D does not
```

These definitions are deliberately pair-relative and support-relative. They do
not assert that an object, agent, self, boundary, or deformer persisted through
perturbation.

## Main Guardrails

Lean proves:

```text
sameSupport_preserves_integrity
supportDestroyed_not_integrity
supportDestroyed_if_left_missing
supportDestroyed_if_right_missing
```

The important content is simple:

```text
support integrity requires the changed support to still carry the declared pair
```

If a changed support drops either endpoint of the carried pair, the support no
longer carries that distinction.

## Tiny Finite Witness

The file reuses the existing recurrent two-state cycle witness.

It declares three support levels:

```text
baseline:
  the full cycle support

mild:
  the same full cycle support

severe:
  the left-only support, which drops the right endpoint
```

Lean proves:

```text
cycle_baseline_supports_merge_left_right
cycle_mild_supports_merge_left_right
cycle_severe_not_supports_merge_left_right
cycle_mild_preserves_baseline_support_integrity
cycle_severe_destroys_baseline_support
cycle_severe_not_support_integrity
cycle_support_threshold_witness
```

The finite witness is not a physical perturbation model. It is the smallest
formal shape of a threshold-like support fact:

```text
mild support change preserves the carried distinction;
severe support change removes an endpoint and destroys support for it.
```

## Why This Matters

This is the lowest safe version of the old "vortex under perturbation" idea.

The project should not say:

```text
the same agent/deformer survived perturbation
```

The formal layer can say:

```text
the declared support still carries the consequence distinction
```

or:

```text
the declared support no longer carries the consequence distinction
```

That is enough to start discussing perturbation robustness without smuggling
identity or object boundaries back into the theory.

## Next Step

The natural stronger version is recurrent support robustness:

```text
under a changed transition relation and support predicate,
does a recurrent viable class still carry the declared distinction?
```

That later layer should keep the same discipline:

```text
preserved carried distinction
not persistent self
```
