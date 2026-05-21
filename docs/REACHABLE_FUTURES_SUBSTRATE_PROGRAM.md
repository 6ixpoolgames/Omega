# Reachable Futures Substrate Program

Public design note for the empirical reset

## Purpose

The empirical arm of Omega is resetting around substrate design.

The object of interest is **reachable futures**: the structure of possible
continuations available to a system, process, or constructor candidate under
constraints.

The current question is:

```text
What is the minimal substrate resolution required to distinguish generic viable
continuation from trivial persistence, recoverable viability, local capture,
and compatibility-preserving viable propagation?
```

This is narrower than the full Omega theory. It is the empirical foundation
needed before stronger Omega claims would be meaningful.

## External Frameworks

The project should attach to mature literatures wherever possible.

Primary anchors:

```text
reachability analysis:
  reachable sets, reachable tubes, reach-avoid problems

viability theory:
  viability kernels, capture basins, controlled invariant sets

formal methods:
  finite transition systems, safety/liveness, model checking, counterexamples

Constructor Theory:
  substrates, attributes, tasks, possible/impossible transformations,
  constructors as repeatable transformation capacity

process and compositional systems:
  composition, interfaces, coupled processes, resource conversion

network robustness:
  bottlenecks, cuts, redundancy, perturbation sensitivity
```

Later layers may use computational mechanics, causal abstraction, and assembly
or lineage measures, but they should not be the base substrate.

## Substrate Ladder

### RFS0: finite reachable-futures substrate

Minimal exact transition system.

```text
states
transformations
admissibility constraints
reachable sets
viability kernels
capture / recovery basins
terminal hazards
```

Goal:

```text
make reachable futures and viability exact before adding agency language
```

### RFS1: perturbation-recovery substrate

Adds damage, repair, re-entry, and irreversible loss.

Goal:

```text
distinguish raw persistence from recoverability
```

### RFS2: coupled-process substrate

Adds multiple interacting components or fields.

Goal:

```text
distinguish compatibility, constructive support, destructive interference,
capture, and component erasure
```

### RFS3: constructor-candidate substrate

Adds persistent transformation-capacity structures with successor relations.

Goal:

```text
move from "states have futures" to "persistent constructors have futures"
```

## Vocabulary Discipline

Use established terms in empirical work:

```text
reachable set
viability kernel
capture basin
re-entry / recovery basin
controlled invariant set
transition system
constructor candidate
repeatable transformation capacity
component preservation
component erasure
counterfactual coupling delta
```

Use Omega terms only after the measured object is stated in public language.

Examples:

```text
compatibility-preserving viable propagation
  internal relation: Omega-compatible candidate

locally viable / globally degrading capture regime
  internal relation: pseudo-Omega-like candidate
```

## Current Standing

What has been shown:

```text
toy substrates can culture nontrivial viability dynamics
neutral task grammars produced stable viability regimes
sampled counterfactual multifield deltas can detect constructive support
```

What has not been shown:

```text
clean Omega-compatible subobjects
robust pseudo-Omega discrimination
constructor-level futures
a general detector for value-bearing trajectory structure
```

The likely blocker is substrate resolution, not compute.

## Relationship To The Broader Theory

The progenitor drafts motivate the larger ambition:

```text
ECHO:
  thermodynamic / informational feasibility

TELOS:
  persistence and trajectory gradients

Gradient Field Theory / Cinfo:
  structural requirements for coherent value-bearing substrate

Gradient Ethics:
  conditional normativity from preserving viable futures under uncertainty

Constrained Reachability:
  operational control pressure toward preserving viable futures

Omega:
  hypothesized compatibility structure of value-bearing reachable futures
```

RFS0/RFS1/RFS2/RFS3 are not replacements for that theory. They are the empirical
substrate ladder for testing whether the theory can attach to reproducible
mathematical objects.

## Public Claim Boundary

Allowed current claim:

```text
We are developing minimal substrates for studying reachable futures and testing
when viable continuation can be distinguished from trivial persistence,
recoverability, constructive compatibility, destructive capture, and
constructor-level persistence.
```

Not yet allowed:

```text
Omega is validated.
Alignment is solved.
Viability is identical to value.
The current toy probes demonstrate full Omega compatibility.
```
