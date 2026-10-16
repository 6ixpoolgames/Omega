from dataclasses import replace
from math import comb, exp

import numpy as np
import pytest

from omega_v2.testbed.analysis.signal_readouts import occupation_integral
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.compounding import (
    CompoundingParameters,
    build_world,
    local_feedback_certificate,
    physical_readouts,
)


def events(world, state, family):
    return [event for module in world.modules for event in module.events(state) if event.family == family]


def test_damage_does_not_change_thermal_assembly_or_resource_process():
    p = CompoundingParameters(capacity=4)
    low, high = build_world(p), build_world(replace(p, damage_rate=.02))
    for state in low.states:
        for family in ('thermal_build', 'thermal_break', 'packet_inflow', 'packet_decay', 'paid_build', 'reverse_build'):
            assert events(low, state, family) == events(high, state, family)


def test_catalysis_preserves_pair_ratio_with_binomial_material_counting():
    p = CompoundingParameters(capacity=4)
    for mechanism in ('loop', 'no_construction_assistance'):
        world = build_world(p, mechanism)
        s, t = (8, 1, 1), (4, 1, 2)
        forward = events(world, s, 'paid_build')[0]
        reverse = events(world, t, 'reverse_build')[0]
        delta = world.energy(t)-world.energy(s)
        assert forward.target == t and reverse.target == s
        assert forward.rate/reverse.rate == pytest.approx(comb(4, 2)/comb(4, 1)*exp(-p.beta*delta))


def test_full_ledger_and_finite_bank_conservation():
    p = CompoundingParameters(capacity=4)
    c = compile_world(build_world(p))
    root = c['index'][(6, 1, 1)]
    final, weights = occupation_integral(c['Q'], root, 16)
    initial = np.zeros(len(final)); initial[root] = 1
    r = physical_readouts(c, final, weights, initial)
    assert abs(r['bank_balance_residual']) < 1e-8
    assert r['net_bath_import_excluding_packet_decay'] == pytest.approx(
        -r['bath_heat']+r.get('unused_packet_energy', 0.), abs=1e-8)
    assert np.max(np.abs(c['Q'] @ (c['observables']['apparatus']+c['observables']['precursor']))) < 1e-10
    assert c['energy'][root] == c['energy'][c['index'][(8, 1, 0)]]


def test_all_cost_coverage_has_stationary_budget_ceiling():
    from omega_v2.testbed.analysis.finite_classes import analyze
    c = compile_world(build_world(CompoundingParameters(capacity=2)))
    a = analyze(c['Q'], .25)
    pi = a['Pi'][0]
    r = physical_readouts(c, pi, pi, pi)
    assert r['capture_funding_fraction'] <= 1+1e-8
    assert r['capture_funding_fraction']+r['recycled_hardware_bank_fraction']+r['bath_bank_fraction'] == pytest.approx(1., abs=1e-8)


def test_descendants_really_increase_the_next_birth_propensity_before_crowding():
    p = CompoundingParameters(capacity=8)
    world = build_world(p)
    certificate = local_feedback_certificate(p)
    for a in (1, 2, 3):
        first = events(world, (8, 1, a), 'paid_build')[0].rate
        second = events(world, (8, 1, a+1), 'paid_build')[0].rate
        assert second-first == pytest.approx(certificate['construction_increments'][str(a)])
        assert second > first
    assert certificate['construction_increments']['6'] < 0


def test_ablations_keep_packets_and_basal_routes_physically_present():
    p = CompoundingParameters(capacity=4)
    loop, basal = build_world(p), build_world(p, 'basal')
    for state in loop.states:
        for family in ('packet_inflow', 'packet_decay', 'thermal_build', 'thermal_break', 'external_damage', 'bank_leak'):
            assert events(loop, state, family) == events(basal, state, family)
    assert events(basal, (8, 1, 0), 'paid_build')[0].rate > 0
    assert events(basal, (0, 1, 0), 'basal_capture')[0].rate > 0


def test_undriven_no_external_damage_control_obeys_full_detailed_balance():
    p = CompoundingParameters(capacity=4, supply_rate=0., damage_rate=0.)
    c = compile_world(build_world(p))
    keep = [i for i, s in enumerate(c['states']) if s[1] == 0]
    weights = np.array([comb(p.capacity, c['states'][i][2])*exp(-p.beta*c['energy'][i]) for i in keep])
    weights /= weights.sum()
    flux = weights[:, None]*c['Q'][keep][:, keep].toarray()
    assert np.max(np.abs(flux-flux.T)) < 1e-12


def test_exact_poisson_occupation_matches_direct_continuous_exponential():
    from scipy.linalg import expm, solve

    from omega_v2.testbed.analysis.finite_classes import analyze
    c = compile_world(build_world(CompoundingParameters(capacity=4)))
    root = c['index'][(6, 1, 1)]
    q = c['Q'].toarray()
    initial = np.zeros(len(q)); initial[root] = 1.
    pi = analyze(c['Q'], .25)['Pi'][root]
    final = initial @ expm(4*q)
    exact = 4*pi+solve((-q+np.ones((len(q), 1))*pi).T, initial-final)
    direct_final, direct = occupation_integral(c['Q'], root, 4.)
    assert np.allclose(final, direct_final, atol=1e-11)
    assert np.allclose(exact, direct, atol=1e-11)
