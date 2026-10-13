"""Optional Rule A-R1 diagnostic for predictive retention.

This operational version measures distinctions between two future samples
that remain predictive after a lag. It does not gate the primary unfiltered
history-breadth readout and is not a canonical definition of Rule A.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
from scipy.linalg import expm


NUMERICAL_TOLERANCE = 1e-10


def _entropy_bits(probabilities: np.ndarray) -> float:
    """Shannon entropy in bits; zero probabilities contribute exactly zero."""
    positive = probabilities[probabilities > 0.0]
    return float(-np.sum(positive * np.log2(positive)))


def _row_entropies_bits(probabilities: np.ndarray) -> np.ndarray:
    """Return Shannon entropy for every row, in bits."""
    terms = np.zeros_like(probabilities)
    positive = probabilities > 0.0
    terms[positive] = probabilities[positive] * np.log2(probabilities[positive])
    return -terms.sum(axis=1)


def _transition(q: np.ndarray, time: float) -> np.ndarray:
    p = expm(time * q)
    if not np.all(np.isfinite(p)):
        raise ValueError("matrix exponential produced non-finite transition values")
    if float(np.min(p)) < -NUMERICAL_TOLERANCE:
        raise ValueError("matrix exponential is not nonnegative within tolerance")
    rows = p.sum(axis=1)
    if np.max(np.abs(rows - 1.0)) > NUMERICAL_TOLERANCE:
        raise ValueError("matrix exponential rows are not stochastic within tolerance")
    # Only floating-point residue is removed; its size is bounded above.
    p = np.maximum(p, 0.0)
    p /= p.sum(axis=1, keepdims=True)
    return p


def retention_profile(
    q: np.ndarray,
    delta: float,
    lags: Sequence[float],
    root_distributions: Mapping[str, Sequence[float]],
) -> dict[str, dict[float, float]]:
    """Return predictive-retention profiles in bits for named root priors.

    For each root state ``x`` and lag ``tau``, the diagnostic is
    ``I(X_delta; X_(delta+tau) | X_0=x)`` under ``P_t=exp(t Q)``. A named
    root distribution averages these known-root values. At tau=0 this equals
    one-step transition entropy. Values are never summed across lags or used
    to filter the primary breadth objective.

    ``q`` is a finite-state row-generator, ``delta`` and all lags are finite
    nonnegative times, and each root distribution is a normalized vector.
    The returned mapping is ``distribution_name -> {lag: bits}``.
    Numerical stochasticity/positivity and MI roundoff tolerance is 1e-10.
    """
    q = np.asarray(q, dtype=float)
    if q.ndim != 2 or q.shape[0] != q.shape[1] or q.shape[0] == 0:
        raise ValueError("q must be a nonempty square matrix")
    if not np.all(np.isfinite(q)):
        raise ValueError("q must contain only finite values")
    if not np.isfinite(delta) or delta < 0:
        raise ValueError("delta must be finite and nonnegative")
    if np.min(q - np.diag(np.diag(q))) < -NUMERICAL_TOLERANCE:
        raise ValueError("q must have nonnegative off-diagonal rates")
    if np.max(np.abs(q.sum(axis=1))) > NUMERICAL_TOLERANCE:
        raise ValueError("q rows must sum to zero within tolerance")
    lag_values = tuple(float(t) for t in lags)
    if any(not np.isfinite(t) or t < 0 for t in lag_values):
        raise ValueError("lags must be finite and nonnegative")
    if len(set(lag_values)) != len(lag_values):
        raise ValueError("lags must be unique")

    n = q.shape[0]
    roots: dict[str, np.ndarray] = {}
    for name, values in root_distributions.items():
        root = np.asarray(values, dtype=float)
        if root.shape != (n,) or not np.all(np.isfinite(root)):
            raise ValueError(f"root distribution {name!r} must be a finite vector of length {n}")
        if np.min(root) < -NUMERICAL_TOLERANCE:
            raise ValueError(f"root distribution {name!r} has negative mass")
        root = np.maximum(root, 0.0)
        total = float(root.sum())
        if abs(total - 1.0) > NUMERICAL_TOLERANCE:
            raise ValueError(f"root distribution {name!r} must sum to one")
        roots[name] = root / total

    p_delta = _transition(q, float(delta))
    results: dict[str, dict[float, float]] = {name: {} for name in roots}
    known_root_by_lag: dict[float, np.ndarray] = {}
    for lag in lag_values:
        p_lag = _transition(q, lag)
        future_given_root = p_delta @ p_lag
        known_root_values = _row_entropies_bits(future_given_root) - (
            p_delta @ _row_entropies_bits(p_lag)
        )
        minimum = float(np.min(known_root_values))
        if minimum < -NUMERICAL_TOLERANCE:
            raise ArithmeticError(
                f"predictive mutual information {minimum} is below rounding tolerance"
            )
        # Clamp only negative floating-point residue covered by the declared tolerance.
        known_root_values = np.maximum(known_root_values, 0.0)
        known_root_by_lag[lag] = known_root_values
        for name, root in roots.items():
            results[name][lag] = float(root @ known_root_values)

    ordered_lags = sorted(lag_values)
    for earlier, later in zip(ordered_lags, ordered_lags[1:]):
        increase = known_root_by_lag[later] - known_root_by_lag[earlier]
        if float(np.max(increase)) > NUMERICAL_TOLERANCE:
            raise ArithmeticError(
                "predictive retention increased across ordered lags by "
                f"{float(np.max(increase))}, above rounding tolerance"
            )
    return results
