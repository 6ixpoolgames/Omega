# Same Optimized Success, Different Declared Recovery Witness

Witness ID: `same_optimized_success_different_declared_recovery_v0`

Status: `same_optimized_success_different_declared_recovery`

## Controlled Baselines

```text
state_count: 4
channel_count: 2
baseline_controls_matched: True
same_optimized_success: True
```

The two channels have the same reachability and entropy controls. Both are
exactly recoverable by an optimized choice over the observation panel.

## Declared Versus Optimized Recovery

```text
declared_target_observation_id: O_first
optimized_candidate_panel: O_first;O_second
declared_channel_exact_declared_recovery: True
shifted_channel_exact_declared_recovery: False
declared_channel_best_observation_id: O_first
shifted_channel_best_observation_id: O_second
```

## Read

Optimized recovery success is insufficient for declared theorem-transfer
readiness. The shifted channel recovers the source distinction only after
substituting a nondeclared observation.

## Not Claimed

```text
Omega validation
value detection
valuer detection
agency detection
identity detection
semantic recovery
substrate-general theory validation
```
