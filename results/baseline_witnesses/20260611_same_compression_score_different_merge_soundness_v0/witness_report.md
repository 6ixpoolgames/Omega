# Same Compression Score, Different Merge Soundness Witness

Witness ID: `same_compression_score_different_merge_soundness_v0`

Status: `same_compression_score_different_merge_soundness`

## Controlled Baseline

```text
compression_scores_matched: True
fragment_count: 4
abstraction_count: 2
```

Both abstractions have the same class count and class-size signature.

## Merge Soundness

```text
sound_abstraction_id: classes_by_declared_a
unsound_abstraction_id: classes_by_nuisance_b
sound_abstraction_merge_sound: True
unsound_abstraction_merge_sound: False
unsound_abstraction_unsound_merge_count: 2
```

## Read

Same compression score does not determine merge soundness against an exact
consequence profile.

## Not Claimed

```text
optimal compression
identity detection
value detection
agency detection
Omega validation
substrate-general abstraction validity
```
