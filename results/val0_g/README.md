# VAL0-G Results

Store VAL0-G neutral grammar geometry atlas outputs here.

Recommended run layout:

```text
results/val0_g/<timestamp-or-run-id>/
  config.json
  results.jsonl
  aggregate.csv
  geometry_class_bins.csv
  survival_curve_bins.csv
  filter_ratio_by_class.csv
  policy_selection_by_class.csv
  parameter_regime_summary.csv
  summary.md
```

Commit compact, interpretable outputs that are useful for public audit.
Keep scratch, calibration, and stress outputs in `results/local_runs/`.

VAL0-G is the current front-edge validation substrate. It asks whether neutral
constructor-style task grammars produce measurable recoverable-continuation
geometries before any claim about full Omega validation.
