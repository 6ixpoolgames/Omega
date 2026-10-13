import numpy as np
import pytest
from scipy.linalg import expm

from omega_v2.testbed.analysis.blocked_entropy import profile, sampled_kernel
from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits


def test_blocked_kernel_and_history_match_dense_on_recombining_chain():
    q = np.array([[-3., 1., 2., 0.], [0., -2., 0., 2.],
                  [0., 0., -1., 1.], [1., 0., 0., -1.]])
    for block in (1, 2, 10):
        p, _entropy, _residual = sampled_kernel(q, .25, block)
        assert np.max(abs(p-expm(q*.25))) < 1e-13
        dense = analyze(q, .25)
        result = profile(q, {"root": 0}, .25, [1, 4], block)
        assert result["rates"]["root"] == pytest.approx(dense["rate_per_step"][0]/.25)
        assert result["bits"]["4"]["root"] == pytest.approx(finite_history_bits(p, 16)[0])


def test_reachable_reduction_does_not_erase_recurrent_mixtures():
    q = np.array([[-2., 1., 1., 0.], [0., -1., 1., 0.],
                  [0., 1., -1., 0.], [0., 0., 0., 0.]])
    result = profile(q, {"root": 0}, .25, [1])
    assert list(result["keep"]) == [0, 1, 2]
    result = profile(q, {"root": 0, "frozen": 3}, .25, [1])
    assert result["classes"] == 2
    assert result["rates"]["frozen"] == 0
    assert sum(result["stationary"]["root"]) == pytest.approx(1)


def test_probability_storage_and_horizon_gates():
    with pytest.raises(MemoryError):
        sampled_kernel(np.zeros((4, 4)), .25, max_kernel_bytes=8)
    with pytest.raises(ValueError):
        profile(np.zeros((2, 2)), {"root": 0}, .25, [.3])


def test_limiting_rate_includes_absorption_into_distinct_futures():
    q = np.array([[-2., 1., 0., 1.], [0., -1., 1., 0.],
                  [0., 1., -1., 0.], [0., 0., 0., 0.]])
    result = profile(q, {"root": 0, "cycling": 1, "frozen": 3}, .25, [1])
    assert result['classes'] == 2
    assert result['rates']['root'] == pytest.approx(result['rates']['cycling'] * .5)
    assert result['rates']['frozen'] == 0
    assert result['stationary']['root'][3] == pytest.approx(.5)
