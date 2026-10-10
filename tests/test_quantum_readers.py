import numpy as np
import pytest

from omega_v2.finite.quantum_readers import (
    controlled_reader,
    observational_controls,
    record_retention,
    sequential_readers,
)


def test_endogenous_reader_weights_and_chain_rule():
    for r in [.25, .5, .75]:
        result, _ = controlled_reader(r)
        assert result["record_probabilities"] == pytest.approx([r, 0, (1-r)/2, (1-r)/2])
        assert result["chain_rule_log_error"] < 1e-12
        assert result["born_error"] < 1e-12
        assert result["global_state_breadth"] == pytest.approx(1)
    assert controlled_reader(.5)[0]["record_breadth"] == pytest.approx(2*np.sqrt(2))


def test_sequential_disturbance_is_order_sensitive():
    zx = sequential_readers("ZX")
    xz = sequential_readers("XZ")
    assert zx["record_probabilities"] == pytest.approx([.5, .5, 0, 0])
    assert xz["record_probabilities"] == pytest.approx([.25]*4)
    assert zx["record_breadth"] == pytest.approx(2)
    assert xz["record_breadth"] == pytest.approx(4)


def test_uncomputation_versus_environment_transfer():
    retained = record_retention("retain")
    undone = record_retention("uncompute")
    transferred = record_retention("transfer")
    assert [retained["record_breadth"], undone["record_breadth"], transferred["record_breadth"]] == pytest.approx([4, 1, 4])
    assert transferred["local_record_breadth"] == pytest.approx(2)
    assert retained["history_offdiagonal_max"] < 1e-12
    assert transferred["history_offdiagonal_max"] < 1e-12
    assert undone["history_offdiagonal_max"] == pytest.approx(.25)
    assert undone["fine_history_breadth"] == pytest.approx(4)
    for result in [retained, undone, transferred]:
        assert result["amplitude_reconstruction_error"] < 1e-12
        assert result["born_error"] < 1e-12
        assert result["global_state_breadth"] == pytest.approx(1)


def test_observational_reference_volume_and_incompatible_rank_one_bases():
    result = observational_controls()
    assert result["rank_one_Z"] == pytest.approx(1)
    assert result["rank_one_X"] == pytest.approx(2)
    assert result["reader_observational_extent"] == pytest.approx(2*result["reader_record_breadth"])
    assert result["with_blank_ancilla"] == pytest.approx(2*result["reader_observational_extent"])
