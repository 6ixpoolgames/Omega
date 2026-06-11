# Same Intervention Effect, Different Declared Recovery Witness

Witness ID: `same_intervention_effect_different_declared_recovery_v0`

Status: `same_intervention_effect_different_declared_recovery`

## Controlled Intervention-Effect Baseline

```text
source_count: 4
intervention_count: 2
system_count: 2
declared_effect_observation_id: target_effect_bit
baseline_controls_hold: True
all_expected_relations_hold: True
```

Both systems implement the same declared intervention effect: `set_effect_0`
sets the observed effect bit to `0`, and `set_effect_1` sets it to `1`.

## Declared Recovery

```text
declared_source_distinction_id: D_d
declared_recovery_observation_id: target_recovery_bit
declared_system_id: effect_with_declared_d_carried
nuisance_system_id: effect_with_nuisance_n_carried
declared_system_exact_declared_recovery: True
nuisance_system_exact_declared_recovery: False
```

## Read

A matched declared intervention-effect summary does not determine declared
post-intervention recovery.

## Not Claimed

```text
causal discovery
causal abstraction
counterfactual semantics
full intervention calculus
semantic recovery
value detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
