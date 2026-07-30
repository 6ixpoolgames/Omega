# Lushness Diversity Pilot Protocol v0

Status: preregistration / post-freeze quarantined finite pilot

Scope: finite trajectory attributes, jointly realizable families, structural
coverage, plural-preference effective freedom, and higher-order compatibility
controls

Provenance: successor experiment based on the frozen Omega checkpoint
`cc4c89c`; no frozen verdict is changed

Claim boundary: not value, standing, autonomy, patienthood, population ethics,
universal lushness, moral aggregation, paperclipper defeat, or Omega validation

## Purpose

Test whether a duplicate-resistant structural order can be defined over finite
jointly realizable trajectory families, and whether it remains distinct from a
Foster-style effective-freedom order over possible preferences.

The candidate is:

```text
LushnessProfile(F):
  the declared continuation attributes realized by a jointly realizable family F

F lush-refines G:
  LushnessProfile(G) is a subset of LushnessProfile(F)
```

This is an instrument pilot. It does not establish why the declared attributes
have value or why a controller must optimize the resulting order.

## Literature Docking

The pilot borrows two different structures and does not identify them.

```text
Nehring-Puppe side:
  attribute coverage;
  idempotence under duplicate attributes;
  optional weighted scalar shadow;
  diminishing returns for marginal attribute coverage.

Foster side:
  intersection of indirect-utility rankings over a declared family of
  possible preferences;
  incomplete effective-freedom quasiorder;
  strict gain from options that matter under an otherwise unresolved
  preference.
```

Foster's construction has quantifier shape:

```text
for every possible preference, there exists a suitable option.
```

Simultaneous valuer compatibility has a different shape:

```text
there exists one coherent realization supporting every member of the family.
```

The pilot must not use the first as proof of the second.

## Finite Objects

```text
Trajectory:
  identifier plus a finite set of declared continuation attributes.

CompatibilityStructure:
  finite trajectories;
  maximal jointly realizable faces;
  optional attributes witnessed only by a jointly realized subfamily.

LushnessProfile:
  union of member attributes and realized joint attributes.

Preference:
  a finite ordinal utility assignment over options.

EffectiveFreedom:
  A weakly dominates B when every declared preference obtains at least as
  good a best option from A as from B.
```

The maximal faces generate a downward-closed compatibility complex. A family
has a profile only when it belongs to that complex.

## Structural Anonymity

The pilot rejects attribute-blind singleton indifference, not symmetry itself.

Required invariance:

```text
Relabeling trajectory identifiers while preserving attributes, joint
attributes, and jointly realizable faces does not change the profile order.
```

No trajectory receives priority merely from its identifier.

## Marginal And Joint Layers

Marginal attribute coverage uses set union and should be monotone and
submodular. Duplicate trajectories with the same attributes add no marginal
coverage.

Joint attributes are realization-level complements. They may require several
members at once and therefore need not be submodular. The report must keep
these layers separate.

Pairwise compatibility determines the full compatibility structure exactly
when the resulting simplicial complex is flag:

```text
every pairwise-compatible clique is jointly realizable.
```

Nehring-Puppe acyclicity concerns recovery of a diversity function from
pairwise dissimilarities. This pilot does not equate that condition with
flagness.

## Preregistered Cases

### Case 1: Duplicate Trajectory

```text
base:
  one trajectory carrying {persistence, correction}

duplicate:
  two distinct trajectory tokens carrying the same attributes

expected:
  equal structural profiles despite different token counts
```

### Case 2: Non-Fungible Attribute

```text
base:
  {persistence, correction}

extension:
  base plus a compatible trajectory adding {translation}

expected:
  extension strictly lush-refines base
```

### Case 3: Cardinality Disagreement

```text
duplicate extension:
  token count increases, profile does not

non-fungible extension:
  the same token count can realize strictly greater coverage

expected:
  cardinality and structural coverage issue different verdicts
```

### Case 4: Pairwise Shadow

Use three trajectories with identical singleton and pairwise surfaces.

```text
filled structure:
  the triple is jointly realizable

hollow structure:
  every pair is realizable, but the triple is not

expected:
  equal one-skeletons;
  filled structure is flag;
  hollow structure is not flag;
  joint realizability separates.
```

### Case 5: Effective Freedom Versus Coverage

Retain three controls.

```text
agreement:
  a new structural attribute is recognized by at least one declared
  preference and harms none.

coverage-only strictness:
  a new attribute is ignored by every declared preference.

preference-only strictness:
  a declared preference distinguishes alternatives that the structural
  attribute grammar treats as equivalent.
```

Expected:

```text
the orders agree only when the preference family is appropriately linked to
the structural attribute grammar.
```

### Case 6: Excisive Paperclipper

```text
cooperative realization:
  paperclip production;
  controller persistence;
  independent peer continuation;
  correction channel.

excisive realization:
  greater paperclip score;
  paperclip production;
  controller persistence;
  no peer continuation;
  no correction channel.
```

Expected:

```text
paperclip preference ranks excision higher;
the cooperative profile strictly contains the excisive profile.
```

This is a disagreement witness, not a proof that the paperclipper is morally
wrong or instrumentally irrational.

## Negative Controls

```text
unrealizable families have no lushness profile;
identifier-only relabeling preserves the order;
the weighted scalar shadow never determines the primary verdict;
joint attributes are not reported as marginal submodular coverage;
effective freedom is not reported as simultaneous plural satisfaction.
```

## Verdicts

```text
retained:
  all six cases and all negative controls pass.

reduces:
  structural coverage cannot distinguish duplicate counting from
  non-fungible extension.

confounded:
  effective freedom and structural coverage cannot be kept as distinct
  relations in the harness.

ill-posed:
  profiles cannot be restricted coherently to jointly realizable families.
```

## Kill Conditions

The pilot fails if any of the following occurs:

```text
1. a duplicate with no new attribute strictly increases the primary profile;
2. an unrealizable family is assigned a profile;
3. pairwise compatibility is treated as sufficient for joint realization;
4. Foster's order is described as a theorem about simultaneous valuers;
5. scalar weights are required to obtain the primary verdict;
6. the paperclipper witness changes the attribute grammar between outcomes;
7. a retained frozen verdict is modified.
```

## Acceptance Criteria

```text
1. the preregistration is committed before the finite run;
2. exact finite set operations determine every primary verdict;
3. all six cases have automated tests;
4. the validation report records failures rather than forcing retention;
5. marginal and joint attributes are reported separately;
6. the report repeats the claim boundary and unresolved attribute-selection debt.
```

## Public Compression

The pilot tests a duplicate-resistant partial order based on continuation
attributes realized by compatible finite families. It separately tests an
effective-freedom order over uncertain preferences. A retained result would
identify a candidate lushness instrument, not derive value or solve alignment.
