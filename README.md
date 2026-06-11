# Omega / Reachable Futures Lab

[![Lean AlphaOmega](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml/badge.svg?branch=master)](https://github.com/6ixpoolgames/Omega/actions/workflows/lean-alphaomega.yml)

Omega is a research program about **consequence-bearing continuation** and its
downstream relation to value-bearing futures.

The working north star is:

```text
Alpha and Omega are two faces of one object.

Alpha names the primitive grammar by which differences can become
consequence-bearing.

Omega names the possible maximal compatible unfolding of consequence-bearing
structure across admissible continuations.
```

In this framing, "future" is the temporal adapter of a broader notion:
continuation. A continuation may be a transition, derivation, completion,
composition, deformation, path, or other admissible unfolding supplied by a
substrate.

Value enters downstream. Value is not a property of arbitrary states; it
requires valuers. Valuers require robust, recoverable, continuation-bearing
trajectories. The formal lower stack asks what must already be true before such
trajectories can become legible.

Current claim boundary:

```text
This repository does not validate Omega.
It does not detect valuers, value, agency, identity, or compatibility.
It contains formal scaffolds, checked finite presentations, and empirical
instruments for studying recoverability, provenance, and finite future
structure.
```

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).

## Mission and Vision

Most alignment and value theories start with agents, preferences, rewards,
selves, or moral objects already on the table. Omega tries to start earlier
without pretending that the lower level is already value.

The current ladder is:

```text
Alpha:
  primitive grammar: relation, distinction, asymmetry

AlphaCalculus:
  recoverability, transport, recurrence, non-erasure, separation, and
  composition laws

Consequence / continuation layer:
  consequence-induced separation, forbidden identification, collapse and
  over-separation guardrails, and continuation-native trajectory scaffolds

AlphaAdapters:
  finite presentations and empirical bridges that expose what a substrate does
  or does not provide

Trajectory / viability layer:
  process-bundles, actions, perturbations, persistence, robustness, and
  compatible continuation

Omega:
  possible maximal compatible development of consequence-bearing continuation,
  with valuer-bearing futures as a downstream value-capable manifestation
```

The central correction is now:

```text
Continuation, not time, is primitive.
A difference matters when erasing it changes what can follow.
Mattering precedes value.
Value enters only when consequence-bearing structures support valuers.
```

Distinction persistence is therefore a necessary substrate condition, not value
itself. The lower object is consequence-bearing difference; the downstream value
object is a robust valuer-bearing trajectory under compatibility and viability
constraints.

## Current Status

The project currently has three active layers.

### 1. Formal Arm

The primitive floor is **Alpha Primitive Core v0**: relation, distinction, and
asymmetry.

`AlphaOmega` is the active Lean umbrella for the project stack.
`AlphaCore`, `AlphaCalculus`, `AlphaAdapters`, and `Omega` are the public layer
names. `ProtoOmega`, `OmegaAdapters`, and `OmegaProper` remain compatibility
implementation namespaces during migration. `OmegaCore` remains checked
provenance from the earlier root-calculus pass.

The Lean sandbox currently checks:

```text
Alpha primitive frame over relation, distinction, and asymmetry;
Alpha reachability and finite separation examples;
primitive non-collapse examples;
primitive nondegeneracy witnesses blocking total relation and identification
collapse;
primitive-preserving maps between Alpha frames, including identity,
composition, witness preservation, and no-map-to-collapse guardrails;
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
finite channel / partition presentation;
probabilistic channel presentation, including exact/probabilistic separation,
full-support converse, finite cascade error bound, fixed-declared versus
Bayes-best policy separation, and thresholded probabilistic non-erasure;
consequence-native guardrails separating directional allowance from symmetric
identification and blocking invalid class formation;
Alpha-to-consequence seed bridge showing that evaluated consequence refusal
over primitive witness endpoints blocks symmetric consequence identification;
proto-teleological seed wrappers showing that primitive Alpha contact plus
evaluated consequence merge-separation implies primitive nondegeneracy,
consequence noncollapse, and a witness blocking symmetric consequence
identification, while primitive nondegeneracy alone and consequence
noncollapse alone are not sufficient;
speculative deformation-profile bridge comparing exact merge-block and
merge-allow profiles between consequence systems over the same Alpha carrier,
without defining identity or recoverability;
profile-abstraction contracts separating coarse allow/block claims from exact
profiles via explicit soundness and completeness predicates;
proto-teleological profile bridge showing that a proto seed supplies a
nonempty exact merge-block profile and defeats universal-allow abstraction
soundness.
```

Key files:

```text
formal/lean/AlphaOmega.lean
formal/lean/AlphaCore.lean
formal/lean/AlphaCalculus.lean
formal/lean/AlphaAdapters.lean
formal/lean/Omega.lean
formal/lean/OmegaCore.lean
docs/research_notes/omega_theory/alpha_primitive_core_v0.md
docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md
docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md
```

The formal work is not a proof of physical or ethical claims. It is a way to
make assumptions, theorem transfer, and failure modes explicit.

### 2. Registry-First Stochastic Channel Arm

The cleanest current empirical-formal bridge is the registry-first stochastic
channel branch.

It uses finite carriers and exact natural-weight channels to separate:

```text
declared registry recovery:
  a predeclared decoder registry works

existence / capacity recovery:
  some exact decoder exists, whether or not it was declared

optimized diagnostic recovery:
  a best available target/decoder choice succeeds after search
```

This branch is designed to block a self-validating shortcut:

```text
some decoder exists = the declared instrument recovered the distinction
```

The current shared engine is:

```text
omega/stochastic_distinction_channel/registry_first_engine.py
```

X2 and X3 are now thin configs over that engine:

```text
omega/stochastic_distinction_channel/registry_first_probe.py
omega/stochastic_distinction_channel/registry_first_x3_probe.py
```

Current retained result:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_x3_v0/
docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_x3_result.md
```

Current read:

```text
carrier_id: X3
state_count: 8
channel_count: 15
registered_rows: 120
provenance_gap_rows: 120
adversarial_audit: PASS
```

The result is a finite presentation/provenance result. It is not value or
valuer detection.

### 3. Future Field Atlas

Future Field Atlas is retained, but it is now demoted to:

```text
Future Field Atlas v0:
  preformal reachable-frontier morphology instrument
```

FFA scans finite transition substrates by unfolding reachable frontiers,
recording topology, comparing product and coupled baselines, checking artifact
completeness, and emitting morphology summaries.

That remains useful as finite-dynamics stress testing. It should not be treated
as the central empirical object for Omega.

The next empirical target should be trajectory-level:

```text
process-bundles
action channels
viability constraints
perturbation regimes
robust continuation
correction channels
compatibility audits
irreversible process loss
```

FFA features can become subordinate diagnostics inside such a trajectory atlas,
but frontier morphology alone is not valuerhood.

## Current Reorientation

Two current roadmap notes define the revised target:

```text
docs/VALUER_FORMAL_TARGET_V0.md
docs/OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md
```

The compact target is:

```text
robust recoverable persistence of future-bearing agency under compatibility
constraints
```

The next formal work should define finite scaffolds for:

```text
trajectory families
process-bundle persistence predicates
action-channel counterfactuality
viability predicates
compatibility predicates
maximal admissible trajectory families
irreversible loss examples
pairwise-vs-joint compatibility failures
singleton-control counterexamples
```

Only after that should the empirical branch build a trajectory-level atlas.

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

Positive empirical results should be read as formal, instrumental, or
substrate-characterization results.

## Start Here

For the current public orientation:

1. [Valuer Formal Target v0](docs/VALUER_FORMAL_TARGET_V0.md)
2. [Omega as Compatible Valuer-Trajectory Space v0](docs/OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md)
3. [Omega Formalism Primer](docs/OMEGA_FORMALISM_PRIMER.md)
4. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
5. [Omega Theory Notes Map](docs/research_notes/omega_theory/README.md)

For checked formal work:

1. [Alpha Primitive Core v0](docs/research_notes/omega_theory/alpha_primitive_core_v0.md)
2. [Omega Primitive Calculus v0 Lean Root Skeleton](docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md)
3. [Probabilistic Channel Presentation v0](docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md)

For empirical results:

1. [Stochastic Registry-First Probe X3 Result](docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_x3_result.md)
2. [Stochastic Registry-First Probe Medium Result](docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_medium_result.md)
3. [Future Field Atlas Instrument Spec](docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
4. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)

For local workflow:

```text
docs/OMEGA_PROJECT_MANUAL.md
```

For external validation:

```text
docs/VALIDATION.md
docs/BASELINE_WITNESS_SMOKE.md
docs/REPRODUCIBILITY_SMOKE.md
docs/CLAIMS_LEDGER.md
docs/KNOWN_REDUCTIONS_AND_BASELINES.md
```

## Repository Map

```text
formal/lean/
  Lean proof-assistant sandbox for Alpha, formal presentations, and adapters

omega/stochastic_distinction_channel/
  registry-first stochastic-channel probes and theorem-transfer audit machinery

omega/future_field_atlas/
  finite reachable-frontier morphology instrument

docs/research_notes/omega_theory/
  dense theory notes and theorem scaffolds

docs/research_notes/validation_results/
  retained empirical result notes

docs/specs/current/
  active run/spec inbox

results/
  local and retained result artifacts
```
