import numpy as np
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.catalytic_binding import CatalyticBinding


def test_catalysis_preserves_reversibility_and_uses_unchanged_neighbor():
    m = CatalyticBinding(barrier=1, capacity=3)
    flux = m.pi[:, None] * m.q
    assert np.max(abs(flux - flux.T)) < 1e-14
    for c, (edge, neighbor) in enumerate(m.catalytic_pairs, m.base_channels):
        x = np.flatnonzero(m.rates[c])
        y = m.targets[c, x]
        assert np.all((m.states[x, 5] & (1 << neighbor)) != 0)
        assert np.all(m.states[x, neighbor] == m.states[x, neighbor + 1])
        assert np.all(m.values[x, 5 + neighbor] == m.values[y, 5 + neighbor])
        assert np.allclose(m.pi[x] * m.rates[c, x], m.pi[y] * m.rates[c, y])
        assert np.all(abs(m.fuel[y] - m.fuel[x]) == 1)
        assert np.all(m.values[x, 5 + edge] != m.values[y, 5 + edge])


def test_two_stage_monitor_marginal_is_the_physical_law():
    m = CatalyticBinding(barrier=1)
    p = m.initial("seeded")
    q = m.two_stage_generator()
    initial = np.concatenate((p, np.zeros(2 * len(p))))
    result = expm_multiply(q.T * 0.2, initial).reshape(3, -1)
    assert result[2].sum() > 0
    assert np.allclose(result.sum(axis=0), m.advance(p, 0.2))
    bill = p @ m.charges(0.2)
    later = m.advance(p, 0.2)
    assert np.isclose(p @ m.fuel - later @ m.fuel, bill[0] - bill[1])
    assert np.isclose(
        later @ m.bond_count - p @ m.bond_count, bill[0] - bill[1] + bill[2] - bill[3]
    )
    assert bill[6] <= bill[0] and bill[7] <= bill[1]


def test_symmetries_and_resource_match():
    m = CatalyticBinding(barrier=1)
    reflected = [
        m.index[(*state[:5][::-1], int(f"{state[5]:04b}"[::-1], 2), state[6])] for state in m.states
    ]
    inverted = [
        m.index[(*(1 - v if v >= 0 else -1 for v in state[:5]), state[5], state[6])]
        for state in m.states
    ]
    assert np.allclose(m.q[np.ix_(reflected, reflected)], m.q)
    assert np.allclose(m.q[np.ix_(inverted, inverted)], m.q)
    a, b = m.snapshot(m.initial("contact_unbound")), m.snapshot(m.initial("assembled"))
    assert np.isclose(a["stored_energy"], b["stored_energy"])
    assert np.isclose(a["free_energy_nats"], b["free_energy_nats"])
    broken = m.breakdown(m.initial("seeded"))
    assert np.isclose(broken["after"].sum(), 1)
    assert broken["after"] @ m.values[:, 5] == 0
