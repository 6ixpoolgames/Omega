# Same Optimized Success, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_optimized_success_different_declared_recovery`
Witness ID: `same_optimized_success_different_declared_recovery_v0`

## Executive Summary

This is the second baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two exact finite channels over the same two-bit carrier:

```text
state = (d, n)
declared source distinction = d
declared target observation = target first bit
optimized observation panel = target first bit or target second bit
```

The declared-positive channel places source `d` in the declared target
observation. The shifted channel places source `d` in the nondeclared optimized
observation.

Both channels have:

```text
same state count;
same per-source reachable count;
same total support-edge count;
same global target support;
same uniform per-source entropy;
same exact optimized recovery success.
```

They differ on declared recovery:

```text
declared channel: declared recovery passes
shifted channel: declared recovery fails, optimized recovery passes
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_optimized_success_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
observation_manifest.csv
support_edges.csv
reachability_baseline_by_channel.csv
baseline_comparison.csv
declared_recovery_by_channel.csv
optimized_panel_recovery_by_observation.csv
optimized_recovery_by_channel.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_optimized_success_different_declared_recovery
carrier_id: X2_dn
state_count: 4
channel_count: 2
baseline_controls_matched: true
same_optimized_success: true
declared_channel_exact_declared_recovery: true
shifted_channel_exact_declared_recovery: false
declared_channel_exact_optimized_recovery: true
shifted_channel_exact_optimized_recovery: true
declared_channel_best_observation_id: O_first
shifted_channel_best_observation_id: O_second
comparison_rows_digest: 04ba433d4be6dedb2df327d0
declared_rows_digest: ae0d677b4f6fec44ea0782b7
optimized_rows_digest: 0fe5377be638696a6c2de4af
summary_digest: e4d287127ff206574da66801
```

## Read

Optimized recovery success is insufficient for declared theorem-transfer
readiness. The shifted channel recovers the source distinction only after
substituting a nondeclared observation.

This does not show that optimized recovery is useless. It shows that optimized
diagnostic success and declared-instrument recovery are different claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_optimized_success_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_optimized_success_different_declared_recovery --out results\baseline_witnesses\20260611_same_optimized_success_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
Omega validation;
value detection;
valuer detection;
agency detection;
identity detection;
semantic recovery;
substrate-general theory validation.
```
