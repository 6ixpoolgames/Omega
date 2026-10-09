import numpy as np
import pytest

from omega_v2.finite.quantum_eraser import eraser_case


@pytest.mark.parametrize("leak", [0., np.pi/6, np.pi/4, np.pi/2])
def test_conditional_fringe_cancellation_and_delayed_equality(leak):
    for phase in [0., np.pi/2, np.pi]:
        early, a = eraser_case("eraser_early", leak, phase)
        delayed, b = eraser_case("eraser_delayed", leak, phase)
        assert a == pytest.approx(b)
        assert early["signal_probabilities"] == pytest.approx([.5, .5])
        assert early["marker_weights"] == pytest.approx([.5, .5])
        assert early["conditional_signal"][0][0] == pytest.approx((1+np.cos(leak)*np.cos(phase))/2)
        assert early["conditional_signal"][1][0] == pytest.approx((1-np.cos(leak)*np.cos(phase))/2)
        assert delayed["delayed_signal_marginal_error"] < 1e-12


def test_copy_prevents_local_undo_but_joint_reversal_recovers():
    clean, _ = eraser_case("reverse_marker", 0., 0.)
    leaked, _ = eraser_case("reverse_marker", np.pi/2, 0.)
    recovered, _ = eraser_case("reverse_all", np.pi/2, 0.)
    assert clean["signal_probabilities"] == pytest.approx([1., 0.])
    assert leaked["signal_probabilities"] == pytest.approx([.5, .5])
    assert recovered["signal_probabilities"] == pytest.approx([1., 0.])
    assert leaked["path_record_trace_distance"] == pytest.approx(1)
    assert leaked["specified_marker_readout_path_tv"] == pytest.approx(0)


def test_conditional_eraser_does_not_merge_global_alternatives():
    r, _ = eraser_case("eraser_early", 0., 0.)
    assert r["signal_breadth"] == pytest.approx(2)
    assert r["conditional_geometric_signal_breadth"] == pytest.approx(1)
    assert r["record_breadth"] == pytest.approx(2)
    assert r["path_record_trace_distance"] == pytest.approx(1)
    assert r["specified_marker_readout_path_tv"] == pytest.approx(0)
    assert r["branch_inner_product_error"] < 1e-12
    assert r["global_purity_error"] < 1e-12
