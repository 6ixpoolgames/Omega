"""Analytic, representation and physical-accounting checks for the follow-up."""

from itertools import product

import numpy as np
import pytest

from omega_v2.experiments.quantum_record_structure_v0 import (
    PROTOCOL_SHA256,
    Gate,
    apparatus_graph,
    bath_bill,
    bath_layer,
    bath_layers,
    bath_start,
    diagonal_source,
    evolve,
    initial_ensemble,
    inverse,
    isomorphic,
    routing_bill,
    routing_setup,
    routing_state,
)
from omega_v2.finite.quantum_profile import (
    Density,
    contract_inputs,
    dephase,
    ensemble_density,
    mutual_information,
    profile,
)
from omega_v2.validation.quantum_record_structure_v0 import (
    delivery,
    fragment_rows,
    protocol_digest,
    relational_controls,
)


def h2(p):
    return -p*np.log2(p)-(1-p)*np.log2(1-p)


def dense(state):
    result = np.zeros((2**len(state.labels),)*2, dtype=complex)
    for (r, c), value in state.entries.items():
        result[r, c] = value
    return result


def test_freeze():
    assert protocol_digest() == PROTOCOL_SHA256


@pytest.mark.parametrize("mode", ("broadcast", "plural"))
@pytest.mark.parametrize("p", (.8, .5))
def test_complete_routing_law_matches_boolean_algebra(mode, p):
    for cut in (3, 6, 9):
        _, full = routing_state(mode, cut, diagonal_source(p))
        entries = {}
        for source in product((0, 1), repeat=3):
            probability = np.prod([p if s == 0 else 1-p for s in source])
            records = (source[0],)*3 if mode == "broadcast" else source
            local = records if cut >= 6 else (0, 0, 0)
            composed = tuple(local[i]*local[(i+1)%3] for i in range(3)) if cut == 9 else (0, 0, 0)
            bits = (*source, *records, *local, *composed)
            basis = int("".join(map(str, bits)), 2)
            entries[basis, basis] = probability
        assert full.distance_max(Density(full.labels, entries)) < 1e-11
        assert full.entropy() == pytest.approx(3*h2(p), abs=1e-9)


@pytest.mark.parametrize("p", (.8, .5))
def test_content_and_redundancy_are_distinct(p):
    for mode in ("broadcast", "plural"):
        state, _ = routing_state(mode, 3, diagonal_source(p))
        data = delivery(state, ("S0", "S1", "S2"), ("R0", "R1", "R2"))
        assert data["joint_content_bits"] == pytest.approx(h2(p)*(1 if mode == "broadcast" else 3))
        assert len(data["singleton_90_percent_readers"]["S0"]) == (3 if mode == "broadcast" else 1)
        prof = profile(state.partial(("R0", "R1", "R2")))
        expected = h2(p) if mode == "broadcast" else 0
        assert [r["mutual_information_bits"] for r in prof["labelled_fragments"]] == pytest.approx([expected]*6)


@pytest.mark.parametrize("mode", ("broadcast", "plural"))
def test_boundary_choi_contracts_coherent_and_actual_sources(mode):
    for cut in (3, 6, 9):
        choi, _ = routing_state(mode, cut, diagonal_source(.8), choi=True)
        assert choi.partial(("I0", "I1", "I2")).distance_max(
            Density(("I0", "I1", "I2"), {(i, i): 1/8 for i in range(8)})) < 1e-11
        for prep in (diagonal_source(.8), diagonal_source(.5), np.ones((2, 2))/2,
                     np.array([[1, -1j], [1j, 1]])/2):
            actual, _ = routing_state(mode, cut, prep)
            linked = contract_inputs(choi, {f"I{i}": prep for i in range(3)})
            assert actual.distance_max(linked) < 1e-11


def test_resource_matching_and_clock_are_explicit():
    for cut in (3, 6, 9):
        for mode in ("broadcast", "plural"):
            _, _, gates, _ = routing_setup(mode)
            bill = routing_bill(cut)
            assert sum(g.op == "CX" for g in gates[:cut]) == bill["CNOT"]
            assert sum(g.op == "CCX" for g in gates[:cut]) == bill["Toffoli"]
            assert bill["elapsed_time"] == cut
    for mode in ("spreading", "echo"):
        for depth in range(9):
            gates = [g for layer in bath_layers(mode)[:depth] for g in layer]
            bill = bath_bill(depth)
            assert sum(g.op in ("RY", "RZ") for g in gates) == bill["rotations"]
            assert sum(g.op == "CZ" for g in gates) == bill["nearest_neighbour_CZ"]
            assert bill["elapsed_time"] == 4+len(gates)


@pytest.mark.parametrize("p", (.8, .5))
def test_localized_record_information_and_ideal_guessing(p):
    labels, ensemble = bath_start(p)
    full = ensemble_density(labels, ensemble)
    rows, _ = fragment_rows(full)
    assert mutual_information(full, ["X"], ["R"]) == pytest.approx(0)
    for row in rows:
        has_record = "E0" in row["fragment"]
        expected = h2(p) if has_record else 0
        assert row["holevo_information_bits"] == pytest.approx(expected)
        assert row["z_readout_information_bits"] == pytest.approx(expected)
        assert row["ideal_binary_guess_success"] == pytest.approx(1 if has_record else max(p, 1-p))


def test_echo_and_inverse_are_full_state_restoration():
    labels, initial = bath_start(.8)
    base = ensemble_density(labels, initial)
    current = initial
    for i, layer in enumerate(bath_layers("echo"), 1):
        current = evolve(labels, current, layer)
        if i % 2 == 0:
            assert ensemble_density(labels, current).distance_max(base) < 1e-11
    gates = [g for layer in bath_layers("spreading") for g in layer]
    recovered = evolve(labels, evolve(labels, initial, gates), inverse(gates))
    assert ensemble_density(labels, recovered).distance_max(base) < 1e-11
    recovered = evolve(labels, recovered, [Gate("CX", "D", ("E0",))])
    measured = dephase(ensemble_density(labels, recovered))
    assert mutual_information(measured, ["X"], ["D"]) == pytest.approx(h2(.8), abs=1e-9)


def test_bath_mixing_against_independent_dense_unitary_and_trace():
    # Independent dense gate construction for a four-qubit chain and a complex ket.
    labels = ("E0", "E1", "E2", "E3")
    initial = initial_ensemble(labels, ("E0",), np.array([[1, -1j], [1j, 1]])/2)
    original = ensemble_density(labels, initial)
    rho = dense(original)
    for gate in bath_layer(3):
        if gate.op == "CZ":
            j, k = labels.index(gate.controls[0]), labels.index(gate.target)
            unitary = np.diag([-1 if ((i >> (3-j)) & 1) and ((i >> (3-k)) & 1) else 1
                               for i in range(16)])
        else:
            a = gate.angle/2
            one = (np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
                   if gate.op == "RY" else np.diag([np.exp(-1j*a), np.exp(1j*a)]))
            unitary = np.array([[1]])
            for label in labels:
                unitary = np.kron(unitary, one if label == gate.target else np.eye(2))
        rho = unitary @ rho @ unitary.conj().T
    sparse = ensemble_density(labels, evolve(labels, initial, bath_layer(3)))
    assert np.max(np.abs(rho-dense(sparse))) < 1e-11
    reduced = np.einsum("abcb->ac", rho.reshape((2,)*8).transpose(
        0, 2, 1, 3, 4, 6, 5, 7).reshape(4, 4, 4, 4))
    assert np.max(np.abs(reduced-dense(sparse.partial(("E0", "E2")))) ) < 1e-11


def test_relabelling_preserves_whole_apparatus_and_rewiring_does_not():
    result = relational_controls()
    for name in ("broadcast", "plural", "bath"):
        assert result[name]["graph_isomorphic"]
        assert result[name]["full_state_error_after_mapping_back"] < 1e-11
    assert not result["broadcast_plural_isomorphic"]
    assert not result["embedded_routing"]["isomorphic"]
    assert result["embedded_routing"]["identity_anchor_reader_bits"] == pytest.approx(1)
    assert result["embedded_routing"]["swap_anchor_reader_bits"] == pytest.approx(0)


def test_preparation_probabilities_cannot_be_relabelled_away():
    labels, sources, gates, _ = routing_setup("plural")
    a = apparatus_graph(labels, sources, gates, [], preparation=diagonal_source(.8))
    b = apparatus_graph(labels, sources, gates, [], preparation=diagonal_source(.5))
    assert not isomorphic(a, b)
