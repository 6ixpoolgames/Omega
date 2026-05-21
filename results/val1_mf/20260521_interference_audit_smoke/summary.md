# VAL1-MF Interference Audit

Counterfactual sampled audit. Neutral bins are primary; interpretive labels are provisional.

## Config

```json
{
  "horizon": 16,
  "max_runtime_seconds": 1800,
  "max_states_per_depth": 2048,
  "num_tasks": 64,
  "out": "results\\val1_mf\\20260521_interference_audit_smoke",
  "pairs": 100,
  "rollout_samples": 256,
  "run_id": "20260521_155708",
  "status": "COMPLETED",
  "workers": 18
}
```

## Aggregate

| scope | n | constructive | destructive | A harm | B harm | mutual support | cap any | low confidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100 | 0.083 | -0.083 | -0.052 | -0.040 | 0.083 | 0.960 | 0.000 |

## Mode Summary

| mode | n | A alive | B alive | joint alive | joint terminal | joint valid actions |
|---|---:|---:|---:|---:|---:|---:|
| uncoupled_parallel | 100 | 0.833 | 0.833 | 0.734 | 0.068 | 14.815 |
| full_coupling | 100 | 0.885 | 0.873 | 0.816 | 0.058 | 15.983 |
| cross_enable_only | 100 | 0.868 | 0.860 | 0.787 | 0.060 | 15.596 |
| cross_obstruct_only | 100 | 0.834 | 0.830 | 0.731 | 0.066 | 14.638 |
| cross_restore_only | 100 | 0.869 | 0.856 | 0.787 | 0.062 | 15.395 |
| cross_commit_only | 100 | 0.837 | 0.833 | 0.735 | 0.066 | 14.761 |
| shared_capacity_only | 100 | 0.839 | 0.830 | 0.734 | 0.066 | 14.770 |

## Interference Bins

| neutral bin | n | constructive | destructive | A harm | B harm | mutual support | low confidence |
|---|---:|---:|---:|---:|---:|---:|---:|
| A_local_dominance_bin | 1 | -0.129 | 0.129 | 0.000 | 0.129 | -0.129 | 0.000 |
| constructive_delta_bin | 22 | 0.361 | -0.361 | -0.222 | -0.161 | 0.361 | 0.000 |
| no_detectable_interference_bin | 77 | 0.006 | -0.006 | -0.004 | -0.008 | 0.006 | 0.000 |

## Ablation Effects

| ablation | n | joint delta | A delta | B delta |
|---|---:|---:|---:|---:|
| enable | 100 | 0.054 | 0.035 | 0.027 |
| obstruct | 100 | -0.003 | 0.001 | -0.003 |
| restore | 100 | 0.054 | 0.036 | 0.023 |
| commit | 100 | 0.001 | 0.003 | -0.000 |
| shared_capacity | 100 | 0.001 | 0.006 | -0.003 |

## Smoke Read

- Bins observed: A_local_dominance_bin, constructive_delta_bin, no_detectable_interference_bin.
- Rows completed: 100.
- Errors: 0.
- Raw joint enumeration is diagnostic only; sampled deltas are the primary readout.
