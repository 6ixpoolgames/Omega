from dataclasses import replace
from itertools import product

import numpy as np

from omega_v2.finite.lattice_chemistry import (
    Event,
    LatticeChemistry,
    Parameters,
    State,
    balance_residual,
)


def test_all_tiny_states_have_thermodynamic_reverse_including_catalysts():
    # Exhaustive full 2x2 chemistry: both bond cycles and cooperative templates occur.
    model = LatticeChemistry(Parameters(side=2, particles=4, capacity=2, catalytic_barrier=2))
    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    worst = 0
    for states, bits, fuel in product(product((0, 1), repeat=4), range(16), range(3)):
        x = State(positions.copy(), list(states),
                  {e for b, e in enumerate(edges) if bits & (1 << b)}, fuel)
        worst = max(worst, balance_residual(model, x))
    assert worst < 1e-12


def test_movement_symmetry_and_replay_conserve_inventory():
    model = LatticeChemistry(Parameters(side=5, particles=8, capacity=8, catalytic_barrier=2))
    initial = model.initial(21, "seeded")
    result = model.simulate(initial, 42, cuts=(0, 0.3, 2))
    replay = initial.copy()
    for time, kind, members, direction, catalyst, rate in result["events"]:
        assert time < 2
        assert balance_residual(model, replay) < 1e-12
        model.apply(replay, Event(kind, members, rate, direction, catalyst))
        model.validate(replay)
    assert replay.key() == (tuple(result["final"]["positions"]),
                            tuple(result["final"]["internal"]),
                            tuple(result["final"]["bonds"]), result["final"]["fuel"])


def test_rotation_and_particle_names_preserve_transition_law():
    model = LatticeChemistry(Parameters(side=5, particles=8, capacity=8, catalytic_barrier=2))
    state = model.initial(11, "seeded")
    permutation = [5, 2, 7, 1, 0, 6, 3, 4]

    def transform(s):
        pos, internal = [None] * 8, [0] * 8
        for i, (x, y) in enumerate(s.positions):
            pos[permutation[i]], internal[permutation[i]] = (4 - y, x), s.internal[i]
        return State(pos, internal, {tuple(sorted((permutation[i], permutation[j])))
                                    for i, j in s.bonds}, s.fuel)

    def law(s, transform_targets=False):
        out = {}
        for e in model.events(s):
            after = s.copy()
            model.apply(after, e)
            key = (transform(after) if transform_targets else after).key()
            out[key] = out.get(key, 0) + e.rate
        return out

    a, b = law(state, True), law(transform(state))
    assert a.keys() == b.keys()
    assert all(np.isclose(a[k], b[k]) for k in a)


def test_catalysis_only_changes_kinetics_and_constant_fuel_density_scales_rates():
    p = Parameters(side=2, particles=4, capacity=4)
    plain, cat = LatticeChemistry(p), LatticeChemistry(replace(p, catalytic_barrier=2))
    s = plain.initial(1, "seeded")
    s.fuel = 2
    assert plain.free_energy(s) == cat.free_energy(s)
    assert all(e.kind != "catalytic" for e in plain.events(s))
    catalytic = [e for e in cat.events(s) if e.kind == "catalytic"]
    assert len(catalytic) == 1 and catalytic[0].members == (2, 3)
    larger = LatticeChemistry(replace(p, capacity=8))
    t = s.copy()
    t.fuel = 4
    a = [e.rate for e in plain.events(s) if e.kind == "fuel"]
    b = [e.rate for e in larger.events(t) if e.kind == "fuel"]
    assert a == b


def test_quiescent_paths_retain_all_requested_cuts():
    model = LatticeChemistry(Parameters(side=2, particles=1, capacity=1, diffusion=0,
                                       switching=0, thermal_binding=0, fuel_binding=0))
    result = model.simulate(model.initial(1), 2, cuts=(0, 1, 100))
    assert not result["events"]
    assert [s["time"] for s in result["snapshots"]] == [0, 1, 100]
    assert result["initial"] == result["final"]
