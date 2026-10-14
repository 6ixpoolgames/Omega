from dataclasses import replace
from math import comb, exp

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world, sample_events
from omega_v2.testbed.exploration import ExplorationParameters
from omega_v2.testbed.paid_sensing import SensorParameters
from omega_v2.testbed.renewal import RenewalParameters, build_world, physical_readouts


def test_resource_power_restarts_reservoir_without_recreating_memory_or_location():
    world = build_world()
    state = (0, 1, 0, 1, 1, 0, 1)
    harvest = next(m for m in world.modules if m.id == 'passive-transduction')
    event = next(ev for ev in harvest.events(state) if ev.family == 'assisted_capture')
    assert event.target == (3, 1, 0, 1, 0, 0, 1)
    assert event.work == 0
    assert world.energy(event.target)-world.energy(state) == -.5
    assert event.increments['assisted_captured_energy'] == 1.5
    for name in ('paid-sensor', 'renewal-mobility'):
        assert not list(next(m for m in world.modules if m.id == name).events(state))


def test_absent_hardware_leaves_only_basal_transduction_not_immortal_control():
    world = build_world()
    state = (8, 1, 1, 0, 1, 0, 0)
    assert not list(next(m for m in world.modules if m.id == 'paid-sensor').events(state))
    assert not list(next(m for m in world.modules if m.id == 'renewal-mobility').events(state))
    events = list(next(m for m in world.modules if m.id == 'passive-transduction').events(state))
    assert {ev.family for ev in events} == {'basal_capture'}
    assert events[0].rate > 0


def test_construction_pairs_preserve_energy_ratios_and_count_degeneracy():
    p = RenewalParameters(capacity=2)
    world = build_world(renewal=p)
    module = next(m for m in world.modules if m.id == 'apparatus-construction')
    for state in ((6, 1, 1, 0, 1, 0, 0), (3, 1, 1, 0, 0, 1, 1)):
        forward = next(ev for ev in module.events(state) if ev.family == 'paid_construction')
        reverse = next(ev for ev in module.events(forward.target) if ev.family == 'reverse_construction')
        assert reverse.target == state
        delta = world.energy(forward.target)-world.energy(state)
        expected = comb(2, forward.target[6])/comb(2, state[6])*exp(-p.beta*delta)
        assert forward.rate/reverse.rate == pytest.approx(expected)
    state = (6, 1, 0, 0, 1, 0, 1)
    fast = next(e for e in module.events(state) if e.family == 'paid_construction')
    slow_world = build_world(renewal=replace(p, autocatalytic_gain=0.))
    slow_module = next(m for m in slow_world.modules if m.id == 'apparatus-construction')
    slow = next(e for e in slow_module.events(state) if e.family == 'paid_construction')
    assert fast.rate == pytest.approx(3*slow.rate)


def test_repair_ablation_keeps_native_thermal_hardware_and_resources():
    world = build_world(renewal=RenewalParameters(repair_enabled=False))
    state = (8, 1, 0, 0, 1, 0, 0)
    events = [e for m in world.modules for e in m.events(state)]
    assert any(e.family == 'thermal_assembly' and e.rate > 0 for e in events)
    assert not any(e.family == 'paid_construction' for e in events)
    assert any(e.family == 'packet_decay' for e in events)


def test_compiler_energy_material_and_half_error_alias():
    sensor = SensorParameters(error=.5, noise_on=.5, noise_retain=.5)
    info = compile_world(build_world('I', sensor=sensor))
    noise = compile_world(build_world('R', sensor=sensor))
    assert len(info['states']) == 864
    assert np.array_equal(info['Q'].toarray(), noise['Q'].toarray())
    assert np.max(abs(info['Q'] @ info['energy']-info['flows']['drive_work']+info['flows']['bath_heat'])) < 1e-12
    assert np.all(info['observables']['apparatus']+info['observables']['precursor'] == 1)
    root = info['index'][(8, 1, 0, 1, 1, 0, 1)]
    readout = physical_readouts(info, root, 2.)
    assert readout['construction_bill'] > 0 and readout['hardware_gross_return_ratio'] > 0
    assert not readout['return_ratio_is_causal_or_net_loop_gain']
    assert readout['all_running_cost_coverage_ratio'] < readout['hardware_gross_return_ratio']


def test_background_same_and_powered_reads_are_identical_when_error_half():
    a = build_world('I', parameters=ExplorationParameters(coupling=4.))
    b = build_world('R', parameters=ExplorationParameters(coupling=4.))
    state = (8, 2, 1, 0, 0, 1, 1)
    for name in ('renewal-resources', 'renewal-mobility', 'apparatus-construction'):
        assert list(next(m for m in a.modules if m.id == name).events(state)) == list(next(m for m in b.modules if m.id == name).events(state))


def test_native_sampler_trace_stays_on_compiled_reachable_physics():
    world = build_world(renewal=RenewalParameters(capacity=2))
    compiled = compile_world(world)
    root = (8, 1, 0, 1, 1, 0, 1)
    final, trace = sample_events(world, root, 32., np.random.default_rng(741))
    state = root
    assert trace
    for _, event in trace:
        assert compiled['Q'][compiled['index'][state], compiled['index'][event.target]] > 0
        assert event in [e for module in world.modules for e in module.events(state)]
        state = event.target
    assert state == final
