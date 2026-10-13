from dataclasses import replace

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.modules.repair_hardware import RepairHardware, build_world


def native(world, state):
    return [event for module in world.modules for event in module.events(state)]


def test_faults_match_initial_impairment_and_hazard():
    state = ((0, 1, 0, 1, 0), (0, 1, 0, 1, 0), (1, 1))
    faults = []
    for mode in ("fast", "slow", "hardware_loss"):
        world = build_world(config=RepairHardware(mode=mode))
        faults.append([e for e in native(world, state) if e.family == "functional_fault"])
    assert all([e.rate for e in row] == [.02, .02] for row in faults)
    assert [[e.target[:2] for e in row] for row in faults].count(
        [e.target[:2] for e in faults[0]]) == 3
    assert faults[0][0].target[2] == (1, 1)
    assert faults[2][0].target[2] == (0, 1)


def test_slowing_preserves_both_repair_directions():
    config = RepairHardware(hazard=0)
    fast = build_world(config=config)
    slow = build_world(config=replace(config, mode="slow"))
    for state in fast.states:
        a = {e.target: e.rate for e in native(fast, state) if e.family == "repair"}
        b = {e.target: e.rate for e in native(slow, state) if e.family == "repair"}
        assert a.keys() == b.keys()
        for target, value in a.items():
            assert b[target] == pytest.approx(value * .1)


def test_hardware_loss_is_irreversible_but_not_total_recovery_loss():
    world = build_world(config=RepairHardware(mode="hardware_loss"))
    state = ((1, 0, 0, 1, 0), (0, 1, 0, 1, 0), (0, 1))
    events = native(world, state)
    assert not any(e.family == "repair" and 0 in e.support for e in events)
    assert any(e.family == "wear" and e.target[0][1] == 1 for e in events)
    for state in world.states:
        assert all(all(b <= a for a, b in zip(state[2], e.target[2]))
                   for e in native(world, state))


def test_compiler_closes_mass_energy_and_material_ledgers():
    for mode in ("fast", "slow", "hardware_loss"):
        compiled = compile_world(build_world(config=RepairHardware(mode=mode)))
        q = compiled["Q"]
        assert np.max(np.abs(q.sum(axis=1))) < 1e-12
        assert np.max(np.abs(q @ compiled["energy"] - compiled["flows"]["drive_work"]
                             + compiled["flows"]["bath_heat"])) < 1e-10
        for state in compiled["states"]:
            for event in native(compiled["world"], state):
                for before, after in zip(state[:2], event.target[:2]):
                    assert before[2] == after[2] == 0
                    assert sum(before[:2]) <= 1 and sum(after[:2]) <= 1


def test_invalid_parameters_and_state_cap():
    with pytest.raises(ValueError):
        RepairHardware(hazard=float("nan"))
    with pytest.raises(ValueError):
        RepairHardware(mode="unknown")
    with pytest.raises(RuntimeError):
        build_world(max_states=200)
