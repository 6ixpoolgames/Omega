# Finite Relational Adapter Design v0

Status: implementation design note
Scope: schema-driven finite adapter IR for Alpha exposure and Layer A audits
Claim boundary: design for a pilot adapter; not empirical validation, not substrate-general transfer, not Omega validation

## Purpose

The next adapter should not be a hand-coded graph witness. It should be a small
universal interface:

```text
substrate-specific source
-> deterministic source compiler
-> finite relational IR
-> selected theory profile / generated profile
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

The most principled shape is not "graph adapter." The principled shape is:

```text
source-specific compiler:
  may know about graph syntax, gridworld syntax, channel syntax, trace syntax,
  or benchmark syntax.

finite relational IR:
  knows only finite domains, predicates, relations, functions, profiles,
  audits, and provenance.

generic audit engine:
  consumes only the finite relational IR.
```

This prevents the source compiler from proving its own conclusions. A source
compiler may derive surfaces, but it must expose those surfaces in the IR before
the generic audits consume them.

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

## Adapter Layers

The pilot has one normalized audit surface and multiple source compilers:

```text
finite grid source
-> derived graph source
-> compiled finite relational IR
-> generic audits

derived graph source
-> compiled finite relational IR
-> generic audits
```

The finite relational IR is intentionally explicit and close to the formal
interfaces. It may contain names like `primitive_rel`, `primitive_sep`,
`primitive_asym`, `merge_separated`, and `carrier_0`.

The derived graph source is much less hand-labeled. It declares only:

```text
nodes;
edges;
observations;
presentations;
safety;
provenance.
```

The compiler derives the formal surfaces mechanically:

```text
Rel:
  directed graph edge.

Sep:
  two states differ under a declared observation.

Asym:
  one-way directed edge plus Sep.

merge_separated:
  some declared observation separates the state pair.

carrier candidate:
  mutual-reach component carrying a separated pair.
```

This keeps the adapter from trusting hand-labeled asymmetry in the source
fixture. It still requires declared observations, presentations, and provenance;
it does not perform unconstrained post-hoc relevance discovery.

Derived graph is the first source compiler. Finite grid is the first additional
source compiler: it derives cells and movement edges from a rectangular grid
source, then routes through the derived graph compiler. Neither source format is
the universal adapter format. Future compilers should target the same finite
relational IR unless they can justify extending the IR itself.

## Hardening Rules

Future adapter work should preserve these constraints:

```text
No private audits:
  source compilers must not make claims that bypass the generic audit engine.

Named derivation rules:
  every generated relation, predicate, carrier, or audit must be traceable to a
  named derivation rule.

Source/IR retention:
  retain both the source artifact and the compiled model artifact.

Digest both sides:
  source digest records the declared input;
  compiled-model digest records the audit surface.

No validation by discovery:
  exploratory candidate generation is allowed only when clearly marked;
  validation claims require predeclared source fields.

No source-trusted asymmetry by default:
  adapter-facing sources should derive asymmetry from directed consequence,
  strict reachability, irreversible loss, or another explicit post-adapter
  rule whenever possible.
```

These rules are stricter than the low-level IR. The IR can still host
hand-written theorem fixtures; adapter-facing sources should avoid that style.

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

The low-level IR can represent a declared Alpha profile directly. The derived
graph layer does something narrower: it derives an Alpha-like exposure from
declared graph observations and strict directed graph structure.

This gives two claim modes:

```text
declared primitive presentation:
  source supplies Rel, Sep, and Asym through the finite relational IR.

derived primitive exposure:
  source supplies graph observations and transitions;
  compiler derives Rel, Sep, and Asym candidates by fixed rules.
```

The derived mode is safer for adapter-facing pilots because asymmetry is an
audit result of the post-adapter structure, not a trusted source label.

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

hidden_reachability_loss:
  a before-transition had a path, the after-transition loses it, and the
  abstract transition still reports it.

nonfactorization:
  same summary value, different declared target value.

carrier_certificate:
  declared carrier contains endpoints, is safe, is closed under transition,
  is internally mutually reachable, and carries a declared separation.

carrier_transfer:
  source and target carriers are both certified and a declared correspondence
  relates the source carrier into the target carrier, including the declared
  endpoints.
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

hidden_reachability_loss_fail.json:
  before dynamics reaches the target;
  after dynamics loses the path;
  abstract dynamics still reports the old path.

proxy_nonfactorization_fail.json:
  same proxy score;
  different safety target;
  non-factorization witness is detected.

carrier_transfer_pass.json:
  source recurrent carrier and target recurrent carrier are both certified;
  declared correspondence covers source carrier and endpoints.

carrier_transfer_fail_missing_return.json:
  source recurrent carrier is certified and correspondence is present;
  target carrier loses return structure, so transfer is rejected.

derived_graph_strict_asymmetry.json:
  source has no primitive relation/separation/asymmetry labels;
  compiler derives Sep from observation difference;
  compiler derives Asym from strict one-way edge plus Sep;
  constant presentation is caught as unsound.

derived_graph_recurrent_carrier.json:
  source has no carrier labels or carrier audit;
  compiler derives an SCC/mutual-reach carrier candidate;
  carrier certificate succeeds for a separated pair.

derived_graph_mixed_asymmetry.json:
  source mixes bidirectional and strict directed edges;
  compiler derives asymmetry only where the one-way edge is paired with an
  observation difference.

finite_grid_east_asymmetry.json:
  source declares a 2x1 east-moving grid;
  compiler derives cells and movement edge before reusing the derived graph
  compiler and generic audits.
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

The derived graph CLI should additionally retain:

```text
source.json
compiled_model.json
source_digest.txt
compiled_model_digest.txt
```

The finite grid CLI retains the same source/compiled/digest outputs, with
compiled provenance marking both `compiled_from = finite_grid` and
`intermediate_compiler = derived_graph`.

The digest makes retained fixtures auditable. The audit results distinguish:

```text
finding:
  what was observed.

passed:
  whether the declared expectation was met.
```

For failure fixtures, `passed = true` can mean the adapter correctly detected a
failure, such as phantom reachability.

## Smoke Validation

The adapter smoke runner exercises all current source layers:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp\finite_relational_adapter_smoke
```

It runs all retained low-level IR fixtures, derived graph fixtures, and finite
grid fixtures. It checks provenance completeness, verifies declared audit
counts, requires retained digest/provenance/audit/summary artifacts, and
confirms that source fixtures do not carry reserved finite relational IR fields.

Generated/adversarial adapter validation is separate:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp\finite_relational_adapter_adversarial
```

It deterministically searches small finite cases for hardening witnesses:

```text
phantom reachability;
hidden reachability loss;
proxy non-factorization;
derived graph asymmetry;
derived graph carrier certification;
finite grid asymmetry.
```

The generator is intentionally finite and boring. It does not discover empirical
truth. It checks that the adapter can produce and retain generated failure-mode
cases without relying only on hand-written fixtures.

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
