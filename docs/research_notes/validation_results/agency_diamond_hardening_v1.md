# Agency Diamond Hardening v1

Command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.agency_diamond_hardening --out-root .tmp\agency_diamond_hardening_validation
```

Source head before batch: `93cff3b41a6bd4a5fac75aebcc7a4dc16dfa063d`

Status: PASS

## Claim Boundary

This is exploratory synthetic finite agency-layer hardening only. It does not
detect agency, identity, value, valuerhood, or Omega. It tests whether the
operational-causal-diamond pilot rejects simple baselines, survives generated
relabel/decoy variants, and obeys basic state-presentation transport controls.

## Decision Gate

- required_baseline_collisions_found: PASS
- strictness_witnesses_passed: PASS
- generated_profiles_preserved: PASS
- transport_controls_passed: PASS

## Load-Bearing Checks

Baseline collisions found: 21.

Required baseline failures:

- control_only_does_not_determine_feedback_axis: PASS
- feedback_only_does_not_determine_reflexive_axis: PASS
- joint_effect_only_does_not_determine_full_classification: PASS
- live_success_only_does_not_determine_joint_axis: PASS
- recurrence_only_does_not_determine_feedback_axis: PASS

Strictness witnesses:

- recurrence_does_not_imply_feedback_advantage: PASS
- control_does_not_imply_feedback_advantage: PASS
- feedback_advantage_does_not_imply_reflexive_maintenance: PASS
- live_success_does_not_determine_joint_effect: PASS
- joint_effect_does_not_imply_reflexive_maintenance: PASS

Generated variants:

- variants: 24
- generated cases: 120
- seeds: 11, 17, 23
- all generated relabel/decoy profiles preserved: PASS

Transport controls:

- positive_quotient_constructible: PASS
- positive_profile_preserved: PASS
- incompatible_need_merge_rejected: PASS
- cold_hot_merge_rejected: PASS

## Interpretation

The operational-causal-diamond profile is doing finite diagnostic work beyond
simple recurrence, control, live-success, feedback-only, or joint-effect-only
projections. The result supports the harness as load-bearing instrumentation,
not as an agency definition or detector.
