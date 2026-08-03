from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from omega_v2.experiments.robust_omega_v0 import (
    DeterministicEnvironmentScenario,
    may_migration_case,
    robust_hollow_triangle_case,
    robust_omega_summary,
    robust_positive_control_case,
)
from omega_v2.finite.model import (
    ControlledMarkovSystem,
    DeterministicPolicy,
)
from omega_v2.finite.realization import (
    FiniteOmega,
    FiniteRealizationRelation,
    PolicyEnvironmentRuns,
)
from omega_v2.validation.robust_omega_v0 import (
    render_report,
    run_robust_omega_v0,
)


def test_clean_may_port_matches_retained_legacy_payload() -> None:
    case = may_migration_case()

    assert case["legacy_parity"]
    assert case["pair_fibers"] == {
        "AB": ["history:a0"],
        "AC": ["history:a1"],
        "BC": ["history:a2"],
    }
    assert case["triple_witness_ids"] == []
    assert case["maximal_face_count"] == 3
    assert not case["greatest_face_exists"]
    assert case["downward_closure_failures"] == []
    assert case["restriction_failures"] == []


def test_exact_candidate_duplicate_does_not_change_may_payload() -> None:
    case = may_migration_case()

    assert case["raw_candidate_count"] == 3
    assert case["duplicate_raw_candidate_count"] == 4
    assert case["quotient_candidate_count"] == 3
    assert case["duplicate_quotient_candidate_count"] == 3
    assert case["duplicate_invariant"]


def test_policy_environment_table_requires_total_deterministic_product() -> None:
    with pytest.raises(ValueError, match="total on the product"):
        PolicyEnvironmentRuns(
            table_id="partial",
            policy_ids=("p0",),
            environment_ids=("e0", "e1"),
            witness_ids=("w0",),
            outcome_rows=(("p0", "e0", "w0"),),
        )

    with pytest.raises(ValueError, match="functional"):
        PolicyEnvironmentRuns(
            table_id="duplicate",
            policy_ids=("p0",),
            environment_ids=("e0",),
            witness_ids=("w0",),
            outcome_rows=(
                ("p0", "e0", "w0"),
                ("p0", "e0", "w0"),
            ),
        )


def test_empty_environment_scope_is_rejected() -> None:
    relation = FiniteRealizationRelation(
        relation_id="single",
        candidate_ids=("A",),
        witness_ids=("w",),
        incidence_rows=(("A", "w"),),
    )
    runs = PolicyEnvironmentRuns(
        table_id="single",
        policy_ids=("p",),
        environment_ids=("e",),
        witness_ids=("w",),
        outcome_rows=(("p", "e", "w"),),
    )

    with pytest.raises(ValueError, match="must be nonempty"):
        FiniteOmega.from_relation(relation, runs, environment_ids=())


def test_deterministic_adapter_rejects_stochastic_selected_rows() -> None:
    system = ControlledMarkovSystem(
        system_id="stochastic",
        states=("start", "left", "right"),
        actions=("step",),
        transitions=(
            ("start", "step", "left", Fraction(1, 2)),
            ("start", "step", "right", Fraction(1, 2)),
            ("left", "step", "left", Fraction(1)),
            ("right", "step", "right", Fraction(1)),
        ),
    )
    scenario = DeterministicEnvironmentScenario(
        "stochastic",
        system,
        "start",
        1,
    )
    policy = DeterministicPolicy(
        policy_id="step",
        rows=tuple((state, "step") for state in system.states),
    )

    from omega_v2.experiments.robust_omega_v0 import deterministic_rollout

    with pytest.raises(ValueError, match="point-mass"):
        deterministic_rollout(scenario, policy)


def test_may_compatibility_need_not_be_robust() -> None:
    summary = robust_omega_summary()
    sensitivity = summary["environment_sensitivity"]

    assert sensitivity["may_compatible"]
    assert sensitivity["robust_calm"]
    assert not sensitivity["robust_full"]
    assert sensitivity["calm_policy_ids"] == ["policy_fragile"]
    assert sensitivity["full_policy_ids"] == []


def test_robustness_is_antitone_in_environment_scope() -> None:
    summary = robust_omega_summary()
    sensitivity = summary["environment_sensitivity"]

    assert sensitivity["environment_antitone_failures"] == []
    assert sensitivity["candidate_classes_stable"]


def test_robust_hollow_triangle_retains_every_securing_policy() -> None:
    case = robust_hollow_triangle_case()

    assert case["all_pairs_robust"]
    assert not case["triple_robust"]
    assert case["pair_policy_ids"] == {
        "AB": ["policy_ab"],
        "AC": ["policy_ac"],
        "BC": ["policy_bc"],
    }
    assert case["triple_policy_ids"] == []
    assert case["robust_maximal_face_count"] == 3
    assert {
        fiber.environment_ids for fiber in case["pair_fibers"].values()
    } == {("north", "south")}
    assert all(
        len(fiber.securing_witnesses[0].environment_runs) == 2
        for fiber in case["pair_fibers"].values()
    )


def test_robust_positive_control_retains_triple_witness_bundle() -> None:
    case = robust_positive_control_case()

    assert case["triple_robust"]
    assert case["triple_policy_ids"] == ["policy_abc"]
    assert case["triple_environment_runs"] == [
        {
            "policy_id": "policy_abc",
            "environment_runs": [
                {
                    "environment_id": "north",
                    "witness_id": (
                        "run:robust_triangle_positive:policy_abc:north"
                    ),
                },
                {
                    "environment_id": "south",
                    "witness_id": (
                        "run:robust_triangle_positive:policy_abc:south"
                    ),
                },
            ],
        }
    ]


def test_robust_fibers_obey_candidate_and_restriction_laws() -> None:
    case = robust_hollow_triangle_case()

    assert case["candidate_antitone_failures"] == []
    assert case["restriction_failures"] == []
    assert case["robust_implies_may_failures"] == []
    assert case["duplicate_invariant"]


def test_generated_run_tables_match_fresh_rollouts() -> None:
    summary = robust_omega_summary()

    assert summary["case_results"]["generated_run_crosscheck"]
    assert not summary["kill_conditions"]["generated_run_table_mismatch"]


def test_summary_retains_all_preregistered_construction_controls() -> None:
    summary = robust_omega_summary()

    assert summary["status"] == "retained"
    assert summary["verdict"] == "finite_may_and_robust_realization_core_retained"
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert summary["semantics"] == {
        "policy_quantifier": "exists",
        "environment_quantifier": "forall",
        "run_semantics": (
            "one_deterministic_finite_run_per_policy_environment"
        ),
        "environment_scope_nonempty": True,
    }
    assert summary["case_results"]["empty_environment_scope_rejected"]
    assert summary["case_results"]["partial_outcome_table_rejected"]
    assert summary["case_results"]["multivalued_outcome_table_rejected"]
    assert not summary["kill_conditions"]["empty_environment_scope_admitted"]
    assert not summary["kill_conditions"]["partial_outcome_table_admitted"]
    assert not summary["kill_conditions"]["multivalued_outcome_table_admitted"]
    assert "moral license" in summary["claim_boundary"]


def test_validation_writes_every_preregistered_artifact(
    tmp_path: Path,
) -> None:
    result = run_robust_omega_v0(out_root=tmp_path)
    run_root = Path(result["run_root"])

    assert result["status"] == "retained"
    assert {path.name for path in run_root.iterdir()} == {
        "summary.json",
        "case_results.csv",
        "candidate_classes.csv",
        "may_fibers.csv",
        "robust_fibers.csv",
        "policy_environment_runs.csv",
        "environment_sensitivity.csv",
        "report.md",
    }
    report = render_report(result)
    assert "Pairwise Robust: True" in report
    assert "Triple Robust: False" in report
    assert "Legacy parity: True" in report
