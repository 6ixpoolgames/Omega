# VAL1-MF Two-Field Compatibility Smoke

Minimal multifield smoke. Neutral bins are primary; interpretive labels are provisional.

## Config

```json
{
  "max_runtime_seconds": 1800,
  "max_states_per_depth": 4096,
  "num_tasks": 64,
  "out": "results\\val1_mf\\20260521_two_field_compatibility_smoke_cap4096",
  "pairs": 150,
  "rollout_samples": 128,
  "run_id": "20260521_153725",
  "status": "COMPLETED",
  "workers": 18
}
```

## Aggregate

| scope | n | A filter | B filter | joint filter | compatibility | A div | B div | joint cap | joint terminal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 150 | 0.677 | 0.672 | 0.967 | 0.967 | -0.289 | -0.295 | 0.947 | 0.055 |

## Compatibility Bins

| neutral bin | n | A filter | B filter | joint filter | compatibility | A div | B div | joint cap | joint terminal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| joint_viable_bin | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.105 |
| mixed_or_censored_bin | 142 | 0.694 | 0.688 | 1.000 | 1.000 | -0.306 | -0.312 | 1.000 | 0.018 |
| mutual_collapse_bin | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| uncoupled_parallel_bin | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.555 |

## Cap Hits By Bin

| neutral bin | n | A single cap | B single cap | joint cap | A coupled cap | B coupled cap |
|---|---:|---:|---:|---:|---:|---:|
| joint_viable_bin | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| mixed_or_censored_bin | 142 | 0.718 | 0.697 | 1.000 | 0.000 | 0.021 |
| mutual_collapse_bin | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| uncoupled_parallel_bin | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Smoke Read

- Bins observed: joint_viable_bin, mixed_or_censored_bin, mutual_collapse_bin, uncoupled_parallel_bin.
- Rows completed: 150.
- Errors: 0.
