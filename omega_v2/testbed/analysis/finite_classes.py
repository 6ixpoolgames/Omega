"""Finite sampled-state entropy and reducible CTMC class analysis.

Generators use the row convention: ``Q[i, j]`` is the rate from i to j.
The dense sampled-state entropy solver intentionally has an explicit memory
gate. Reachability and channel surveys are available independently in
``channel_access``.
"""
from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from scipy.linalg import expm, solve
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

_PROB_TOL = 1e-10
_NEG_TOL = 1e-12
_RESIDUAL_TOL = 1e-8


def _generator(Q):
    q = csr_matrix(Q, dtype=float)
    if q.ndim != 2 or q.shape[0] != q.shape[1] or q.shape[0] == 0:
        raise ValueError("Q must be a nonempty square generator")
    if not np.all(np.isfinite(q.data)):
        raise ValueError("Q must contain only finite values")
    original = csr_matrix(Q, dtype=float)
    original.sum_duplicates()
    offdiag = original.copy()
    offdiag.setdiag(0.0)
    offdiag.eliminate_zeros()
    if np.any(offdiag.data < 0):
        raise ValueError("Q must have nonnegative off-diagonal rates")
    diagonal = original.diagonal()
    if np.any(diagonal > 0):
        raise ValueError("Q must have nonpositive diagonal entries")
    rows = np.asarray(original.sum(axis=1)).ravel()
    scale = max(1.0, float(np.max(np.abs(original.data))) if original.nnz else 1.0)
    if np.max(np.abs(rows)) > 1e-10 * scale:
        raise ValueError("Q rows must sum to zero")
    return original.tocsr()


def _starts_mask(starts, n):
    if np.isscalar(starts):
        starts = [starts]
    out = np.zeros(n, dtype=bool)
    for value in starts:
        if isinstance(value, (bool, np.bool_)) or int(value) != value:
            raise ValueError("starts must contain integer state indices")
        i = int(value)
        if i < 0 or i >= n:
            raise ValueError("start index is outside Q")
        out[i] = True
    return out


def reachable_indices(Q, starts):
    """Return sorted indices reachable along positive-rate transitions."""
    q = _generator(Q)
    n = q.shape[0]
    seen = _starts_mask(starts, n)
    stack = list(np.flatnonzero(seen))
    # A zero-rate diagonal self-loop must not affect graph reachability.
    graph = q.copy()
    graph.setdiag(0.0)
    graph.eliminate_zeros()
    while stack:
        i = stack.pop()
        lo, hi = graph.indptr[i], graph.indptr[i + 1]
        for pos in range(lo, hi):
            j = graph.indices[pos]
            if graph.data[pos] > 0 and not seen[j]:
                seen[j] = True
                stack.append(int(j))
    return np.flatnonzero(seen)


def _row_entropy(P):
    p = np.asarray(P, dtype=float)
    positive = p > 0
    terms = np.zeros_like(p)
    terms[positive] = -p[positive] * np.log2(p[positive])
    return terms.sum(axis=1)


def finite_history_bits(P, n):
    """Return per-root expected conditional history bits over n steps."""
    p = np.asarray(P, dtype=float)
    if p.ndim != 2 or p.shape[0] != p.shape[1] or p.shape[0] == 0:
        raise ValueError("P must be a nonempty square transition matrix")
    if not np.all(np.isfinite(p)) or np.any(p < 0):
        raise ValueError("P must be finite and nonnegative")
    if np.max(np.abs(p.sum(axis=1) - 1.0)) > 1e-10:
        raise ValueError("P rows must sum to one")
    if isinstance(n, (bool, np.bool_)) or int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer")
    g = _row_entropy(p)
    total = np.zeros(p.shape[0], dtype=float)
    for _ in range(int(n)):
        total += g
        g = p @ g
    return total


def _closed_classes(q):
    n = q.shape[0]
    graph = q.copy()
    graph.setdiag(0.0)
    graph.data[graph.data < 0] = 0.0
    graph.eliminate_zeros()
    count, labels = connected_components(graph, directed=True, connection="strong")
    classes = []
    for label in range(count):
        members = np.flatnonzero(labels == label)
        outside = np.ones(n, dtype=bool)
        outside[members] = False
        if not np.any(outside):
            classes.append(members)
            continue
        exits = q[members][:, outside]
        if exits.nnz and np.any(exits.data > 0):
            continue
        classes.append(members)
    if not classes:
        raise ArithmeticError("finite generator has no closed communicating class")
    return classes, labels


def _stationary(qc):
    n = qc.shape[0]
    if n == 1:
        return np.ones(1)
    a = qc.toarray().T.copy()
    a[-1, :] = 1.0
    rhs = np.zeros(n)
    rhs[-1] = 1.0
    pi = solve(a, rhs, assume_a="gen")
    if np.min(pi) < -1e-10:
        raise ArithmeticError("stationary solve produced negative mass")
    pi = np.maximum(pi, 0.0)
    total = pi.sum()
    if not np.isfinite(total) or abs(total - 1.0) > _PROB_TOL:
        raise ArithmeticError("stationary solve failed normalization tolerance")
    return pi / total


def _sampled_transition(q, delta, max_dense_bytes):
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError("delta must be finite and positive")
    if isinstance(max_dense_bytes, (bool, np.bool_)) or int(max_dense_bytes) != max_dense_bytes or max_dense_bytes <= 0:
        raise ValueError("max_dense_bytes must be a positive integer")
    n = q.shape[0]
    estimated = 8 * n * n * np.dtype(np.float64).itemsize
    if estimated > int(max_dense_bytes):
        raise MemoryError(f"dense entropy analysis estimates {estimated} bytes, cap is {max_dense_bytes}")
    p = expm(q.toarray() * float(delta))
    if not np.all(np.isfinite(p)):
        raise ArithmeticError("matrix exponential produced nonfinite probabilities")
    minimum = float(np.min(p))
    row_error = float(np.max(np.abs(p.sum(axis=1) - 1.0)))
    if minimum < -_NEG_TOL:
        raise ArithmeticError(f"matrix exponential has negative probability {minimum}")
    if row_error > _PROB_TOL:
        raise ArithmeticError(f"matrix exponential row-sum error {row_error} exceeds tolerance")
    p[p < 0] = 0.0
    p /= p.sum(axis=1, keepdims=True)
    return p, int(estimated)


def analyze(Q, delta, max_dense_bytes=512 * 1024 * 1024):
    """Analyze sampled entropy and limiting classes for a finite CTMC.

    The gate estimates eight dense float64 n-by-n work arrays, covering P,
    matrix exponential workspaces, and dense block solves. Limiting projection
    and Poisson solves are performed by recurrent/transient blocks.
    ``Pi`` is returned only up to 512 states; the full vector ``rate_per_step``
    and offset remain available at all supported gated sizes.
    """
    q = _generator(Q)
    n = q.shape[0]
    p, estimated = _sampled_transition(q, delta, max_dense_bytes)
    g = _row_entropy(p)
    classes, _ = _closed_classes(q)
    k = len(classes)
    stationary = []
    class_rates = np.empty(k, dtype=float)
    for c, members in enumerate(classes):
        pi = _stationary(q[members][:, members])
        stationary.append(pi)
        class_rates[c] = float(pi @ g[members])

    is_recurrent = np.zeros(n, dtype=bool)
    for c, members in enumerate(classes):
        is_recurrent[members] = True
    transient = np.flatnonzero(~is_recurrent)
    absorption = np.zeros((n, k), dtype=float)
    for c, members in enumerate(classes):
        absorption[members, c] = 1.0
    if transient.size:
        qtt = q[transient][:, transient].toarray()
        rhs = np.zeros((transient.size, k), dtype=float)
        for c, members in enumerate(classes):
            rhs[:, c] = np.asarray(q[transient][:, members].sum(axis=1)).ravel()
        weights = solve(-qtt, rhs, assume_a="gen")
        if np.min(weights) < -1e-9:
            raise ArithmeticError("absorption solve produced negative probability")
        weights = np.maximum(weights, 0.0)
        rowsums = weights.sum(axis=1)
        row_error = float(np.max(np.abs(rowsums - 1.0)))
        if np.any(rowsums <= 0) or row_error > _PROB_TOL:
            raise ArithmeticError(f"absorption probabilities fail normalization tolerance: {row_error}")
        absorption[transient] = weights

    rate = absorption @ class_rates
    b = np.zeros(n, dtype=float)
    for c, members in enumerate(classes):
        pi = stationary[c]
        pc = p[np.ix_(members, members)]
        system = np.eye(len(members)) - pc + np.ones((len(members), 1)) * pi[None, :]
        b[members] = solve(system, g[members] - class_rates[c], assume_a="gen")
    if transient.size:
        ptt = p[np.ix_(transient, transient)]
        ptr = p[np.ix_(transient, np.flatnonzero(is_recurrent))]
        recurrent = np.flatnonzero(is_recurrent)
        rhs_transient = g[transient] - rate[transient] + ptr @ b[recurrent]
        b[transient] = solve(np.eye(len(transient)) - ptt, rhs_transient, assume_a="gen")

    # The projection acts through absorption weights followed by each class's
    # stationary average; keeping that factorization avoids an n-by-n Pi.
    projection_residual = float(np.max(np.abs(p @ absorption - absorption)))
    for c, members in enumerate(classes):
        pi = stationary[c]
        stationarity_p = float(np.max(np.abs(pi @ p[np.ix_(members, members)] - pi)))
        projection_residual = max(projection_residual, stationarity_p)
    pi_limit = None
    if n <= 512:
        pi_limit = np.zeros((n, n), dtype=float)
        for c, members in enumerate(classes):
            pi_limit[:, members] += absorption[:, c, None] * stationary[c][None, :]
        projection_residual = max(
            projection_residual,
            float(np.max(np.abs(pi_limit @ pi_limit - pi_limit))),
            float(np.max(np.abs(p @ pi_limit - pi_limit))),
            float(np.max(np.abs(pi_limit @ p - pi_limit))),
        )
    stationarity_residual = max(
        float(np.max(np.abs(stationary[c] @ q[member][:, member].toarray())))
        for c, member in enumerate(classes)
    )
    absorption_residual = 0.0
    if transient.size:
        absorption_residual = float(np.max(np.abs(q[transient][:, transient].toarray() @ absorption[transient] + rhs)))
    poisson_residual = 0.0
    normalization_residual = 0.0
    for c, members in enumerate(classes):
        pi = stationary[c]
        pc = p[np.ix_(members, members)]
        residual = (np.eye(len(members)) - pc + np.ones((len(members), 1)) * pi[None, :]) @ b[members]
        poisson_residual = max(poisson_residual, float(np.max(np.abs(residual - (g[members] - class_rates[c])))))
        normalization_residual = max(normalization_residual, abs(float(pi @ b[members])))
    if transient.size:
        residual = b[transient] - p[np.ix_(transient, np.arange(n))] @ b
        poisson_residual = max(poisson_residual, float(np.max(np.abs(residual - (g[transient] - rate[transient])))))
    residuals = {
        "row_stochastic": float(np.max(np.abs(p.sum(axis=1) - 1.0))),
        "stationarity": stationarity_residual,
        "absorption": absorption_residual,
        "projection": projection_residual,
        "poisson": poisson_residual,
        "poisson_normalization": normalization_residual,
    }
    failed = {name: value for name, value in residuals.items() if value > _RESIDUAL_TOL}
    if failed:
        raise ArithmeticError(f"finite-class analysis residuals exceed tolerance: {failed}")
    return {
        "P": p,
        "row_entropy": g,
        "class_indices": [x.copy() for x in classes],
        "absorption": absorption,
        "stationary": [x.copy() for x in stationary],
        "class_rate_per_step": class_rates,
        "rate_per_step": rate,
        "offset": b,
        "residuals": residuals,
        "Pi": pi_limit,
        "dense_bytes_estimate": int(estimated),
    }


def _query_distribution(query, n):
    if np.isscalar(query):
        out = np.zeros(n, dtype=float)
        if isinstance(query, (bool, np.bool_)) or int(query) != query or query < 0 or query >= n:
            raise ValueError("query state index is invalid")
        out[int(query)] = 1.0
        return out
    out = np.asarray(query, dtype=float)
    if out.shape != (n,) or not np.all(np.isfinite(out)) or np.any(out < -1e-12):
        raise ValueError("query distributions must be finite nonnegative vectors of length n")
    if abs(float(out.sum()) - 1.0) > 1e-10:
        raise ValueError("query distributions must sum to one")
    return np.maximum(out, 0.0) / out.sum()


def evaluate(Q, delta, horizons, queries, limiting=True, max_dense_bytes=512 * 1024 * 1024):
    """Evaluate finite history bits and optional limiting rate/offset by root.

    ``horizons`` are nonnegative integer sample counts, and ``queries`` maps
    caller-chosen names to a state index or a probability row over states.
    The returned object contains only JSON-safe scalars, lists and mappings.
    """
    if limiting:
        result = analyze(Q, delta, max_dense_bytes=max_dense_bytes)
    else:
        q = _generator(Q)
        p, _ = _sampled_transition(q, delta, max_dense_bytes)
        result = {"P": p, "row_entropy": _row_entropy(p),
                  "residuals": {"row_stochastic": float(np.max(np.abs(p.sum(axis=1) - 1.0)))}}
    p = result["P"]
    if not isinstance(queries, Mapping) or not queries:
        raise ValueError("queries must be a nonempty name-to-root mapping")
    ns = []
    for h in horizons:
        if isinstance(h, (bool, np.bool_)) or int(h) != h or h < 0:
            raise ValueError("horizons must contain nonnegative integer sample counts")
        ns.append(int(h))
    profiles = {}
    max_h = max(ns, default=0)
    all_bits = {name: [] for name in queries}
    if ns:
        finite = np.zeros(p.shape[0], dtype=float)
        step_entropy = result["row_entropy"].copy()
        wanted = set(ns)
        if 0 in wanted:
            for name, query in queries.items():
                all_bits[name].append((0, 0.0))
        for step in range(1, max_h + 1):
            finite += step_entropy
            step_entropy = p @ step_entropy
            if step in wanted:
                for name, query in queries.items():
                    all_bits[name].append((step, float(_query_distribution(query, len(finite)) @ finite)))
        for name in queries:
            profiles[name] = {str(step): value for step, value in all_bits[name]}
    out = {"delta": float(delta), "horizons_steps": ns, "profiles_bits": profiles,
           "residuals": {k: float(v) for k, v in result["residuals"].items()}}
    if limiting:
        out["classes"] = [x.tolist() for x in result["class_indices"]]
        out["absorption"] = result["absorption"].tolist()
    if limiting:
        out["limiting"] = {}
        for name, query in queries.items():
            nu = _query_distribution(query, p.shape[0])
            out["limiting"][name] = {
                "rate_bits_per_step": float(nu @ result["rate_per_step"]),
                "rate_bits_per_time": float((nu @ result["rate_per_step"]) / delta),
                "offset_bits": float(nu @ result["offset"]),
            }
    return out
