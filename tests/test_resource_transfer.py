from dataclasses import replace
from math import exp

import numpy as np
import pytest

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import FrictionParameters, d_bank
from omega_v2.testbed.resource_transfer import TransferPolicy, build_world, transfer_events


def parameters(**kwargs):
    return FrictionParameters(charge_capacity=1, d_energy_capacity=2,
                              d_energy_quantum=.5, **kwargs)


def test_default_adapter_has_a_compatible_fractional_grid():
    world = build_world()
    assert len(world.states) == 9984


@pytest.mark.parametrize('mode', ['passive', 'extract', 'cooperate', 'sham', 'ordinary'])
def test_all_controller_reactions_enabled_obey_dark_detailed_balance(mode):
    p = parameters(drive=False)
    w = build_world(p, TransferPolicy(mode=mode))
    c = compile_world(w)
    weights = np.array([w.degeneracy(s)*exp(-p.beta*w.energy(s)) for s in w.states])
    weights /= weights.sum()
    flux = c['Q'].multiply(weights[:, None])
    assert max(abs((flux-flux.T).data), default=0) < 1e-12
    assert max(abs(c['Q']@c['energy']-c['flows']['drive_work']+c['flows']['bath_heat'])) < 1e-12
    for subject in ('D', 'S'):
        accounted = sum(v for k, v in c['flows'].items() if k.startswith(subject+'_energy_by_family.'))
        assert max(abs(c['Q']@c['observables'][subject+'.owned_energy']-accounted)) < 1e-12


def test_extraction_has_real_income_bill_and_exact_reverse():
    p, policy = parameters(), TransferPolicy(mode='extract', cost=.5)
    # D has prepaid fuel; S has one resource unit. Same physical location.
    s = (1, 0, 1, 1, 0, 1, 1, 1)
    event = next(e for e in transfer_events(s, p, policy) if e.increments.get('extract_forward'))
    assert event.target == (1, 0, 1, 2, 0, 1, 0, 1)
    assert event.increments['transfer_D'] == .5
    assert event.increments['transfer_S'] == -1
    assert event.increments['extract_gross_bill'] == .5
    rev = next(e for e in transfer_events(event.target, p, policy)
               if e.increments.get('extract_reverse'))
    assert rev.target == s and rev.increments['extract_reverse_refund'] == .5


@pytest.mark.parametrize('missing', [2, 7])
def test_removing_hardware_removes_only_catalytic_boost(missing):
    p = parameters()
    s = list((1, 0, 1, 1, 0, 1, 1, 1)); s[missing] = 0; s = tuple(s)
    extract = list(transfer_events(s, p, TransferPolicy(mode='extract')))
    passive = list(transfer_events(s, p, TransferPolicy(mode='passive')))
    assert extract == passive and extract


def test_contact_prepayment_caps_and_stoichiometry():
    p, policy = parameters(), TransferPolicy(mode='extract')
    assert not list(transfer_events((1, 0, 1, 1, 1, 1, 1, 1), p, policy))
    w = build_world(p, policy)
    for s in w.states:
        for e in transfer_events(s, p, policy):
            w.validate(e.target)
            if e.increments.get('extract_forward'):
                assert s[3] >= d_bank(p).ticks(policy.cost)
            assert e.target[2] == s[2] and e.target[5] == s[5] and e.target[7] == s[7]
            assert set(e.support) <= {3, 6}
            assert w.energy(e.target)-w.energy(s) == pytest.approx(-policy.cost if
                any(e.increments.get(k) for k in ('extract_forward', 'cooperate_forward'))
                else policy.cost if any(e.increments.get(k) for k in ('extract_reverse', 'cooperate_reverse'))
                else -.5*(s[3]-e.target[3]))


def test_bad_grids_and_invalid_costs_fail_instead_of_rounding():
    with pytest.raises(ValueError): build_world(parameters(), TransferPolicy(cost=.3))
    with pytest.raises(ValueError): TransferPolicy(cost=0)
    with pytest.raises(ValueError): TransferPolicy(cost=-1)
    with pytest.raises(RuntimeError): build_world(parameters(), TransferPolicy(), max_states=100)
