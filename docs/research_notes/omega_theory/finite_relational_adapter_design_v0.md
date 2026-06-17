# Finite Relational Adapter Design v0

Status: implementation design note
Scope: schema-driven finite adapter IR for Alpha exposure and Layer A audits
Claim boundary: design for a pilot adapter; not empirical validation, not substrate-general transfer, not Omega validation

## Purpose

The next adapter should not be a hand-coded graph witness. It should be a small
universal interface:

```text
substrate-specific source
-> declared finite relational model
-> selected theory profile
-> generic audits
-> retained provenance
```

The first concrete implementation can use finite graph fixtures, but the core
should be reusable for gridworlds, finite channel supports, automata, trace
sets, benchmark-eval summaries, and Alpha primitive presentations.

## Core Principle

Keep the core adapter boring:

```text
finite domains;
named predicates;
named relations;
named functions;
profiles that assign roles;
provenance.
```

Put theory meaning in profiles, not in the model core.

## Universal Core

The core object is:

```text
FiniteRelationalModel:
  domains:
    named finite sets

  predicates:
    named subsets of a domain

  relations:
    named finite relations over declared domains

  functions:
    named finite maps from a domain to labels or another declared domain

  profiles:
    role selections for audits

  audits:
    declared checks to run

  provenance:
    declaration timing, source, controls, artifacts, and claim boundary
```

The old "carrier" field remains usable as shorthand for:

```text
domains.state
```

## Profiles

Profiles interpret named structures without changing the model.

Examples:

```text
Alpha profile:
  rel  -> primitive relation
  sep  -> distinction-indexed separation
  asym -> asymmetric bearing

Continuation profile:
  transition -> selected transition relation
  safety     -> selected safety predicate
  target     -> selected target/loss predicate

Presentation profile:
  presentation -> selected finite function
  forbidden    -> selected forbidden-merge relation

Carrier profile:
  transition -> selected transition relation
  safety     -> selected safety predicate
  carrier    -> selected candidate carrier predicate
  endpoints  -> declared endpoints
  separation -> selected consequence-separation relation

Transfer profile:
  source/target dynamics
  source/target carriers
  correspondence relation
```

This lets future adapters add new profiles without rewriting the core schema.

## Alpha Mapping

Alpha maps cleanly into the finite relational core:

```text
Alpha.X
  -> domains.state

Alpha.Dist
  -> domains.distinction

Alpha.Rel
  -> binary relation over state x state

Alpha.Sep
  -> ternary relation over distinction x state x state

Alpha.Asym
  -> ternary relation over distinction x state x state
```

The adapter must not infer Alpha automatically from arbitrary graph structure.
It should require a declared Alpha profile and provenance.

Safe audit chain:

```text
declared primitive symbols
-> Alpha law audit
-> primitive apartness/path candidates
-> primitive exposure or realization audit
-> consequence/dynamics audits
```

## First Audits

The first implementation should support:

```text
alpha_laws:
  Sep irreflexive;
  Sep symmetric;
  Asym implies Rel;
  Asym implies Sep.

sound_presentation:
  presentation kernel avoids a declared forbidden relation.

phantom_reachability:
  abstract transition has a path that the exact transition lacks.

nonfactorization:
  same summary value, different declared target value.

carrier_certificate:
  declared carrier contains endpoints, is safe, is closed under transition,
  is internally mutually reachable, and carries a declared separation.
```

These are intentionally small. They exercise the current theorem spine without
claiming that the Python adapter proves the Lean theorems.

## Fixture Strategy

Use fixture files, not hard-coded Python examples:

```text
sound_pass.json:
  Alpha laws pass;
  presentation is sound;
  carrier certificate succeeds.

phantom_reachability_fail.json:
  abstract path exists;
  exact path does not;
  phantom reachability is detected.

proxy_nonfactorization_fail.json:
  same proxy score;
  different safety target;
  non-factorization witness is detected.
```

Each fixture should include provenance.

## Provenance Requirements

Every adapter model should include at least:

```text
declared_before_run;
source;
claim_boundary;
```

Richer empirical adapters should use:

```text
docs/templates/ADAPTER_PROVENANCE_TEMPLATE.md
```

## Expected Outputs

The CLI should produce:

```text
model_digest.txt
provenance_check.json
audit_results.json
summary.json
```

The digest makes retained fixtures auditable. The audit results distinguish:

```text
finding:
  what was observed.

passed:
  whether the declared expectation was met.
```

For failure fixtures, `passed = true` can mean the adapter correctly detected a
failure, such as phantom reachability.

## Future Compatibility

This design keeps the path open for:

```text
gridworld compilers;
finite MDP support compilers;
stochastic-channel support compilers;
trace-set compilers;
benchmark-eval compilers;
adapter-to-Lean export;
visualization notebooks;
probabilistic and approximate profiles;
joint viability and transfer profiles.
```

The stable interface is:

```text
source-specific compiler
-> FiniteRelationalModel
-> role profile
-> audit result
```

## Non-Claims

This adapter does not prove:

```text
the declared exact facts are correct for a real substrate;
the abstraction is safe in deployment;
value, agency, valuerhood, or Omega;
that graph fixtures scale to frontier systems.
```

It only tests whether the formal audit discipline can be applied to declared
finite structures with retained provenance.

## Related Notes

- [adapter_provenance_v0.md](adapter_provenance_v0.md)
- [audit_response_roadmap_v0.md](audit_response_roadmap_v0.md)
- [ai_proxy_failure_nonfactorization_v0.md](ai_proxy_failure_nonfactorization_v0.md)
- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [primitive_exposure_realization_bridge_v0.md](primitive_exposure_realization_bridge_v0.md)
