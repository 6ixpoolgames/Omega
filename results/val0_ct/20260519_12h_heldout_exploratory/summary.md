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
  "elapsed_seconds": 5477.017592499993,
  "families": [
    "unlabeled_structural",
    "cost_brittle",
    "delayed_robust",
    "low_resolution_dense",
    "lock_in_seeded",
    "brittle_peak",
    "structured_asymmetric_v2"
  ],
  "h": [
    1,
    2
  ],
  "job_order": "interleaved",
  "max_jobs": null,
  "max_paths": 512,
  "max_pending_multiplier": 1,
  "max_runtime_seconds": 42300.0,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260519_183945",
  "sample_size": 256,
  "seed_counts": {
    "brittle_peak": 40,
    "cost_brittle": 100,
    "delayed_robust": 100,
    "lock_in_seeded": 50,
    "low_resolution_dense": 50,
    "structured_asymmetric_v2": 40,
    "unlabeled_structural": 150
  },
  "seeds": 20,
  "shutdown_reserve_seconds": 900.0,
  "status": "completed",
  "store_steps": false,
  "workers": 18
}
```

## Policy Means

| family | policy | mean global LHR | mean local LHR | pseudo-Omega rate |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.461 | 0.000 | 0.000 |
| brittle_peak | R0_lookahead | 0.176 | 0.000 | 0.000 |
| brittle_peak | R1 | 0.547 | 0.000 | 0.000 |
| brittle_peak | pseudo_omega | 0.000 | 0.000 | 0.000 |
| brittle_peak | random | 0.057 | 0.000 | 0.000 |
| cost_brittle | R0 | 0.465 | 0.000 | 0.000 |
| cost_brittle | R0_lookahead | 0.664 | 0.000 | 0.000 |
| cost_brittle | R1 | 0.576 | 0.000 | 0.000 |
| cost_brittle | pseudo_omega | 0.259 | 0.000 | 0.000 |
| cost_brittle | random | 0.336 | 0.000 | 0.000 |
| delayed_robust | R0 | 0.527 | 0.000 | 0.000 |
| delayed_robust | R0_lookahead | 0.740 | 0.000 | 0.000 |
| delayed_robust | R1 | 0.614 | 0.000 | 0.000 |
| delayed_robust | pseudo_omega | 0.352 | 0.000 | 0.000 |
| delayed_robust | random | 0.369 | 0.000 | 0.000 |
| lock_in_seeded | R0 | 0.145 | 20.840 | 0.990 |
| lock_in_seeded | R0_lookahead | 0.450 | 11.810 | 0.980 |
| lock_in_seeded | R1 | 0.442 | 12.860 | 0.980 |
| lock_in_seeded | pseudo_omega | 0.000 | 22.400 | 1.000 |
| lock_in_seeded | random | 0.071 | 20.010 | 0.980 |
| low_resolution_dense | R0 | 0.517 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.535 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.534 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.461 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.496 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0 | 0.480 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0_lookahead | 0.277 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R1 | 0.571 | 0.000 | 0.000 |
| structured_asymmetric_v2 | pseudo_omega | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | random | 0.079 | 0.000 | 0.000 |
| unlabeled_structural | R0 | 0.369 | 0.000 | 0.000 |
| unlabeled_structural | R0_lookahead | 0.440 | 0.000 | 0.000 |
| unlabeled_structural | R1 | 0.398 | 0.000 | 0.000 |
| unlabeled_structural | pseudo_omega | 0.045 | 0.000 | 0.000 |
| unlabeled_structural | random | 0.100 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.599 | -0.694 | 1.636 |
| brittle_peak | R0_lookahead | 0.359 | -0.591 | 1.536 |
| brittle_peak | R1 | 0.290 | -0.491 | 0.980 |
| brittle_peak | pseudo_omega | 0.384 | -0.477 | 0.415 |
| brittle_peak | random | 0.494 | -0.519 | 0.894 |
| cost_brittle | R0 | 0.397 | -0.321 | 0.174 |
| cost_brittle | R0_lookahead | 0.292 | -0.387 | 0.139 |
| cost_brittle | R1 | 0.201 | -0.256 | 0.209 |
| cost_brittle | pseudo_omega | 0.122 | -0.413 | 0.029 |
| cost_brittle | random | 0.233 | -0.374 | 0.094 |
| delayed_robust | R0 | 0.439 | -0.433 | 0.266 |
| delayed_robust | R0_lookahead | 0.318 | -0.449 | 0.321 |
| delayed_robust | R1 | 0.219 | -0.385 | 0.300 |
| delayed_robust | pseudo_omega | 0.167 | -0.505 | 0.094 |
| delayed_robust | random | 0.286 | -0.503 | 0.227 |
| lock_in_seeded | R0 | 0.308 | -0.748 | 2.651 |
| lock_in_seeded | R0_lookahead | 0.296 | -0.965 | 8.183 |
| lock_in_seeded | R1 | 0.226 | -0.754 | 5.758 |
| lock_in_seeded | pseudo_omega | 0.314 | -0.519 | 1.129 |
| lock_in_seeded | random | 0.311 | -0.710 | 3.462 |
| low_resolution_dense | R0 | 0.387 | -0.418 | 0.273 |
| low_resolution_dense | R0_lookahead | 0.183 | -0.469 | 0.333 |
| low_resolution_dense | R1 | 0.153 | -0.446 | 0.285 |
| low_resolution_dense | pseudo_omega | 0.287 | -0.387 | 0.282 |
| low_resolution_dense | random | 0.378 | -0.428 | 0.327 |
| structured_asymmetric_v2 | R0 | 0.559 | -0.626 | 1.411 |
| structured_asymmetric_v2 | R0_lookahead | 0.316 | -0.601 | 1.464 |
| structured_asymmetric_v2 | R1 | 0.296 | -0.493 | 0.865 |
| structured_asymmetric_v2 | pseudo_omega | 0.385 | -0.477 | 0.390 |
| structured_asymmetric_v2 | random | 0.461 | -0.512 | 0.872 |
| unlabeled_structural | R0 | 0.485 | -0.774 | 2.346 |
| unlabeled_structural | R0_lookahead | 0.409 | -0.989 | 4.581 |
| unlabeled_structural | R1 | 0.346 | -0.811 | 3.883 |
| unlabeled_structural | pseudo_omega | 0.415 | -0.539 | 0.860 |
| unlabeled_structural | random | 0.478 | -0.695 | 2.211 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Exploratory Read

This run completed normally and produced 5,300 rows inside the 12-hour budget.

Primary result:

- Calibration anchors reproduced:
  - `brittle_peak`: R1 0.547 vs R0-lookahead 0.176.
  - `structured_asymmetric_v2`: R1 0.571 vs R0-lookahead 0.277.
- Low-resolution control remained matched:
  - `low_resolution_dense`: R1 0.534 vs R0-lookahead 0.535.
- Lock-in control replicated:
  - `pseudo_omega`: global LHR 0.000, local LHR 22.400, pseudo-Omega flag 1.000.
- Held-out families did not produce a broad R1 win:
  - `cost_brittle`: R1 0.576 vs R0-lookahead 0.664.
  - `delayed_robust`: R1 0.614 vs R0-lookahead 0.740.
  - `unlabeled_structural`: R1 0.398 vs R0-lookahead 0.440.

Interpretation:

```text
The current R1 signal remains strong in the designed calibration families, but
does not yet generalize cleanly across the current held-out generators.
```

Useful hooks:

- `cost_brittle` and `delayed_robust` look more like generator-debug surfaces
  than positive held-out variants in their current form.
- `unlabeled_structural` is the most important future hook because it is not
  hand-labeled brittle/robust and shows high candidate variance.
- Post-hoc variance bins suggest that R1 approaches parity as candidate
  variance rises, but does not reliably beat R0-lookahead.

Decision:

```text
Do not claim held-out generalization yet. The next useful probe should focus on
unlabeled structural regimes and post-hoc peak-retention classification rather
than adding more named brittle/robust generators.
```
