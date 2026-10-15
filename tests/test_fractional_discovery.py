from fractions import Fraction
from dataclasses import replace
from math import exp

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.sparse import csr_matrix

from omega_v2.testbed.energy_grid import EnergyGrid
from omega_v2.testbed.domination_friction import (
    FrictionParameters, FrictionPolicy, build_world, d_bank, physical_energy, DISCOVERED, TRAP)
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.analysis.streamed_history import StreamedQueries, entropy_stream, entropy_stream_cadences
from omega_v2.testbed.analysis.observed_history import entropy_rows
from omega_v2.testbed.analysis.friction_attribution import activity_rows
from omega_v2.testbed.contracts import Event, RuleModule, WorldSpec


def test_fractional_energy_is_exact_internally_and_does_not_round_physical_bills():
    bank = EnergyGrid(3, Fraction(1, 10))
    assert bank.ticks(.3) == bank.ticks(.1+.2) == 3
    assert bank.energy(30) == 3
    assert bank.ticks(Fraction(1, 10)) == 1
    with pytest.raises(ValueError):
        bank.ticks(.15)
    with pytest.raises(ValueError):
        EnergyGrid(2.05, .1)


@pytest.mark.parametrize('discovery', [False, True])
@pytest.mark.parametrize('role', ['friction', 'ordinary'])
def test_fractional_native_dark_law_satisfies_detailed_balance(discovery, role):
    p = FrictionParameters(drive=False, charge_capacity=1, d_energy_capacity=2,
                          d_energy_quantum=.5, discovery=discovery, device_role=role)
    w = build_world(p, FrictionPolicy(phi=0), max_states=5000)
    c = compile_world(w)
    weights = np.array([w.degeneracy(s)*exp(-p.beta*w.energy(s)) for s in w.states])
    weights /= weights.sum()
    balance = c['Q'].multiply(weights[:, None])
    assert max(abs((balance-balance.T).data), default=0) < 1e-12
    assert max(abs(weights @ c['Q'])) < 1e-12


def test_fractional_bill_consumes_energy_without_changing_untargeted_subject():
    p = FrictionParameters(d_energy_capacity=3, d_energy_quantum=.1)
    w = build_world(p, FrictionPolicy(cost=.3), max_states=25000)
    s = (1, 0, 1, 10, 1, 1, 1, 1)
    interventions = [e for m in w.modules for e in m.events(s) if e.family == 'friction.block']
    assert interventions
    for e in interventions:
        assert e.target[3] == 7 and e.target[4:] == s[4:]
        assert w.energy(e.target)-w.energy(s) == pytest.approx(-.3)
        assert e.increments['friction_fuel'] == .3


def test_ordinary_material_is_productive_without_friction_capability():
    p = FrictionParameters(device_role='ordinary')
    state = (1, 0, 1, 1, 1, 1, 1, 1)
    ordinary = build_world(p, FrictionPolicy(phi=.95))
    idle = build_world(replace(p, device_role='friction'), FrictionPolicy(phi=0))
    a = [e for m in ordinary.modules for e in m.events(state)]
    b = [e for m in idle.modules for e in m.events(state)]
    assert not any(e.family.startswith('friction') for e in a)
    assert sum(e.rate for e in a if e.family == 'D.capture') > sum(e.rate for e in b if e.family == 'D.capture')
    assert ordinary.energy(state) == idle.energy(state)


def test_paid_discovery_is_physical_and_uses_energy_before_access():
    p = FrictionParameters(discovery=True, opportunity_yield=4)
    w = build_world(p, FrictionPolicy(phi=0))
    s = (1, 0, 1, 0, TRAP, 1, 1, 1)
    found = [e for m in w.modules for e in m.events(s) if e.family == 'S.discovery_paid']
    assert len(found) == 1
    assert found[0].target[4] == DISCOVERED and found[0].target[6] == 0
    assert found[0].increments['discovery_fuel'] == 1
    dest = found[0].target
    assert any(e.family == 'S.capture' for m in w.modules for e in m.events(dest))


def test_streaming_matches_exact_dense_entropy_and_finite_history():
    q = csr_matrix([[-.5, .2, .3], [.4, -.5, .1], [.2, .2, -.4]])
    P = expm(q.toarray()*.25)
    g, diagnostics = entropy_stream(q, .25, block_rows=2)
    assert g == pytest.approx(entropy_rows(P), abs=1e-13)
    solver = StreamedQueries(q)
    sampled = solver.sampled(.25, 2)
    total = np.zeros(3)
    for _ in range(32):
        total = g+P @ total
    assert solver.finite(sampled, 8) == pytest.approx(total, abs=1e-9)
    weights, _ = solver.sampled_occupation(0, 8, .25)
    direct = np.zeros(3)
    row = np.array([1., 0, 0])
    for _ in range(32):
        direct += row
        row = row @ P
    assert weights == pytest.approx(direct, abs=1e-9)
    assert diagnostics['full_kernel_stored'] is False
    together = entropy_stream_cadences(q, [.125, .25, .5], 2)
    for clock in together:
        assert together[clock][0] == pytest.approx(entropy_rows(expm(q.toarray()*clock)), abs=1e-13)


def test_activity_attribution_groups_shared_physical_destinations_before_labels():
    s = (0, 0, 0, 1, 0, 0, 0, 0)
    dest = (0, 0, 0, 0, 0, 0, 0, 0)
    def events(state):
        if state == s:
            yield Event('a', 'friction.block', dest, .2, (3,))
            yield Event('b', 'D.capture', dest, .3, (3,))
    world = WorldSpec('shared-outcome-test', '1', (s, dest), lambda x: None,
                      lambda x: x[3], {}, (RuleModule('events', '1', events),))
    rows = activity_rows(world)
    assert sum(r['jumps'][0] for r in rows.values()) == pytest.approx(.5)
    assert sum(r['finite_bits'][0] for r in rows.values()) == pytest.approx(.5*(np.log2(np.e)-np.log2(.5)))
    assert sum(r['mark_bits'][0] for r in rows.values()) == pytest.approx(0)


def test_sham_preserves_conditional_S_transitions_and_pays_real_bill():
    p = FrictionParameters()
    idle = build_world(p, FrictionPolicy(phi=0))
    sham = build_world(p, FrictionPolicy(mode='sham', phi=.95, cost=1))
    state = (1, 0, 1, 1, 1, 1, 1, 1)
    def S_rates(world):
        rates = {}
        for module in world.modules:
            for event in module.events(state):
                dest = event.target[4:7]
                if dest != state[4:7]:
                    rates[dest] = rates.get(dest, 0)+event.rate
        return rates
    assert S_rates(sham) == pytest.approx(S_rates(idle))
    bills = [event for module in sham.modules for event in module.events(state)
             if event.family == 'friction.sham']
    assert bills and all(e.target[3] == 0 and e.increments['friction_fuel'] == 1 for e in bills)


def test_discovery_can_be_inaccessible_to_capture_without_freezing_native_motion():
    p = FrictionParameters(discovery=True, opportunity_yield=0)
    world = build_world(p, FrictionPolicy(phi=0))
    state = (1, 0, 1, 1, DISCOVERED, 1, 1, 1)
    events = [e for module in world.modules for e in module.events(state)]
    assert any(e.family == 'S.discovery_basal' and e.target[4] == TRAP for e in events)
    assert not any(e.family == 'S.capture' and e.rate > 0 for e in events)


def test_expanded_profile_agrees_with_dense_original_on_same_physical_law():
    from omega_v2.testbed.analysis.expanded_friction_profile import profile as streamed
    from omega_v2.testbed.analysis.friction_profile import profile as dense
    from omega_v2.testbed.domination_friction import matched_roots
    p = FrictionParameters(charge_capacity=1)
    w = build_world(p, FrictionPolicy(phi=0))
    c = compile_world(w)
    roots = {'device_present': matched_roots(p)['device_present']}
    a = streamed(w, c, roots, [.25], [4])
    b = dense(c, roots, [.25], [4])
    aa, bb = (r['cadences']['0.25']['profiles']['device_present']['4'] for r in (a, b))
    assert aa['global_bits'] == pytest.approx(bb['global_bits'], abs=1e-7)
    for subject in ('D', 'S'):
        assert aa['subjects'][subject]['lower_bits'] == pytest.approx(bb['subjects'][subject]['lower_bits'], abs=1e-7)
        assert aa['subjects'][subject]['upper_bits'] == pytest.approx(bb['subjects'][subject]['upper_bits'], abs=1e-7)
    assert a['physical']['device_present']['4']['ledger'] == pytest.approx(b['physical']['device_present']['4']['ledger'], abs=1e-8)
