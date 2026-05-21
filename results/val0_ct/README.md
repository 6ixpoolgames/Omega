# VAL0-CT Results

Store VAL0-CT run outputs here.

Current status:

```text
VAL0-CT is the completed first task-space calibration layer.
It remains useful for guardrails, R1/R0/R0-lookahead comparisons, and
reachable-neighborhood diagnostics, but it is no longer the front-edge
validation target.
```

The active front edge is VAL0-G neutral grammar geometry discovery. Future
VAL0-G outputs should go under:

```text
results/val0_g/<timestamp-or-run-id>/
```

Recommended run layout:

```text
results/val0_ct/<timestamp-or-run-id>/
  config.json
  results.jsonl
  aggregate.csv
  summary.md
```

Only commit compact, interpretable summaries and artifacts that are worth
sharing. Keep scratch, calibration, and stress outputs in `results/local_runs/`.
