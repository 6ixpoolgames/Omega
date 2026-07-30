from pathlib import Path

import pytest

from omega.adapters.finite_relational.canonical_process_monitors import (
    CertifiedObservationInterface,
    PropertyAutomaton,
    ancestry_match_automaton,
    build_process_lift,
    canonical_minimization_witness,
    canonical_process_monitors_summary,
    direct_emission_control_witness,
    lift_path,
    lifting_and_projection_witness,
    minimize_property_automaton,
    observation_equivariance_witness,
    property_family_residue_witness,
    shared_fork_histories,
    shared_fork_system,
    symmetric_copy_witness,
    unique_step_lift_failures,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_canonical_process_monitors import (
    render_report,
    run_finite_relational_canonical_process_monitors,
)


def test_observation_interface_is_state_and_action_relabel_equivariant() -> None:
    witness = observation_equivariance_witness()

    assert witness["edge_count"] > 0
    assert witness["mismatches"] == []
    assert witness["equivariant"] is True


def test_property_automaton_requires_total_deterministic_update() -> None:
    system, observation = shared_fork_system()
    alphabet = observation.alphabet(system)

    with pytest.raises(ValueError, match="must be total"):
        PropertyAutomaton(
            property_id="incomplete",
            states=("q",),
            alphabet=alphabet,
            initial_state="q",
            transitions=(),
            outputs=(("q", frozenset()),),
        )

    duplicate = tuple(("q", symbol, "q") for symbol in alphabet)
    with pytest.raises(ValueError, match="must be deterministic"):
        PropertyAutomaton(
            property_id="nondeterministic",
            states=("q",),
            alphabet=alphabet,
            initial_state="q",
            transitions=duplicate + (duplicate[0],),
            outputs=(("q", frozenset()),),
        )


def test_redundant_property_presentations_minimize_identically() -> None:
    witness = canonical_minimization_witness()

    assert witness["redundant_state_count"] > witness["compact_state_count"]
    assert witness["redundant_minimal_state_count"] == witness["compact_minimal_state_count"]
    assert witness["canonical_payloads_equal"] is True


def test_passive_product_has_unique_step_and_path_lifting() -> None:
    system, observation = shared_fork_system()
    monitor = minimize_property_automaton(ancestry_match_automaton(system, observation))
    lift = build_process_lift(
        system,
        monitor,
        observation,
        initial_world_state="origin",
    )
    alpha_path, _beta_path = shared_fork_histories()

    assert unique_step_lift_failures(lift) == []
    lifted_nodes = lift_path(lift, monitor.initial_state, alpha_path)
    assert [node.world_state for node in lifted_nodes] == ["origin", "hub"]


def test_world_only_lift_preserves_projected_behavior() -> None:
    witness = lifting_and_projection_witness()

    assert witness["unique_step_lift_failures"] == []
    assert witness["unique_path_lifting"] is True
    assert witness["projection_conservation_failures"] == []
    assert witness["projection_conserved"] is True


def test_direct_emitted_label_does_not_count_as_history_residue() -> None:
    witness = direct_emission_control_witness()

    assert witness["base_profiles_equal"] is True
    assert witness["current_emits_equal"] is False
    assert witness["direct_profile_difference_visible"] is True
    assert witness["history_residue"] is False
    assert witness["direct_emission_excluded"] is True


def test_property_family_reports_relative_and_family_core_residue_exactly() -> None:
    witness = property_family_residue_witness()

    assert witness["history_residue_vector"] == {
        "ancestry_match": True,
        "completion": False,
        "fixed_hazard": False,
    }
    assert witness["corridor_residue_vector"] == {
        "ancestry_match": True,
        "completion": False,
        "fixed_hazard": False,
    }
    assert witness["family_core_history_residue"] is False
    assert witness["family_core_corridor_residue"] is False
    assert witness["classification"] == "family-dependent"


def test_symmetric_copy_cannot_be_split_by_raw_identifiers() -> None:
    witness = symmetric_copy_witness()

    assert witness["branch_observations_equal"] is True
    assert witness["monitor_states_equal"] is True
    assert witness["history_residue"] is False
    assert witness["verdict"] == "unresolved"


def test_action_classes_must_be_total() -> None:
    system, _observation = shared_fork_system()
    incomplete = CertifiedObservationInterface(
        interface_id="incomplete",
        action_classes=(("route_alpha", "route"),),
    )

    with pytest.raises(ValueError, match="must be total"):
        incomplete.validate(system)


def test_summary_separates_correctness_and_risky_finite_result() -> None:
    summary = canonical_process_monitors_summary()

    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert summary["cases"]["property_family_residue"]["classification"] == ("family-dependent")
    assert "PM8_family_classification" in summary["evidence_classification"]["risky_finite_result"]
    assert "identity" in summary["not_claimed"]


def test_validation_retains_machine_readable_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_canonical_process_monitors(out_root=tmp_path)

    assert result["status"] == "PASS"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "case_results.csv").exists()
    assert (run_root / "residue_results.csv").exists()
    assert (run_root / "lift_results.csv").exists()
    assert (run_root / "report.md").exists()

    residue_rows = read_csv(run_root / "residue_results.csv")
    assert {row["property"] for row in residue_rows} == {
        "ancestry_match",
        "completion",
        "fixed_hazard",
    }

    report = render_report(result)
    assert "Canonical Process Monitors v0 Report" in report
    assert "Family classification: family-dependent" in report
