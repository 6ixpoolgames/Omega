# Same Entropy, Different Declared Recovery Profile Witness

Witness ID: `same_entropy_different_recovery_profile_v0`

Status: `same_entropy_different_recovery_profile`

## Controlled Baseline

```text
entropy_controls_hold: True
all_expected_relations_hold: True
```

The two channels have matched per-source support count, per-source entropy,
global target support, global target weights, and global output entropy.

## Recovery Profile Difference

```text
preserve_a_recovery_profile: recovered:D_A|failed:D_B
preserve_b_recovery_profile: recovered:D_B|failed:D_A
```

## Read

Matched entropy summaries do not determine which declared distinction is
recoverable.

## Not Claimed

```text
semantic recovery
identity detection
value detection
valuer detection
agency detection
Omega validation
substrate-general theory validation
```
