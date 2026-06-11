# Same Reachability, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_reachability_different_recovery`
Witness ID: `same_reachability_different_recovery_v0`

## Executive Summary

This is the first baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two exact finite channels over the same two-bit carrier:

```text
state = (d, n)
declared distinction = d
```

The positive channel preserves `d` while scrambling the nuisance coordinate
`n`. The matched control erases `d` while preserving `n`.

Both channels have:

```text
same state count;
same per-source reachable count;
same total support-edge count;
same global target support;
same uniform per-source entropy.
```

They differ on the declared recovery contract:

```text
target first bit must recover source first bit over support.
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_reachability_different_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
support_edges.csv
reachability_baseline_by_channel.csv
declared_recovery_by_channel.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_reachability_different_declared_recovery
carrier_id: X2_dn
state_count: 4
channel_count: 2
baseline_controls_matched: true
preserve_channel_exact_declared_recovery: true
erase_channel_exact_declared_recovery: false
baseline_rows_digest: 9f174be31509c86b991e04ac
recovery_rows_digest: 91c914e7c07917ddb0cca7bd
comparison_rows_digest: 12ef86adf78ef4561992a3f2
summary_digest: c1060773f394dda007f45987
```

## Read

Reachability count and global reachable support are insufficient for declared
consequence-bearing recovery in this finite witness.

This does not show that reachability is unimportant. It shows that reachability
alone does not determine which declared distinction is preserved or erased.

## Validation

Focused test:

```powershell
pytest tests\test_same_reachability_different_recovery.py -q
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_reachability_different_recovery --out results\baseline_witnesses\20260611_same_reachability_different_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
Omega validation;
value detection;
valuer detection;
agency detection;
identity detection;
substrate-general theory validation.
```
