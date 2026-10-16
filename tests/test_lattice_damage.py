from itertools import product

import numpy as np

from omega_v2.finite.lattice_chemistry import Event, LatticeChemistry, Parameters, State
from omega_v2.finite.lattice_damage import (
    connected,
    native_failure,
    observe,
    probe_coordinates,
    squared_response,
)


def square(bonds):
    return State([(0, 0), (1, 0), (0, 1), (1, 1)], [1] * 4, set(bonds), 4)


def test_bond_restoration_and_alternate_connection_are_distinct():
    state = square({(0, 1), (0, 2), (2, 3), (1, 3)})
    assert connected(state, (0, 1), exclude_pair=True)
    state.bonds.remove((0, 1))
    assert connected(state, (0, 1))
    state.bonds.remove((2, 3))
    assert not connected(state, (0, 1))


def test_native_failure_retains_hazard_zero_and_physical_energy_change():
    model = LatticeChemistry(Parameters(side=2, particles=4, capacity=4, catalytic_barrier=2))
    assert native_failure(model, square(set()), 0)["total_hazard"] == 0
    before = square({(0, 1)})
    failure = native_failure(model, before, 1)
    assert failure["selected"].members == (0, 1)
    assert failure["edge_probability_given_state"] == 1
    assert failure["after"].fuel == before.fuel
    assert failure["is_bridge"]
    assert failure["lost_template_formation_rate"] > 0
    assert failure["template_targets_before"] == 1
    assert failure["energy_change"] == model.p.bond_strength


def test_first_recovery_is_not_deadline_occupancy_or_persistence():
    model = LatticeChemistry(Parameters(side=2, particles=4, capacity=4))
    initial = square(set())
    pair = (0, 1)
    e = Event("thermal", pair, 1)
    trajectory = {"initial": initial.record(),
                  "events": [e.record(0.2), e.record(0.4)],
                  "snapshots": [{"catalytic_forward": 0}] * 3}
    views = observe(model, trajectory, pair, probe_coordinates(model, initial, pair), (0, 0.3, 1))
    assert [v["readouts"]["ever_original_bond"] for v in views] == [0, 1, 1]
    assert [v["readouts"]["original_bond_present"] for v in views] == [0, 1, 0]
    assert [v["readouts"]["lost_again_after_bond"] for v in views] == [0, 0, 1]


def test_noise_correction_is_unbiased_and_not_clipped():
    # Exhaust all two-sample Bernoulli outcomes, rather than a flaky random test.
    p, q, expected = 0.2, 0.7, 0.0
    for a, b, c, d in product((0, 1), repeat=4):
        weight = p**(a+b) * (1-p)**(2-a-b) * q**(c+d) * (1-q)**(2-c-d)
        expected += weight * squared_response([[a], [b]], [[c], [d]])
    assert np.isclose(expected, (p-q)**2)
    assert squared_response([[0], [1]], [[0], [1]]) < 0


def test_projection_counts_structure_not_particle_names():
    model = LatticeChemistry(Parameters(side=2, particles=4, capacity=4))
    state = square({(0, 1)})
    coords = probe_coordinates(model, state, (0, 1))
    result = model.simulate(state, 45, cuts=(0, 0.5))
    views = observe(model, result, (0, 1), coords, (0, 0.5))
    assert np.all(views[0]["cells"].sum(axis=1) == 1)
    assert views[0]["edges"].sum() == 1
