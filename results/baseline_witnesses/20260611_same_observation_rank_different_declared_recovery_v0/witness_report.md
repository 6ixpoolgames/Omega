# Same Observation Rank, Different Declared Recovery Witness

Witness ID: `same_observation_rank_different_declared_recovery_v0`

Status: `same_observation_rank_different_declared_recovery`

## Controlled Observation Baseline

```text
state_count: 4
observer_count: 2
finite_observation_rank: 1
baseline_controls_hold: True
all_expected_relations_hold: True
```

Both observers are deterministic one-bit observers with the same output support,
same observation block count, and same block-size signature.

## Declared Recovery

```text
declared_source_distinction_id: D_d
declared_observer_id: observe_declared_d
nuisance_observer_id: observe_nuisance_n
declared_observer_exact_declared_recovery: True
nuisance_observer_exact_declared_recovery: False
```

## Read

Finite observation-rank and partition-shape summaries do not determine declared
distinction recovery.

## Not Claimed

```text
full linear observability
control synthesis
semantic recovery
value detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
