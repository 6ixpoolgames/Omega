# Relational Composability Protocol v0

Status: preregistration / finite coupling-instrument protocol
Scope: finite individual vectors, fixed full-vector census, explicit compatibility relations, and negative controls
Claim boundary: not value, not standing, not agency, not plurality theory, not population ethics, not aggregation, not population optimum, not Omega validation

## Purpose

This sprint tests whether a finite coupling/compatibility relation can separate
ensembles after the individual surface is held fixed.

Question:

```text
Can two ensembles have the same marginal scalar census, the same full vector
census, and the same pure span, while differing in declared joint
compatibility?
```

This is a coupling-instrument sprint. It does not define population value,
standing, plurality, agency, or aggregation.

## Relation To Ensemble Span

Ensemble span v0 showed that orientation can separate after marginal scalar
controls are matched. It also retained the negative control:

```text
same full vector census -> same pure span
```

Therefore any surplus with identical full vectors must live in additional
relational or coupling data. Relational Composability v0 tests that next layer.

## Objects

The finite harness uses:

```text
Axis:
  a finite coordinate label.

ValuerVector:
  an integer vector over declared axes.

CoupledEnsemble:
  a finite list of valuer vectors plus a declared compatibility relation
  between vector ids.

CompatibilityProfile:
  compatible pair count;
  connected component sizes;
  max compatible component size;
  isolated-valuer count;
  all-vectors-jointly-compatible flag;
  coupling matrix.
```

The compatibility relation is registered data. The sprint does not claim the
relation is morally correct or complete.

## Verdicts

```text
separated:
  matched marginal scalar controls, identical full vector census, equivalent
  pure span, and different compatibility profile.

reduces:
  apparent compatibility difference is already visible in vector or span
  controls.

ill-posed:
  compatibility cannot be defined cleanly enough for the finite harness.
```

## Candidate Witness

Axes:

```text
A, B
```

Individual vectors, held fixed:

```text
vA = A
vB = B
```

Compatible ensemble:

```text
compatible_pairs = {(vA, vB)}
```

Blocked ensemble:

```text
compatible_pairs = {}
```

Matched controls:

```text
same marginal scalar census;
same full vector census;
same pure span;
same span rank.
```

Expected separation:

```text
compatible pair count: 1 vs 0
max compatible component size: 2 vs 1
all vectors jointly compatible: true vs false
```

## Negative Control

If the full vector census and compatibility relation are identical, this
instrument must not separate the ensembles:

```text
same full vector census + same coupling -> same compatibility profile
```

This blocks an overread. Relational composability v0 is not hidden value or
population ethics; it is a finite registered-coupling profile.

## Kill Condition

If the candidate pair only separates by changing individual vectors, marginal
scalar controls, or pure span, the sprint reports `reduces` or `ill-posed`.

Do not claim a relational coordinate unless the full individual surface is held
fixed.

## Nonclaims

This protocol does not claim:

```text
value;
standing;
agency;
plurality theory;
population ethics;
aggregation;
population optimum;
Omega validation.
```

## Public Compression

Relational Composability v0 tests the first coupling coordinate beyond pure
span: same individual vectors and same span, different declared compatibility
relation. It is an instrument for joint structure, not a value theory.
