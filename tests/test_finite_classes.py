import numpy as np
import pytest

import omega_v2.testbed.analysis.finite_classes as finite_classes
from omega_v2.testbed.analysis.finite_classes import (
    analyze, evaluate, finite_history_bits, reachable_indices,
)


def _fork_generator():
    # State 0 chooses one of two recurrent thermal classes. The classes have
    # distinct switching rates, hence distinct sampled entropy rates.
    return np.array([
        [-2.0, 1.0, 0.0, 1.0, 0.0],
        [0.0, -1.0, 1.0, 0.0, 0.0],
        [0.0, 1.0, -1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -4.0, 4.0],
        [0.0, 0.0, 0.0, 2.0, -2.0],
    ])


def test_reducible_fork_has_class_absorption_rates_and_poisson_identity():
    q = _fork_generator()
    result = analyze(q, 0.4)
    assert [x.tolist() for x in result["class_indices"]] == [[1, 2], [3, 4]]
    np.testing.assert_allclose(result["absorption"][0], [0.5, 0.5], atol=1e-12)
    assert result["class_rate_per_step"][1] > result["class_rate_per_step"][0]
    for value in result["residuals"].values():
        assert value < 1e-9

    p = result["P"]
    g = result["row_entropy"]
    direct = finite_history_bits(p, 12)
    formula = 12 * result["rate_per_step"] + result["offset"] - np.linalg.matrix_power(p, 12) @ result["offset"]
    np.testing.assert_allclose(direct, formula, atol=1e-9)
    report = evaluate(q, 0.4, [0, 1, 12], {"fork": 0})
    assert report["profiles_bits"]["fork"]["0"] == 0.0
    assert report["limiting"]["fork"]["rate_bits_per_time"] > 0


def test_reachable_indices_follows_positive_rate_edges_only():
    q = np.array([[-1.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    assert reachable_indices(q, [0]).tolist() == [0, 1]


def test_dense_memory_gate_and_invalid_arguments():
    q = _fork_generator()
    with pytest.raises(MemoryError):
        analyze(q, 0.2, max_dense_bytes=100)
    with pytest.raises(ValueError):
        analyze(q, 0)
    with pytest.raises(ValueError):
        finite_history_bits(np.eye(2), -1)


def test_arbitrarily_small_positive_exit_is_not_classified_as_closed():
    q = np.array([[-1e-16, 1e-16], [0.0, 0.0]])
    result = analyze(q, 1e16)
    assert [x.tolist() for x in result["class_indices"]] == [[1]]
    np.testing.assert_allclose(result["absorption"][0], [1.0], atol=1e-12)


@pytest.mark.parametrize("q", [
    np.array([[0.5, -0.5], [0.0, 0.0]]),
    np.array([[1.0]]),
])
def test_generator_rejects_negative_rates_and_positive_diagonal(q):
    with pytest.raises(ValueError):
        reachable_indices(q, [0])


def test_analysis_rejects_exponential_and_projection_errors(monkeypatch):
    q = np.array([[-0.3, 0.3], [0.1, -0.1]])
    monkeypatch.setattr(finite_classes, "expm", lambda _: np.array([[0.8, 0.2], [0.2, 0.8]]))
    with pytest.raises(ArithmeticError, match="projection"):
        analyze(q, 1.0)

    monkeypatch.setattr(finite_classes, "expm", lambda _: np.array([[1.0, 0.1], [0.0, 1.0]]))
    with pytest.raises(ArithmeticError, match="row-sum"):
        analyze(q, 1.0)
