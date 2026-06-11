# Same Reachability, Different Declared Recovery Witness

Witness ID: `same_reachability_different_recovery_v0`

Status: `same_reachability_different_declared_recovery`

## Controlled Baselines

```text
state_count: 4
channel_count: 2
baseline_controls_matched: True
```

The two channels have the same per-source reachable count, same total edge
count, same global target support, and same uniform per-source entropy.

## Declared Recovery

```text
declared_source_distinction_id: D_d
declared_target_observation_id: O_d
preserve_channel_exact_declared_recovery: True
erase_channel_exact_declared_recovery: False
```

## Read

Reachability count and global reachable support are insufficient for declared
distinction recovery in this finite witness.

## Not Claimed

```text
Omega validation
value detection
valuer detection
agency detection
identity detection
substrate-general theory validation
```
