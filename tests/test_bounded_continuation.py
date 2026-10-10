import numpy as np
import pytest

from omega_v2.finite.bounded_continuation import (
    echo_profiles,
    ensemble_controls,
    eraser_profile,
    holevo_extent,
    recorded_profile,
)
from omega_v2.finite.quantum_extent import effective_number


def test_internal_mixedness_is_not_alternative_breadth():
    controls = ensemble_controls()
    assert controls["identical_mixed"]["extent"] == pytest.approx(1)
    assert controls["identical_mixed"]["output_entropy"] > 0
    orthogonal = controls["orthogonal_mixed"]
    assert orthogonal["extent"] == pytest.approx(effective_number([.3, .7]))
    for key, value in controls.items():
        if key.endswith("_error"):
            assert value < 1e-12


@pytest.mark.parametrize("p", [.1, .5, .9])
def test_binary_overlap_matches_analytic_spectrum(p):
    for c in (0., .3, .8, 1.):
        vector = np.array([c, np.sqrt(1-c*c)])
        result = holevo_extent([p, 1-p], [np.diag([1., 0.]), np.outer(vector, vector)])
        gap = np.sqrt(1-4*p*(1-p)*(1-c*c))
        expected = effective_number([(1+gap)/2, (1-gap)/2])
        assert result["extent"] == pytest.approx(expected)
        assert result["bound_error"] < 1e-12


def test_eraser_changes_record_location_without_erasing_global_conditionals():
    for leak in (0., np.pi/6, np.pi/2):
        for mode in ("retain", "eraser_early", "eraser_delayed"):
            row = eraser_profile(mode, leak)
            assert row["joint_record"]["extent"] == pytest.approx(2)
        undone = eraser_profile("reverse_all", leak)
        assert undone["joint_record"]["extent"] == pytest.approx(1)
        assert undone["whole_conditional_system"]["extent"] == pytest.approx(2)
        partial = eraser_profile("reverse_marker", leak)
        assert partial["marker"]["extent"] == pytest.approx(1)
        expected = effective_number([(1+np.cos(leak))/2, (1-np.cos(leak))/2])
        assert partial["joint_record"]["extent"] == pytest.approx(expected)


def test_certified_classical_history_growth_has_no_initial_dimension_ceiling():
    for count in (1, 2, 3):
        result = recorded_profile(count)
        assert result["extent"] == pytest.approx(2**count)
        assert result["record_certificate_error"] < 1e-12
        assert result["refinement_error"] < 1e-12
    # Actual reduced-state entropy is a different quantity from history breadth.
    assert recorded_profile(3)["actual_output_entropy"] == pytest.approx(np.log(2))


def test_bounds_do_not_fix_fictitious_checkpoint_alternatives():
    rows = echo_profiles()
    assert rows["endpoint"]["extent"] == pytest.approx(1)
    assert rows["refined"]["extent"] == pytest.approx(2)
    assert rows["refined"]["bound_error"] < 1e-12
    assert rows["refined"]["proposed_record_certificate_error"] > .1
    assert rows["coherently_grouped"]["extent"] == pytest.approx(1)
    assert rows["grouped_record_certificate_error"] < 1e-12


def test_invalid_probabilities_and_states_are_rejected():
    with pytest.raises(ValueError):
        holevo_extent([.2, .2], [np.eye(2)/2]*2)
    with pytest.raises(ValueError):
        holevo_extent([1.], [np.eye(2)])
    with pytest.raises(ValueError):
        holevo_extent([1.], [np.diag([1.1, -.1])])
