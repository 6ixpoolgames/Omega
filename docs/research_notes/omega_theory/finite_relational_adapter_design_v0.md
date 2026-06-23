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

The executable source-contract rule is:

```text
source-level compilers may declare substrate syntax:
  nodes, edges, observations, presentations, grids, obstacles,
  source/target graph pairs, or correspondences.

source-level compilers may not declare finite relational IR surfaces:
  predicates, relations, functions, profiles, audits.
```

The helper `omega.adapters.finite_relational.source_contract` now provides the
shared reserved-field gate used by derived graph, finite grid, and grid
obstacle source compilers. It also exposes a small compiled-provenance check so
tests can require named derivation rules rather than trusting the compiler by
inspection.

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

bounded_recovery:
  a declared observation function and declared decoder family are checked
  against a declared target predicate; recovery means some decoder in the
  bounded family exactly recovers target membership from the observation.

target_scramble_sensitivity:
  a declared target predicate and a supplied scrambled/erased target predicate
  are compared under the same observation and decoder family. The audit is
  sensitive when exact recoverability or the successful decoder surface changes.
  This is a provenance gate against decorative targets; it does not prove that
  the target is empirically correct or value-bearing.

presentation_fact_closure:
  a declared presentation family is checked for common visible pairs and
  common target predicates. The audit can require selected pairs or targets to
  be common, and selected pairs or targets to be absent from the common facts.
  This is the adapter analogue of the Lean presentation/fact closure pilots.
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

simple_form_nonfactorization_fail.json:
  same simple-form summary;
  different declared functional target;
  non-factorization witness is detected.

entropy_controlled_nonfactorization_fail.json:
  same entropy/histogram summary;
  different bounded-recoverability target;
  non-factorization witness is detected.

ordered_trace_nonfactorization_fail.json:
  same unordered trace bag;
  different order-sensitive recovery target;
  non-factorization witness is detected.

bounded_recovery_pass.json:
  a declared observation and decoder family include a decoder that exactly
  recovers the target predicate.

bounded_recovery_entropy_fail.json:
  the observation histogram matches the pass fixture, but every observed label
  mixes target-true and target-false states, so no declared decoder recovers
  the target.

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

Generated/adversarial validation also includes:

```text
generated_presentation_fact_closure:
  derived graph source declares only nodes, edges, observations, presentations,
  safety, and provenance;
  compiler derives the carrier certificate;
  generated closure audits show the certified endpoint pair is common-visible
  under identity presentation and absent after admitting a constant
  presentation.

generated_reachability_fact_closure:
  generated finite transition relation derives a can-reach-goal target
  predicate; exact reach-status presentation preserves it, while constant
  status removes it from common target facts.

generated_viability_fact_closure:
  generated finite transition/safety structure derives a self-sustaining-safe
  target predicate; exact viability-status presentation preserves it, while
  constant status removes it from common target facts.

generated_recovery_fact_closure:
  generated observation/decoder structure checks bounded recovery for an exact
  observation and failure for a constant observation; exact observation
  preserves the target fact, while constant observation removes it from common
  target facts.

generated_stale_reflected_fact_closure:
  generated before/after transition relations derive stale and reflected
  reach-status presentations; stale preserves the before-loss reachability
  fact, reflected preserves the after-loss reachability fact, and their common
  closure keeps only the constant target.

generated_multi_presentation_fact_closure:
  generated row and column presentations preserve different exact facts; the
  declared family closure keeps only facts visible through every presentation.

generated_crosscutting_presentation_closure:
  generated row, column, and parity presentations each preserve a different
  exact target fact; the full declared family keeps only the constant target
  and no ordered visible state pairs.

generated_graph_pair_transfer:
  generated source and target graph cycles are compiled separately, then a
  declared endpoint correspondence is audited as a carrier-transfer contract.

generated_graph_pair_transfer_missing_return:
  generated source and target graphs keep the same declared endpoint
  correspondence, but the target graph loses its return edge, so carrier
  transfer is rejected.

generated_transport_fact_closure:
  generated source and target recurrent carriers satisfy the carrier-transfer
  audit; lifted source/target endpoint-role presentations preserve a
  transported role fact, while an erasing transport view removes that role from
  common target facts.

generated_failed_transport_fact_closure:
  generated source carrier and endpoint correspondence look transfer-like, and
  lifted role presentations preserve the transported role label; the
  carrier-transfer audit rejects transfer because the target loses return
  structure.
```

Each fixture should include provenance.

Graph-pair transfer characterization is a source-generator path rather than a
single adversarial case:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_graph_pair_transfer `
  --out-root .tmp\finite_relational_graph_pair_transfer
```

It declares:

```text
source graph;
target graph;
endpoint correspondence;
source and target endpoint roles.
```

It derives:

```text
compiled source graph IR;
compiled target graph IR;
carrier-transfer audit surface;
source/target compiled-model digests.
```

The current characterization enumerates:

```text
two-node target graph edge subsets;
three-node target graph edge subsets with an intermediate target state.
```

The three-node sweep is the important extension control: transfer can be
accepted when target support expands beyond the two source endpoints, but only
if the whole target carrier still earns recurrent certification. Endpoint
correspondence alone is not enough, and target forward endpoint reachability is
not enough either.

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

Second-source parity has a separate retained-output path:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_source_parity `
  --out-root .tmp\finite_relational_source_parity
```

It compares equivalent derived-graph and finite-grid source artifacts after
compilation into finite relational IR. The retained parity cases check:

```text
graph_grid_strict_asymmetry_parity:
  relation, separation, asymmetry, presentation, and audit findings match
  after declared state renaming.

graph_grid_recurrent_carrier_parity:
  recurrent carrier certification, merge separation, presentation, and audit
  findings match after declared state renaming.

graph_grid_observation_closure_parity:
  a source-derived observation target, presentation/fact closure findings, and
  observed closure payloads match after declared state renaming.
```

This is still synthetic compiler parity, not empirical validation. It helps
ensure that the normalized IR is not merely an artifact of one source compiler.

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
finite grid asymmetry;
presentation/fact closure shrinkage for a derived carrier pair;
presentation/fact closure shrinkage for generated reachability, viability, and
recovery-style target facts;
presentation/fact closure shrinkage for stale/reflected reach-status facts;
presentation/fact closure shrinkage for multi-presentation row/column fact
intersections;
presentation/fact closure shrinkage for transported endpoint-role facts under
a carrier-transfer contract;
failed-transport control showing role-label closure is weaker than earned
carrier transfer.
```

The generator is intentionally finite and boring. It does not discover empirical
truth. It checks that the adapter can produce and retain generated failure-mode
cases without relying only on hand-written fixtures.

Controlled synthetic empirics are a separate path:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_empirical `
  --out-root .tmp\finite_relational_adapter_empirical
```

This path enumerates declared small search spaces and reports frequencies, not
just existence witnesses. The first pilot covers:

```text
fixed 2/2 observation histogram vs bounded target recovery;
unordered trace bags vs order-sensitive trace recovery;
stale abstraction hiding exact reachability loss;
endpoint forward reachability without recurrent carrier certification.
```

It is still synthetic finite empirics. A pass means the generated study and its
representative audits ran as declared; it does not validate a real substrate.

The first source-generator pilot beyond generic enumeration is gridworld
obstacle insertion:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_grid_obstacle `
  --out-root .tmp\finite_relational_grid_obstacle
```

This generator declares:

```text
finite grid dimensions;
movement rule;
source and target cells;
before and after obstacle sets.
```

It derives:

```text
before transition relation;
after transition relation;
stale abstract transition relation;
hidden-reachability-loss audit.
```

The current characterization enumerates obstacle insertions over three small
source-level grid classes:

```text
3x3 orthogonal midline source-target path;
3x3 directed east/south diagonal source-target path;
4x2 orthogonal rectangular source-target path.
```

Each study retains both a hidden-loss representative and a no-hidden-loss
control. This is still synthetic source-level validation, not external
empirical evidence.

The retained representatives also derive source-reach status presentations:

```text
stale_source_reach_status:
  reachability from the declared source under before dynamics.

reflected_source_reach_status:
  reachability from the declared source under after dynamics.
```

The optional grid closure audits check:

```text
reflected status preserves after_reachable_from_source;
adding stale status to the family removes after_reachable_from_source from
the common target facts while retaining all_states.
```

This makes the grid obstacle characterization an empirical-adjacent
source-generator example for both hidden loss and presentation/fact closure.

The simple-form, entropy, ordered-trace, and bounded-recovery fixtures are
motivated by the useful-information and constraint-selection note:

```text
useful_information_and_constraint_selection_v0.md
```

They keep raw complexity, entropy, and unordered summaries in proxy/audit
position. They are not implementations of epiplexity or generalization theory.

The deterministic pre-stochastic recovery layer has a separate runner:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_deterministic_layer `
  --out-root .tmp\finite_relational_deterministic_layer
```

It covers exact recovery and observation discipline before stochastic or
approximate audits are introduced:

```text
joint bounded recovery failure;
decoder class strictness;
observation refinement monotonicity;
deterministic garbling non-improvement;
minimal sufficient observation;
reflected versus stale hidden loss.
```

This runner is not a new source compiler. It is a finite deterministic
calibration surface for later stochastic adapter work.

The first stochastic characterization layer also has a separate runner:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_stochastic_recovery `
  --out-root .tmp\finite_relational_stochastic_recovery_robust_randomized
```

It uses exact rational finite channels and records a recovery surface rather
than imposing a threshold:

```text
support ambiguity;
support-exact recovery;
optimized worst-case deterministic decoder success;
declared-versus-optimized decoder gap;
coarsening/refinement behavior;
per-source failure localization;
joint versus marginal recovery;
declared randomized decoder behavior;
declared robust randomized recovery over an ambiguity set.
```

The coarsening check has a narrow information claim: if a coarse observation is
deterministic post-processing of an already available fine observation, an
unrestricted fine decoder can simulate the coarse decoder. This does not deny
that coarse variables can be semantically useful, target-aligned, more stable,
or more legible.

The first stochastic continuation-loss layer has its own runner:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_stochastic_continuation `
  --out-root .tmp\finite_relational_stochastic_continuation
```

It uses exact rational transition kernels and finite-horizon hit probabilities.
The current checks cover:

```text
stale abstraction hiding stochastic hit-probability loss;
reflected abstraction reporting the loss;
reflected hit-status preserving the after-hit target fact;
stale/reflected hit-status closure dropping that nonconstant fact;
one selected hit-probability scalar matching while the horizon profile differs.
```

The first policy-conditioned stochastic dynamics layer has its own runner:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_policy_dynamics `
  --out-root .tmp\finite_relational_policy_dynamics
```

It adds finite actions and deterministic policies while keeping exact rational
arithmetic and finite horizons. Its retained artifacts intentionally separate:

```text
facts.json:
  generated finite facts

hypotheses.json:
  expected/observed/pass-fail interpretation
```

The current checks cover stale/reflected policy hit-probability loss,
policy-conditioned stale/reflected hit-status closure over the after-hit target
fact, and a policy-conditioned non-factorization witness where the same coarse
support summary yields different hit probability.

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
