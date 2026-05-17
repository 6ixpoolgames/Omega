# Omega Experimental Roadmap

Status: working roadmap after the Constructor Theory / VAL0-CT pivot.

Stance: skeptically open. Treat Omega as a candidate formal object until it
produces definitions, discriminators, and failure modes that survive controls.

## 1. Current Position

The current project center is no longer the early single-Omega entropy
invariant or the COM/fiber witness.

Current validation target:

```text
VAL0-CT:
  single-field proto-Omega validation in constructor-style task algebras
```

Primary question:

```text
Does persistence-conditioned reachability, R1, predict long-horizon
reachability retention better than raw reachability, R0, and matched
R0-lookahead controls in structured task algebras?
```

This is not full Omega validation. It is an intentionally narrow test for the
earliest operational precursor:

```text
reachable task-space that remains future-bearing across horizons
```

## 2. Why The Pivot Happened

Earlier branches taught useful lessons but are no longer the front edge.

Single-Omega work showed:

- raw entropy is not the object;
- viable futures matter more than reachable noise;
- coarse-graining admissibility is central.

COM/fiber work showed:

- viable propagation through certified fibers can survive meaningful controls;
- component preservation and transport matter more than raw entropy expansion;
- learned quotients did not cleanly rediscover the analytic COM coordinate.

Trajectory-space and invariant-stack work showed:

- quotient-light approaches are valuable diagnostics;
- simple trajectory geometry and hard invariant stacks failed control
  guardrails.

CA/DAR/DAX work showed:

- primitive distinction/asymmetry/relation motifs can be found and anatomized;
- q=3/r=1 produced a real motif ecology;
- DAX-G5 failed held-out prediction, so that detector is descriptive rather
  than validation-ready.

The pivot is therefore pragmatic:

```text
move from bare dynamics to task-space structure before trying embodied valuers
or multifield Omega.
```

## 3. Current Formal Spine

Working stack:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viability
-> Omega-compatible viability
-> lushness of value-bearing trajectory space
```

Constructor Theory supplies the task language:

```text
possible / impossible transformations
substrates / attributes / tasks
constructors / task repertoires
```

Omega supplies the relevance filter:

```text
which possible task structures preserve, degrade, expand, or collapse
future-bearing reachability
```

## 4. Immediate Implementation Roadmap

Follow:

- `docs/research_notes/validation_design/val0_ct_implementation_spec.md`
- `docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md`

Implementation order:

```text
1. algebra.py + reachability.py
   get R0 correct on deterministic toy graphs

2. hand-built R0/R1 divergence tests
   prove R1 is not just a renamed R0-lookahead selector

3. generators.py
   low_resolution_dense
   structured_asymmetric
   lock_in_seeded

4. policies.py
   random
   R0
   R0_lookahead
   R1
   pseudo_omega

5. simulation.py + run_smoke.py

6. summarize.py + diagnostics.py
```

Do not implement `mixed`, `noise_branching`, embodied agents, multifield
coupling, or GPU acceleration until the first three generator families are
clean.

## 5. First Smoke Target

Recommended first smoke:

```text
families:
  low_resolution_dense
  structured_asymmetric
  lock_in_seeded

num_tasks:
  64 or 128

num_constructors:
  2 or 4

seeds:
  20-50 per family

horizon grid:
  h in {1, 2, 4}
  H in {4, 8}
  T in {16, 32}

R1 sample size:
  N = 256 candidate paths

R1 threshold:
  primary = 0.50 * R0_initial

policies:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega
```

Primary report:

```text
R1 vs R0 vs R0_lookahead on global long-horizon reachability retention
low-resolution collapse diagnostics
pseudo-Omega local/global divergence
generator-family stability
horizon-band sensitivity
```

## 6. Hardware / Workflow Baseline

Machine profile observed by Python:

- logical CPUs: 24
- calibrated heavy CPU profile: 18 worker processes
- observed CPU usage target: about 80%

VAL0-CT should be CPU-first.

Reason:

- task-graph traversal is easier to inspect on CPU;
- deterministic debugging matters more than throughput at the smoke stage;
- batch parallelism over seeds/families/policies/horizons is enough initially.

GPU work is deferred until smoke runs show a dense fixed-size graph bottleneck.

## 7. Success, Failure, Ambiguity

Success:

```text
R1 preserves or predicts long-horizon reachability retention better than R0
and equal-budget R0_lookahead in structured algebras.

R1 does not spuriously outperform in low-resolution controls.

pseudo-Omega cases show high local reachability with weaker global retention.
```

Failure:

```text
R1 adds no predictive value in structured algebras.

R1 only tracks task count, degree, density, or planning budget.

R1 is unstable across generator families.

pseudo-Omega cases are not distinguishable from proto-Omega cases.
```

Ambiguity:

```text
R1 works only in hand-seeded algebras.

R1 collapses to R0 broadly.

R2/R3 sidecars outperform R1 but are harder to interpret.

The generator produces too many low-resolution cases.
```

## 8. Roadmap Beyond VAL0

```text
VAL0-CT:
  single-field proto-Omega
  R1 predicts long-horizon reachability retention

VAL1-CT:
  coupled fields
  joint reachability and compatibility gap

VAL2:
  perturbation and recoverability
  R2 sidecar becomes primary

VAL3:
  embodied minimal valuers
  self-maintenance, boundary, repair, action channels

VAL4:
  multifield Omega
  compatibility, corridors, pseudo-Omega traps, re-entry
```

Each phase must define failure before scaling.
