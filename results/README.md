# Results Layout

Generated outputs should not be written into the repository root.

Use this layout:

```text
results/
  rfs/
    <timestamp-or-run-id>/
      config.json
      results.jsonl
      aggregate.csv
      summary.md

  val0_g/
    <timestamp-or-run-id>/
      config.json
      results.jsonl
      aggregate.csv
      summary.md

  val0_ct/
    <timestamp-or-run-id>/
      config.json
      results.jsonl
      aggregate.csv
      summary.md

  historical_probes/
    <archived result folders from older branches>

  local_runs/
    ignored local smoke, calibration, stress, and scratch outputs
```

## Rules

- New tracked validation results should live under a named branch folder such as
  `results/rfs/<run-id>/`, `results/val0_g/<run-id>/`, or
  `results/val0_ct/<run-id>/`.
- Local smoke/calibration/stress outputs should live under `results/local_runs/`
  and stay ignored.
- Historical result folders from the old root layout are archived under
  `results/historical_probes/`.
- Do not add new root-level `*_results` folders.
