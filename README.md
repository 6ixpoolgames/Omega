# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega / Reachable Futures** theory project.

The project studies **reachable futures**: how neutral finite transition systems shape which futures remain reachable, excluded, concentrated, transformed, control-equivalent, measurement-limited, recoverable, or composable.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, moral rules, or privileged agent/valuer boundaries. The executable work in this repo is narrower and earlier-stage: building instruments and minimal substrates where fragments of that idea can become mathematically testable.

This repository does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## Start here

If you are new to the project, start with:

1. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
2. [Omega Formal Core v0](docs/research_notes/omega_theory/omega_formal_core_v0.md)
3. [Future Field Atlas Instrument Spec](docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
4. [Hard top-m mechanism result](docs/research_notes/validation_results/rfs_mb0_top_m_mechanism_audit_result.md)
5. [Top-m geometry audit result](docs/research_notes/validation_results/rfs_mb0_top_m_geometry_audit_result.md)
6. [MaxEnt local transition Phase 1 preflight result](docs/research_notes/validation_results/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md)
7. [Low-beta preservation sensitivity scaleup result](docs/research_notes/validation_results/rfs_mb0_low_beta_preservation_sensitivity_scaleup_result.md)
8. [Asymmetry-ladder preservation scaleup result](docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md)
9. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)

The external reader guide gives a short, current, claim-bounded overview of the project and the best reading paths for technical readers, implementation reviewers, and historical context.

## Current status in one paragraph

VAL0/VAL1 were useful reconnaissance probes. RFS-MB0 then reoriented from endpoint support/distribution deformation and static coflow spectra toward directional **horizon-transport** instrumentation. The H128 response-surface scaleup passed matched-marginal instrument gates and surfaced a stable-to-amplified-aligned response surface. Transition-energy characterization turned the branch into a substrate-response atlas. Preservation asymmetry, especially `symbol_histogram_distance`, became the strongest non-template substrate hook; MaxEnt and top-m audits then narrowed the read. The latest hard-top-m mechanism pass found a fixed low-rank-core boundary: baseline `m=3`, `m=4` with one weakest edge removed, and `m=5` with two weakest edges removed were response-bearing, while expansion, random deletion, and strongest-edge deletion stayed stable. This closes the old single-frontier mechanism branch as substrate anatomy. The current branch is now **Future Field Atlas**, a pre-scientific instrumentation reset: build an atlas instrument that scans lawful frontier evolution, preserves raw topology, maps features, and defers labels/interpretation to downstream analysis. This is still not a scientific validation gate, candidate promotion, holdout result, or Omega/agency/value claim.

## Current formal core

The current definitional anchor is:

```text
Omega is the boundary-nonprivileged compatibility structure of futures that
support recoverable, non-erasing propagation of value-bearing substrates.
```

In this usage, a value-bearing substrate is not an ontologically privileged agent, self, object, or valuer. It is:

```text
an admissibly designated process-bundle supporting recoverable, non-erasing,
viable propagation of future-relevant distinctions.
```

This formal core records what the empirical arm has forced the theory not to say:

```text
not raw entropy;
not survival alone;
not static reachability;
not COM as a universal quotient;
not an agent/valuer/identity-first ontology;
not a scalar before tuple anatomy;
not local persistence that degrades broader future-bearing structure.
```

The empirical branch therefore measures future-field deformation first, then asks whether any boundary, quotient, process-bundle, or value-bearing designation is earned under predictive, transport, recoverability, non-erasure, compatibility, and matched-control audits. See [Omega Formal Core v0](docs/research_notes/omega_theory/omega_formal_core_v0.md).

## Current instrument reset: Future Field Atlas

The live implementation target is no longer a broader response-classification sweep. It is a clean instrument build:

```text
Future Field Atlas:
  scanner first;
  mapper second;
  analyzer third;
  labels last.
```

Spec:

- [Future Field Atlas Instrument Spec](docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)

Branch:

```text
instrument/future-field-atlas
```

Target package / runner:

```text
omega.future_field_atlas
omega.future_field_atlas.run_future_field_atlas
```

Purpose:

```text
Build a clean future-field atlas instrument that scans lawful frontier evolution,
preserves raw topology, maps features, and defers labeling/interpretation to
downstream analysis.
```

This is a **pre-scientific instrument build**, not a result branch. The first milestone is to recover the known fixed top-3 low-rank successor-core boundary pattern from raw topology, without relying on response-class labels as primary evidence.

## Why the instrumentation reset exists

The old horizon-transport runner was useful. It produced transport matrices, SVD summaries, matched-null audits, response classifications, and aggregate tables. It established a working measurement discipline and narrowed the substrate anatomy.

But its workflow is still response-classifier-first:

```text
generate substrate;
build selected horizon-pair transport matrices;
compute summaries;
classify response;
aggregate labels.
```

Future Field Atlas uses a topology-first workflow:

```text
generate lawful substrate;
scan frontier evolution;
preserve topology;
map raw features;
analyze downstream;
label last, if useful.
```

This matters because the project's object is futures: their topology, dynamics, lush reachability, deformation, composability, recoverability, and interaction. Coupled frontier work should not begin from labels such as `transport_amplified_aligned`. It should begin from raw frontier geometry and joint/product deformation fields.

## Legacy live object: horizon transport

Horizon transport asks what earlier reachable-future structures become at later horizons:

```text
T_{H_a -> H_b}
```

This is a directional matrix family measured with SVD and matched controls. It is not a static co-occurrence object.

The H128 response-surface run reported:

```text
jobs_completed: 11520 / 11520
errors: 0
matrix_count: 660
null_replicates: 15
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
terminal_saturation_flagged_rows: 0 / 660
```

Empirical response classes in that run:

```text
transport_stable: 235
transport_amplified_aligned: 381
```

This established horizon transport as a useful legacy instrument, not as Omega validation. Future Field Atlas should preserve compatibility with horizon-transport views as derived artifacts, while making raw frontier topology primary.

## Key concept: transition energy

The current substrate program uses explicit transition energy:

```text
E(s,t)
```

`E(s,t)` is an edge-selection score over possible transformations. It is not moral cost, thermodynamic energy, utility, value, reward, fitness, or Omega.

The minimal ladder is:

```text
E0 locality only:
  E(s,t) = d(s,t) + roughness

E1 directional asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + roughness

E2 preservation asymmetry:
  E(s,t) = d(s,t) + beta * |I(t)-I(s)| + roughness

E3 combined:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + beta * |I(t)-I(s)| + roughness
```

`A(s)` is a directional asymmetry field. `I(s)` is a macro-invariant / coarse asymmetry coordinate.

## Current substrate-anatomy result

The preservation-focused asymmetry-ladder and low-beta passes strengthened the preservation-asymmetry read. The cleanest target was:

```text
symbol_histogram_distance
```

MaxEnt and top-m audits then narrowed the mechanism:

```text
MaxEnt macro-marginal:
  did not recover the response

softmax / Gibbs:
  did not recover the response

rank-conditioned local sampling:
  did not recover the response

hard-top-m mechanism boundary-resolution sweep:
  baseline m=3, m=4 with one weakest edge removed, and m=5 with two weakest
  edges removed were response-bearing;
  expansion, random deletion, and strongest-edge deletion stayed stable
```

Current substrate-anatomy read:

```text
fixed low-rank successor-core / core-fringe boundary pressure
```

This is a coupling primitive candidate for later coupled frontier scanning. It is not Omega, value, agency, or validation.

## What current results do and do not mean

Current results mean:

```text
horizon transport was a useful legacy instrument;
matched marginal nulls did not explain away the H128 response surface;
perturbation changed future transport geometry without simply destroying it;
horizon depth appears loadbearing in the response profile;
transition-energy substrate laws express different response regimes;
preservation asymmetry became the strongest non-template substrate hook;
MaxEnt/top-m audits narrowed the mechanism to fixed low-rank successor-core boundary pressure;
Omega Formal Core v0 is the current definitional anchor;
Future Field Atlas is the current implementation branch for a raw-topology-first instrument reset.
```

Current results do **not** mean:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
life detected;
self-replication detected;
candidate promoted;
holdout ready;
graph-channel causality shown;
value-bearing structure demonstrated.
```

## Control philosophy

A key reorientation in the project is the separation between detector-null controls and perturbation-response profiles.

```text
Null controls test the detector.
Perturbations test the candidate response profile.
Destructive ablation maps viability boundaries; it is not ordinary negative evidence.
```

Future Field Atlas keeps this discipline but moves the primary evidence back to raw topology:

```text
scanner:
  saves frontier geometry

mapper:
  computes raw topology and deformation features

analyzer:
  compares baselines, perturbations, product controls, and coupled runs

labeler:
  optional downstream convenience layer only
```

Labels must be reconstructible from raw columns and must not drive artifact retention.

## How to read the project

### Quick orientation

Read:

1. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
2. [Omega Formal Core v0](docs/research_notes/omega_theory/omega_formal_core_v0.md)
3. [Future Field Atlas Instrument Spec](docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
4. [Hard top-m mechanism result](docs/research_notes/validation_results/rfs_mb0_top_m_mechanism_audit_result.md)
5. [Top-m geometry audit result](docs/research_notes/validation_results/rfs_mb0_top_m_geometry_audit_result.md)
6. [MaxEnt local transition Phase 1 preflight result](docs/research_notes/validation_results/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md)
7. [Low-beta preservation sensitivity scaleup result](docs/research_notes/validation_results/rfs_mb0_low_beta_preservation_sensitivity_scaleup_result.md)
8. [Asymmetry-ladder preservation scaleup result](docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md)

### Theory orientation

Read:

1. [Omega Formal Core v0](docs/research_notes/omega_theory/omega_formal_core_v0.md)
2. [Horizon Transport and Aligned Amplification](docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md)
3. [Transition Energy and Constraint Untethering](docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md)
4. [Transition-Energy Substrate Atlas](docs/research_notes/omega_theory/transition_energy_substrate_atlas.md)
5. [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
6. [Boundary non-privileging and field-deformation theory note](docs/research_notes/omega_theory/boundary_nonprivileging_and_field_deformation.md)

### Implementation orientation

Read:

1. [Future Field Atlas Instrument Spec](docs/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
2. [Top-m mechanism audit spec](docs/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md)
3. [Top-m geometry audit spec](docs/RFS_MB0_TOP_M_GEOMETRY_AUDIT_SPEC.md)
4. [Max-entropy local transition preflight spec](docs/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md)
5. [Asymmetry-ladder transition-energy spec](docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md)
6. [Horizon-transport runner map](docs/implementation/horizon_transport_runner_map.md)
7. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)

### Historical orientation

Read:

1. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
4. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)

## Current next step

The current next step is **not** holdout, graph perturbation, direct channel diagnostics, coupled-frontier science, or candidate promotion.

The current next step is:

```text
Future Field Atlas instrument build
```

Near-term implementation target:

```text
Phase 0:
  single-frontier scanner smoke

Phase 1:
  known-mechanism recovery from raw topology
  target: retained top-3 low-rank successor-core boundary pressure

Phase 2:
  coupled future-field scan only after Phase 0/1 pass
```

Still blocked:

```text
holdout scoring;
n=6 transfer;
alphabet expansion as promotion;
graph-channel causal claims;
agent/value/Omega labels;
coupled-frontier interpretation before the atlas scanner works.
```

## Why this matters for alignment

Omega is motivated by a central alignment problem:

> A system can become highly capable, persistent, and effective while degrading the broader conditions under which value-bearing futures remain possible.

In public-facing terms, this is a locally viable / globally degrading capture regime or destructive lock-in: local success that collapses broader future possibility.

The current empirical program does not validate alignment. It asks what substrate and measurement discipline are needed before the earliest precursor can be resolved:

> Can future-landscape deformation be measured well enough to distinguish nontrivial future-structuring effects from saturation, trivial persistence, clocks, collapse, probe artifacts, generic finite-frontier dynamics, and matched-control equivalence?

Future Field Atlas is the next measurement-discipline step: it builds a topology-first instrument so that later coupled future-field scans can analyze composability, recovery, capture, erasure, and support from raw geometry rather than response labels.

## Workflow

This repository is developed through a human-directed, AI-assisted research workflow.

The core theoretical motivation, project judgment, branch selection, interpretive standards, and many key pivots are human-generated. AI systems are used as implementation and critique accelerators: they draft specs, modify runners, generate reports, audit code, summarize results, and propose follow-up experiments.

## Roadmap

```text
VAL0/VAL1:
  historical reconnaissance; useful but not the active empirical frame

RFS0:
  exact finite reachability measurement-floor smoke; insufficient control separation

RFS-MB0 / horizon-transport lineage:
  neutral future-landscape deformation program;
  endpoint support/distribution and quotient probes became measurement-limited;
  frontier-transform instrumentation matured into horizon-transport instrumentation;
  transition-energy families replaced hand-built symbolic laws;
  MaxEnt/top-m audits narrowed preservation response to fixed low-rank successor-core boundary pressure

Future Field Atlas:
  current pre-scientific instrument build;
  scanner-first / mapper-second / label-last workflow;
  Phase 0/1 recovers known low-rank-core boundary signal from raw topology;
  Phase 2 later enables coupled future-field scans

Coupled future-field scans:
  only after atlas Phase 0/1 passes;
  compatibility, capture, erasure, support, and recovery features from raw topology

Scale hierarchy / constructor-like branches:
  only after earlier substrate and measurement layers mature enough to justify revisiting them
```

## Important caveat

The current scientific claim is modest:

> Directional horizon-transport instrumentation can measure a matched-marginal-separated response surface in neutral toy substrates. Transition-energy substrate characterization shows that different generic substrate laws express different response regimes. Preservation asymmetry narrowed to fixed low-rank successor-core boundary pressure in the current substrate anatomy. Omega Formal Core v0 is the current definitional anchor, but Omega-compatible subobjects have not been demonstrated. Future Field Atlas is an instrument build, not a validation result.
