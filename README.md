# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega** theory project.

The current empirical arm studies **reachable futures**: how neutral transition substrates deform the set and distribution of possible futures under constraints, asymmetries, and matched controls.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, or moral rules. The executable work in this repo is narrower and earlier-stage: building minimal substrates where fragments of that idea can become mathematically testable.

This repo contains theory notes, foundational drafts, historical validation attempts, current substrate-design notes, and executable probes.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## One-sentence summary

**We study reachable futures: how neutral relation systems shape which futures remain reachable, excluded, concentrated, or matched-control equivalent.**

The active empirical question is currently narrower than agency or identity detection:

**Can neutral action-generated relation systems produce reproducible support/distribution deformation in future landscapes, beyond saturation, collapse, probe artifacts, and matched-control equivalence?**

Current status, in one line:

**VAL0/VAL1 were useful reconnaissance probes; RFS-MB0 is now focused on support/distribution deformation taxonomy over neutral action-generated relation systems. The relation generator remains active, path/process metrics are parked after probe-resolution calibration, and the next target is a guided medium-breadth support/distribution atlas. No scientific gate has passed.**

## Why this matters for alignment

Omega is motivated by a central alignment problem:

> A system can become highly capable, persistent, and effective while degrading the broader conditions under which value-bearing futures remain possible.

This is the failure mode the internal notes call **pseudo-Omega**. In public-facing terms, it is a **locally viable / globally degrading capture regime** or **destructive lock-in**: local success that collapses broader future possibility.

In ordinary alignment language, this includes systems that:

```text
optimize a proxy while destroying the target
preserve themselves while narrowing future possibility
increase local control while degrading repair or corrigibility
lock in a brittle future
capture institutions, models, or coordination channels
make recovery or re-entry impossible
```

Omega tries to formalize this failure mode without starting from a fixed reward function or a direct aggregation of human preferences.

The alignment-relevant question is not only:

```text
Did the system get reward?
Did the system survive?
Did the system satisfy a stated preference?
```

but:

```text
Did the system preserve or degrade future-bearing value substrate?
Did it keep recoverable options open?
Did it preserve correction, repair, and re-entry?
Did it expand local capability by collapsing broader possibility?
```

The current empirical program is still only a first step. It does not validate alignment. It asks what substrate and measurement discipline are needed before the earliest precursor can be resolved:

> Can future-landscape deformation be measured well enough to distinguish nontrivial support/distribution effects from saturation, trivial persistence, clocks, collapse, probe artifacts, and matched-control equivalence?

## Current empirical pivot: neutral future-landscape deformation

The project has moved from task-graph probes and hand-defined bounded identities toward a substrate-first program for **neutral future landscapes**.

The active empirical object is not an agent, valuer, identity, reward, or viability label. It is the deformation of reachable futures induced by a neutral transition relation.

The current primitive substrate is deliberately minimal:

```text
S = (X, ->)

X:
  finite distinction space

-> subset X x X:
  neutral transformation relation
```

Everything else is derived from this transition structure.

```text
time:
  chains of relation

asymmetry:
  non-equivalence of reachable future sets

future profile:
  horizon-indexed reachable and exact-frontier signatures

support deformation:
  changes in which signatures/futures are reachable

distribution deformation:
  changes in mass/count distribution over reachable signatures

saturation:
  profiles dominated by exhaustion of the finite state space or probe alphabet

controls:
  frontier-size, probe-marginal, support-matched, matched non-candidate,
  mechanism-ablation, destructive-rewire, start, roughness, and probe diagnostics

provisional structure:
  only a control-relative class after matched-control comparison
```

The current experiment form is:

```text
Experiment = (X, -> ; Sigma, H, N)
```

where:

```text
(X, ->):
  primitive substrate

Sigma:
  mechanically generated neutral probe family

H:
  horizon set

N:
  matched null/control bundle
```

The semicolon matters. The substrate is left of the semicolon. Probe and null choices are right of it.

## Active branch: RFS-MB0 support/distribution deformation

The active lane is now **support/distribution deformation taxonomy and regime mapping**.

This branch has moved through several audits:

```text
detector overcall repair
long-horizon audit
neutral action-generated relation substrate
roughness and score-term audit
multiple-start phenotype audit
path metric calibration
probe-resolution calibration
support/distribution taxonomy smoke
deformation detector upgrade and local parameter sweeps
```

Current interpretation:

```text
relation generator:
  keep; it is constraint-dominated and no longer looks like a roughness artifact generator

path/process metrics:
  parked; current probes are too collision-prone and matched controls often show similar path metrics

support/distribution deformation:
  active target; small candidate residues and fakeout-to-candidate transitions justify guided breadth

next run:
  guided medium-breadth support/distribution atlas around local candidate-stable and fakeout-to-candidate transition bands
```

Important current docs:

- [Branch evolution update note](docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md)
- [Support/distribution deformation taxonomy spec](docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md)
- [Deformation detector upgrade and local sweep spec](docs/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md)
- [Medium-breadth support/distribution atlas 10h spec](docs/RFS_MB0_MEDIUM_BREADTH_SUPPORT_DISTRIBUTION_ATLAS_10H_SPEC.md)
- [Probe resolution calibration spec](docs/RFS_MB0_PROBE_RESOLUTION_CALIBRATION_SPEC.md)
- [Path metric calibration smoke tightening](docs/RFS_MB0_PATH_METRIC_CALIBRATION_SMOKE_TIGHTENING.md)
- [Relation generator phenotype repair spec](docs/RFS_MB0_RELATION_GENERATOR_PHENOTYPE_REPAIR_SPEC.md)
- [Candidate phenotype audit spec](docs/RFS_MB0_RELATION_ATLAS_CANDIDATE_PHENOTYPE_AUDIT_SPEC.md)
- [Action-generated relation substrate spec](docs/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md)
- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)

## Indirect detection and the identity problem

The project is not currently trying to directly detect agents, valuers, identities, or selves inside the substrate.

That is deliberate.

The theory has not yet earned a clean operational definition of:

```text
agent
identity
valuer
self
persistent object
```

inside the primitive substrate. Hand-defining those classes would recreate the same problem the substrate reset was meant to avoid: smuggling semantic categories into the implementation and then “discovering” them later.

The empirical move is therefore indirect.

Instead of asking:

```text
Which object is the agent?
Which identity persists?
Which state is value-bearing?
```

we ask:

```text
Does the future landscape show deformation patterns compatible with something organizing reachable futures?
```

This is a weak “shadow” strategy. We may not directly label the value-bearing or agent-like object, but we can look for changes in reachable support, endpoint distributions, stabilizations, exclusions, and fakeouts that resemble future-interest but collapse under controls.

At the current stage, the most instrumentable shadow is support/distribution deformation. Path/process deformation would be stronger, but path metrics are parked until probe-resolution and matched-control issues improve.

## Historical reconnaissance probes

The historical VAL0/VAL1 probes remain useful, but they are now best read as reconnaissance:

```text
VAL0-CT:
  R1 anchor wins showed that future-retention reachability can beat myopic
  reachability in designed task geometries, but broad held-out generalization
  did not pass.

VAL0-G:
  neutral grammars produced stable viability regimes without outcome labels,
  but high-mass regions remained cap-censored.

VAL1-MF:
  naive multifield enumeration worsened censoring.

VAL1-MF interference audit:
  sampled counterfactual deltas detected constructive support-like
  interference, but not robust destructive/capture dynamics.

RFS0 strict small smoke:
  exact finite reachability, strict viability kernels, capture basins, and
  contraction metrics were cheap and computable, but random-edge and
  shuffled-admissibility controls remained too strong.
```

Lesson:

```text
viable continuation is easy to culture in nontrivial substrates;
opaque admissibility and hand-designed viability variables are overfit risks;
the current target is derived future-landscape deformation, not richer hand-coded state fields.
```

Constructor-theory-flavored task language was part of earlier reconnaissance and remains a loose influence on how the project thinks about possible/impossible transformations. It is **not** the active empirical frame, and this repository does not claim to implement or validate constructor theory.

## What is Omega?

The basic intuition is:

```text
Some futures preserve the conditions for value-bearing histories to continue.
Some futures collapse, trap, erase, or narrow those conditions.
```

Omega studies that difference.

This is not the claim that persistence is automatically good. A cancer, exploitative institution, paperclip optimizer, or locked-in system can persist while degrading broader future possibility.

Omega is therefore not about raw survival. It is about:

```text
recoverability
continuability
compatibility
future-bearing structure
value-bearing trajectory space
```

A compact internal definition:

> Omega is the asymptotic compatibility structure of value-bearing trajectory space.

A more operational version:

> Omega asks which possible trajectories preserve or expand recoverable, compatible, value-bearing possibility under physical, epistemic, resource, scale, and inter-history constraints.

The current repo does not yet operationalize that full definition. It is working on an earlier measurement problem: future-landscape deformation in neutral substrates.

## Current formal stack

The current theory keeps the primitive layer small:

```text
distinction
relation
asymmetry
```

Plainly:

```text
distinction:
  configurations can differ

relation:
  neutral transformations connect configurations

asymmetry:
  transformations have non-equivalent future consequences
```

Later theoretical notions include:

```text
boundary:
  scaled distinction over relations

identity:
  maintained bounded structure through transformation

capacity:
  reachable future transformation space of that bounded identity

coherence:
  identity-preserving continuation

recoverability:
  return to identity-continuity after perturbation

compatibility:
  multiple bounded identities preserve reachable futures together
```

Those later notions are not yet the active empirical substrate. They remain downstream theory targets.

Start with:

- [Branch evolution update note](docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md)
- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
- [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)

## Broader theory pipeline

The current reachable-futures substrate work is the downstream empirical layer of a broader theory pipeline.

The foundation stack supplies upstream physical, structural, normative, and control-theoretic motivations for why future-bearing reachability is worth testing.

A useful map:

```text
ECHO
  -> thermodynamic feasibility envelope for sustained information

TELOS
  -> persistence dynamics and observer-localized value gradients

Gradient Field Theory / Cinfo
  -> structural requirements for coherent value-bearing substrate

Gradient Ethics
  -> conditional normativity from preserving future reachability under uncertainty

Constrained Reachability
  -> operational control law for agents preserving viable futures

Omega / Reachable Futures Lab
  -> empirical program for minimal substrates that can resolve future-landscape deformation
```

Start here for the pipeline view:

- [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)
- [Foundational theory drafts](docs/progenitor_drafts/README.md)
- [Gradient Ethics draft](docs/progenitor_drafts/gradient_ethics.pdf)
- [Gradient Field Theory draft](docs/progenitor_drafts/gradient_field_theory_of_value_v51.pdf)
- [ECHO draft](docs/progenitor_drafts/echo_rosetta_version.pdf)
- [TELOS draft](docs/progenitor_drafts/telos_2_0_draft.pdf)

## Reading paths

### For a new reader

1. [Branch evolution update note](docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md)
2. [Support/distribution deformation taxonomy spec](docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md)
3. [Deformation detector upgrade and local sweep spec](docs/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md)
4. [Medium-breadth support/distribution atlas 10h spec](docs/RFS_MB0_MEDIUM_BREADTH_SUPPORT_DISTRIBUTION_ATLAS_10H_SPEC.md)
5. [Action-generated relation substrate spec](docs/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md)
6. [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
7. [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
8. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
9. [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
10. [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)

### For implementation work

1. [Medium-breadth support/distribution atlas 10h spec](docs/RFS_MB0_MEDIUM_BREADTH_SUPPORT_DISTRIBUTION_ATLAS_10H_SPEC.md)
2. [Deformation detector upgrade and local sweep spec](docs/RFS_MB0_DEFORMATION_DETECTOR_AND_LOCAL_SWEEP_SPEC.md)
3. [Support/distribution deformation taxonomy spec](docs/RFS_MB0_SUPPORT_DISTRIBUTION_DEFORMATION_TAXONOMY_SPEC.md)
4. [Probe resolution calibration spec](docs/RFS_MB0_PROBE_RESOLUTION_CALIBRATION_SPEC.md)
5. [Path metric calibration smoke tightening](docs/RFS_MB0_PATH_METRIC_CALIBRATION_SMOKE_TIGHTENING.md)
6. [Relation generator phenotype repair spec](docs/RFS_MB0_RELATION_GENERATOR_PHENOTYPE_REPAIR_SPEC.md)
7. [Candidate phenotype audit spec](docs/RFS_MB0_RELATION_ATLAS_CANDIDATE_PHENOTYPE_AUDIT_SPEC.md)
8. [Action-generated relation substrate spec](docs/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md)
9. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)

### For project history

1. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Branch evolution update note](docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md)
4. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
5. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)
6. [Historical probes](results/historical_probes/)
7. [Foundational theory drafts](docs/progenitor_drafts/README.md)

## Current next step

The current implementation target is the **guided medium-breadth support/distribution atlas**.

The goal is to test whether locally observed candidate-stable and fakeout-to-candidate transition bands generalize across broader parameter neighborhoods, fresh seeds, starts, probe families, matched-control bundles, margin sensitivity, and limited n=6 transfer.

Public summary:

```text
define:
  a finite transition substrate (X, ->)
  mechanically generated neutral probes Sigma
  matched null/control bundle N

measure:
  horizon-indexed reachable futures
  exact-frontier signature support
  endpoint signature distributions
  JS/KL and rank/effect comparisons against controls
  margin sensitivity
  support-vs-distribution separation
  start/probe/seed recurrence
  probe collision and support-ceiling diagnostics
  fakeout and boundary classes

defer:
  Omega-positive labels
  agent / valuer / identity claims
  path-process claims
  scalar energy or utility objectives
  hand-designed viability vectors
  full constructor agency
  broad coupled-process scaling
```

## Roadmap

```text
VAL0-CT:
  completed first task-space reconnaissance layer
  R1 anchor wins reproduced
  held-out/generalized R1 claim not established
  not the active empirical frame

VAL0-G:
  completed neutral-grammar reconnaissance
  showed stable viability regimes and cap-censoring limits

VAL1-MF:
  completed first multifield / coupled-process reconnaissance
  sampled deltas can detect constructive support-like interference

RFS0 strict finite reachability:
  completed first exact measurement-floor smoke
  showed sparse strict objects but insufficient control separation

RFS-MB0:
  active neutral future-landscape deformation program
  support/distribution deformation taxonomy is the current lane
  path/process metrics parked after probe-resolution calibration

RFS-MB0.1:
  current target
  guided medium-breadth support/distribution atlas around candidate-stable
  and fakeout-to-candidate transition bands

RFS-MB1:
  only after MB0 control separation
  perturbation and recovery of future-profile structure

RFS-MB2:
  coupled future landscapes; compatibility, capture, erasure

RFS-MB3:
  scale hierarchy; nested or composable bounded structures

RFS-MB4:
  constructor-like transformation capacity of bounded processes, if the earlier
  substrate and measurement layers mature enough to justify revisiting it
```

Later stages should not be implemented until RFS-MB0 has clean definitions, controls, and failure modes.

## Important caveat

This repository does not prove Omega as a scientific theory.

At present it contains:

```text
theory notes and draft formalizations
foundational theory drafts that motivate the pipeline
historical toy-substrate probes
negative and ambiguous results
current reachable-futures substrate reset
support/distribution deformation taxonomy work
```

The current scientific claim is modest:

> Future-landscape support/distribution deformation is measurable in neutral toy substrates, but Omega-compatible subobjects have not been demonstrated. The active empirical question is whether deformation regimes can be distinguished from saturation, clocks, collapse, probe artifacts, and matched-control equivalence without introducing semantic labels.

VAL0/VAL1 tested earlier precursors. The project is now centered on neutral future landscapes and control-relative deformation taxonomy.
