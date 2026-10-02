"""Frozen tiny quantum record-network experiment; no lushness fit."""

from __future__ import annotations

from itertools import product

import numpy as np

from omega_v2.finite.quantum_profile import (
    Density,
    channel_choi,
    controlled_x,
    ensemble_density,
    mutual_information,
    profile,
    single_gate,
    size_multisets,
    swap,
    tensor,
)

PROTOCOL = "docs/research_notes/omega_v2/quantum_frame_profile_protocol_v0.md"
PROTOCOL_SHA256 = "769a83462ed7eead9e85973273546f265b1815437619eb19aedfbd6e448acd2e"
PREPARATIONS = {
    "intact": (1, 0, 1, 0, 0.0),
    "damaged": (0, 0, 1, 0, 0.0),
    "erased": (1, 1, 1, 0, 0.0),
    "cycling": (1, 0, 0, 0, 0.0),
    "photocopier": (1, 0, 1, 1, 0.0),
    "common_delay": (1, 0, 1, 0, 0.2),
}
HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def source_state(p):
    return np.diag([p, 1-p]).astype(complex)


def network(name, rounds, *, choi=False, preparation=None):
    """Return reduced interface, full quantum state, and classical memory log.

    Interface per round: S,R,M,D,K, preceded by I for Choi probes.
    Classical switches have definite values; Q's actual mixture is retained.
    """
    if rounds not in (1, 2):
        raise ValueError("protocol allows only one or two rounds")
    wire, erase, aligned, copy, q_probability = PREPARATIONS[name]
    labels = tuple(["Q"] + [f"{p}{j}" for j in range(1, rounds+1)
                             for p in (("I",) if choi else ()) + ("S", "R", "M", "D", "K", "E")])
    indices = {label: i for i, label in enumerate(labels)}
    width = len(labels)
    sources = []
    if not choi:
        prep = source_state(.8) if preparation is None else np.asarray(preparation, complex)
        values, vectors = np.linalg.eigh(prep)
        if values.min() < -1e-12 or abs(values.sum()-1) > 1e-12:
            raise ValueError("invalid source state")
        sources = [(float(v), vectors[:, i]) for i, v in enumerate(values) if v > 0]
    choices = [()] if choi else product(sources, repeat=rounds)
    choices = list(choices)
    ensemble = []
    for q, q_weight in ((0, 1-q_probability), (1, q_probability)):
        if not q_weight:
            continue
        for selection in choices:
            vector = {q << (width-1): 1.0 + 0j}
            weight = q_weight
            for j in range(1, rounds+1):
                s = indices[f"S{j}"]
                if choi:
                    i = indices[f"I{j}"]
                    vector = single_gate(vector, width, i, HADAMARD)
                    vector = controlled_x(vector, width, s, {i: 1})
                else:
                    source_weight, ket = selection[j-1]
                    weight *= source_weight
                    # Only the first column acts on an initially blank source.
                    gate = np.column_stack((ket, [-ket[1].conjugate(), ket[0].conjugate()]))
                    vector = single_gate(vector, width, s, gate)
            w, link = wire, 0
            for j in range(1, rounds+1):
                s, r, m, d, k, e = (indices[f"{p}{j}"] for p in "SRMDKE")
                vector = controlled_x(vector, width, r, {s: 1})
                if copy:
                    vector = controlled_x(vector, width, k, {s: 1})
                if erase:
                    vector = swap(vector, width, r, e)
                if w:
                    vector = controlled_x(vector, width, m, {r: 1, indices["Q"]: 0})
                if aligned and not erase:
                    w, link = 1, 1
                vector = controlled_x(vector, width, k, {indices["Q"]: 1})
                if link:
                    vector = controlled_x(vector, width, d, {m: 1})
            ensemble.append((weight, vector))
    full = ensemble_density(labels, ensemble)
    interface = tuple(label for label in labels if label != "Q" and not label.startswith("E"))
    memory, w, link = [], wire, 0
    for j in range(1, rounds+1):
        before = {"wire": w, "link": link}
        if aligned and not erase:
            w, link = 1, 1
        memory.append({"round": j, "before_installation": before,
                       "after_installation": {"wire": w, "link": link}})
    bill = {
        "rounds": rounds, "elapsed_time": 5*rounds, "fresh_source_qubits": rounds,
        "fresh_blank_qubits": 5*rounds, "delay_memory_qubits": 1,
        "classical_configuration_registers": 5,
        "scheduled_primitive_slots": 7*rounds,
        "virtual_choi_reference_qubits": rounds if choi else 0,
        "note": "Scheduled controlled primitives; not an energy or optimal implementation claim.",
    }
    return full.partial(interface), full, {"configuration_history": memory, "bill": bill}


def causal_trace_error(choi, previous=None):
    last = 1 if previous is None else 2
    kept = [label for label in choi.labels if not (label.endswith(str(last))
                                                  and not label.startswith("I"))]
    actual = choi.partial(kept)
    maximally_mixed = Density((f"I{last}",), {(0, 0): .5, (1, 1): .5})
    expected = maximally_mixed if previous is None else tensor(previous, maximally_mixed)
    return actual.distance_max(expected)


def calibrations():
    p = .8
    ghz = ensemble_density(("S", "E1", "E2", "E3"),
                           [(1.0, {0: complex(np.sqrt(p)), 15: complex(np.sqrt(1-p))})])
    ghz_profile = profile(ghz)
    ident = channel_choi(np.eye(4), ("I1", "I2"), ("O1", "O2"))
    swap_matrix = np.array([[1, 0, 0, 0], [0, 0, 1, 0],
                            [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
    swapped = channel_choi(swap_matrix, ("I1", "I2"), ("O1", "O2"))
    pi, ps = profile(ident), profile(swapped)
    mi, ms = size_multisets(pi), size_multisets(ps)
    single = channel_choi(np.eye(2), ("I",), ("O",))
    hadamard = channel_choi(HADAMARD, ("I",), ("O",))
    first = channel_choi(np.eye(2), ("I1",), ("O1",))
    second = channel_choi(np.eye(2), ("I2",), ("O2",))
    open_comb = tensor(first, second)
    # Join two normalized channel Choi matrices by the link product. The factor
    # d=2 compensates the second input's Choi normalization.
    linked_entries = {}
    for i, o, j, v in product(range(2), repeat=4):
        linked_entries[(i << 1) | o, (j << 1) | v] = 2 * sum(
            first.entries.get(((i << 1) | a, (j << 1) | b), 0)
            * second.entries.get(((a << 1) | o, (b << 1) | v), 0)
            for a, b in product(range(2), repeat=2))
    linked = Density(("I", "O"), linked_entries)
    return {
        "ghz": {
            "profile": ghz_profile,
            "system_to_one_environment_bit": mutual_information(ghz, ["S"], ["E1"]),
            "system_to_all_environment": mutual_information(ghz, ["S"], ["E1", "E2", "E3"]),
        },
        "identity_swap": {
            "identity_profile": pi, "swap_profile": ps,
            "size_multiset_max_difference": float(max(
                abs(a-b) for k in mi for a, b in zip(mi[k], ms[k], strict=True))),
            "identity_I1_O1_information": mutual_information(ident, ["I1"], ["O1"]),
            "swap_I1_O1_information": mutual_information(swapped, ["I1"], ["O1"]),
        },
        "identity_hadamard": {
            "identity_profile": profile(single), "hadamard_profile": profile(hadamard),
            "z_reader_identity_law": (.5*np.abs(np.eye(2))**2).tolist(),
            "z_reader_hadamard_law": (.5*np.abs(HADAMARD)**2).tolist(),
        },
        "temporal_subdivision": {
            "single_profile": profile(single), "two_open_slots_profile": profile(open_comb),
            "composed_matrix_max_difference": linked.distance_max(single),
        },
    }
