"""Physical-site histories and a deliberately falsifiable signed extent candidate."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.quantum_extent import (
    decoherence_matrix,
    effective_number,
    expand_history,
    grouped_matrix,
)

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
SITE = (np.diag([1., 0.]), np.diag([0., 1.]))


def hopping(theta):
    """Exact one-particle two-site propagator for H=J X, theta=J dt/hbar."""
    return np.cos(theta) * np.eye(2) - 1j * np.sin(theta) * X


def spatial_setup(first, second, marker=0., phase=0.):
    """Position x detector, initially L,0; detector is physically located at R."""
    rotate = np.cos(marker) * np.eye(2) - 1j * np.sin(marker) * Y
    record = np.kron(SITE[0], np.eye(2)) + np.kron(SITE[1], rotate)
    local_phase = np.kron(np.diag([1., np.exp(1j * phase)]), np.eye(2))
    first_u = np.kron(hopping(first), np.eye(2))
    second_u = np.kron(hopping(second), np.eye(2)) @ local_phase @ record
    projectors = [np.kron(p, np.eye(2)) for p in SITE]
    return np.array([1., 0., 0., 0.], dtype=complex), [
        (first_u, projectors), (second_u, projectors)]


def signed_extent(weights, volumes=None, tolerance=1e-12):
    """No probability repair: significant negatives invalidate ordinary entropy.

    Sub-tolerance negative floating-point residues contribute zero to x log x;
    weights are never rescaled and the original signed values are retained.
    """
    weights = np.asarray(weights, dtype=float)
    volumes = np.ones_like(weights) if volumes is None else np.asarray(volumes, dtype=float)
    if volumes.shape != weights.shape or np.any(volumes <= 0):
        raise ValueError("Positive reference cell volumes required")
    if np.any(~np.isfinite(weights)) or not np.isclose(weights.sum(), 1., atol=tolerance, rtol=0):
        raise ValueError("Normalized finite signed weights required")
    if np.min(weights) < -tolerance:
        return None
    positive = weights > 0
    return float(np.exp(-np.dot(weights[positive], np.log(weights[positive] / volumes[positive]))))


def analyze(psi, stages):
    rows, labels = expand_history(psi, stages)
    matrix = decoherence_matrix(rows)
    z = matrix.sum(axis=1)
    q = z.real
    state = psi.copy()
    marginals = []
    for u, ps in stages:
        state = u @ state
        marginals.append([float(np.vdot(p @ state, p @ state).real) for p in ps])
    groups = [[i for i, label in enumerate(labels) if label[-1] == y]
              for y in range(len(stages[-1][1]))]
    coarse = grouped_matrix(matrix, groups)
    q_endpoint = np.array([q[g].sum() for g in groups])
    q_first = np.array([sum(q[i] for i, label in enumerate(labels) if label[0] == x)
                        for x in range(len(stages[0][1]))])
    result = {
        "labels": labels,
        "q": q.tolist(),
        "z_imag": z.imag.tolist(),
        "negative_mass": float(-q[q < -1e-12].sum()),
        "candidate_extent": signed_extent(q),
        "diagonal_history_breadth": effective_number(matrix.diagonal().real),
        "site_probabilities": marginals,
        "site_breadths": [effective_number(p) for p in marginals],
        "joint_endpoint_breadth": effective_number(abs(state)**2),
        "history_offdiagonal_max": float(np.max(abs(matrix - np.diag(matrix.diagonal())))),
        "normalization_error": float(abs(z.sum() - 1)),
        "amplitude_error": float(np.max(abs(rows.sum(axis=0) - state))),
        "endpoint_coarsening_error": float(np.max(abs(coarse.diagonal().real - marginals[-1]))),
        "q_endpoint_error": float(np.max(abs(q_endpoint - marginals[-1]))),
        "q_first_error": float(np.max(abs(q_first - marginals[0]))),
    }
    return result, matrix, z


def representation_checks():
    psi, stages = spatial_setup(np.pi / 4, np.pi / 6, 0., np.pi / 2)
    _, reference, z = analyze(psi, stages)
    rng = np.random.default_rng(814)
    w, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    rotate = [(w @ u @ w.conj().T, [w @ p @ w.conj().T for p in ps])
              for u, ps in stages]
    _, rotated, _ = analyze(w @ psi, rotate)
    enlarged = [(np.kron(u, np.eye(2)), [np.kron(p, np.eye(2)) for p in ps])
                for u, ps in stages]
    _, blank, _ = analyze(np.kron(psi, [1., 0.]), enlarged)
    _, identity, _ = analyze(psi, [(np.eye(4), [np.eye(4)])] + stages)
    half = np.kron(hopping(np.pi / 8), np.eye(2))
    subdivided = [(half, [np.eye(4)]), (half, stages[0][1]), stages[1]]
    _, split, _ = analyze(psi, subdivided)
    refined = [(half, stages[0][1]), (half, stages[0][1]), stages[1]]
    rows, labels = expand_history(psi, refined)
    grouped = [[i for i, label in enumerate(labels) if label[1:] == (a, b)]
               for a in range(2) for b in range(2)]
    recovered = grouped_matrix(decoherence_matrix(rows), grouped)

    product_stages = [(np.kron(u, u), [np.kron(p, q) for p in ps for q in ps])
                      for u, ps in stages]
    _, product_d, _ = analyze(np.kron(psi, psi), product_stages)
    # Product expansion labels order (a1,b1),(a2,b2), unlike kron's (a1,a2),(b1,b2).
    order = [(a1 * 2 + b1) * 4 + (a2 * 2 + b2)
             for a1 in range(2) for a2 in range(2)
             for b1 in range(2) for b2 in range(2)]
    product_d = product_d[np.ix_(order, order)]
    product_z = product_d.sum(axis=1)
    product_q = product_z.real
    individual_extent = signed_extent(z.real)
    joint_extent = signed_extent(product_q)
    return {
        "covariance_error": float(np.max(abs(rotated - reference))),
        "blank_ancilla_error": float(np.max(abs(blank - reference))),
        "identity_error": float(np.max(abs(identity - reference))),
        "subdivision_error": float(np.max(abs(split - reference))),
        "resolved_refinement_coarsening_error": float(np.max(abs(recovered - reference))),
        "independent_d_error": float(np.max(abs(product_d - np.kron(reference, reference)))),
        "independent_complex_z_error": float(np.max(abs(product_z - np.kron(z, z)))),
        "real_allocation_product_defect": float(np.max(abs(product_q - np.kron(z.real, z.real)))),
        "individual_candidate_extent": individual_extent,
        "product_candidate_extent": joint_extent,
        "squared_individual_candidate_extent": None if individual_extent is None else individual_extent**2,
        "product_minimum_q": float(product_q.min()),
        "product_negative_mass": float(-product_q[product_q < -1e-12].sum()),
    }
