# Probe I0b Closure Recommendation

Probe I0b reused the existing Probe I0 estimator table and did not rerun
simulation.

## Result

Trajectory branch reopened: `False`

Recommendation:

```text
Close trajectory-native invariant branch for now; proceed with Probe 13 formal fiber-transport audit.
```

## Why

- Best hard stack: `S5` under
  `coupled_q10`, balanced score
  `0.3209876543209877`.
- Best soft stack: `I3_mandatory_plus_1_of_I2_I4_I5_I6`, balanced score
  `0.08950617283950617`.
- First zero-retention hard stack: `S4`.
- Main dropout invariant: `I2_ordered_distinction_persistence`.
- Pareto interpretation: `coupled profiles show partial Pareto separation`.
- I5: `diagnostic only, not gate-ready`.
- I6: `diagnostic only, not gate-ready`.
