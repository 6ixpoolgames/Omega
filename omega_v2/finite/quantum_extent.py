"""Exact finite decoherence matrices; candidate breadth readouts, not an extent law."""

from __future__ import annotations

import numpy as np


def effective_number(weights):
    """Shannon effective number, refusing unnormalized weights."""
    weights = np.asarray(weights, dtype=float)
    if np.min(weights) < -1e-12 or not np.isclose(weights.sum(), 1, atol=1e-12):
        raise ValueError("Weights must be nonnegative and normalized; no repair normalization")
    positive = weights[weights > 0]
    return float(np.exp(-np.dot(positive, np.log(positive))))


def expand_history(psi, stages):
    """Stages are (unitary, exhaustive orthogonal projectors).

    Each row returned is C_alpha psi. Intermediate alternatives are amplitude
    contributions; they are not assumed to be decoherent physical records.
    """
    rows = np.asarray(psi, dtype=complex)[None, :]
    labels = [()]
    size = rows.shape[1]
    eye = np.eye(size)
    for unitary, projectors in stages:
        if not np.allclose(unitary.conj().T @ unitary, eye, atol=1e-12):
            raise ValueError("Nonunitary stage")
        if not np.allclose(sum(projectors), eye, atol=1e-12):
            raise ValueError("Incomplete projective family")
        for i, projector in enumerate(projectors):
            if not np.allclose(projector, projector.conj().T, atol=1e-12):
                raise ValueError("Non-Hermitian projector")
            for j, other in enumerate(projectors):
                target = projector if i == j else np.zeros_like(projector)
                if not np.allclose(projector @ other, target, atol=1e-12):
                    raise ValueError("Nonorthogonal/nonidempotent projectors")
        rows = np.array([p @ unitary @ row for row in rows for p in projectors])
        labels = [label + (i,) for label in labels for i in range(len(projectors))]
    return rows, labels


def decoherence_matrix(rows):
    """D_ab = <v_b|v_a>; Hermitian positive semidefinite Gram matrix."""
    return rows @ rows.conj().T


def grouped_matrix(matrix, groups):
    flattened = [i for group in groups for i in group]
    if sorted(flattened) != list(range(len(matrix))):
        raise ValueError("Groups must partition all histories exactly once")
    incidence = np.zeros((len(groups), len(matrix)))
    for r, group in enumerate(groups):
        incidence[r, group] = 1
    return incidence @ matrix @ incidence.T


def record_weights(matrix, groups):
    """Return weights for a supplied medium-decoherent partition.

    This checks the mathematical family, not physical record provenance.
    """
    grouped = grouped_matrix(matrix, groups)
    off_diagonal = grouped - np.diag(np.diag(grouped))
    if np.max(np.abs(off_diagonal)) > 1e-12:
        raise ValueError("Partition is not medium-decoherent; no classical record breadth")
    weights = np.real(np.diag(grouped))
    effective_number(weights)
    return weights


def quantum_measure(matrix, subset):
    return float(np.real(matrix[np.ix_(subset, subset)].sum()))


def circuit(phi=0.0, eta=1.0, reader="signal", checkpoints="z"):
    """Return initial state and stages for a two-qubit interferometer.

    eta is marker-state overlap. reader='eraser' means X on the marker,
    implemented by H followed by a full S,E computational readout.
    """
    if not 0 <= eta <= 1:
        raise ValueError("eta must lie in [0,1]")
    eye = np.eye(2)
    hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    z = [np.diag([1, 0]), np.diag([0, 1])]
    sz = [np.kron(p, eye) for p in z]
    psi = np.array([1, 0, 0, 0], dtype=complex)
    sine = np.sqrt(1 - eta**2)
    rotation = np.array([[eta, -sine], [sine, eta]])
    marker = np.kron(z[0], eye) + np.kron(z[1], rotation)
    phase = np.kron(np.diag([1, np.exp(1j * phi)]), eye)
    hs = np.kron(hadamard, eye)
    if checkpoints not in {"none", "z", "zx"}:
        raise ValueError("Unknown checkpoint expansion")
    stages = [(hs, [np.eye(4)] if checkpoints == "none" else sz)]
    if checkpoints == "zx":
        stages.append((np.eye(4), [hs @ p @ hs for p in sz]))
    final_u = hs @ phase @ marker
    if reader == "signal":
        final_projectors = sz
    elif reader in {"joint", "eraser"}:
        final_projectors = [np.diag(np.eye(4)[i]) for i in range(4)]
        if reader == "eraser":
            final_u = np.kron(eye, hadamard) @ final_u
    else:
        raise ValueError("Unknown reader")
    stages.append((final_u, final_projectors))
    return psi, stages


def evaluate(psi, stages):
    """Evaluate diagnostics for declared analytical history projectors.

    The legacy ``record_breadth`` is the specified endpoint Born breadth;
    actual record formation requires separate apparatus/model provenance.
    """
    rows, labels = expand_history(psi, stages)
    matrix = decoherence_matrix(rows)
    groups = [[i for i, label in enumerate(labels) if label[-1] == y]
              for y in range(len(stages[-1][1]))]
    probabilities = record_weights(matrix, groups)
    direct = np.array(psi, dtype=complex)
    for unitary, _ in stages:
        direct = unitary @ direct
    direct_p = np.array([np.vdot(p @ direct, p @ direct).real for p in stages[-1][1]])
    pure = np.outer(direct, direct.conj())
    result = {
        "fine_history_breadth": effective_number(np.real(np.diag(matrix))),
        "spectral_breadth": effective_number(np.linalg.eigvalsh(matrix)),
        "record_breadth": effective_number(probabilities),
        "global_state_breadth": effective_number(np.linalg.eigvalsh(pure)),
        "record_probabilities": probabilities.tolist(),
        "born_error": float(np.max(np.abs(probabilities - direct_p))),
        "amplitude_reconstruction_error": float(np.max(np.abs(rows.sum(axis=0) - direct))),
        "normalization_error": float(abs(matrix.sum() - 1)),
        "trace_error": float(abs(np.trace(matrix) - 1)),
    }
    return result, matrix
