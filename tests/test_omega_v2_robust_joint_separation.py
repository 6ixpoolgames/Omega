from __future__ import annotations

from pathlib import Path

from omega_v2.experiments.robust_joint_separation_v0 import (
    FULL_ENVIRONMENTS,
    NORTH_ENVIRONMENTS,
    environment_scope_rows,
    may_fiber_rows,
    policy_environment_run_rows,
    robust_fiber_rows,
    robust_joint_separation_summary,
    robust_positive_case,
    strict_joint_case,
    strict_joint_fixture,
    structural_control_rows,
)
from omega_v2.validation.robust_joint_separation_v0 import (
    retain_robust_joint_separation_v0,
)


def test_strict_relation_keeps_the_may_triple_nonempty() -> None:
    case = strict_joint_case()
    assert case["may_triple_nonempty"] is True
    assert case["may_triple_witness_ids"] == ["w_abc"]


def test_all_pairs_are_robust_over_the_full_scope() -> None:
    case = strict_joint_case()
    assert case["all_pairs_robust"] is True
    assert case["pair_policy_ids"] == {
        "AB": ["p_ab", "p_try"],
        "AC": ["p_ac"],
        "BC": ["p_bc"],
    }
    assert {
        fiber.environment_ids for fiber in case["pair_fibers"].values()
    } == {FULL_ENVIRONMENTS}


def test_full_triple_is_not_robust_despite_may_realization() -> None:
    case = strict_joint_case()
    assert case["full_triple_robust"] is False
    assert case["full_triple_policy_ids"] == []
    assert case["may_triple_nonempty"] is True


def test_north_scope_restores_the_triple_through_try_policy() -> None:
    case = strict_joint_case()
    assert case["north"].environment_ids == NORTH_ENVIRONMENTS
    assert case["north_triple_robust"] is True
    assert case["north_triple_policy_ids"] == ["p_try"]
    assert case["north_triple_runs"] == [
        {
            "policy_id": "p_try",
            "environment_runs": [
                {
                    "environment_id": "north",
                    "witness_id": "w_abc",
                }
            ],
        }
    ]


def test_environment_narrowing_changes_no_may_fiber() -> None:
    case = strict_joint_case()
    assert case["may_scope_invariant"] is True
    assert (
        case["full"].may.structural_payload()
        == case["north"].may.structural_payload()
    )


def test_environment_antitonicity_holds() -> None:
    case = strict_joint_case()
    assert case["environment_antitone_failures"] == []


def test_positive_control_secures_the_triple_across_both_environments() -> None:
    positive = robust_positive_case()
    assert positive["triple_robust"] is True
    assert positive["triple_policy_ids"] == ["p_abc"]
    assert positive["may_payload_matches_strict"] is True
    assert positive["triple_runs"] == [
        {
            "policy_id": "p_abc",
            "environment_runs": [
                {
                    "environment_id": "north",
                    "witness_id": "w_abc",
                },
                {
                    "environment_id": "south",
                    "witness_id": "w_abc",
                },
            ],
        }
    ]


def test_duplicate_candidate_changes_no_quotient_payload() -> None:
    case = strict_joint_case()
    assert case["duplicate_raw_candidate_count"] == 4
    assert case["duplicate_quotient_candidate_count"] == 3
    assert case["duplicate_may_invariant"] is True
    assert case["duplicate_robust_invariant"] is True


def test_all_structural_laws_hold() -> None:
    case = strict_joint_case()
    assert case["may_downward_closure_failures"] == []
    assert case["may_restriction_failures"] == []
    assert case["candidate_antitone_failures"] == []
    assert case["robust_restriction_failures"] == []
    assert case["robust_implies_may_failures"] == []


def test_all_robust_witnesses_retain_complete_run_evidence() -> None:
    case = strict_joint_case()
    positive = robust_positive_case()
    assert case["complete_full_run_evidence"] is True
    assert case["complete_north_run_evidence"] is True
    assert positive["complete_run_evidence"] is True


def test_pair_and_triple_queries_share_the_full_scope() -> None:
    case = strict_joint_case()
    assert case["pair_triple_scope_match"] is True
    assert case["full_triple_fiber"].environment_ids == FULL_ENVIRONMENTS


def test_strict_policy_table_is_total_and_exact() -> None:
    fixture = strict_joint_fixture()
    runs = fixture["runs"]
    assert len(runs.outcome_rows) == (
        len(runs.policy_ids) * len(runs.environment_ids)
    )
    assert runs.witness_for("p_try", "north") == "w_abc"
    assert runs.witness_for("p_try", "south") == "w_ab"


def test_summary_retains_every_preregistered_case() -> None:
    summary = robust_joint_separation_summary()
    assert summary["status"] == "retained"
    assert (
        summary["verdict"]
        == "joint_realizability_does_not_imply_joint_robust_securability"
    )
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert "moral license" in summary["claim_boundary"]


def test_artifact_rows_retain_fibers_runs_scopes_and_controls() -> None:
    summary = robust_joint_separation_summary()
    assert any(
        row["nonempty"] and row["witness_ids"] == "w_abc"
        for row in may_fiber_rows(summary)
    )
    assert any(
        row["case"] == "strict_full"
        and row["family"]
        and not row["nonempty"]
        for row in robust_fiber_rows(summary)
    )
    assert len(policy_environment_run_rows(summary)) == 18
    assert environment_scope_rows(summary) == [
        {
            "scope": "north",
            "environment_ids": "north",
            "may_triple_witness_ids": "w_abc",
            "robust_triple": True,
            "triple_policy_ids": "p_try",
        },
        {
            "scope": "full",
            "environment_ids": "north|south",
            "may_triple_witness_ids": "w_abc",
            "robust_triple": False,
            "triple_policy_ids": "",
        },
    ]
    assert all(row["passed"] for row in structural_control_rows(summary))


def test_validation_retains_all_declared_artifacts(tmp_path: Path) -> None:
    result = retain_robust_joint_separation_v0(tmp_path)
    assert result["status"] == "retained"
    assert {
        path.name for path in tmp_path.iterdir()
    } == {
        "summary.json",
        "may_fibers.csv",
        "robust_fibers.csv",
        "policy_environment_runs.csv",
        "environment_scope.csv",
        "structural_controls.csv",
        "report.md",
    }
