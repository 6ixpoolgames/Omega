# Directional Asymmetry and Operational Capability v0 Validation

Status: retained
Verdict: asymmetry_not_sufficient_and_preexisting_bias_not_necessary
Protocol: `docs/research_notes/omega_v2/directional_asymmetry_capability_protocol_v0.md`
Finite path horizon: 3

## Hypothesis Verdicts

- directional_asymmetry_sufficiency: rejected
- preexisting_substrate_bias_necessity: rejected_for_declared_operational_features
- process_level_asymmetry_necessity: unresolved
- independent_directional_bias_enabling: rejected_in_matched_product_control
- coupled_directional_resource_enabling: unresolved

## Case Results

- DA1_passive_asymmetry_not_sufficient: True
- DA2_reversal_paired_census_complete: True
- DA3_reversible_primitives_allow_functional_noninvertibility: True
- DA4_matched_record_selector_control: True
- DA5_independent_bias_does_not_change_profile: True

## Passive Biased Cycle

- Path-reversal total variation: 11/16
- Reciprocal support: True
- Causal action influence: False
- Record-sensitive selection: False
- Closed-loop persistence: True

## Reversal-Paired Action Census

- Permutations: 6
- Policies: 48
- Manifest digest: `f112cb529f12d2c5386e514120c6d3d72a8ba1a36dbba835a7fe9577a259a287`
- All primitive actions bijective: True
- All reversal contracts hold: True
- All constant forward/reverse distances zero: True
- Noninjective mixed-policy witnesses: 12
- First witness: {"actions_have_distinct_effects": true, "closed_loop_image_size": 2, "closed_loop_injective": false, "closed_loop_targets": "1|2|1", "permutation": "120", "permutation_id": "permutation_120", "policy": "forward|forward|reverse", "primitive_actions_bijective": true, "qualifying_noninvertible_selector": true, "reversal_contract_holds": true, "reverse_pair_total_variation": "0", "uses_both_actions": true}

## Matched Record-Sensitive Pair

- Balanced / biased directional total variation: 0 / 11/16
- Balanced selector / baseline branch fidelity: 1 / 1/2
- Biased selector / baseline branch fidelity: 1 / 1/2
- Policy-deformation total variation, balanced / biased: 1/2 / 1/2
- Selector closed-loop reversal TV, balanced / biased: 1 / 1
- Selector closed-loop reciprocal support, balanced / biased: False / False
- Operational signature unchanged: True
- Branch fidelity unchanged: True
- Policy deformation unchanged: True

Matched controls:

- state_space_equal: True
- actions_equal: True
- transition_support_equal: True
- selector_controller_equal: True
- baseline_controller_equal: True
- initial_world_record_law_equal: True
- branch_fidelity_event_equal: True
- phase_probabilities_differ: True

## Dependency Surface

- model: finite states, finite actions, exact transition kernel
- experiment: initial law, controller, finite horizon
- measurement: action involution, path reversal, branch-fidelity event
- interpretation: operational feature definitions

## Kill Conditions

- passive_control_has_synthetic_selection: False
- census_not_exhaustive: False
- primitive_reversal_contract_fails: False
- matched_surface_changes_beyond_phase_bias: False
- directionality_control_does_not_separate: False
- feature_vector_changes_under_independent_product: False

## Claim Boundary

Finite operational countermodels only; not Alpha, valuerhood, agency, standing, value, moral license, Omega compatibility, or a physical arrow-of-time result.

The independent-product control does not test a directional resource coupled to controller operation.
