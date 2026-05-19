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
  "elapsed_seconds": 1955.4409175999754,
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
  "run_id": "20260519_130105",
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
| brittle_peak | R0 | 0.478 | 0.000 | 0.000 |
| brittle_peak | R0_lookahead | 0.189 | 0.000 | 0.000 |
| brittle_peak | R1 | 0.539 | 0.000 | 0.000 |
| brittle_peak | pseudo_omega | 0.000 | 0.000 | 0.000 |
| brittle_peak | random | 0.052 | 0.000 | 0.000 |
| lock_in_seeded | R0 | 0.163 | 20.663 | 0.988 |
| lock_in_seeded | R0_lookahead | 0.460 | 11.575 | 0.975 |
| lock_in_seeded | R1 | 0.456 | 12.387 | 0.975 |
| lock_in_seeded | pseudo_omega | 0.000 | 22.400 | 1.000 |
| lock_in_seeded | random | 0.067 | 20.413 | 0.988 |
| low_resolution_dense | R0 | 0.516 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.535 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.534 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.462 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.500 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0 | 0.484 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0_lookahead | 0.289 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R1 | 0.577 | 0.000 | 0.000 |
| structured_asymmetric_v2 | pseudo_omega | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | random | 0.072 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.593 | -0.750 | 1.836 |
| brittle_peak | R0_lookahead | 0.355 | -0.631 | 1.786 |
| brittle_peak | R1 | 0.293 | -0.533 | 1.054 |
| brittle_peak | pseudo_omega | 0.382 | -0.499 | 0.513 |
| brittle_peak | random | 0.475 | -0.545 | 0.940 |
| lock_in_seeded | R0 | 0.295 | -0.746 | 2.737 |
| lock_in_seeded | R0_lookahead | 0.294 | -0.931 | 7.846 |
| lock_in_seeded | R1 | 0.227 | -0.743 | 5.543 |
| lock_in_seeded | pseudo_omega | 0.304 | -0.517 | 1.104 |
| lock_in_seeded | random | 0.307 | -0.705 | 3.346 |
| low_resolution_dense | R0 | 0.392 | -0.415 | 0.271 |
| low_resolution_dense | R0_lookahead | 0.186 | -0.461 | 0.307 |
| low_resolution_dense | R1 | 0.149 | -0.440 | 0.250 |
| low_resolution_dense | pseudo_omega | 0.284 | -0.380 | 0.257 |
| low_resolution_dense | random | 0.386 | -0.428 | 0.317 |
| structured_asymmetric_v2 | R0 | 0.543 | -0.673 | 1.487 |
| structured_asymmetric_v2 | R0_lookahead | 0.317 | -0.610 | 1.542 |
| structured_asymmetric_v2 | R1 | 0.302 | -0.530 | 0.882 |
| structured_asymmetric_v2 | pseudo_omega | 0.380 | -0.491 | 0.417 |
| structured_asymmetric_v2 | random | 0.474 | -0.520 | 0.838 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Primary Read

This targeted confirmation run increased continuation horizon while keeping the
rollout horizon inside the generator's nonterminal depth:

```text
H = 16
T = 32
h = 1, 2
```

The R1/R0-lookahead separation survives and strengthens:

- `brittle_peak`: R1 mean global LHR 0.539 vs R0-lookahead 0.189.
- `structured_asymmetric_v2`: R1 mean global LHR 0.577 vs R0-lookahead 0.289.
- `low_resolution_dense`: R1 mean global LHR 0.534 vs R0-lookahead 0.535, effectively matched.
- `lock_in_seeded`: pseudo-Omega retained the local/global destructive-lock-in diagnostic.

Band-level read:

- `brittle_peak`, `h=1`: R1 0.360 vs R0-lookahead 0.190.
- `brittle_peak`, `h=2`: R1 0.719 vs R0-lookahead 0.188.
- `structured_asymmetric_v2`, `h=1`: R1 0.412 vs R0-lookahead 0.313.
- `structured_asymmetric_v2`, `h=2`: R1 0.742 vs R0-lookahead 0.265.

Interpretation:

```text
This is the strongest current VAL0-CT calibration evidence that robust
future-preserving reachability can outperform equal-budget greedy peak
reachability in generated brittle/robust task algebras.
```

It remains calibration evidence, not full Omega validation.
