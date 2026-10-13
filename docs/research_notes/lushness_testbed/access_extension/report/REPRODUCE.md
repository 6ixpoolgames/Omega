# Reproduce the extension and automatic interpretation

Use the existing Windows `.venv` from the original Omega checkout.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_controlled_slice.py tests/test_rule_a_assessment.py tests/test_access_extension.py tests/test_access_extension_report.py -q
.\.venv\Scripts\python.exe scripts/run_access_slices.py extension_smoke --factor 6
.\.venv\Scripts\python.exe scripts/run_access_extension_batch.py --report docs/research_notes/lushness_testbed/access_extension/report
```

The batch runs all four registered capture factors sequentially. Each worker has
a 120-second wall cap, 1 GiB process-tree memory cap and 256 MiB output cap; all
numerical libraries use one thread. Before ranking, the runner snapshots and hashes
the protocol, law, readout modules and report generator. An incomplete regime
blocks a successful batch report.

After execution the batch automatically writes the human results, compact JSON
with registered outcomes and full selected-policy Rule A profiles, report hashes
and source/result provenance. Full 1296-policy tables remain in ignored local
run directories; none are published. No deletion or Git operation occurs.

Individual regime: `scripts/run_access_slices.py access_extension --factor 6`.
Retrospective aggregation uses `scripts/report_access_extension.py`, taking one or
more completed run directories plus `--output`. The report names candidate-only
overlay/cadence comparisons and records every negative sign. Rule A is not a reward.

The final batch also verifies identical numerical results with the initial
execution of these registered worlds; repetition is a reproducibility check,
not independent empirical evidence. Additional audit fields do not alter the law.

Remaining scope: the physical model has no molecular spatial/velocity gas degree
of freedom, growing population or controller memory. Its complete energy-shell
reference is the matched randomized preparation within this declared adapter.
