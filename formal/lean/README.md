# Omega Formal Lean Sandbox

Status: local proof-assistant pressure test

This directory contains the first Lean 4 sandbox for the Omega formalism. It is
not the full quantale-presheaf formalization yet. The current target is a small
order-theoretic kernel that checks whether the prose recoverability lemmas can
actually be stated and proved without hidden assumptions.

## Local Toolchain

This workspace uses a portable Lean toolchain:

```powershell
.tools\lean-4.30.0\lean-4.30.0-windows\bin\lean.exe --version
```

Do not assume Lean is globally installed. From the repository root, use:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
```

Then build:

```powershell
cd formal\lean
lake build OmegaCore
```

## Current Checked Content

`OmegaCore/Basic.lean` defines:

```text
DistinctionFrame:
  minimal preorder-like distinction frame

ValueFrame:
  ordered tensor structure for asymmetry/support values

Recovers:
  structural pullback plus thresholded asymmetry support

NonErasing:
  every declared required distinction has a recovering witness
```

Checked lemmas:

```text
recoverability_weaken_source
recoverability_strengthen_target
non_erasure_monotonicity
compositional_recoverability
```

The file currently contains no `sorry`, `admit`, or Lean `axiom` declarations.

## Discipline Rule

Do not call a prose result "proved" in public-facing documentation unless the
corresponding Lean file checks without `sorry`.

Allowed weaker labels:

```text
formal scaffold
prose lemma
conjecture
adapter obligation
empirical hypothesis
```

## Next Formal Targets

1. Add finite examples that instantiate `DistinctionFrame` and `ValueFrame`.
2. Add a finite transition-system adapter sketch.
3. Add explicit failure examples where a theorem cannot be stated because an
   adapter lacks monotonicity, pullback functoriality, or compositional support.
4. Only then lift toward the full presheaf/profunctor/quantale kernel.
