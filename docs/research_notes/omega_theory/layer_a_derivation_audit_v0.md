# Layer A Derivation Audit v0

Status: derivation ledger / claims hygiene note
Scope: active Layer A formal stack
Claim boundary: not value, not agency, not valuerhood, not deformer theory, not Omega validation

## Core rebase

Layer A should currently be described as a continuation-map integrity
discipline.

It asks:

```text
When can a summary, quotient, presentation, support, boundary proxy, or
transition abstraction be trusted not to erase, fabricate, or hide the
continuation facts it is being used to reason about?
```

This is not a retreat from the larger ambition. It is the floor the larger
ambition needs. Before a theory can talk responsibly about value-bearing
continuation, it must first know when its maps of continuation are sound.

## Classification rule

Every active object should be classified as one of:

```text
Supplied:
  assumed from a substrate, adapter, declared panel, model, or candidate.

Derived:
  follows from supplied structure.

Contract:
  explicit sufficient condition we require in order to transfer or preserve a
  fact.

Witness:
  finite example showing a tempting implication fails or a contract is strict.

Analogue:
  known mathematical neighbor.

Non-claim:
  what the object does not establish.
```

The most important hygiene rule is:

```text
Supplied candidates do not have standing until they pass derived validity
checks.
```

For support language, this means:

```text
declared support = candidate carrier
valid support = carrier with a certificate
```

## Current source-of-structure table

| Area | Supplied | Derived | Contracts | Witnesses / strictness | Standard analogue | Non-claims |
|---|---|---|---|---|---|---|
| Alpha primitive core | `Rel`, `Sep`, `Asym` | primitive apartness, relation-generated paths, primitive noncollapse from actual witnesses, primitive-sound presentation constraints | primitive-preserving map laws and sound-presentation pullback | collapse blockers, constant-presentation unsoundness, no maps to collapsed targets | indexed apartness, graph reachability, sound quotient discipline | does not derive consequence, adapter dynamics, value, or agency |
| Primitive exposure / realization bridge | Alpha frame, Alpha consequence system, adapter transition relation, safety/recurrent carrier assumptions | proto seed from primitive nondegeneracy plus exposure; internal paths from primitive paths plus realization; carrier certificate from mutual reach plus exposure/realization/recurrent safety | consequence exposure of primitive apartness; dynamics realization of primitive relation | blocks Alpha-alone proto-teleology and Alpha-alone dynamics claims | observation exposure, simulation/realization contract | exposure, dynamics, safety, and recurrence remain adapter-supplied |
| Generic presentation soundness | forbidden-merge relation and presentation map | kernel-avoidance soundness, pair visibility, pullback along forbidden-preserving maps | choice of forbidden relation | constant presentation unsound when forbidden pairs exist | kernel containment, sound quotient/refinement | does not choose the correct forbidden relation |
| Continuation deformation compression | summary and declared continuation fact | deformation/proxy failure as non-factorization | declared fact selection | same summary with different fact blocks factorization | non-factorization, anti-Goodhart witness | not a deformer object or agency claim |
| Approximation contract compression | exact claim predicate and abstract claim predicate | soundness, completeness, exact approximation | choice of exact facts and abstract claim language | empty abstraction is sound but incomplete when exact facts exist; total abstraction is complete but unsound when false claims exist | abstract interpretation, sound approximation | does not prove declared exact facts are the right substrate facts |
| Carrier semantics compression | carrier presentation/denotation, dynamics, safety | carrier semantics, round-trip path membership, semantic certificates | path-match and recurrence/certification checks | raw support is only one carrier presentation | transition-system language semantics | not objecthood, identity, boundary, or agency |
| Consequence relation | contexts, outcomes, consequence map, comparison, evaluated panel | compatibility, identifiability, separation, merge blocking | panel health predicates | collapse, over-separation, universal allowance, all-refusal checks | contextual equivalence, apartness, observational indistinguishability | not purpose, value, or preference |
| Sound quotient / presentation | quotient or presentation map | kernel containment / sound merge condition | soundness, reflection, loss visibility | phantom reachability, hidden loss | sound quotient, abstraction/refinement | not boundary realism |
| Non-factorization | summary function and target function | target not determined by summary | none required | same summary with different target | factorization through quotient / fiber constancy | not a proof that every summary fails |
| Reachability / viability | transition relation `Next`, safety predicate `safe` | reach, finite paths, viability, safe prefixes | reflection contracts for abstraction | phantom and hidden reach/viability losses | fixed points, viability theory, transition systems | not value or ethics by itself |
| Recurrent carrying | candidate carrier `C`, endpoints `x y` | recurrent carrying certificate, loss, restoration, rerouting facts | transfer, path-transfer, extension, lineage, successor contracts | endpoint viability not enough, forward reachability not enough, individual carrying not joint carrying | strongly connected components, invariant sets, recurrent classes | not identity, selfhood, agency, or objecthood |
| Simulation transfer | source/target dynamics, candidate carriers, correspondence relation | path transfer through relation simulation; map simulation as graph-relation instance | recurrent target carrier, edge-to-path simulation, separation preservation | same-support and map transfer are not primitive identity claims | simulation/refinement, graph of a function | not bisimulation or recoverable identity |
| Profile abstraction | exact allow/block profile, abstract allow/block claims | local profile soundness/completeness as generic approximation contracts | sound and complete abstraction contracts | sound but incomplete, complete but unsound | abstract interpretation | not proof that a coarse view is true |

## Module audit pattern

Each module should be auditable using this template:

```text
Module:

Supplied:

Derived:

Contracts:

Positive theorem:

Witness / strictness:

Standard analogue:

Non-claims:

Self-validation risk:
```

## Recurrent-support audit summary

### RecurrentSupportRobustness

Supplied:

```text
ConsequenceSystem S
transition relation Next
safety predicate safe
candidate carrier C
declared endpoints x y
```

Derived:

```text
RecurrentSupportCarries S Next safe C x y
endpoint viability
missing endpoint/path destruction lemmas
```

Non-claim:

```text
C is not an object, boundary, self, or agent.
C is a candidate carrier; carrying gives it pair-relative standing.
```

### RecurrentSupportTransfer

Supplied:

```text
source dynamics Next0
target dynamics Next1
candidate carrier C
safe0 and safe1
```

Contract:

```text
SafeTransfersOn C safe0 safe1
NoNewExitsFrom Next1 C
InternalEdgesPreservedOn Next0 Next1 C
```

Positive theorem:

```text
the contract transfers recurrent carrying on the same carrier.
```

Self-validation risk:

```text
The theorem is a sufficient-condition theorem. Its hypotheses contain the
needed preservation structure. It should not be sold as a natural law.
```

Strictness already present:

```text
path-level transfer strictly relaxes edge-level transfer.
the broken cycle violates the internal-edge preservation clause.
```

### RecurrentSupportPathTransfer

Contract:

```text
old internal paths are replaceable by new internal paths.
```

Improvement over edge transfer:

```text
allows rerouting without exact edge identity.
```

Remaining issue:

```text
still a declared sufficient condition unless derived from a standard
correspondence such as simulation.
```

### RecurrentSupportExtension / Lineage / SuccessorDistinction

Contract:

```text
extension: carrying transfers from C into D under replacement paths inside D.
lineage: target carrier explicitly carries the same endpoints.
successor: target carrier carries translated endpoints under a relation that
preserves merge separation.
```

Non-claim:

```text
not recoverability, not identity through time, not deformer theory.
```

## Repair direction

The current support stack should be retained as a fallback sufficient-condition
calculus, but future work should move toward:

```text
CarrierCertificate:
  declared support becomes a candidate carrier; carrying is the certificate.

GeneratedCarrier:
  canonical candidate carriers generated from reachability/path structure.

SimulationTransfer:
  path-transfer contracts derived from standard simulation/refinement
  relations rather than hand-listed preservation clauses.

Trajectory languages:
  eventual replacement or complement for spatial support language.
```

## Landed repair modules

This repair pass has landed the first version of those moves:

```text
CarrierCertificate.lean
  support predicates are candidate carriers; recurrent carrying is the
  certificate that gives them pair-relative standing.

GeneratedCarrier.lean
  mutual-reach carriers provide canonical candidates generated from internal
  path structure.

CarrierTrajectoryLanguage.lean
  carrier certificates expose round-trip path-language membership.

SimulationTransfer.lean
  certificate transfer can be derived from map-based and relation-based
  edge-to-path simulation.

CarrierPresentationValidity.lean
  sound presentations cannot erase certified carrier endpoints.
```

## Near-term rule

Do not introduce a deformer object yet.

Use the neutral Layer A form:

```text
future deformation = change in a derived continuation fact under a declared
transformation.
```

Candidate derived continuation facts include:

```text
reach
viability
joint viability
consequence identifiability
merge separation
exact recovery
recurrent carrier certificate
trajectory language membership
```

A later deformer candidate can be defined only after this transformation-level
language is stable.

## Over-compression guardrail

Compression should expose repeated proof forms, not delete distinctions that
carry theory load.

Keep domain-specific names at the boundary:

```text
PrimitiveApart
ConsequenceMergeSeparated
TargetSeparatedBy
CarrierCertificate
RecurrentSupportCarries
ConsequenceExposesPrimitiveApartness
DynamicsRealizesPrimitiveRel
```

Use generic names underneath:

```text
Forbidden
SoundPresentationBy
NonFactorization
SoundApprox
CompleteApprox
```

The safe pattern is:

```text
generic theorem below;
domain-specific theorem above.
```

If compression makes supplied adapter structure look derived, or makes a
sufficient transfer contract look necessary, it has gone too far.
