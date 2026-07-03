# Omega Decision Blackwell Conservativity v0

Status: deterministic finite conservativity wrapper / ODT1 theorem bridge
Scope: deterministic experiment factorization and policy-simulation preservation
Claim boundary: not stochastic Blackwell theory, not Le Cam deficiency,
not probabilistic garbling, not final value, not correct valuation class,
not aggregation, not arbitration, not agency, not identity, not valuerhood,
not moral standing, not probability-aware risk, not quantum mechanics,
not Omega validation.

## Purpose

This note records the deterministic finite Blackwell-shaped conservativity
wrapper for ODT1.

ODT1 compares already-licensed outcome surfaces by Hoare, Smyth, and Plotkin
dominance. The deterministic Blackwell wrapper shows that the usual
deterministic information order enters ODT1 as policy simulation:

```text
If experiment F factors through experiment E,
then every F-policy compiles into an E-policy
with the same statewise action and the same outcome surface.
```

This recovers deterministic finite Blackwell comparison as factorization. It
does not open stochastic Blackwell theory.

## Deterministic Experiments

A deterministic experiment is an observation map:

```text
E : State -> ObsE
F : State -> ObsF
```

`E` is at least as informative as `F` when `F` factors through `E`:

```text
exists k : ObsE -> ObsF,
  forall s, F(s) = k(E(s)).
```

Reading:

```text
Anything observable through F can be recovered from what E observes.
```

## Policy Compilation

Given:

```text
policy_F : ObsF -> Act
k        : ObsE -> ObsF
```

the compiled policy over the finer experiment is:

```text
compile(policy_F)(e_obs) = policy_F(k(e_obs)).
```

The Lean bridge proves statewise preservation:

```text
compile(policy_F)(E(s)) = policy_F(F(s)).
```

## Outcome Surface Preservation

For any deterministic outcome map:

```text
outcome : State -> Act -> W
```

the policy outcome surface is:

```text
{ w | exists s, w = outcome(s, policy(E(s))) }.
```

The Lean bridge proves:

```text
OutcomeSurface(E, compile(policy_F), outcome)
  =
OutcomeSurface(F, policy_F, outcome)
```

as predicate equivalence.

Consequently, the compiled and original policy surfaces are Hoare-equivalent,
Smyth-equivalent, and Plotkin-equivalent inside ODT1.

## Finite Strictness Example

The retained Lean example uses two states.

```text
identity experiment:
  observe(s) = s

constant experiment:
  observe(s) = unit
```

The identity experiment factors to the constant experiment. The constant
experiment does not factor back to the identity experiment.

In a matching task:

```text
state s0 requires action a0 for good
state s1 requires action a1 for good
```

the identity policy can produce the surface `{good}`. A fixed constant policy
can expose both `good` and `bad`. The theorem bridge separately shows that any
constant-observation policy compiled through the identity observation has the
same outcome surface as the original constant policy.

## What This Recovers

This recovers the deterministic, finite, factorization-shaped part of the
Blackwell order:

```text
more informative observation
  -> can simulate less informative observation
  -> preserves every policy outcome surface
  -> ODT1 dominance sees no loss for the compiled policy
```

## What This Does Not Claim

This note does not claim:

```text
stochastic Blackwell theory
Le Cam deficiency
probabilistic garbling
Bayes risk
expected utility
mixed policies
randomized actions
ODT2 arbitration
standing or valuerhood
aggregation
agency or identity
quantum mechanics
Omega validation
```

## Public Compression

Deterministic Blackwell comparison is recovered as factorization: if the
coarser experiment factors through the finer one, every coarser policy can be
run through the finer experiment with the same outcome surface.

