import numpy as np
import pytest

from omega_v2.finite.quantum_extent import (
    circuit,
    decoherence_matrix,
    effective_number,
    evaluate,
    expand_history,
    quantum_measure,
    record_weights,
)


def test_interferometer_phase_and_refinement():
    for phi, expected in [(0, 1), (np.pi / 2, 2), (np.pi, 1)]:
        result, _ = evaluate(*circuit(phi))
        assert result["fine_history_breadth"] == pytest.approx(4)
        assert result["spectral_breadth"] == pytest.approx(2)
        assert result["record_breadth"] == pytest.approx(expected)
        for checkpoints in ["none", "zx"]:
            other, _ = evaluate(*circuit(phi, checkpoints=checkpoints))
            assert other["record_probabilities"] == pytest.approx(result["record_probabilities"])
            assert other["amplitude_reconstruction_error"] < 1e-12


def test_marker_and_unpostselected_eraser():
    for phi in [0, np.pi / 2, np.pi]:
        joint, _ = evaluate(*circuit(phi, eta=0, reader="joint"))
        assert [joint[k] for k in ["fine_history_breadth", "spectral_breadth", "record_breadth"]] == pytest.approx([4, 4, 4])
        eraser, _ = evaluate(*circuit(phi, eta=0, reader="eraser"))
        expected = 2 * effective_number([(1 + np.cos(phi)) / 2, (1 - np.cos(phi)) / 2])
        assert eraser["record_breadth"] == pytest.approx(expected)
        assert eraser["fine_history_breadth"] == pytest.approx(8)
        assert eraser["spectral_breadth"] == pytest.approx(4)
        assert np.array(eraser["record_probabilities"]).reshape(2, 2).sum(axis=1) == pytest.approx([.5, .5])
        assert eraser["global_state_breadth"] == pytest.approx(1)
    for eta in [0, .5, 1]:
        for phi in [0, np.pi / 2, np.pi]:
            result, _ = evaluate(*circuit(phi, eta))
            assert result["record_probabilities"] == pytest.approx([(1 + eta*np.cos(phi))/2, (1 - eta*np.cos(phi))/2])


def test_quantum_measure_sum_rule_and_nonmonotonicity():
    _, matrix = evaluate(*circuit())
    # Histories ordered (a,y): 01 and 11 cancel at output y=1.
    assert quantum_measure(matrix, [1]) == pytest.approx(.25)
    assert quantum_measure(matrix, [1, 3]) == pytest.approx(0)
    a, b, c = [0], [1], [2, 3]
    rhs = (quantum_measure(matrix, a+b) + quantum_measure(matrix, a+c)
           + quantum_measure(matrix, b+c) - quantum_measure(matrix, a)
           - quantum_measure(matrix, b) - quantum_measure(matrix, c))
    assert quantum_measure(matrix, a+b+c) == pytest.approx(rhs)
    with pytest.raises(ValueError, match="not medium-decoherent"):
        record_weights(matrix, [[0], [1, 2, 3]])
    with pytest.raises(ValueError, match="normalized"):
        effective_number([.25, .25])


def test_description_invariances():
    psi, stages = circuit(.37, .5, "eraser")
    rows, _ = expand_history(psi, stages)
    result, matrix = evaluate(psi, stages)
    rng = np.random.default_rng(842)
    unitary, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j*rng.normal(size=(4, 4)))
    rotated = [(unitary @ u @ unitary.conj().T,
                [unitary @ p @ unitary.conj().T for p in projectors])
               for u, projectors in stages]
    other, rotated_matrix = evaluate(unitary @ psi, rotated)
    assert rotated_matrix == pytest.approx(matrix)
    assert other["record_breadth"] == pytest.approx(result["record_breadth"])
    permutation = rng.permutation(len(rows))
    assert decoherence_matrix(rows[permutation]) == pytest.approx(matrix[np.ix_(permutation, permutation)])
    enlarged = [(np.kron(u, np.eye(2)), [np.kron(p, np.eye(2)) for p in ps])
                for u, ps in stages]
    blank, blank_matrix = evaluate(np.kron(psi, [1, 0]), enlarged)
    assert blank_matrix == pytest.approx(matrix)
    assert blank["record_breadth"] == pytest.approx(result["record_breadth"])
    identity, identity_matrix = evaluate(psi, [(np.eye(4), [np.eye(4)])] + stages)
    assert identity_matrix == pytest.approx(matrix)
    assert identity["record_breadth"] == pytest.approx(result["record_breadth"])


def test_classical_recovery_and_independent_product():
    p = np.array([.9, .05, .05])
    matrix = np.diag(p).astype(complex)
    weights = record_weights(matrix, [[0], [1], [2]])
    assert effective_number(weights) == pytest.approx(effective_number(np.linalg.eigvalsh(matrix)))
    joint = np.kron(p, [.5, .5])
    assert effective_number(joint) == pytest.approx(2 * effective_number(p))
