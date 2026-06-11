# Same Marginal Success, Different Joint Success Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_marginal_success_different_joint_success`
Witness ID: `same_marginal_success_different_joint_success_v0`

## Executive Summary

This is the third baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two exact finite weighted channels over the same two-bit source
carrier:

```text
state = (a, b)
marginal distinctions = D_A, D_B
joint distinction = D_joint
```

The controlled marginal baseline is Bayes-best single-bit recovery success for
`D_A` and `D_B`. It is not exact marginal preservation.

Both channels have:

```text
same source count;
same per-source support count;
same per-source weight total;
same per-source entropy;
same D_A Bayes-best success;
same D_B Bayes-best success.
```

They differ on joint success:

```text
correlated_both_or_none: D_joint success = 5/8
independent_bit_masks:  D_joint success = 9/16
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_marginal_success_different_joint_success_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
support_edges.csv
channel_baseline_by_channel.csv
bayes_recovery_by_distinction.csv
marginal_success_by_channel.csv
joint_success_by_channel.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_marginal_success_different_joint_success
carrier_id: X2_ab
source_count: 4
channel_count: 2
controls_hold: true
same_marginal_success: true
different_joint_success: true
correlated_marginal_success_vector: D_A:3/4;D_B:3/4
independent_marginal_success_vector: D_A:3/4;D_B:3/4
correlated_joint_success_fraction: 5/8
independent_joint_success_fraction: 9/16
comparison_rows_digest: 226e7a3bd2d917b7d0b61b61
marginal_rows_digest: 59ada47993b78630ae27ff43
joint_rows_digest: 80ebbb8f8c473f5c040e0c9c
recovery_rows_digest: 35ec7eaf4e99b1ea96617096
summary_digest: 912eeaaa57a4e4cc7a4c7841
```

## Read

Matched marginal diagnostic success does not determine joint recovery success.

This does not show that marginal evidence is useless. It shows that marginal
success is not by itself a joint recovery claim.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_marginal_success_different_joint_success.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_marginal_success_different_joint_success --out results\baseline_witnesses\20260611_same_marginal_success_different_joint_success_v0
```

## Not Claimed

This witness does not claim:

```text
exact marginal preservation;
Omega validation;
value detection;
valuer detection;
agency detection;
identity detection;
semantic recovery;
substrate-general theory validation.
```
