# Marginal Coupling Non-Factorization v0

Status: finite baseline witness note

This note records a small finite theorem:

```text
same local marginals
different joint coupling
```

Therefore the joint factorization/coupling target does not factor through the
local marginal summary.

## Lean Location

```text
formal/lean/OmegaProper/BaselineWitnesses/MarginalCouplingNonFactorization.lean
```

## Tables

The witness uses two binary joint tables with integer weights.

Product-uniform table:

```text
1 1
1 1
```

Diagonal-coupled table:

```text
2 0
0 2
```

Both have the same local marginals:

```text
row counts = [2, 2]
col counts = [2, 2]
total      = 4
```

But they differ on joint factorization.

## Computed Summary

```text
MarginalSummary:
  rowCounts
  colCounts
  total
```

Lean proves:

```text
marginalSummary productUniform =
  marginalSummary diagonalCoupled
```

## Computed Target

The target is `jointFactorizes`.

It uses integer cross-multiplication to avoid fractions:

```text
weight(a,e) * total = row(a) * col(e)
```

Lean proves:

```text
jointFactorizes productUniform = true
jointFactorizes diagonalCoupled = false
```

## Non-Factorization

The main theorem is:

```text
marginalSummary_jointFactorization_nonFactorization
```

Meaning:

```text
joint factorization does not factor through local marginal summary
```

## Why This Matters

This is the first finite coupling witness for the boundary/presentation track.

It does not identify an agent, object, self, or boundary. It only shows that a
local/marginal view can miss joint structure.

This is the disciplined finite version of:

```text
do not infer joint coupling from local marginals
```

Later work can ask when such joint coupling is also consequence-relevant,
presentation-invariant, viable, or alignment-relevant.

## Claim Boundary

This note does not define value, agency, identity, recoverability, boundary
realism, or Omega proper.

It only proves a finite non-factorization witness for marginal summaries and
joint coupling.
