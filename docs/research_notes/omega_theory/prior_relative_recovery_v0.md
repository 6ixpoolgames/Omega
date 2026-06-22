# Prior-Relative Recovery v0

Status: Lean theorem-spine checkpoint
Scope: expected deterministic recovery under declared rational finite source priors
Claim boundary: not robust recovery, not empirical prior validity, not value, not agency, not identity, not Omega validation

## Purpose

The recovery layer now separates:

```text
worst-case source thresholds;
robust ambiguity-set thresholds;
prior-relative expected thresholds.
```

The prior-relative object is:

```text
ExpectedRecoveryExistsAt mu C target observe tau
```

meaning:

```text
there exists a deterministic decoder whose expected success under the declared
source prior mu is at least tau.
```

The allowed-decoder-class form is:

```text
ExpectedRecoveryExistsInAt mu C target observe Allowed tau
```

## Lean Location

Main file:

```text
formal/lean/OmegaProper/Recovery/Prior.lean
```

Imported by:

```text
formal/lean/OmegaProper/Recovery.lean
```

## Proved Shape

The Lean layer proves:

```text
Expected success is nonnegative when the profile is nonnegative.
Expected success is at most 1 when the profile is pointwise at most 1.
Worst-case threshold recovery implies prior-relative expected threshold
  recovery under any declared prior.
ExpectedRecoveryExistsAt is monotone downward in threshold.
ExpectedRecoveryExistsInAt is monotone downward in threshold.
ExpectedRecoveryExistsAt is the unrestricted ExpectedRecoveryExistsInAt
  specialization.
Point-mass priors reduce expected success to source success at the selected
  source.
```

The examples layer also proves the finite strictness witness:

```text
high expected recovery under a skewed declared prior
does not imply worst-case recovery.
```

## Interpretation

Prior-relative recovery is an average-case guarantee over a supplied prior.
It is not a replacement for worst-case or robust recovery. It answers a
different question:

```text
how much success does this decoder get under this declared source weighting?
```

The prior is supplied structure and must be justified by the adapter/provenance
layer before it is used in an empirical claim.

## Claim Boundary

This layer does not claim:

```text
that the prior is empirically correct;
that high expected success protects every source;
that expected recovery is a value function;
that expected recovery is an alignment criterion;
Omega validation.
```
