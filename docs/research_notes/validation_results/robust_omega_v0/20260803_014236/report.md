# Omega v2 May and Robust Realization v0 Validation

Status: retained
Verdict: finite_may_and_robust_realization_core_retained
Protocol: `docs/research_notes/omega_v2/robust_omega_protocol_v0.md`

## Quantifier Contract

- Policy quantifier: exists
- Environment quantifier: forall
- Run semantics: one_deterministic_finite_run_per_policy_environment
- Nonempty environment scope required: True

## Case Results

- legacy_may_parity: True
- may_duplicate_invariance: True
- may_but_not_robust: True
- environment_sensitivity: True
- robust_hollow_triangle: True
- robust_positive_control: True
- robust_duplicate_invariance: True
- generated_run_crosscheck: True
- candidate_antitonicity: True
- environment_antitonicity: True
- robust_implies_may: True
- restriction_laws: True
- empty_environment_scope_rejected: True
- partial_outcome_table_rejected: True
- multivalued_outcome_table_rejected: True

## May Migration

- Pair fibers: {"AB": ["history:a0"], "AC": ["history:a1"], "BC": ["history:a2"]}
- Triple witnesses: []
- Maximal faces: 3
- Greatest face exists: False
- Structural digest: `b79cd2f3be3a4b98047055a0776bfe4411109ca0502678d75d14bc00560e8e28`
- Legacy parity: True
- Duplicate invariant: True

## May but Not Robust

- May-compatible: True
- Robust over calm scope: True
- Robust over full scope: False
- Environment antitone failures: 0
- Candidate classes stable across scopes: True

## Robust Hollow Triangle

- Pairwise Robust: True
- Triple Robust: False
- Pair securing policies: {"AB": ["policy_ab"], "AC": ["policy_ac"], "BC": ["policy_bc"]}
- Triple securing policies: []
- Robust maximal faces: 3
- Candidate antitone failures: 0
- Restriction failures: 0
- Robust-implies-May failures: 0
- Duplicate invariant: True

## Robust Positive Control

- Triple Robust: True
- Securing policies: ['policy_abc']
- Environment-indexed witnesses: [{"environment_runs": [{"environment_id": "north", "witness_id": "run:robust_triangle_positive:policy_abc:north"}, {"environment_id": "south", "witness_id": "run:robust_triangle_positive:policy_abc:south"}], "policy_id": "policy_abc"}]

## Kill Conditions

- legacy_may_parity_failed: False
- empty_environment_scope_admitted: False
- partial_outcome_table_admitted: False
- multivalued_outcome_table_admitted: False
- generated_run_table_mismatch: False
- candidate_antitonicity_failed: False
- environment_antitonicity_failed: False
- robust_without_may: False
- candidate_duplicate_changed_payload: False
- robust_witnesses_discarded: False
- pair_triple_scope_mismatch: False

## Claim Boundary

Finite deterministic May/Robust realization only; not candidate correctness, empirical robustness, identity, agency, valuerhood, standing, value, moral license, universal Omega, or selection of a maximal face.

The retained fixtures are exact finite constructions. They do not validate the supplied candidate, policy, or environment classes as empirical or moral objects.
