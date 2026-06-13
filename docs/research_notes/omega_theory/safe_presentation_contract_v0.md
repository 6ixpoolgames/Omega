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
```

If the contract holds, abstract reachability implies exact reachability.

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
```

If the contract holds, abstract viability implies exact viability.

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
```
