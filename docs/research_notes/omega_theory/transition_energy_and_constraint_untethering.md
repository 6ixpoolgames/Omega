# Transition Energy and Constraint Untethering

Status: theory / substrate-design note  
Scope: RFS-MB0 substrate untethering before horizon-transport instrument promotion  
Claim boundary: not Omega detection, not agent detection, not value detection, not identity detection, not candidate promotion

## 0. One-sentence update

The current relation-generated substrate still uses hand-built constraint templates; before promoting the horizon-transport instrument, the project should test whether matched-marginal-separated horizon transport persists when transformations are generated from generic transition-energy families instead of a named constraint vocabulary.

In compact form:

```text
current substrate:
  finite symbolic states + hand-built constraint templates + scored edge selection

next substrate repair:
  finite symbolic states + local proposal kernel + transition energy E(s,t)

purpose:
  separate horizon-transport phenomena from artifacts of modular/equality/difference constraint grammar
```

## 1. Why this note exists

The H128 horizon-transport branch surfaced the cleanest empirical object in the project so far:

```text
matched-marginal-separated horizon transport;
stable short horizons;
amplified-aligned middle/deep horizons;
no terminal saturation through H=128;
no empirical weakened/rerouted/reopened/collapsed rows under the tested ladder.
```

But the substrate that produced this object is not foundation-free.

The current relation generator is neutral-ish but still uses hand-built constraint templates:

```text
local_modular_sum_preference
local_equality_relation
local_difference_relation
```

The generated instances vary coordinates, residues, weights, seeds, roughness, and graph realization. However, the available forms of law are still selected by us.

This creates a live artifact risk:

```text
The detected horizon-transport response surface may partly reflect the chosen symbolic constraint grammar.
```

The right repair is not to abandon the substrate. It is to test the instrument across more primitive transition-generation principles.

## 2. Distinction, relation, asymmetry, and transition energy

The primitive stack remains:

```text
distinction:
  states can differ

relation:
  some transformations connect states

asymmetry:
  transformations can have non-equivalent future consequences
```

A transition-energy formalism makes the relation-generation step explicit.

Let:

```text
X:
  finite state space

Q(s -> t):
  local proposal kernel / neighborhood relation

E(s,t):
  transition energy or transition score

R:
  selection rule that converts Q and E into directed edges
```

Then:

```text
s -> t exists if t is selected from Q(s) by R using E(s,t)
```

For example:

```text
edges(s) = top_m candidates t in Q(s) with lowest E(s,t)
```

or probabilistically:

```text
P(s -> t) proportional to exp(-beta E(s,t))
```

Here `energy` or `cost` means edge-selection score. It is not moral value, utility, thermodynamic energy, or Omega.

## 3. Distance is not the same as cost

A distance or metric defines how states are near or far:

```text
d(s,t):
  how different states s and t are
```

A transition energy defines how favored a directed transformation is:

```text
E(s,t):
  how easy / likely / selected the move s -> t is under the substrate law
```

A simple distance is often symmetric:

```text
d(s,t) = d(t,s)
```

A transition energy can be directional:

```text
E(s,t) != E(t,s)
```

For instance:

```text
E(s,t) = d(s,t) + beta * (V(t) - V(s)) + epsilon * roughness(s,t)
```

If `V(t) < V(s)`, moving from `s` to `t` can be cheaper than moving from `t` to `s`.

This induces asymmetry without requiring a named symbolic constraint like equality or modular sum.

## 4. Invariants as minimal lawlike structure

The point of `E(s,t)` is not to remove all assumptions. That is impossible.

The point is to make assumptions:

```text
explicit;
generic;
sweepable;
less semantically loaded;
less tied to a hand-picked law vocabulary.
```

Invariants are a principled way to define a universe-like substrate. They specify what is conserved, approximately conserved, expensive to change, or structurally smooth.

Examples:

```text
locality:
  nearby states are easier to reach than distant states

out-degree:
  each state has bounded branching

smooth potential:
  neighboring states have related scalar field values

budget / conservation:
  some total mass, histogram, Hamming weight, or coarse macro-statistic is hard to change

reversibility fraction:
  some transitions have return paths while others do not

roughness:
  deterministic seeded micro-variation breaks ties and near-ties
```

These are still design choices. The virtue is that they are generic macro-structure choices rather than named symbolic laws.

## 5. Why this is not a retreat from asymmetry

Asymmetry is not lost when hand-built constraints are removed.

Asymmetry can enter through:

```text
potential descent/ascent terms;
non-symmetric E(s,t);
directed edge selection from local neighborhoods;
bounded out-degree selection;
roughness-induced tie-breaking;
reversibility fraction less than 1;
macro-invariant gradients or budgets.
```

The important distinction is:

```text
current substrate asymmetry:
  direction shaped partly by hand-built symbolic constraint templates

transition-energy substrate asymmetry:
  direction shaped by generic local geometry, potentials, invariants, and edge-selection rules
```

The second is more appropriate for testing whether horizon transport is a general future-field phenomenon rather than an artifact of the constraint grammar.

## 6. Candidate transition-energy families

### E0: locality only

Minimal null-like substrate.

```text
E_0(s,t) = d_H(s,t) + epsilon * roughness(s,t)
```

Expected behavior:

```text
may diffuse or saturate trivially;
may be too structureless;
useful as a lower baseline.
```

### E1: locality plus smooth random potential

Best first serious replacement for the current constraint grammar.

```text
E_1(s,t) = d_H(s,t) + beta * (V(t) - V(s)) + epsilon * roughness(s,t)
```

where `V` is a seeded smooth random field over `X`.

Expected behavior:

```text
locality, directionality, smooth landscape structure, and roughness;
no named modular/equality/difference laws.
```

### E2: locality plus budget / conservation

Adds a generic macro-invariant.

```text
E_2(s,t) = d_H(s,t) + lambda * |B(t) - B(s)| + epsilon * roughness(s,t)
```

where `B` may be:

```text
symbol histogram;
Hamming weight;
total coordinate mass;
coarse resource budget.
```

Expected behavior:

```text
lawlike structure through approximate conservation;
not tied to specific symbolic constraints.
```

### E3: maximum-entropy local transition ensemble

Longer-term target.

Specify macro constraints only:

```text
state count;
locality radius;
out-degree distribution;
reversibility fraction;
smoothness level;
roughness level;
optional energy marginal distribution.
```

Then sample transition graphs from the maximum-entropy ensemble satisfying those macros.

Expected behavior:

```text
best long-term anti-smuggling substrate;
more implementation work;
less appropriate as the first repair unless E0/E1/E2 are insufficient.
```

## 7. What must be tested

The core empirical question is:

```text
Does matched-marginal-separated horizon transport with aligned amplification persist when the named constraint vocabulary is removed?
```

Possible outcomes:

```text
persists across E1/E2:
  horizon transport is less likely to be a grammar artifact

appears only in current constraint-template substrate:
  grammar-artifact risk is high

locality-only trivial, E1 works:
  generic smooth landscape structure may be sufficient

E2 works but E1 does not:
  conservation/budget-like invariants may be needed

none work:
  current H128 object may depend on hand-built constraint grammar or current detector assumptions
```

## 8. Relationship to the H128 result

The H128 result remains important.

It established the current live object:

```text
matched-marginal-separated horizon transport with horizon-dependent aligned amplification
```

But before promoting the instrument beyond the current substrate family, the project must ask:

```text
Is the object substrate-general, or constraint-template-specific?
```

This note says the next repair should be substrate untethering, not immediate promotion.

## 9. Claim boundary

Even if the transition-energy substrates reproduce aligned amplification, the result would not show:

```text
Omega;
agency;
valuerhood;
identity;
life;
self-replication;
graph-channel causality;
holdout generalization.
```

It would show only:

```text
horizon-transport response structure is not limited to the original hand-built constraint vocabulary.
```

That would be a major instrument/substrate robustness result, but still not a candidate claim.

## 10. 3P check

### Principled

Transition energy makes the lawlike substrate assumptions explicit: state space, locality, invariants, potential, roughness, and selection rule.

### Parsimonious

Start with the smallest generic families: locality only, locality plus smooth potential, and locality plus budget/conservation.

### Predictive

Each family predicts a different horizon-transport response profile. If the H128 object is not grammar-artifact, some version of it should persist beyond the original constraint-template substrate.

## 11. Bottom line

The current instrument is strong enough to surface a clean horizon-transport response object.

The substrate is not yet clean enough to promote that object broadly.

The next principled move is:

```text
replace hand-built constraint templates with explicit transition-energy families,
then test whether horizon transport and aligned amplification persist.
```
