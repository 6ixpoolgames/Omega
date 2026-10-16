import numpy as np
import pytest

from omega_v2.finite.coherent_reference import (
    pair_for,
    recorded_hops,
    reference_controls,
    reference_extent,
    spatial_reference,
)
from omega_v2.finite.quantum_extent import effective_number
from omega_v2.finite.spatial_futuresfield import spatial_setup


def test_diagonal_reference_formula_and_support():
    p, m = np.array([.25, .75]), np.array([2., 3.])
    assert reference_extent(np.diag(p), np.diag(m))["extent"] == pytest.approx(np.exp(-np.dot(p, np.log(p/m))))
    with pytest.raises(ValueError, match="support"):
        reference_extent(np.diag(p), np.diag([1., 0.]))
    with pytest.raises(ValueError, match="trace one"):
        reference_extent(np.diag([.1, .1]), np.eye(2))


def test_full_complex_product_and_covariance():
    controls = reference_controls()
    assert max(v for k, v in controls.items() if k.endswith("_error")) < 1e-10
    assert controls["product"]["extent"] == pytest.approx(controls["original"]["extent"]**2)


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_classical_growth_is_suppressed_by_fixed_reference_mass(count):
    psi, ref, stages = recorded_hops(count)
    d, m = pair_for(psi, ref, stages)
    assert np.trace(m).real == pytest.approx(2)
    assert d == pytest.approx(np.diag(d.diagonal()))
    assert effective_number(d.diagonal().real) == pytest.approx(2**count)
    assert reference_extent(d, m)["extent"] == pytest.approx(2)


def test_reference_bound_despite_signed_allocation_failure():
    psi, stages = spatial_setup(np.pi/4, np.pi/6)
    d, m = pair_for(psi, spatial_reference(), stages)
    assert np.min(d.sum(axis=1).real) < -.09
    result = reference_extent(d, m)
    assert 1-1e-12 <= result["extent"] <= 2+1e-12
