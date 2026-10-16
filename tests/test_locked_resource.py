import math

import numpy as np

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.contracts import WorldSpec
from omega_v2.testbed.locked_resource import (
    STATES, BASE_BARRIER, BETA, build_world, describe, energy, make_root,
)


def test_world_conserves_finite_inventory_and_roots_match_energy():
    assert len(STATES) == describe()["states"] == 15
    for s in STATES:
        assert s[0] + s[1] <= 1
        assert s[2] + s[3] <= 2
    assert energy(make_root(True)) == energy(make_root(False))


def test_basal_rates_are_positive_and_thermodynamically_paired():
    world = build_world()
    by_source = {s: [e for e in world.modules[0].events(s) if e.family == "basal_release"]
                 for s in STATES}
    for s in STATES:
        basal = by_source[s]
        if s[1]:
            assert not basal
            continue
        assert len(basal) == 1
        e = basal[0]
        assert e.rate > 0
        reverse = next(x for x in by_source[e.target] if x.target == s)
        delta = energy(e.target) - energy(s)
        assert math.isclose(e.rate / reverse.rate, math.exp(-BETA * delta), rel_tol=1e-12)
        assert e.rate < 2 * BASE_BARRIER


def test_paid_release_requires_apparatus_and_has_fueled_reverse():
    world = build_world()
    events = {s: tuple(world.modules[0].events(s)) for s in STATES}
    for s in STATES:
        paid = [e for e in events[s] if e.family == "fuel_release"]
        if s[2] == 0:
            assert not paid
        for e in paid:
            assert e.target[0] != s[0]
            assert abs(e.increments["stored_fuel_energy_consumed"]) == 2
            reverse = next(x for x in events[e.target]
                           if x.family == e.family and x.target == s)
            assert math.isclose(e.rate / reverse.rate,
                                math.exp(-BETA * (energy(e.target) - energy(s))),
                                rel_tol=1e-12)


def test_compiler_energy_and_observable_ledgers_close():
    model = compile_world(build_world())
    q = model["Q"]
    assert np.max(np.abs(q @ model["energy"] - model["flows"]["drive_work"]
                         + model["flows"]["bath_heat"])) < 1e-10
    for name, values in model["observables"].items():
        assert np.max(np.abs(q @ values - model["flows"][f"net_{name}"])) < 1e-10
    assert np.max(np.abs(q @ model["observables"]["fuel_inventory_energy"]
                         + model["flows"]["stored_fuel_energy_consumed"])) < 1e-10
    assert not np.any(model["flows"]["drive_work"])
    assert "fuel_release" in model["families"]


def test_disabled_fixture_module_has_no_events():
    world = build_world()
    disabled = WorldSpec(world.id + "-disabled", world.version, world.states,
                         world.validate, world.energy, world.observables, (),
                         world.metadata)
    assert compile_world(disabled)["Q"].nnz == len(STATES)
