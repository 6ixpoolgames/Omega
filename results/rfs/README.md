# RFS Results

Retained outputs for the Reachable Futures Substrate program.

Planned layout:

```text
results/rfs/<timestamp-or-run-id>/
  config.json
  status.json
  results.jsonl
  results.csv
  aggregate.csv
  summary.md
```

RFS outputs should report established reachability/viability quantities first:

```text
reachable sets
viability kernels
capture / recovery basins
terminal hazards
future-space contraction under intervention
```

Do not label rows Omega-positive in the substrate. Interpretive labels belong
in result notes after controls and failure modes are visible.
