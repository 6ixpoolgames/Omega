# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega** theory project.

The current empirical arm studies **reachable futures**: how abstract dynamical substrates preserve, lose, recover, compose, or capture future possibility under constraints.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, or moral rules. The executable work in this repo is the narrower downstream effort: building minimal substrates where those ideas can become mathematically testable.

This repo contains theory notes, foundational drafts, historical validation attempts, current substrate-design notes, and executable probes.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## One-sentence summary

**We study reachable futures: which possible continuations remain viable, recoverable, composable, or become locally persistent while degrading broader future possibility.**

The current empirical reset asks a narrower substrate question:

**What is the minimal substrate resolution needed to distinguish generic viable continuation from compatibility-preserving viable propagation, local capture, and trivial persistence?**

Current status, in one line:

**VAL0/VAL1 were useful reconnaissance probes; the active pivot is now substrate design for reachable futures of persistent transformation-capacity structures.**

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

In this framing, alignment is not a terminal-state target. It is a constraint on trajectory space:

> An aligned system should preserve and extend the conditions under which recoverable value-bearing futures remain possible.

The current empirical program is still only a first step. It does not validate alignment. It asks what substrate is needed before the earliest precursor can be resolved:

> Can reachable futures be measured well enough to distinguish mere viability from recoverable, compatibility-preserving viability and local capture?

## Current empirical pivot: reachable futures substrate design

The project has moved from task-graph probes toward a substrate-first program for **reachable futures**.

The current question is not:

```text
Did we find Omega?
```

It is:

```text
What minimal substrate can resolve the difference between:
  generic viable continuation
  trivial persistence
  recoverable viability
  constructive compatibility
  local capture / destructive lock-in
  constructor-level viable continuation
```

The mature external frameworks we are anchoring to are:

```text
reachability analysis:
  reachable sets, reachable tubes, reach-avoid structure

viability theory:
  viability kernels, capture basins, controlled invariant sets

formal methods:
  finite transition systems, safety/liveness, counterexamples

Constructor Theory:
  substrates, attributes, tasks, possible/impossible transformations,
  constructors as repeatable transformation capacity

process / compositional systems:
  parallel and sequential composition, interfaces, coupled processes

network robustness:
  bottlenecks, cuts, redundancy, perturbation sensitivity
```

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
```

Lesson:

```text
viable continuation is easy to culture in nontrivial substrates;
Omega-compatible discrimination is not yet demonstrated;
the likely blocker is substrate resolution, not compute.
```

Current design files:

- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
- [Viability ecology reorientation](docs/research_notes/validation_design/val_ecology_viability_reorientation.md)
- [VAL1-MF interference audit result](docs/research_notes/validation_results/val1_mf_interference_audit_smoke_result.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)

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

## Current formal stack

The current theory is built from a small primitive stack:

```text
distinction
  -> asymmetry
  -> relation / causal continuity
  -> identity
  -> continuability
  -> recoverability
  -> valuerhood
  -> viable trajectory space
  -> Omega-compatible futures
```

In plain language:

```text
distinction:
  differences can exist

asymmetry:
  different paths can produce different consequences

relation:
  causal continuity links differences across transformation

identity:
  organized causal continuity persists through change

continuability:
  identity has admissible future paths

recoverability:
  continuability survives perturbation

valuerhood:
  a bounded historical identity has continuations that preserve, degrade,
  restore, or collapse its own recoverable continuability

viability:
  continuability under constraints and horizons

Omega:
  nested value-bearing trajectory space that remains recoverably compatible
```

Start with:

- [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
- [Viability ecology reorientation](docs/research_notes/validation_design/val_ecology_viability_reorientation.md)

## Broader theory pipeline

The current reachable-futures substrate work is the downstream empirical layer of a broader theory pipeline.

The foundation stack supplies the upstream physical, structural, normative, and control-theoretic layers that motivate why future-bearing reachability is worth testing.

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
  -> empirical program for minimal substrates that can resolve viable futures
```

Start here for the pipeline view:

- [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)
- [Foundational theory drafts](docs/progenitor_drafts/README.md)
- [Gradient Ethics draft](docs/progenitor_drafts/gradient_ethics.pdf)
- [Gradient Field Theory draft](docs/progenitor_drafts/gradient_field_theory_of_value_v51.pdf)
- [ECHO draft](docs/progenitor_drafts/echo_rosetta_version.pdf)
- [TELOS draft](docs/progenitor_drafts/telos_2_0_draft.pdf)

## Why Constructor Theory?

Constructor Theory is useful here because it gives a language for possible and impossible transformations.

Instead of asking only:

```text
Did the agent survive?
Did reward increase?
Did a gridworld variable stay high?
```

reachable-futures probes ask:

```text
Which transformations remain possible?
Which paths preserve future reachability?
Which paths collapse into lock-in?
Which geometries retain descendant possibility across horizons?
Which policies or dynamics select those geometries?
```

This makes the validation target less anthropocentric and less preference-first.

Working bridge:

```text
Constructor Theory gives a language for possible and impossible transformations.
Omega asks which possible transformations preserve value-bearing future possibility.
```

## Reading paths

### For a new reader

1. [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
2. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
3. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
5. [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)

### For implementation work

1. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
2. [VAL0-G neutral grammar geometry atlas spec](docs/VAL0_G_NEUTRAL_GRAMMAR_GEOMETRY_ATLAS_SPEC.md)
3. [VAL1-MF interference audit result](docs/research_notes/validation_results/val1_mf_interference_audit_smoke_result.md)
4. [Validation design notes](docs/research_notes/validation_design/README.md)

### For project history

1. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)
5. [Historical probes](results/historical_probes/)
6. [Foundational theory drafts](docs/progenitor_drafts/README.md)

## Current next step

The current implementation target is **RFS0**, a small finite reachable-futures substrate with exact reachability and viability measurements.

Public summary:

```text
define:
  finite transition systems with explicit states, transformations,
  admissibility constraints, and perturbations

measure:
  reachable sets
  viability kernels
  capture / recovery basins
  terminal hazards
  future-space contraction under intervention

defer:
  Omega-positive labels
  full constructor agency
  broad multifield scaling
  GPU-heavy experiments
```

Technical design is in:

- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)

## Roadmap

```text
VAL0-CT:
  completed first task-space calibration layer
  R1 anchor wins reproduced
  held-out/generalized R1 claim not established

VAL0-G:
  completed neutral-grammar reconnaissance
  showed stable viability regimes and cap-censoring limits

VAL1-MF:
  completed first multifield reconnaissance
  sampled deltas can detect constructive support-like interference

RFS0:
  active reset target
  exact finite reachable-futures substrate with viability kernels and
  capture/recovery basins

RFS1:
  perturbation-recovery substrate
  distinguish persistence from recoverability

RFS2:
  coupled-process substrate
  distinguish compatibility from capture and component erasure

RFS3:
  constructor-candidate substrate
  persistent transformation-capacity structures with successor relations
```

Later stages should not be implemented until RFS0 has clean definitions, controls, and failure modes.

## Important caveat

This repository does not prove Omega as a scientific theory.

At present it contains:

```text
theory notes and draft formalizations
foundational theory drafts that motivate the pipeline
historical toy-substrate probes
negative and ambiguous results
current reachable-futures substrate reset
VAL0-CT validation designs and results
```

The current scientific claim is modest:

> Viable continuation dynamics appear in our toy substrates, but Omega-compatible subobjects have not been cleanly demonstrated. The next empirical question is the minimal substrate resolution required to distinguish compatibility-preserving viable propagation from generic viability, trivial persistence, and local capture.

VAL0/VAL1 tested early versions of that precursor. The project is now resetting around reachable-futures substrate design.
