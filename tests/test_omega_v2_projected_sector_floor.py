from __future__ import annotations

from pathlib import Path

import pytest

from omega_v2.experiments.projected_sector_floor_v0 import (
    commuting_diamond_fixture,
    commuting_diamond_rows,
    fixture_rows,
    genuine_nonconfluent_fixture,
    history_comparison_rows,
    janus_source_fixture,
    null_projection_fixture,
    one_sided_source_fixture,
    projected_component_rows,
    projected_sector_fixtures,
    projected_sector_floor_summary,
    projection_profile_rows,
    recurrent_cycle_fixture,
    sector_profile_rows,
    terminating_disintegration_fixture,
)
from omega_v2.finite.projected_sector import (
    DeclaredIndependence,
    FiniteHistory,
    FiniteProjection,
    FiniteTransitionSystem,
    ProjectionPolarity,
    audit_commuting_diamonds,
    histories_commute_in_audited_diamond,
    histories_exactly_equal,
    histories_project_to_same_levels,
    mutual_projected_reachability_is_equivalence,
    projected_components,
    projected_reachability_is_preorder,
    projected_reachability_rows,
    projection_profile,
    sector_profile,
)
from omega_v2.validation.projected_sector_floor_v0 import (
    retain_projected_sector_floor_v0,
)


def test_transition_system_accepts_partial_nondeterministic_relations() -> None:
    fixture = terminating_disintegration_fixture()

    assert fixture.system.successors("root") == ("left", "right")
    assert fixture.system.successors("dust") == ()
    assert fixture.system.reachable_from("root") == (
        "root",
        "left",
        "right",
        "dust",
    )


def test_transition_system_rejects_unknown_rows() -> None:
    with pytest.raises(ValueError, match="unknown state"):
        FiniteTransitionSystem(
            system_id="bad",
            states=("known",),
            labels=("step",),
            transitions=(("known", "step", "unknown"),),
        )


def test_projection_must_be_total_on_the_exact_interface() -> None:
    with pytest.raises(ValueError, match="total"):
        FiniteProjection(
            projection_id="partial",
            states=("left", "right"),
            rows=(("left", 0),),
        )


def test_projected_reach_is_a_preorder_and_mutual_reach_is_equivalence() -> None:
    for fixture in projected_sector_fixtures():
        assert projected_reachability_is_preorder(
            fixture.system,
            fixture.projection,
        )
        assert mutual_projected_reachability_is_equivalence(
            fixture.system,
            fixture.projection,
        )


def test_null_projection_retains_the_recurrent_cycle() -> None:
    fixture = null_projection_fixture()
    profile = projection_profile(fixture.system, fixture.projection)

    assert profile.polarity is ProjectionPolarity.NULL
    assert projected_components(
        fixture.system,
        fixture.projection,
    ) == (("a", "b"),)
    assert set(
        projected_reachability_rows(
            fixture.system,
            fixture.projection,
        )
    ) == {("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")}


def test_projection_controls_separate_one_sided_and_janus_sources() -> None:
    one_sided_fixture = one_sided_source_fixture()
    one_sided = projection_profile(
        one_sided_fixture.system,
        one_sided_fixture.projection,
    )
    janus_fixture = janus_source_fixture()
    janus = projection_profile(
        janus_fixture.system,
        janus_fixture.projection,
    )

    assert one_sided.polarity is ProjectionPolarity.POSITIVE_ONLY
    assert one_sided.projected_source_component_count == 1
    assert one_sided.projected_sink_component_count == 1
    assert janus.polarity is ProjectionPolarity.BIDIRECTIONAL
    assert janus.janus_sources == ("center",)


def test_termination_recurrence_and_confluence_are_separate() -> None:
    disintegration_fixture = terminating_disintegration_fixture()
    disintegration = sector_profile(
        disintegration_fixture.system,
        horizon=3,
        independence=disintegration_fixture.independence,
    )
    recurrent_fixture = recurrent_cycle_fixture()
    recurrent = sector_profile(
        recurrent_fixture.system,
        horizon=3,
        independence=recurrent_fixture.independence,
    )
    branch_fixture = genuine_nonconfluent_fixture()
    branch = sector_profile(
        branch_fixture.system,
        horizon=3,
        independence=branch_fixture.independence,
    )

    assert disintegration.terminating
    assert disintegration.locally_confluent
    assert disintegration.globally_confluent
    assert disintegration.recurrent_components == ()
    assert not recurrent.terminating
    assert recurrent.recurrent_components == (("a", "b"),)
    assert recurrent.branching_state_count == 0
    assert branch.terminating
    assert not branch.locally_confluent
    assert not branch.globally_confluent


def test_exact_projected_and_commuting_history_layers_do_not_collapse() -> None:
    fixture = commuting_diamond_fixture()
    audit = audit_commuting_diamonds(
        fixture.system,
        fixture.independence,
    )
    assert len(audit.diamonds) == 1
    diamond = audit.diamonds[0]

    assert not histories_exactly_equal(
        diamond.left_history,
        diamond.right_history,
    )
    assert histories_project_to_same_levels(
        diamond.left_history,
        fixture.projection,
        diamond.right_history,
        fixture.projection,
    )
    assert histories_commute_in_audited_diamond(
        diamond.left_history,
        diamond.right_history,
        audit,
    )
    assert audit.failures == ()


def test_declared_independence_failure_is_reported_not_merged() -> None:
    system = FiniteTransitionSystem(
        system_id="open_square",
        states=("root", "left", "right"),
        labels=("a", "b"),
        transitions=(("root", "a", "left"), ("root", "b", "right")),
    )
    audit = audit_commuting_diamonds(
        system,
        DeclaredIndependence(
            labels=system.labels,
            pairs=(("a", "b"),),
        ),
    )

    assert audit.opportunities == 1
    assert audit.diamonds == ()
    assert len(audit.failures) == 1


def test_invalid_history_is_rejected_against_the_system() -> None:
    fixture = one_sided_source_fixture()
    history = FiniteHistory(
        states=("s0", "s2"),
        labels=("step",),
    )

    with pytest.raises(ValueError, match="outside"):
        history.validate(fixture.system)


def test_summary_retains_every_preregistered_case_without_single_verdict() -> None:
    summary = projected_sector_floor_summary()

    assert summary["status"] == "retained"
    assert summary["verdict"] == (
        "projected_order_retained_and_sector_properties_separate"
    )
    assert summary["fixture_count"] == 7
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert "valuerhood" in summary["claim_boundary"]
    assert "coherent" not in summary
    assert "coherence" not in summary


def test_artifact_rows_cover_fixtures_profiles_components_and_histories() -> None:
    summary = projected_sector_floor_summary()

    assert len(fixture_rows(summary)) == 7
    assert len(sector_profile_rows(summary)) == 7
    assert len(projection_profile_rows(summary)) == 7
    assert len(projected_component_rows(summary)) >= 7
    assert len(history_comparison_rows(summary)) == 2
    assert commuting_diamond_rows(summary) == [
        {
            "fixture_id": "commuting_diamond",
            "source": "root",
            "left_label": "a",
            "right_label": "b",
            "left_state": "left",
            "right_state": "right",
            "target": "joined",
        }
    ]


def test_validation_retains_all_declared_artifacts(tmp_path: Path) -> None:
    result = retain_projected_sector_floor_v0(tmp_path)

    assert result["status"] == "retained"
    assert {path.name for path in tmp_path.iterdir()} == {
        "summary.json",
        "fixtures.csv",
        "sector_profiles.csv",
        "projection_profiles.csv",
        "projected_components.csv",
        "history_comparisons.csv",
        "commuting_diamonds.csv",
        "report.md",
    }
