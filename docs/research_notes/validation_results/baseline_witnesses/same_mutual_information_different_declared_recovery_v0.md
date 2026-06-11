# Same Mutual Information, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_mutual_information_different_declared_recovery`
Witness ID: `same_mutual_information_different_declared_recovery_v0`

## Executive Summary

This is a baseline-controlled witness for the mutual-information / channel
capacity row in `docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two deterministic binary-output channels over the same uniform
two-bit source:

```text
state = (d, n)
declared source distinction = d
declared target observation = binary output y
```

The first channel transmits `d`. The second channel transmits nuisance bit `n`.

Both channels have:

```text
same source count;
same output support;
same output weights;
same output entropy;
same conditional output entropy;
same mutual information I(X;Y);
same deterministic binary-output capacity.
```

They differ on declared registry recovery:

```text
transmit_declared_d: declared recovery passes
transmit_nuisance_n: declared recovery fails
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_mutual_information_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
output_manifest.csv
channel_kernel.csv
information_baseline_by_channel.csv
declared_recovery_by_channel.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_mutual_information_different_declared_recovery
carrier_id: X2_dn
source_count: 4
channel_count: 2
information_controls_hold: true
declared_recovery_differs: true
all_expected_relations_hold: true
declared_channel_mutual_information_bits: 1.000000
nuisance_channel_mutual_information_bits: 1.000000
declared_channel_capacity_bits: 1.000000
nuisance_channel_capacity_bits: 1.000000
declared_channel_exact_declared_recovery: true
nuisance_channel_exact_declared_recovery: false
information_rows_digest: dad12ae66dc8667e4ab13048
recovery_rows_digest: 0f4e5e294120431d45e1bbd0
comparison_rows_digest: d7103efe076b856631469a6d
summary_digest: 933238fd3a377691a38bab20
```

## Read

Generic source-output mutual information and deterministic output capacity do
not determine declared registry recovery.

This does not show that mutual information or channel capacity is useless. It
shows that generic information transfer and declared registry recovery are
different claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_mutual_information_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_mutual_information_different_declared_recovery --out results\baseline_witnesses\20260611_same_mutual_information_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
semantic recovery;
value detection;
valuer detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
