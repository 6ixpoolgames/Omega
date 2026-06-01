# Omega Formal Core v0.2: Future-Distinction Dynamics

Status: working formalism / theory-arm draft  
Date: 2026-06-01  
Claim boundary: formal orientation note, not empirical validation and not theorem closure

## 0. Purpose

This document redrafts the Omega formal core around a cleaner ontology:

```text
relation:
  the substrate condition

distinction:
  the future-bearing content

asymmetry:
  the channeling law

dynamics:
  the iterated unfolding of future-distinctions through relations under asymmetry

Omega:
  the admissible subset of dynamics whose future-relevant distinctions persist
  to terminus in a recoverable, non-erasing, and compatible manner
```

The purpose of this version is not to close the theory. The purpose is to make
the live formal object explicit enough that the Future Field Atlas can test
finite approximants without overclaiming.

This draft incorporates the useful part of the recent persistent-future-
distinction proposal: future-distinction capacity must be considered before
asymmetry is allowed to channel it. It rejects two brittle overclosures:

```text
1. persistent distinction does not mean separability under every possible
   quotient forever;

2. non-erasure is not automatically forced by distinction capacity.
```

Non-erasure is not assumed. It is the target property.

## 1. Motivating sentence

A compact working definition:

```text
Omega is the admissible subset of future-field dynamics for which
future-relevant distinctions persist to terminus in a recoverable, non-erasing,
and compatible manner.
```

Expanded:

```text
Given a relational substrate, Omega is the class of admissible dynamics generated
by relation, distinction, and asymmetry such that future-relevant distinctions
propagate recoverably, non-erasingly, and compatibly to the relevant terminal
regime.
```

This makes Omega a property-bearing class of dynamics, not merely a set of end
states, a utility function, a reward, an entropy score, a survival condition, or
an agent boundary.

## 2. Base object: relational substrate

A relational substrate is a finite directed transition structure:

```text
S = finite state set
R subset S x S = directed admissible transition relation
```

Write:

```text
s -> t
```

when `(s,t) in R`.

Relation is the quiet fundamental assumption. If there is no relation, there is
no transition, no frontier, no propagation, and no future field. Relation does
not by itself decide what matters. It supplies the condition under which futures
can exist.

In this redraft:

```text
relation is not the primary live variable;
relation is the substrate condition.
```

## 3. Frontiers and future fields

For start state `s` and horizon `H`, define the raw reachable frontier:

```text
F_H(s) = { x in S : there exists a path s -> ... -> x of length H }
```

For stochastic or weighted systems, `F_H(s)` may be a measure over states rather
than a set. This draft begins with the finite set case and treats measure-valued
frontiers as a later generalization.

The future field from `s` is the horizon-indexed family:

```text
F_*(s) = (F_0(s), F_1(s), F_2(s), ...)
```

A coupled future field is the corresponding joint frontier process induced by a
coupled relation or coupled operator over two or more fields.

## 4. Admissible observables and quotients

An observable or quotient is a map:

```text
q : S -> Q
```

where `Q` may be finite, metric, ordered, vector-valued, or structured.

The pushforward of a frontier under `q` is:

```text
q(F_H(s))
```

for support-valued frontiers, or `q_# mu_H` for measure-valued frontiers.

Admissibility matters. Not every quotient is meaningful. A constant quotient can
destroy every distinction. A hand-picked quotient can smuggle in the conclusion.

An admissible observable family `Q_adm` should be:

```text
predeclared;
nontrivial;
computable from the substrate without using the desired conclusion;
transport-relevant;
not merely a frontier-size proxy;
auditable under controls.
```

This version intentionally uses an admissible family rather than quantifying over
all possible quotients.

## 5. Future-distinction

A state difference is not automatically a future-distinction.

A future-distinction is a difference whose consequences remain separable across
reachable frontiers under at least one admissible observable over a specified
horizon regime.

Working finite definition:

```text
Given an admissible observable family Q_adm and horizon regime W, starts s1 and
s2 exhibit a future-distinction when there exists q in Q_adm such that the
frontier observations q(F_H(s1)) and q(F_H(s2)) remain separated under a declared
separation criterion for H in W.
```

For support-valued frontiers, separation may be:

```text
q(F_H(s1)) != q(F_H(s2));
nonzero symmetric difference;
nonzero metric distance;
nonzero persistence score;
```

For measure-valued frontiers, separation may be:

```text
total variation distance;
Wasserstein or entropic transport distance;
quotient distribution divergence;
other declared metric over q_# frontier measures.
```

The key correction:

```text
Persistent future-distinction is not “different under every quotient forever.”
It is “separable by an admissible, nontrivial, predeclared observable family
over a relevant horizon regime.”
```

## 6. Future-distinction capacity

A relational substrate has future-distinction capacity relative to
`Q_adm` and horizon regime `W` if at least one pair of starts exhibits a
persistent or recurrent future-distinction under `Q_adm` across `W`.

```text
DistCap(S, R; Q_adm, W) = true
```

when such a pair exists.

Future-distinction capacity is a necessary precondition for Omega-relevance. It
is not sufficient.

Contractive substrates, absorbing chains, or pure-death processes may fail at
this layer if they do not support any admissible persistent future-distinction.

This prevents a fancy asymmetry field from manufacturing Omega-relevance in a
substrate with no future-bearing distinction capacity.

## 7. Asymmetry as channeling

Asymmetry is lawful non-neutrality in the relational substrate. It channels which
future-distinctions propagate, collapse, recover, or compose.

In the current atlas lineage, asymmetry often appears through a transition
energy:

```text
E(s,t) = d(s,t) + beta * |I(t) - I(s)| + roughness(s,t)
```

where:

```text
d(s,t): local transition distance or move cost
I: admissible invariant / observable coordinate
beta: strength of preservation pressure
roughness: deterministic tie-breaking or small substrate noise
```

But this is only one implementation form. The formal role is broader:

```text
an asymmetry is a lawful bias that orders or weights admissible continuations
relative to future-distinction propagation.
```

Asymmetry does not create the first distinction. It channels already available
future-distinction capacity.

This is the key ordering:

```text
future-distinction capacity before asymmetry;
asymmetry before observed deformation;
deformation before identity-like designation.
```

## 8. Dynamics as derived process

Dynamics is not a fourth primitive. It is the realized unfolding of relation,
distinction, and asymmetry over horizon.

```text
dynamics = iterated propagation of future-distinctions through relations under
lawful asymmetry
```

More explicitly:

```text
Given a relational substrate (S,R), admissible observables Q_adm, and an
asymmetry/channeling law A, a dynamics D is the horizon-indexed evolution of
future-distinctions induced by repeated application of the resulting transition
process.
```

The atlas measures dynamics. The formalism explains dynamics through relation,
distinction, and asymmetry.

## 9. Terminus

A terminus is the relevant terminal regime of a dynamics.

In a finite system this may be:

```text
absorbing state;
absorbing class;
closed recurrent class;
cycle;
stabilized frontier quotient;
limit distribution;
declared finite horizon;
terminal frontier under a chosen experimental regime.
```

The formalism should not assume all systems have the same kind of terminal
object. Instead, each analysis must declare its terminal regime:

```text
Term(D) = declared terminal regime of dynamics D
```

## 10. Persistence to terminus

A future-distinction persists to terminus when it remains recoverably represented
through the dynamics until the declared terminal regime.

This does not require identical state constituents. Constituents may turn over.
The pattern may persist while the microstates churn.

This is the vortex analogy:

```text
what persists is not the same matter;
what persists is a recoverable dynamic pattern.
```

Persistence to terminus rules out brief flashes of structure that disappear
before the dynamics reaches its relevant terminal regime.

## 11. Recoverability as operational identity

This draft treats recoverability as the operational form of identity.

Identity is not primitive. Recoverability is evidential.

```text
Identity asks: what is the same thing?
Recoverability asks: what distinction-pattern can be reconstructed, reidentified,
or transported through deformation under an admissible map?
```

Because the project rejects privileged self, agent, object, and valuer
boundaries, recoverability is the only form of identity admissible at this layer.

A recoverable distinction is one for which there exists an admissible
reconstruction, transport, section, inverse-like map, or quotient-level
identification preserving the relevant distinction across deformation.

Informally:

```text
recoverability is identity without ontological privilege.
```

This is compatible with the no-self / boundary-nonprivileging posture. A boundary
or identity is not assumed. It is earned when a recoverable pattern explains the
future-field deformation better than alternatives.

## 12. Non-erasure

Non-erasure is the central target property. It is not automatic.

A dynamics is non-erasing relative to `Q_adm`, `W`, and `Term(D)` when
future-relevant distinctions that should remain recoverable are not destroyed,
collapsed into misleading aggregates, or locally preserved at the cost of broader
future-bearing structure.

Non-erasure is stronger than:

```text
survival;
static persistence;
entropy maximization;
frontier size;
local viability;
endpoint reachability.
```

A dynamics can survive while erasing future-relevant distinctions. A dynamics can
expand reachability while destroying recoverable structure. A dynamics can
preserve a local invariant while capturing or collapsing other compatible future
fields.

Non-erasure is therefore a substantive property to prove, measure, or falsify.

## 13. Compatibility

Compatibility concerns composition of future-bearing dynamics.

A dynamics may be proto-Omega-like in isolation but fail compatibility when
composed with another dynamics. Compatibility asks whether multiple
future-bearing structures can coexist, interact, or compose without trivial
capture, erasure, or collapse of recoverable future-distinctions.

Compatibility is not simple product equivalence.

Possible coupled outcomes include:

```text
product-equivalent coexistence;
constructive support;
recoverable deformation;
asymmetric marginal loss;
capture;
erasure;
destructive interference;
collapse.
```

The atlas may measure product-breaking residuals, marginal retention, and
composition residuals, but these do not by themselves establish compatibility.
They become compatibility evidence only after recurrence, controls, and
formal criteria.

## 14. Proto-Omega and Omega

The primitives do not guarantee proto-Omega.

A universe can have relation, distinction, and asymmetry while still collapsing,
erasing, or capturing all future-relevant distinctions.

The robust strong statement is weaker and cleaner:

```text
Any universe with relation, distinction, and asymmetry is Omega-assessable.
```

Proto-Omega is the single-field version of the target property:

```text
A dynamics is proto-Omega when future-relevant distinctions persist to terminus
recoverably and non-erasingly within a declared future field.
```

Omega adds compatibility:

```text
A dynamics is Omega-relevant when future-relevant distinctions persist to
terminus recoverably, non-erasingly, and compatibly under admissible designation
and composition.
```

Thus:

```text
Proto-Omega:
  recoverable non-erasing persistence within a future field

Omega:
  compatible recoverable non-erasing persistence across admissible future-bearing
  dynamics or designations
```

## 15. The central strong claim

The project should not claim:

```text
every universe with the primitives produces Omega.
```

That is too strong.

The stronger defensible claim is:

```text
Wherever value-bearing structure exists, its substrate-general form must involve
recoverable, non-erasing, compatible propagation of future-relevant distinctions.
```

This is a central conjectural bridge, not an empirical result.

It mirrors the relation to other frameworks:

```text
FEP does not say every system is an organism;
viability theory does not say every state remains viable;
constructor theory does not say every transformation is possible;
Omega should not say every universe produces value.
```

Omega should say:

```text
if value-bearing futures exist, their boundary-nonprivileged structural form is
recoverable, non-erasing, compatible future-distinction dynamics.
```

## 16. Phase ladder

The ladder below is conservative. It is designed to prevent overnaming.

### Phase 0: Future-distinction capacity

Question:

```text
Does the raw relational substrate support future-distinctions under admissible
observables before asymmetry is interpreted as channeling?
```

Evidence:

```text
raw frontier distinguishability;
quotient frontier separation;
distinction persistence over declared horizon regime;
non-contracting future-field support under admissible observables.
```

Claim allowed:

```text
The substrate has future-distinction capacity relative to Q_adm and W.
```

Claim not allowed:

```text
The substrate is Omega-relevant.
```

### Phase 1: Lawful channeling

Question:

```text
Does an invariant/asymmetry law channel future-distinctions in a reproducible,
auditable way?
```

Evidence:

```text
transition-energy anatomy;
selection-operator geometry;
rank-boundary geometry;
frontier deformation under matched controls;
channeling that does not reduce to frontier size or cap artifacts.
```

Claim allowed:

```text
Asymmetry channels future-distinction propagation in the specified substrate.
```

### Phase 2: Structured deformation

Question:

```text
Does a perturbation or coupled operator produce product-breaking or baseline-
separated future-field deformation?
```

Evidence:

```text
joint-vs-product residuals;
composition residuals;
marginal retention differences;
complete artifact status;
passing reconstruction audits.
```

Claim allowed:

```text
A formal operator produces structured future-field deformation.
```

Claim not allowed:

```text
The deformation is support, capture, erasure, compatibility, or agency.
```

### Phase 3: Persistent deformation

Question:

```text
Does deformation persist across horizons, starts, seeds, operators, or nearby
substrates?
```

Evidence:

```text
horizon persistence;
start recurrence;
seed recurrence;
operator-setting recurrence;
selected depth checks after breadth sweeps;
persistence feature maps.
```

Claim allowed:

```text
The deformation is not merely a one-horizon or one-start artifact.
```

### Phase 4: Recoverable deformation

Question:

```text
Can the relevant distinction-pattern be reconstructed or reidentified through
the deformation?
```

Evidence:

```text
recoverable quotient/fiber structure;
low composition residual on selected components;
high marginal retention on persistent classes;
existence of an admissible reconstruction or inverse-like map.
```

Claim allowed:

```text
The deformation preserves operational identity of the relevant distinction-
pattern under the declared admissible map.
```

### Phase 5: Non-erasure

Question:

```text
Does the dynamics preserve future-relevant distinctions rather than merely
surviving, expanding, or locally stabilizing while erasing them?
```

Evidence:

```text
stable or non-decreasing future-distinction measure under nulls;
no hidden collapse under quotient/fiber audits;
no capture by frontier-size artifacts;
non-erasure across perturbation and horizon.
```

Claim allowed:

```text
The dynamics is non-erasing relative to the declared future-relevant distinction
measure and admissible observable family.
```

### Phase 6: Proto-designation

Question:

```text
Can a boundary, process bundle, quotient, or fiber be inferred because it
predicts future-field deformation and recoverability better than alternatives?
```

Claim allowed:

```text
admissible designation;
proto-designation;
process-bundle footprint;
recoverable pattern identity.
```

Claim not allowed:

```text
self;
agent;
valuer;
identity as primitive.
```

### Phase 7: Compatibility, capture, and erasure

Question:

```text
When multiple future-bearing dynamics compose, are their recoverable future-
distinctions preserved, supported, captured, erased, or collapsed?
```

Evidence:

```text
joint-vs-product residuals;
recurring marginal retention asymmetries;
quotient/fiber survival;
non-erasure diagnostics;
recoverability under coupling;
controls showing effects are not cap or frontier-size artifacts.
```

Claim allowed only after formal criteria:

```text
candidate compatibility;
candidate capture;
candidate erasure;
candidate support.
```

### Phase 8: Omega-relevant candidacy

Question:

```text
Does an admissibly designated process-bundle support recoverable, non-erasing,
compatible propagation of future-relevant distinctions to terminus?
```

This phase is not currently achieved.

## 17. Atlas interface

The Future Field Atlas is not the definition of Omega. It is the current finite
instrument for probing approximants.

Mapping:

```text
raw frontier distinguishability:
  Phase 0 future-distinction capacity

rank-boundary geometry:
  Phase 1 lawful channeling, not value

joint_support_residual_fraction:
  Phase 2 product-breaking deformation, not interaction by itself

marginal_retention_fraction:
  marginal set preservation, not causal support by itself

composition_residual:
  transport-flow noncomposition or recovery candidate, not agency

artifact_status = truncated_noninterpretable:
  blocks topology-dependent scientific interpretation

reconstruction_audit != clean pass:
  blocks strong topology claims
```

A future atlas extension should add a Phase 0 raw distinction-capacity audit:

```text
raw_frontier_distinction_capacity_by_horizon.csv
quotient_frontier_separation_by_horizon.csv
distinction_persistence_summary.csv
contracting_or_absorbing_substrate_flag.csv
```

This should precede rank-boundary or coupled interpretation.

## 18. Falsification criteria

The theory gains credibility only if it can fail.

Potential falsifiers or weakeners:

```text
1. Raw future-distinction capacity is absent in the tested substrate class.
   Result: substrate ineligible for Omega claims.

2. Channeling vanishes across admissible observables or is explained entirely by
   frontier size, saturation, or cap artifacts.
   Result: invariant/asymmetry engine too weak or too hand-tuned.

3. Rank-boundary effects vanish under operator variation.
   Result: current rank-boundary finding is calibration-local.

4. Coupled residuals are fully explained by product frontier size, heavy-pair
   skew, cap poisoning, or reconstruction artifacts.
   Result: no coupled deformation claim.

5. Deformation persists but is never recoverable under any admissible quotient,
   fiber, or reconstruction map.
   Result: no proto-designation or identity-like claim.

6. Non-erasure fails in otherwise distinction-capable dynamics under admissible
   asymmetry.
   Result: current admissibility criteria are insufficient.

7. Compatibility fails systematically: local proto-Omega dynamics only persist
   by erasing or capturing other future-bearing dynamics.
   Result: Omega-relevance blocked.
```

## 19. Terminal object sketch

The grand ambition can be sketched, but not claimed.

One possible categorical orientation:

```text
Objects:
  future-field dynamics equipped with relational substrate, admissible
  observables, future-distinction capacity, recoverability structure,
  non-erasure constraints, and compatibility conditions.

Morphisms:
  simulations or maps preserving future-relevant distinctions, recoverability,
  non-erasure, and compatibility structure.

Omega-like object:
  a maximal or terminal compatibility structure of admissible dynamics into
  which Omega-relevant future-bearing processes map insofar as they preserve
  recoverable, non-erasing future-distinctions.
```

This may turn out to be a terminal object, a reflective subcategory, a closure
operator, or a maximal fixed point. The correct mathematical packaging is not
yet known.

The purpose of the sketch is to preserve the ambition:

```text
Omega is not a privileged agent, utility, value scalar, or boundary.
Omega is the compatibility structure of recoverable non-erasing future-
distinction dynamics.
```

## 20. Relation to established frameworks

### Free Energy Principle

FEP often begins with systems separated by Markov blankets. Omega should treat
blanket-like boundaries as recoverable dynamic patterns, not primitives.

A Markov blanket becomes admissible only when it functions as a recoverable
pattern boundary through future-field dynamics.

### Viability theory

Viability theory studies remaining within constraints. Omega generalizes the
question from survival inside a set to preservation of future-relevant
distinctions.

A locally viable process that erases compatible future-bearing structure fails
Omega even if it remains viable.

### Constructor theory

Constructor theory studies possible and impossible transformations. Omega can be
read as a constraint theory over transformations that preserve or erase
future-bearing distinctions.

### Assembly theory

Assembly theory tracks construction histories of objects. Omega tracks the
future-field preservation, recoverability, and compatibility of distinctions.

The direction differs:

```text
assembly:
  how did this object become constructible?

Omega:
  what future-bearing distinctions can continue recoverably and compatibly?
```

## 21. Current open conjectures

Conjecture A:

```text
In sufficiently rich relational substrates with future-distinction capacity,
some admissible asymmetry laws generate proto-Omega dynamics.
```

Conjecture B:

```text
Recoverability is the substrate-neutral operational form of identity.
```

Conjecture C:

```text
All value-bearing structures require recoverable, non-erasing, compatible
future-distinction dynamics.
```

Conjecture D:

```text
The Future Field Atlas can detect early approximants of proto-Omega as persistent,
recoverable, non-erasing deformation patterns before agent, valuer, or identity
language is admissible.
```

None of these are established by current empirical results.

## 22. Summary

The formal stack is now:

```text
relation:
  makes futures possible

distinction:
  makes futures informative

asymmetry:
  channels futures

dynamics:
  unfolds the channeling

recoverability:
  operational identity of distinction-patterns

non-erasure:
  prevents fake success by collapse, survival, entropy, or local persistence

compatibility:
  prevents local proto-Omega from destroying other future-bearing structure

proto-Omega:
  single-field recoverable non-erasing persistence to terminus

Omega:
  compatible recoverable non-erasing persistence of future-relevant distinctions
  under admissible designation and composition
```

The strongest clean current statement:

```text
Wherever value-bearing structure exists, its substrate-general form must involve
recoverable, non-erasing, compatible propagation of future-relevant distinctions.
```

The empirical arm builds and stresses the microscope.

The formal arm defines what would count as seeing.
