# Same Entropy, Different Declared Recovery Profile Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_entropy_different_recovery_profile`
Witness ID: `same_entropy_different_recovery_profile_v0`

## Executive Summary

This is the fifth baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two exact finite channels over the same two-bit carrier:

```text
state = (a, b)
declared distinction panel = D_A, D_B
```

The first channel preserves `A` while scrambling `B`. The second channel
preserves `B` while scrambling `A`.

Both channels have:

```text
same source count;
same support-edge count;
same per-source support count;
same per-source entropy;
same global target support;
same global target weights;
same global target entropy.
```

They differ on the declared recovery profile:

```text
preserve_a_scramble_b: recovered D_A, failed D_B
preserve_b_scramble_a: recovered D_B, failed D_A
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_entropy_different_recovery_profile_v0/
```

Expected artifacts:

```text
state_manifest.csv
channel_manifest.csv
support_edges.csv
entropy_baseline_by_channel.csv
declared_recovery_by_distinction.csv
recovery_profile_by_channel.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_entropy_different_recovery_profile
carrier_id: X2_ab
source_count: 4
channel_count: 2
declared_distinction_panel: D_A;D_B
entropy_controls_hold: true
recovery_profile_differs: true
all_expected_relations_hold: true
preserve_a_recovery_profile: recovered:D_A|failed:D_B
preserve_b_recovery_profile: recovered:D_B|failed:D_A
entropy_rows_digest: 00002e352904fdb89aae0b09
profile_rows_digest: 02462700e24acca05b3ce204
comparison_rows_digest: 7f2772daac73892298feb445
recovery_rows_digest: 4d7e346a120ac0a3dc48ae0d
summary_digest: cf36d5fa73cd16c84790dcdd
```

## Read

Matched entropy summaries do not determine which declared distinction is
recoverable.

This does not show that entropy is useless. It shows that entropy summaries
alone are not a consequence-bearing distinction profile.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_entropy_different_recovery_profile.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_entropy_different_recovery_profile --out results\baseline_witnesses\20260611_same_entropy_different_recovery_profile_v0
```

## Not Claimed

This witness does not claim:

```text
semantic recovery;
identity detection;
value detection;
valuer detection;
agency detection;
Omega validation;
substrate-general theory validation.
```
