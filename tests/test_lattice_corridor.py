from itertools import combinations, product
from math import exp

import numpy as np

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State
from omega_v2.finite.lattice_damage import native_failure
from omega_v2.finite.lattice_equilibrium import collapsed_log_weight, sample_chain
from omega_v2.finite.lattice_history_profile import history_profile


def test_collapsed_equilibrium_matches_full_bond_fuel_enumeration():
    model = LatticeChemistry(Parameters(side=2, particles=3, capacity=2,
                                       bond_strength=1.3))
    sites = [(0, 0), (1, 0), (0, 1), (1, 1)]
    ratios = []
    for positions in combinations(sites, 3):
        for internal in product((0, 1), repeat=3):
            state = State(list(positions), list(internal), set(), 0)
            contacts = model.contacts(state, {p: i for i, p in enumerate(positions)})
            total = 0.0
            for flags, fuel in product(product((0, 1), repeat=len(contacts)), range(3)):
                state.bonds = {e for e, b in zip(contacts, flags, strict=True) if b}
                state.fuel = fuel
                total += exp(-model.free_energy(state))
            ratios.append(total/exp(collapsed_log_weight(model, state)))
    assert np.ptp(ratios) < 1e-12
    assert np.isclose(ratios[0], (1+exp(-model.p.fuel_energy))**model.p.capacity)


def test_equilibrium_sampler_tiny_moments_against_enumeration():
    model = LatticeChemistry(Parameters(side=2, particles=3, capacity=2,
                                       bond_strength=1.3))
    positions = [(0, 0), (1, 0), (0, 1)]
    weights, exposure = [], []
    for internal in product((0, 1), repeat=3):
        state = State(positions, list(internal), set(), 0)
        weights.append(exp(collapsed_log_weight(model, state)))
        exposure.append(sum(internal))
    expected = np.dot(weights, exposure)/sum(weights)
    samples = sample_chain(model, 31841, samples=1200, burn_sweeps=100, spacing=4)
    observed = np.array([sum(s["internal"]) for s in samples["states"]])
    assert abs(observed.mean()-expected) < 6*observed.std(ddof=1)/np.sqrt(len(observed))


def test_contribution_can_continue_after_original_template_loss():
    model = LatticeChemistry(Parameters(side=3, particles=6, capacity=6,
                                       catalytic_barrier=2))
    initial = State([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)],
                    [1]*6, {(0, 1)}, 6)
    state, logs = initial.copy(), []
    for time, kind, pair, cat in ((0.2, "catalytic", (2, 3), (0, 1)),
                                  (0.4, "thermal", (0, 1), ()),
                                  (0.6, "catalytic", (4, 5), (2, 3)),
                                  (0.8, "thermal", (2, 3), ())):
        event = next(e for e in model.events(state)
                     if e.kind == kind and e.members == pair and e.catalyst == cat)
        logs.append(event.record(time))
        model.apply(state, event)
    row = history_profile(model, {"initial": initial.record(), "events": logs}, (0, 1))[-1]
    assert row["productive_products"] == 1
    assert row["productive_products_later_lost"] == 1
    assert row["live_productive_products"] == 0
    assert row["ever_product_reused"] == 1
    assert row["new_material_pairs"] == 2


def test_template_failure_selection_preserves_total_rarity():
    model = LatticeChemistry(Parameters(side=3, particles=6, capacity=6,
                                       catalytic_barrier=2))
    state = State([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)],
                  [1, 1, 0, 1, 1, 1], {(0, 1), (0, 2)}, 6)
    failure = native_failure(model, state, 11, templates_only=True)
    assert failure["selected"].members == (0, 1)
    assert 0 < failure["total_hazard"] < failure["all_thermal_failure_hazard"]
    state.fuel = 0
    empty = native_failure(model, state, 11, templates_only=True)
    assert empty["selected"] is None
    assert empty["total_hazard"] == 0 < empty["all_thermal_failure_hazard"]
