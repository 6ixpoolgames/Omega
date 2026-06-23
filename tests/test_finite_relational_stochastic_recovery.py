from fractions import Fraction
from pathlib import Path

from omega.adapters.finite_relational import (
    all_deterministic_decoders,
    compose_coarse_decoder_through_fine,
    generate_stochastic_recovery_study,
    optimized_worst_case_decoder,
    optimized_declared_randomized_worst_case_decoder,
    optimized_declared_robust_randomized_worst_case_decoder,
    optimized_robust_worst_case_decoder,
    paired_joint_union_bound_by_source,
    randomized_success_by_source,
    robust_randomized_success_by_channel,
    robust_worst_case_success,
    success_by_source,
    support_ambiguities,
    support_exact_recoverable,
    validate_channel,
    worst_case_success,
)
from omega.validation.finite_relational_stochastic_recovery import (
    run_finite_relational_stochastic_recovery,
)


REQUIRED_FAMILY_IDS = {
    "support_exact_vs_high_confidence",
    "same_support_different_probabilities",
    "declared_vs_optimized_decoder_gap",
    "coarsening_non_improvement",
    "coarse_decoder_simulable_by_fine",
    "same_worst_case_different_failure_localization",
    "same_marginal_success_different_joint_failure",
    "randomized_decoder_axis",
    "robust_randomized_ambiguity_axis",
}


def test_stochastic_recovery_covers_expected_characterization_families() -> None:
    families = generate_stochastic_recovery_study()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS

    support = by_id["support_exact_vs_high_confidence"].metrics
    assert support["exact_support_recoverable"] is True
    assert support["noisy_support_recoverable"] is False
    assert support["exact_best_worst_case_success"] == "1"
    assert support["noisy_best_worst_case_success"] == "99/100"
    assert support["noisy_support_ambiguity_count"] == 2

    same_support = by_id["same_support_different_probabilities"].metrics
    assert same_support["same_positive_support"] is True
    assert same_support["high_support_recoverable"] is False
    assert same_support["low_support_recoverable"] is False
    assert same_support["high_best_worst_case_success"] == "9/10"
    assert same_support["low_best_worst_case_success"] == "3/5"
    assert same_support["support_ambiguity_count"] == 2

    decoder_gap = by_id["declared_vs_optimized_decoder_gap"].metrics
    assert decoder_gap["declared_worst_case_success"] == "1/10"
    assert decoder_gap["optimized_worst_case_success"] == "9/10"
    assert decoder_gap["declared_per_source_success"] == {"x0": "1/10", "x1": "1/10"}
    assert decoder_gap["optimized_per_source_success"] == {"x0": "9/10", "x1": "9/10"}

    coarsening = by_id["coarsening_non_improvement"].metrics
    assert coarsening["fine_refines_coarse"] is True
    assert coarsening["fine_support_recoverable"] is True
    assert coarsening["coarse_support_recoverable"] is False
    assert coarsening["fine_best_worst_case_success"] == "1"
    assert coarsening["coarse_best_worst_case_success"] == "0"
    assert coarsening["coarse_best_no_greater_than_fine_best"] is True

    simulable = by_id["coarse_decoder_simulable_by_fine"].metrics
    assert simulable["fine_refines_coarse"] is True
    assert simulable["same_success_after_composition"] is True
    assert simulable["coarse_per_source_success"] == {"x0": "1", "x1": "1"}
    assert simulable["fine_composed_per_source_success"] == {"x0": "1", "x1": "1"}

    localization = by_id["same_worst_case_different_failure_localization"].metrics
    assert localization["same_worst_case_success"] is True
    assert localization["same_per_source_success_vector"] is False
    assert localization["balanced_worst_case_success"] == "4/5"
    assert localization["localized_worst_case_success"] == "4/5"
    assert localization["balanced_per_source_success"] == {"x0": "4/5", "x1": "4/5"}
    assert localization["localized_per_source_success"] == {"x0": "1", "x1": "4/5"}

    joint = by_id["same_marginal_success_different_joint_failure"].metrics
    assert joint["same_marginal_worst_case_success"] is True
    assert joint["same_joint_worst_case_success"] is False
    assert joint["independent_first_worst_case_success"] == "5/6"
    assert joint["independent_second_worst_case_success"] == "5/6"
    assert joint["correlated_first_worst_case_success"] == "5/6"
    assert joint["correlated_second_worst_case_success"] == "5/6"
    assert joint["independent_joint_worst_case_success"] == "3/4"
    assert joint["correlated_joint_worst_case_success"] == "5/6"
    assert joint["independent_union_bound_worst_case"] == "2/3"
    assert joint["correlated_union_bound_worst_case"] == "2/3"
    assert joint["independent_union_bound_by_source"] == {
        "00": "2/3",
        "01": "2/3",
        "10": "2/3",
        "11": "2/3",
    }
    assert joint["correlated_union_bound_by_source"] == {
        "00": "2/3",
        "01": "2/3",
        "10": "2/3",
        "11": "2/3",
    }
    assert joint["independent_joint_meets_union_bound"] is True
    assert joint["correlated_joint_meets_union_bound"] is True

    randomized = by_id["randomized_decoder_axis"].metrics
    assert randomized["deterministic_optimized_worst_case_success"] == "0"
    assert randomized["declared_randomized_worst_case_success"] == "1/2"
    assert randomized["declared_randomized_per_source_success"] == {"x0": "1/2", "x1": "1/2"}
    assert randomized["optimized_declared_randomized_family_decoder"] == "uniform"
    assert randomized["optimized_declared_randomized_family_worst_case_success"] == "1/2"
    assert randomized["optimized_declared_randomized_family_per_source_success"] == {
        "x0": "1/2",
        "x1": "1/2",
    }
    assert randomized["randomized_beats_deterministic_maximin"] is True

    robust_randomized = by_id["robust_randomized_ambiguity_axis"].metrics
    assert robust_randomized["per_channel_deterministic_worst_case_success"] == {
        "flipped": "1",
        "identity": "1",
    }
    assert robust_randomized["optimized_deterministic_robust_worst_case_success"] == "0"
    assert robust_randomized["declared_randomized_robust_worst_case_success"] == "1/2"
    assert robust_randomized["declared_randomized_robust_per_channel_success"] == {
        "flipped": {"x0": "1/2", "x1": "1/2"},
        "identity": {"x0": "1/2", "x1": "1/2"},
    }
    assert (
        robust_randomized["optimized_declared_robust_randomized_family_decoder"]
        == "uniform"
    )
    assert (
        robust_randomized[
            "optimized_declared_robust_randomized_family_worst_case_success"
        ]
        == "1/2"
    )
    assert robust_randomized[
        "optimized_declared_robust_randomized_family_per_channel_success"
    ] == {
        "flipped": {"x0": "1/2", "x1": "1/2"},
        "identity": {"x0": "1/2", "x1": "1/2"},
    }
    assert robust_randomized["per_channel_exact_but_not_deterministically_robust"] is True
    assert robust_randomized["randomized_beats_deterministic_robust_maximin"] is True


def test_stochastic_helpers_use_exact_rational_probabilities() -> None:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    channel = {
        "x0": {"y0": Fraction(9, 10), "y1": Fraction(1, 10)},
        "x1": {"y0": Fraction(1, 10), "y1": Fraction(9, 10)},
    }
    observation = {"y0": "left", "y1": "right"}
    target = {"x0": "false", "x1": "true"}

    validate_channel(states, outputs, channel)
    ambiguities = support_ambiguities(states, outputs, channel, observation, target)
    result = optimized_worst_case_decoder(states, outputs, channel, observation, target)

    assert support_exact_recoverable(states, outputs, channel, observation, target) is False
    assert len(ambiguities) == 2
    assert result.decoder == {"left": "false", "right": "true"}
    assert result.worst_case_success == Fraction(9, 10)
    assert result.per_source_success == {"x0": Fraction(9, 10), "x1": Fraction(9, 10)}
    assert len(all_deterministic_decoders(("left", "right"), ("false", "true"))) == 4


def test_coarse_decoder_composition_preserves_success_from_fine_observation() -> None:
    states = ("x0", "x1")
    outputs = ("a0", "a1", "b0", "b1")
    channel = {
        "x0": {
            "a0": Fraction(1, 2),
            "a1": Fraction(1, 2),
            "b0": Fraction(0),
            "b1": Fraction(0),
        },
        "x1": {
            "a0": Fraction(0),
            "a1": Fraction(0),
            "b0": Fraction(1, 2),
            "b1": Fraction(1, 2),
        },
    }
    target = {"x0": "false", "x1": "true"}
    fine = {"a0": "a0", "a1": "a1", "b0": "b0", "b1": "b1"}
    coarse = {"a0": "a", "a1": "a", "b0": "b", "b1": "b"}
    coarse_decoder = {"a": "false", "b": "true"}
    fine_decoder = compose_coarse_decoder_through_fine(
        outputs,
        fine,
        coarse,
        coarse_decoder,
    )

    assert fine_decoder == {"a0": "false", "a1": "false", "b0": "true", "b1": "true"}
    assert success_by_source(states, outputs, channel, coarse, target, coarse_decoder) == (
        success_by_source(states, outputs, channel, fine, target, fine_decoder)
    )


def test_declared_randomized_decoder_axis_is_exact_but_not_general_optimization() -> None:
    states = ("x0", "x1")
    outputs = ("same",)
    channel = {
        "x0": {"same": Fraction(1)},
        "x1": {"same": Fraction(1)},
    }
    observation = {"same": "observed"}
    target = {"x0": "false", "x1": "true"}
    randomized_decoder = {"observed": {"false": Fraction(1, 2), "true": Fraction(1, 2)}}

    deterministic = optimized_worst_case_decoder(states, outputs, channel, observation, target)
    randomized = randomized_success_by_source(
        states,
        outputs,
        channel,
        observation,
        target,
        randomized_decoder,
    )

    assert deterministic.worst_case_success == Fraction(0)
    assert randomized == {"x0": Fraction(1, 2), "x1": Fraction(1, 2)}
    assert worst_case_success(randomized) == Fraction(1, 2)


def test_paired_joint_union_bound_profile_is_source_indexed() -> None:
    first = {"x0": Fraction(5, 6), "x1": Fraction(3, 4)}
    second = {"x0": Fraction(2, 3), "x1": Fraction(4, 5)}

    assert paired_joint_union_bound_by_source(first, second) == {
        "x0": Fraction(1, 2),
        "x1": Fraction(11, 20),
    }


def test_declared_randomized_family_optimizer_is_exact_enumeration() -> None:
    states = ("x0", "x1")
    outputs = ("same",)
    channel = {
        "x0": {"same": Fraction(1)},
        "x1": {"same": Fraction(1)},
    }
    observation = {"same": "observed"}
    target = {"x0": "false", "x1": "true"}
    decoders = {
        "always_false": {"observed": {"false": Fraction(1), "true": Fraction(0)}},
        "always_true": {"observed": {"false": Fraction(0), "true": Fraction(1)}},
        "uniform": {"observed": {"false": Fraction(1, 2), "true": Fraction(1, 2)}},
    }

    optimized = optimized_declared_randomized_worst_case_decoder(
        states,
        outputs,
        channel,
        observation,
        target,
        decoders,
    )

    assert optimized.decoder_name == "uniform"
    assert optimized.worst_case_success == Fraction(1, 2)
    assert optimized.per_source_success == {"x0": Fraction(1, 2), "x1": Fraction(1, 2)}


def test_robust_randomized_axis_uses_one_decoder_over_ambiguity_set() -> None:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    channels = {
        "flipped": {
            "x0": {"y0": Fraction(0), "y1": Fraction(1)},
            "x1": {"y0": Fraction(1), "y1": Fraction(0)},
        },
        "identity": {
            "x0": {"y0": Fraction(1), "y1": Fraction(0)},
            "x1": {"y0": Fraction(0), "y1": Fraction(1)},
        },
    }
    observation = {"y0": "left", "y1": "right"}
    target = {"x0": "false", "x1": "true"}
    randomized_decoder = {
        "left": {"false": Fraction(1, 2), "true": Fraction(1, 2)},
        "right": {"false": Fraction(1, 2), "true": Fraction(1, 2)},
    }

    deterministic = optimized_robust_worst_case_decoder(
        states,
        outputs,
        channels,
        observation,
        target,
    )
    randomized = robust_randomized_success_by_channel(
        states,
        outputs,
        channels,
        observation,
        target,
        randomized_decoder,
    )

    assert deterministic.robust_worst_case_success == Fraction(0)
    assert randomized == {
        "flipped": {"x0": Fraction(1, 2), "x1": Fraction(1, 2)},
        "identity": {"x0": Fraction(1, 2), "x1": Fraction(1, 2)},
    }
    assert robust_worst_case_success(randomized) == Fraction(1, 2)


def test_declared_robust_randomized_family_optimizer_is_exact_enumeration() -> None:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    channels = {
        "flipped": {
            "x0": {"y0": Fraction(0), "y1": Fraction(1)},
            "x1": {"y0": Fraction(1), "y1": Fraction(0)},
        },
        "identity": {
            "x0": {"y0": Fraction(1), "y1": Fraction(0)},
            "x1": {"y0": Fraction(0), "y1": Fraction(1)},
        },
    }
    observation = {"y0": "left", "y1": "right"}
    target = {"x0": "false", "x1": "true"}
    decoders = {
        "flipped_point_mass": {
            "left": {"false": Fraction(0), "true": Fraction(1)},
            "right": {"false": Fraction(1), "true": Fraction(0)},
        },
        "identity_point_mass": {
            "left": {"false": Fraction(1), "true": Fraction(0)},
            "right": {"false": Fraction(0), "true": Fraction(1)},
        },
        "uniform": {
            "left": {"false": Fraction(1, 2), "true": Fraction(1, 2)},
            "right": {"false": Fraction(1, 2), "true": Fraction(1, 2)},
        },
    }

    optimized = optimized_declared_robust_randomized_worst_case_decoder(
        states,
        outputs,
        channels,
        observation,
        target,
        decoders,
    )

    assert optimized.decoder_name == "uniform"
    assert optimized.robust_worst_case_success == Fraction(1, 2)
    assert optimized.per_channel_success == {
        "flipped": {"x0": Fraction(1, 2), "x1": Fraction(1, 2)},
        "identity": {"x0": Fraction(1, 2), "x1": Fraction(1, 2)},
    }


def test_stochastic_recovery_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_stochastic_recovery(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert family_dir.exists()
        assert (family_dir / "family_summary.json").exists()
