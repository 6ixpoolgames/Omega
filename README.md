# Omega / Reachable Futures Lab

This repository is the working lab for the **Omega / Reachable Futures**
research project.

Omega is an attempt to formalize **value-bearing futures** without starting
from reward, utility, moral rules, fixed agent boundaries, fixed selves, or
privileged valuers.

The project is ambitious, but the current claim is deliberately modest:

```text
We are building formal scaffolds and empirical instruments for finite
future-field dynamics. We are not claiming Omega validation.
```

## Start Here

For the current project state, read:

1. [Omega Formalism Primer](docs/OMEGA_FORMALISM_PRIMER.md)
2. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
3. [Omega Primitive Calculus v0 Lean Root Skeleton](docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md)
4. [Omega Formal Core v0.2](docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md)
5. [Theory Arm Map v0](docs/research_notes/omega_theory/theory_arm_map_v0.md)
6. [Omega Theory Notes Map](docs/research_notes/omega_theory/README.md)
7. [Future Field Atlas Instrument Spec](docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
8. [Formal Interface Distinction Panel Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_interface_distinction_panel_result.md)
9. [Rank-Order Boundary Class Expansion Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md)
10. [Rank-Order Boundary Visualization Note](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md)
11. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)
12. [Project Manual](docs/OMEGA_PROJECT_MANUAL.md)

## The Core Idea

The current root formalism is **Omega Primitive Calculus v0**.

Its support-level grammar is:

```text
relation -> distinction -> asymmetry
```

Where:

```text
relation:
  composable consequential connectedness

distinction:
  preordered non-equivalence structure; differences capable of preservation,
  transformation, collapse, or recovery

asymmetry:
  normal lax distinction transport along relation
```

Compact root object:

```text
A : C -> DistTrans
```

where `C` is a category of relational contexts and `DistTrans` is the
support-level category of preorder-indexed distinction transports.

Future-Distinction Dynamics is the current working presentation of that root
calculus for reachable-futures modeling.

Compact working target:

```text
Omega is the admissible subset of future-field dynamics for which
future-relevant distinctions persist to terminus in a recoverable, non-erasing,
and compatible manner.
```

The current completion-layer target is:

```text
Omega is the space of maximal admissible compatibility completions in which
proto-valuer-bearing dynamics propagate recoverably and non-erasingly without
systematic irreversible destruction of one another's distinction-content.
```

This is the target formal object, not an empirical result.

## Why This Is Not Utility or Reward

Omega is not defined as:

```text
maximizing reward;
maximizing utility;
maximizing entropy;
preserving a fixed agent;
preserving a fixed self;
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
Can process-like structures maintain distinction-content through churn better
than matched identity-decay nulls?
Can such structures compose into maximal compatibility completions?
```

## Formal Stack

The active theory arm is layered:

```text
Layer 0: Omega Primitive Calculus v0
  relation, distinction, asymmetry, recoverability, recurrent recoverability,
  non-erasure, compatibility, completion

Layer 0a: Future-Distinction Dynamics
  relation, distinction, asymmetry, dynamics, recoverability, non-erasure,
  compatibility

Layer 1: Admissibility and Identity-Decay Nulls
  process-bundle designations, activity channels, matched nulls, maintenance
  gaps

Layer 2: Proto-Valuer Ladder
  pre-proto-valuers, proto-valuers, induced asymmetry-preferences,
  compatibility-audited valuers

Layer 3: Completion Layer
  Omega as maximal admissible compatibility completions of proto-valuer-bearing
  dynamics

Layer 4: Finite Theorem Scaffolds
  small finite proofs and witnesses showing that the ladder properties do not
  collapse into one another

Layer 5: Empirical Interface Targets
  finite distinction measures, null manifests, maintenance-gap rows,
  self-conditioning rows, compatibility-audit rows
```

Finite scaffolds currently establish:

```text
finite maximal admissible completions exist when the admissible family is
nonempty, including a Lean-checked Finset/Fintype specialization;

a greatest completion need not exist, now checked as a finite Lean
counterexample;

pairwise admissibility does not imply joint admissibility, now checked as a
finite Lean counterexample;

marginal-like non-erasure does not imply strictly joint non-erasure, now checked
as a finite Lean distinction-transport counterexample;

finite completions are computable by exhaustive enumeration in principle.
```

These are mathematical scaffolds, not physical-world validation.

The current Lean formalization checks the support-level root skeleton:

```text
formal/lean/OmegaCore/DistTrans.lean
formal/lean/OmegaCore/NormalLax.lean
formal/lean/OmegaCore/Recurrent.lean
formal/lean/OmegaCore/Completion.lean
formal/lean/OmegaCore/Counterexamples.lean
formal/lean/OmegaCore/MarginalJoint.lean
formal/lean/OmegaCore/AdapterFailures.lean
formal/lean/OmegaCore/Presentations/FiniteBoolean.lean
formal/lean/OmegaCore/Presentations/FiniteChannel.lean
```

Checked results include DistTrans closure, relation-level identity and
associativity laws, recoverability weakening/strengthening, compositional
recoverability from laxity, non-erasure monotonicity, finite-chain recurrent
recoverability, finite-enumeration maximal completion existence, and
Finset/Fintype maximal completion existence. The finite counterexample layer
also checks that pairwise admissibility does not imply joint admissibility,
maximal admissible completions need not be unique, and a greatest admissible
completion need not exist. The marginal/joint counterexample layer checks that
preserving each component-like distinction does not force preservation of a
strictly joint distinction. The adapter-failure layer checks that theorem
transfer fails without source-weakening closure, target-strengthening closure,
or lax composition inclusion. The first worked presentation layer checks that
Boolean relation support recovery induces valid distinction transports and
composes across changed carrier types. The finite channel presentation checks
exact decoder recovery over observable partitions, including identity-channel
refinement, channel composition, changed-carrier recovery, and constant-channel
erasure.

## Empirical Arm: Future Field Atlas

The active empirical instrument is **Future Field Atlas**.

It scans finite transition substrates by:

```text
generating lawful state spaces and transition laws;
unfolding reachable frontiers across horizons;
recording raw or retained frontier topology;
comparing product and coupled future-field baselines;
checking artifact completeness and reconstruction audits;
emitting compact morphology summaries;
leaving interpretation downstream.
```

The instrument is designed to prevent premature semantic promotion. It does not
start with labels like agent, valuer, support, capture, erasure, or value.

## Current Empirical Result

The current positive empirical pattern is narrow:

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

Observed compact topology:

```text
A and B marginal support are preserved;
joint support is restricted relative to the product baseline;
the effect persists in targeted H128 depth checks for pair012, pair014, and
pair026;
typical controls remain low-residual and high-retention.
```

The two tested alternate observables did not reproduce the high-yield
signature:

```text
hamming_weight_or_nonzero_count
total_coordinate_mass
```

This is not an Omega result. It is product-vs-coupled future-field geometry
under a formal operator.

## What Is Not Claimed

This repository does **not** currently claim:

```text
Omega validation;
proto-valuer detection;
valuer detection;
agent detection;
identity detection;
value detection;
compatibility detection;
support / capture / erasure detection;
life detection;
self-replication detection;
holdout readiness;
substrate-general theory validation.
```

Positive results should be read as instrument and substrate-characterization
results.

## Current Next Step

The latest empirical step completed the compact representative-control
formal-interface panel.

It emits declared finite distinction-measure artifacts over:

```text
high-yield representatives:
  pair005
  pair012
  pair014
  pair026

controls:
  low/medium residual pairs
  product selector
  zero-penalty joint rank-prefix
  scalar mismatch 0.020
  shared_capacity v1 reference
```

The panel has 40 / 40 requested cells available, 0 missing or blocked cells, and
separates the four high-yield representatives from the low/medium controls under
the declared rank_order_boundary joint-vs-marginal finite measure.

The current formal next step is to add nontrivial finite examples, failed
adapter examples, and a tighter bridge from the Lean root skeleton into
admissible process-bundle, identity-decay-null, maintenance-gap,
self-conditioning, and compatibility-audit instrumentation.

## Repository Map

```text
README.md
  public pitch and current state

docs/OMEGA_FORMALISM_PRIMER.md
  readable bridge to the current formal stack

docs/EXTERNAL_READER_GUIDE.md
  longer collaborator onboarding guide

docs/OMEGA_PROJECT_MANUAL.md
  operational workflow, local commands, run retention, repo process

formal/lean/
  Lean proof-assistant sandbox for the root formal skeleton

docs/PUBLIC_RESULTS_INDEX.md
  empirical result index

docs/OMEGA_RUNNING_LOG.md
  chronological project log

docs/research_notes/omega_theory/
  dense theory notes and finite theorem scaffolds

docs/research_notes/omega_theory/README.md
  status map for dense theory notes

docs/research_notes/validation_results/
  retained empirical result notes

omega/future_field_atlas/
  current empirical instrument code
```

## Project Posture

The stance is:

```text
principled;
parsimonious;
predictive / revelatory;
skeptically open.
```

The goal is not to protect a theory. The goal is to build a formal object and
an empirical instrument strong enough that weak formulations can fail.
