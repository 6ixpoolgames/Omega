# Omega / Reachable Futures Lab

This repository is the working lab for the **Omega / Reachable Futures** research project.

The current active program is **Future Field Atlas**: a topology-first instrument for scanning finite future fields under lawful transformations. It records raw reachable-frontier structure, preserves formal condition identity, checks reconstruction audits, and only then supports downstream interpretation.

The long-term Omega ambition is broader: a substrate-neutral account of value-bearing futures and alignment-relevant failure modes that does not begin from rewards, utility functions, moral rules, fixed agent boundaries, or privileged valuers.

This repository does **not** prove Omega. It builds instruments and formal objects that let weak formulations fail.

## Start here

For the current project state, read these first:

1. [External Reader Guide](docs/EXTERNAL_READER_GUIDE.md)
2. [Omega Formal Core v0.2: Future-Distinction Dynamics](docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md)
3. [Future Field Atlas Instrument Spec](docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
4. [Future Field Atlas Glossary](docs/FUTURE_FIELD_ATLAS_GLOSSARY.md)
5. [Substrate Morphology Atlas Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md)
6. [Shared-Capacity H64 Smoke Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md)
7. [Coupled H64 Mechanism-Resolution Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_mechanism_resolution_result.md)
8. [Coupled H64 Ladder Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_ladder_result.md)
9. [Coupled H64 Broad Sweep Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_broad_sweep_result.md)
10. [Coupled Worker-Spool Scale Validation](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_worker_spool_scale_validation_result.md)
11. [Coupled H128 Depth and Triadic Profile Smoke](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h128_and_triadic_profile_smoke_result.md)
12. [Future Field Atlas H128 Calibration Pass](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_h128_calibration_pass_result.md)
13. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)

Historical RFS-MB0 results are still retained, but they are now background. Future Field Atlas is the fresh active frame.

## Current status

The live empirical object is **not** the old response-classifier runner. It is:

```text
Future Field Atlas:
  formal spec identity;
  raw reachable-frontier topology;
  product and coupled future-field baselines;
  artifact completeness semantics;
  reconstruction audits;
  compact retention summaries;
  labels last, if at all.
```

The single-field atlas has passed H128 calibration with complete artifacts and reconstruction audits. The coupled atlas has passed small hardening runs, an H64 pair8 breadth sweep, selected H128 depth checks, and a first H64 coupling-strength ladder.

The coupled H64 ladder first found threshold-like behavior in the current rank-boundary mismatch operator:

```text
0.00 differs from positive penalty;
0.05, 0.10, 0.25, and 0.50 are topology-identical at this resolution;
positive penalty preserves A/B marginal reachability in the primary readout;
pair005 is anomalous and becomes much more joint-restrictive at H64.
```

The follow-up mechanism-resolution pass refined that read:

```text
0.001 differs from 0.000;
0.001, 0.002, 0.005, and 0.010 are distinct in compact topology digests;
0.020 and 0.050 saturate to the same compact topology digest;
true product selection differs from zero-penalty joint rank-prefix selection;
pair005 remains a heavy-pair / critical-pair clue and persists in targeted H128.
```

The first substrate morphology atlas now maps the retained coupled outputs
directly instead of treating any single operator ladder as the whole object:

```text
26 retained coupled run directories and 2 compact summary directories ingested;
all 26 coupled inputs passed clean gates;
pair005 remains the only high-residual / joint-restrictive exemplar in the retained set;
observable coverage is still single-observable only: symbol_histogram_distance.
```

The first shared-capacity H64 smoke completed cleanly, but it did **not** earn
scale-up as a mechanism branch:

```text
shared_capacity v1:
  operational in the coupled atlas;
  no caps, complete artifacts, reconstruction audits PASS;
  prunes A/B marginal support and then becomes product-dense over surviving marginals.

desired pair005-like scalar-mismatch signature:
  preserved A/B marginals;
  restricted joint combinations.
```

This is not an Omega result. It is a clean product-vs-coupled future-field geometry result under a formal operator.

## Current formal core

The current theory-arm draft is [Omega Formal Core v0.2: Future-Distinction Dynamics](docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md).

The compact working definition is:

```text
Omega is the admissible subset of future-field dynamics for which
future-relevant distinctions persist to terminus in a recoverable, non-erasing,
and compatible manner.
```

The cleaned ontology is:

```text
relation:
  the substrate condition; what can follow what

distinction:
  the future-bearing content; what differences can matter across futures

asymmetry:
  the channeling law; how futures are non-neutrally ordered

dynamics:
  the iterated unfolding of future-distinctions through relations under asymmetry

recoverability:
  operational identity of distinction-patterns without privileged self-boundaries

non-erasure:
  the target property that prevents fake success by survival, entropy, collapse,
  or local persistence

compatibility:
  composition without trivial capture, erasure, or collapse of other future-
  bearing structure
```

The strongest clean statement currently allowed is:

```text
Wherever value-bearing structure exists, its substrate-general form must involve
recoverable, non-erasing, compatible propagation of future-relevant distinctions.
```

That is a theory-arm conjectural bridge, not an empirical result.

## Future Field Atlas

Future Field Atlas replaces the older classifier-first posture with a scanner-first posture:

```text
old posture:
  generate substrate;
  build selected horizon-pair matrices;
  classify response;
  aggregate labels.

new posture:
  generate lawful substrate;
  scan frontier evolution;
  preserve topology;
  map raw features;
  audit reconstruction;
  analyze downstream;
  label last, if useful.
```

Current package targets:

```text
omega.future_field_atlas
omega.future_field_atlas.run_future_field_atlas
omega.future_field_atlas.run_coupled_future_field_atlas
```

Core formal identities:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
FrontierScanSpec
CoupledOperatorSpec
```

Current instrument discipline:

```text
historical treatment names are glossary-only;
runtime conditions are spec/operator based;
raw topology is primary;
derived summaries must reconstruct from raw rows and manifests;
truncated topology is non-interpretable;
marginal projection deltas are non-causal;
product-vs-coupled residuals are geometry, not interaction claims.
```

## What current results do and do not mean

Current results mean:

```text
Future Field Atlas can scan finite future-field topology with formal condition identity;
raw frontier artifacts and compact summaries can be reconstructed and audited;
single-field H128 calibration is complete and reconstruction-passing;
coupled H64 pair8 breadth is operationally manageable with sharded/compact output;
coupled H64 ladder shows threshold-like zero-vs-positive rank-boundary mismatch geometry;
near-zero mechanism resolution shows scalar mismatch effects through 0.010 and saturation by 0.020;
zero-penalty joint rank-prefix selection is not product-equivalent;
pair-level heterogeneity matters, especially pair005.
substrate morphology is now summarized across retained coupled outputs before
choosing the next operator.
shared_capacity v1 is operational but currently behaves as marginal pruning,
not as marginal-preserving joint restriction.
```

Current results do **not** mean:

```text
Omega detected;
agent detected;
identity detected;
valuer detected;
value detected;
life detected;
self-replication detected;
compatibility detected;
support/capture/erasure demonstrated;
scientific validation gate passed;
holdout ready;
graph-channel causality shown.
```

## Current next step

The next empirical step is **not broad H128 scale expansion** and not
shared-capacity v1 scale-up.

Current decision point:

```text
choose between:
  rank-order-native coupled operator;
  or a marginal-coverage-preserving shared-capacity v2.

rank-order-native is the cleaner next branch unless theory specifically needs
finite shared capacity.

observable-extension remains a priority because retained coupled morphology is
still single-observable only: symbol_histogram_distance.
```

Broad H128 coupled surveys remain premature. H128 should stay targeted until a
rank-order-native operator or marginal-preserving capacity repair is justified.

## How to read the project

### Theory orientation

1. [Omega Formal Core v0.2: Future-Distinction Dynamics](docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md)
2. [Future Field Atlas, Phase Ladder, and Terminal Object Sketch](docs/research_notes/omega_theory/future_field_atlas_phase_ladder_and_terminal_object_update.md)
3. [Omega Formal Core v0](docs/research_notes/omega_theory/omega_formal_core_v0.md)
4. [Boundary Non-Privileging and Field-Deformation Theory Note](docs/research_notes/omega_theory/boundary_nonprivileging_and_field_deformation.md)
5. [Horizon Transport and Aligned Amplification](docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md)
6. [Transition Energy and Constraint Untethering](docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md)

### Instrument orientation

1. [Future Field Atlas Instrument Spec](docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md)
2. [Future Field Atlas Glossary](docs/FUTURE_FIELD_ATLAS_GLOSSARY.md)
3. [Future Field Atlas Phase 0/1 Smoke](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_phase0_1_smoke_result.md)
4. [Future Field Atlas H128 Calibration Pass](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_h128_calibration_pass_result.md)
5. [Coupled Hardening Result](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_hardening_result.md)
6. [Coupled H64 Broad Sweep](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_broad_sweep_result.md)
7. [Coupled H64 Ladder](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_ladder_result.md)
8. [Coupled H64 Mechanism Resolution](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_mechanism_resolution_result.md)
9. [Substrate Morphology Atlas](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md)
10. [Shared-Capacity H64 Smoke](docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md)

### Historical orientation

1. [Public Results Index](docs/PUBLIC_RESULTS_INDEX.md)
2. [Running Log](docs/OMEGA_RUNNING_LOG.md)
3. [Project Manual](docs/OMEGA_PROJECT_MANUAL.md)
4. [Historical Probe Terms](docs/research_notes/omega_theory/historical_probe_terms.md)
5. [Hard Top-M Mechanism Result](docs/research_notes/validation_results/rfs_mb0/rfs_mb0_top_m_mechanism_audit_result.md)
6. [Top-M Geometry Audit Result](docs/research_notes/validation_results/rfs_mb0/rfs_mb0_top_m_geometry_audit_result.md)
7. [MaxEnt Local Transition Phase 1 Preflight Result](docs/research_notes/validation_results/rfs_mb0/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md)

## Why this matters for alignment

Omega is motivated by a central alignment problem:

> A system can become highly capable, persistent, and effective while degrading the broader conditions under which value-bearing futures remain possible.

Future Field Atlas does not validate alignment. It builds the measurement discipline needed before the earliest precursor can be resolved:

> Can future-field deformation be measured well enough to distinguish nontrivial future-structuring effects from saturation, trivial persistence, collapse, clock artifacts, probe artifacts, generic finite-frontier dynamics, and product/matched-control equivalence?

The current formal core states the target without assuming a self, agent, valuer, or utility function first:

```text
recoverable, non-erasing, compatible propagation of future-relevant distinctions.
```

## Workflow

This repository is developed through a human-directed, AI-assisted research workflow.

The core theoretical motivation, branch selection, interpretive standards, and key pivots are human-generated. AI systems are used as implementation and critique accelerators: they draft specs, modify runners, generate reports, audit code, summarize results, and propose follow-up experiments.

## Roadmap

```text
VAL0/VAL1:
  historical reconnaissance; useful but not the active empirical frame

RFS0:
  exact finite reachability measurement-floor smoke; insufficient control separation

RFS-MB0 / horizon-transport lineage:
  neutral future-landscape deformation program;
  endpoint support/distribution and quotient probes became measurement-limited;
  horizon transport and transition-energy substrates revealed useful anatomy;
  hard top-m audits narrowed the preservation response to low-rank successor-boundary geometry

Future Field Atlas:
  current active empirical frame;
  raw topology first;
  formal spec identity;
  coupled product-vs-joint future-field scans;
  current result: H64 near-zero mechanism resolution, scalar saturation by 0.020,
  product selector distinct from zero-penalty joint rank-prefix, pair005 heavy-pair clue

Theory arm:
  current active formal frame;
  Omega Formal Core v0.2: future-distinction dynamics;
  phase ladder, atlas interface, falsification criteria, and terminal-object sketch

Next coupled operators:
  consider rank-order-native, shared-capacity, boundary-collision, or
  asymmetric-deformation operators; shared-capacity is the current leading
  principled candidate

Scale hierarchy / constructor-like branches:
  only after future-field instrumentation and formal claim ladder mature enough
```

## Important caveat

The current scientific claim is modest:

> Future Field Atlas can measure reconstructible finite future-field topology under lawful transition substrates. Current coupled H64 results show near-zero scalar mismatch sensitivity that saturates by `0.020`, a true product selector distinct from zero-penalty joint rank-prefix selection, and a persistent pair005 heavy-pair clue. Omega-compatible subobjects have not been demonstrated.
