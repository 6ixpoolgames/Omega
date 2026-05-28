# Results Layout

Generated outputs should not be written into the repository root.

Use this layout:

```text
results/
  rfs0/
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

- Large generated validation outputs should normally stay ignored and be
  summarized in retained notes under `docs/research_notes/validation_results/`.
- If a small result artifact is deliberately tracked, it should live under a
  named branch folder such as `results/rfs0/<run-id>/`,
  `results/val0_g/<run-id>/`, or `results/val0_ct/<run-id>/`.
- Local smoke/calibration/stress outputs should live under `results/local_runs/`
  and stay ignored.
- RFS-MB0 future-landscape and relation-atlas raw outputs are local run
  artifacts unless a maintainer explicitly promotes a compact subset.
- Historical result folders from the old root layout are archived under
  `results/historical_probes/`.
- Do not add new root-level `*_results` folders.
