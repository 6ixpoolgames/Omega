# Safe Presentation Contract v0

Status: foundational contract note

This note records the first packaged contract for using presentations in
reachability and viability claims.

This does not define value, agency, identity, alignment, or Omega proper.

## Lean Location

```text
formal/lean/OmegaProper/Trajectory/SafePresentationContract.lean
```

## Why A Contract Is Needed

The repo now has two kinds of discipline:

```text
consequence soundness:
  a presentation must not merge consequence-separated fragments

dynamics reflection:
  abstract targets/safety and steps must reflect back to exact targets/safety
  and exact steps
```

These answer different questions. A reachability or viability claim can need
both.

## Reachability Contract

```text
ReachabilitySafePresentationContract
```

packages:

```text
consequence_sound
target_reflects
step_reflects
```

Lean proves:

```text
reachabilityContract_reflects_reach
reachabilityContract_blocks_mergeSeparated_erasure
reachabilityContract_reflects_finitePath
reachabilityContract_lifts_finitePath_endpoint
```

If the contract holds, abstract reachability implies exact reachability.
It also blocks erasure of merge-separated consequence pairs, reflects finite
paths to target, and directly lifts abstract finite-path endpoints to exact
finite-path endpoints.

## Viability Contract

```text
ViabilitySafePresentationContract
```

packages:

```text
consequence_sound
safe_reflects
step_reflects
```

Lean proves:

```text
viabilityContract_reflects_viability
viabilityContract_blocks_mergeSeparated_erasure
viabilityContract_reflects_safePrefixes
viabilityContract_reflects_safePrefix
```

If the contract holds, abstract viability implies exact viability.
It also blocks erasure of merge-separated consequence pairs, reflects abstract
viability to arbitrarily long exact safe prefixes, and directly lifts finite
safe-prefix witnesses.

## Interpretation

This is not a magic guarantee that a presentation is useful or optimal.

It is a proof-carrying interface:

```text
if a presentation is used for a continuation claim,
it should carry the soundness/reflection obligations needed by that claim
```

The contract is the formal version of:

```text
no erased consequence distinctions
no invented targets or safety
no invented sustaining transitions
no invented finite-path witnesses
no invented safe-prefix witnesses
```

## Existing Negative Controls

The current phantom examples are rejected by the packaged contracts:

```text
PhantomReachability.mergePresentation_not_reachabilitySafeContract
PhantomViability.bad_presentation_not_viabilitySafeContract
```

The reachability example fails consequence soundness by merging
consequence-separated exact states. The viability example fails step
reflection by adding an abstract self-loop with no exact transition witness.

## Relation To Loss Visibility

This contract blocks fabricated continuation claims. It does not by itself name
the hidden-loss condition. The combined layer is:

```text
LossAwarePresentationContract.lean
```

which pairs this safe/reflection contract with loss visibility.
