from dataclasses import replace

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.exploration import build_world as legacy_world
from omega_v2.testbed.paid_sensing import SensorParameters, build_world, cue, readouts


def test_paid_sensor_resolves_information_vs_noise_without_changing_motor_or_resource():
    info, noise = build_world('I'), build_world('R')
    assert info.states == noise.states == legacy_world().states
    for state in ((8, 1, 0, 1, 0, 1), (8, 1, 0, 1, 1, 0)):
        for name in ('resource-patches', 'costed-mobility'):
            a = next(m for m in info.modules if m.id == name)
            b = next(m for m in noise.modules if m.id == name)
            assert list(a.events(state)) == list(b.events(state))
        outputs = []
        for world in (info, noise):
            events = list(next(m for m in world.modules if m.id == 'paid-sensor').events(state))
            assert sum(e.rate for e in events) == pytest.approx(.2)
            assert all(e.increments['sensor_bill'] == .5 for e in events)
            outputs.append(sum(e.rate for e in events if e.target[2] == 1)/.2)
        assert outputs[0] == pytest.approx(.9 if cue(state) else .1)
        assert outputs[1] == pytest.approx(.2)


def test_uninformative_sensor_is_exact_alias_at_half_error():
    sensor = SensorParameters(error=.5, noise_on=.5, noise_retain=.5)
    info = compile_world(build_world('I', sensor=sensor))
    noise = compile_world(build_world('R', sensor=sensor))
    assert np.array_equal(info['Q'].toarray(), noise['Q'].toarray())


def test_reading_same_value_still_pays_and_low_energy_cannot_make_free_bit():
    sensor = next(m for m in build_world('I').modules if m.id == 'paid-sensor')
    events = list(sensor.events((2, 1, 0, 0, 0, 1)))
    assert all(e.target == (1, 1, 0, 0, 0, 1) for e in events)
    assert all(e.increments['signal_charge'] == 0 for e in events)
    assert any(e.increments['register_write_failure'] == 1 for e in events)
    for event in sensor.events((8, 1, 1, 0, 0, 1)):
        assert event.target[0] == 7
        assert event.increments['sensor_bill'] == .5
    assert list(sensor.events((0, 1, 0, 0, 0, 1))) == []


def test_energy_ledger_and_conditional_information_are_physical():
    for mode in ('I', 'R'):
        compiled = compile_world(build_world(mode))
        root = compiled['index'][(8, 1, 0, 1, 0, 1)]
        result = readouts(compiled, root, 4.)
        assert result['sensor_bill'] > 0 and result['register_activation'] > 0
        assert np.max(abs(compiled['Q'] @ compiled['energy']-compiled['flows']['drive_work']
                          +compiled['flows']['bath_heat'])) < 1e-12
        if mode == 'R':
            assert abs(result['conditional_sensor_write_information_bits']) < 1e-12
        else:
            assert result['conditional_sensor_write_information_bits'] > .001
    with pytest.raises(ValueError):
        build_world(sensor=replace(SensorParameters(), read_cost=.3))
