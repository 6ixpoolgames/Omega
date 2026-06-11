# Same Frontier Morphology, Different Declared Loss Profile Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_frontier_morphology_different_loss_profile`
Witness ID: `same_frontier_morphology_different_loss_profile_v0`

## Executive Summary

This is the sixth baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two exact finite one-step channels over the same two-bit carrier:

```text
state = (v, n)
declared viability predicate = v = 1
loss rule = source is viable and no viable target appears in the one-step support
```

The first channel preserves `v`. The second channel flips `v`.

Both channels have:

```text
same source count;
same support-edge count;
same per-source support count;
same per-source entropy;
same global target support;
same global target weights;
same viable-target-count multiset.
```

They differ on the declared horizon-local loss profile for currently viable
sources:

```text
preserve_declared_v: 10:0;11:0
flip_declared_v:     10:1;11:1
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_frontier_morphology_different_loss_profile_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
support_edges.csv
frontier_morphology_by_channel.csv
loss_profile_by_source.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_frontier_morphology_different_declared_loss_profile
carrier_id: X2_vn
source_count: 4
channel_count: 2
declared_viability_predicate: state first bit v = 1
loss_rule: source viable and no viable target in declared one-step support
morphology_controls_hold: true
loss_profile_differs: true
all_expected_relations_hold: true
preserve_loss_signature: 10:0;11:0
flip_loss_signature: 10:1;11:1
preserve_loss_count: 0
flip_loss_count: 2
morphology_rows_digest: 08c9209a5abd91b222607406
loss_rows_digest: 25b4476d0288819616a10a76
comparison_rows_digest: 46b12e84998777b4929a6416
summary_digest: 0eae52da3c940ae908bd7084
```

## Read

Matched frontier morphology summaries do not determine the declared
horizon-local loss profile.

This does not show that frontier morphology is useless. It shows that morphology
summaries alone are not a declared horizon-local loss certificate.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_frontier_morphology_different_loss_profile.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_frontier_morphology_different_loss_profile --out results\baseline_witnesses\20260611_same_frontier_morphology_different_loss_profile_v0
```

## Not Claimed

This witness does not claim:

```text
real-world viability;
real irreversibility;
value detection;
valuer detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
