# Omega Formalism Primer

Status: public onboarding / current best formalism
Scope: compact bridge from README to the dense theory notes
Claim boundary: formal orientation only; not empirical validation, not valuer detection, not Omega validation

## One-Sentence Ambition

Omega is an attempt to formalize **value-bearing futures** without taking
reward, utility, moral rules, fixed agents, fixed selves, or privileged valuers
as primitives.

The project asks whether there is a substrate-neutral structure beneath those
later concepts:

```text
future-bearing distinctions that propagate recoverably, non-erasingly, and
compatibly through lawful dynamics.
```

The empirical arm is not trying to detect value directly. It is building a
finite microscope for the precursor geometry.

## The Current Formal Object

The current root formalism is **Omega Primitive Calculus v0**.

The root grammar is:

```text
relation -> distinction -> asymmetry
```

Where:

```text
relation:
  composable consequential connectedness

distinction:
  preordered non-equivalence structure; a difference capable of preservation,
  transformation, collapse, or recovery

asymmetry:
  normal lax distinction transport through relation
```

The compact Lean target is:

```text
A : C -> DistTrans
```

where `C` is a category of relational contexts and `DistTrans` is the
support-level category of preorder-indexed distinction transports.

Future-Distinction Dynamics is the current working presentation of this root
calculus for reachable-futures modeling.

The compact working target is:

```text
Omega is the admissible subset of future-field dynamics for which
future-relevant distinctions persist to terminus in a recoverable, non-erasing,
and compatible manner.
```

The newer completion-layer target is:

```text
Omega is the space of maximal admissible compatibility completions in which
proto-valuer-bearing dynamics propagate recoverably and non-erasingly without
systematic irreversible destruction of one another's distinction-content.
```

This is the target formal object. It is not an empirical result.

## Why This Is Not Utility, Reward, or Ethics

Omega is not defined as:

```text
maximizing reward;
maximizing utility;
maximizing entropy;
minimizing suffering;
preserving life;
preserving agents;
obeying a moral rule;
protecting a privileged valuer.
```

Those may be downstream interpretations in some substrates. They are not
allowed as primitives.

The project starts lower:

```text
Can futures carry distinctions?
Can those distinctions remain recoverable?
Can they avoid erasing one another under composition?
Can a process maintain distinction-content through churn better than matched
identity-decay nulls?
Can such processes compose into maximal compatibility completions?
```

## Layered Formal Stack

The current theory arm is organized as a ladder.

### Layer 0: Omega Primitive Calculus v0

Primary note:

```text
docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md
```

Defines:

```text
relation;
distinction;
asymmetry;
recoverability;
recurrent recoverability;
non-erasure;
joint compatibility;
completion.
```

Lean root files:

```text
formal/lean/OmegaCore/DistTrans.lean
formal/lean/OmegaCore/NormalLax.lean
```

Checked:

```text
DistTrans closure;
relation-level identity and associativity laws;
recoverability weakening;
recoverability strengthening;
compositional recoverability from laxity;
non-erasure monotonicity;
finite-chain recurrent recoverability;
finite-enumeration maximal completion existence;
Finset/Fintype maximal completion existence;
finite completion counterexamples;
marginal-like non-erasure not implying strictly joint non-erasure;
adapter-failure examples for missing closure or laxity laws.
```

### Layer 0a: Future-Distinction Dynamics

Primary note:

```text
docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md
```

Defines:

```text
future fields;
admissible observables;
future-distinctions;
future-distinction capacity;
recoverability;
non-erasure;
compatibility;
proto-Omega / Omega claim discipline.
```

Key correction:

```text
Persistent distinction does not mean "different under every quotient forever."
It means separable under a declared admissible observable family over a declared
horizon regime.
```

### Layer 1: Admissibility and Identity-Decay Nulls

Primary notes:

```text
docs/research_notes/omega_theory/admissibility_enrichment_and_identity_decay_nulls.md
docs/research_notes/omega_theory/identity_decay_null_taxonomy_v0.md
```

Purpose:

```text
Define candidate process bundles, activity channels, matched nulls, and
maintenance gaps without making self, identity, or dissolution primitive.
```

Key correction:

```text
Identity-decay is not a cosmic law. It is a declared matched null comparison:
what distinction-content would be expected to decay when the maintaining
activity is passivized, randomized, ablated, unsupported, or otherwise removed.
```

### Layer 2: Proto-Valuer Ladder

Primary notes:

```text
docs/research_notes/omega_theory/omega_proto_valuer_compatibility_completions.md
docs/research_notes/omega_theory/finite_proto_valuer_separation_theorems_v0.md
docs/research_notes/omega_theory/tiny_transition_system_witnesses_v0.md
```

The ladder is:

```text
future-distinction capacity
-> process-bundle designation
-> maintenance over identity-decay null
-> self-conditioning of transition environment
-> proto-valuer
-> compatibility-audited valuer
```

Important boundary:

```text
Current empirical results do not instantiate proto-valuers or valuers.
```

The ladder exists to prevent overpromotion from local persistence or high
residuals into value language.

### Layer 3: Compatibility Completions

Primary notes:

```text
docs/research_notes/omega_theory/finite_omega_completion_theorems_v0.md
docs/research_notes/omega_theory/compatibility_audit_taxonomy_v0.md
```

The completion layer asks:

```text
Which candidate future-bearing units can jointly propagate without systematic
irreversible destruction of each other's distinction-content?
```

Finite theorem scaffolds currently establish:

```text
finite maximal admissible completions exist when the admissible family is
nonempty, including the Finset/Fintype specialization now checked in Lean;

a greatest completion need not exist, now checked as a finite Lean
counterexample;

pairwise admissibility does not imply joint admissibility, now checked as a
finite Lean counterexample;

marginal-like non-erasure does not imply strictly joint non-erasure, now checked
as a finite Lean distinction-transport counterexample;

finite completions are computable by exhaustive enumeration in principle.
```

These are small finite facts, not a proof that Omega exists physically.

### Layer 4: Finite Distinction Measures

Primary note:

```text
docs/research_notes/omega_theory/finite_distinction_measures_v0.md
```

Purpose:

```text
Prevent the metric from becoming a back door.
```

Finite distinction measures must be:

```text
predeclared;
finite;
reconstructible;
observable-indexed;
horizon-scoped;
control-auditable;
claim-bounded.
```

They may measure finite distinction structure. They do not detect value,
valuerhood, agency, identity, support, capture, erasure, compatibility, or
Omega.

### Layer 5: Empirical Interface

Primary empirical instrument:

```text
Future Field Atlas
```

It emits:

```text
formal spec identity;
reachable-frontier topology;
product and coupled future-field baselines;
artifact completeness status;
reconstruction audits;
operator and observable summaries;
compact retained morphology.
```

The empirical arm must eventually add:

```text
process-bundle manifests;
admissible observable manifests;
identity-decay null manifests;
maintenance-gap rows;
self-conditioning rows;
compatibility-audit rows.
```

Those are future targets, not current claims.

## Current Empirical Status

The current empirical result is modest but useful.

Future Field Atlas can measure reconstructible finite future-field topology
under lawful transition substrates.

Current coupled rank-order-boundary results show a marginal-preserving
joint-restriction class under `symbol_histogram_distance`:

```text
pair005
pair012
pair014
pair026
```

The observed pattern:

```text
A and B marginal support are preserved;
joint support is restricted relative to the product baseline;
the effect is visible in compact topology summaries and targeted H128 depth.
```

The tested alternate observables:

```text
hamming_weight_or_nonzero_count
total_coordinate_mass
```

did not reproduce the high-yield signature.

The first formal-interface distinction panel is now complete. It maps the
high-yield representatives and low/medium controls into declared finite
distinction-measure artifacts across product, zero-penalty joint rank-prefix,
scalar mismatch 0.020, shared_capacity v1, and rank_order_boundary references.
The panel has 40 / 40 cells available and 0 missing or blocked cells.

## What Is Not Claimed

The project does not currently claim:

```text
Omega validation;
proto-valuer detection;
valuer detection;
agent detection;
identity detection;
value detection;
compatibility detection;
support / capture / erasure detection;
life or self-replication detection;
holdout readiness;
substrate-general theory validation.
```

The strongest current claim is:

```text
We have a formal target, finite scaffolds that block several easy collapses,
and an empirical atlas that can probe precursor future-field topology under
strict reconstruction and claim boundaries.
```

## Recommended Reading Order

For theory:

```text
1. docs/research_notes/omega_theory/README.md
2. docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md
3. docs/research_notes/omega_theory/theory_arm_map_v0.md
4. docs/research_notes/omega_theory/finite_omega_completion_theorems_v0.md
5. docs/research_notes/omega_theory/finite_distinction_measures_v0.md
6. docs/research_notes/omega_theory/compatibility_audit_taxonomy_v0.md
```

For empirical status:

```text
1. docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_interface_distinction_panel_result.md
2. docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md
3. docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md
4. docs/research_notes/validation_results/future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md
5. docs/PUBLIC_RESULTS_INDEX.md
```

For operations:

```text
docs/OMEGA_PROJECT_MANUAL.md
```
