# Same Control Reach, Different Declared Recovery Witness

Witness ID: `same_control_reach_different_declared_recovery_v0`

Status: `same_control_reach_different_declared_recovery`

## Controlled Control-Reach Baseline

```text
source_count: 4
control_count: 2
system_count: 2
global_target_support: 00;01;10;11
per_source_reachable_target_count_signature: 00:2;01:2;10:2;11:2
reach_controls_hold: True
all_expected_relations_hold: True
```

Both systems have the same finite control-reach summary under the declared
control panel.

## Declared Recovery

```text
declared_source_distinction_id: D_d
declared_recovery_observation_id: target_recovery_bit
declared_system_id: control_with_declared_d_carried
nuisance_system_id: control_with_nuisance_n_carried
declared_system_exact_declared_recovery: True
nuisance_system_exact_declared_recovery: False
```

## Read

A matched finite control-reach summary does not determine declared recovery.

## Not Claimed

```text
full controllability
optimal control
control synthesis
semantic recovery
value detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
