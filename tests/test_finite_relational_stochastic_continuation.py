from fractions import Fraction
from pathlib import Path

from omega.adapters.finite_relational import (
    distribution_after_horizon,
    generate_stochastic_continuation_loss_study,
    hit_probability_within_horizon,
    validate_transition_kernel,
)
from omega.validation.finite_relational_stochastic_continuation import (
    run_finite_relational_stochastic_continuation,
)


REQUIRED_FAMILY_IDS = {
    "noisy_line_grid_stale_hidden_hit_loss",
    "same_hit_probability_different_horizon_profile",
}


def test_stochastic_continuation_loss_covers_expected_families() -> None:
    families = generate_stochastic_continuation_loss_study()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS

    hidden = by_id["noisy_line_grid_stale_hidden_hit_loss"].metrics
    assert hidden["horizon"] == 2
    assert hidden["before_hit_probability"] == "9/10"
    assert hidden["after_hit_probability"] == "1/10"
    assert hidden["loss_amount"] == "4/5"
    assert hidden["stale_abstraction_hit_probability"] == "9/10"
    assert hidden["reflected_abstraction_hit_probability"] == "1/10"
    assert hidden["stale_hides_loss"] is True
    assert hidden["reflected_reports_loss"] is True

    profile = by_id["same_hit_probability_different_horizon_profile"].metrics
    assert profile["fast_horizon_1_hit_probability"] == "3/4"
    assert profile["slow_horizon_2_hit_probability"] == "3/4"
    assert profile["same_selected_hit_probability"] is True
    assert profile["same_profile"] is False
    assert profile["fast_profile"] == {"1": "3/4", "2": "3/4", "3": "3/4"}
    assert profile["slow_profile"] == {"1": "1/2", "2": "3/4", "3": "7/8"}


def test_finite_horizon_hit_probability_uses_exact_rational_markov_kernel() -> None:
    states = ("x0", "x1", "x2")
    kernel = {
        "x0": {"x0": Fraction(0), "x1": Fraction(1), "x2": Fraction(0)},
        "x1": {"x0": Fraction(0), "x1": Fraction(1, 10), "x2": Fraction(9, 10)},
        "x2": {"x0": Fraction(0), "x1": Fraction(0), "x2": Fraction(1)},
    }

    validate_transition_kernel(states, kernel)
    assert distribution_after_horizon(states, kernel, "x0", 1) == {
        "x0": Fraction(0),
        "x1": Fraction(1),
        "x2": Fraction(0),
    }
    assert hit_probability_within_horizon(
        states,
        kernel,
        "x0",
        frozenset({"x2"}),
        2,
    ) == Fraction(9, 10)


def test_stochastic_continuation_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_stochastic_continuation(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert family_dir.exists()
        assert (family_dir / "family_summary.json").exists()
