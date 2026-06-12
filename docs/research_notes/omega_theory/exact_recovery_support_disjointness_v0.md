# Exact Recovery as Support Disjointness v0

Status: branch exploration note

This note records the standard compression behind exact declared recovery for
support-style channels.

## Setup

Let:

```text
X        source states
Y        output states
D        declared source classes
O        declared target observations
K        X -> Y -> Prop          support relation
d        X -> D                  declared source distinction
o        Y -> O                  declared target observation
decoder  O -> D
```

Exact declared recovery means:

```text
forall x y, K x y -> decoder (o y) = d x
```

## Support-Disjointness Criterion

Observed support disjointness says:

```text
if x1 can produce y1
and x2 can produce y2
and o(y1) = o(y2)
then d(x1) = d(x2)
```

In words:

```text
outputs with the same declared observation never arise from different declared
source classes.
```

## Theorem

The Lean theorem proves:

```text
ExactRecoveryExists K d o <-> ObservedSupportDisjoint K d o
```

with an explicit `[Nonempty D]` assumption.

## Why `[Nonempty D]` Appears

The reverse direction constructs a total decoder:

```text
decoder : O -> D
```

For observations that actually occur on the support relation, support
disjointness makes the decoded declared class well-defined.

For observations that never occur, exact recovery imposes no constraint. A
total decoder still needs some value there, so Lean requires `[Nonempty D]` to
choose an arbitrary fallback.

This fallback is not a recovery claim. It is bookkeeping for unreachable
observations.

## Lean Location

```text
formal/lean/OmegaProper/BaselineWitnesses/ExactRecoverySupport.lean
```

## Relation to Registry-First Discipline

The theorem describes exact recovery for a fixed declared target observation.
It should not be confused with optimized recovery:

```text
declared recovery:
  the predeclared observation/decoder works

optimized recovery:
  some observation/decoder found after search works
```

The registry-first branch exists to keep those claims separate.
