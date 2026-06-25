# Agency Diamond Stochastic Pilot v1

Status: PASS

## Claim Boundary

Exploratory finite stochastic agency-diamond pilot only. This uses exact-rational synthetic controlled systems to test probabilistic live-vs-open-loop feedback, reflexive maintenance, joint effect, blind generated profiles, and strong-lumpability coherence controls. It does not detect agency, identity, value, valuerhood, or Omega, and it does not validate any empirical transition model.

## Generator

- blind seed count: 40
- horizons: 1, 2, 3, 4
- surface: Exact-rational stochastic controlled systems generated from structural knobs; no expected class labels are declared.

## Decision Gate

- blind_pool_has_no_expected_class_labels: PASS
- multiple_classes_discovered: PASS
- required_classes_discovered: PASS
- stochasticity_present: PASS
- counterexample_search_witnesses_found: PASS
- coherence_has_positive_and_negative_controls: PASS
- negative_results_retained: PASS

## Blind Classification Counts

- control_without_feedback_advantage: 56
- dominant_joint_contraction: 24
- feedback_advantage: 28
- passive_or_driven_recurrence: 28
- reflexive_maintenance: 24

## Derived Clusters

- cluster count: 6
- control:+|observable:+|feedback:negative|reflexive:none|joint:zero|recurrence:True: 28 (representative: blind__seed2201_h1)
- control:+|observable:+|feedback:positive|reflexive:none|joint:none|recurrence:True: 28 (representative: blind__seed2204_h1)
- control:+|observable:0|feedback:zero|reflexive:none|joint:none|recurrence:True: 28 (representative: blind__seed2203_h1)
- control:0|observable:0|feedback:zero|reflexive:none|joint:none|recurrence:True: 28 (representative: blind__seed2202_h1)
- control:+|observable:+|feedback:positive|reflexive:none|joint:negative|recurrence:True: 24 (representative: blind__seed2206_h1)
- control:+|observable:+|feedback:positive|reflexive:positive|joint:none|recurrence:True: 24 (representative: blind__seed2205_h1)

## Counterexample Search

- stochastic_recurrence_does_not_imply_feedback_advantage: PASS
- stochastic_control_does_not_imply_feedback_advantage: PASS
- stochastic_feedback_does_not_imply_reflexive_maintenance: PASS
- stochastic_live_success_scalar_does_not_determine_joint_effect: PASS

## Stochastic Coherence

- report count: 80
- strongly lumpable: 47
- non-lumpable: 33

## Negative Result Retention

- passive_or_driven_recurrence: retained
- control_without_feedback: retained
- feedback_without_reflexive: retained
- negative_joint_effect: retained
