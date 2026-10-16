import numpy as np

from omega_v2.finite.local_flow import Flip, LocalFlow


def test_equilibrium_retains_memory_and_has_no_net_current():
    energy = np.array([0, 2, 2, 0], dtype=float)
    model = LocalFlow(2, [Flip(0, 0.1), Flip(1, 0.1)], energy)
    expected = np.exp(-energy)
    expected /= expected.sum()
    assert np.allclose(model.pi, expected)
    assert np.allclose(model.pi[:, None] * model.q, (model.pi[:, None] * model.q).T)
    assert abs(model.thermodynamics()["entropy_production_nats_per_time"]) < 1e-12
    assert model.thermodynamics()["activity_per_time"] > 0
    assert model.profiles(0.1)["memory_bits"][1] > 0


def test_restart_and_no_remote_effect_without_coupling():
    model = LocalFlow(2, [Flip(0, 0.1), Flip(1, 0.1)])
    assert np.allclose(model.kernel(0.3) @ model.kernel(0.7), model.kernel(1))
    profile = model.profiles(1)
    assert profile["flip_response_tv"][2][0] < 1e-12
    assert np.isclose(profile["flip_response_tv"][1][0], np.exp(-0.2))


def test_signed_flow_complements_and_conditional_blind_spot():
    model = LocalFlow(2, [Flip(0, 0.02), Flip(1, 0.1), Flip(1, 1, 4, (0,), 2)])
    flow = model.signed_flow()
    assert np.isclose(flow[1] + flow[2], 0, atol=1e-12)
    assert model.thermodynamics()["entropy_production_nats_per_time"] > 0
    profile = model.profiles(0.1, [0.5, 0, 0, 0.5])
    assert abs(profile["incremental_bits"][0]) < 1e-12
    assert profile["held_bits"][2][0] > 0
    assert profile["flip_response_tv"][2][0] > 0
