# Stochastic Continuation Loss v0

Status: finite adapter validation note
Scope: exact rational finite-horizon stochastic transition kernels
Claim boundary: synthetic finite Markov-kernel validation only; not MDP policy validation, not empirical substrate validation, not value, agency, alignment, or Omega validation

## Purpose

The first stochastic recovery layer is static: source states pass through a
finite stochastic channel into observations. The next bridge is continuation:

```text
state -> stochastic next state
finite horizon
target hit probability
before / after / stale / reflected transition kernels
```

This is not a policy or MDP layer. There are no actions yet. It asks whether
finite-horizon continuation facts are preserved, hidden, or reported under a
stochastic perturbation.

## Implemented Families

### Noisy Line-Grid Stale Hidden Hit Loss

A three-state noisy line grid has a finite-horizon hit probability:

```text
x0 -> x1 -> x2
```

At horizon `2`:

```text
before hit probability:    9/10
after hit probability:     1/10
loss amount:               4/5
stale abstraction reports: 9/10
reflected reports:         1/10
```

This is the stochastic analogue of deterministic hidden reachability loss:
a stale abstraction keeps reporting the old continuation fact after the exact
transition kernel has changed.

The family also exposes a presentation/fact closure check over finite-horizon
hit-status facts. Using threshold `1/2` at horizon `2`, the reflected
hit-status presentation preserves the after-kernel high-hit target:

```text
after_high_hit;
all_states.
```

Adding the stale hit-status presentation to the family removes the after-kernel
high-hit fact from the common target facts:

```text
common target facts under stale + reflected: all_states
```

The closure audit is run through the same finite relational
`presentation_fact_closure` engine used by the deterministic grid obstacle
pilot.

### Same Selected Hit Probability, Different Horizon Profile

Two kernels can share one selected hit-probability scalar while their
finite-horizon profiles differ:

```text
fast profile: {1: 3/4, 2: 3/4, 3: 3/4}
slow profile: {1: 1/2, 2: 3/4, 3: 7/8}
```

This blocks the shortcut:

```text
same hit probability at one horizon => same continuation profile
```

## Reproduction

Run:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_stochastic_continuation `
  --out-root .tmp\finite_relational_stochastic_continuation
```

The retained result summary is:

```text
../validation_results/finite_relational_stochastic_continuation_v0.json
```

## Why This Is Not Yet MDP Validation

This layer has:

```text
finite states;
fixed transition kernels;
finite horizons;
exact rational arithmetic.
```

It does not yet have:

```text
actions;
policies;
policy classes;
viability kernels under stochastic control;
learned transition estimates.
```

That restraint is deliberate. Stale-versus-reflected stochastic continuation
loss should be clean before policy-conditioned dynamics are added.

## Non-Claims

This layer does not claim:

```text
Gradient Ethics validation;
safe policy synthesis;
large-world stochastic transfer;
value, agency, or Omega.
```

It is a finite exact stochastic continuation audit surface.
