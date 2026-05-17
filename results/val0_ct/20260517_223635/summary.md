# VAL0-CT Smoke Summary

This is a harness and workflow validation run for the VAL0-CT constructor task algebra probe.
It is not evidence for full Omega.

This run uses bounded path expansion (`max_paths = 512`). An unbounded/exact
20-seed attempt hit a one-hour timeout before producing results, so this should
be read as the first bounded smoke rather than exhaustive reachability
enumeration.

## Config

```json
{
  "H": [
    4,
    8
  ],
  "T": [
    16,
    32
  ],
  "cpu_count": 24,
  "elapsed_seconds": 1778.7405117999997,
  "families": [
    "low_resolution_dense",
    "structured_asymmetric",
    "lock_in_seeded"
  ],
  "h": [
    1,
    2,
    4
  ],
  "max_paths": 512,
  "num_constructors": 2,
  "num_tasks": 64,
  "policies": [
    "random",
    "R0",
    "R0_lookahead",
    "R1",
    "pseudo_omega"
  ],
  "run_id": "20260517_223635",
  "sample_size": 256,
  "seeds": 20,
  "workers": 18
}
```

## Policy Means

| family | policy | mean global LHR | mean local LHR | pseudo-Omega rate |
|---|---:|---:|---:|---:|
| lock_in_seeded | R0 | 0.439 | 18.446 | 0.792 |
| lock_in_seeded | R0_lookahead | 0.695 | 12.558 | 0.562 |
| lock_in_seeded | R1 | 0.694 | 12.608 | 0.554 |
| lock_in_seeded | pseudo_omega | 0.204 | 22.125 | 1.000 |
| lock_in_seeded | random | 0.374 | 16.358 | 0.808 |
| low_resolution_dense | R0 | 0.708 | 0.000 | 0.000 |
| low_resolution_dense | R0_lookahead | 0.716 | 0.000 | 0.000 |
| low_resolution_dense | R1 | 0.717 | 0.000 | 0.000 |
| low_resolution_dense | pseudo_omega | 0.595 | 0.000 | 0.000 |
| low_resolution_dense | random | 0.670 | 0.000 | 0.000 |
| structured_asymmetric | R0 | 0.704 | 0.000 | 0.000 |
| structured_asymmetric | R0_lookahead | 0.703 | 0.000 | 0.000 |
| structured_asymmetric | R1 | 0.702 | 0.000 | 0.000 |
| structured_asymmetric | pseudo_omega | 0.604 | 0.000 | 0.000 |
| structured_asymmetric | random | 0.663 | 0.000 | 0.000 |

## Interpretation Guardrails

- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.
- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.
- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.

## Immediate Read

- `R1` and `R0_lookahead` are nearly identical in the current generators, so
  this smoke validates the harness more than it validates the R1 distinction.
- The `lock_in_seeded` family successfully produces pseudo-Omega behavior:
  local reachability/persistence rises while global LHR falls.
- The next revision should sharpen the R1 threshold/selector and generator
  asymmetry so robust mean future reachability can diverge from greedy peak
  lookahead.
