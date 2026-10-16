from dataclasses import replace

import numpy as np
import pytest
from scipy.linalg import expm

from omega_v2.testbed.analysis.finite_classes import finite_history_bits
from omega_v2.testbed.analysis.observed_history import (
    exact_prefix_entropy,
    history_bounds,
    interval_comparison,
)
from omega_v2.testbed.analysis.signal_readouts import (
    coordinate_shares,
    occupation_integral,
    physical_readouts,
)
from omega_v2.testbed.aversive_signals import ARMS, SignalParameters, build_world
from omega_v2.testbed.compiler import compile_world


@pytest.mark.parametrize('arm', ARMS)
def test_all_arms_close_mass_energy_and_keep_environment_after_death(arm):
    compiled = compile_world(build_world(arm))
    q, flows = compiled['Q'], compiled['flows']
    assert np.max(abs(q.sum(axis=1))) < 1e-12
    assert np.max(abs(q @ compiled['energy']-flows['drive_work']+flows['bath_heat'])) < 1e-12
    dead = (0, 0, 0, 1, 1)
    events = [event for module in compiled['world'].modules for event in module.events(dead)]
    assert {x.family for x in events} == {'hazard_toggle', 'patch_thermal'}
    assert all(x.target[0] == 0 and x.target[1] == 0 for x in events)


def test_same_environment_exactly_matched_and_no_signal_action_labels():
    for state in build_world().states:
        references = []
        for arm in ARMS:
            events = tuple(build_world(arm).modules[0].events(state))
            references.append([(x.target, x.rate) for x in events
                               if x.family in {'hazard_toggle', 'patch_thermal'}])
            assert all(x.target != state for x in events)
        assert all(x == references[0] for x in references)


def test_blocked_escape_pays_bill_but_never_moves_and_signal_cost_is_physical():
    world = build_world('A')
    source = (6, 0, 1, 1, 1)
    attempts = [x for x in world.modules[0].events(source) if x.family.startswith('escape_')]
    assert len(attempts) == 1
    assert attempts[0].target[:2] == (4, 0)
    assert attempts[0].increments['struggle_bill'] == 1.
    charged = [x for x in world.modules[0].events((6, 0, 0, 1, 1))
               if x.increments.get('signal_activation')]
    assert len(charged) == 1
    assert charged[0].target[:3] == (4, 0, 1)
    assert charged[0].increments['signal_charge'] == .5


def test_hijack_is_independent_of_hazard_and_normal_signal_has_no_standalone_on():
    world = build_world('D')
    for loc, z in ((0, 0), (0, 1), (1, 0), (1, 1)):
        events = list(world.modules[0].events((6, loc, 0, z, 1)))
        on = [x for x in events if x.family == 'signal_on']
        assert len(on) == 1 and on[0].rate == .2
    assert not any(x.family == 'signal_on' for x in build_world('E').modules[0].events(
        (6, 0, 0, 1, 1)))


def test_quantized_bills_and_profitable_foraging_enforced():
    with pytest.raises(ValueError, match='quantum multiple'):
        replace(SignalParameters(), struggle_cost=.7)
    with pytest.raises(ValueError, match='exceed'):
        replace(SignalParameters(), food_yield=.5)
    for arm in ('B', 'N'):
        world = build_world(arm)
        off = {x.family: x.rate for x in world.modules[0].events((6, 0, 0, 1, 1))}
        on = {x.family: x.rate for x in world.modules[0].events((6, 0, 1, 1, 1))}
        assert off['escape_failure'] == on['escape_failure']


def test_hidden_observation_bounds_enclose_exact_nonmarkov_prefix():
    p = np.array([[.7, .2, .1], [.1, .4, .5], [.3, .2, .5]])
    labels = [0, 0, 1]
    bounds = history_bounds(p, labels, 0, 4)
    exact = exact_prefix_entropy(p, labels, 0, 4)
    assert bounds['lower_bits'] <= exact+1e-12 <= bounds['upper_bits']+1e-12
    full = history_bounds(p, [0, 1, 2], 0, 4)
    value = finite_history_bits(p, 4)[0]
    assert full['lower_bits'] == pytest.approx(value)
    assert full['upper_bits'] == pytest.approx(value)
    assert history_bounds(p, [0, 0, 0], 0, 4)['upper_bits'] == pytest.approx(0.)
    with pytest.raises(MemoryError):
        exact_prefix_entropy(p, labels, 0, 10, max_prefixes=2)


def test_overlapping_bounds_are_unresolved_not_a_tie():
    a = {'lower_bits': 1., 'upper_bits': 3.}
    assert interval_comparison(a, a, 1e-8)['verdict'] == 'unresolved'
    exact = {'lower_bits': 2., 'upper_bits': 2.}
    assert interval_comparison(exact, exact, 1e-8)['verdict'] == 'compression_within_tolerance'
    assert interval_comparison({'lower_bits': 4., 'upper_bits': 5.}, a, 1e-8)[
        'verdict'] == 'strict_positive'


def test_occupation_integral_matches_known_absorbing_solution():
    from scipy.sparse import csr_matrix
    q = csr_matrix([[-2., 2.], [0., 0.]])
    final, integral = occupation_integral(q, 0, 3.)
    assert final[0] == pytest.approx(np.exp(-6))
    assert integral[0] == pytest.approx((1-np.exp(-6))/2)
    assert integral.sum() == pytest.approx(3.)


def test_signal_readouts_and_chain_rule_shares_are_not_semantic_scores():
    compiled = compile_world(build_world('A'))
    ref = compile_world(build_world('B'))
    root = compiled['index'][(6, 0, 0, 1, 1)]
    stats = physical_readouts(compiled, ref, root, 1.)
    assert stats['obstructed_signal_time'] > 0
    assert stats['escape_disposition_shift'] == pytest.approx(.63)
    assert stats['tracking_external_hazard_mi_bits'] >= 0
    assert stats['qualification'].startswith('unscored')
    kernel = expm(compiled['Q'].toarray()*.25)
    shares = coordinate_shares(kernel, compiled['states'], root, 4)
    assert sum(shares['bits']) == pytest.approx(finite_history_bits(kernel, 4)[root])
    assert min(shares['bits']) > -1e-10
    with pytest.raises(ValueError, match='disable'):
        physical_readouts(compiled, compiled, root, 1.)
