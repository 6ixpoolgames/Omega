"""Unitary physical readers and reversible records for tiny extent probes."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.quantum_extent import effective_number, evaluate

H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)


def local_gate(matrix, target, width):
    result = np.ones((1, 1))
    for site in range(width):
        result = np.kron(result, matrix if site == target else np.eye(2))
    return result


def cnot(control, target, width):
    if control == target:
        raise ValueError("Distinct sites required")
    result = np.zeros((2**width, 2**width))
    for x in range(2**width):
        flip = (x >> (width - 1 - control)) & 1
        y = x ^ (flip << (width - 1 - target))
        result[y, x] = 1
    return result


def projectors(sites, width):
    labels = [sum(((x >> (width - 1 - site)) & 1) << (len(sites) - 1 - i)
                  for i, site in enumerate(sites)) for x in range(2**width)]
    return [np.diag(np.array(labels) == y).astype(float) for y in range(2**len(sites))]


def initial(width):
    state = np.zeros(2**width, dtype=complex)
    state[0] = 1
    return state


def record_gate(basis, signal, memory, width):
    gate = cnot(signal, memory, width)
    if basis == "Z":
        return gate
    if basis == "X":
        h = local_gate(H, signal, width)
        return h @ gate @ h
    raise ValueError("Unknown basis")


def controlled_reader(r):
    """C,S,M; C=0 selects Z, C=1 selects X. Return result and full state."""
    if not 0 <= r <= 1:
        raise ValueError("Preparation weight outside [0,1]")
    preparation = np.array([[np.sqrt(r), -np.sqrt(1-r)],
                            [np.sqrt(1-r), np.sqrt(r)]])
    psi = local_gate(preparation, 0, 3) @ initial(3)
    z, x = [record_gate(basis, 0, 1, 2) for basis in ["Z", "X"]]
    unitary = np.kron(np.diag([1, 0]), z) + np.kron(np.diag([0, 1]), x)
    result, _ = evaluate(psi, [(unitary, projectors((0, 2), 3))])
    state = unitary @ psi
    memory_p = np.array(result["record_probabilities"]).reshape(2, 2).sum(axis=0)
    result["memory_only_breadth"] = effective_number(memory_p)
    result["chain_rule_log_error"] = float(abs(np.log(result["record_breadth"])
        - np.log(effective_number([r, 1-r])) - (1-r)*np.log(2)))
    return result, state


def sequential_readers(order):
    """S,M1,M2; both readouts are actual unitary recording interactions."""
    unitary = record_gate(order[1], 0, 2, 3) @ record_gate(order[0], 0, 1, 3)
    result, _ = evaluate(initial(3), [(unitary, projectors((1, 2), 3))])
    return result


def record_retention(mode):
    """S,M1,M2,E. First-stage M1 alternatives are not artificially collapsed."""
    width = 4
    h = local_gate(H, 0, width)
    first = cnot(0, 1, width) @ h
    if mode == "retain":
        between = np.eye(16)
    elif mode == "uncompute":
        between = cnot(0, 1, width)
    elif mode == "transfer":
        between = cnot(1, 3, width) @ cnot(3, 1, width) @ cnot(1, 3, width)
    else:
        raise ValueError("Unknown record treatment")
    second = cnot(0, 2, width) @ h @ between
    stages = [(first, projectors((1,), width)),
              (second, projectors((1, 2, 3), width))]
    result, matrix = evaluate(initial(width), stages)
    result["history_offdiagonal_max"] = float(np.max(np.abs(matrix-np.diag(np.diag(matrix)))))
    full_p = np.array(result["record_probabilities"]).reshape(2, 2, 2)
    local_p = full_p.sum(axis=2).reshape(-1)
    result["local_record_probabilities"] = local_p.tolist()
    result["local_record_breadth"] = effective_number(local_p)
    return result


def observational_extent(psi, partitions):
    """Single-time exp observational entropy; volumes use full Hilbert trace.

    This reference measure intentionally counts unresolved Hilbert dimensions,
    not solely reachable support of the supplied pure root.
    """
    probabilities = np.array([np.vdot(p @ psi, p @ psi).real for p in partitions])
    volumes = np.array([np.trace(p).real for p in partitions])
    positive = probabilities > 0
    entropy = -np.sum(probabilities[positive] * np.log(probabilities[positive]/volumes[positive]))
    return float(np.exp(entropy))


def observational_controls():
    psi = initial(1)
    z = projectors((0,), 1)
    x = [H @ p @ H for p in z]
    r = .5
    result, state = controlled_reader(r)
    parts = projectors((0, 2), 3)
    return {
        "rank_one_Z": observational_extent(psi, z),
        "rank_one_X": observational_extent(psi, x),
        "reader_record_breadth": result["record_breadth"],
        "reader_observational_extent": observational_extent(state, parts),
        "with_blank_ancilla": observational_extent(np.kron(state, [1, 0]),
                                                  [np.kron(p, np.eye(2)) for p in parts]),
    }
