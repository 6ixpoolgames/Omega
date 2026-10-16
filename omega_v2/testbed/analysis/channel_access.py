"""Structural access, first passage and finite deadline recovery surveys."""
from __future__ import annotations

import numpy as np
from scipy.sparse import bmat, csr_matrix
from scipy.sparse.linalg import expm_multiply

from .finite_classes import _generator, _starts_mask


def _target_mask(target_mask, n):
    mask = np.asarray(target_mask, dtype=bool)
    if mask.shape != (n,):
        raise ValueError("target_mask must be a boolean vector of length n")
    return mask


def _initial_distribution(initial, n):
    if np.isscalar(initial):
        mask = _starts_mask(initial, n)
        out = mask.astype(float)
    else:
        out = np.asarray(initial, dtype=float)
        if out.shape != (n,) or not np.all(np.isfinite(out)) or np.any(out < -1e-12):
            raise ValueError("initial must be a state index or finite nonnegative vector of length n")
        if abs(float(out.sum()) - 1.0) > 1e-10:
            raise ValueError("initial distribution must sum to one")
        out = np.maximum(out, 0.0) / out.sum()
    return out


def _graph(q):
    graph = q.copy()
    graph.setdiag(0.0)
    graph.data[graph.data < 0] = 0.0
    graph.eliminate_zeros()
    return graph


def closure_mask(Q, target_mask):
    """Mark states with no positive-rate path to any target state.

    This is structural access over every positive off-diagonal transition in
    Q. A fixed-policy closure mask can be computed by passing that policy's Q.
    """
    q = _generator(Q)
    targets = _target_mask(target_mask, q.shape[0])
    if not np.any(targets):
        return np.ones(q.shape[0], dtype=bool)
    rev = _graph(q).transpose().tocsr()
    seen = np.zeros(q.shape[0], dtype=bool)
    stack = list(np.flatnonzero(targets))
    seen[stack] = True
    while stack:
        j = stack.pop()
        for i in rev.indices[rev.indptr[j]:rev.indptr[j + 1]]:
            if not seen[i]:
                seen[i] = True
                stack.append(int(i))
    return ~seen


def access_witness(Q, start, target_mask):
    """Return a shortest positive-rate path from start to target, or None."""
    q = _generator(Q)
    n = q.shape[0]
    if isinstance(start, (bool, np.bool_)) or int(start) != start or start < 0 or start >= n:
        raise ValueError("start must be a valid integer state index")
    start = int(start)
    target = _target_mask(target_mask, n)
    if target[start]:
        return [start]
    graph = _graph(q)
    predecessor = np.full(n, -1, dtype=int)
    seen = np.zeros(n, dtype=bool)
    seen[start] = True
    queue = [start]
    head = 0
    while head < len(queue):
        i = queue[head]
        head += 1
        for j in graph.indices[graph.indptr[i]:graph.indptr[i + 1]]:
            if seen[j]:
                continue
            seen[j] = True
            predecessor[j] = i
            if target[j]:
                path = [int(j)]
                while path[-1] != start:
                    path.append(int(predecessor[path[-1]]))
                return list(reversed(path))
            queue.append(int(j))
    return None


def closure_certificate(Q, mask):
    """Certify a proposed set has no positive-rate edge leaving it."""
    q = _generator(Q)
    closed = _target_mask(mask, q.shape[0])
    outside = ~closed
    exits = q[closed][:, outside]
    positive = exits.data > 0
    edge_count = int(np.count_nonzero(positive))
    return {
        "closed": edge_count == 0,
        "state_count": int(np.count_nonzero(closed)),
        "outgoing_positive_edge_count": edge_count,
        "outgoing_positive_rate_sum": float(exits.data[positive].sum()) if edge_count else 0.0,
    }


def first_passage(Q, initial, target_mask, T):
    """Return probability of hitting a target by T and killed endpoint mass.

    The killed subgenerator keeps Q's original diagonal, so probability lost
    from the complement is precisely first entry. Initial target mass counts
    as an immediate hit at time zero.
    """
    q = _generator(Q)
    n = q.shape[0]
    target = _target_mask(target_mask, n)
    p0 = _initial_distribution(initial, n)
    if not np.isfinite(T) or T < 0:
        raise ValueError("T must be finite and nonnegative")
    outside = np.flatnonzero(~target)
    killed_mass = np.zeros(n, dtype=float)
    if T == 0:
        killed_mass[outside] = p0[outside]
    elif outside.size:
        killed = q[outside][:, outside].tocsr()
        survivors = np.asarray(expm_multiply(killed.transpose().tocsr() * float(T), p0[outside])).ravel()
        if not np.all(np.isfinite(survivors)) or np.min(survivors) < -1e-12:
            raise ArithmeticError("killed propagation produced invalid probability mass")
        killed_mass[outside] = np.maximum(survivors, 0.0)
    survival = float(killed_mass.sum())
    if survival < -1e-10 or survival > 1.0 + 1e-10:
        raise ArithmeticError(f"killed survival mass {survival} is outside probability tolerance")
    survival = float(np.clip(survival, 0.0, 1.0))
    hit = 1.0 - survival
    return {
        "horizon": float(T),
        "hit_probability": hit,
        "survival_probability": survival,
        "survivor_distribution": killed_mass,
    }


def recovery_profile(Q, initial, target_mask, horizons):
    """Survey hit, endpoint occupancy and integrated target occupation.

    Hit probability is first entry by the deadline. Endpoint probability is
    ordinary full-process occupancy at the deadline. Integrated occupation
    is expected time in the target set over [0, T].
    """
    q = _generator(Q)
    n = q.shape[0]
    target = _target_mask(target_mask, n)
    p0 = _initial_distribution(initial, n)
    times = []
    for horizon in horizons:
        if not np.isfinite(horizon) or horizon < 0:
            raise ValueError("horizons must be finite and nonnegative")
        times.append(float(horizon))
    if len(set(times)) != len(times):
        raise ValueError("horizons must be unique")
    if not np.any(target):
        return {str(t): {"hit_probability": 0.0, "endpoint_target_probability": 0.0,
                         "integrated_target_occupation": 0.0} for t in times}

    # Column convention for expm_multiply: dp/dt = Q.T p. The final scalar
    # coordinate accumulates target occupation continuously.
    selector = csr_matrix(target.astype(float).reshape(1, n))
    augmented = bmat([[q.transpose().tocsr(), csr_matrix((n, 1))],
                      [selector, csr_matrix((1, 1))]], format="csr")
    initial_augmented = np.concatenate([p0, [0.0]])
    profile = {}
    for T in times:
        state = expm_multiply(augmented * T, initial_augmented)
        endpoint = np.asarray(state[:n]).ravel()
        if not np.all(np.isfinite(endpoint)) or np.min(endpoint) < -1e-12:
            raise ArithmeticError("full propagation produced invalid probability mass")
        endpoint = np.maximum(endpoint, 0.0)
        endpoint_mass = float(endpoint.sum())
        if abs(endpoint_mass - 1.0) > 1e-10:
            raise ArithmeticError(f"full propagation mass error {endpoint_mass - 1.0} exceeds tolerance")
        endpoint /= endpoint_mass
        occupation = float(state[n])
        if not np.isfinite(occupation) or occupation < -1e-10 or occupation > T + 1e-10:
            raise ArithmeticError("integrated target occupation is outside its bounds")
        passage = first_passage(q, p0, target, T)
        profile[str(T)] = {
            "hit_probability": float(passage["hit_probability"]),
            "endpoint_target_probability": float(endpoint[target].sum()),
            "integrated_target_occupation": max(0.0, occupation),
        }
    return profile
