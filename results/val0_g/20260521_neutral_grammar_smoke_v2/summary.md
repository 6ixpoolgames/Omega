# VAL0-G Neutral Grammar Geometry Smoke

Geometry-first smoke. This run does not test full Omega and does not tune R1.

## Config

```json
{
  "cut_samples": 4,
  "guardrail_seeds": 12,
  "max_runtime_seconds": 1800,
  "max_states_per_depth": 512,
  "neutral_seeds": 50,
  "num_tasks": 64,
  "out": "results\\val0_g\\20260521_neutral_grammar_smoke_v2",
  "rollout_samples": 128,
  "run_id": "20260521_125819",
  "status": "COMPLETED",
  "workers": 18
}
```

## Family Aggregate

| family | n | survival AUC | slope | mass d16 | P terminal d16 | cut k1 | B8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 12 | 156.000 | 34.000 | 512.000 | 0.000 | 1.000 | 1.000 |
| low_resolution_dense | 12 | 14.997 | 32.400 | 512.000 | 0.000 | 1.000 | 1.000 |
| neutral_grammar_v1 | 50 | 74.961 | 24.697 | 373.640 | 0.339 | 0.585 | 1.450 |

## Post-Hoc Geometry Classes

| class | n | survival AUC | mass d16 | P terminal d16 | cut k1 |
|---|---:|---:|---:|---:|---:|
| deep_corridor_like | 14 | 24.924 | 512.000 | 0.002 | 0.940 |
| recoverable_basin_like | 38 | 107.545 | 512.000 | 0.010 | 1.000 |
| self_terminating | 16 | 11.873 | 79.625 | 0.979 | 0.131 |
| thin_ridge | 6 | 195.733 | 512.000 | 0.150 | 0.000 |

## Smoke Read

- Neutral classes observed: deep_corridor_like, recoverable_basin_like, self_terminating, thin_ridge.
- Rows completed: 74.
- Errors: 0.
