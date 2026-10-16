import numpy as np
import pytest

from omega_v2.finite.interaction_selected_history import (
    competing_case,
    environment_preparation_control,
    physical_orientation_control,
    representation_controls,
    single_axis_case,
)


@pytest.mark.parametrize("copies", [1, 2, 3])
def test_aligned_single_axis_selection_and_analytic_records(copies):
    g = 0.23
    result = single_axis_case(g, copies, angle=0.37)
    expected_overlap = np.cos(2 * g) ** copies
    assert result["selection"]["dimension"] == 1
    assert abs(result["selected_axis_alignment"] - 1) < 1e-10
    assert result["analytic_overlap_error"] < 1e-10
    assert result["analytic_coherence_error"] < 1e-10
    assert result["conditional_overlap_real"] == pytest.approx(expected_overlap, abs=1e-10)
    assert result["environment_trace_distance"] == pytest.approx(
        np.sqrt(1 - expected_overlap**2), abs=1e-10
    )


def test_zero_interaction_preserves_all_three_axes():
    result = single_axis_case(0, copies=2, angle=0.41)
    assert result["selection"]["dimension"] == 3


@pytest.mark.parametrize("mode", ["ZX", "XZ", "simultaneous"])
def test_competing_nonzero_interactions_select_no_axis(mode):
    result = competing_case(1, mode)
    assert result["selection"]["dimension"] == 0


@pytest.mark.parametrize("mode", ["ZX", "XZ", "simultaneous"])
def test_zero_competing_coupling_restores_one_conserved_axis(mode):
    result = competing_case(0, mode)
    assert result["selection"]["dimension"] == 1


@pytest.mark.parametrize("g, expected_records", [(np.pi / 4, 2), (np.pi / 2, 1)])
def test_single_axis_dephasing_and_revival_are_distinguished(g, expected_records):
    result = single_axis_case(g, copies=1)
    assert result["selection"]["dimension"] == 1
    assert result["record_breadth"] == pytest.approx(expected_records, abs=1e-10)
    assert result["analytic_overlap_error"] < 1e-10


def test_representation_controls_and_blank_ancilla_observables():
    result = representation_controls()
    assert max(result["errors"].values()) < 1e-10
    original, blank = result["original"], result["blank"]
    for key in ("record_breadth", "spectral_breadth", "record_probabilities"):
        assert blank[key] == pytest.approx(original[key], abs=1e-10)
    assert blank["observational_extent"] == pytest.approx(
        2 * original["observational_extent"], abs=1e-10
    )


def test_physical_orientation_control_keeps_z_reader_fixed():
    result = physical_orientation_control()
    assert result["Z"]["selection"]["dimension"] == 1
    assert result["X"]["selection"]["dimension"] == 1
    assert result["Z"]["readout"]["record_breadth"] == pytest.approx(1, abs=1e-10)
    assert result["X"]["readout"]["record_breadth"] == pytest.approx(2, abs=1e-10)


def test_conserved_axis_does_not_guarantee_a_record_for_every_environment_root():
    result = environment_preparation_control()
    assert result["Z_blank"]["environment_trace_distance"] == pytest.approx(1, abs=1e-10)
    assert result["Y_eigenstate"]["conditional_overlap_magnitude"] == pytest.approx(1, abs=1e-10)
    assert result["Y_eigenstate"]["environment_trace_distance"] == pytest.approx(0, abs=1e-10)
    assert result["Z_blank"]["spectral_breadth"] == pytest.approx(4, abs=1e-10)
    assert result["Y_eigenstate"]["spectral_breadth"] == pytest.approx(2, abs=1e-10)
    assert result["Z_blank"]["record_breadth"] == pytest.approx(2, abs=1e-10)
    assert result["Y_eigenstate"]["record_breadth"] == pytest.approx(2, abs=1e-10)
