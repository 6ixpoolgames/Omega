import math

import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.controlled_feedback import (
    ControlledFeedbackController,
    ControlledFeedbackParameters,
    build_world,
)
from omega_v2.testbed.resource_feedback import ResourceFeedbackParameters


def make_world(responses=((0.0, 0.0), (0.5, 0.5))):
    rates = dict(ResourceFeedbackParameters().rates)
    rates["feedback"] = 0.04
    base = ResourceFeedbackParameters(
        feedback="basal_catalytic",
        feedback_basal=0.002,
        rates=rates,
        apparatus_capacity=1,
        carrier_capacity=2,
    )
    controller = ControlledFeedbackController("fixed-observation-policy", responses)
    return build_world(ControlledFeedbackParameters(base, controller))


def test_actuation_support_declares_embodied_read_and_disallows_hidden_observations():
    world = make_world()
    for state in world.states:
        for module in world.modules:
            for e in module.events(state):
                if e.family.startswith('actuation_'):
                    assert {1,2,3} <= set(e.support)
    with pytest.raises(ValueError, match='physical sensing'):
        ControlledFeedbackController('invalid', ((0.,0.),(1.,0.)), observation='full world')


def event(world, state, family, target=None):
    found = [
        e
        for e in world.modules[0].events(state)
        if e.family == family and (target is None or e.target == target)
    ]
    assert len(found) == 1
    return found[0]


def test_zero_response_leaves_only_basal_gate_dynamics_and_no_command_cost():
    world = make_world(((0.0, 0.0), (0.0, 0.0)))
    events = tuple(world.modules[0].events((2, 1, 1, 0)))
    assert {e.family for e in events} >= {"resource_feedback", "gate_relaxation"}
    assert not {"actuation_use", "actuation_service"} & {e.family for e in events}
    feedback = event(world, (2, 1, 1, 0), "resource_feedback", (3, 1, 2, 0))
    assert feedback.rate == pytest.approx(0.002 * 1 * math.exp(1.0))
    assert event(world, (2, 1, 1, 0), "gate_relaxation").rate == pytest.approx(0.003)


def test_no_apparatus_has_basal_catalysis_and_suppresses_actuation():
    world = make_world(((1.0, 0.0), (0.0, 0.0)))
    state = (2, 0, 1, 1)
    events = tuple(world.modules[0].events(state))
    assert not {"actuation_use", "actuation_service"} & {e.family for e in events}
    feedback = event(world, state, "resource_feedback", (3, 0, 2, 1))
    assert feedback.rate == pytest.approx(0.002 * math.exp(1.0))


def test_command_pairs_have_correct_energy_count_factors_and_fixed_observation():
    world = make_world(((0.0, 0.0), (0.0, 1.0)))
    source = (2, 1, 1, 0)
    forward = event(world, source, "actuation_use", (2, 1, 0, 1))
    reverse = event(world, (2, 1, 0, 1), "actuation_use", source)
    assert forward.rate == pytest.approx(0.015 * 1 / 1 * 1 * math.exp(1.0))
    assert reverse.rate == pytest.approx(0.015 * 1 / 1 * 2 * math.exp(-1.0))
    assert forward.increments["net_actuation_fuel"] == 1
    assert reverse.increments["net_actuation_fuel"] == -1
    assert forward.increments["gross_actuation_fuel"] == 1
    assert reverse.increments["gross_actuation_fuel"] == 0
    assert reverse.increments["gross_actuation_return"] == 1
    # Changing gate and carrier occupancy cannot change the controller's response;
    # after removing the explicit pool-count and energy factors, the coefficient is fixed.
    src2 = (2, 1, 2, 0)
    f2 = event(world, src2, "actuation_use", (2, 1, 1, 1))
    norm1 = forward.rate / (1 * math.exp(1.0))
    norm2 = f2.rate / (2 * math.exp(1.0))
    assert norm1 == pytest.approx(norm2)


def test_native_generator_and_accounting_close_and_thermal_families_ignore_gate():
    world = make_world()
    compiled = compile_world(world)
    q, flows = compiled["Q"], compiled["flows"]
    assert max(abs(q.sum(axis=1).A.ravel())) < 1e-10
    assert max(abs(q @ compiled["energy"] - flows["drive_work"] + flows["bath_heat"])) < 1e-9
    assert "switches" in flows and "gross_actuation_fuel" in flows and "net_actuation_fuel" in flows
    for resource, apparatus, charged in ((0, 1, 1), (1, 1, 1), (2, 1, 1), (3, 1, 1)):
        e0 = {
            (e.family, e.target[:3]): e.rate
            for e in world.modules[0].events((resource, apparatus, charged, 0))
            if e.family in {"downstream_thermal", "basal_release", "carrier_thermal", "wear"}
        }
        e1 = {
            (e.family, e.target[:3]): e.rate
            for e in world.modules[0].events((resource, apparatus, charged, 1))
            if e.family in {"downstream_thermal", "basal_release", "carrier_thermal", "wear"}
        }
        assert e0 == pytest.approx(e1)
    assert "external_controlled_oracles" in world.metadata
    assert world.metadata["external_controlled_oracles"] is False


def test_state_validation_rejects_nonboolean_gate_encoding():
    world = make_world()
    with pytest.raises(ValueError):
        world.validate((0, 0, 0, True))
    with pytest.raises(ValueError):
        world.validate((0, 0, 0, 2))


def test_disabled_catalysis_keeps_paired_basal_feedback_and_energy_balance():
    rates = dict(ResourceFeedbackParameters().rates)
    base = ResourceFeedbackParameters(
        feedback="basal_catalytic",
        feedback_basal=0.002,
        catalysis_enabled=False,
        rates=rates,
        apparatus_capacity=1,
        carrier_capacity=2,
    )
    controller = ControlledFeedbackController("basal-only", ((0.0, 0.0), (0.0, 0.0)))
    world = build_world(ControlledFeedbackParameters(base, controller))
    for gate in (0, 1):
        forward = event(world, (2, 1, 1, gate), "resource_feedback", (3, 1, 2, gate))
        reverse = event(world, (3, 1, 2, gate), "resource_feedback", (2, 1, 1, gate))
        assert forward.rate == pytest.approx(0.002 * math.exp(1.0))
        assert reverse.rate == pytest.approx(0.002 * 2 * math.exp(-1.0))
    compiled = compile_world(world)
    assert (
        max(
            abs(
                compiled["Q"] @ compiled["energy"]
                - compiled["flows"]["drive_work"]
                + compiled["flows"]["bath_heat"]
            )
        )
        < 1e-9
    )
