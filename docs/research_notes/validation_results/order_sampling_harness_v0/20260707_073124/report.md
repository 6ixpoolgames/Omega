# Order Sampling Harness v0 Report

Status: PASS
Verdict: calibrated
Protocol: `docs/research_notes/omega_theory/order_sampling_harness_protocol_v0.md`

## Calibration Witnesses

- Loss comparison classification: dependent
- Fragility classification: fragile
- Pathological-order classification: pathological
- Expansion comparison classification: invariant_true
- Kill conditions pass: True

## Loss Dependency

- discrete: False
- local_below_joint: False
- joint_below_local: True

## Fragility

- discrete: False
- local_below_joint: False
- joint_below_local: True

## Pathological Order

- pathological_phantom_order: verdict=False, soundness_violation=True

## Expansion Invariance

- discrete: True
- task_below_revision_below_joint: True
- task_below_joint_below_revision: True

## Claim Boundary

This is a finite declared-order sensitivity harness. It does not derive the correct fact order, value, standing, aggregation, arbitration, patienthood, or Omega validation.
