import numpy as np

from omega_v2.finite.fuel_flow import FuelFlow


def test_reversible_fuel_accounting_and_preparation_charge():
    m = FuelFlow(3)
    assert np.isclose(m.initial(False) @ m.energy, m.initial(True) @ m.energy)
    for rate, targets in zip(m.rates, m.targets, strict=True):
        active = rate > 0
        assert np.array_equal(targets[targets[active]], m.ids[active])
        assert np.allclose(
            m.pi[active] * rate[active], m.pi[targets[active]] * rate[targets[active]]
        )
    assert np.allclose(m.pi @ m.q, 0)
    k, charges = m.evolution(2)
    p = m.initial(False)
    bill = p @ charges
    assert np.isclose(p @ m.fuel - p @ k @ m.fuel, bill[0] - bill[1] + bill[2] - bill[3])


def test_zero_fuel_is_not_a_terminal_and_restart_keeps_stock():
    m = FuelFlow(1)
    p = m.initial(True)
    assert p @ m.exhaustion_probability(0) == 1
    assert (p @ m.evolution(1)[0])[m.fuel > 0].sum() > 0
    assert np.allclose(m.evolution(0.3)[0] @ m.evolution(0.7)[0], m.evolution(1)[0])


def test_repair_occurs_under_same_generator_and_absorption_is_separate():
    m = FuelFlow(2)
    broken = m.initial(False)
    later = broken @ m.evolution(1)[0]
    assert m.snapshot(later)["link_on_probability"] > 0
    cut = m.breakdown_cut(later)
    assert cut["rate"] > 0
    assert np.isclose(cut["after"].sum(), 1)
    assert cut["after"] @ m.bits[:, 3] == 0
    assert cut["after"] @ m.evolution(1)[0] @ m.bits[:, 3] > 0
    assert (
        broken @ m.exhaustion_probability(2)
        >= m.snapshot(broken @ m.evolution(2)[0])["fuel_zero_probability"] - 1e-12
    )
