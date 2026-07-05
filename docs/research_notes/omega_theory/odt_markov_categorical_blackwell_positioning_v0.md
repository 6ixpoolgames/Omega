# ODT Markov-Categorical Blackwell Positioning v0

Status: positioning note / stochastic-Blackwell roadmap boundary
Scope: deterministic and finite-rational stochastic Blackwell-shaped bridges
Claim boundary: not full stochastic Blackwell theory, not Le Cam deficiency,
not Bayes risk, not expected utility, not final value, not aggregation, not
arbitration, not agency, not identity, not quantum mechanics, not Omega
validation

## Purpose

ODT1 now has two Blackwell-shaped bridges:

```text
deterministic:
  factorization iff universal policy simulation

finite rational stochastic:
  garbling -> randomized policy compilation with preserved state/action mass
```

The second bridge is deliberately one-way. This note records where it sits
relative to Markov-categorical comparison of statistical experiments.

## External Anchor

The Markov-categorical Blackwell line studies statistical experiments and
Blackwell-Sherman-Stein style comparison in categorical probability.

The relevant external lesson is that:

```text
experiments, garblings, and decision functionals can be organized as categorical
maps rather than as bespoke matrix manipulations.
```

Reference: [Representable Markov Categories and Comparison of Statistical
Experiments in Categorical Probability](https://arxiv.org/abs/2010.07416).

## Current ODT Position

The current finite-rational Lean bridge proves only:

```text
E --garbling--> F
policy over F observations
  -> compiled randomized policy over E observations
  -> same induced action mass at every state.
```

This is enough to show that the ODT1 stochastic surface is compatible with the
easy direction of Blackwell comparison:

```text
if F is a garbling of E, then E can simulate F-observation randomized policies.
```

It does not prove the converse:

```text
universal decision performance comparison -> garbling.
```

It also does not lift action-mass equality to a final outcome/value theorem.
That would require a declared outcome surface, valuation discipline, and risk
or expectation semantics.

## Why Not Prove The Converse Now?

The stochastic converse is not just an algebraic rearrangement. It normally
routes through separation/duality arguments and a precise decision-problem
class.

Opening it now would blur three surfaces the repo currently keeps separate:

```text
stochastic experiment comparison;
ODT1 outcome-surface dominance;
ODT2 arbitration/valuation authority.
```

The current forward bridge is sufficient for the ODT stabilization phase.

## Future Route

A future stochastic closure pass should decide, before coding, which statement
is desired:

```text
1. finite matrix Blackwell-Sherman-Stein theorem;
2. Markov-categorical wrapper theorem;
3. Le Cam / approximate deficiency comparison;
4. ODT-specific outcome-surface conservativity theorem.
```

Those are related but not interchangeable.

## Nonclaims

This note does not claim:

```text
full stochastic Blackwell equivalence;
Le Cam deficiency;
Bayes-risk or expected-utility theorem;
that action mass is final value;
that the ODT preorder or valuation class is correct;
aggregation, arbitration, standing, agency, identity, selfhood, quantum
mechanics, or Omega validation.
```

## Public Compression

ODT currently proves the easy finite-rational stochastic Blackwell direction:
garbling compiles randomized policies while preserving state/action mass. The
full stochastic converse is a later theorem target, not a landed claim.
