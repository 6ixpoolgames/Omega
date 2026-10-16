import numpy as np
import pytest

from omega_v2.finite.closed_schlogl import build_model


@pytest.mark.parametrize("k", [0, 0.1, 1, 10])
def test_generator_conservation_and_detailed_balance(k):
    model = build_model(k, 1.0)
    q = model["q"]
    pi = model["pi"]

    assert len(model["states"]) == 105
    assert q.shape == (105, 105)
    assert np.allclose(q.sum(axis=1), 0.0, atol=1e-12)
    assert np.allclose(pi @ q, 0.0, atol=1e-12)
    assert np.allclose(pi[:, None] * q, pi[None, :] * q.T, atol=1e-12)
    assert np.all(q[~np.eye(len(q), dtype=bool)] >= 0)
    assert np.all(np.diag(q) <= 0)


def test_equal_species_totals_root_placements_and_autocatalytic_propensity():
    model = build_model(2.5, 1.0)
    index = model["index"]
    forward = model["observables"]["forward"]
    ready = (0, 2, 1, 1, 0, 0)
    separated = (1, 2, 0, 0, 0, 1)

    assert sum(ready[0::3]) == sum(separated[0::3]) == 1
    assert sum(ready[1::3]) == sum(separated[1::3]) == 2
    assert sum(ready[2::3]) == sum(separated[2::3]) == 1
    assert forward[index[ready]] == pytest.approx(2 * 2.5)
    assert forward[index[separated]] == pytest.approx(0)
    assert model["pi"][index[ready]] == pytest.approx(model["pi"][index[separated]])


@pytest.mark.parametrize("k,d", [(0, 0.1), (0.1, 1), (1, 10), (10, 0.1)])
def test_voxel_swap_symmetry(k, d):
    model = build_model(k, d)
    swap = [model["index"][state[3:] + state[:3]] for state in model["states"]]
    q = model["q"]

    assert np.allclose(q, q[np.ix_(swap, swap)], atol=1e-12)
    assert np.allclose(model["pi"], model["pi"][swap], atol=1e-12)
