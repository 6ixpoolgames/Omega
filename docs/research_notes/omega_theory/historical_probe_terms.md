# Historical Probe Terms

Glossary appendix for older validation branches and result-index jargon

## Purpose

The Omega repository contains several historical probe branches whose terminology can be hard for new readers to parse.

This file defines older probe/result terms that are useful for provenance, controls, and failure analysis, but are no longer the current validation center.

The current validation center is VAL0-G. These terms mostly belong to earlier COM/fiber, trajectory-space, DA/DAR/DAX, rule-space, and VAL0-CT calibration branches.

For public-facing writing, prefer plain-language explanations first, then introduce the internal term if needed.

## COM / fiber branch

### COM

COM means center of mass.

In the historical probes, COM was an analytic coordinate/readout used to coarse-grain toy-substrate states and track propagation through time.

COM is not Omega. It is a historical coordinate that produced a bounded positive witness in earlier toy substrates.

### COM-like witness

A COM-like witness is historical evidence that a COM-based readout showed viable propagation through a toy substrate under some controls.

It should be read as:

```text
bounded evidence for viable propagation in a specific toy setting
```

not as:

```text
proof of Omega
```

### Fiber

A fiber is a coarse-grained bundle or class of states/trajectories under a quotient or readout.

In the historical COM branch, fibers were used to ask whether trajectories moved through structured coarse-grained regions rather than arbitrary microstates.

### Fiber transport

Fiber transport is propagation through coarse-grained fibers over time.

The question is whether a trajectory moves through fibers in a way that preserves meaningful continuation structure rather than collapsing into noise, stasis, or a degenerate coordinate.

### Certified fiber

A certified fiber is a fiber that passed the relevant guardrails or controls for a particular historical probe.

Certification is probe-local. It does not mean the fiber is Omega-compatible in the full theory.

### Multi-step viable propagation

Multi-step viable propagation means future-bearing continuation across more than one transition or horizon.

It is an older phrase close to the current VAL0-CT phrase:

```text
future-bearing reachability
```

### F,T attractive multifield toy substrate

The F,T attractive multifield toy substrate was an older coupled-field toy system where COM/fiber witnesses were tested.

It should not be confused with full multifield Omega. It was a specific toy environment, not the general theory.

## Coarse-graining and quotient terms

### Quotient

A quotient is a coarse-graining that maps detailed states, trajectories, or histories into equivalence classes.

A quotient is useful only if it preserves the structure relevant to the claim being tested.

### Learned quotient

A learned quotient is a coarse-graining discovered by a learning method rather than hand-coded by the researcher.

In older probes, learned quotients were used to test whether viable propagation structure could be rediscovered without being handed COM labels.

### Learned kappa

Learned kappa was an older learned-quotient / learned coarse-graining attempt.

It asked whether simple predictive clustering could discover the same kind of viable propagation structure as COM.

The historical result was mixed/negative: learned kappa saw some structure but did not replace COM as the stronger analytic coordinate.

### Coarse-graining discipline

Coarse-graining discipline means using controls to test whether a readout preserves relevant structure rather than inventing it.

A disciplined coarse-graining should reject fakeouts such as pure phase, stasis, noise, arbitrary clustering, and component-erasure.

### Component projection

A component projection is a readout that focuses on one component of a larger coupled system.

Component projections are useful diagnostics, but can become fakeouts if the target structure requires multiple components.

### Component balance

Component balance asks whether a candidate signal depends on multiple necessary components rather than collapsing to one component.

A high score from one component alone may indicate a fakeout or over-compressed explanation.

### Component erasure

Component erasure is the failure mode where a metric looks good because it ignores a necessary component.

This is a scale/abstraction problem: the readout hides collapse by throwing away the part that collapsed.

## Trajectory-space and invariant branch

### Trajectory-native branch

The trajectory-native branch attempted to define Omega-like structure directly over trajectories, rather than through COM/fibers or constructor task algebras.

It is currently demoted relative to VAL0-CT.

### Viable trajectory geometry

Viable trajectory geometry was an attempted trajectory-space route: look for geometric structure among viable futures.

Historical controls showed that simple rank/collapse geometry was too vulnerable to fakeouts.

### Ordered distinction readout

An ordered distinction readout tracks whether distinctions persist in an order-sensitive way over trajectories.

These readouts were diagnostically useful but did not become object-defining.

### Invariant stack

An invariant stack is a combined set of candidate tests/constraints meant to reject fakeouts while retaining the target signal.

A stack can fail by being too weak or too strict.

In the historical trajectory branch, stronger stacks rejected controls but also erased the coupled target condition.

### Soft stack

A soft stack is a relaxed or continuous version of an invariant stack.

It tests whether a branch failed because thresholds were too hard rather than because the object was misspecified.

### Pareto profile

A Pareto profile is a multi-metric non-dominated profile used when no single hard threshold is reliable.

It helps show tradeoffs among candidate criteria without forcing premature scalarization.

### Control leak

A control leak occurs when a control condition passes the same detector as the target.

Control leaks weaken interpretation because the detector is not specific to the hypothesized structure.

### Guardrail

A guardrail is a pre-specified control, diagnostic, or constraint designed to block a known fakeout.

Guardrails are not decorative. They define what a positive result must survive.

### Load-bearing

A feature is load-bearing if it is actually necessary for the signal.

If removing, shuffling, or ablating the feature does not reduce the signal, then it was not load-bearing.

### Relation load-bearing

Relation is load-bearing when causal-continuity or relational structure is necessary for the signal.

A relation-shuffled control should damage the result if relation is genuinely load-bearing.

### Asymmetry load-bearing

Asymmetry is load-bearing when path-consequence differences are necessary for the signal.

An asymmetry-ablated or symmetrized control should damage the result if asymmetry is genuinely load-bearing.

## DA / DAR / DAX branch

### DA

DA refers to distinction/asymmetry probes.

These probes tested primitive-floor structure before adding the full relation component.

### DAR

DAR refers to distinction, asymmetry, and relation.

The DAR branch tried to build minimal worlds where these primitives were jointly necessary for persistence-like or proto-Omega-like structure.

### DAX

DAX refers to the later rule-space / cellular-automata-style branch derived from the distinction/asymmetry/relation program.

It included ECA and expanded rule-space probes such as q=3/r=1.

### Non-commutative history

Non-commutative history means order matters.

```text
A then B
  is not equivalent to
B then A
```

This was used to sharpen asymmetry: different ordered paths should lead to different consequences.

### Edge memory

Edge memory is memory stored on persistent directed relations or edges rather than only in local node states.

It was introduced to test relation as persistent causal-history dependence rather than local-state recurrence.

### Connection graph

A connection graph is a graph of relations used to represent which histories, sites, or states are connected by persistent relation-like structure.

In DAX-R, connection-like relation was tested as an admissibility criterion for coarse-graining.

### Lineage cap

A lineage cap is a diagnostic limit or saturation effect where lineage-like continuation becomes artificially capped by the substrate or metric.

Frequent lineage caps can make apparent persistence hard to interpret.

### Merge conflict

A merge conflict occurs when multiple histories or branches map into the same downstream state or identity class in a way that obscures distinct causal histories.

It can create fake persistence by hiding path differences.

### Local phase fakeout

A local phase fakeout is apparent identity or persistence explained by clock-like phase recurrence.

It is a fakeout when the claim requires historical identity or recoverability rather than phase cycling.

### Symmetric/self leak

A symmetric/self leak occurs when a supposedly relational or asymmetric detector also passes symmetric or self-only controls.

This suggests the detector may be measuring local recurrence or generic persistence rather than the intended primitive structure.

## Rule-space and motif terms

### ECA

ECA means elementary cellular automata: the 256 one-dimensional binary nearest-neighbor cellular automata rules.

They were used as a minimal exhaustive rule-space audit.

### q=3/r=1

q=3/r=1 denotes a one-dimensional cellular automata rule space with three symbols/states and radius one.

It was explored because it offers more expressive structure than elementary binary rules while remaining relatively small.

### q=2/r=2

q=2/r=2 denotes a binary cellular automata rule space with radius two.

It was sampled as another minimal expansion beyond ECA.

### Motif

A motif is a recurring local pattern in a rule-space or cellular-automata substrate.

Motifs can be interesting without being Omega-like. They require guardrails against phase, emission, stasis, and interaction fakeouts.

### Emitter-like motif

An emitter-like motif repeatedly emits patterns.

Emitter-like motifs can show robust persistence, but emission alone does not establish recoverable identity, valuerhood, or Omega compatibility.

### Motif anatomy

Motif anatomy is the analysis of how a motif works: its persistence, perturbation response, dependence on primitives, and interaction behavior.

### Motif ecology

Motif ecology is the study of how motifs interact, coexist, compose, or interfere inside a rule-space substrate.

### Fertile band

A fertile band was a historical expectation/diagnostic region where interesting motif density might appear.

It should not be treated as a target definition. It was a pretest expectation, not Omega itself.

### Barren band

A barren band is a rule-space region expected to lack useful structured signal or used as a contrast/control region.

In historical probes, barren bands sometimes produced control positives, which weakened detector interpretation.

### Detector freeze

A detector freeze means pre-registering a detector before held-out evaluation.

The point is to prevent changing the detector after seeing held-out results.

### Held-out prediction

Held-out prediction tests a frozen detector on data, rules, or worlds not used to design it.

A held-out failure is stronger evidence against a detector than a failure on exploratory data.

## Run-status terms

### Smoke run

A smoke run is a small early run designed to check whether a probe behaves sanely before scaling.

Smoke runs are not final validation.

### Calibration run

A calibration run tests whether a probe's controls, diagnostics, thresholds, or generator settings are in a reasonable range.

Calibration runs should not be over-interpreted as validation.

### Stress run

A stress run tests robustness under larger scale, stronger perturbation, broader generator settings, or adversarial controls.

### Branch closure

Branch closure is the decision to stop scaling a validation branch because controls, fakeouts, or failure modes remain unresolved.

Closure does not mean the branch was useless. It means it should no longer be treated as the validation center.

### Demoted branch

A demoted branch is a line of investigation retained for provenance and lessons learned, but no longer treated as the current active validation path.

### Historical result set

A historical result set is retained because it documents how the project reached its current state.

Historical result sets may include useful controls, negative results, and failure anatomy, even when they are no longer central.

## Public-facing usage note

When writing for new readers, translate historical probe terms into their current role.

Examples:

```text
COM/fiber witness:
  historical toy-substrate evidence for viable propagation

DAX-G5:
  held-out detector failure that helped motivate the VAL0-CT pivot

trajectory-native invariant stack:
  demoted attempt to define Omega-like structure directly over trajectories

fertile band:
  historical diagnostic expectation, not a target definition
```

The current front door remains:

```text
VAL0-G:
  neutral-grammar recoverable-continuation geometry in constructor-style task algebras
```
