# Omega v2 Generated-Controller Robust Separation v0 Validation

Status: retained
Verdict: generated_controller_joint_realizability_does_not_imply_joint_robust_securability
Protocol: `docs/research_notes/omega_v2/generated_controller_robust_separation_protocol_v0.md`
Summary digest: `abbf4ce3786b022763aadfff012d9fec977a5380cf686e9a04685dbd5a92a073`

## Controller Class

- Enumerated controllers: 36
- Generated behavior classes: 9
- Pair-securing sequences: {"AB": ["xy", "yx"], "AC": ["xz", "zx"], "BC": ["yz", "zy"]}

## Strict Separation

- May triple witness count: 4
- North triple sequences: ['xy']
- South triple sequences: ['yx']
- Full-scope triple sequences: []

## Matched Positive

- Full-scope triple sequences: ['xy']
- Strict/positive May support match: True

## Case Results

- controller_enumeration_complete: True
- behavior_classes_complete: True
- generated_runs_match_fresh_rollout: True
- generated_runs_match_compiled_closed_loop: True
- strict_observation_stream_shared: True
- strict_action_sequence_shared: True
- candidate_membership_trajectory_extensional: True
- strict_may_triple_nonempty: True
- strict_each_environment_triple: True
- strict_pairwise_robust: True
- strict_pair_sequences_match: True
- strict_full_triple_not_robust: True
- strict_singleton_scopes_restore_triple: True
- strict_pair_triple_scope_match: True
- positive_full_triple_robust: True
- strict_positive_may_support_match: True
- behavior_reduction_preserves_verdicts: True
- structural_laws_pass: True
- complete_run_evidence: True

## Kill Conditions

- controller_enumeration_partial: False
- controller_count_mismatch: False
- behavior_class_count_mismatch: False
- generated_run_table_mismatch: False
- closed_loop_compilation_mismatch: False
- observation_stream_differs: False
- action_sequence_differs_across_environments: False
- candidate_membership_not_trajectory_extensional: False
- strict_environment_triple_missing: False
- strict_pair_not_robust: False
- strict_full_triple_robust: False
- strict_singleton_scope_failed: False
- positive_control_failed: False
- behavior_reduction_changed_verdict: False
- pair_triple_scope_mismatch: False
- structural_law_failed: False
- run_evidence_discarded: False

## Claim Boundary

Finite exact separation under a completely enumerated bounded deterministic controller class. Not a claim about the correct controller, environment, or candidate classes; partial observation in general; stochastic or empirical robustness; identity; agency; valuerhood; standing; value; moral compatibility; or universal Omega.

The run exhausts one bounded deterministic controller class. It does not identify that class with agency, valuerhood, empirical control, or moral compatibility.
