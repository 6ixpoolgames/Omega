import numpy as np
import pytest

from omega_v2.finite.spatial_futuresfield import (
    analyze,
    representation_checks,
    signed_extent,
    spatial_setup,
)


def test_signed_weight_witness_and_record_threshold():
    for marker in [0., np.pi / 6, np.pi / 4, np.arccos(1 / np.sqrt(3)), np.pi / 2]:
        r, _, _ = analyze(*spatial_setup(np.pi / 4, np.pi / 6, marker))
        assert r["q"][2] == pytest.approx((1 - np.sqrt(3) * np.cos(marker)) / 8)
        assert (r["candidate_extent"] is None) == (np.cos(marker) > 1 / np.sqrt(3) + 1e-12)


def test_classical_record_limit_and_coherent_echo():
    coherent, _, _ = analyze(*spatial_setup(np.pi / 4, -np.pi / 4))
    recorded, d, _ = analyze(*spatial_setup(np.pi / 4, -np.pi / 4, np.pi / 2))
    assert coherent["candidate_extent"] == pytest.approx(2)
    assert coherent["site_breadths"][-1] == pytest.approx(1)
    assert recorded["candidate_extent"] == pytest.approx(4)
    assert d == pytest.approx(np.diag(d.diagonal()))
    assert recorded["candidate_extent"] == pytest.approx(recorded["diagonal_history_breadth"])


def test_representation_covariance_and_complex_product_failure():
    controls = representation_checks()
    assert max(v for k, v in controls.items() if k.endswith("_error")) < 1e-12
    assert controls["real_allocation_product_defect"] > 1e-4
    assert controls["individual_candidate_extent"] is not None
    assert controls["product_candidate_extent"] is None
    assert controls["product_minimum_q"] == pytest.approx(-1 / 32)


def test_extent_does_not_repair_negative_or_unnormalized_weights():
    assert signed_extent([1.1, -.1]) is None
    with pytest.raises(ValueError, match="Normalized"):
        signed_extent([.1, .2])
    assert signed_extent([.5, .5], [2., 2.]) == pytest.approx(4.)


def test_spatial_born_law_and_restrictions():
    for first, second, marker, phase in [(.3, -.8, .7, .4), (.4, .6, 0., np.pi / 2)]:
        r, _, _ = analyze(*spatial_setup(first, second, marker, phase))
        expected = (np.cos(first)**2 * np.cos(second)**2 + np.sin(first)**2 * np.sin(second)**2
                    - 2*np.cos(first)*np.sin(first)*np.cos(second)*np.sin(second)*np.cos(marker)*np.cos(phase))
        assert r["site_probabilities"][-1][0] == pytest.approx(expected)
        assert max(v for k, v in r.items() if k.endswith("_error")) < 1e-12
