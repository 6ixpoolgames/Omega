from collections import deque
from dataclasses import replace

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.controllers.reserve import (
    RESPONSES, ReservePolicy, candidate_family,
)
from omega_v2.testbed.modules.actuation import ActuationSpec
from omega_v2.testbed.modules.growth import build_world
from omega_v2.testbed import growing_population as legacy


def test_candidate_family_covers_threshold_surplus_and_worn_variants():
    family = candidate_family(3)
    ids = {p.id for p in family}
    assert len(family) == len(ids) == 22
    assert {p.surplus for p in family if p.id.startswith('reserve-')} == {
        'mix25', 'mix50', 'mix75', 'export'
    }
    for k in (2, 3):
        for surplus in ('mix25', 'mix50', 'mix75', 'export'):
            assert f'reserve-{k}-{surplus}' in ids
            assert f'reserve-{k}-{surplus}-worn-service' in ids


def test_reserve_threshold_response_uses_local_active_and_worn_counts_only():
    policy = ReservePolicy('probe', threshold=2, surplus='mix50', service_if_worn=True)
    # Changes in fuel, gate, damage do not alter a fixed (w,a) response.
    assert policy.response((0, 2, 0, 0, 0)) == policy.response((0, 2, 1, 3, 1))
    assert policy.response((1, 2, 0, 2, 1)) == RESPONSES['service']
    assert policy.response((0, 1, 0, 0, 0)) == RESPONSES['service']
    assert policy.response((0, 0, 0, 0, 1)) == RESPONSES['idle']


@pytest.mark.parametrize('kwargs', [
    {'observation': 'fuel'}, {'observation': 'gate'},
    {'observation': 'foreign-compartment'},
])
def test_unphysical_observation_channels_are_rejected(kwargs):
    with pytest.raises(ValueError, match='physical mechanism'):
        ReservePolicy('invalid', **kwargs)


def test_reserve_controller_requires_embodied_actuation():
    with pytest.raises(ValueError, match='embodied'):
        build_world((1, 1), ReservePolicy('reserve'))


@pytest.mark.parametrize('name', list(RESPONSES))
def test_constant_embodied_controller_embeds_old_active_table_exactly(name):
    """Old inactive entries are irrelevant because embodied a=0 cannot actuate."""
    response = RESPONSES[name]
    active_table = (response[0], response[1])
    old_table = ((.2, .3), active_table, (.8, .1), active_table)
    policy = ReservePolicy('constant-' + name, surplus=name)
    embodied = ActuationSpec(mode='embodied')
    states = [
        ((w, a, 0, f, gate), (0, 0, 0, 0, 0))
        for w in range(2) for a in range(3-w)
        for f in range(3) for gate in (0, 1)
    ]
    for state in states:
        old_events = legacy.events(
            tuple((w, a, f, gate) for w, a, d, f, gate in state),
            (2, 1), old_table,
        )
        old_switch = [e for e in old_events if e.family.startswith('switch_')]
        world = build_world((2, 1), policy, actuation=embodied)
        new_events = next(m.events(state) for m in world.modules if m.id == 'growth')
        new_switch = {(e.family, e.target, e.rate) for e in new_events
                      if e.family.startswith('switch_')}
        # Adapt legacy targets (w,a,f,g) into (w,a,d,f,g).
        embedded = set()
        old_state = tuple((w, a, f, gate) for w, a, d, f, gate in state)
        for event in old_switch:
            c = next(c for c in range(2) if event.target[c] != old_state[c])
            target = tuple((x[0], x[1], 0, x[2], x[3]) for x in event.target)
            rate = event.rate * state[c][1] / (2 if c == 0 else 1)
            if rate:
                embedded.add((event.family, target, rate))
        assert new_switch == embedded


def test_reserve_switch_pairs_preserve_thermal_detailed_balance_without_shocks():
    policy = ReservePolicy('reserve-2-mix50', threshold=2, surplus='mix50')
    params = replace(legacy.DEFAULT, chemical_potential=0.)
    world = build_world((2, 1), policy, params=params,
                        actuation=ActuationSpec(mode='embodied'))
    model = compile_world(world)
    states = model['states']
    weights = np.array([world.degeneracy(s) * np.exp(-world.energy(s)) for s in states])
    weights /= weights.sum()
    flux = model['Q'].multiply(weights[:, None])
    delta = flux - flux.T
    assert max(abs(delta.data), default=0.) < 1e-12
    shock_module = next(m for m in world.modules if m.id == 'shocks')
    assert all(not shock_module.events(s) for s in world.states)


def test_thresholds_differ_on_a_reachable_three_plus_one_state():
    low = ReservePolicy('k2', threshold=2, surplus='mix25')
    high = ReservePolicy('k3', threshold=3, surplus='mix25')
    world = build_world((3, 1), low, actuation=ActuationSpec(mode='embodied'))
    start = ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    target = ((0, 2, 0, 0, 0), (0, 0, 0, 0, 0))
    # Search the small native event graph for a construction path to target.
    queue, seen = deque([start]), {start}
    while queue and target not in seen:
        state = queue.popleft()
        for module in world.modules:
            for event in module.events(state):
                if event.target not in seen:
                    seen.add(event.target)
                    queue.append(event.target)
    assert target in seen
    low_world = world
    high_world = build_world((3, 1), high, actuation=ActuationSpec(mode='embodied'))
    get_growth = lambda w: next(m.events(target) for m in w.modules if m.id == 'growth')
    rates = lambda w: {(e.family, e.target, e.rate) for e in get_growth(w)
                       if e.family.startswith('switch_')}
    assert rates(low_world) != rates(high_world)
