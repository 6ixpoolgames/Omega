# Agency Diamond Cross-Substrate v1

Status: PASS

## Claim Boundary

Exploratory finite cross-substrate challenge only. This does not detect agency, identity, value, valuerhood, or Omega; it checks whether the operational-causal-diamond profile preserves its hierarchy, adversarial counterexamples, and basic transport controls across several small generated source grammars with held-out seeds.

## Generator

- substrates: boolean, grid, resource
- train seeds: 211, 223
- holdout seeds: 601, 607, 613
- horizons: 1, 2, 3, 4, 6

## Decision Gate

- multiple_substrates_tested: PASS
- holdout_classes_cover_required: PASS
- required_baseline_collisions_found: PASS
- counterexample_search_witnesses_found: PASS
- adversarial_probes_found: PASS
- no_collapse_alerts: PASS
- transport_invariance_passed: PASS

## Holdout Classification Counts

- control_without_feedback_advantage: 15
- dominant_joint_contraction: 15
- feedback_advantage: 45
- passive_or_driven_recurrence: 6
- passive_persistence: 9
- reflexive_maintenance: 30

## Holdout Classification By Substrate

- boolean: feedback_advantage: 15, passive_or_driven_recurrence: 6, passive_persistence: 9, reflexive_maintenance: 15
- grid: control_without_feedback_advantage: 15, feedback_advantage: 15, reflexive_maintenance: 15
- resource: dominant_joint_contraction: 15, feedback_advantage: 15

## Adversarial Probes

- cross_substrate_same_substrate_separates_feedback: PASS
- cross_substrate_control_without_feedback_found: PASS
- cross_substrate_feedback_without_reflexive_found: PASS
- cross_substrate_joint_sign_not_live_success: PASS
- cross_substrate_recurrence_not_feedback: PASS
- each_substrate_has_multiple_classifications: PASS

## Counterexample Search

- generated_recurrence_does_not_imply_feedback_advantage: PASS
- generated_control_does_not_imply_feedback_advantage: PASS
- generated_feedback_does_not_imply_reflexive_maintenance: PASS
- generated_live_success_does_not_determine_joint_effect: PASS

## Transport

- relabel_profiles_preserved: PASS
- identity_presentations_preserve_profiles: PASS
- quotient_controls_passed: PASS
