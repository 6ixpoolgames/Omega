# Same Coarse Bisimulation, Different Consequence Profile Witness

Witness ID: `same_coarse_bisimulation_different_consequence_profile_v0`

Status: `same_coarse_bisimulation_different_consequence_profile`

## Controlled Baseline

```text
state_count: 4
transition_edge_count: 4
coarse_panel_id: coarse_unit_observation
coarse_partition_signature: coarse_all_states:00;01;10;11
baseline_controls_matched: True
expanded_profile_counts_matched: True
```

Both expanded panels share the same transition system and the same one-block
coarse observation partition.

## Expanded Profiles

```text
declared_d_panel_id: declared_d_expanded_panel
declared_n_panel_id: declared_n_expanded_panel
expanded_profile_signatures_differ: True
declared_d_allowed_pair_signature: 00,01;10,11
declared_n_allowed_pair_signature: 00,10;01,11
declared_d_blocked_pair_signature: 00,10;00,11;01,10;01,11
declared_n_blocked_pair_signature: 00,01;00,11;01,10;10,11
```

## Read

The same coarse bisimulation-style partition does not determine the exact
consequence profile under a declared expanded panel.

## Not Claimed

```text
arbitrary post-hoc panel validity
global identity
bisimulation novelty
value detection
agency detection
Omega validation
substrate-general panel validity
```
