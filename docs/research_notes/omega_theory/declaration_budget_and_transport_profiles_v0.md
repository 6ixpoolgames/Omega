# Declaration Budget And Transport Profiles V0

Status: discipline note
Scope: adapter/theory hygiene for recoverability, composability, and transport
Claim boundary: not identity theory, not agency, not valuerhood, not Omega validation

## Purpose

The project should not try to be declaration-free. There is no useful adapter
without an interface, a source of observations, and a target class of facts.

The discipline is:

```text
Declare the interface and admissible transformations.
Generate candidates where possible.
Certify invariant facts.
Retain provenance for every choice.
```

This note turns that into a ledger. Its purpose is to prevent smuggling through
supports, carriers, decoders, presentations, lineages, and identity-like
language.

## The Budget Ledger

Every adapter, proof note, or empirical pilot should say what was:

```text
declared:
  supplied by the user, adapter source, registry, or theorem statement;

generated:
  mechanically proposed by a fixed rule from declared inputs;

certified:
  accepted only after passing an invariant check or audit;

searched:
  found by enumerating or optimizing over a candidate space;

selected post-hoc:
  chosen after seeing results and therefore not eligible as validation evidence
  without a separate holdout or adversarial control.
```

This ledger is more important than the label attached to the object. A
declared support is weak. A generated support is better. A generated support
that passes a carrier certificate is stronger. A support selected after seeing
the desired result is a source of evidence leakage.

## Mainline Object: Transport Profile

Use `transport profile` or `certificate bundle` for the mainline object.

Do not use `identity profile` in Layer A.

A transport profile records:

```text
certificates:
  the recovered or carried facts;

transformations:
  the presentation, perturbation, handoff, simulation, or abstraction steps;

tolerances:
  exact or approximate bounds under which transport is being claimed;

evidence:
  successful transports, failed transports, and retained counterexamples.
```

This says:

```text
what survived or was reconstructed under which transformations.
```

It does not say:

```text
this is the same object;
this is a self;
this is an agent;
this is a valuer.
```

## Recoverability And Composability

The mainline should certify two things before touching identity language.

Recoverability:

```text
a declared target, distinction, certificate, or profile can be reconstructed,
re-established, or transported after a transformation.
```

Composability:

```text
multiple recoverable structures coexist, transfer, or remain jointly viable
without destroying one another.
```

These are enough for Layer A.

Identity is not needed to say:

```text
the target recovered;
the loss was hidden;
the carrier certificate failed;
the transfer succeeded;
the two certificates conflict;
the bounded decoder family could not recover the target.
```

## Identity Position

No-self should be used as an anti-smuggling rule, not as a ban on useful
identity-like descriptions.

Mainline rule:

```text
Do not certify identity.
Certify recoverability and composability.
Treat identity as a possible later compression over repeated certificate
transport.
```

This keeps identity downstream.

An identity-like surface may later be useful if a bundle of certificates:

```text
transports across admissible changes;
retains enough consequence-bearing structure;
supports prediction and intervention;
has explicit failure boundaries;
composes with other such bundles without collapsing joint compatibility.
```

But that belongs to the speculative/vortical branch until the lower transport
facts are stable.

## Adapter Checklist

For every adapter run, record:

```text
substrate interface:
  states, traces, actions, observations, transitions, channels, or grids;

declared target:
  what the run is trying to recover, preserve, or detect;

admissible transformations:
  presentation, abstraction, perturbation, handoff, or simulation class;

generated candidates:
  supports, carriers, decoders, summaries, obstacle cases, or correspondences;

certification audits:
  bounded recovery, non-factorization, hidden loss, carrier certificate,
  transfer, sound presentation, or joint compatibility;

controls:
  negative cases, strictness witnesses, stale abstractions, proxy-preserved
  target changes, missing-return failures;

selection timing:
  which choices were declared before the run and which were exploratory.
```

## Current Repository Mapping

Declared:

```text
finite relational domains;
source grid/graph interfaces;
target predicates;
decoder families;
presentation maps;
audit expectations.
```

Generated:

```text
derived graph Alpha-like surfaces;
finite grid movement graphs;
mutual-reach carrier candidates;
generated adversarial cases;
controlled finite empirical families.
```

Certified:

```text
Alpha laws;
sound presentations;
non-factorization witnesses;
bounded recovery;
hidden reachability loss;
carrier certificates;
carrier transfer.
```

Still mostly declared or contract-shaped:

```text
support choices outside generated-carrier flows;
decoder family expressiveness;
admissible transformation classes;
lineage/correspondence choices;
joint target panels.
```

These should be hardened by generation, strictness witnesses, and retained
counterexamples before being used for stronger claims.

## Non-Claims

This note does not define:

```text
identity;
selfhood;
agency;
valuerhood;
value;
Omega;
real-world empirical validity.
```

It only defines a hygiene rule:

```text
keep the declaration budget visible,
generate candidates where possible,
certify recoverability and composability,
and quarantine identity as a later compression over transport profiles.
```

## Near-Term Consequence

The next empirical-adapter step should use this ledger explicitly.

For example:

```text
gridworld obstacle insertion:
  declared interface:
    finite grid, movement rule, source, target;
  generated candidates:
    obstacle insertions and before/after transition relations;
  certified fact:
    hidden reachability loss under stale abstraction;
  retained evidence:
    source digest, compiled model digest, audit finding, search-space count;
  non-claim:
    no real-world validation, no identity, no agency, no Omega.
```
