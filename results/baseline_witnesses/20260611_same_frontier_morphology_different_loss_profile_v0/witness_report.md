# Same Frontier Morphology, Different Declared Loss Profile Witness

Witness ID: `same_frontier_morphology_different_loss_profile_v0`

Status: `same_frontier_morphology_different_declared_loss_profile`

## Controlled Baseline

```text
morphology_controls_hold: True
all_expected_relations_hold: True
```

The two channels match coarse one-step frontier morphology summaries, including
support count, global target support, entropy, and viable-target-count multiset.

## Declared Loss Profile

```text
declared_viability_predicate: state first bit v = 1
loss_rule: source viable and no viable target in declared one-step support
preserve_loss_signature: 10:0;11:0
flip_loss_signature: 10:1;11:1
preserve_loss_count: 0
flip_loss_count: 2
```

## Read

Matched frontier morphology summaries do not determine the declared
horizon-local loss profile.

## Not Claimed

```text
real-world viability
real irreversibility
value detection
valuer detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
