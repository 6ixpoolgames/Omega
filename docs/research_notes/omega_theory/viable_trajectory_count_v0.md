# Viable Trajectory Count v0

Status: finite adapter count pilot
Scope: exact finite transition systems, declared safety predicates, finite horizons
Claim boundary: not value, not agency, not entropy, not Omega validation

## Purpose

The dynamic-equivariance audit checks whether a presentation commutes with
transition structure. The next small object is a count profile over the
transition structure itself:

```text
how many safe finite trajectories exist at each horizon?
```

This is the finite, pre-entropy floor beneath later "lushness" language. It
does not take a limit, does not define a value measure, and does not claim that
more trajectories are morally better. It only exposes a trajectory-count shape
for a declared finite dynamics and safety predicate.

## Adapter Surface

The finite relational adapter now includes:

```text
viable_trajectory_count
viable_trajectory_count_comparison
```

Given:

```text
next : State -> State -> Prop
safe : State -> Prop
horizon : Nat
optional start_predicate : State -> Prop
```

it counts words of edge length `0..horizon`:

```text
x0, x1, ..., xn
```

such that every state is safe and every adjacent pair is a declared transition
edge. If `start_predicate` is absent, every safe state may start a word.

The audit reports:

```text
count_profile
final_count
safe_state_count
safe_start_state_count
transition_edge_count
nonempty_at_horizon
```

and can check expected count profiles through:

```text
expected_count_profile
expected_final_count
```

The comparison audit adds:

```text
exact_transition
exact_safety
presentation
abstract_transition
abstract_safety
horizon
```

and reports:

```text
exact_count_profile
abstract_count_profile
count_profile_delta
inflates
hides
equivariant
```

The `equivariant` flag is imported from the dynamic-presentation audit. Count
equality is not claimed to follow from equivariance alone, because a
many-to-one presentation can legitimately compress state-word counts. The
current strictness cases therefore use identity presentations: any count
distortion there comes from bad abstract dynamics, not from quotienting states.

## Current Generated Cases

```text
generated_viable_trajectory_count_cycle:
  a two-state cycle with both states safe has profile [2, 2, 2, 2]
  through horizon 3.

generated_viable_trajectory_count_branching:
  a fully branching two-state safe graph has profile [2, 4, 8, 16]
  through horizon 3.

generated_viable_count_inflation:
  identity presentation, exact cycle, abstract graph with phantom self-edges;
  abstract profile [2, 4, 8] inflates exact profile [2, 2, 2].

generated_viable_count_hiding:
  identity presentation, exact fully branching graph, abstract cycle missing
  self-edges; abstract profile [2, 2, 2] hides exact profile [2, 4, 8].
```

These two cases establish only that the adapter can distinguish finite safe
trajectory-count profiles and detect simple non-equivariant distortions. They
are not yet a pressure or entropy theorem.

## Next Uses

The useful next bridges are:

```text
dynamic equivariance + viable count:
  only compare trajectory counts through presentations that commute with
  dynamics.

unsound / non-equivariant presentation:
  show how a bad abstract dynamics can inflate or hide safe trajectory counts.

finite horizon profile:
  use count_profile as a finite approximation surface before any asymptotic
  entropy/lushness claim.
```

## Related Notes

- [dynamic_presentation_equivariance_v0.md](dynamic_presentation_equivariance_v0.md)
- [finite_relational_adapter_design_v0.md](finite_relational_adapter_design_v0.md)
- [presentation_fact_closure_v0.md](presentation_fact_closure_v0.md)
- [stochastic_continuation_loss_v0.md](stochastic_continuation_loss_v0.md)
