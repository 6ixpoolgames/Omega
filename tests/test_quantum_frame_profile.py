"""Independent analytic and contraction checks for the finite quantum probe."""

from itertools import product

import numpy as np
import pytest

from omega_v2.experiments.quantum_frame_profile_v0 import (
    PREPARATIONS,
    PROTOCOL_SHA256,
    calibrations,
    causal_trace_error,
    network,
    source_state,
)
from omega_v2.finite.quantum_profile import (
    Density,
    contract_inputs,
    ensemble_density,
    mutual_information,
    record_diagnostics,
)
from omega_v2.validation.quantum_frame_profile_v0 import protocol_digest


def test_protocol_is_frozen():
    assert protocol_digest() == PROTOCOL_SHA256


def test_sparse_trace_and_entropy_against_dense_entangled_state():
    rng = np.random.default_rng(1907)
    ket = rng.normal(size=16) + 1j*rng.normal(size=16)
    ket /= np.linalg.norm(ket)
    state = ensemble_density(("a", "b", "c", "d"), [(1.0, dict(enumerate(ket)))])
    # Keep a,c; independently reshape the ket into kept/environment Schmidt matrix.
    schmidt = ket.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
    expected = schmidt @ schmidt.conj().T
    reduced = state.partial(["a", "c"])
    assert np.allclose(reduced.matrix(), expected, atol=1e-12, rtol=0)
    singular_values = np.linalg.svd(schmidt, compute_uv=False)
    probabilities = singular_values**2
    assert reduced.entropy() == pytest.approx(-sum(probabilities*np.log2(probabilities)), abs=1e-12)


@pytest.mark.parametrize("name", PREPARATIONS)
def test_causal_comb_constraints_and_physical_contraction(name):
    previous = None
    states = [source_state(.8), source_state(.5), np.ones((2, 2))/2,
              np.array([[1, -1j], [1j, 1]])/2]
    for horizon in (1, 2):
        choi, full, _ = network(name, horizon, choi=True)
        assert full.trace() == pytest.approx(1, abs=1e-12)
        assert causal_trace_error(choi, previous) < 1e-12
        for prep in states:
            actual, _, _ = network(name, horizon, preparation=prep)
            linked = contract_inputs(choi, {f"I{j}": prep for j in range(1, horizon+1)})
            assert actual.distance_max(linked) < 1e-12
        previous = choi


@pytest.mark.parametrize("name", PREPARATIONS)
def test_classical_limit_matches_closed_form_complete_output_law(name):
    # Formula for outputs, independent of the gate simulator and partial trace.
    expected = {}
    for s1, s2, delay in product((0, 1), repeat=3):
        q = .2 if name == "common_delay" else 0
        mass = (.8 if s1 == 0 else .2)*(.8 if s2 == 0 else .2)*(q if delay else 1-q)
        if not mass:
            continue
        bits = []
        for j, source in enumerate((s1, s2), 1):
            r = 0 if name == "erased" else source
            m = 0 if name == "erased" or (name == "damaged" and j == 1) or delay else source
            d = 0 if name in ("erased", "cycling") else m
            k = source if name == "photocopier" else delay
            bits.extend((source, r, m, d, k))
        basis = int("".join(map(str, bits)), 2)
        expected[basis] = expected.get(basis, 0)+mass
    actual, _, _ = network(name, 2)
    expected_state = Density(actual.labels, {(basis, basis): mass for basis, mass in expected.items()})
    assert actual.distance_max(expected_state) < 1e-12


def test_repair_changes_later_delivery_and_erasure_retains_bath():
    h = -(.8*np.log2(.8)+.2*np.log2(.2))
    expected = {"intact": (h, h), "damaged": (0, h), "erased": (0, 0), "cycling": (0, 0)}
    for name, infos in expected.items():
        actual, full, _ = network(name, 2)
        observed = record_diagnostics(actual, 2)["sources"]
        assert [r["downstream_information_bits"] for r in observed] == pytest.approx(infos)
        if name == "erased":
            for j in (1, 2):
                assert mutual_information(full, [f"S{j}"], [f"E{j}"]) == pytest.approx(h)


def test_analytic_controls():
    controls = calibrations()
    h = -(.8*np.log2(.8)+.2*np.log2(.2))
    ghz = controls["ghz"]
    assert ghz["system_to_one_environment_bit"] == pytest.approx(h)
    assert ghz["system_to_all_environment"] == pytest.approx(2*h)
    assert [r["mutual_information_bits"] for r in ghz["profile"]["labelled_fragments"]] == pytest.approx([2*h]*14)
    sw = controls["identity_swap"]
    assert sw["size_multiset_max_difference"] < 1e-12
    assert sw["identity_I1_O1_information"] == pytest.approx(2)
    assert sw["swap_I1_O1_information"] == pytest.approx(0)
    hh = controls["identity_hadamard"]
    assert [r["mutual_information_bits"] for r in hh["identity_profile"]["labelled_fragments"]] == pytest.approx([2, 2])
    assert [r["mutual_information_bits"] for r in hh["hadamard_profile"]["labelled_fragments"]] == pytest.approx([2, 2])
    assert controls["temporal_subdivision"]["composed_matrix_max_difference"] < 1e-12


def test_coherences_are_not_replaced_by_classical_histories():
    intact, _, _ = network("intact", 1, choi=True)
    erased, full, _ = network("erased", 1, choi=True)
    assert intact.entropy() == pytest.approx(0, abs=1e-12)
    assert any(r != c and abs(v) > .1 for (r, c), v in intact.entries.items())
    assert erased.entropy() == pytest.approx(1, abs=1e-12)
    assert full.entropy() == pytest.approx(0, abs=1e-12)


def test_future_cycle_cannot_signal_to_earlier_outputs():
    for name in PREPARATIONS:
        first, _, _ = network(name, 1, preparation=source_state(.8))
        both, _, _ = network(name, 2, preparation=source_state(.8))
        assert first.distance_max(both.partial(first.labels)) < 1e-12


def test_invalid_factors_are_not_silently_relabelled():
    state = Density(("a",), {(0, 0): 1})
    with pytest.raises(ValueError):
        state.partial(["unknown"])
    with pytest.raises(ValueError):
        state.partial(["a", "a"])
