# VAL0-G Neutral Grammar Geometry Smoke

Geometry-first smoke. This run does not test full Omega and does not tune R1.

## Config

```json
{
  "cut_samples": 4,
  "guardrail_seeds": 50,
  "max_runtime_seconds": 3600,
  "max_states_per_depth": 2048,
  "neutral_seeds": 250,
  "num_tasks": 64,
  "out": "results\\val0_g\\20260521_neutral_grammar_stability_probe_cap2048",
  "rollout_samples": 128,
  "run_id": "20260521_131149",
  "signature_modes": [
    "coarse",
    "full"
  ],
  "status": "COMPLETED",
  "workers": 18
}
```

## Family Aggregate

| family | n | survival AUC | mass d16 | mass d32 | P terminal d16 | P terminal d32 | initial cut | downstream cut | cap d16 | cap d32 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 100 | 605.394 | 2048.000 | 2045.760 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.990 |
| low_resolution_dense | 100 | 55.162 | 2048.000 | 2048.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| neutral_grammar_v1 | 500 | 286.230 | 1415.658 | 1080.990 | 0.369 | 0.650 | 0.547 | 0.673 | 0.676 | 0.500 |

## Neutral Bins

| neutral bin | n | survival AUC | mass d16 | P terminal d16 | downstream cut | cap d16 |
|---|---:|---:|---:|---:|---:|---:|
| depth_persistent_bin | 4 | 540.875 | 2048.000 | 0.262 | 1.000 | 1.000 |
| high_branching_low_terminal_bin | 7 | 320.886 | 1875.857 | 0.150 | 0.794 | 0.857 |
| high_mass_high_cut_bin | 490 | 389.502 | 2048.000 | 0.009 | 0.997 | 1.000 |
| high_mass_low_cut_bin | 11 | 69.526 | 781.000 | 0.257 | 0.173 | 0.182 |
| high_terminal_bin | 170 | 29.347 | 277.241 | 0.973 | 0.116 | 0.106 |
| mixed_or_noise_bin | 18 | 452.830 | 2048.000 | 0.533 | 0.932 | 1.000 |

## Post-Hoc Geometry Classes

| class | n | survival AUC | mass d16 | P terminal d16 | cut k1 |
|---|---:|---:|---:|---:|---:|
| deep_corridor_like | 4 | 540.875 | 2048.000 | 0.262 | 1.000 |
| lush_branching_like | 7 | 320.886 | 1875.857 | 0.150 | 0.794 |
| mixed_or_noise | 18 | 452.830 | 2048.000 | 0.533 | 0.932 |
| recoverable_basin_like | 490 | 389.502 | 2048.000 | 0.009 | 0.997 |
| self_terminating | 170 | 29.347 | 277.241 | 0.973 | 0.116 |
| thin_ridge | 11 | 69.526 | 781.000 | 0.257 | 0.173 |

## Signature Agreement

| family | same class | same neutral bin | rel mass d16 diff | rel survival AUC diff | rel downstream cut diff |
|---|---:|---:|---:|---:|---:|
| brittle_peak | 1.000 | 1.000 | 0.000 | -0.001 | 0.000 |
| low_resolution_dense | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| neutral_grammar_v1 | 0.996 | 0.996 | -0.003 | -0.000 | 0.001 |

## Smoke Read

- Neutral classes observed: deep_corridor_like, lush_branching_like, mixed_or_noise, recoverable_basin_like, self_terminating, thin_ridge.
- Rows completed: 700.
- Errors: 0.
