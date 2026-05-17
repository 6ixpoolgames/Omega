# VAL0-CT Runbook

Operational notes for generating VAL0-CT runs

## Purpose

This runbook contains the technical run-generation details that should not live in the public-facing README.

The public README explains the theory, alignment relevance, current validation target, and reading path. This file explains how to run the current probe.

The canonical implementation design remains:

```text
docs/research_notes/validation_design/val0_ct_implementation_spec.md
```

## Current smoke target

Implement the VAL0-CT smoke target CPU-first.

Initial generator families:

```text
low_resolution_dense
structured_asymmetric
lock_in_seeded
```

Initial policies:

```text
random
R0
R0_lookahead
R1
pseudo_omega
```

Primary comparison:

```text
R1 vs R0 vs equal-budget R0_lookahead
on long-horizon reachability retention
```

Important methodological constraints:

```text
R1 must not use max future reachability as its primary selector.
R1 uses robust future-reachability retention.
R0-lookahead gets the same planning budget as R1.
R1 ≈ R0 in low-resolution algebras is diagnostic, not automatic failure.
```

## CPU-first stance

VAL0-CT should start CPU-first.

Reason:

```text
task-graph traversal is easier to inspect on CPU
R0/R1 bugs are easier to debug with deterministic CPU code
batch parallelism over seeds/families/policies/horizons is enough for smoke runs
GPU support would add complexity before the workload shape is known
```

GPU support is deferred until smoke runs show a real dense batched reachability bottleneck.

## Environment

Use the local virtual environment directly when working on the original machine:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

For CPU-heavy probes, the calibrated default on the original machine is:

```text
18 worker processes
```

For older GPU/CuPy work on the original machine, use `omega_env.bat` or run `omega_env.ps1` with a PowerShell execution-policy bypass. The environment scripts add Torch's bundled CUDA 13 NVRTC DLL directory to `PATH` and point CuPy's kernel cache at `.cupy-cache/`.

This GPU/CuPy setup is historical and should not be needed for VAL0-CT smoke runs.

## Output locations

Future VAL0-CT outputs should live under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Use:

```text
results/local_runs/
```

for ignored smoke, calibration, stress, or scratch outputs.

Do not add new root-level `*_results` folders.

## Recommended implementation order

Follow the implementation spec order:

```text
1. algebra.py + reachability.py
   get R0 correct on toy graphs before implementing R1

2. deterministic hand-built R0 tests
   verify BFS/path traversal, obstruction handling, and cost constraints

3. generators.py: low_resolution_dense
   verify too_dense / flat_asymmetry diagnostics

4. reachability.py: R1
   implement R1_mean_future_R0 selector and thresholded aggregates

5. policies.py
   implement random, R0, R0_lookahead, R1 in that order
   verify R0_lookahead and R1 can diverge on a hand-built case

6. generators.py: structured_asymmetric + lock_in_seeded

7. simulation.py + run_smoke.py

8. summarize.py + diagnostics.py
```

Do not implement `mixed` or `noise_branching` until the first three generator families are clean.

## Minimal smoke configuration

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
  h ∈ {1, 2, 4}
  H ∈ {4, 8}
  T ∈ {16, 32}

R1 sample size:
  N = 256 candidate paths

R1 threshold:
  primary = 0.50 * R0_initial
```

Optional second smoke:

```text
add:
  low_resolution_sparse
  noise_branching
  mixed
  persistence
  empowerment_like
  R2 sidecar
  R1 threshold sensitivity at 0.25 and 0.75
  R1 sample size N = 512
```

## Expected output files

Each run directory should contain:

```text
config.json
results.jsonl
aggregate.csv
summary.md
```

Optional later additions:

```text
plots/
figures/
diagnostics.json
```

## Interpretation checks

Pre-register these interpretations before looking at results:

```text
R1 > R0/R0-lookahead in structured algebras:
  promising proto-Omega signal

R1 ≈ R0 in low-resolution algebras:
  expected diagnostic

R1 ≈ R0 everywhere:
  generator lacks relevant asymmetry/resolution or R1 is too weak

R0-lookahead > R1 in structured algebras:
  R1 likely misspecified or outcome is pure reachability

pseudo-Omega local rises while global falls:
  local/global divergence diagnostic confirmed
```

## What not to add yet

Do not add these to the first smoke:

```text
lineage / successor constructors
multi-field coupling
corridors
epistemic correction
parallel task composition
scale composition
embodied substrate instantiation
full lushness metric
GPU acceleration
```

The first implementation should test one thing:

> In constructor-style task algebras, does future-preserving reachability behave differently from raw reachability when the algebra has enough asymmetry and temporal depth?
