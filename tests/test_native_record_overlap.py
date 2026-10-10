import numpy as np
import pytest

from omega_v2.finite.coherent_reference import recorded_hops
from omega_v2.finite.native_record_overlap import (
    analyze_records,
    delayed_record_echo,
    overlap_controls,
    record_copy_control,
)
from omega_v2.finite.quantum_extent import effective_number
from omega_v2.finite.spatial_futuresfield import spatial_setup


def test_conditional_record_overlap_interpolation():
    for phi in [0., np.pi/6, np.pi/4, np.pi/2]:
        r, _, _ = analyze_records(*spatial_setup(np.pi/4, 0., phi), (1,), 2)
        expected = effective_number([(1+np.cos(phi))/2, (1-np.cos(phi))/2])
        assert r["overlap_extent"] == pytest.approx(expected)
        assert r["actual_record_rank_extent"] == pytest.approx(expected)


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_recorded_history_growth_versus_actual_memory_rank(n):
    psi, _, stages = recorded_hops(n)
    r, _, _ = analyze_records(psi, stages, range(1, n+1), n+1)
    assert r["overlap_extent"] == pytest.approx(2**n)
    assert r["actual_record_rank_extent"] == pytest.approx(2)
    assert r["record_basis_breadth"] == pytest.approx(2**n)


def test_math_checkpoint_changes_candidate_without_changing_physics():
    coarse, ac, _ = analyze_records(*delayed_record_echo(False), (1,), 2)
    fine, af, _ = analyze_records(*delayed_record_echo(True), (1,), 2)
    assert af == pytest.approx(ac)
    assert coarse["actual_record_rank_extent"] == pytest.approx(1)
    assert fine["actual_record_rank_extent"] == pytest.approx(1)
    assert coarse["overlap_extent"] == pytest.approx(1)
    assert fine["overlap_extent"] == pytest.approx(2)


def test_copying_records_changes_reduction_not_global_purity():
    r = record_copy_control()
    assert r["before_original_memory_extent"] == pytest.approx(2)
    assert r["after_original_memory_extent"] == pytest.approx(4)
    assert r["after_all_memories_extent"] == pytest.approx(2)
    assert r["after_all_records_basis_breadth"] == pytest.approx(4)
    assert r["global_purity_error"] < 1e-12


def test_composition_and_representation_controls():
    assert max(overlap_controls().values()) < 1e-12
