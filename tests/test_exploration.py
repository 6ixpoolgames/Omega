from dataclasses import replace

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world, sample_events
from omega_v2.testbed.exploration import ARMS, ExplorationParameters, build_world


def test_zero_coupling_is_exact_register_control_alias():
    p = ExplorationParameters(coupling=0.)
    reference = compile_world(build_world('B_R', parameters=p))
    for arm in ('B_X', 'M_C', 'S_A'):
        other = compile_world(build_world(arm, parameters=p))
        assert np.array_equal(reference['Q'].toarray(), other['Q'].toarray())


def test_physical_resource_dynamics_and_bills_remain_after_death():
    for arm in ARMS:
        world = build_world(arm)
        compiled = compile_world(world)
        assert len(compiled['states']) == 408
        assert np.max(abs(compiled['Q'] @ compiled['energy']-compiled['flows']['drive_work']
                          +compiled['flows']['bath_heat'])) < 1e-12
        for state in ((0, 0, 0, 1, 0, 1), (0, 2, 0, 0, 1, 0)):
            events = [ev for module in world.modules for ev in module.events(state)]
            assert {ev.family for ev in events} == {'packet_decay', 'packet_inflow', 'hazard_toggle'}
            assert all(ev.target[0] == 0 and ev.target[2] == 0 for ev in events)
            assert sum(ev.rate for ev in events) > 0


def test_food_transfer_depletes_stock_without_creating_external_work():
    world = build_world()
    state = (4, 1, 0, 0, 1, 0)
    events = [ev for module in world.modules for ev in module.events(state)]
    food = next(ev for ev in events if ev.family == 'forage_success')
    assert food.target == (7, 1, 0, 0, 0, 0)
    assert food.work == 0
    assert world.energy(food.target)-world.energy(state) == -.5
    move = next(ev for ev in events if ev.family == 'movement')
    assert move.target == (3, 2, 0, 0, 1, 0)
    assert move.increments['movement_bill'] == .5
    assert world.energy(move.target)-world.energy(state) == -.5


def test_coupling_changes_only_native_mobility_not_boundary():
    worlds = [build_world(a) for a in ARMS]
    for state in ((4, 1, 0, 1, 1, 0), (4, 2, 1, 0, 0, 1)):
        boundaries = [list(w.modules[0].events(state)) for w in worlds]
        assert all(ev == boundaries[0] for ev in boundaries)
    state = (4, 1, 1, 0, 0, 1)
    native = next(ev for ev in worlds[1].modules[2].events(state))
    coupled = next(ev for ev in worlds[2].modules[2].events(state))
    assert coupled.rate == 2*native.rate
    assert coupled.target == native.target and coupled.work == native.work


def test_sampler_uses_the_compiled_native_events_and_valid_parameters():
    world = build_world()
    final, events = sample_events(world, (8, 0, 0, 1, 1, 0), 4., np.random.default_rng(123))
    world.validate(final)
    state = (8, 0, 0, 1, 1, 0)
    for _, ev in events:
        assert ev in [e for module in world.modules for e in module.events(state)]
        state = ev.target
    with pytest.raises(ValueError):
        ExplorationParameters(contrast=1.)
    with pytest.raises(ValueError):
        build_world(parameters=replace(ExplorationParameters(), movement_cost=.3))
