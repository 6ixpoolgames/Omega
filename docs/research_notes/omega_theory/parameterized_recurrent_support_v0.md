# Parameterized Recurrent Support v0

Status: formal checkpoint note
Scope: bounded finite family for recurrent support carrying and one-way loss
Claim boundary: not infinite-scale behavior, not agency, not identity, not Omega validation

## Thesis

The two-state recurrent-support loss witness is not the only finite instance of
the pattern. The Lean stack now includes a bounded finite family of supports of
size `n + 2`.

For every `n`, the full bounded cycle:

```text
0 -> 1 -> 2 -> ... -> n + 1 -> 0
```

recurrently carries the declared consequence distinction between `0` and `1`.

The broken bounded dynamics:

```text
0 -> 1 -> 2 -> ... -> n + 1 -> n + 1
```

preserves endpoint viability and the forward path from `0` to `1`, but removes
the return path from `1` to `0`. Therefore recurrent carrying of the declared
distinction is lost.

## Lean location

```text
formal/lean/OmegaProper/Trajectory/ParameterizedRecurrentSupport.lean
```

The central theorem is:

```text
parameterized_recurrent_support_loss_witness
```

It packages, for every `n : Nat`:

```text
full bounded cycle recurrently carries 0/1;
broken bounded dynamics keeps 0 viable;
broken bounded dynamics keeps 1 viable;
broken bounded dynamics keeps the forward internal path 0 -> 1;
broken bounded dynamics has no internal path 1 -> 0;
therefore broken bounded dynamics destroys recurrent support carrying.
```

## Why this matters

The previous loss/restoration triptych was intentionally tiny. That made the
proofs readable, but it left an obvious concern:

```text
is recurrent-support loss just a two-state artifact?
```

This parameterized family answers that concern for a simple finite class. The
lesson persists across arbitrarily many finite intermediate states:

```text
endpoint viability plus forward reachability still does not imply recurrent
support carrying.
```

The missing return path is the load-bearing fact.

## What this does not prove

This is still a bounded finite family, not a theorem about arbitrary infinite
worlds, arbitrary perturbations, arbitrary supports, or empirical substrates.

It also does not define:

```text
identity;
agency;
deformer structure;
valuerhood;
alignment;
Omega proper.
```

It strengthens the local perturbation floor by showing the basic loss pattern
scales across a declared finite family.

## Relation to the perturbation floor

This note should be read immediately after:

```text
recurrent_support_perturbation_floor_v0.md
```

That note summarizes the local calculus:

```text
support, loss, preservation, restoration, and rerouting
```

This parameterized witness adds:

```text
finite-family persistence of the one-way-loss pattern
```

without changing the claim boundary.

## Next targets

The next useful extensions are:

1. Support extension:
   carrying transfers from support `C` into a larger support `D`.

2. Support lineage:
   support `C` hands off carrying to a different support `D`.

3. Successor distinctions:
   the exact pair is not preserved, but a translated distinction is.

4. Perturbation budget:
   minimum removals needed to destroy recurrent carrying.
