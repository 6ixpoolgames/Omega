# Omega Decision Stochastic Blackwell v0

Status: finite rational forward bridge / ODT1 theorem extension
Scope: stochastic garbling implies randomized-policy simulation with preserved
state/action mass
Claim boundary: not full stochastic Blackwell theorem, not Le Cam deficiency,
not probabilistic comparison iff all decision problems, not Bayes risk, not
expected utility, not final value, not correct valuation class, not
aggregation, not arbitration, not agency, not identity, not valuerhood, not
moral standing, not quantum mechanics, not Omega validation

## Purpose

This note records the first stochastic Blackwell-shaped bridge in the ODT
stack.

The theorem is deliberately one-way:

```text
finite rational garbling
  -> randomized policy compilation
  -> same induced state/action mass
```

It does not prove the full stochastic Blackwell theorem or Le Cam deficiency.

## Finite Rational Experiments

A stochastic experiment is an exact rational row-stochastic channel:

```text
E : State -> ObsE -> Q
F : State -> ObsF -> Q
```

Each row sums to `1`, and each entry is nonnegative.

## Garbling

`F` is a garbling of `E` when there is a finite rational transition:

```text
G : ObsE -> ObsF -> Q
```

such that:

```text
F(s, f) = sum_e E(s, e) * G(e, f)
```

for every state `s` and coarse observation `f`.

Reading:

```text
Observe through E, then stochastically post-process through G.
```

## Randomized Policy Compilation

Given a randomized policy over the coarser observation:

```text
pi_F : ObsF -> Act -> Q
```

the compiled policy over the finer observation is:

```text
pi_E(e, a) = sum_f G(e, f) * pi_F(f, a)
```

The Lean file proves that `pi_E` is again a valid randomized policy when
`pi_F` and `G` are row-stochastic.

## Induced Action-Mass Preservation

The induced action mass at a state is:

```text
Mass(E, pi, s, a) = sum_e E(s, e) * pi(e, a).
```

The landed theorem proves:

```text
Mass(E, compile(pi_F), s, a)
  =
Mass(F, pi_F, s, a)
```

for every state `s` and action `a`.

This is the stochastic analogue of deterministic policy simulation, stated at
the action-distribution level rather than as equality of deterministic
statewise actions.

## What This Recovers

This recovers the easy direction of stochastic Blackwell comparison:

```text
garbling
  -> no loss for randomized policy behavior expressible through the coarser
     experiment
```

The proof is finite and exact-rational. It is an algebraic associativity and
sum-rearrangement theorem.

## What This Does Not Claim

This note does not claim:

```text
full stochastic Blackwell iff theorem;
Le Cam deficiency;
Farkas/separation theorem;
Bayes risk theorem;
expected utility theorem;
that the action distribution is the final outcome surface;
that risk attitudes are settled;
ODT2 arbitration;
standing or valuerhood;
agency or identity;
quantum mechanics;
Omega validation.
```

## Public Compression

Stochastic Blackwell v0 proves the forward simulation direction: if a finite
rational experiment is a garbling of a finer experiment, then every randomized
policy over the garbled observation compiles into a randomized policy over the
finer observation with the same induced action distribution.

