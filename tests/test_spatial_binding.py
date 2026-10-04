import numpy as np

from omega_v2.finite.continuation_readout import ContinuationReadout
from omega_v2.finite.spatial_binding import SpatialBinding


def test_local_reversibility_inventory_and_actual_assembly():
    m = SpatialBinding(capacity=2)
    flux = m.pi[:, None] * m.q
    assert np.allclose(flux, flux.T)
    assert np.max(abs(m.pi @ m.q)) < 1e-14
    reflected = [
        m.index[(*state[:5][::-1], int(f"{state[5]:04b}"[::-1], 2), state[6])] for state in m.states
    ]
    assert np.allclose(m.q[np.ix_(reflected, reflected)], m.q)
    assert np.all((m.states[:, :5] >= 0).sum(axis=1) == 3)
    for c in range(len(m.rates)):
        active = m.rates[c] > 0
        assert np.all(m.q[m.targets[c, active], m.ids[active]] > 0)
    p = m.initial("contact_unbound")
    k, charges = m.evolution(0.2)
    assert p @ k @ m.bond_count > 0
    bill = p @ charges
    assert np.isclose(p @ m.fuel - p @ k @ m.fuel, bill[0] - bill[1])
    assert np.isclose(
        p @ k @ m.bond_count - p @ m.bond_count, bill[0] - bill[1] + bill[2] - bill[3]
    )


def test_preparations_same_stored_energy_and_full_frame_is_injective():
    m = SpatialBinding(capacity=2)
    for kind in ("dispersed", "contact_unbound", "assembled"):
        p = m.initial(kind)
        assert np.isclose(p @ m.energy, 8)
        assert np.isclose(p.sum(), 1)
    readout = ContinuationReadout(m, {0: [], 1: list(range(10))})
    assert readout.frames[1][1].shape[1] == len(m.ids)
    result = readout.profiles(m.initial("assembled"), 0)
    assert np.allclose(result["reaction_response_tv"][0], 0)
    active = np.array(result["event_present"])
    assert np.allclose(np.array(result["reaction_response_tv"])[1, active], 1)
    assert np.allclose(result["incremental_prediction_bits"], 0)


def test_translation_and_exchange_transport_internal_state_without_labels():
    m = SpatialBinding(capacity=2)
    x = m.index[(-1, 0, 1, 0, -1, 6, 0)]
    c = m.channel_names.index("move_1_3_1")
    y = m.targets[c, x]
    assert tuple(m.states[y]) == (-1, -1, 0, 1, 0, 12, 0)
    assert m.rates[c, x] == m.mobility / 3
    # The same contact exchange rule applies with or without a bond.
    unbound = m.index[(-1, 0, 1, 0, -1, 0, 0)]
    assert m.rates[6, x] == m.rates[6, unbound] == 1
