# Omega v2 Process Interface Identifiability Protocol v0

Status: preregistered finite identifiability and feature-independence protocol

Date: 2026-08-03

Depends on:

```text
docs/research_notes/omega_v2/alpha_omega_foundation_report_v0.md
docs/research_notes/omega_v2/directional_asymmetry_capability_report_v0.md
docs/research_notes/omega_v2/robust_omega_report_v0.md
```

## Question

The clean May/Robust realization core accepts candidate patterns, policies,
and environment cases as inputs. Its algebra does not determine where a
candidate process boundary comes from.

This sprint asks:

> Given an exact finite factorized dynamics and a declared intervention
> semantics, which component sets remain admissible as process interfaces, and
> when is one interface identified rather than merely one of several
> observationally compatible boundaries?

The result may be:

```text
IDENTIFIED:
  exactly one inclusion-minimal interface satisfies the declared feature
  query under complete intervention evidence;

SET_IDENTIFIED:
  several incomparable inclusion-minimal interfaces satisfy it;

UNRESOLVED:
  the available evidence cannot certify or reject all required features;

NO_CANDIDATE:
  every candidate is rejected by at least one observed required feature.
```

`FEATURE_DEPENDENT` is a cross-query audit label, not a fifth identification
status. It applies when changing the declared feature query changes the
retained minimal-interface family.

## Claim Boundary

This is not a valuer definition.

It is not:

```text
agency;
consciousness;
identity;
patienthood;
standing;
value;
moral license;
responsibility;
universal process individuation;
or Omega validation.
```

The output is a finite operational interface family relative to:

```text
a component factorization;
a transition map;
an initial support;
an evidence mode;
a finite horizon;
and a declared feature query.
```

No interface may be silently promoted to a valuer or preferred realization.

## Modeling Inputs and Derived Quantities

### Modeling inputs

The v0 adapter receives:

```text
Component:
  a finite ordered set of component identifiers;

State:
  one Boolean value for every component;

T:
  a total deterministic synchronous update map State -> State;

Initial:
  a nonempty set of states;

H:
  a positive finite audit horizon;

Atoms:
  optional presentation annotations that the structural analyzer must ignore.
```

The state space must be the complete Boolean product. This makes every
single-coordinate source intervention well-typed without inventing missing
states.

The Boolean-network adapter is a finite laboratory, not a claim that physical
or agentic processes are fundamentally Boolean or synchronously updated.

### Intervention semantics

For a source state `s`, component `i`, and alternate Boolean value `b`, define:

```text
do_source(s, i := b):
  replace coordinate i in s by b, then apply T.
```

The intervention family is exhaustive over all states, components, and
alternate Boolean values.

This is the v0 causal semantics. It is declared adapter structure, not a
universal derivation of intervention meaning.

### Derived quantities

The implementation must derive:

```text
reachable states through H;
reachable recurrent states;
the exact coordinate influence graph;
one profile for every nonempty proper component subset;
and the evidence fiber of every declared interface query.
```

Component names and optional atoms must not enter any structural predicate.

## Exact Interface Features

Let `I` be a nonempty proper set of components and `O` its complement.

### Coordinate influence

`Influences(i,j)` holds iff there are two states that differ only at coordinate
`i` whose next states differ at coordinate `j`.

Define:

```text
internal_influence(I):
  some i in I influences some j in I;

incoming_influence(I):
  some i in O influences some j in I;

outgoing_influence(I):
  some i in I influences some j in O.
```

Every retained influence edge must carry the source-state pair and differing
target values that witness it.

### Persistent variation

`persistent_variation(I)` holds iff the reachable recurrent states contain at
least two distinct projections onto `I`.

This detects retained nontrivial interface state. It does not assert identity,
selfhood, or value.

### Latent-state multiplicity

`latent_state_multiplicity(I)` holds iff, after at least one update and within
the declared horizon, two reachable states have:

```text
the same O projection;
different I projections.
```

This is a finite hidden-state condition. It does not by itself establish that
the hidden distinction was learned, useful, or causally active.

### Record acquisition

For v0:

```text
record_acquisition(I) :=
  incoming_influence(I)
  and latent_state_multiplicity(I).
```

This is explicitly a derived composite. The independence census must not
advertise it as a primitive feature.

### Record-sensitive outflow

`record_sensitive_outflow(I)` holds iff two reachable states have the same
outside projection and different inside projections, and their next outside
projections differ.

This is the boundary-free analogue of the earlier controller test:

```text
same present outside;
different retained inside;
different next outside.
```

It is still relative to the supplied component factorization.

### Bounded continuation influence

`continuation_influence_H(I)` holds iff changing one component in `I` at a
reachable source changes the resulting outside-state trace within `H` steps.

Every positive verdict must retain:

```text
the source state;
the intervened source;
the changed coordinate;
the baseline outside trace;
and the intervened outside trace.
```

## Evidence Modes

### Observational

Observational evidence may report:

```text
persistent_variation;
latent_state_multiplicity.
```

The causal features remain `UNKNOWN`:

```text
internal_influence;
incoming_influence;
outgoing_influence;
record_acquisition;
record_sensitive_outflow;
continuation_influence.
```

Correlations, copied records, or common-driver structure must not be converted
into causal edges.

### Interventional

Complete intervention evidence evaluates every feature exactly using the full
transition table and exhaustive single-coordinate interventions.

Interventional equivalence must imply observational equivalence. The converse
must be challenged by an explicit finite counterexample.

## Query and Set Identification

An `InterfaceQuery` contains an explicit list of features required to be true.

For each candidate interface:

```text
rejected:
  at least one required feature is FALSE;

certified:
  every required feature is TRUE;

consistent but unresolved:
  no required feature is FALSE and at least one is UNKNOWN.
```

The analyzer retains all certified or unresolved candidates. It then reports
all inclusion-minimal members of that family. It never chooses one candidate
from several incomparable minima.

The primary query is fixed before the run:

```text
persistent_variation;
record_acquisition;
record_sensitive_outflow;
continuation_influence.
```

Secondary queries may be run only to measure feature dependence. They must be
reported as separate declared queries.

## Exact Two-Component Census

Enumerate every deterministic synchronous Boolean update over:

```text
components:
  inside, outside;

state count:
  4;

possible update maps:
  4^4 = 256;

initial support:
  {(0,0), (1,0)};

horizon:
  4;

candidate interface:
  {inside}.
```

For the base features:

```text
persistent_variation;
internal_influence;
incoming_influence;
outgoing_influence;
latent_state_multiplicity;
record_sensitive_outflow;
continuation_influence;
```

report:

```text
true count;
false count;
joint signature count;
and an exact isolating pair when two systems agree on every other listed
feature and differ on the target feature.
```

Verdict per feature:

```text
ISOLATED:
  an exact isolating pair exists;

NOT_ISOLATED_IN_CENSUS:
  no pair exists in the exhaustive declared class.
```

Absence of an isolating pair in this census is not a universal reduction
theorem.

`record_acquisition` is reported separately as a declared conjunction and is
not eligible for an independence verdict.

## Required Controls

### Annotation invariance

Adding an `agent` atom to the same state/dynamics object must not change:

```text
influence edges;
interface profiles;
query fibers;
or identification status.
```

### Component-renaming covariance

A bijective component renaming must transport profiles and candidate families
without changing their structural content.

### Common-driver shadow

Use three components where one driver controls two correlated descendants.

Required:

```text
the descendants are observationally correlated;
the influence graph contains driver-to-descendant edges;
and no descendant-to-descendant edge is fabricated.
```

### Copied-record shadow

Use a source, a copied record, and an output all driven by the source.

Required:

```text
the copy tracks the source;
intervening on the copy does not change the output;
and the copy is not certified by the primary query.
```

### Observational non-identifiability

Retain two models with:

```text
the same component set;
the same initial support;
the same reachable observational transition rows;
different responses to one declared intervention.
```

Required:

```text
observational signatures equal;
interventional signatures unequal;
observational query unresolved;
and intervention evidence separates the relevant interface profile.
```

### Identified and set-identified positives

Retain:

```text
one fixture with exactly one inclusion-minimal primary-query interface;
one symmetry fixture with several incomparable inclusion-minimal interfaces.
```

The second fixture must return `SET_IDENTIFIED`, not select a representative.

## Memory-Update Injectivity Control

The prior directional-capability report left open whether generated
closed-loop asymmetry was controller organization or non-injective
record-writing.

Add a narrow control over the same finite world/memory surface:

```text
copy update:
  memory' = observation;

reversible update:
  memory' = memory XOR observation.
```

The world coordinate remains fixed in this control.

Audit:

```text
conditional update injectivity for each observation;
closed-loop map image size;
closed-loop map injectivity;
and update-collision witnesses.
```

Required:

```text
the copy update is conditionally non-injective and its closed-loop map
contracts;

the XOR update is conditionally injective and its closed-loop map is
bijective.
```

This control may show that record erasure is sufficient for functional
noninvertibility in the fixture. It does not settle the prior stochastic
record-selector result or derive thermodynamic cost.

## Formal Spine

Add:

```text
formal/lean/OmegaV2/Finite/Identifiability.lean
```

Define:

```text
EvidenceFiber;
EvidenceRefines;
ObservationallyEquivalent;
InterventionallyEquivalent.
```

Retain without placeholders:

```text
refined_fiber_subset;
identified_under_coarse_implies_identified_under_refinement;
interventional_equivalence_implies_observational_equivalence;
observational_equivalence_does_not_imply_interventional_equivalence.
```

The final theorem is an explicit finite counterexample, not an axiom.

Do not formalize the complete Boolean-network census in Lean during v0.

## Deliverables

Add:

```text
omega_v2/finite/process_interfaces.py
omega_v2/experiments/process_interface_identifiability_v0.py
omega_v2/validation/process_interface_identifiability_v0.py
tests/test_omega_v2_process_interface_identifiability.py
formal/lean/OmegaV2/Finite/Identifiability.lean
docs/research_notes/omega_v2/process_interface_identifiability_report_v0.md
```

Retain:

```text
summary.json;
interface_profiles.csv;
identification_results.csv;
influence_edges.csv;
independence_census.csv;
independence_witnesses.csv;
negative_controls.csv;
memory_injectivity.csv;
report.md.
```

## Acceptance Criteria

The sprint is retained only if:

1. The analyzer enumerates every nonempty proper component subset.
2. Structural results are invariant to state annotations.
3. Component renaming transports, rather than changes, the result.
4. Observational evidence leaves causal features unknown.
5. Intervention evidence uses exhaustive source-coordinate perturbations.
6. Common-driver and copied-record controls create no phantom causal edge.
7. The observationally equivalent pair separates under intervention.
8. The exact 256-system census is complete and reproducible.
9. Every independence verdict is backed by an exact witness or explicitly
   limited to the census.
10. Identified and set-identified positive controls both pass.
11. The memory-injectivity control separates copy from reversible update.
12. Lean checks without `sorry`, `admit`, `axiom`, or placeholder theorem.
13. Focused and full Python tests pass.
14. No valuer, agency, standing, identity, value, or moral verdict is emitted.

## Kill Conditions

Stop for audit rather than retain the sprint if:

```text
an injected atom changes a structural profile;
the analyzer consumes a component named agent or controller specially;
an observational correlation is emitted as a causal edge;
a common driver creates a descendant-to-descendant influence edge;
a copied record is credited with the source's causal effect;
an observationally equivalent pair is declared uniquely identified without
intervention evidence;
one interface is selected from several incomparable minima;
the census samples rather than enumerates all 256 systems;
absence of an isolating pair is reported as a universal theorem;
the copy and XOR update controls differ in their world dynamics;
or any result is interpreted as valuerhood, agency, identity, standing, value,
moral license, or universal Omega.
```

## Public Compression

Exact dynamics do not automatically supply a unique process boundary.
Observation alone may leave several boundaries compatible with the data.
Interventions can shrink that evidence fiber, but even complete finite causal
evidence may retain several incomparable minimal interfaces. A process
interface should therefore be identified as a set-valued, feature-relative
object, not inserted by an `agent` label or selected by fiat.
