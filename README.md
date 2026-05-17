# Omega Validation

This repository is the executable validation workspace for the Omega theory
project.

## What Is Omega?

Omega is a proposed **structural theory of value-bearing futures**: a way to
study which possible trajectories preserve, expand, trap, or collapse the
conditions under which value-bearing histories can continue.

In philosophy terms, this sits near formal value theory and axiology. In AI
alignment terms, it is closer to a structural account of future-preserving
reachability than to reward modeling, preference learning, or utility
maximization.

The working idea is simple:

```text
Some futures preserve the conditions for value-bearing histories to continue.
Some futures collapse, trap, erase, or narrow those conditions.
```

Omega studies that difference without starting from human preferences, rewards,
utility functions, or moral rules.

At the highest level, Omega asks:

> Which possible trajectories preserve or expand recoverable, compatible,
> value-bearing possibility across time and scale?

This is not a claim that all persistence is good. A cancer, a paperclip
maximizer, or a locked-in exploitative system can persist while destroying
broader future possibility. Omega therefore cares about **recoverable,
compatible, future-bearing structure**, not raw survival.

The current formal stack is:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viable trajectory space
-> Omega-compatible futures
```

In plainer terms:

- distinctions can exist;
- different paths can matter;
- causal continuity lets histories form;
- some histories become identities;
- some identities can recover from disturbance;
- some recoverable identities become valuers, because their possible
  continuations matter to their own future continuability;
- Omega asks which larger trajectory structures preserve and compose those
  value-bearing possibilities.

The project is not claiming this is proven. The point of this repo is to turn
that idea into testable mathematical objects and let controls break them when
they are too weak.

The current stance is deliberately modest:

> derive candidate mathematical objects, implement them, test them against
> controls, and record what fails.

## Current Pivot: VAL0-CT

The project has recently pivoted from bare field dynamics and cellular/rule
space probes toward a Constructor-Theory-style task-space validation layer.

Current working thesis:

```text
Omega is the compatibility structure of value-bearing trajectory space.
```

The current validation target is not full Omega. The next target is
**VAL0-CT**, a single-field proto-Omega probe in generated constructor-style
task algebras.

VAL0-CT asks:

```text
Does persistence-conditioned reachability, R1, predict long-horizon
reachability retention better than raw reachability, R0, and matched
R0-lookahead controls in structured task algebras?
```

This is intentionally narrower than the full theory. It tests whether reachable
task-space can remain future-bearing across horizons. If that fails, the current
proto-Omega operationalization is wrong or underspecified.

Start here for the current pivot:

- [VAL0-CT implementation spec](docs/research_notes/validation_design/val0_ct_implementation_spec.md)
- [VAL0-CT validation design](docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md)
- [Constructor Theory and Omega axiology](docs/research_notes/omega_theory/constructor_theory_and_omega_axiology.md)
- [Deriving Omega relevance from primitives](docs/research_notes/omega_theory/deriving_omega_relevance_from_primitives.md)
- [Current formal stack](docs/research_notes/omega_theory/formal_stack_v0.md)
- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
- [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)

## How To Read The Older Results

The older COM/fiber, trajectory-space, CA, DAR, and DAX probes are retained
because they document the path, controls, and failure modes that forced the
current pivot.

They should not be read as the current validation center.

Current interpretation:

- COM-like fiber transport is historical evidence for viable propagation and
  coarse-graining discipline.
- Trajectory-space probes are useful negative constraints and fakeout anatomy.
- CA/DAR/DAX probes calibrate the primitive floor: distinction, asymmetry, and
  causal continuity.
- DAX-G5 failed as a held-out predictive detector, which is part of why the
  project moved to task-space validation.

## Start Here

- [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
- [Running log](docs/OMEGA_RUNNING_LOG.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)
- [Current theory draft](docs/current_theory/README.md)
- [Validation design notes](docs/research_notes/validation_design/README.md)
- [Omega theory notes](docs/research_notes/omega_theory/)
- [Public terms and translations](docs/research_notes/omega_theory/public_terms_and_translations.md)
- [Primitive-branch notes](docs/research_notes/primitive_branch/README.md)
- [Progenitor drafts](docs/progenitor_drafts/README.md)

## Current Next Step

Implement the VAL0-CT smoke target, CPU-first:

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
  pseudo_omega

primary comparison:
  R1 vs R0 vs equal-budget R0_lookahead on long-horizon reachability retention
```

The first implementation should be lean. Get `R0` correct on toy graphs before
implementing `R1`. Do not add mixed generators, noise branching, embodied
agents, multifield coupling, or GPU acceleration until the first three
generator families are clean.

Future result outputs should live under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Use `results/local_runs/` for ignored smoke, calibration, stress, or scratch
outputs. Do not add new root-level `*_results` folders.

## Important Caveat

This repository does not prove Omega as a scientific theory. At present it
contains:

- theory notes and draft formalizations;
- historical toy-substrate probes;
- negative and ambiguous results;
- a current validation design for VAL0-CT.

The scientific value of the repo is in the controls and failure modes as much
as in any positive signal.

## Environment

Use the local virtual environment directly when working on the original machine:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

For CPU-heavy probes, the calibrated default is:

```text
18 worker processes
```

VAL0-CT should start CPU-first. GPU support is deferred until smoke runs show a
real dense batched reachability bottleneck.

For older GPU/CuPy work on the original machine, use `omega_env.bat` or run
`omega_env.ps1` with a PowerShell execution-policy bypass. The environment
scripts add Torch's bundled CUDA 13 NVRTC DLL directory to `PATH` and point
CuPy's kernel cache at `.cupy-cache/`.

## Historical Result Sets

The public tree keeps compact historical outputs that matter for provenance and
failure analysis. They are no longer the current center:

- `results/historical_probes/`

Historical scripts remain in the repository because they document how the
current state was reached. New work should normally start from the VAL0-CT
validation design unless deliberately revisiting an older branch.
