# Transition Energy and Constraint Untethering

Status: theory / substrate-design note  
Scope: RFS-MB0 substrate untethering before horizon-transport instrument promotion  
Claim boundary: not Omega detection, not agent detection, not value detection, not identity detection, not candidate promotion

## 0. One-sentence update

The current relation-generated substrate still uses hand-built constraint templates. Before promoting the horizon-transport instrument, the project should test whether matched-marginal-separated horizon transport persists when transformations are generated from explicit transition-energy families instead of a named symbolic constraint vocabulary.

In compact form:

```text
current substrate:
  finite symbolic states + hand-built constraint templates + scored edge selection

next substrate repair:
  finite symbolic states + local proposal kernel + transition energy E(s,t)

purpose:
  separate horizon-transport phenomena from artifacts of modular/equality/difference constraint grammar
```

Terminology correction:

```text
Do not call the invariant-preserving family a budget family.
The theory concept is macro-invariant / asymmetry-preservation.
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

A transition-energy formalism makes relation generation explicit.

Let:

```text
X:
  finite state space

Q(s -> t):
  local proposal kernel / neighborhood relation

E(s,t):
  transition energy or edge-selection score

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

Here `energy` means edge-selection score. It is not moral value, utility, thermodynamic energy, or Omega.

## 3. Distance is not the same as transition energy

A distance or metric defines how states are near or far:

```text
d(s,t):
  how different states s and t are
```

A transition energy defines how favored a directed transformation is:

```text
E(s,t):
  how selected the move s -> t is under the substrate law
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
E(s,t) = d(s,t) + alpha * (A(t) - A(s)) + epsilon * roughness(s,t)
```

If `A(t) < A(s)`, moving from `s` to `t` can be selected differently than moving from `t` to `s`.

This induces asymmetry without requiring a named symbolic constraint like equality or modular sum.

## 4. Two minimal asymmetry ingredients

The formulation should separate two kinds of asymmetry.

### 4.1 Directional asymmetry

A scalar asymmetry field:

```text
A(s):
  directional asymmetry coordinate over states
```

adds a directional term:

```text
A(t) - A(s)
```

This makes one direction across the field different from the reverse direction.

### 4.2 Preservation asymmetry

A macro-invariant:

```text
I(s):
  coarse asymmetry structure / macro-invariant over states
```

adds a preservation term:

```text
|I(t) - I(s)|
```

This makes erasing or changing a coarse distinction less available than preserving it.

Directional asymmetry creates preferred flow.

Preservation asymmetry creates resistance to erasure of coarse structure.

Both are asymmetry. They play different roles.

## 5. Minimal transition-energy ladder

The substrate ladder should be stated without semantic labels.

### E0: locality only

```text
E_0(s,t) = d_H(s,t) + epsilon * roughness(s,t)
```

Expected role:

```text
baseline for bounded local branching;
may diffuse or saturate trivially;
useful as a lower comparator.
```

### E1: locality plus directional asymmetry

```text
E_1(s,t) = d_H(s,t) + alpha * (A(t) - A(s)) + epsilon * roughness(s,t)
```

Expected role:

```text
minimal directional lawlike flow;
no named symbolic constraint templates.
```

### E2: locality plus preservation asymmetry

```text
E_2(s,t) = d_H(s,t) + beta * |I(t) - I(s)| + epsilon * roughness(s,t)
```

`I(s)` may be mechanically generated from coarse state summaries such as:

```text
total coordinate mass;
symbol histogram;
nonzero-coordinate count;
other preregistered macro-invariant coordinates.
```

Expected role:

```text
minimal invariant-preserving lawlike structure;
tests whether coherent horizon transport requires persistence of coarse distinctions.
```

### E3: combined directional and preservation asymmetry

```text
E_3(s,t) = d_H(s,t) + alpha * (A(t) - A(s)) + beta * |I(t) - I(s)| + epsilon * roughness(s,t)
```

Expected role:

```text
minimal universe-like transition substrate:
locality + direction + preservation + roughness.
```

### E4: maximum-entropy local transition ensemble

Longer-term target.

Specify macro constraints only:

```text
state count;
locality radius;
out-degree distribution;
reversibility fraction;
roughness level;
directional-asymmetry marginal, if used;
macro-invariant marginal, if used.
```

Then sample transition graphs from the maximum-entropy ensemble satisfying those macros.

## 6. Why this is not a retreat from asymmetry

Asymmetry is not lost when hand-built constraints are removed.

Asymmetry can enter through:

```text
directional asymmetry fields;
macro-invariant preservation terms;
non-symmetric E(s,t);
directed edge selection from local neighborhoods;
bounded out-degree selection;
roughness-induced tie-breaking;
reversibility fraction less than 1.
```

The important distinction is:

```text
current substrate asymmetry:
  direction shaped partly by hand-built symbolic constraint templates

transition-energy substrate asymmetry:
  direction and preservation shaped by explicit locality, asymmetry fields, macro-invariants, roughness, and edge selection
```

The second is more appropriate for testing whether horizon transport is a general future-field phenomenon rather than an artifact of the constraint grammar.

## 7. What must be tested

The core empirical question is:

```text
Does matched-marginal-separated horizon transport with aligned amplification persist when named constraint vocabulary is removed?
```

Possible outcomes:

```text
E1 works:
  directional asymmetry may be sufficient

E2 works:
  preservation asymmetry / macro-invariants may be needed

E3 works better than either alone:
  direction and preservation may be complementary

E0 works:
  aligned amplification may be generic to bounded local branching and requires stronger nulls

none work:
  the current H128 object may depend on hand-built constraint grammar or current detector assumptions
```

## 8. Relationship to the H128 result

The H128 result remains important. It established the current live object:

```text
matched-marginal-separated horizon transport with horizon-dependent aligned amplification
```

But before promoting the instrument beyond the current substrate family, the project must ask:

```text
Is the object substrate-general, or constraint-template-specific?
```

This note says the next repair should be substrate untethering, not immediate promotion.

## 9. Claim boundary

Even if transition-energy substrates reproduce aligned amplification, the result would not show:

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

Transition energy makes substrate assumptions explicit: state space, locality, directional asymmetry, preservation asymmetry, roughness, and selection rule.

### Parsimonious

Start with the smallest generic families: locality only, locality plus directional asymmetry, locality plus preservation asymmetry, and their combination.

### Predictive

Each family predicts a different horizon-transport response profile. If the H128 object is not grammar-artifact, some version of it should persist beyond the original constraint-template substrate.

## 11. Bottom line

The current instrument is strong enough to surface a clean horizon-transport response object.

The substrate is not yet clean enough to promote that object broadly.

The next principled move is:

```text
replace hand-built constraint templates with explicit transition-energy families,
then test which minimal asymmetry ingredients produce which horizon-transport response profiles.
```
