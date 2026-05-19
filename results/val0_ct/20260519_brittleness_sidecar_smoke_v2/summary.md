# VAL0-CT Brittleness Sidecar Smoke

Brittleness is diagnostic only. This run does not change R1, R0-lookahead, policies, or success criteria.

## Config

```json
{
  "H": 16,
  "T": 32,
  "brittleness_candidate_sample": 32,
  "brittleness_stress_samples": 4,
  "elapsed_seconds": 1087.7634230999975,
  "families": [
    "brittle_peak",
    "structured_asymmetric_v2",
    "low_resolution_dense",
    "lock_in_seeded"
  ],
  "h": [
    1,
    2
  ],
  "max_paths": 512,
  "num_constructors": 2,
  "num_tasks": 64,
  "out": "results\\val0_ct\\20260519_brittleness_sidecar_smoke_v2",
  "run_id": "20260519_160636",
  "sample_size": 256,
  "seeds": 8
}
```

## Aggregate

| family | n | mean R1 advantage | mean brittleness | chosen brittleness gap | corr(brittleness,R1_advantage) |
|---|---:|---:|---:|---:|---:|
| brittle_peak | 16 | 0.408 | 0.107 | -0.010 | 0.050 |
| lock_in_seeded | 16 | 0.013 | 0.153 | -0.002 | -0.286 |
| low_resolution_dense | 16 | -0.003 | 0.000 | 0.000 | 0.000 |
| structured_asymmetric_v2 | 16 | 0.322 | 0.112 | -0.017 | -0.176 |

## Interpretation Guardrails

- Positive `chosen_brittleness_gap` means R0-lookahead selected a more brittle branch than R1.
- High brittleness in low-resolution dense controls would be suspicious.
- Correlation is exploratory in this smoke because sample sizes are small.

## Primary Read

This smoke is a useful negative result for the current sidecar proxy.

What worked:

- The sidecar is parsimonious and diagnostic-only; it does not alter R1,
  R0-lookahead, policies, or success criteria.
- `low_resolution_dense` no longer receives spurious brittleness after adding a
  density penalty to structuredness.
- Positive anchor families still show R1 advantage:
  - `brittle_peak`: mean R1 advantage 0.408.
  - `structured_asymmetric_v2`: mean R1 advantage 0.322.

What failed:

- The key predictive sanity check did not pass.
- `chosen_brittleness_gap` was slightly negative in `brittle_peak`
  (-0.010) and `structured_asymmetric_v2` (-0.017).
- `corr(brittleness, R1_advantage)` was near zero or negative in the positive
  families.

Interpretation:

```text
The current brittleness proxy is not yet measuring the structural property that
explains R1's advantage over R0-lookahead.
```

This does not negate the prior R1 calibration result. It means the proposed
sidecar, as currently implemented, should not be used to explain or classify
held-out regimes in a larger run.

Recommended next move:

```text
Do not scale this brittleness metric yet. Revise the sidecar around path
variation / retained-depth collapse rather than candidate-level enabled-drop
and obstruction-add stresses.
```
