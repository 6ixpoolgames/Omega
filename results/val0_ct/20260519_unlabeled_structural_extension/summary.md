# VAL0-CT Smoke Summary

This is a harness and workflow validation run for the VAL0-CT constructor task algebra probe.
It is not evidence for full Omega.

## Config

```json
{
  "H": [
    16
  ],
  "T": [
    32
  ],
  "checkpoint_every": 100,
  "cpu_count": 24,
  "elapsed_seconds": 1682.511395599984,
  "families": [
    "unlabeled_structural"
  ],
  "h": [
    1,
    2
  ],
  "job_order": "interleaved",
  "max_jobs": null,
  "max_paths": 512,
  "max_pending_multiplier": 1,
  "max_runtime_seconds": 10800.0,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260519_201205",
  "sample_size": 256,
  "seed_counts": {
    "unlabeled_structural": 300
  },
  "seeds": 20,
  "shutdown_reserve_seconds": 600.0,
  "status": "completed",
  "store_steps": false,
  "workers": 18
}
```

## Policy Means

| family | policy | mean global LHR | mean local LHR | pseudo-Omega rate |
|---|---:|---:|---:|---:|
| unlabeled_structural | R0 | 0.370 | 0.000 | 0.000 |
| unlabeled_structural | R0_lookahead | 0.449 | 0.000 | 0.000 |
| unlabeled_structural | R1 | 0.405 | 0.000 | 0.000 |
| unlabeled_structural | pseudo_omega | 0.043 | 0.000 | 0.000 |
| unlabeled_structural | random | 0.101 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| unlabeled_structural | R0 | 0.490 | -0.774 | 2.265 |
| unlabeled_structural | R0_lookahead | 0.405 | -0.971 | 4.473 |
| unlabeled_structural | R1 | 0.349 | -0.793 | 3.814 |
| unlabeled_structural | pseudo_omega | 0.406 | -0.561 | 0.929 |
| unlabeled_structural | random | 0.491 | -0.710 | 2.337 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Primary Read

This extension focused only on `unlabeled_structural` because it is the most
important anti-overfit surface from the held-out exploratory spec.

Result:

- `h = 1`: R1 remains below R0-lookahead on mean global LHR.
- `h = 2`: R1 moves closer to parity, but still does not produce a clean mean win.

Combined with the main exploratory run, higher candidate variance improves R1's
relative position:

```text
highest candidate-variance quintiles:
  h = 1 mean R1 advantage = -0.027, win rate = 0.309
  h = 2 mean R1 advantage = -0.006, win rate = 0.346
```

Interpretation:

```text
Candidate variance is a real hook, but not enough by itself. The next useful
unlabeled probe should classify regimes by peak-retention gap and terminal-depth
structure, then ask whether R1 advantage appears specifically there.
```
