import numpy as np
import pytest

from omega_v2.testbed.rule_a_assessment import retention_profile


def _h(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def test_two_state_profile_matches_independent_closed_form():
    rate = 0.7
    q = np.array([[-rate, rate], [rate, -rate]])
    delta = 0.4
    lags = (0.0, 0.25, 1.0, 4.0)
    got = retention_profile(q, delta, lags, {"root-0": [1.0, 0.0]})["root-0"]
    u = (1.0 - np.exp(-2.0 * rate * delta)) / 2.0
    for tau in lags:
        v = (1.0 - np.exp(-2.0 * rate * tau)) / 2.0
        expected = _h([u * (1 - v) + (1 - u) * v, 1 - (u * (1 - v) + (1 - u) * v)]) - _h([v, 1 - v])
        assert got[tau] == pytest.approx(expected, abs=1e-12)
    assert got[0.0] == pytest.approx(_h([u, 1 - u]), abs=1e-12)


def test_constant_process_has_zero_retention():
    q = np.zeros((1, 1))
    profile = retention_profile(q, 0.25, (0.0, 0.25, 1.0, 64.0), {"only": [1.0]})
    assert all(value == 0.0 for value in profile["only"].values())


def test_symmetric_two_state_retention_is_nonnegative_and_decreases():
    q = np.array([[-1.0, 1.0], [1.0, -1.0]])
    lags = (0.0, 0.25, 1.0, 4.0, 16.0, 64.0)
    values = list(retention_profile(q, 0.25, lags, {"one-hot": [1.0, 0.0]})["one-hot"].values())
    assert all(x >= 0.0 for x in values)
    assert all(a + 1e-10 >= b for a, b in zip(values, values[1:]))
    assert values[-1] < 1e-10


def test_state_relabeling_preserves_named_root_profile():
    q = np.array([[-2.0, 1.0, 1.0], [0.5, -1.0, 0.5], [1.0, 0.0, -1.0]])
    root = np.array([0.2, 0.3, 0.5])
    permutation = np.array([2, 0, 1])
    lags = (0.0, 0.25, 1.0, 4.0, 16.0, 64.0)
    original = retention_profile(q, 0.25, lags, {"prior": root})["prior"]
    relabeled = retention_profile(
        q[np.ix_(permutation, permutation)], 0.25, lags, {"prior": root[permutation]}
    )["prior"]
    assert relabeled == pytest.approx(original, abs=1e-12)


def test_rejects_non_generator_and_malformed_root():
    with pytest.raises(ValueError, match="rows must sum to zero"):
        retention_profile(np.array([[-1.0, 0.0], [0.0, -1.0]]), 1.0, (0.0,), {"r": [1, 0]})
    with pytest.raises(ValueError, match="sum to one"):
        retention_profile(np.zeros((2, 2)), 1.0, (0.0,), {"r": [0.2, 0.2]})
