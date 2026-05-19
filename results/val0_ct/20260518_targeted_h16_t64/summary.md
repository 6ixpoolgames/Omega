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
    64
  ],
  "checkpoint_every": 100,
  "cpu_count": 24,
  "elapsed_seconds": 2260.6538248000143,
  "families": [
    "brittle_peak",
    "structured_asymmetric_v2",
    "lock_in_seeded",
    "low_resolution_dense"
  ],
  "h": [
    1,
    2
  ],
  "job_order": "interleaved",
  "max_jobs": null,
  "max_paths": 512,
  "max_pending_multiplier": 1,
  "max_runtime_seconds": 14400.0,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260519_122257",
  "sample_size": 256,
  "seed_counts": {
    "brittle_peak": 100,
    "lock_in_seeded": 40,
    "low_resolution_dense": 30,
    "structured_asymmetric_v2": 80
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
| brittle_peak | R0 | 0.000 | 0.000 | 0.000 |
| brittle_peak | R0_lookahead | 0.000 | 0.000 | 0.000 |
| brittle_peak | R1 | 0.000 | 0.000 | 0.000 |
| brittle_peak | pseudo_omega | 0.000 | 0.000 | 0.000 |
| brittle_peak | random | 0.000 | 0.000 | 0.000 |
| lock_in_seeded | R0 | 0.000 | 21.900 | 0.988 |
| lock_in_seeded | R0_lookahead | 0.000 | 20.688 | 1.000 |
| lock_in_seeded | R1 | 0.000 | 20.475 | 1.000 |
| lock_in_seeded | pseudo_omega | 0.000 | 22.400 | 1.000 |
| lock_in_seeded | random | 0.000 | 20.212 | 0.950 |
| low_resolution_dense | R0 | 0.000 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.000 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.000 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.000 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0 | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0_lookahead | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R1 | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | pseudo_omega | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | random | 0.000 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.572 | -0.689 | 1.462 |
| brittle_peak | R0_lookahead | 0.384 | -0.597 | 1.610 |
| brittle_peak | R1 | 0.324 | -0.480 | 0.824 |
| brittle_peak | pseudo_omega | 0.393 | -0.499 | 0.513 |
| brittle_peak | random | 0.486 | -0.524 | 0.924 |
| lock_in_seeded | R0 | 0.329 | -0.664 | 2.123 |
| lock_in_seeded | R0_lookahead | 0.293 | -0.746 | 5.216 |
| lock_in_seeded | R1 | 0.273 | -0.617 | 3.636 |
| lock_in_seeded | pseudo_omega | 0.303 | -0.517 | 1.104 |
| lock_in_seeded | random | 0.338 | -0.665 | 2.848 |
| low_resolution_dense | R0 | 0.349 | -0.412 | 0.210 |
| low_resolution_dense | R0_lookahead | 0.183 | -0.442 | 0.216 |
| low_resolution_dense | R1 | 0.157 | -0.424 | 0.182 |
| low_resolution_dense | pseudo_omega | 0.256 | -0.392 | 0.168 |
| low_resolution_dense | random | 0.303 | -0.410 | 0.223 |
| structured_asymmetric_v2 | R0 | 0.541 | -0.634 | 1.205 |
| structured_asymmetric_v2 | R0_lookahead | 0.362 | -0.573 | 1.351 |
| structured_asymmetric_v2 | R1 | 0.320 | -0.479 | 0.678 |
| structured_asymmetric_v2 | pseudo_omega | 0.390 | -0.491 | 0.417 |
| structured_asymmetric_v2 | random | 0.488 | -0.511 | 0.803 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Primary Read

This targeted harder-horizon run completed normally, but it is over-hard for
the current generators:

```text
H = 16
T = 64
```

Global LHR collapsed to zero for every family and policy. This means the run is
not useful for comparing R1 against R0-lookahead on retained reachability. It is
useful as a boundary result: `T = 64` is beyond the current generator depth for
the present 64-task algebras.

Decision:

```text
Treat this as a collapse-boundary diagnostic, not as negative evidence against
R1. Use shorter rollout or deeper generators before retesting T = 64.
```
