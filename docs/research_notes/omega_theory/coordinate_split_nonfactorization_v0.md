# Coordinate-Split Non-Factorization v0

Status: branch exploration note

This note states the common finite-witness template behind many retained
baseline witnesses.

## Template

Let the finite carrier split into:

```text
X = D x N
```

where:

```text
D = declared coordinate
N = nuisance coordinate
```

Construct two systems:

```text
S_D:
  exposes / carries D

S_N:
  exposes / carries N
```

A coordinate-symmetric baseline summary cannot distinguish these two systems:

```text
f(S_D) = f(S_N)
```

but the declared target can:

```text
g(S_D) != g(S_N)
```

Therefore:

```text
NonFactorization f g
```

The target does not factor through the baseline summary.

## Boolean Case

The first Lean version uses the existing four-point carrier:

```text
X2 = Bool x Bool
```

with:

```text
declaredFirstSystem:
  exposes the first bit

declaredSecondSystem:
  exposes the second bit
```

The module keeps the schematic `Unit` baseline as the minimal witness, but it
also adds a nontrivial finite count summary:

```text
source count = 4
outcome count = 2
compatible ordered pairs = 8
blocked ordered pairs = 8
```

This summary is still invariant under the declared/nuisance swap, but the
declared target distinguishes the two exposures. The Lean theorem proves this
nontrivial count baseline is also a non-factorization witness.

The module also records the profile contrast:

```text
declared-coordinate exposure blocks x00 ~ x10
nuisance-coordinate exposure allows x00 ~ x10
both exposures have the balanced two-by-two profile shape
```

## Lean Location

```text
formal/lean/OmegaProper/BaselineWitnesses/CoordinateSplit.lean
```

This is deliberately small. It is a template for several finite witness
families, not a proof that all retained witnesses reduce to one theorem.
