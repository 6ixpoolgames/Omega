# OmegaAdapters Probabilistic Non-Erasure Native v0

Status: Lean-checked native adapter layer
Scope: finite thresholded probabilistic non-erasure over declared requirement
sets

## Summary

This pass adds a small Lean layer for thresholded probabilistic non-erasure:

```text
formal/lean/OmegaAdapters/ProbabilisticNonErasureNative.lean
```

The central definition is:

```text
ProbNonErasing Req RecoveredAtThreshold
```

where `Req` is a finite requirement predicate over distinction tokens and
`RecoveredAtThreshold` is external evidence. The definition does not search for
a decoder, optimize over targets, or infer provenance. That evidence must come
from a declared registry, fixed policy, or explicitly classified measurement
layer.

## Checked Surface

The module checks:

```text
probNonErasing_mono_requirement:
  if Small subset Large and Large is probabilistically non-erasing, then Small
  is probabilistically non-erasing

exactSupport_nonErasing_transfers_to_prob:
  exact-support non-erasure transfers to probabilistic non-erasure only through
  an explicit bridge from exact recovery to threshold recovery

exactSupport_implies_thresholdedDecoderRecovers_100:
  exact support recovery gives thresholded decoder recovery at the 100 percent
  threshold

marginal_recovery_does_not_force_all_requirements:
  marginal requirement recovery does not force a larger joint-inclusive
  requirement set

thresholded_nonErasing_not_exactSupport:
  thresholded probabilistic non-erasure can hold while exact support recovery
  fails
```

## Evidence Boundary

RecoveredAtThreshold is external evidence. This prevents the non-erasure
definition from becoming self-validating:

```text
not built in:
  decoder existence
  registry success
  Bayes / optimized target search
  support exactness
  empirical provenance

required from outside:
  an already classified recovery predicate
```

This matches the current empirical artifacts:

```text
recovery_provenance_class
registry_digest
cascade_evidence_status
theorem_transfer_class
```

## Read

The theorem is intentionally simple. The value is structural: once recovery
evidence is supplied, non-erasure is monotone under requirement weakening. What
counts as recovery remains outside the theorem and must be supplied by the
appropriate presentation or registry-backed measurement package.

## Validation

```text
lake build OmegaAdapters: passed
```
