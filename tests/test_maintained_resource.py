import math

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.maintained_resource import (
    BETA, ENERGY, EMPTY, LOCKED, RATES, STATES, USABLE, WASTE,
    build_world, energy, roots,
)


def test_bounded_material_and_energy_carrier_inventories_and_matched_roots():
    assert len(STATES) == 16
    for resource, apparatus, charged in STATES:
        assert resource in (EMPTY, LOCKED, USABLE, WASTE)
        assert apparatus + (1 - apparatus) == 1
        assert charged + (1 - charged) == 1
    r = roots()
    assert energy(r["organized"]) == energy(r["unorganized"])
    assert r["organized"] == r["matched_ablation"]


def test_isolated_thermal_channels_obey_paired_rate_law():
    world = build_world(paid_path=True)
    all_events = {s: tuple(world.modules[0].events(s)) for s in STATES}
    for s, events in all_events.items():
        for e in events:
            if e.family in {"resource_inlet", "locked_export", "waste_export",
                            "carrier_recharge", "carrier_export"}:
                continue
            reverse = next(x for x in all_events[e.target]
                           if x.family == e.family and x.target == s)
            delta = energy(e.target) - energy(s)
            assert math.isclose(e.rate / reverse.rate,
                                math.exp(-BETA * delta), rel_tol=1e-12)


def test_boundary_work_closes_and_noop_full_buffer_events_are_absent():
    world = build_world()
    for s in STATES:
        for e in world.modules[0].events(s):
            assert e.target != s
            if e.family in {"resource_inlet", "locked_export", "waste_export",
                            "carrier_recharge", "carrier_export"}:
                assert math.isclose(e.work, energy(e.target) - energy(s), abs_tol=1e-14)
    assert RATES["resource_inlet"] > 0 and RATES["carrier_recharge"] > 0
    assert ENERGY["charged_carrier"] > ENERGY["empty"]


def test_paid_path_requires_apparatus_and_charged_carrier():
    world = build_world()
    for s in STATES:
        paid = [e for e in world.modules[0].events(s) if e.family == "paid_release"]
        assert not paid or (s[0] in (LOCKED, USABLE) and s[1] == 1
                             and s[2] == (1 if s[0] == LOCKED else 0))
        for e in paid:
            reverse = next(x for x in world.modules[0].events(e.target)
                           if x.family == e.family and x.target == s)
            assert math.isclose(e.rate / reverse.rate,
                                math.exp(-BETA * (energy(e.target) - energy(s))),
                                rel_tol=1e-12)


def test_ablation_preserves_states_boundaries_and_apparatus_dynamics():
    capable, ablated = build_world(True), build_world(False)
    assert capable.states == ablated.states
    assert len(compile_world(capable)["Q"].data) >= len(compile_world(ablated)["Q"].data)
    for s in STATES:
        c = tuple(capable.modules[0].events(s)); a = tuple(ablated.modules[0].events(s))
        assert all(e.family != "paid_release" for e in a)
        # The full inaccessible-resource background stays native in both arms,
        # including basal release and downstream thermal return, not only ports.
        assert tuple(e for e in c if e.family != "paid_release") == a
        for family in {"resource_inlet", "locked_export", "waste_export",
                       "carrier_recharge", "carrier_export", "maintenance"}:
            ce = sorted((e.target, e.rate, e.work) for e in c if e.family == family)
            ae = sorted((e.target, e.rate, e.work) for e in a if e.family == family)
            assert ce == ae


def test_compiler_energy_and_observable_accounting_close():
    model = compile_world(build_world())
    q = model["Q"]
    assert np.max(np.abs(q @ model["energy"] - model["flows"]["drive_work"]
                         + model["flows"]["bath_heat"])) < 1e-10
    for name, values in model["observables"].items():
        assert np.max(np.abs(q @ values - model["flows"][f"net_{name}"])) < 1e-10
    assert np.any(model["flows"]["drive_work"] != 0)
    assert "paid_release" in model["families"]
    assert "paid_release" not in compile_world(build_world(False))["families"]
    adjacency = csr_matrix((model["Q"].toarray() > 0).astype(np.int8))
    nclasses, _ = connected_components(adjacency, directed=True, connection="strong")
    assert nclasses == 1
