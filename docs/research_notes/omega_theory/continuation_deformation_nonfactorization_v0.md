# Continuation Deformation as Non-Factorization v0

Status: active compression note
Scope: finite deformation/proxy-failure language
Claim boundary: not deformer theory, not agency, not identity, not value, not Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/ContinuationDeformation.lean
```

The compression is:

```text
finite continuation deformation = non-factorization of a declared continuation
fact through a proposed summary.
```

In Lean:

```text
ContinuationDeformation summary fact :=
  NonFactorization summary fact
```

## Interpretation

A finite deformation witness has the shape:

```text
summary a = summary b
fact a != fact b
```

So the summary cannot determine the fact.

This is the same pattern as:

```text
same benchmark score, different safety fact;
same presentation, different target;
same proxy, different continuation property;
same coarse future map, different derived reachability/viability/carrier fact.
```

## Why This Matters

This keeps "deformation" from becoming an object-like or identity-loaded term.
The safe Layer A version is just:

```text
a declared continuation fact changes while the proposed summary stays fixed.
```

That is standard non-factorization.

## Existing Bridge

The module proves:

```text
TargetObstructedByPresentation target present
<->
ContinuationDeformation present target
```

So target obstruction is not a separate mystery. It is the same non-factorization
schema applied to a presentation and target.

## Non-Claims

This does not define:

```text
deformer object;
agency;
identity;
valuerhood;
value;
Omega.
```

Those require additional structure beyond finite non-factorization.

## Related Notes

- [presentation_soundness_pattern_v0.md](presentation_soundness_pattern_v0.md)
- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [nonfactorization_witness_index_v0.md](nonfactorization_witness_index_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
