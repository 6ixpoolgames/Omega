# Same Compression Score, Different Merge Soundness Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_compression_score_different_merge_soundness`
Witness ID: `same_compression_score_different_merge_soundness_v0`

## Executive Summary

This is the fourth baseline-controlled witness requested by
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs an exact merge profile over four fragments:

```text
fragment = (a, b)
exact profile rule:
  same declared a allows merge
  different declared a blocks merge
```

It then compares two abstractions with the same simple compression score:

```text
classes_by_declared_a:
  groups by declared a
  merge-sound

classes_by_nuisance_b:
  groups by nuisance b
  not merge-sound
```

Both abstractions have:

```text
same fragment count;
same class count;
same assignment count;
same class-size signature;
same simple compression score.
```

They differ on merge soundness against the exact profile.

## Retained Output

```text
results/baseline_witnesses/20260611_same_compression_score_different_merge_soundness_v0/
```

Expected artifacts:

```text
fragment_manifest.csv
exact_profile_pairs.csv
abstraction_manifest.csv
abstraction_membership.csv
merge_soundness_audit.csv
compression_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_compression_score_different_merge_soundness
carrier_id: X2_ab
fragment_count: 4
abstraction_count: 2
compression_scores_matched: true
sound_abstraction_id: classes_by_declared_a
unsound_abstraction_id: classes_by_nuisance_b
sound_abstraction_merge_sound: true
unsound_abstraction_merge_sound: false
sound_abstraction_unsound_merge_count: 0
unsound_abstraction_unsound_merge_count: 2
abstraction_rows_digest: a9b0f42b71b535a1a8164a01
audit_rows_digest: fe5ef0f24c8f850706a7963f
compression_rows_digest: 77d992893ef8efc6d7645b94
summary_digest: 5d7b24afd945f6bcb188fc98
```

## Read

Same compression score does not determine merge soundness against an exact
consequence profile.

This does not show that compression is useless. It shows that compression score
alone is not a merge-soundness certificate.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_compression_score_different_merge_soundness.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_compression_score_different_merge_soundness --out results\baseline_witnesses\20260611_same_compression_score_different_merge_soundness_v0
```

## Not Claimed

This witness does not claim:

```text
optimal compression;
identity detection;
value detection;
agency detection;
Omega validation;
substrate-general abstraction validity.
```
