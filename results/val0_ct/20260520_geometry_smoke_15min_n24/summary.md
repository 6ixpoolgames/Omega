# VAL0-CT Reachable-Neighborhood Geometry Smoke

Diagnostic-only sidecar. Policies are frozen; geometry is measured after R1 and R0-lookahead choices.

## Config

```json
{
  "H": 16,
  "T": 32,
  "families": [
    "brittle_peak",
    "structured_asymmetric_v2",
    "low_resolution_dense",
    "unlabeled_structural"
  ],
  "geometry_samples": 32,
  "h": [
    1,
    2
  ],
  "max_paths": 512,
  "max_runtime_seconds": 900,
  "num_constructors": 2,
  "num_tasks": 64,
  "out": "results\\val0_ct\\20260520_geometry_smoke_15min_n24",
  "reentry_samples": 3,
  "run_id": "20260520_180404",
  "sample_size": 256,
  "seeds": 24,
  "status": "COMPLETED",
  "workers": 18
}
```

## Aggregate

| family | h | n | mean R1 advantage | same choice | terminal gap | d16 gap | corridor d8 gap | corridor d16 gap | re-entry gap | corr(term,R1adv) | corr(reentry,R1adv) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 1 | 24 | 0.319 | 0.417 | 0.000 | 7.833 | -0.292 | 6.958 | -0.102 | 0.000 | -0.012 |
| brittle_peak | 2 | 24 | 0.555 | 0.042 | 0.000 | 13.708 | -3.583 | 10.167 | -0.196 | 0.000 | 0.178 |
| low_resolution_dense | 1 | 24 | -0.003 | 0.542 | 0.000 | -1.208 | 0.000 | 0.000 | 0.000 | 0.000 | -0.033 |
| low_resolution_dense | 2 | 24 | 0.002 | 0.250 | 0.000 | 0.417 | 0.000 | 0.000 | 0.003 | 0.000 | 0.121 |
| structured_asymmetric_v2 | 1 | 24 | 0.215 | 0.417 | 0.000 | 7.042 | -1.875 | -0.417 | -0.119 | 0.000 | 0.043 |
| structured_asymmetric_v2 | 2 | 24 | 0.473 | 0.083 | 0.000 | 12.792 | -6.167 | 1.542 | -0.189 | 0.000 | -0.444 |
| unlabeled_structural | 1 | 24 | -0.038 | 0.750 | 0.000 | -0.333 | 2.500 | -6.208 | -0.025 | 0.000 | -0.198 |
| unlabeled_structural | 2 | 24 | 0.034 | 0.417 | 0.000 | -0.500 | 2.792 | -1.333 | -0.017 | 0.000 | 0.271 |

## Smoke Interpretation

- Minimal success: non-degenerate geometry, anchor R1 advantage preserved, dense control not spuriously separated.
- Stronger success: positive anchor families show positive geometry gaps for R1-selected states.
- Best smoke signal: unlabeled structural rows show geometry gaps that move with R1 advantage.
- Correlations are exploratory at this sample size.

## Completion

- Rows completed: 192
- Errors: 0
