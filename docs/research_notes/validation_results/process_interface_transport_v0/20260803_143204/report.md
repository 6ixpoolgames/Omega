# Omega v2 Process Interface Transport v0 Validation

Status: retained
Verdict: finite_process_interface_transport_classified
Protocol: `docs/research_notes/omega_v2/process_interface_transport_protocol_v0.md`
Horizon: 4

## Exact Transport Controls

- Relabeling: INVARIANT
- Coarse to fine: REFINED
- Coarse minima: [['inside', 'aux']]
- Fine minima: [['inside']]
- Fine to coarse: MERGED
- Annotation control: INVARIANT
- Observation-only comparison: UNRESOLVED
- Query mismatch: OBSTRUCTED

## Several Refined Minima

- Verdict: REFINED
- Coarse minima: [['left', 'right']]
- Fine minima: [['left'], ['right']]

## Cross-cut Obstruction

- Same observational signature: True
- Forward exact: False
- Reverse exact: False
- Family verdict: OBSTRUCTED
- Saturation adds: ['c', 'd']

## Case Results

- partition_validation: True
- block_relabeling_invariant: True
- strict_refinement_detected: True
- reverse_merge_detected: True
- several_refined_minima_retained: True
- crosscut_obstructed: True
- crosscut_failure_witnessed: True
- query_mismatch_obstructed: True
- annotation_invariance: True
- observational_transport_unresolved: True
- observation_does_not_override_crosscut: True

## Kill Conditions

- invalid_partition_accepted: False
- relabeling_changed_family: False
- refinement_not_decomposable: False
- merge_reported_exact_forward: False
- refined_representative_selected: False
- crosscut_called_exact: False
- saturation_silently_accepted: False
- query_mismatch_called_invariant: False
- observational_causality_claimed: False

## Claim Boundary

Finite factorization-relative interface transport only; not identity, agency, valuerhood, consciousness, patienthood, standing, value, responsibility, moral license, or Omega validation.

The checker compares finite partition-relative interface families. It does not infer a canonical process boundary.
