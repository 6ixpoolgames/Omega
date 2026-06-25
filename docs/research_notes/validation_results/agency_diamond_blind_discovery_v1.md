# Agency Diamond Blind Discovery v1

Status: PASS

## Claim Boundary

Exploratory finite blind-discovery pilot only. This does not detect agency, identity, value, valuerhood, or Omega; it checks whether a frozen pool of seeded systems with no expected class labels yields derived profile clusters, hierarchy counterexamples, ablation sensitivity, and retained null/collapse cases.

## Generator

- seed count: 60
- horizons: 1, 2, 3, 4, 6
- ablation horizons: 1, 2, 3, 4
- surface: Seeded structural knobs only; expected class labels are not declared by the pool.

## Decision Gate

- blind_pool_has_no_expected_class_labels: PASS
- multiple_classes_discovered: PASS
- required_classes_discovered: PASS
- required_baseline_collisions_found: PASS
- counterexample_search_witnesses_found: PASS
- ablation_probes_passed: PASS
- negative_results_retained: PASS
- collapse_alerts_retained: PASS

## Classification Counts

- control_without_feedback_advantage: 35
- dominant_joint_contraction: 25
- feedback_advantage: 90
- passive_or_driven_recurrence: 25
- passive_persistence: 40
- reflexive_maintenance: 85

## Derived Clusters

- cluster count: 13
- control=True|observable=True|feedback=positive|reflexive=positive|joint=undeclared|recurrence=True: 55 (representative: blind__seed1205_h1)
- control=False|observable=False|feedback=zero|reflexive=not_applicable|joint=undeclared|recurrence=False: 40 (representative: blind__seed1201_h1)
- control=True|observable=True|feedback=positive|reflexive=not_applicable|joint=positive|recurrence=True: 30 (representative: blind__seed1204_h1)
- control=True|observable=True|feedback=positive|reflexive=not_applicable|joint=undeclared|recurrence=True: 30 (representative: blind__seed1206_h1)
- control=False|observable=False|feedback=zero|reflexive=not_applicable|joint=undeclared|recurrence=True: 25 (representative: blind__seed1201_h4)
- control=True|observable=True|feedback=positive|reflexive=not_positive|joint=undeclared|recurrence=True: 20 (representative: blind__seed1203_h1)
- control=True|observable=True|feedback=positive|reflexive=positive|joint=positive|recurrence=True: 20 (representative: blind__seed1224_h1)
- control=True|observable=True|feedback=zero|reflexive=not_applicable|joint=undeclared|recurrence=True: 20 (representative: blind__seed1220_h1)

## Counterexample Search

- blind_recurrence_does_not_imply_feedback_advantage: PASS
- blind_control_does_not_imply_feedback_advantage: PASS
- blind_feedback_does_not_imply_reflexive_maintenance: PASS
- blind_live_success_scalar_does_not_determine_joint_effect: PASS

## Ablation Probes

- blind_observation_ablation_reduces_feedback: PASS
- blind_fixed_policy_ablation_reduces_feedback: PASS
- blind_action_choice_ablation_removes_control: PASS
- blind_channel_ablation_reduces_reflexive_maintenance: PASS
- blind_joint_ablation_changes_joint_effect: PASS

## Negative Result Retention

- passive_persistence: retained
- no_control: retained
- control_without_feedback: retained
- feedback_without_reflexive: retained
- negative_joint_effect: retained
