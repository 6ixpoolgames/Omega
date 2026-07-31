# Generated Continuation Dynamics Protocol v0

Status: preregistration / post-freeze finite discovery protocol

Scope: exhaustive small action-labelled dynamics, compatibility derived from
shared-action continuation kernels, and generator-relative deformation
distributions

Claim boundary: not thermodynamics, an arrow-of-time theorem, physical degrees
of freedom, value, valuerhood, agency, standing, identity, moral license,
lushness, or Omega validation

## Purpose

This pass asks two questions using reproducible finite generators:

```text
1. Can a non-flag compatibility complex be derived from exact coupled
   continuation dynamics rather than supplied as declared faces?

2. How are expansion, contraction, equivalence, and mixed deformation verdicts
   distributed in several declared finite generator classes?
```

The first target is a constructive non-implication result. The second is a
generator-relative distribution audit with no required direction.

## Fixed Terminology

The pass separates:

```text
physical action/outcome structure:
  the exact generated transition system;

bounded capability order:
  alternating refinement of positive behavior signatures at horizon h;

deformation:
  comparison of source and target capability in that bounded order;

history fibre:
  not audited in this pass;

thermodynamic orientation:
  not supplied by graph direction alone and therefore not claimed.
```

Forward time does not imply expansion by definition.

## Part I - Generated Joint Compatibility

### Component dynamics

Use:

```text
components:
  A, B, C

shared action alphabet:
  a0, a1, a2, a3

component states:
  live, dead

safe set:
  {live}
```

Each component declares exactly two actions that preserve `live`. Every other
action sends `live` to `dead`; every action keeps `dead` at `dead`.

The exhaustive generator enumerates every ordered assignment:

```text
(Allowed_A, Allowed_B, Allowed_C)
```

where each allowed set is a two-element subset of the four-action alphabet.
The expected manifest size is:

```text
C(4,2)^3 = 216 assignments.
```

This count is a generator correctness condition, not a theory result.

### Shared-action product

For a nonempty component family `F`, construct the exact product:

```text
(x_i)_(i in F) -a-> (y_i)_(i in F)
iff
for one shared action a,
each component i takes its a-labelled transition.
```

The controller chooses one action before all component transitions. It may not
choose one action per component.

The product safe set is:

```text
Safe_F = { tuples whose every component is live }.
```

Compute the greatest fixed point:

```text
K_F = gfp X.
  { s in Safe_F |
    exists one shared action a,
    every a-successor of s lies in X }.
```

The generated compatibility predicate is:

```text
JointlyRealizable(F)
iff
the all-live initial tuple belongs to K_F.
```

No maximal face may be supplied to this computation.

### Derived compatibility complex

Evaluate `JointlyRealizable` on every nonempty family. Add the empty family by
convention. Derive maximal faces from the resulting downward-closed family.

The implementation must check downward closure rather than assume it:

```text
JointlyRealizable(F) and G subset F
implies JointlyRealizable(G).
```

### Generated hollow witness

Search the 216 assignments for:

```text
all singleton families jointly realizable;
all three pairs jointly realizable;
the triple not jointly realizable.
```

If found, retain the lexicographically first assignment under the declared
canonical ordering.

This is a generated non-flag witness because the complete one-skeleton does not
fill the triple.

### Matched filled control

Search the same manifest for a filled assignment matching the hollow witness
on:

```text
action alphabet size;
component count;
per-component allowed-action counts;
sorted pairwise common-action counts;
singleton kernel sizes;
sorted pair kernel sizes;
complete one-skeleton.
```

The filled control must have the triple in its kernel. Retain the
lexicographically first exact match.

### Independent-action negative control

Recompute the hollow assignment under the invalid quantifier:

```text
each component may choose its own action.
```

The triple should then be viable because every component has at least one safe
action. This is a negative control demonstrating why the same-action
quantifier is load-bearing.

### Joint compatibility cases

```text
GN1:
  exhaustive manifest and deterministic canonical ordering;

GN2:
  derived realizable families are downward closed for every assignment;

GN3:
  at least one generated non-flag witness exists;

GN4:
  a matched filled control exists;

GN5:
  independent component actions falsely fill the retained hollow triple;

GN6:
  component and action relabeling preserve the derived face structure;

GN7:
  a component with no live-preserving action fails singleton compatibility;

GN8:
  the existing CompatibilityStructure can consume derived maximal faces
  without altering them.
```

GN3 is a constructive strictness witness:

```text
pairwise continuation compatibility
does not imply
joint continuation compatibility.
```

It does not establish prevalence, value, or lushness.

## Part II - Generated Deformation Distribution

### Exact exhaustive systems

Use:

```text
states:
  s0, s1, s2

actions:
  a0, a1

transition rule:
  exactly one successor for every state/action pair

positive atom grammar:
  one optional atom p at each state
```

Enumerate all transition tables and all atom masks:

```text
3^(3*2) * 2^3 = 5,832 complete deterministic systems.
```

Every generated system is serial.

### Declared generator classes

Report these classes separately:

```text
complete:
  all 5,832 systems;

reversible:
  each action acts as a permutation of the three states;

absorbing:
  s2 is fixed by every action and every state can reach s2 in the underlying
  directed graph.
```

Class overlap is allowed and must be reported. No pooled result may be called a
substrate-independent distribution.

`absorbing` is a finite directed-dynamics class, not a thermodynamic model.
`reversible` is a structural null, not a complete physical model.

### Deformation relation

For each declared horizon:

```text
h in {0,1,2}
```

compute all state behavior signatures once per system. For every exact
source-target transition, compare source and target under structural
alternating refinement:

```text
EXPANSION;
CONTRACTION;
EQUIVALENT;
MIXED.
```

This is equivalent to comparing represented capability down-sets, but avoids a
cross-system representative basis.

### Primary and diagnostic weights

Primary distribution:

```text
unique structural edges (source,target), each counted once per system.
```

Also report:

```text
per-system mean verdict shares;
action-edge counts, with one row per state/action transition;
systems containing at least one instance of each verdict.
```

Action-edge counts are diagnostic only because duplicating an
effect-equivalent action can change those weights without changing behavior.

Do not introduce probabilities, trajectory frequencies, or occupancy weights.

### Sensitivity and null controls

```text
DD1:
  manifest counts and generator determinism;

DD2:
  complete/reversible/absorbing distributions at h = 0,1,2;

DD3:
  state/action/atom relabeling preserves structural-edge verdicts;

DD4:
  duplicating one action preserves structural-edge verdicts but may alter
  action-edge weights;

DD5:
  all four verdicts remain available to the classifier on retained controls;

DD6:
  horizon sensitivity is reported rather than silently pooled;

DD7:
  reversing a generated edge is not presumed to invert its verdict unless the
  reverse edge exists and is separately classified.
```

No expansion majority is required. A contraction majority, mixed result, or
near-uniform result is equally retainable.

## Evidence Classes

```text
generator correctness:
  manifest counts, deterministic ordering, relabeling, duplicate-action
  control, deadlock control, and output reconstruction;

constructive strictness:
  generated non-flagness under the shared-action product;

risky generated result:
  deformation distributions within each declared generator class and horizon.
```

The matched filled/hollow comparison is a finite counterexample to a proposed
implication. It is not an empirical frequency claim.

## Kill Conditions

Stop and report rather than repair if:

1. compatibility faces must be supplied manually;
2. the shared-action product accidentally permits component-specific actions;
3. derived realizable families are not downward closed;
4. no hollow witness or no matched filled control exists in the preregistered
   216-assignment manifest;
5. the primary deformation distribution changes under action duplication;
6. relabeling changes any retained structural verdict;
7. an ensemble is silently resampled after observing its distribution;
8. arbitrary graph direction is described as a thermodynamic arrow;
9. generator-relative frequencies are promoted as universal probabilities;
10. any prior retained verdict changes.

## Retained Outputs

The run must retain:

```text
summary.json;
case_results.csv;
generator_manifest.csv;
nonflag_search.csv;
nonflag_witness.json;
deformation_distribution.csv;
deformation_system_summary.csv;
sensitivity_results.csv;
report.md.
```

The generator manifest may use one row per declared class/count rather than one
row per system if the complete enumeration is reconstructible from the public
code and parameters.

## Public Compression

A shared-action continuation kernel can generate a hollow compatibility
triangle: every pair persists, while the triple has no common safe action.
Separately, finite deformation verdicts can be counted over declared exhaustive
system classes. Those distributions are properties of the generators and
horizons used; they are not yet a thermodynamic arrow.

## Explicitly Out of Scope

```text
thermodynamic entropy or entropy production;
micro/macro coarse-graining;
occupancy or path probabilities;
history-fibre monotonicity;
admissible projection selection;
operational identity;
property-family admission;
value or lushness derivation;
new public Omega claims.
```
