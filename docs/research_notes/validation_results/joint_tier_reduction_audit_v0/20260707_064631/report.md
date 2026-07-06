# Joint-Tier Reduction Audit v0 Report

Status: PASS
Verdict: calibrated
Protocol: `docs/research_notes/omega_theory/joint_tier_reduction_audit_protocol_v0.md`

## Planted Nulls

### ensemble_span: total_l1_amount

- Verdict: reduces
- Reduction basis: `marginal_summary.total_l1_amount`
- Passes: True
- Note: This is a planted reducible scalar, not the ensemble-span axis.

### relational_composability: compatible_pair_count

- Verdict: reduces
- Reduction basis: `CompatibilityProfile.compatible_pair_count`
- Passes: True
- Note: This planted coordinate is only edge count; it is not the v0.1 component-structure witness.

### joint_recovery_compatibility: joint_missing_fact_count

- Verdict: reduces
- Reduction basis: `RecoveryProfile.joint_missing_fact_ids`
- Passes: True
- Note: This planted coordinate is a direct recovery-profile scalar.

### colonization_axis: viable_state_count

- Verdict: reduces
- Reduction basis: `colonization control_panel.viable_state_count`
- Passes: True
- Note: This planted coordinate is a declared control-panel quantity, not colonization structure.

## Reduction Attempts

### relational_composability

- Hypothesis: reduces to pure span plus edge count or degree sequence
- Verdict: survives_simple_graph_scalar_reduction
- Passes: True

### colonization_axis

- Hypothesis: reduces to control panel plus simple scalar chain shadows
- Verdict: survives_scalar_shadow_reduction_lens_debt_open
- Passes: True

### joint_recovery_compatibility

- Hypothesis: factors as coupling surface plus registered recovery labels
- Verdict: bridge_not_independent_axis
- Passes: True

## Claim Boundary

This is a finite audit of instrument reduction pressure. It does not prove value, standing, agency, population ethics, plurality theory, aggregation, patienthood, or Omega validation.

## Public Compression

The joint-tier reduction audit calibrates planted-null controls before NOLP: known reducible coordinates reduce, relational composability survives cheap graph-scalar reductions, colonization keeps an explicit lens-invariance debt, and joint-recovery compatibility is treated as a recovery-grounded bridge rather than an independent axis.
