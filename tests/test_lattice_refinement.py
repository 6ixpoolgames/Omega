import json
from dataclasses import replace

import numpy as np

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State
from omega_v2.finite.lattice_compartment import (
    CompartmentChemistry,
    LocalEvent,
    LocalState,
    Reservoir,
)
from omega_v2.finite.lattice_history_atlas import (
    HistoryAtlas,
    event_from_record,
    prefix_probability,
    simulate_history,
    state_from_record,
)
from omega_v2.finite.lattice_transport_exact import (
    channel_balance_error,
    diagnostics,
    exact_generator,
    lift_matrix,
    next_two_chemical_bindings,
    propagate,
)


def square(p):
    return State([(0, 0), (1, 0), (0, 1), (1, 1)], [1]*4, {(0, 1)}, p.capacity)


def test_local_routes_equilibrium_and_conditional_averaging_with_unequal_volumes():
    p = Parameters(side=2, particles=4, capacity=2, catalytic_barrier=2)
    shared = exact_generator(LatticeChemistry(p), square(p))
    model = CompartmentChemistry(p, Reservoir(volumes=(.4, 1.6)))
    local = exact_generator(model, model.lift(square(p), np.random.default_rng(7)))
    assert channel_balance_error(local) < 2e-14
    assert diagnostics(local)["balance_error"] < 1e-13
    lift, project = lift_matrix(shared, local)
    assert np.max(np.abs(np.asarray(lift.sum(axis=0))-1)) < 1e-14
    assert np.max(np.abs(project@local["pi"]-shared["pi"])) < 1e-13
    averaged = project@local["q"].T@lift-shared["q"].T
    assert np.max(np.abs(averaged.data), initial=0) < 1e-13
    # Equality of the conditionally averaged instantaneous generator does NOT
    # assert exact lumpability at finite transport.
    defect = project@local["q"].T-shared["q"].T@project
    assert np.max(np.abs(defect.data)) > .01


def test_single_compartment_matches_native_shared_process_including_timed_query():
    p = Parameters(side=2, particles=4, capacity=1, catalytic_barrier=2)
    shared = exact_generator(LatticeChemistry(p), square(p))
    model = CompartmentChemistry(p, Reservoir(grid=(1, 1)))
    local = exact_generator(model, model.lift(square(p), np.random.default_rng(3)))
    lift, project = lift_matrix(shared, local)
    assert np.max(np.abs((project@local["q"].T@lift-shared["q"].T).data), initial=0) < 1e-13
    assert np.allclose(lift.T@next_two_chemical_bindings(local, 1),
                       next_two_chemical_bindings(shared, 1))
    assert np.max(next_two_chemical_bindings(local, 1)) < 1e-14


def test_fast_transport_converges_on_the_common_projected_law():
    p = Parameters(side=2, particles=4, capacity=1, catalytic_barrier=2)
    shared = exact_generator(LatticeChemistry(p), square(p))
    p0 = np.eye(1, len(shared["states"]), 0).ravel()
    target = propagate(shared["q"], p0, 1)
    errors = []
    for speed in (.1, 100):
        model = CompartmentChemistry(p, Reservoir(transport=speed))
        local = exact_generator(model, model.lift(square(p), np.random.default_rng(3)))
        lift, project = lift_matrix(shared, local)
        result = project@propagate(local["q"], lift@p0, 1)
        assert abs(result.sum()-1) < 1e-11
        errors.append(np.abs(result-target).sum()/2)
    assert errors[1] < .03*errors[0]


def test_mobility_changes_native_motion_but_not_equilibrium_on_mobile_patch():
    p = Parameters(side=2, particles=3, capacity=1)
    initial = State([(0, 0), (1, 0), (0, 1)], [1]*3, {(0, 1)}, 1)
    # Use an uncongested dimer separately; the 2x2 three-particle patch can block it.
    roomy = State([(0, 0), (1, 0), (2, 2)], [1]*3, {(0, 1)}, 1)
    slow = LatticeChemistry(replace(p, side=3))
    fast = LatticeChemistry(replace(p, side=3, mobility_exponent=.5))
    a = [e.rate for e in slow.events(roomy) if e.kind == "move" and len(e.members) == 2]
    b = [e.rate for e in fast.events(roomy) if e.kind == "move" and len(e.members) == 2]
    assert a and np.allclose(np.array(b)/a, np.sqrt(2))
    exacts = [exact_generator(LatticeChemistry(replace(p, mobility_exponent=g)), initial)
              for g in (1, .5)]
    assert np.allclose(exacts[0]["pi"], exacts[1]["pi"])
    assert all(diagnostics(e)["balance_error"] < 1e-13 for e in exacts)


def test_residual_cache_ignores_particle_names_but_keeps_physical_allocations():
    p = Parameters(side=2, particles=4, capacity=2, catalytic_barrier=2)
    model = CompartmentChemistry(p)
    s = model.lift(square(p), np.random.default_rng(8))
    atlas = HistoryAtlas(model)
    permutation = [2, 0, 3, 1]
    inverse = {old: new for new, old in enumerate(permutation)}
    renamed = LocalState([s.positions[i] for i in permutation], [s.internal[i] for i in permutation],
                         {tuple(sorted((inverse[i], inverse[j]))) for i, j in s.bonds},
                         s.fuels.copy(), s.wastes.copy())
    assert atlas.intern(s)[0] == atlas.intern(renamed)[0]
    s.fuels, renamed.fuels = [2, 0], [0, 2]
    assert atlas.intern(s)[0] != atlas.intern(renamed)[0]
    # The local allocation changes embedded channel rates despite equal total fuel.
    assert atlas.channels[atlas.intern(s)[0]] != atlas.channels[atlas.intern(renamed)[0]]


def test_reconvergent_prefixes_survive_residual_sharing_with_native_mass():
    p = Parameters(side=2, particles=2, capacity=1, diffusion=0,
                   thermal_binding=0, fuel_binding=0, exposed_energy=0)
    model = LatticeChemistry(p)
    initial = State([(0, 0), (1, 1)], [0, 0], set(), 1)
    atlas = HistoryAtlas(model)
    nodes = atlas.prefixes(initial, 2)
    assert len(nodes) == 7 and len(atlas.states) == 4
    second = [n for n in nodes if n["depth"] == 2]
    assert sum(n["residual"] == nodes[0]["residual"] for n in second) == 2
    assert np.isclose(sum(prefix_probability(n, 1) for n in second), 1-1.2*np.exp(-.2))
    assert np.isclose(sum(n["embedded_weight"] for n in second), 1)


def test_local_history_replay_and_prefix_clock_density():
    p = Parameters(side=4, particles=4, capacity=4, catalytic_barrier=2, mobility_exponent=.5)
    model = CompartmentChemistry(p, Reservoir(transport=3))
    initial = model.initial(21, "seeded")
    atlas = HistoryAtlas(model)
    result = simulate_history(atlas, initial, 42, cuts=(0, .1, 1))
    replay, time, log_density = initial.copy(), 0., 0.
    for i, row in enumerate(result["events"]):
        e = LocalEvent(**row["event"])
        total = sum(c.rate for c in model.events(replay))
        log_density += np.log(e.rate)-total*(row["time"]-time)
        assert all(parent < i for parent in row["parents"])
        model.apply(replay, e)
        model.validate(replay)
        time = row["time"]
    log_density -= sum(c.rate for c in model.events(replay))*(1-time)
    assert replay.record() == result["final"]
    assert np.isclose(log_density, result["snapshots"][-1]["log_path_density"])
    assert any(row["event"]["kind"] == "hop" for row in result["events"])
    restored = json.loads(json.dumps(result))
    replay = state_from_record(restored["initial"])
    for row in restored["events"]:
        model.apply(replay, event_from_record(row["event"]))
    assert replay.key() == state_from_record(restored["final"]).key()
