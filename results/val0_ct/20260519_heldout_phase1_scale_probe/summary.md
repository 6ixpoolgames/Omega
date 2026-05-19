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
  "checkpoint_every": 50,
  "cpu_count": 24,
  "elapsed_seconds": 1400.5022193999903,
  "families": [
    "brittle_peak",
    "structured_asymmetric_v2",
    "low_resolution_dense",
    "cost_brittle",
    "delayed_robust",
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
  "max_runtime_seconds": 5400.0,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260519_142911",
  "sample_size": 256,
  "seed_counts": {
    "brittle_peak": 20,
    "cost_brittle": 20,
    "delayed_robust": 20,
    "low_resolution_dense": 20,
    "structured_asymmetric_v2": 20,
    "unlabeled_structural": 20
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
| brittle_peak | R0 | 0.467 | 0.000 | 0.000 |
| brittle_peak | R0_lookahead | 0.183 | 0.000 | 0.000 |
| brittle_peak | R1 | 0.551 | 0.000 | 0.000 |
| brittle_peak | pseudo_omega | 0.000 | 0.000 | 0.000 |
| brittle_peak | random | 0.081 | 0.000 | 0.000 |
| cost_brittle | R0 | 0.462 | 0.000 | 0.000 |
| cost_brittle | R0_lookahead | 0.662 | 0.000 | 0.000 |
| cost_brittle | R1 | 0.582 | 0.000 | 0.000 |
| cost_brittle | pseudo_omega | 0.261 | 0.000 | 0.000 |
| cost_brittle | random | 0.344 | 0.000 | 0.000 |
| delayed_robust | R0 | 0.536 | 0.000 | 0.000 |
| delayed_robust | R0_lookahead | 0.748 | 0.000 | 0.000 |
| delayed_robust | R1 | 0.620 | 0.000 | 0.000 |
| delayed_robust | pseudo_omega | 0.356 | 0.000 | 0.000 |
| delayed_robust | random | 0.371 | 0.000 | 0.000 |
| low_resolution_dense | R0 | 0.517 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.531 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.532 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.456 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.496 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0 | 0.471 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0_lookahead | 0.282 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R1 | 0.563 | 0.000 | 0.000 |
| structured_asymmetric_v2 | pseudo_omega | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | random | 0.098 | 0.000 | 0.000 |
| unlabeled_structural | R0 | 0.384 | 0.000 | 0.000 |
| unlabeled_structural | R0_lookahead | 0.428 | 0.000 | 0.000 |
| unlabeled_structural | R1 | 0.421 | 0.000 | 0.000 |
| unlabeled_structural | pseudo_omega | 0.037 | 0.000 | 0.000 |
| unlabeled_structural | random | 0.125 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.584 | -0.685 | 1.593 |
| brittle_peak | R0_lookahead | 0.367 | -0.585 | 1.527 |
| brittle_peak | R1 | 0.289 | -0.450 | 0.941 |
| brittle_peak | pseudo_omega | 0.408 | -0.474 | 0.409 |
| brittle_peak | random | 0.473 | -0.515 | 0.885 |
| cost_brittle | R0 | 0.370 | -0.326 | 0.184 |
| cost_brittle | R0_lookahead | 0.311 | -0.403 | 0.143 |
| cost_brittle | R1 | 0.185 | -0.252 | 0.230 |
| cost_brittle | pseudo_omega | 0.143 | -0.411 | 0.032 |
| cost_brittle | random | 0.242 | -0.374 | 0.096 |
| delayed_robust | R0 | 0.430 | -0.434 | 0.280 |
| delayed_robust | R0_lookahead | 0.323 | -0.460 | 0.338 |
| delayed_robust | R1 | 0.209 | -0.384 | 0.307 |
| delayed_robust | pseudo_omega | 0.161 | -0.505 | 0.097 |
| delayed_robust | random | 0.305 | -0.509 | 0.223 |
| low_resolution_dense | R0 | 0.406 | -0.406 | 0.273 |
| low_resolution_dense | R0_lookahead | 0.188 | -0.459 | 0.314 |
| low_resolution_dense | R1 | 0.149 | -0.447 | 0.255 |
| low_resolution_dense | pseudo_omega | 0.266 | -0.394 | 0.278 |
| low_resolution_dense | random | 0.387 | -0.432 | 0.319 |
| structured_asymmetric_v2 | R0 | 0.565 | -0.626 | 1.406 |
| structured_asymmetric_v2 | R0_lookahead | 0.319 | -0.586 | 1.310 |
| structured_asymmetric_v2 | R1 | 0.289 | -0.498 | 0.829 |
| structured_asymmetric_v2 | pseudo_omega | 0.401 | -0.475 | 0.419 |
| structured_asymmetric_v2 | random | 0.499 | -0.504 | 0.844 |
| unlabeled_structural | R0 | 0.482 | -0.797 | 2.526 |
| unlabeled_structural | R0_lookahead | 0.385 | -1.119 | 5.804 |
| unlabeled_structural | R1 | 0.353 | -0.856 | 4.996 |
| unlabeled_structural | pseudo_omega | 0.418 | -0.603 | 1.057 |
| unlabeled_structural | random | 0.473 | -0.745 | 2.508 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Scale-Readiness Read

This was a small Phase 1 held-out generalization probe, not the 12-hour run.

Runtime:

```text
rows: 1200
elapsed: 1400.5 seconds
throughput: ~0.86 rows / second
status: completed
```

Operational conclusion:

```text
The hardened runner is ready to scale into a 12-hour run.
```

At this observed throughput, a Phase 2 run in the 5,000-7,000 row range should
fit comfortably inside 12 hours with the runner's own checkpointing and
wall-clock controls.

Scientific read:

- Known positive anchors reproduced:
  - `brittle_peak`: R1 0.551 vs R0-lookahead 0.183.
  - `structured_asymmetric_v2`: R1 0.563 vs R0-lookahead 0.282.
- Negative control remained matched:
  - `low_resolution_dense`: R1 0.532 vs R0-lookahead 0.531.
- Held-out variants are mixed:
  - `cost_brittle`: R1 0.582 vs R0-lookahead 0.662; R1 only wins at `h=2`.
  - `delayed_robust`: R1 0.620 vs R0-lookahead 0.748; current generator is not producing the intended R1 advantage.
  - `unlabeled_structural`: R1 0.421 vs R0-lookahead 0.428 overall; R1 wins weakly at `h=2` but loses at `h=1`.

Recommendation:

```text
Do scale a 12-hour run, but do not spend it evenly across all held-out variants.
Prioritize anchors, low_resolution_dense, lock_in_seeded, and unlabeled_structural
with structural post-classification. Include smaller cost_brittle/delayed_robust
arms as generator-debug/calibration arms unless revised first.
```

Implementation caveat:

```text
cost_brittle is currently a structural proxy. The Task cost field is populated,
but R0/R1 are not yet budget-aware, so cost barriers are also encoded through
downstream obstruction/sinks. Do not interpret it as a completed cost-sensitive
reachability test.
```
