# Same Mutual Information, Different Declared Recovery Witness

Witness ID: `same_mutual_information_different_declared_recovery_v0`

Status: `same_mutual_information_different_declared_recovery`

## Controlled Information Baseline

```text
information_controls_hold: True
all_expected_relations_hold: True
declared_channel_mutual_information_bits: 1.000000
nuisance_channel_mutual_information_bits: 1.000000
declared_channel_capacity_bits: 1.000000
nuisance_channel_capacity_bits: 1.000000
```

Both channels are deterministic binary-output channels over the same uniform
two-bit source. Each transmits exactly one bit of source information and has the
same deterministic binary-output capacity.

## Declared Registry Recovery

```text
declared_source_distinction_id: D_d
declared_target_observation_id: O_y
declared_channel_exact_declared_recovery: True
nuisance_channel_exact_declared_recovery: False
```

## Read

Generic source-output mutual information and deterministic output capacity do
not determine declared registry recovery. The matched control transmits a
nuisance bit with the same information score while failing the declared
distinction contract.

## Not Claimed

```text
semantic recovery
value detection
valuer detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
