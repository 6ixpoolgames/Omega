import math
from collections import defaultdict
from math import comb

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.resource_feedback import (
    EMPTY,
    LOCKED,
    USABLE,
    WASTE,
    ResourceFeedbackParameters,
    build_resource_feedback_module,
    build_world,
)


def event_map(world):
    return {s: tuple(world.modules[0].events(s)) for s in world.states}


def test_parameters_do_not_mutate_through_input_containers_and_caps_refuse_truncation():
    parameters = ResourceFeedbackParameters()
    with pytest.raises(TypeError):
        parameters.rates['feedback'] = 0
    world = build_world(ResourceFeedbackParameters(apparatus_capacity=2, carrier_capacity=2))
    assert world.degeneracy((LOCKED, 1, 1)) == 4
    with pytest.raises(RuntimeError):
        build_world(max_states=10)


def test_same_law_basal_feedback_survives_without_catalyst_and_accelerates_both_directions():
    p = ResourceFeedbackParameters(feedback='basal_catalytic')
    world = build_world(p)
    def feedback(state):
        return next(e for e in world.modules[0].events(state) if e.family == 'resource_feedback')
    forward0 = feedback((USABLE, 0, 0))
    forward1 = feedback((USABLE, 1, 0))
    reverse0 = feedback((WASTE, 0, 1))
    reverse1 = feedback((WASTE, 1, 1))
    assert forward0.rate > 0 and reverse0.rate > 0
    boost = (p.feedback_basal+p.rates['feedback'])/p.feedback_basal
    assert forward1.rate/forward0.rate == pytest.approx(boost)
    assert reverse1.rate/reverse0.rate == pytest.approx(boost)
    assert forward1.rate/reverse1.rate == pytest.approx(forward0.rate/reverse0.rate)


def test_local_count_pools_energies_and_metadata_are_explicit():
    world = build_world()
    assert len(world.states) == 16
    assert world.energy((EMPTY, 0, 0)) == 0
    assert world.energy((LOCKED, 1, 0)) == 7
    assert world.energy((USABLE, 1, 1)) == 8
    assert world.energy((WASTE, 0, 1)) == 2
    assert world.observables["precursor"]((LOCKED, 0, 0)) == 1
    assert world.observables["spent_carrier"]((LOCKED, 0, 0)) == 1
    assert world.metadata["thermodynamics"]["external_carrier_drive"] is False
    assert world.metadata["inventory"]["apparatus_precursor"]["precursor"] == "capacity-a"
    module = build_resource_feedback_module()
    assert module.provides and callable(module.events)


def test_count_degeneracy_adjusted_reverse_ratios_for_all_internal_channels():
    p = ResourceFeedbackParameters(apparatus_capacity=2, carrier_capacity=2)
    world = build_world(p)
    events = event_map(world)
    degeneracy = lambda s: comb(2, s[1]) * comb(2, s[2])
    paired = {"basal_release", "downstream_thermal", "fueled_access",
              "resource_feedback", "construction", "wear", "carrier_thermal"}
    seen = set()
    for source, choices in events.items():
        for event in choices:
            if event.family not in paired:
                continue
            reverse = next(e for e in events[event.target]
                           if e.family == event.family and e.target == source)
            delta = world.energy(event.target) - world.energy(source)
            expected = math.exp(-p.beta * delta) * degeneracy(event.target) / degeneracy(source)
            assert math.isclose(event.rate / reverse.rate, expected, rel_tol=1e-12)
            seen.add(event.family)
    assert seen == paired


def test_boundary_work_is_exact_and_material_ledgers_are_typed():
    world = build_world()
    events = event_map(world)
    boundary = {"resource_inlet", "locked_export", "waste_export"}
    increments = defaultdict(set)
    for source, choices in events.items():
        for event in choices:
            if event.family in boundary:
                assert event.work == world.energy(event.target) - world.energy(source)
            for key in event.increments:
                increments[event.family].add(key)
    assert increments["resource_inlet"] == {"accepted_resource_input"}
    assert increments["resource_feedback"] == {
        "net_feedback_fuel", "gross_feedback_forward", "gross_feedback_reverse"}
    assert increments["construction"] == {
        "construction_forward", "construction_reverse", "construction_cost"}
    assert "access_fuel_cost" in increments["fueled_access"]
    assert not (boundary & {"carrier_thermal", "resource_feedback"})
    model = compile_world(world)
    assert np.max(np.abs(model["Q"] @ model["energy"] - model["flows"]["drive_work"]
                         + model["flows"]["bath_heat"])) < 1e-10


def test_feedback_options_have_matched_ablation_and_catalyst_modes():
    catalytic = build_world(ResourceFeedbackParameters(feedback="catalytic"))
    uncatalytic = build_world(ResourceFeedbackParameters(feedback="uncatalytic"))
    absent = build_world(ResourceFeedbackParameters(feedback="absent"))
    c_events, u_events, a_events = map(event_map, (catalytic, uncatalytic, absent))
    for state in catalytic.states:
        assert tuple(e for e in c_events[state] if e.family != "resource_feedback") == a_events[state]
        assert all(e.family != "resource_feedback" for e in a_events[state])
    # At a=1 on the default capacity, catalytic and uncatalytic prefactors agree.
    s = (USABLE, 1, 0)
    c = next(e for e in c_events[s] if e.family == "resource_feedback")
    u = next(e for e in u_events[s] if e.family == "resource_feedback")
    assert c.rate == u.rate
    # At a=0 the catalytic channel vanishes, while uncatalytic feedback remains.
    s0 = (USABLE, 0, 0)
    assert not any(e.family == "resource_feedback" for e in c_events[s0])
    assert any(e.family == "resource_feedback" for e in u_events[s0])
    # Ablation leaves all non-feedback event definitions byte-for-byte equal.
    assert compile_world(catalytic)["states"] == compile_world(absent)["states"]
    for state in catalytic.states:
        assert tuple(e for e in c_events[state] if e.family != "resource_feedback") == a_events[state]


def test_capacity_two_expands_state_space_and_compiles():
    world = build_world(ResourceFeedbackParameters(apparatus_capacity=2, carrier_capacity=2))
    assert len(world.states) == 36
    assert (LOCKED, 2, 2) in world.states
    model = compile_world(world)
    assert model["Q"].shape == (36, 36)
    assert model["observables"]["precursor"][world.states.index((LOCKED, 1, 0))] == 1
    assert model["observables"]["spent_carrier"][world.states.index((LOCKED, 1, 0))] == 2


@pytest.mark.parametrize("kwargs", [
    {"beta": 0}, {"apparatus_capacity": 0}, {"carrier_capacity": -1},
    {"feedback": "enabled"}, {"rates": {"wear": 0}},
])
def test_parameters_reject_invalid_scales_options_and_rates(kwargs):
    with pytest.raises(ValueError):
        ResourceFeedbackParameters(**kwargs)
