# Agency Diamond Midscale Pilot v0

Command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.agency_diamond_midscale --out-root .tmp\agency_diamond_midscale_validation
```

Base commit: `e2d9eb6edcc324c9dc21fd5312ecde2ade2bc1a3`

Status: PASS

## Scope

This is a synthetic finite agency-layer pilot. It does not detect agency,
identity, value, valuerhood, or Omega. It checks whether declared finite
null-battery systems separate persistence, control, feedback advantage,
reflexive maintenance, and joint-continuation effect.

## Coverage

- Systems: 8
- Cases: 40
- Horizons: 1, 2, 3, 4, 6

## Prespecified Checks

- passive_has_no_control: PASS
- driven_cycle_has_recurrence_without_control: PASS
- open_loop_has_control_without_feedback_advantage: PASS
- feedback_cases_gain_over_replay: PASS
- thermostat_has_no_reflexive_challenge: PASS
- self_restoring_has_reflexive_advantage: PASS
- dominant_controller_has_negative_joint_effect: PASS
- cooperative_controller_has_positive_joint_effect: PASS

## Classification Counts

- control_without_feedback_advantage: 5
- dominant_joint_contraction: 5
- feedback_advantage: 15
- passive_or_driven_recurrence: 8
- passive_persistence: 2
- reflexive_maintenance: 5

## Interpretation

The pilot is a null battery for the operational-causal-diamond proposal. It
separates passive persistence, driven recurrence, externally available control,
feedback advantage over matched open-loop replay, reflexive maintenance of the
control-observation channel, and positive or negative joint-continuation effect.

The result supports the design of the agency-layer test harness. It is not a
claim that the fixtures are agents or that the metrics are sufficient for
agency.
