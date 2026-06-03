# Omega / Reachable Futures Lab

Omega is a research program about **value-bearing futures**.

The project asks whether ideas normally introduced late, such as value,
valuerhood, agency, identity, preference, or compatibility, can be approached
from a lower-level formal structure:

```text
relation -> distinction -> asymmetry
```

Current claim boundary:

```text
This repository does not validate Omega.
It contains formal scaffolds, worked presentations, and empirical instruments
for studying finite reachable-future structure.
```

## Current Status

The project now has two active arms.

### 1. Formal Arm

The current root formalism is **Omega Primitive Calculus v0**.

Compact Lean target:

```text
A : C -> DistTrans
```

where:

```text
C:
  relational contexts and composable unfoldings

DistTrans:
  preorder-indexed distinction transports closed under source weakening and
  target strengthening
```

The Lean sandbox currently checks:

```text
root transport laws;
recoverability weakening / strengthening;
compositional recoverability;
non-erasure monotonicity;
finite-chain recurrent recoverability;
finite maximal completion existence;
finite counterexamples for pairwise-vs-joint and greatest-vs-maximal collapse;
marginal-like non-erasure not implying strictly joint non-erasure;
adapter-failure examples for missing closure or laxity laws;
Boolean relation support presentation;
finite channel / partition presentation.
```

Key files:

```text
formal/lean/OmegaCore.lean
formal/lean/OmegaCore/DistTrans.lean
formal/lean/OmegaCore/NormalLax.lean
formal/lean/OmegaCore/Presentations/FiniteBoolean.lean
formal/lean/OmegaCore/Presentations/FiniteChannel.lean
docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md
```

The formal work is not a proof of physical or ethical claims. It is a way to
make the primitive calculus precise enough to fail, transfer, or separate cleanly.

### 2. Empirical Arm

The active empirical instrument is **Future Field Atlas**.

It scans finite transition substrates by:

```text
generating lawful state spaces and transition laws;
unfolding reachable frontiers across horizons;
recording frontier topology;
comparing product and coupled future-field baselines;
checking artifact completeness and reconstruction audits;
emitting compact morphology summaries;
compiling retained panels into formal adapter bundles for theorem-transfer
audits.
```

The current empirical pattern is narrow:

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

Current read:

```text
A and B marginal support are preserved;
joint support is restricted relative to the product baseline;
the effect persists in targeted H128 depth checks for pair012, pair014, and
pair026;
tested alternate observables did not reproduce the high-yield signature.
```

This is not an Omega result. It is a finite product-vs-coupled future-field
geometry result under declared operators and observables.

The current bridge artifact is the **formal adapter conformance package**. It
compiles the retained formal-interface panel into contexts, unfoldings,
distinction fibers, preorders, transport witnesses, closed transports, law
checks, and theorem-transfer status. The generated closed presentation passes
the checked root laws; strict raw conformance is not claimed.

A newer **stochastic distinction-channel** bridge tests the same primitive roles
in a cleaner prebiotic substrate: stochastic relation `K(y|x)`, declared finite
distinctions, named decoders, support-level exact recovery, and probabilistic
decoder success. It is a formal-consumption probe, not a validation claim.

## What This Repository Does Not Claim

This repository does not currently claim:

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

Positive empirical results should be read as instrument and
substrate-characterization results.

## Start Here

For a public overview:

1. [Omega Formalism Primer](docs/OMEGA_FORMALISM_PRIMER.md)
2. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
3. [Omega Primitive Calculus v0 Lean Root Skeleton](docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md)
4. [Omega Theory Notes Map](docs/research_notes/omega_theory/README.md)
5. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)

For the empirical branch:

1. [Future Field Atlas Instrument Spec](docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
2. [Formal Interface Distinction Panel Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_interface_distinction_panel_result.md)
3. [Rank-Order Boundary Class Expansion Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md)
4. [Rank-Order Boundary Visualization Note](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md)

For local workflow:

```text
docs/OMEGA_PROJECT_MANUAL.md
```

## Repository Map

```text
formal/lean/
  Lean proof-assistant sandbox for the root calculus and presentations

omega/future_field_atlas/
  current empirical instrument code

docs/research_notes/omega_theory/
  dense theory notes and theorem scaffolds

docs/research_notes/validation_results/
  retained empirical result notes

docs/specs/current/
  active run/spec inbox

results/
  local and retained result artifacts
```

## Project Posture

The stance is:

```text
principled;
parsimonious;
predictive / revelatory;
skeptically open.
```

The goal is not to protect a theory. The goal is to build formal objects and
empirical instruments strong enough that weak formulations can fail.
