import numpy as np

from omega_v2.finite.extent_probe_models import devices, history_profiles, reversible_gate


def test_exact_history_endpoints_and_mass():
    for device in devices():
        initial, kernel = device.arrays()
        histories = history_profiles(device, 3)
        measured = np.array([histories['endpoints'].get(s, 0) for s in device.states])
        assert abs(histories['mass']-1) < 1e-12
        np.testing.assert_allclose(measured, initial @ np.linalg.matrix_power(kernel, 3),
                                   atol=1e-12, rtol=0)


def test_gate_accelerates_both_directions_and_preserves_equilibrium():
    off, on = reversible_gate(False), reversible_gate(True)
    _, k0 = off.arrays()
    _, k1 = on.arrays()
    index = {s: i for i, s in enumerate(on.states)}
    for bit in (0, 1):
        i, j = index[1, bit], index[1, 1-bit]
        assert k1[i, j] == 7*k0[i, j]
    np.testing.assert_allclose(k1, k1.T, atol=0, rtol=0)
    np.testing.assert_allclose(np.ones(4)/4 @ k1, np.ones(4)/4)
