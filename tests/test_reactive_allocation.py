from dataclasses import replace
from math import exp
import numpy as np
import pytest
from scipy.linalg import expm

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.reactive_allocation import (
    MODES, AllocationParameters, AllocationPolicy, build_world, policies, root)
from omega_v2.testbed.analysis.friction_profile import (
    projected_rows, two_observation_rows, two_observation_bounds, projection_bounds)
from omega_v2.testbed.analysis.policy_search_profile import two_observation_summary


def test_controller_family_is_complete_and_includes_constants_and_adaptation():
    family = policies()
    assert len(family) == len({p.responses for p in family}) == 36
    assert all(AllocationPolicy((m, m)) in family for m in MODES)
    assert AllocationPolicy(('productive', 'extract')) in family
    assert AllocationPolicy(('hold', 'hold')) in family
    with pytest.raises(ValueError):
        build_world(policy=AllocationPolicy(('idle',)))


@pytest.mark.parametrize('responses', [('idle', 'idle'), ('productive', 'combined'), ('extract', 'donate')])
def test_all_native_channels_obey_dark_detailed_balance_and_energy(responses):
    p = AllocationParameters(drive=False)
    world = build_world(p, AllocationPolicy(responses))
    c = compile_world(world)
    weights = np.array([world.degeneracy(s)*exp(-p.beta*world.energy(s)) for s in world.states])
    weights /= weights.sum()
    flux = c['Q'].multiply(weights[:, None])
    assert max(abs((flux-flux.T).data), default=0.) < 1e-12
    assert max(abs(c['Q'] @ c['energy']-c['flows']['drive_work']+c['flows']['bath_heat'])) < 1e-12
    for sub in ('D', 'S'):
        net = sum(v for k, v in c['flows'].items() if k.startswith(sub+'_energy_by_family.'))
        assert max(abs(c['Q'] @ c['observables'][sub+'.owned_energy']-net)) < 1e-12


def test_commands_spend_real_energy_have_real_reverse_and_stop_without_apparatus():
    p = AllocationParameters()
    world = build_world(p, AllocationPolicy(('extract', 'productive')))
    s = (1, 1, 1, 2, 2, 0, 0)
    selector = next(m for m in world.modules if m.id == 'selector')
    command = next(e for e in selector.events(s) if e.increments.get('selector_forward'))
    assert command.target[3] == 1 and command.target[6] == MODES.index('extract')
    assert world.energy(command.target)-world.energy(s) == pytest.approx(-.5)
    reverse = next(e for e in selector.events(command.target) if e.target == s)
    assert reverse.increments['selector_reverse'] == 1
    dead = (1, 0, 1, 2, 2, 0, 0)
    assert {e.family for e in selector.events(dead)} == {'selector.relaxation'}


def test_no_implicit_idle_charger_assistance_or_free_hybrid_extra_capacity():
    world = build_world()
    pump = next(m for m in world.modules if m.id == 'funded-pump')
    rates = {}
    for name in ('idle', 'productive', 'extract', 'combined'):
        s = (1, 1, 1, 2, 2, 0, MODES.index(name))
        rates[name] = sum(e.rate for e in pump.events(s) if e.family == 'pump.charge')
    assert rates['productive'] == pytest.approx(rates['idle'])
    assert rates['combined']-rates['idle'] == pytest.approx((rates['extract']-rates['idle'])/2)
    assert root(world) == root(build_world(policy=AllocationPolicy(('extract', 'combined'))))


def test_fractional_bills_are_exact_and_state_cap_does_not_truncate():
    with pytest.raises(ValueError):
        AllocationParameters(switch_cost=.25)
    p = AllocationParameters(quantum=.25, switch_cost=.25)
    assert len(build_world(p).states) == 9720
    with pytest.raises(RuntimeError):
        build_world(p, max_states=9000)


def test_streamed_two_observation_query_matches_original_tensor_bounds():
    Q = np.array([[-.8, .4, .2, .2], [.3, -.9, .4, .2],
                  [.2, .2, -.7, .3], [.1, .2, .4, -.7]])
    P = expm(Q*.25)
    groups, future, single = projected_rows(P, [(0,), (0,), (1,), (1,)], (0,))
    joint, old_rows = two_observation_rows(P, groups, future)
    initial = np.array([1., 0., 0., 0.])
    occupation = initial+initial @ P+initial @ P @ P
    rows, upper = two_observation_summary(P, groups, future, {'test': occupation})
    assert np.allclose(rows, old_rows, atol=1e-12)
    previous = projection_bounds(groups, future, single, occupation+initial @ P @ P @ P, 100.)
    bounds = two_observation_bounds(groups, joint, old_rows, occupation, single[0], previous)
    assert max(previous['lower_bits'], single[0]+occupation @ rows) == pytest.approx(bounds['lower_bits'])
    assert min(previous['upper_bits'], single[0]+upper['test']) == pytest.approx(bounds['upper_bits'])


def test_bounds_enclose_direct_hidden_markov_history_enumeration():
    Q = np.array([[-.8, .4, .2, .2], [.3, -.9, .4, .2],
                  [.2, .2, -.7, .3], [.1, .2, .4, -.7]])
    P = expm(Q*.25)
    groups, future, single = projected_rows(P, [(0,), (0,), (1,), (1,)], (0,))
    paths = {((), 0): 1.}
    initial = np.array([1., 0., 0., 0.])
    current, occupation, before = initial.copy(), np.zeros(4), np.zeros(4)
    for step in range(5):
        occupation += current
        if step < 4:
            before += current
        current = current @ P
        nxt = {}
        for (word, hidden), probability in paths.items():
            for target in range(4):
                key = (word+(int(groups[target]),), target)
                nxt[key] = nxt.get(key, 0.)+probability*P[hidden, target]
        paths = nxt
    observed = {}
    for (word, _), probability in paths.items():
        observed[word] = observed.get(word, 0.)+probability
    exact = -sum(v*np.log2(v) for v in observed.values())
    previous = projection_bounds(groups, future, single, occupation, 100.)
    rows, upper = two_observation_summary(P, groups, future, {'test': before})
    lower = max(previous['lower_bits'], single[0]+before @ rows)
    high = min(previous['upper_bits'], single[0]+upper['test'])
    assert lower <= exact+1e-12 <= high+1e-12
