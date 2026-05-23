# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega** theory project.

The current empirical arm studies **reachable futures**: how abstract dynamical substrates preserve, lose, recover, compose, or capture future possibility under constraints.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, or moral rules. The executable work in this repo is the narrower downstream effort: building minimal substrates where those ideas can become mathematically testable.

This repo contains theory notes, foundational drafts, historical validation attempts, current substrate-design notes, and executable probes.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## One-sentence summary

**We study reachable futures: which possible continuations remain viable, recoverable, composable, or become locally persistent while degrading broader future possibility.**

The current empirical reset asks a narrower substrate question:

**Can neutral transition systems produce future-landscape structure that survives matched-null comparison, rather than just reflecting saturation, clocks, collapse, or probe artifacts?**

Current status, in one line:

**VAL0/VAL1 were useful reconnaissance probes; the active branch is now RFS-MB0 future-landscape detection, with detector v1.1, long-horizon audit support, and action-generated relation-atlas calibration implemented. No aggregate scientific pass yet.**

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

> Can reachable futures be measured well enough to distinguish structured future deformation from saturation, trivial persistence, clocks, collapse, and matched-control artifacts?

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

capacity:
  available future transformation space

future profile:
  horizon-indexed reachable and exact-frontier signatures

future landscape deformation:
  changes in reachability, signature distributions, recurrence, transition
  information, and null-relative divergence across horizons

saturation:
  profiles dominated by exhaustion of the finite state space

controls:
  random, degree-preserving, probe-marginal, fixed-point, cycle, permissive,
  strict, and coordinate-permutation comparisons

provisional structure:
  only a control-relative class after matched-null comparison
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
  horizon

N:
  matched null bundle
```

The semicolon matters. The substrate is left of the semicolon. Probe and null choices are right of it.

Current design files:

- [Future landscape pattern spec](docs/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md)
- [Future landscape detector v1 handoff](docs/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md)
- [Future landscape detector v1.1 smoke result](docs/research_notes/validation_results/rfs_mb0_future_landscape_detector_v1_1_smoke_result.md)
- [Future landscape long-horizon audit result](docs/research_notes/validation_results/rfs_mb0_future_landscape_long_horizon_environment_audit_result.md)
- [Action-generated relation atlas v0 calibration result](docs/research_notes/validation_results/rfs_mb0_action_generated_relation_atlas_v0_calibration_result.md)
- [Future landscape detector v1 smoke result](docs/research_notes/validation_results/rfs_mb0_future_landscape_detector_v1_smoke_result.md)
- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
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
Which future profiles saturate, collapse, cycle, or survive matched controls?
Which apparent structures disappear under degree-preserving or frontier-matched nulls?
```

This makes the validation target less anthropocentric and less preference-first.

Working bridge:

```text
Constructor Theory gives a language for possible and impossible transformations.
Omega asks which possible transformations preserve value-bearing future possibility.
```

## Reading paths

### For a new reader

1. [Future landscape detector v1.1 smoke result](docs/research_notes/validation_results/rfs_mb0_future_landscape_detector_v1_1_smoke_result.md)
2. [Future landscape long-horizon audit result](docs/research_notes/validation_results/rfs_mb0_future_landscape_long_horizon_environment_audit_result.md)
3. [Action-generated relation atlas v0 calibration result](docs/research_notes/validation_results/rfs_mb0_action_generated_relation_atlas_v0_calibration_result.md)
4. [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
5. [Future landscape pattern spec](docs/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md)
6. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
7. [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
8. [Foundation stack as pipeline](docs/research_notes/omega_theory/progenitor_stack_as_pipeline.md)

### For implementation work

1. [Future landscape detector v1 handoff](docs/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md)
2. [Future landscape v1.1 code targets](docs/RFS_MB0_FUTURE_LANDSCAPE_V1_1_CODE_TARGETS.md)
3. [Future landscape detector v1.1 smoke result](docs/research_notes/validation_results/rfs_mb0_future_landscape_detector_v1_1_smoke_result.md)
4. [Future landscape long-horizon audit spec](docs/RFS_MB0_FUTURE_LANDSCAPE_LONG_HORIZON_ENVIRONMENT_AUDIT.md)
5. [Future landscape long-horizon audit result](docs/research_notes/validation_results/rfs_mb0_future_landscape_long_horizon_environment_audit_result.md)
6. [Action-generated relation substrate spec](docs/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md)
7. [Action-generated relation atlas v0 calibration result](docs/research_notes/validation_results/rfs_mb0_action_generated_relation_atlas_v0_calibration_result.md)
8. [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
9. [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)

### For project history

1. [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
2. [Running log](docs/OMEGA_RUNNING_LOG.md)
3. [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
4. [Historical probe terms](docs/research_notes/omega_theory/historical_probe_terms.md)
5. [Historical probes](results/historical_probes/)
6. [Foundational theory drafts](docs/progenitor_drafts/README.md)

## Current next step

The current implementation target is **RFS-MB0 Future Landscape Detector v1.1 with long-horizon and action-generated relation-atlas diagnostics**.

The detector v1.1 smoke, long-horizon audit, and action-generated relation-atlas calibration passed as implementation runs, but not as a scientific gate. The detector keeps local profile candidates visible while preventing them from becoming family-level claims. The long-horizon audit suggests the current failure is not just an H16 cutoff. The relation atlas removes hand-named positive families and produces middle-regime neutral environments, but still has zero atlas gate passes.

Public summary:

```text
define:
  a finite transition substrate (X, ->)
  mechanically generated neutral probes Sigma
  matched null bundle N

measure:
  horizon-indexed reachable futures
  exact-frontier signature distributions
  transition-level signature mutual information
  transition conditional entropy and motif reuse
  JS/KL divergence from random, degree, and probe-marginal nulls
  saturation diagnostics
  conservative control-relative profile classes

defer:
  Omega-positive labels
  agent / valuer / identity claims
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
  active future-landscape detector
  v1.1 implemented; scientific gate not passed

RFS-MB0.1:
  next target
  develop non-saturating structured candidates and stronger frontier/saturation
  matched nulls

RFS-MB1:
  only after MB0 control separation
  perturbation and recovery of future-profile structure

RFS-MB2:
  coupled future landscapes; compatibility, capture, erasure

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

> Reachable-future structure is measurable in neutral toy substrates, but Omega-compatible subobjects have not been demonstrated. The active empirical question is whether future-landscape deformation can be distinguished from saturation, clocks, collapse, and matched-control artifacts without introducing semantic labels.

VAL0/VAL1 tested earlier precursors. The project is now resetting around neutral future landscapes and control-relative detection.
