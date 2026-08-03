# Omega v2 Robust Joint Separation v0 Validation

Status: retained
Verdict: joint_realizability_does_not_imply_joint_robust_securability
Protocol: `docs/research_notes/omega_v2/robust_joint_separation_protocol_v0.md`
Summary digest: `189a08b58d46f25e8be66a2176b3b96034af4da54445a890aac1360189148fd5`

## Strict Separation

- May triple witnesses: ['w_abc']
- Pair policies: {"AB": ["p_ab", "p_try"], "AC": ["p_ac"], "BC": ["p_bc"]}
- Full triple Robust: False
- Full triple policies: []
- North triple Robust: True
- North triple policies: ['p_try']
- Robust maximal-face count: 3

## Matched Positive

- Triple Robust: True
- Triple policies: ['p_abc']
- May payload matches strict fixture: True

## Case Results

- may_triple_nonempty: True
- all_pairs_robust: True
- pair_policy_sets_exact: True
- full_triple_not_robust: True
- north_triple_robust: True
- environment_scope_isolates_failure: True
- positive_control: True
- duplicate_invariance: True
- structural_laws: True
- complete_run_evidence: True
- pair_triple_scope_match: True

## Kill Conditions

- may_triple_empty: False
- pair_not_robust: False
- pair_policy_set_changed: False
- full_triple_robust: False
- north_triple_not_robust: False
- scope_failed_to_isolate: False
- positive_control_failed: False
- duplicate_changed_payload: False
- structural_law_failed: False
- run_evidence_discarded: False
- pair_triple_scope_mismatch: False

## Claim Boundary

Finite deterministic lookup-table separation only; not dynamic control, empirical robustness, candidate correctness, identity, agency, valuerhood, standing, value, moral license, or Omega validation.

The fixture isolates lookup-table Robust securability from joint May realization. It does not establish dynamic, empirical, or moral robustness.
