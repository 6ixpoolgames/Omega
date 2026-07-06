# Ensemble Span Protocol v0

Status: preregistration / finite joint-tier instrument protocol
Scope: finite integer-vector ensembles, marginal scalar controls, span/orientation detectors, and negative controls
Claim boundary: not value, not standing, not agency, not population ethics, not aggregation, not relational surplus, not population optimum, not Omega validation

## Purpose

This sprint tests whether ensemble orientation / diversity can separate finite
ensembles after matching marginal scalar summaries.

Question:

```text
Can population/ensemble structure contain certified information that is not
recoverable from per-valuer scalar summaries?
```

This is an instrument sprint. It does not define population value or standing.

## Correction

Pure span is not census-blind if the census includes full per-valuer vectors.

If every valuer's full coordinate vector is known, then the span is determined.
The honest target is therefore:

```text
same marginal scalar census;
same summed per-valuer amount;
different ensemble orientation / span.
```

Not:

```text
same full vector multiset;
different pure span.
```

The latter would require relational composability or coupling data beyond pure
span. That is explicitly out of scope.

## Objects

The finite harness uses:

```text
Axis:
  a finite coordinate label.

ValuerVector:
  an integer vector over declared axes.

Ensemble:
  a finite list of valuer vectors over the same axes.

MarginalSummary:
  scalar controls that ignore orientation:
    valuer count;
    per-valuer L1 norm multiset;
    total L1 amount;
    max individual L1 norm.

SpanProfile:
  exact rank, Gram matrix, Gram determinant, axis supports, and vector census.

SpanOrder:
  span-inclusion, checked by exact rational row rank:
    span(left) includes span(right) iff rank(left) = rank(left union right).
```

Scalar detectors such as rank and Gram determinant are useful diagnostics.
They are not promoted as value or invariant population measures.

## Verdicts

```text
separated:
  matched marginal-scalar census, different ensemble span/order.

reduces:
  apparent span difference is already visible in the declared marginal controls.

ill-posed:
  span/order cannot be defined cleanly enough for the finite harness.
```

## Candidate Witness

Axes:

```text
A, B
```

Redundant ensemble:

```text
v1 = A
v2 = A
```

Orthogonal ensemble:

```text
v1 = A
v2 = B
```

Matched marginal scalar controls:

```text
valuer count: 2 = 2
per-valuer norm multiset: {1, 1} = {1, 1}
summed marginal amount: 2 = 2
max individual capacity: 1 = 1
```

Expected separation:

```text
redundant span rank: 1
orthogonal span rank: 2
```

Reading:

```text
more of the same and different axes are not equivalent, even when scalar
population summaries match.
```

## Diminishing Returns Witness

Base:

```text
{A}
```

Correlated addition:

```text
{A} + A
```

Orthogonal addition:

```text
{A} + B
```

Expected:

```text
correlated addition: rank gain 0
orthogonal addition: rank gain 1
```

This supports only a coverage-geometry claim:

```text
the marginal span contribution of an added field depends on orientation
relative to the ensemble, not only individual magnitude.
```

It is not moral value.

## Negative Controls

Control 1:

```text
if all vectors are identical, span reduces to singleton orientation.
```

Control 2:

```text
if full vector census is identical, pure span cannot separate.
```

This second control is load-bearing. It prevents pure span from being mistaken
for relational composability.

## Kill Condition

If no matched marginal-control pair is found, report `reduces` or `ill-posed`.
Do not claim a joint-tier coordinate.

If the witness depends on changing marginal scalar controls, the sprint fails.

## Nonclaims

This protocol does not claim:

```text
population value;
standing;
moral aggregation;
relational surplus;
patienthood;
agency;
optimal population composition;
large-deformer ethics;
Omega validation.
```

## Public Compression

The ensemble-span pilot tests whether redundant and orthogonal ensembles can
separate after marginal scalar summaries are matched. A positive result makes
ensemble orientation a live joint-tier instrument, not a population-value
theory.
