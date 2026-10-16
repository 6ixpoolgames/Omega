from dataclasses import replace

import numpy as np
import pytest

from omega_v2.testbed.aversive_signals import SignalParameters
from omega_v2.testbed.aversive_signals import build_world as old_world
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.signal_controls import build_world, calibrate, moments


@pytest.mark.parametrize('arm', ('A', 'B'))
def test_legacy_control_generators_remain_identical(arm):
    p = replace(SignalParameters(), escape_bias=.25, signal_upkeep=.02)
    new = compile_world(build_world(arm, p))
    old = compile_world(old_world(arm, p))
    assert new['states'] == old['states']
    assert np.array_equal(new['Q'].toarray(), old['Q'].toarray())


@pytest.mark.parametrize('arm', ('A0', 'B_R'))
def test_disconnecting_behaviour_does_not_remove_cost_or_enable_escape(arm):
    world = build_world(arm, on_rate=.04, off_rate=.3) if arm == 'B_R' else build_world(arm)
    off = [event for event in world.modules[0].events((6, 0, 0, 1, 1))
           if event.family.startswith(('escape_', 'forage_'))]
    on = [event for event in world.modules[0].events((6, 0, 1, 1, 1))
          if event.family.startswith(('escape_', 'forage_'))]
    assert [(event.family, event.rate) for event in off] == [(event.family, event.rate) for event in on]
    assert not any(event.family == 'escape_success' for event in off+on)
    assert any(event.family == 'signal_upkeep' for event in world.modules[0].events((6, 0, 1, 1, 1)))
    compiled = compile_world(world)
    assert np.max(abs(compiled['Q'] @ compiled['energy']-compiled['flows']['drive_work']
                      +compiled['flows']['bath_heat'])) < 1e-12


def test_independent_firing_is_not_conditioned_on_hazard():
    world = build_world('B_R', on_rate=.04, off_rate=.3)
    for hazard in (0, 1):
        events = [event for event in world.modules[0].events((6, 0, 0, hazard, 1))
                  if event.family == 'signal_on']
        assert len(events) == 1 and events[0].rate == .04
    dead = list(world.modules[0].events((0, 0, 0, 1, 1)))
    assert not any(event.family.startswith('signal_') for event in dead)


def test_switch_count_includes_physical_register_reset_at_death():
    p = replace(SignalParameters(), signal_hijack=.04, signal_off=.3)
    world = build_world('B_R', p, .04, .3)
    state = (1, 0, 1, 1, 1)
    assert any(event.target[0] == 0 and event.target[2] == 0
               for event in world.modules[0].events(state))
    c = compile_world(world)
    result = moments(c, c['index'][(6, 0, 0, 1, 1)], 4.)
    assert result['switch_count'] > 0 and result['charging_energy'] > 0


def test_matching_fits_physical_moments_without_entropy_or_perfect_charge_claim():
    p = replace(SignalParameters(), escape_bias=.25, signal_upkeep=.02, struggle_cost=.5)
    result = calibrate(p, (8, 0, 0, 1, 1), horizon=16.)
    assert result['success']
    assert result['maximum_relative_error'] <= 1e-6
    assert not result['fitted_using_lushness']
    assert not result['full_correlations_matched']
    with pytest.raises(ValueError):
        build_world('B_R')
