"""Full-matrix extent relative to a declared propagated initial reference."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.quantum_extent import decoherence_matrix, expand_history, grouped_matrix
from omega_v2.finite.quantum_readers import cnot, local_gate, projectors
from omega_v2.finite.spatial_futuresfield import hopping, spatial_setup


def psd_eigenvalues(matrix, tolerance=1e-12):
    matrix = np.asarray(matrix, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.isfinite(matrix).all():
        raise ValueError("Finite square matrix required")
    if not np.allclose(matrix, matrix.conj().T, atol=tolerance, rtol=0):
        raise ValueError("Hermitian matrix required")
    values, vectors = np.linalg.eigh(matrix)
    if values.min() < -tolerance:
        raise ValueError("Positive semidefinite matrix required")
    return values, vectors


def history_kernel(density, stages):
    """Linear map of a positive source operator; no trace normalization."""
    values, vectors = psd_eigenvalues(density)
    result = None
    for i, weight in enumerate(values):
        if weight > 1e-12:
            rows, _ = expand_history(vectors[:, i], stages)
            term = weight * decoherence_matrix(rows)
            result = term if result is None else result + term
    if result is None:
        raise ValueError("Nonzero source reference required")
    return result


def reference_extent(density, reference, tolerance=1e-12):
    """exp(-Tr D(log D-log M)), support-aware; reference is not normalized."""
    d, _ = psd_eigenvalues(density, tolerance)
    m, basis = psd_eigenvalues(reference, tolerance)
    if density.shape != reference.shape:
        raise ValueError("Matching matrix shapes required")
    if not np.isclose(d.sum(), 1., atol=tolerance, rtol=0):
        raise ValueError("Actual history density must have trace one")
    positive_m = m > tolerance
    weight = np.diag(basis.conj().T @ density @ basis).real
    if weight[~positive_m].sum() > tolerance:
        raise ValueError("Actual support exceeds reference support")
    positive_d = d > tolerance
    tr_d_log_d = np.dot(d[positive_d], np.log(d[positive_d]))
    tr_d_log_m = np.dot(weight[positive_m], np.log(m[positive_m]))
    log_volume = float(tr_d_log_m - tr_d_log_d)
    mass = float(m.sum())
    return {"extent": float(np.exp(log_volume)), "log_extent": log_volume,
            "reference_mass": mass, "relative_entropy_to_normalized_reference": float(np.log(mass) - log_volume)}


def spatial_reference():
    return np.diag([1., 0., 1., 0.]).astype(complex)


def pair_for(psi, reference, stages):
    return history_kernel(np.outer(psi, psi.conj()), stages), history_kernel(reference, stages)


def recorded_hops(count):
    """Particle site plus n blank local memory bits, one fresh record per hop."""
    width = count + 1
    size = 2**width
    psi = np.zeros(size, dtype=complex)
    psi[0] = 1
    reference = np.zeros((size, size), dtype=complex)
    reference[0, 0] = reference[size // 2, size // 2] = 1
    hop = local_gate(hopping(np.pi / 4), 0, width)
    stages = [(cnot(0, memory, width) @ hop, projectors((0,), width))
              for memory in range(1, width)]
    return psi, reference, stages


def reference_controls():
    psi, stages = spatial_setup(np.pi / 4, np.pi / 6, 0., np.pi / 2)
    reference = spatial_reference()
    d, m = pair_for(psi, reference, stages)
    base = reference_extent(d, m)
    rng = np.random.default_rng(820)
    w, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j*rng.normal(size=(4, 4)))
    rotated = [(w @ u @ w.conj().T, [w @ p @ w.conj().T for p in ps]) for u, ps in stages]
    dr, mr = pair_for(w @ psi, w @ reference @ w.conj().T, rotated)
    enlarged = [(np.kron(u, np.eye(2)), [np.kron(p, np.eye(2)) for p in ps]) for u, ps in stages]
    db, mb = pair_for(np.kron(psi, [1., 0.]), np.kron(reference, np.diag([1., 0.])), enlarged)
    di, mi = pair_for(psi, reference, [(np.eye(4), [np.eye(4)])] + stages)
    half = np.kron(hopping(np.pi / 8), np.eye(2))
    ds, ms = pair_for(psi, reference, [(half, [np.eye(4)]), (half, stages[0][1]), stages[1]])
    fine_stages = [(half, stages[0][1]), (half, stages[0][1]), stages[1]]
    df, mf = pair_for(psi, reference, fine_stages)
    _, labels = expand_history(psi, fine_stages)
    groups = [[i for i, label in enumerate(labels) if label[1:] == (a, b)] for a in range(2) for b in range(2)]
    dg, mg = grouped_matrix(df, groups), grouped_matrix(mf, groups)
    endpoint_stages = [(stages[1][0] @ stages[0][0], stages[-1][1])]
    de, me = pair_for(psi, reference, endpoint_stages)
    du, mu = pair_for(psi, reference, [(stages[1][0] @ stages[0][0], [np.eye(4)])])
    product_stages = [(np.kron(u, u), [np.kron(p, q) for p in ps for q in ps]) for u, ps in stages]
    dp, mp = pair_for(np.kron(psi, psi), np.kron(reference, reference), product_stages)
    product = reference_extent(dp, mp)
    order = [(a1*2+b1)*4+(a2*2+b2) for a1 in range(2) for a2 in range(2)
             for b1 in range(2) for b2 in range(2)]
    ambient = history_kernel(np.eye(4), stages)
    return {
        "original": base,
        "refined": reference_extent(df, mf),
        "endpoint_only": reference_extent(de, me),
        "unresolved": reference_extent(du, mu),
        "unrestricted_detector_reference": reference_extent(d, ambient),
        "product": product,
        "covariance_error": float(max(np.max(abs(dr-d)), np.max(abs(mr-m)))),
        "blank_ancilla_error": float(max(np.max(abs(db-d)), np.max(abs(mb-m)))),
        "identity_error": float(max(np.max(abs(di-d)), np.max(abs(mi-m)))),
        "subdivision_error": float(max(np.max(abs(ds-d)), np.max(abs(ms-m)))),
        "coherent_regrouping_error": float(max(np.max(abs(dg-d)), np.max(abs(mg-m)))),
        "product_kernel_error": float(max(np.max(abs(dp[np.ix_(order, order)]-np.kron(d, d))),
                                           np.max(abs(mp[np.ix_(order, order)]-np.kron(m, m))))),
        "extent_product_error": float(abs(product["extent"]-base["extent"]**2)),
        "reference_scaling_error": float(abs(reference_extent(d, 3*m)["extent"]-3*base["extent"])),
    }
