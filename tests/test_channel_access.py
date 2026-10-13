import numpy as np

from omega_v2.testbed.analysis.channel_access import (
    access_witness, closure_certificate, closure_mask, first_passage, recovery_profile,
)


def test_finite_barrier_thermal_reconstruction_keeps_channel_structurally_open():
    # Inactive apparatus can be thermally reconstructed; active apparatus can
    # also wear down. Positive reverse noise makes the two-state chain recurrent.
    q = np.array([[-0.3, 0.3], [0.1, -0.1]])
    target = np.array([False, True])
    assert not closure_mask(q, target).any()
    passage = first_passage(q, 0, target, 2.0)
    assert 0.0 < passage["hit_probability"] < 1.0
    assert abs(passage["hit_probability"] + passage["survival_probability"] - 1.0) < 1e-12

    profile = recovery_profile(q, 0, target, [0.0, 2.0])
    assert profile["0.0"]["hit_probability"] == 0.0
    assert profile["2.0"]["hit_probability"] > profile["2.0"]["endpoint_target_probability"]
    assert profile["2.0"]["integrated_target_occupation"] > 0.0


def test_pure_death_hit_cdf_matches_erlang_independent_formula():
    rate = 0.7
    q = np.zeros((4, 4))
    for i in range(1, 4):
        q[i, i - 1] = rate
        q[i, i] = -rate
    target = np.array([True, False, False, False])
    assert not closure_mask(q, target).any()
    horizon = 1.3
    expected = 1.0 - np.exp(-rate * horizon) * (1.0 + rate * horizon + (rate * horizon) ** 2 / 2.0)
    result = first_passage(q, 3, target, horizon)
    assert abs(result["hit_probability"] - expected) < 1e-11
    assert result["survivor_distribution"][0] == 0.0


def test_exact_closure_and_initial_mass_in_target():
    q = np.array([
        [-1.0, 1.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ])
    target = np.array([False, True, False])
    np.testing.assert_array_equal(closure_mask(q, target), [False, False, True])
    result = first_passage(q, [0.25, 0.5, 0.25], target, 0.0)
    assert result["hit_probability"] == 0.5
    assert result["survival_probability"] == 0.5
    assert access_witness(q, 0, target) == [0, 1]
    assert access_witness(q, 2, target) is None
    assert closure_certificate(q, [False, True, True]) == {
        "closed": True,
        "state_count": 2,
        "outgoing_positive_edge_count": 0,
        "outgoing_positive_rate_sum": 0.0,
    }
    certificate = closure_certificate(q, [True, False, False])
    assert certificate["closed"] is False
    assert certificate["outgoing_positive_edge_count"] == 1
