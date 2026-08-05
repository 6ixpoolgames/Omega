# Omega v2 Projected-Sector Floor v0 Validation

Status: retained
Verdict: projected_order_retained_and_sector_properties_separate
Protocol: `docs/research_notes/omega_v2/projected_sector_floor_protocol_v0.md`
Protocol commit: `62fb6c9`
Summary digest: `5166685c7b47f25026522c64d0bae7c474762faf7803ee20944199dd391e5363`

## Exact Scope

- Preregistered fixtures: 7
- Bounded extendability horizon: 3
- Formal fragment: `formal/lean/OmegaV2/Finite/ProjectedOrder.lean`

## Retained Separations

- A terminating, branching disintegration law can remain locally and globally confluent.
- A terminating branch can fail both local and global confluence.
- A recurrent nonbranching sector differs from both terminating controls.
- Two exact-distinct histories can be related by an independent commuting diamond and share one projected history.
- A projection can be null, one-sided, or bidirectional; bidirectionality does not select a preferred polarity.

## Case Results

- seven_preregistered_fixtures_retained: True
- all_fixture_transition_rows_retained_exactly: True
- all_projected_reach_relations_are_preorders: True
- all_mutual_projected_reach_relations_are_equivalences: True
- all_projected_condensations_are_acyclic: True
- termination_matches_absence_of_recurrent_components: True
- terminating_disintegration_is_confluent: True
- recurrent_cycle_is_recurrent_and_nonbranching: True
- genuine_branch_is_nonconfluent: True
- commuting_diamond_closes: True
- diamond_exact_histories_remain_distinct: True
- diamond_histories_share_one_projection: True
- diamond_histories_are_commuting_equivalent: True
- declared_relabeling_preserves_history: True
- null_projection_remains_null: True
- one_sided_source_remains_positive_only: True
- janus_source_remains_bidirectional: True
- partial_and_nondeterministic_systems_are_admitted: True
- no_single_coherence_boolean_emitted: True

## Kill Conditions

- fixture_transition_rows_changed: False
- projected_reachability_failed_preorder: False
- mutual_reachability_failed_equivalence: False
- projected_condensation_contains_cycle: False
- terminating_disintegration_reported_nonconfluent: False
- genuine_branch_reported_confluent: False
- commuting_diamond_not_detected: False
- exact_diamond_histories_were_merged: False
- null_projection_received_directional_polarity: False
- partial_or_nondeterministic_system_rejected: False
- single_coherence_boolean_emitted: False

## Claim Boundary

Finite support-level projection, reachability, history, termination, recurrence, confluence, and commutation only; not persistence, identity, observerhood, agency, valuerhood, value, Omega compatibility, or moral license.

## Public Compression

A projection turns a finite transition sector into an ordered continuation view, but it does not create persistence, identity, or value. Termination, recurrence, confluence, and independent commutation remain distinct properties.
