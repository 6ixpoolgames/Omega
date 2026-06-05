# OmegaAdapters Probabilistic Channel Cascade Evidence Native v0

Status: Lean-checked cascade evidence-object repair
Scope: finite path-ensemble evidence for probabilistic channel cascade bounds

## Purpose

This pass makes the finite cascade path ensemble an explicit theorem input.

The earlier cascade theorem already measured first-stage, second-stage, and
composite decoder error over the same path ensemble. This repair adds a generic
object:

```text
CascadeEvidence:
  finite path type
  path weight
  first-stage error predicate
  second-stage error predicate
  composite error predicate
```

The generic theorem consumes this object. It does not accept independently
normalized stage summaries.

## Lean Artifact

Added:

```text
formal/lean/OmegaAdapters/ProbabilisticChannelCascadeEvidenceNative.lean
```

Updated:

```text
formal/lean/OmegaAdapters/ProbabilisticChannel.lean
formal/lean/OmegaAdapters.lean
```

## Definitions

The evidence module defines:

```text
CascadeEvidence
CascadeEvidence.totalMass
CascadeEvidence.errorMass
CascadeEvidence.firstErrorMass
CascadeEvidence.secondErrorMass
CascadeEvidence.compositeErrorMass
CascadeEvidence.CompositeFailureCovered
```

## Checked Theorem Surface

The generic theorem is:

```text
CascadeEvidence.union_bound:
  if every composite failure is covered by a first-stage or second-stage
  failure on the same path, then composite error mass is bounded by first-stage
  plus second-stage error mass.
```

The channel bridge is:

```text
channelCascadeEvidence:
  builds a CascadeEvidence object from a finite natural-weight channel cascade

channelCascadeEvidence_covered:
  proves the channel evidence satisfies composite-failure coverage

channel_cascade_bound_from_evidence:
  obtains the channel cascade bound from the generic evidence theorem
```

## Anti-Misuse Boundary

This repair separates:

```text
valid theorem input:
  one weighted path ensemble with path-level error predicates

invalid shortcut:
  independently normalized first-stage, second-stage, and composite summary
  rates
```

Future empirical cascade audits should emit a path-ensemble artifact or a
lossless digest sufficient to reconstruct one. Summary tables can report rates,
but theorem transfer should cite the evidence object.

## Validation

Validated by:

```powershell
lake build OmegaAdapters
```
