# External Reader Guide

Status: onboarding guide for outside collaborators
Scope: current Alpha primitive floor, Omega support stack, and Future Field Atlas workspace
Claim boundary: this repository does not claim Omega validation, agency detection, value detection, identity detection, life detection, candidate promotion, holdout readiness, or graph-channel causality.

## 0. What this repository is

This repository is an empirical research workspace for the Omega / Reachable Futures project.

For the shortest public overview, read the repository README first. For the
current formal stack, read:

```text
docs/OMEGA_FORMALISM_PRIMER.md
docs/research_notes/omega_theory/alpha_primitive_core_v0.md
docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md
```

This guide is the longer collaborator tour: it explains how the formal ambition
connects to the current Future Field Atlas empirical branch and what the current
results do and do not mean.

The current primitive floor is **Alpha Primitive Core v0**:

```text
relation -> distinction -> asymmetry
```

Lean separately checks the older OmegaCore support/recoverability skeleton:

```text
A : C -> DistTrans
```

The checked Lean layer now includes:

```text
DistTrans closure and relation-level category laws;
Alpha primitive frame and finite separation examples;
recoverability weakening / strengthening;
compositional recoverability from laxity;
non-erasure monotonicity;
finite-chain recurrent recoverability;
finite-enumeration maximal completion existence;
Finset/Fintype maximal completion existence;
finite completion counterexamples;
marginal-like non-erasure not implying strictly joint non-erasure;
adapter-failure examples for missing closure or laxity laws;
Boolean relation support presentation;
finite channel / partition presentation;
probabilistic channel presentation with exact/probabilistic separation,
full-support converse, and finite cascade error bound.
```

Future Field Atlas is not Omega proper. It is an empirical instrument that tries
to expose finite reachable-future substrates to that root grammar.

The current work asks a narrow question:

```text
Can neutral finite transition systems produce measurable future-landscape
structure that separates from matched nulls, without importing semantic labels
such as agent, valuer, identity, or good?
```

The current implementation target is **Future Field Atlas** instrumentation:

```text
generate lawful substrates;
unfold reachable frontiers;
record raw topology;
map geometry;
contrast conditions;
label only as a derived view.
```

The immediate predecessor instrument is **horizon transport**:

```text
T_{H_a -> H_b}
```

It measures how structures in earlier reachable-future frontiers become structures in later reachable-future frontiers. The atlas rebuild keeps that lesson, but makes raw frontier topology and rank-boundary anatomy the primary data product before response labels are applied. Current atlas conditions are represented by state-space, transition-law, selection-operator, observable, and frontier-scan specs. The latest H32 publication-schema smoke also emits formal spec manifests, condition-identity manifests, artifact-completeness summaries, and reconstruction audits for derived artifacts. Historical treatment names are translation aids in the atlas glossary, not runtime primitives.

The current atlas posture is now morphology-first. Retained coupled runs are
postprocessed into pair-aware morphology tables before designing richer coupled
operators. The rank-order-boundary branch now has four high-yield
symbol_histogram_distance exemplars: pair005, pair012, pair014, and pair026.
Pair012, pair014, and pair026 were confirmed under targeted H128. The observable-extension smoke did
not reproduce the high-yield signature under `hamming_weight_or_nonzero_count`
or `total_coordinate_mass`.

The historical substrate lineage used explicit **transition energy**:

```text
E(s,t)
```

where `E(s,t)` is an edge-selection score over possible transitions. It is not utility, reward, fitness, value, thermodynamic energy, or Omega.

## 1. What this repository is not claiming

This repository does **not** currently claim:

```text
Omega validated;
agent detected;
valuer detected;
identity detected;
life detected;
self-replication detected;
candidate promoted;
holdout ready;
graph-channel causality established;
value-bearing structure demonstrated.
```

Positive results should be read as **instrument and substrate-characterization results**, not as full theory validation.

## 2. Current result in plain English

The project now has a checked formal root and a bounded empirical instrument.

Formal side:

```text
Omega Primitive Calculus v0 has a Lean-checked support-level root skeleton.
It also has finite counterexamples, adapter-failure examples, and two worked
presentations: Boolean relation support and finite channel / partition
recovery.
```

Empirical side:

```text
Future Field Atlas measures finite reachable-frontier topology under declared
operators and observables.
```

The strongest current empirical pattern is narrow:

```text
rank_order_boundary under symbol_histogram_distance
```

High-yield representatives:

```text
pair005
pair012
pair014
pair026
```

Observed geometry:

```text
A and B marginal support are preserved;
joint support is restricted relative to the product baseline;
the effect persists in targeted H128 depth checks for pair012, pair014, and
pair026;
tested alternate observables did not reproduce the high-yield signature.
```

This is not an Omega result. It is a product-vs-coupled finite future-field
geometry result under declared operators.

## 3. Core vocabulary

### Distinction

A finite state space:

```text
X
```

States differ from one another.

### Relation

A transition relation:

```text
s -> t
```

Some states can transform into other states.

### Asymmetry

A transformation is not equivalent to its reverse, or does not have the same future consequences.

### Horizon

A finite lookahead scale. Horizon transport compares structures at one horizon to structures at another.

### Horizon transport

A directional matrix family:

```text
T_{H_a -> H_b}
```

This asks what earlier reachable-future structures become later.

### Transition energy

An edge-selection score:

```text
E(s,t)
```

Lower-energy transitions are selected more readily. This is a substrate-generation rule, not a value claim.

### Directional asymmetry

A scalar asymmetry field:

```text
A(s)
```

used through:

```text
A(t) - A(s)
```

This makes one direction across the field different from the reverse.

### Preservation asymmetry

A macro-invariant or coarse asymmetry coordinate:

```text
I(s)
```

used through:

```text
|I(t) - I(s)|
```

This makes erasing or changing a coarse distinction less available than preserving it.

### Matched nulls

Control matrices that preserve important low-level structure, such as row/column marginals, while destroying the candidate structure being tested. Passing these nulls is an instrument requirement, not a theory validation claim.

### Perturbation response

A perturbation is not treated as simple survival/failure. It can produce response profiles:

```text
stable
amplified-aligned
weakened
rerouted
reopened
collapsed
control-equivalent
measurement-limited
```

## 4. Historical transition-energy substrate context

The transition-energy ladder is important historical context for how the
empirical instrument reached its current coupled Future Field Atlas form.

Earlier substrate work used:

```text
E0 locality only:
  E(s,t) = d(s,t) + roughness

E1 directional asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + roughness

E2 preservation asymmetry:
  E(s,t) = d(s,t) + beta * |I(t)-I(s)| + roughness

E3 combined asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + beta * |I(t)-I(s)| + roughness
```

The historical read was:

```text
E0:
  baseline

E1:
  differentiated response / rerouting

E2:
  preservation-asymmetry response in the tested substrate family

E3:
  clean but not yet tuned or synergistic in the sparse tested grid
```

This is no longer the public front-door claim. The current public-facing center
is the Lean-checked root calculus plus Future Field Atlas as a finite
reachable-future instrument.

## 5. Best first reading path

### 15-minute orientation

Read:

1. `README.md`
2. `docs/OMEGA_FORMALISM_PRIMER.md`
3. this guide
4. `docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md`

Goal: understand the current formal root, empirical microscope, and claim
boundary before reading older probe results.

### 60-minute technical orientation

Read:

1. `docs/research_notes/omega_theory/README.md`
2. `docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md`
3. `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_adapter_conformance_package_result.md`
4. `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_interface_distinction_panel_result.md`
5. `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md`
6. `docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_distinction_channel_fixed_policy_result.md`
7. `docs/PUBLIC_RESULTS_INDEX.md`

Goal: understand how the formal stack, Future Field Atlas, and stochastic
channel bridge currently fit together.

### Implementation orientation

Read:

1. `docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
2. `docs/specs/current/FUTURE_FIELD_ATLAS_FORMAL_ADAPTER_CONFORMANCE_PACKAGE_SPEC.md`
3. `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_EMPIRICAL_SPEC.md`
4. `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_FIXED_POLICY_SPEC.md`
5. `formal/lean/README.md`
6. `docs/OMEGA_PROJECT_MANUAL.md`

Goal: understand what the current instruments emit, what formal artifacts are
consumable, and where active specs belong.

### Historical orientation

Read only after the current branch is clear:

1. `docs/PUBLIC_RESULTS_INDEX.md`
2. `docs/OMEGA_RUNNING_LOG.md`
3. `docs/OMEGA_PROJECT_MANUAL.md`
4. `docs/research_notes/omega_theory/historical_probe_terms.md`

Goal: understand the failed and demoted branches that led to the current instrument.

## 6. Current empirical state

The current empirical state is:

```text
Future Field Atlas:
  current empirical microscope

formal spec identity:
  required before result interpretation

artifact completeness and reconstruction audits:
  mandatory gates

product baseline:
  true product-equivalence reference for coupled scans

rank_order_boundary:
  current high-yield coupled morphology operator under symbol_histogram_distance

high-yield representatives:
  pair005, pair012, pair014, pair026

alternate observables:
  hamming_weight_or_nonzero_count and total_coordinate_mass did not reproduce
  the high-yield signature

claim boundary:
  no Omega, value, valuerhood, identity, support/capture/erasure, or
  compatibility detection
```

## 7. Current next step

The immediate next task is not holdout and not candidate promotion.

It is:

```text
bridge discipline
```

That means:

```text
formal side:
  add finite transition-system / adapter sketches only when the root-law
  obligations are explicit

empirical side:
  keep Future Field Atlas outputs reconstructible, operator-native, and
  claim-bounded

theory side:
  connect admissible observables, identity-decay nulls, maintenance gaps, and
  compatibility audits without importing valuer semantics too early
```

The focus should be:

```text
make the bridge from formal presentation to empirical adapter explicit;
avoid semantic promotion;
continue observable design before stronger substrate-general claims.
```

## 8. How to evaluate a result note

When reading a result note, look for these questions:

```text
Did all jobs complete?
Were there errors?
Did matched marginal detector-null gates pass?
Did the fixture contract pass?
Are response rows interpretable, or measurement-limited?
Are baseline-missing rows separated from real response classes?
Does the result change the instrument, the substrate family, or the broader theory?
Does the note explicitly block Omega/agency/value/candidate claims?
```

A result can be very useful while still making no Omega claim.

## 9. How an outside collaborator can help

Useful contributions include:

```text
reviewing the transition-energy formalism;
checking whether the matched null suite is strong enough;
proposing cleaner maximum-entropy transition ensembles;
reviewing matrix and spectral methodology;
stress-testing the response taxonomy;
helping design non-semantic substrate families;
improving documentation and reproducibility;
identifying hidden assumptions in E(s,t), A(s), and I(s).
```

The project especially benefits from criticism that distinguishes:

```text
instrument artifact;
substrate artifact;
real but low-level transport structure;
stronger theory-relevant structure.
```

## 10. The mantra

The working mantra is:

```text
Principled.
Parsimonious.
Predictive.
```

Principled: define objects from the substrate and controls, not from semantic labels.

Parsimonious: prefer the smallest substrate ingredients that can explain the observed response.

Predictive: every theory update should imply a concrete next run or failure mode.
