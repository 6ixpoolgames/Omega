# Agency Diamond Challenge v1

Command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.agency_diamond_challenge --out-root .tmp\agency_diamond_challenge_validation
```

Source head before batch: `6d589b32f2f1bb9f59a3cbaf50f1589262cc35d8`

Status: PASS

## Claim Boundary

This is exploratory non-handcrafted finite challenge generation only. It does
not detect agency, identity, value, valuerhood, or Omega. It checks whether
predeclared generated systems with held-out seeds recover hierarchy
distinctions, baseline collisions, counterexample-search witnesses, and basic
transport/invariance controls.

## Generator

- Grammars: cycle, open_loop, feedback, reflexive, joint_positive, joint_negative
- Train seeds: 101, 103, 107
- Holdout seeds: 401, 409, 419, 431
- Horizons: 1, 2, 3, 4, 6
- Systems: 42
- Metric cases: 210
- Holdout metric cases: 120

## Decision Gate

- holdout_classes_cover_required: PASS
- required_baseline_collisions_found: PASS
- counterexample_search_witnesses_found: PASS
- no_collapse_alerts: PASS
- transport_invariance_passed: PASS

## Holdout Results

Holdout classification counts:

- control_without_feedback_advantage: 20
- dominant_joint_contraction: 20
- feedback_advantage: 40
- passive_or_driven_recurrence: 5
- passive_persistence: 15
- reflexive_maintenance: 20

Baseline collisions found: 21.

Required baseline failures:

- control_only_does_not_determine_feedback_axis: PASS
- feedback_only_does_not_determine_reflexive_axis: PASS
- joint_effect_only_does_not_determine_full_classification: PASS
- live_success_only_does_not_determine_joint_axis: PASS
- recurrence_only_does_not_determine_feedback_axis: PASS

Counterexample-search witnesses:

- generated_recurrence_does_not_imply_feedback_advantage: PASS
- generated_control_does_not_imply_feedback_advantage: PASS
- generated_feedback_does_not_imply_reflexive_maintenance: PASS
- generated_live_success_does_not_determine_joint_effect: PASS

Collapse alerts: 0.

Transport/invariance controls:

- relabel_profiles_preserved: PASS
- identity_presentations_preserve_profiles: PASS
- quotient_controls_passed: PASS

## Interpretation

Challenge v1 moves the causal-diamond harness beyond hand-authored examples.
Individual holdout cases are generated from a frozen grammar and seed schedule,
and the labels are computed from traces. The result is load-bearing as a finite
instrumentation check: it pressures recurrence-only, control-only, feedback-only,
live-success-only, and joint-effect-only simplifications while preserving the
profile under basic nonsemantic presentation changes.

It is still synthetic finite challenge generation, not agency detection.
