# VAL0-CT 12h Unlabeled Geometry Battery

Diagnostic-only battery. Policies are frozen; geometry is measured after R1 and R0-lookahead choices.

## Config

```json
{
  "H": 16,
  "T": 32,
  "checkpoint_rows": 100,
  "geometry_samples": 32,
  "guardrail_seeds": 150,
  "h": [
    1,
    2
  ],
  "max_paths": 512,
  "max_runtime_seconds": 43200,
  "num_constructors": 2,
  "num_tasks": 64,
  "out": "results\\val0_ct\\20260520_12h_unlabeled_geometry_battery",
  "phase": "guardrails",
  "reentry_samples": 0,
  "run_id": "20260520_183756",
  "sample_size": 256,
  "sanity_seeds": 8,
  "status": "COMPLETED",
  "unlabeled_seeds": 2500,
  "workers": 18
}
```

## Aggregate

| phase | family | h | n | mean R1 advantage | R1 win rate | R1 LHR | R0-lookahead LHR | same choice | corridor d8 gap | variance | depth d16 gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| guardrails | brittle_peak | 1 | 150 | 0.188 | 0.513 | 0.380 | 0.192 | 0.460 | -1.840 | 0.000 | 6.040 |
| guardrails | brittle_peak | 2 | 150 | 0.511 | 0.913 | 0.711 | 0.200 | 0.113 | -5.447 | 1.789 | 9.960 |
| guardrails | low_resolution_dense | 1 | 150 | -0.004 | 0.080 | 0.530 | 0.534 | 0.593 | 0.000 | 0.640 | 0.053 |
| guardrails | low_resolution_dense | 2 | 150 | -0.001 | 0.093 | 0.535 | 0.535 | 0.213 | 0.000 | 0.937 | -0.040 |
| guardrails | structured_asymmetric_v2 | 1 | 150 | 0.096 | 0.473 | 0.413 | 0.316 | 0.460 | -3.587 | 0.000 | 5.653 |
| guardrails | structured_asymmetric_v2 | 2 | 150 | 0.437 | 0.933 | 0.733 | 0.296 | 0.127 | -7.653 | 1.655 | 10.027 |
| sanity | brittle_peak | 1 | 8 | 0.269 | 0.750 | 0.501 | 0.232 | 0.375 | -6.500 | 0.000 | 9.375 |
| sanity | brittle_peak | 2 | 8 | 0.547 | 1.000 | 0.757 | 0.210 | 0.000 | -10.875 | 1.166 | 14.125 |
| sanity | low_resolution_dense | 1 | 8 | -0.005 | 0.000 | 0.547 | 0.552 | 0.625 | 0.000 | 0.796 | -1.250 |
| sanity | low_resolution_dense | 2 | 8 | -0.000 | 0.250 | 0.547 | 0.547 | 0.375 | 0.000 | 1.234 | 0.125 |
| sanity | unlabeled_structural | 1 | 8 | -0.111 | 0.250 | 0.305 | 0.416 | 0.750 | 4.625 | 2.530 | -0.125 |
| sanity | unlabeled_structural | 2 | 8 | 0.058 | 0.125 | 0.410 | 0.352 | 0.250 | 3.500 | 4.665 | 1.125 |
| unlabeled_main | unlabeled_structural | 1 | 2500 | -0.067 | 0.180 | 0.378 | 0.445 | 0.623 | -0.043 | 3.111 | -0.278 |
| unlabeled_main | unlabeled_structural | 2 | 2500 | -0.033 | 0.278 | 0.435 | 0.467 | 0.533 | 0.090 | 5.054 | -0.016 |

## Unlabeled Highlights

- `geometry_gap_corridor_width_d8` q1 vs q5: mean R1 advantage -0.052 -> -0.055; win rate 0.220 -> 0.228.
- `candidate_future_R0_variance` q1 vs q5: mean R1 advantage -0.084 -> -0.036; win rate 0.172 -> 0.268.
- `geometry_gap_depth_profile_d16` q1 vs q5: mean R1 advantage -0.039 -> -0.050; win rate 0.245 -> 0.238.
- Best corridor x variance cell: scope h=2, corridor q4, variance q5, n=71, mean R1 advantage -0.002, win rate 0.408.

## Completion

- Rows completed: 5948
- Errors: 0
