# VAL0-CT Smoke Summary

This is a harness and workflow validation run for the VAL0-CT constructor task algebra probe.
It is not evidence for full Omega.

## Config

```json
{
  "H": [
    4,
    8
  ],
  "T": [
    16,
    32
  ],
  "checkpoint_every": 100,
  "cpu_count": 24,
  "elapsed_seconds": 16181.90018869999,
  "families": [
    "brittle_peak",
    "structured_asymmetric_v2",
    "lock_in_seeded",
    "low_resolution_dense"
  ],
  "h": [
    1,
    2,
    4
  ],
  "job_order": "interleaved",
  "max_jobs": null,
  "max_paths": 512,
  "max_pending_multiplier": 1,
  "max_runtime_seconds": 28800.0,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260518_223209",
  "sample_size": 256,
  "seed_counts": {
    "brittle_peak": 150,
    "lock_in_seeded": 50,
    "low_resolution_dense": 50,
    "structured_asymmetric_v2": 100
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
| brittle_peak | R0 | 0.411 | 0.000 | 0.000 |
| brittle_peak | R0_lookahead | 0.383 | 0.000 | 0.000 |
| brittle_peak | R1 | 0.471 | 0.000 | 0.000 |
| brittle_peak | pseudo_omega | 0.053 | 0.000 | 0.000 |
| brittle_peak | random | 0.184 | 0.000 | 0.000 |
| lock_in_seeded | R0 | 0.441 | 18.297 | 0.805 |
| lock_in_seeded | R0_lookahead | 0.705 | 11.935 | 0.543 |
| lock_in_seeded | R1 | 0.693 | 12.832 | 0.583 |
| lock_in_seeded | pseudo_omega | 0.213 | 22.190 | 1.000 |
| lock_in_seeded | random | 0.387 | 16.172 | 0.812 |
| low_resolution_dense | R0 | 0.708 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.718 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.717 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.599 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.671 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0 | 0.426 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R0_lookahead | 0.432 | 0.000 | 0.000 |
| structured_asymmetric_v2 | R1 | 0.496 | 0.000 | 0.000 |
| structured_asymmetric_v2 | pseudo_omega | 0.083 | 0.000 | 0.000 |
| structured_asymmetric_v2 | random | 0.223 | 0.000 | 0.000 |

## R1 / R0-Lookahead Diagnostics

| family | policy | same-choice rate | score gap | candidate variance |
|---|---:|---:|---:|---:|
| brittle_peak | R0 | 0.608 | -2.225 | 6.211 |
| brittle_peak | R0_lookahead | 0.605 | -2.107 | 6.510 |
| brittle_peak | R1 | 0.554 | -1.902 | 5.687 |
| brittle_peak | pseudo_omega | 0.471 | -1.515 | 1.716 |
| brittle_peak | random | 0.596 | -1.942 | 4.155 |
| lock_in_seeded | R0 | 0.531 | -1.909 | 2.634 |
| lock_in_seeded | R0_lookahead | 0.593 | -2.263 | 5.797 |
| lock_in_seeded | R1 | 0.581 | -2.157 | 5.042 |
| lock_in_seeded | pseudo_omega | 0.536 | -1.291 | 1.019 |
| lock_in_seeded | random | 0.568 | -1.979 | 3.652 |
| low_resolution_dense | R0 | 0.576 | -1.113 | 0.618 |
| low_resolution_dense | R0_lookahead | 0.516 | -1.126 | 0.716 |
| low_resolution_dense | R1 | 0.494 | -1.109 | 0.669 |
| low_resolution_dense | pseudo_omega | 0.588 | -1.028 | 0.623 |
| low_resolution_dense | random | 0.599 | -1.121 | 0.710 |
| structured_asymmetric_v2 | R0 | 0.622 | -2.143 | 5.348 |
| structured_asymmetric_v2 | R0_lookahead | 0.614 | -2.043 | 5.710 |
| structured_asymmetric_v2 | R1 | 0.564 | -1.868 | 4.710 |
| structured_asymmetric_v2 | pseudo_omega | 0.486 | -1.485 | 1.528 |
| structured_asymmetric_v2 | random | 0.619 | -1.908 | 3.667 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Primary Read

This run completed normally and produced 21,000 condition rows.

The main calibration result is positive but scoped:

- `brittle_peak`: R1 mean global LHR 0.471 vs R0-lookahead 0.383.
- `structured_asymmetric_v2`: R1 mean global LHR 0.496 vs R0-lookahead 0.432.
- `low_resolution_dense`: R1 and R0-lookahead remained matched, as expected for the low-resolution control.
- `lock_in_seeded`: pseudo-Omega again produced low global LHR, high local LHR, and a 1.000 pseudo-Omega flag rate.

The separation is horizon-dependent:

- R1 advantage appears mainly at `h = 1` and `h = 2`.
- At `h = 4`, same-choice rates rise and the R1/R0-lookahead difference mostly collapses.

Interpretation:

```text
This is evidence that the current R1 selector can differ from equal-budget
greedy peak reachability in generated brittle/robust task algebras.
It is not evidence for full Omega.
```

The `h = 4` collapse is important. It suggests the separation is not a generic
R1 advantage; it appears when the near-term candidate horizon is short enough
that greedy peak and robust retention remain behaviorally distinct.
