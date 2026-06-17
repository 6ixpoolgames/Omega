# Approximation Contract v0

Status: active compression note
Scope: generic sound/complete approximation contracts
Claim boundary: not proof that an abstraction is correct; not value, agency, or Omega validation

## Purpose

This note documents:

```text
formal/lean/OmegaProper/Trajectory/ApproximationContract.lean
formal/lean/OmegaProper/Trajectory/ProfileApproximation.lean
```

The compression is:

```text
sound approximation:
  abstract claim -> exact claim

complete approximation:
  exact claim -> abstract claim
```

## Generic Form

```text
SoundApprox Exact Abstract :=
  forall i, Abstract i -> Exact i

CompleteApprox Exact Abstract :=
  forall i, Exact i -> Abstract i
```

This is the standard approximation shape behind the existing profile
abstraction layer.

## Profile Instances

For profile abstraction, the index type is ordered fragment pairs:

```text
PairIndex S.Fragment := S.Fragment x S.Fragment
```

Then:

```text
SoundAllows P
<->
SoundApprox (ExactAllowClaim S) (AbstractAllowClaim P)

SoundBlocks P
<->
SoundApprox (ExactBlockClaim S) (AbstractBlockClaim P)

CompleteForAllows P
<->
CompleteApprox (ExactAllowClaim S) (AbstractAllowClaim P)

CompleteForBlocks P
<->
CompleteApprox (ExactBlockClaim S) (AbstractBlockClaim P)
```

## Why This Matters

This compresses profile abstraction into a standard mathematical idiom:

```text
no false positives = soundness;
no missed exact facts = completeness.
```

The previous local profile names remain useful, but the shared contract is now
explicit.

## Non-Claims

Soundness and completeness are contracts against declared exact facts. They do
not by themselves prove that the declared exact facts are the right facts for a
real substrate.

## Related Notes

- [presentation_soundness_pattern_v0.md](presentation_soundness_pattern_v0.md)
- [standard_core_compression_v0.md](standard_core_compression_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
