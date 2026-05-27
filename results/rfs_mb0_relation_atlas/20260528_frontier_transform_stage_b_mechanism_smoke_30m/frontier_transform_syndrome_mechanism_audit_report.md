# Frontier-Transform Syndrome Mechanism Audit: Stage B Smoke

## Claim Boundary

Mechanism-control dependency smoke only. No holdout scoring, no n=6, no alphabet expansion, no candidate promotion.

## Run Shape

Jobs completed: `224/224`
Metric rows: `18816`
Errors: `0`

## Decision Summary

| syndrome_id | decision_class | baseline_rate | max_dependency | max_destructiveness |
|---|---|---:|---:|---:|
| SYN_A_low_growth_high_bottleneck_low_offdiag | control_too_destructive_underdetermined | 0.026786 | 1.000 | 1.000 |
| SYN_B_high_turnover_high_offdiag_high_window_delta | no_measurable_syndrome | 0.000000 | 0.000 | 1.000 |
| SYN_C_low_growth_high_concentration_low_entropy | control_too_destructive_underdetermined | 0.026786 | 1.000 | 1.000 |
| SYN_D_high_turnover_high_entropy_low_bottleneck_control | no_measurable_syndrome | 0.000000 | 0.000 | 1.000 |

## Substrate Preservation

Control systems flagged too destructive: `160`

Mechanism controls are interpreted as dependency profiles, not survival gates.

## Output Manifest

See `output_manifest.json`.
