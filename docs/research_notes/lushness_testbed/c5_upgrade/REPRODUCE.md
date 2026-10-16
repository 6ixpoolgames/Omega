# Reproduce the C5 physical upgrade

From the repository root, use the local environment:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_c5_physics.py tests/test_exchange_controls.py tests/test_resource_transfer.py tests/test_domination_friction.py tests/test_domination_stage_a.py tests/test_fractional_discovery.py tests/test_uniformized_entropy.py -q
.venv/Scripts/python.exe scripts/run_c5_upgrade.py pump --smoke --jobs 1 --seconds 300 --budget 600
.venv/Scripts/python.exe scripts/run_c5_upgrade.py opportunity --smoke --jobs 1 --seconds 300 --budget 600
.venv/Scripts/python.exe scripts/run_c5_upgrade.py loss --smoke --jobs 1 --seconds 300 --budget 600
```

After the relevant smoke passes, replace `--smoke` with a full run and use
`--seconds 900 --budget 14400`. Two workers maximum across concurrently running
drivers, including other studies. Study names are `pump`, `opportunity`, `loss`,
`audit-controls` and `cost-boundary`. A completed identical source/config hash
reuses verified compact results. Changing source creates a different identity;
it does not replace old results silently.

Generate each completed report with:

```powershell
.venv/Scripts/python.exe scripts/report_c5_upgrade.py pump
```

Replace the final study name as appropriate. The reporter validates receipt,
configuration, caps, result checksum, source imports and resource/numerical
residuals. It retains compact CSV maps and one compressed code-only archive per
source identity. Frozen inputs live in `SURVEY_PLAN.json`, including the exact
bank capacities, quantums, source strengths, field strengths and initial present.

Large query intermediates remain in ignored `results/local_runs/lushness_testbed`.
These are reconstructible from retained source/config/results; no full dense
transition matrices are included in the publication records. No cleanup, commit,
push or upload occurs automatically as part of this workflow.
