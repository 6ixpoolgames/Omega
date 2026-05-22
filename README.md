# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega** theory project.

The current empirical arm studies **reachable futures**: how abstract dynamical substrates preserve, lose, recover, compose, or capture future possibility under constraints.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, or moral rules. The executable work in this repo is the narrower downstream effort: building minimal substrates where those ideas can become mathematically testable.

This repo contains theory notes, foundational drafts, historical validation attempts, current substrate-design notes, and executable probes.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## One-sentence summary

**We study reachable futures: which possible continuations remain viable, recoverable, composable, or become locally persistent while degrading broader future possibility.**

The current empirical reset asks a narrower substrate question:

**Can bounded structures be derived from neutral transition systems, and do those structures have identity-preserving reachable futures that can be distinguished from trivial persistence, local capture, and control artifacts?**

Current status, in one line:

**VAL0/VAL1 were useful reconnaissance probes; the active pivot is now a minimal reachable-futures formalism where bounded identities are derived from relational dynamics rather than inserted as state variables.**

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

> Can reachable futures be measured well enough to distinguish mere persistence from identity-preserving, recoverable, compatibility-preserving continuation and local capture?

## Current empirical pivot: minimal reachable-futures formalism

The project has moved from task-graph probes toward a substrate-first program for **reachable futures of derived bounded structures**.

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

capacity:
  available future transformation space

boundary:
  scaled distinction over relations; a derived bounded-structure candidate

identity:
  continuity of a derived bounded structure through neutral transformations

coherence:
  preservation of identity-preserving reachable futures

dissipation-like contraction:
  loss of identity-preserving reachable futures

viability:
  nonempty or sufficiently rich identity-preserving futures

recovery:
  return to identity-continuity after perturbation
```

The current experiment form is:

```text
Experiment = (X, -> ; E_sigma, ~=_sigma, H, P)
```

where:

```text
(X, ->):
  primitive substrate

E_sigma:
  boundary / bounded-structure extraction rule at scale sigma

~=_sigma:
  structural continuity criterion

H:
  horizon

P:
  optional perturbation relation
```

The semicolon matters. The substrate is left of the semicolon. Probe choices are right of it.

Current design files:

- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
- [Viability ecology reorientation](docs/research_notes/validation_design/val_ecology_viability_reorientation.md)
- [RFS0 strict reachable futures small smoke result](docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)

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
the next target is derived bounded identity, not richer hand-coded state fields.
```

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

Then:

```text
boundary:
  scaled distinction over relations

identity:
  maintained bounded structure through transformation

capacity:
  reachable future transformation space of that bounded identity

coherence:
  identity-preserving continuation

dissipation-like behavior:
  contraction of identity-preserving futures

recoverability:
  return to identity-continuity after perturbation

compatibility:
  multiple bounded identities preserve reachable futures together
```

Start with:

- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
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
Which bounded structures retain reachable futures across horizons?
Which coupled bounded processes preserve or erase one another's futures?
```

This makes the validation target less anthropocentric and less preference-first.

Working bridge:

```text
Constructor Theory gives a language for possible and impossible transformations.
Omega asks which possible transformations preserve value-bearing future possibility.
```

## Reading paths

### For a new reader

1. [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
2. [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
3. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
4. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
5. [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
6. [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)

### For implementation work

1. [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
2. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
3. [RFS0 strict reachable futures batch spec](docs/RFS0_STRICT_REACHABLE_FUTURES_BATCH_SPEC.md)
4. [RFS0 strict reachable futures small smoke result](docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md)
5. [Validation design notes](docs/research_notes/validation_design/README.md)

### For project history

1. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)
5. [Historical probes](results/historical_probes/)
6. [Foundational theory drafts](docs/progenitor_drafts/README.md)

## Current next step

The current implementation target is **RFS-MB0**, a derived-boundary / identity-futures smoke.

Public summary:

```text
define:
  a finite transition substrate (X, ->)
  boundary extraction rules E_sigma
  structural continuity criteria ~=_sigma

measure:
  derived bounded-structure candidates
  identity-preserving reachable futures
  identity-continuity survival curves
  future contraction ratios
  recovery after boundary perturbation
  control comparison against shuffled relations and random transitions

defer:
  Omega-positive labels
  scalar energy or utility objectives
  hand-designed viability vectors
  full constructor agency
  broad coupled-process scaling
```

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
  completed first multifield / coupled-process reconnaissance
  sampled deltas can detect constructive support-like interference

RFS0 strict finite reachability:
  completed first exact measurement-floor smoke
  showed sparse strict objects but insufficient control separation

RFS-MB0:
  active reset target
  derive bounded structures from (X, ->) and measure identity-preserving futures

RFS-MB1:
  perturbation and recovery of identity-continuity

RFS-MB2:
  coupled bounded processes; compatibility, capture, erasure

RFS-MB3:
  scale hierarchy; nested or composable bounded structures

RFS-MB4:
  constructor candidates; repeatable transformation capacity of bounded processes
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
VAL0-CT validation designs and results
```

The current scientific claim is modest:

> Viable continuation dynamics appear in our toy substrates, but Omega-compatible subobjects have not been cleanly demonstrated. The next empirical question is whether bounded identities can be derived from neutral transition substrates and whether their identity-preserving reachable futures can distinguish compatibility-preserving continuation from trivial persistence, artifact, and local capture.

VAL0/VAL1 tested early versions of that precursor. The project is now resetting around derived bounded structures and identity-preserving reachable futures.
