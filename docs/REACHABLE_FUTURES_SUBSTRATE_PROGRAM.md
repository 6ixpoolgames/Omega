# Reachable Futures Substrate Program

Public design note for the empirical reset

## Purpose

The empirical arm of Omega is resetting around substrate design.

The object of interest is **reachable futures**: the structure of possible continuations available to a bounded process under neutral transformations.

The current question is:

```text
Can bounded structures be derived from neutral transition systems, and do those
structures have identity-preserving reachable futures that can be distinguished
from trivial persistence, local capture, and control artifacts?
```

This is narrower than the full Omega theory. It is the empirical foundation needed before stronger Omega claims would be meaningful.

## Minimal Formalism

The primitive substrate is deliberately small:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

-> subset X x X:
  neutral transformation relation
```

Everything else is derived.

```text
time:
  chains of relation

asymmetry:
  non-equivalent reachable future sets

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

A full experiment can be written:

```text
Experiment = (X, -> ; E_sigma, ~=_sigma, H, P)
```

where the substrate is left of the semicolon and probe choices are right of it.

```text
E_sigma:
  boundary / bounded-structure extraction rule at scale sigma

~=_sigma:
  structural continuity criterion

H:
  horizon

P:
  optional perturbation relation
```

The central measured object is:

```text
F_H^mu(x):
  identity-preserving reachable futures of a derived bounded structure mu
```

See:

```text
docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md
```

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

Markov-blanket / boundary formalisms:
  minimal inside/outside/interface decompositions for bounded processes
```

Later layers may use computational mechanics, causal abstraction, and assembly or lineage measures, but they should not be the base substrate.

## Substrate Ladder

### RFS0 strict finite reachability: exact measurement floor

Minimal exact transition system with explicit admissibility filters.

```text
states
transformations
admissibility constraints
reachable sets
viability kernels
capture / recovery basins
terminal hazards
```

Status:

```text
completed first smoke; exact computation is cheap, but random-edge and
shuffled-admissibility controls remain too strong.
```

Lesson:

```text
opaque admissibility is not enough; the next substrate must derive the bounded
identity whose futures are being tracked.
```

### RFS-MB0: derived boundary / identity futures

Derive bounded-structure candidates from `(X, ->)` and measure identity-preserving reachable futures.

```text
boundary extraction E_sigma
structural continuity ~=_sigma
identity-preserving future sets F_H^mu
future contraction ratios
control comparison against shuffled relations and random transitions
```

Goal:

```text
move from whole-graph futures to futures of derived bounded structures
```

### RFS-MB1: perturbation-recovery of identity-continuity

Adds boundary perturbation, damage, recovery, and re-entry into identity-continuity.

Goal:

```text
distinguish raw identity persistence from recoverability
```

### RFS-MB2: coupled bounded processes

Studies multiple derived bounded structures in the same transition substrate.

Goal:

```text
distinguish compatibility, constructive support, destructive interference,
capture, and component erasure as relations among identity-preserving futures
```

The older internal term `multifield` should be treated as historical. Prefer:

```text
coupled bounded processes
multi-component transition systems
composed processes
```

### RFS-MB3: scale hierarchy

Studies nested or composable bounded structures across extraction scales.

Goal:

```text
represent fractal / scale-relative agency without assuming the whole field is
the identity-bearing object
```

### RFS-MB4: constructor-candidate substrate

Adds repeatable transformation capacity of bounded processes.

Goal:

```text
move from identity-preserving futures to constructor-level futures
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
bounded process
identity-preserving futures
coupled bounded processes
constructor candidate
repeatable transformation capacity
component preservation
component erasure
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
sampled counterfactual coupled-process deltas can detect constructive support
strict finite reachability is exact and cheap at small scale
```

What has not been shown:

```text
clean Omega-compatible subobjects
robust pseudo-Omega discrimination
identity-preserving bounded-process futures
constructor-level futures
a general detector for value-bearing trajectory structure
```

The likely blocker is substrate resolution and identity extraction, not compute.

## Relationship To The Broader Theory

The foundational drafts motivate the larger ambition:

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

RFS0/RFS-MB0/RFS-MB1/RFS-MB2/RFS-MB3/RFS-MB4 are not replacements for that theory. They are the empirical substrate ladder for testing whether the theory can attach to reproducible mathematical objects.

## Public Claim Boundary

Allowed current claim:

```text
We are developing minimal substrates for studying reachable futures of derived
bounded structures and testing when identity-preserving continuation can be
distinguished from trivial persistence, recoverability, constructive
compatibility, destructive capture, and constructor-level persistence.
```

Not yet allowed:

```text
Omega is validated.
Alignment is solved.
Viability is identical to value.
The current toy probes demonstrate full Omega compatibility.
The extracted bounded structures are agents.
```
