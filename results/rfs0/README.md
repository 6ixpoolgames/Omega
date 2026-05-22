# RFS0 Results

Retained outputs for the first Reachable Futures Substrate program.

Current retained result:

- `20260522_strict_reachable_futures_small_smoke/`

Read the paired result note first:

- `docs/research_notes/validation_results/rfs0_strict_reachable_futures_small_smoke_result.md`

Planned layout:

```text
results/rfs0/<timestamp-or-run-id>/
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
