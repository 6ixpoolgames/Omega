# Omega Validation

This repository is the executable validation workspace for the **Omega** theory project.

Omega is a research program for naturalized axiology: a way to reason about value-bearing possibility without beginning from human preferences, reward functions, utility functions, or moral rules.

The repo contains theory notes, progenitor drafts, historical validation attempts, current validation designs, and executable probes.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects and letting those objects fail when they are too weak.

## One-sentence summary

**Omega studies which possible trajectories preserve or expand recoverable, compatible, value-bearing possibility across time and scale.**

The current empirical program tests a narrower precursor:

**Can future-bearing reachability be detected in Constructor-Theory-style task space?**

## Why this matters for alignment

Omega is motivated by a central alignment problem:

> A system can become highly capable, persistent, and effective while degrading the broader conditions under which value-bearing futures remain possible.

This is the failure mode the internal notes call **pseudo-Omega**. In public-facing terms, it is **destructive lock-in**: local success that collapses broader future possibility.

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

This is why the project focuses on reachability, recoverability, destructive lock-in, Constructor Theory, and task-space validation. The goal is to detect whether a system is preserving future-bearing possibility or converting it into local lock-in.

The current VAL0-CT probe is only the first step. It does not validate alignment. It tests the earliest precursor:

> Can future-bearing reachability be detected and distinguished from raw reachability in constructor-style task space?

## The broader theory pipeline

The current Omega/VAL0-CT work is the downstream validation layer of a broader theory pipeline.

The progenitor drafts are not merely old background. They supply the upstream physical, structural, normative, and control-theoretic layers that explain why future-bearing reachability is the right object to test.

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

Omega / Constructor Theory / VAL0-CT
  -> empirical program for detecting proto-Omega structure in task space
```

In short:

```text
progenitor stack:
  why future-bearing value substrate should exist and matter

Omega derivation:
  what the relevant structure is

VAL0-CT:
  first test of whether that structure has a detectable task-space precursor
```

Start here for the pipeline view:

- [Progenitor stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)
- [Progenitor drafts](docs/progenitor_drafts/README.md)
- [Gradient Ethics draft](docs/progenitor_drafts/gradient_ethics.pdf)
- [Gradient Field Theory draft](docs/progenitor_drafts/gradient_field_theory_of_value_v51.pdf)
- [ECHO draft](docs/progenitor_drafts/echo_rosetta_version.pdf)
- [TELOS draft](docs/progenitor_drafts/telos_2_0_draft.pdf)

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

A compact definition:

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

- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
- [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
- [Deriving Omega relevance from primitives](docs/research_notes/omega_theory/deriving_omega_relevance_from_primitives.md)
- [Omega as viable value-bearing trajectory space](docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md)

## Current validation pivot: VAL0-CT

The project has moved from cellular/rule-space probes toward a **Constructor-Theory-style task-space validation layer**.

Constructor Theory gives a language of:

```text
tasks
attributes
constructors
possible / impossible transformations
task repertoires
```

Omega is treated as a filter/refinement over that task space.

The current validation target is **not full Omega**. It is **VAL0-CT**, a single-field proto-Omega probe.

VAL0-CT asks:

```text
Does persistence-conditioned reachability, R1, predict long-horizon
reachability retention better than raw reachability, R0, and matched
R0-lookahead controls in structured task algebras?
```

In simpler terms:

```text
R0:
  what is reachable?

R1:
  what is reachable that still leaves futures open?

VAL0-CT:
  does R1 predict long-horizon future-bearing reachability better than controls?
```

This is intentionally modest. It tests whether the first precursor of Omega can be operationalized:

```text
reachable task-space that remains future-bearing across horizons
```

Start with:

- [VAL0-CT validation design](docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md)
- [VAL0-CT implementation spec](docs/research_notes/validation_design/val0_ct_implementation_spec.md)
- [VAL0-CT runbook](docs/VAL0_CT_RUNBOOK.md)
- [Constructor Theory and Omega axiology](docs/research_notes/omega_theory/constructor_theory_and_omega_axiology.md)

## Why Constructor Theory?

Constructor Theory is useful here because it shifts the validation target away from hand-labeled toy-agent variables and toward possible transformations.

Instead of asking:

```text
Did the agent survive?
Did reward increase?
Did a gridworld variable stay high?
```

VAL0-CT asks:

```text
Which task repertoires remain possible?
Which task paths preserve future reachability?
Which paths collapse into lock-in?
Which policies preserve future-bearing task space across horizons?
```

This makes the validation target less anthropocentric and less preference-first.

The current working slogan:

```text
Constructor Theory gives the physics of possibility.
Omega gives the constraint structure of value-bearing possibility.
```

## How the progenitor drafts tie in

Each progenitor layer answers a different upstream question.

```text
ECHO:
  What does sustained information processing physically cost?

TELOS:
  Where do persistence and observer-localized value gradients arise?

Gradient Field Theory / Cinfo:
  What structural requirements must a coherent value-bearing substrate satisfy?

Gradient Ethics:
  Why does preserving future reachability have conditional normative force for agents?

Constrained Reachability:
  How should an agent act when reward, uncertainty, reachability, and irreversible loss interact?

VAL0-CT:
  Can the predicted future-bearing reachability signature be detected in task-space dynamics?
```

This is why the current probe is not just an isolated toy model. It is a deliberately narrow test of a downstream signature implied by the larger stack.

The progenitor stack does not prove Omega. It gives the current validation program its target.

## How to read the historical probes

The older COM/fiber, trajectory-space, CA, DAR, and DAX probes are retained because they document the path, controls, and failure modes that forced the current pivot.

They should not be read as the current validation center.

Current interpretation:

```text
COM / fiber results:
  historical evidence for viable propagation and coarse-graining discipline

trajectory-space probes:
  negative constraints and fakeout anatomy

CA / DAR / DAX probes:
  primitive-floor calibration:
  distinction, asymmetry, causal continuity, identity fakeouts

DAX-G5:
  failed as a held-out predictive detector,
  motivating the move toward task-space validation
```

The scientific value of these probes is as much in the controls and failures as in any positive signal.

Historical terminology is defined here:

- [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)

## Reading paths

### For a new reader

1. [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
2. [Progenitor stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)
3. [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
4. [Deriving Omega relevance from primitives](docs/research_notes/omega_theory/deriving_omega_relevance_from_primitives.md)
5. [Omega as viable value-bearing trajectory space](docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md)
6. [Constructor Theory and Omega axiology](docs/research_notes/omega_theory/constructor_theory_and_omega_axiology.md)
7. [VAL0-CT validation design](docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md)

### For the broader theory pipeline

1. [Progenitor stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)
2. [Progenitor drafts overview](docs/progenitor_drafts/README.md)
3. [ECHO draft](docs/progenitor_drafts/echo_rosetta_version.pdf)
4. [TELOS draft](docs/progenitor_drafts/telos_2_0_draft.pdf)
5. [Gradient Field Theory draft](docs/progenitor_drafts/gradient_field_theory_of_value_v51.pdf)
6. [Gradient Ethics draft](docs/progenitor_drafts/gradient_ethics.pdf)
7. [Constrained Reachability context](docs/progenitor_drafts/intelligent_agency_under_computational_irreducibility.pdf)

### For implementation work

1. [VAL0-CT runbook](docs/VAL0_CT_RUNBOOK.md)
2. [VAL0-CT implementation spec](docs/research_notes/validation_design/val0_ct_implementation_spec.md)
3. [VAL0-CT validation design](docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md)
4. [Validation design notes](docs/research_notes/validation_design/README.md)

### For project history

1. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)
5. [Historical probes](results/historical_probes/)
6. [Progenitor drafts](docs/progenitor_drafts/README.md)

## Current next step

The current implementation target is the VAL0-CT smoke run.

Public summary:

```text
families:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

policies:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega / destructive lock-in

primary comparison:
  R1 vs R0 vs equal-budget R0_lookahead
  on long-horizon reachability retention
```

Technical run details are in:

- [VAL0-CT runbook](docs/VAL0_CT_RUNBOOK.md)

## Roadmap

```text
VAL0-CT:
  single-field proto-Omega
  R1 predicts long-horizon reachability retention

VAL1-CT:
  coupled fields
  joint reachability and compatibility gap

VAL2-CT:
  local/global divergence
  pseudo-Omega / destructive lock-in task families

VAL3-CT:
  corridors
  mutually future-bearing task pathways

VAL4-CT:
  scale composition
  higher-order fields vs component fields

VAL5-CT:
  lineage / successor fields
  propagation across generations
```

VAL0 is the current center. Later stages should not be implemented until the single-field task-algebra probe is understood.

## Important caveat

This repository does not prove Omega as a scientific theory.

At present it contains:

```text
theory notes and draft formalizations
progenitor drafts that motivate the pipeline
historical toy-substrate probes
negative and ambiguous results
current VAL0-CT validation design
current VAL0-CT implementation spec
```

The current scientific claim is modest:

> If Omega is the asymptotic compatibility structure of value-bearing possibility, then its earliest detectable precursor should be reachable task-space that remains future-bearing across horizons.

VAL0-CT tests that precursor.

## Historical result sets

The public tree keeps compact historical outputs that matter for provenance and failure analysis. They are no longer the current center:

```text
results/historical_probes/
```

Historical scripts remain because they document how the current state was reached. New work should normally start from the VAL0-CT validation design unless deliberately revisiting an older branch.
