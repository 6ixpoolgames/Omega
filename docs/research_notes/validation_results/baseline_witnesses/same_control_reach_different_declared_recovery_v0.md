# Same Control Reach, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_control_reach_different_declared_recovery`
Witness ID: `same_control_reach_different_declared_recovery_v0`

## Executive Summary

This is a baseline-controlled witness for the controllability/control-reach row
in `docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two deterministic one-step controlled systems over the same
four-state carrier:

```text
state = (d, n)
controls = drive_0, drive_1
declared source distinction = d
declared recovery observation = target_recovery_bit
```

Both systems have the same finite control-reach summary:

```text
global_target_support = 00;01;10;11
per_source_reachable_target_count_signature = 00:2;01:2;10:2;11:2
target_count_by_control_signature = drive_0:2;drive_1:2
target_control_bits_by_control_signature = drive_0:0;drive_1:1
```

They differ on declared recovery:

```text
control_with_declared_d_carried: declared recovery passes
control_with_nuisance_n_carried: declared recovery fails
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_control_reach_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
control_manifest.csv
system_manifest.csv
transition_edges.csv
control_reach_by_system.csv
declared_recovery_by_system.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_control_reach_different_declared_recovery
carrier_id: X2_dn_control_reach
source_count: 4
control_count: 2
system_count: 2
global_target_support: 00;01;10;11
per_source_reachable_target_count_signature: 00:2;01:2;10:2;11:2
reach_controls_hold: true
all_expected_relations_hold: true
declared_system_id: control_with_declared_d_carried
nuisance_system_id: control_with_nuisance_n_carried
declared_system_exact_declared_recovery: true
nuisance_system_exact_declared_recovery: false
reach_rows_digest: 503a573c0c33a132747fe3e9
recovery_rows_digest: d7324630a9993ba757d68043
comparison_rows_digest: a7c3e22a2f1d86716310c68b
summary_digest: ff73f43bc4aaeec3bc1ea9ce
```

## Read

A matched finite control-reach summary does not determine declared recovery.

This does not show that controllability or control reach is useless. It shows
that this finite control-reach summary and declared recovery are different
claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_control_reach_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_control_reach_different_declared_recovery --out results\baseline_witnesses\20260611_same_control_reach_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
full controllability;
optimal control;
control synthesis;
semantic recovery;
value detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
