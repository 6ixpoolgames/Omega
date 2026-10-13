# Reproduction and next-run gate

From the Omega root using its `.venv/Scripts/python.exe`:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_testbed_contracts.py tests/test_material_sink.py tests/test_finite_classes.py tests/test_channel_access.py tests/test_snapshot_execution.py tests/test_channel_experiment.py tests/test_channel_native_sampling.py tests/test_event_sequences.py tests/test_growing_population.py tests/test_growing_comparison.py -q
.venv/Scripts/python.exe scripts/run_channel_comparison.py smoke --arm uniform_absorbing
.venv/Scripts/python.exe scripts/run_channel_comparison.py smoke --arm worn_absorbing
.venv/Scripts/python.exe scripts/run_channel_comparison.py smoke --arm worn_reversible
.venv/Scripts/python.exe scripts/run_channel_comparison.py profile --arm uniform_absorbing
```

Every execution creates a new ignored run folder, immutable source/config bundle,
hash manifest, runtime profile, status and artifact inventory. The existing
engineering evidence has its exact run IDs and input hashes in
`engineering_report/PROVENANCE.json`. Reproduction runs do not overwrite it.

Generate a new human/machine report into an explicitly chosen new output folder:

```powershell
.venv/Scripts/python.exe scripts/report_channel_comparison.py <run1> <run2> <run3> <pilot> --output <new-report-folder>
```

The reporter verifies source and artifact hashes before retaining compact data.
Arrays/event dumps and frozen source bundles stay local. Git publication is an
explicit action, never part of this command.

`PROTOCOL_DRAFT.json` is deliberately incomplete and refused by scientific mode.
Before running science, file an amended frozen protocol with all physical base
parameters, the chosen damage law/range, matched roots, search class, clock,
resource budget and executable registered numerical outcome predicates.

An outcome is `{id,metric,operator,threshold?,tolerance?}`. Supported metrics are
`winner_rate`, `seed_excess`, `closure_probability`, `functioning_margin`,
`max_residual`, and `uniform_null_error`. Operators are `record`, `eq`, `le`, `ge`,
`lt`, `gt`. Record-only outcomes have status open_outcome. Missing physical
applicability gives unsupported, not a passed prediction. Extend the versioned
metric registry for a new comparison instead of inserting executable formulas.

Scientific invocation after that separate freeze/launch decision:

```powershell
.venv/Scripts/python.exe scripts/run_channel_comparison.py scientific --protocol <frozen-protocol.json>
```

The current pilot does not justify the draft 120-second budget for 36 larger
tables. A complete single-policy preflight remains the next engineering gate.
No scientific grid or ethical verdict was produced by the implementation smoke.
