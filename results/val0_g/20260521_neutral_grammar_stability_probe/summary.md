# VAL0-G Neutral Grammar Geometry Smoke

Geometry-first smoke. This run does not test full Omega and does not tune R1.

## Config

```json
{
  "cut_samples": 4,
  "guardrail_seeds": 50,
  "max_runtime_seconds": 3600,
  "max_states_per_depth": 512,
  "neutral_seeds": 250,
  "num_tasks": 64,
  "out": "results\\val0_g\\20260521_neutral_grammar_stability_probe",
  "rollout_samples": 128,
  "run_id": "20260521_131034",
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
| brittle_peak | 100 | 172.412 | 512.000 | 508.940 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.990 |
| low_resolution_dense | 100 | 15.778 | 512.000 | 512.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| neutral_grammar_v1 | 500 | 81.285 | 358.238 | 260.066 | 0.369 | 0.650 | 0.553 | 0.680 | 0.684 | 0.478 |

## Neutral Bins

| neutral bin | n | survival AUC | mass d16 | P terminal d16 | downstream cut | cap d16 |
|---|---:|---:|---:|---:|---:|---:|
| depth_persistent_bin | 108 | 25.908 | 512.000 | 0.014 | 0.995 | 1.000 |
| high_branching_low_terminal_bin | 3 | 78.139 | 512.000 | 0.182 | 0.697 | 1.000 |
| high_mass_high_cut_bin | 391 | 132.592 | 511.959 | 0.012 | 0.998 | 0.997 |
| high_mass_low_cut_bin | 10 | 31.442 | 299.600 | 0.266 | 0.159 | 0.300 |
| high_terminal_bin | 170 | 10.399 | 72.347 | 0.973 | 0.126 | 0.118 |
| mixed_or_noise_bin | 18 | 139.062 | 512.000 | 0.533 | 0.972 | 1.000 |

## Post-Hoc Geometry Classes

| class | n | survival AUC | mass d16 | P terminal d16 | cut k1 |
|---|---:|---:|---:|---:|---:|
| deep_corridor_like | 108 | 25.908 | 512.000 | 0.014 | 0.995 |
| lush_branching_like | 3 | 78.139 | 512.000 | 0.182 | 0.697 |
| mixed_or_noise | 18 | 139.062 | 512.000 | 0.533 | 0.972 |
| recoverable_basin_like | 391 | 132.592 | 511.959 | 0.012 | 0.998 |
| self_terminating | 170 | 10.399 | 72.347 | 0.973 | 0.126 |
| thin_ridge | 10 | 31.442 | 299.600 | 0.266 | 0.159 |

## Signature Agreement

| family | same class | same neutral bin | rel mass d16 diff | rel survival AUC diff | rel downstream cut diff |
|---|---:|---:|---:|---:|---:|
| brittle_peak | 1.000 | 1.000 | 0.000 | 0.003 | 0.000 |
| low_resolution_dense | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| neutral_grammar_v1 | 0.996 | 0.996 | -0.001 | -0.000 | 0.001 |

## Smoke Read

- Neutral classes observed: deep_corridor_like, lush_branching_like, mixed_or_noise, recoverable_basin_like, self_terminating, thin_ridge.
- Rows completed: 700.
- Errors: 0.
