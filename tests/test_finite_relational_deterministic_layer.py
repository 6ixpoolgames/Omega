from pathlib import Path

from omega.adapters.finite_relational import (
    all_binary_targets,
    all_observations,
    generate_deterministic_layer_study,
    minimal_sufficient_observation,
    observation_refines,
    recoverable_targets,
    target_recoverable_from_observation,
)
from omega.validation.finite_relational_deterministic_layer import (
    run_finite_relational_deterministic_layer,
)


REQUIRED_FAMILY_IDS = {
    "joint_bounded_recovery_panel_failure",
    "decoder_class_strictness",
    "observation_refinement_monotonicity",
    "deterministic_garbling_non_improvement",
    "minimal_sufficient_observation",
    "reflected_vs_stale_hidden_loss",
}


def test_deterministic_layer_covers_expected_pre_stochastic_families() -> None:
    families = generate_deterministic_layer_study()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS

    joint = by_id["joint_bounded_recovery_panel_failure"].metrics
    assert joint["target_first_recoverable_from_first_observation"] is True
    assert joint["target_second_recoverable_from_second_observation"] is True
    assert joint["joint_recoverable_from_first_observation"] is False
    assert joint["joint_recoverable_from_second_observation"] is False
    assert joint["individual_recovery_implies_joint_recovery"] is False

    decoder = by_id["decoder_class_strictness"].metrics
    assert decoder["recoverable_by_weak_class"] is False
    assert decoder["recoverable_by_rich_class"] is True
    assert decoder["weak_decoder_count"] == 2
    assert decoder["rich_decoder_count"] == 4

    refinement = by_id["observation_refinement_monotonicity"].metrics
    assert refinement["finer_refines_coarse"] is True
    assert refinement["coarse_recoverable_target_count"] == 4
    assert refinement["finer_recoverable_target_count"] == 16
    assert refinement["coarse_targets_subset_of_finer_targets"] is True

    garbling = by_id["deterministic_garbling_non_improvement"].metrics
    assert garbling["source_refines_garbled"] is True
    assert garbling["source_recoverable_target_count"] == 16
    assert garbling["garbled_recoverable_target_count"] == 4
    assert garbling["garbled_targets_subset_of_source_targets"] is True

    minimal = by_id["minimal_sufficient_observation"].metrics
    assert minimal["minimal_recovers_target"] is True
    assert minimal["enumerated_observation_count"] == 256
    assert minimal["recovering_observation_count"] == 84
    assert minimal["all_recovering_observations_refine_minimal"] is True

    hidden_loss = by_id["reflected_vs_stale_hidden_loss"].metrics
    assert hidden_loss["before_path"] is True
    assert hidden_loss["after_path"] is False
    assert hidden_loss["stale_abstraction_hidden_loss"] is True
    assert hidden_loss["reflected_abstraction_hidden_loss"] is False
    assert hidden_loss["reflected_abstraction_reports_lost_path"] is False


def test_minimal_sufficient_observation_is_coarsest_exact_binary_observation() -> None:
    states = ("00", "01", "10", "11")
    target = frozenset({"10", "11"})
    minimal = minimal_sufficient_observation(states, target)
    observations = all_observations(states, ("l0", "l1", "l2", "l3"))
    recovering_observations = [
        observation
        for observation in observations
        if target_recoverable_from_observation(states, observation, target)
    ]

    assert target_recoverable_from_observation(states, minimal, target)
    assert len(all_binary_targets(states)) == 16
    assert len(recoverable_targets(states, minimal)) == 4
    assert len(recovering_observations) == 84
    assert all(
        observation_refines(states, observation, minimal)
        for observation in recovering_observations
    )


def test_deterministic_layer_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_deterministic_layer(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert family_dir.exists()
        assert (family_dir / "family_summary.json").exists()
