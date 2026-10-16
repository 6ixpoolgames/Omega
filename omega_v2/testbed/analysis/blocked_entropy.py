"""Memory-bounded sampled-state entropy: native exponential in row blocks.

Blocking is numerical only. All reachable physical states and all sample paths
remain in the kernel; there is no finite-rate cut or survival conditioning.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import expm_multiply, spsolve

from .finite_classes import _closed_classes, _generator, _stationary, reachable_indices


def sampled_kernel(Q, delta, block_rows=64, max_kernel_bytes=256*1024**2):
    q = _generator(Q)
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError("Positive finite cadence required")
    if type(block_rows) is not int or block_rows < 1:
        raise ValueError("Positive integer block size required")
    n = q.shape[0]
    if n*n*8 > max_kernel_bytes:
        raise MemoryError("Full sampled kernel exceeds declared storage budget")
    p = np.empty((n, n))
    minimum, mass_error = 0., 0.
    for lo in range(0, n, block_rows):
        hi = min(n, lo+block_rows)
        basis = np.zeros((n, hi-lo))
        basis[np.arange(lo, hi), np.arange(hi-lo)] = 1.
        block = expm_multiply(q.T*delta, basis).T
        minimum = min(minimum, float(block.min()))
        mass_error = max(mass_error, float(np.max(abs(block.sum(axis=1)-1))))
        if minimum < -1e-12 or mass_error > 1e-10:
            raise ArithmeticError("Sampled probability residual failed")
        block[block < 0] = 0.
        block /= block.sum(axis=1, keepdims=True)
        p[lo:hi] = block
    entropy = np.empty(n)
    for lo in range(0, n, block_rows):
        block = p[lo:lo+block_rows]
        terms = np.zeros_like(block)
        np.log2(block, out=terms, where=block > 0)
        entropy[lo:lo+block_rows] = -(block*terms).sum(axis=1)
    return p, entropy, {"kernel_mass": mass_error, "negative_probability": abs(minimum)}


def profile(Q, roots, delta, horizons, block_rows=64, max_kernel_bytes=256*1024**2):
    """Root-conditional finite breadth and limiting rates, no offset approximation."""
    q_full = _generator(Q)
    keep = reachable_indices(q_full, roots.values())
    q = q_full[keep][:, keep]
    positions = {int(original): i for i, original in enumerate(keep)}
    roots_local = {name: positions[int(index)] for name, index in roots.items()}
    if (not horizons or any(t <= 0 or abs(t/delta-round(t/delta)) > 1e-10
                            for t in horizons)):
        raise ValueError("Horizons must be positive cadence multiples")
    p, entropy, residuals = sampled_kernel(q, delta, block_rows, max_kernel_bytes)
    steps = {round(t/delta): str(t) for t in horizons}
    total = np.zeros(len(keep))
    bits = {}
    for step in range(1, max(steps)+1):
        total = entropy + p @ total
        if step in steps:
            bits[steps[step]] = {name: float(total[index]) for name, index in roots_local.items()}
    classes, _ = _closed_classes(q)
    stationary = [_stationary(q[m][:, m]) for m in classes]
    class_rates = np.array([pi @ entropy[m] / delta for pi, m in zip(stationary, classes)])
    absorption = np.zeros((len(keep), len(classes)))
    recurrent = np.zeros(len(keep), dtype=bool)
    for c, members in enumerate(classes):
        recurrent[members] = True
        absorption[members, c] = 1.
    transient = np.flatnonzero(~recurrent)
    if len(transient):
        rhs = np.column_stack([np.asarray(q[transient][:, m].sum(axis=1)).ravel()
                               for m in classes])
        solved = spsolve(-q[transient][:, transient].tocsc(), rhs)
        solved = np.asarray(solved).reshape(len(transient), len(classes))
        if solved.min() < -1e-10 or np.max(abs(solved.sum(axis=1)-1)) > 1e-9:
            raise ArithmeticError("Recurrent absorption residual failed")
        absorption[transient] = np.maximum(solved, 0)
    rates = {name: float(absorption[index] @ class_rates) for name, index in roots_local.items()}
    stationary_by_root = {}
    for name, index in roots_local.items():
        distribution = np.zeros(len(keep))
        for weight, members, pi in zip(absorption[index], classes, stationary):
            distribution[members] += weight*pi
        stationary_by_root[name] = distribution
    del p
    return {"bits": bits, "rates": rates, "keep": keep,
            "stationary": stationary_by_root, "classes": len(classes),
            "residuals": residuals}
