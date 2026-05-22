# RFS0 Strict Reachable Futures Batch

Exact finite substrate batch. Omega-positive labels are not used.

## Config

```json
{
  "checkpoint_every": 1,
  "controls": "structured,dense_permissive_control,dead_control,random_edge_control,shuffled_admissibility_control,no_perturbation_control",
  "max_runtime_seconds": 900,
  "out": "results\\rfs0\\20260522_strict_reachable_futures_small_smoke",
  "regimes": "balanced,permissive,harsh,repair_rich,commit_rich,capacity_tight",
  "run_id": "20260522_090447",
  "seeds_per_regime": 3,
  "status": "COMPLETED",
  "workers": 18
}
```

## Aggregate

| scope | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | recovery cap | recovery integrity | contraction | expansion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 108 | 369.0 | 231.2 | 0.1028 | 1142.5 | 0.796 | 0.776 | 0.243 | 0.000 |

## Kernel Classes

| class | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |
|---|---:|---:|---:|---:|---:|---:|---:|
| strict_large_or_trivial | 36 | 634.0 | 634.0 | 0.2818 | 1355.0 | 0.208 | 0.000 |
| strict_moderate | 38 | 308.8 | 56.2 | 0.0250 | 1508.7 | 0.494 | 0.000 |
| strict_sparse_nonzero | 3 | 168.0 | 4.3 | 0.0019 | 2250.0 | 0.000 | 0.000 |
| strict_zero | 31 | 154.5 | 0.0 | 0.0000 | 339.7 | 0.000 | 0.000 |

## Controls

| control | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |
|---|---:|---:|---:|---:|---:|---:|---:|
| dead_control | 18 | 108.0 | 0.0 | 0.0000 | 108.0 | 0.000 | 0.000 |
| dense_permissive_control | 18 | 900.0 | 900.0 | 0.4000 | 1125.0 | 0.270 | 0.000 |
| no_perturbation_control | 18 | 402.0 | 109.5 | 0.0487 | 801.5 | 0.542 | 0.000 |
| random_edge_control | 18 | 268.0 | 38.6 | 0.0172 | 2250.0 | 0.000 | 0.000 |
| shuffled_admissibility_control | 18 | 268.0 | 266.3 | 0.1183 | 1785.4 | 0.106 | 0.000 |
| structured | 18 | 268.0 | 73.0 | 0.0324 | 785.0 | 0.541 | 0.000 |

## Structured Regimes

| regime | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |
|---|---:|---:|---:|---:|---:|---:|---:|
| balanced | 3 | 288.0 | 18.0 | 0.0080 | 867.0 | 1.000 | 0.000 |
| capacity_tight | 3 | 216.0 | 0.0 | 0.0000 | 648.0 | 0.000 | 0.000 |
| commit_rich | 3 | 288.0 | 18.0 | 0.0080 | 867.0 | 1.000 | 0.000 |
| harsh | 3 | 144.0 | 0.0 | 0.0000 | 399.0 | 0.000 | 0.000 |
| permissive | 3 | 384.0 | 384.0 | 0.1707 | 1062.0 | 0.247 | 0.000 |
| repair_rich | 3 | 288.0 | 18.0 | 0.0080 | 867.0 | 1.000 | 0.000 |

## Smoke Read

- Rows completed: 108.
- Errors: 0.
- Graceful-stop behavior: partial rows, CSV summaries, status, and this summary are rewritten after completed jobs.
