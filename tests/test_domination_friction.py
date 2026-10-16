from dataclasses import replace
from math import exp

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.sparse import csr_matrix

from omega_v2.testbed.analysis.friction_profile import (
    first_passage,
    projected_rows,
    projection_bounds,
    sampled_occupation,
)
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import (
    ACCESS,
    BUILD,
    TRAP,
    FrictionParameters,
    FrictionPolicy,
    build_world,
    energy,
    matched_roots,
)


def events(world, state):
    return [e for m in world.modules for e in m.events(state)]


@pytest.mark.parametrize('mode', ['blocking', 'steering'])
@pytest.mark.parametrize('missing', ['device', 'apparatus', 'charge'])
def test_friction_is_embodied_and_native_processes_survive(mode, missing):
    p = FrictionParameters()
    w = build_world(p, FrictionPolicy(mode=mode, cost=1))
    values = [1, ACCESS, 1, 1, BUILD, 1, 1, 1]
    values[{'device': 7, 'apparatus': 2, 'charge': 3}[missing]] = 0
    state = tuple(values)
    actual = events(w, state)
    idle = events(build_world(p, FrictionPolicy(phi=0)), state)
    assert not any(e.family.startswith('friction') for e in actual)
    assert {(e.target, e.family, e.rate) for e in actual} == {
        (e.target, e.family, e.rate) for e in idle}


@pytest.mark.parametrize('direction,loc', [('entry', BUILD), ('exit', TRAP)])
def test_steering_matches_local_S_exit_rate_and_debits_each_intervention(direction, loc):
    policy = FrictionPolicy(mode='steering', steering_scope='native_events', direction=direction,
                            region=(ACCESS,) if direction == 'entry' else (TRAP,), cost=1)
    p = FrictionParameters()
    state = (1, ACCESS, 1, 2, loc, 1, 1, 1)
    active = events(build_world(p, policy), state)
    idle = events(build_world(p, replace(policy, phi=0)), state)
    own = sum(e.rate for e in idle if e.family.startswith('S.'))
    changed = sum(e.rate for e in active if e.family.startswith(('S.', 'friction.')))
    assert changed == pytest.approx(own, abs=1e-12)
    for e in active:
        if e.family == 'friction.steer':
            assert e.target[3] == state[3]-1
            assert e.target[4:] != state[4:]
            assert e.increments['friction_fuel'] == 1


def test_blocked_attempts_have_real_cost_and_zero_cost_creates_no_self_events():
    s = (1, ACCESS, 1, 2, BUILD, 1, 1, 1)
    paid = events(build_world(policy=FrictionPolicy(cost=1)), s)
    blocked = [e for e in paid if e.family == 'friction.block']
    assert blocked
    assert all(e.target[4:] == s[4:] and e.target[3] == 1 for e in blocked)
    free = build_world(policy=FrictionPolicy(cost=0))
    assert not any(e.target == s for e in events(free, s))
    assert not any(e.family == 'friction.block' for e in events(free, s))
    assert free.observables['suppressed_rate'](s) > 0


@pytest.mark.parametrize('kappa', [0., 2.])
def test_dark_chemistry_obeys_canonical_detailed_balance_even_with_complementarity(kappa):
    p = FrictionParameters(charge_capacity=1, drive=False, kappa=kappa)
    w = build_world(p, FrictionPolicy(phi=0))
    c = compile_world(w)
    weights = np.array([w.degeneracy(s)*exp(-p.beta*energy(s)) for s in c['states']])
    weights /= weights.sum()
    balance = c['Q'].multiply(weights[:, None])
    defect = balance-balance.T
    assert max(abs(defect.data), default=0) < 1e-12
    assert max(abs(weights @ c['Q'])) < 1e-12


def test_energy_ledgers_and_redirected_functional_reactions_are_retained():
    c = compile_world(build_world(policy=FrictionPolicy(
        mode='steering', steering_scope='native_events', direction='exit', region=(TRAP,), cost=2)))
    assert max(abs(c['Q'] @ c['energy']-c['flows']['drive_work']
                   +c['flows']['bath_heat'])) < 1e-10
    s = (1, ACCESS, 1, 2, TRAP, 1, 1, 1)
    assert c['flows']['friction_fuel'][c['index'][s]] > 0
    s2 = (1, ACCESS, 1, 2, BUILD, 0, 1, 1)
    redirected = [e for e in events(c['world'], s2) if e.family == 'friction.steer'
                  and e.target[5] == 1]
    # Here no exits are targeted (trap-exit policy); no invented construction.
    assert not redirected


def test_background_is_identical_and_all_reference_material_remains_in_law():
    idle = build_world(policy=FrictionPolicy(phi=0))
    active = build_world(policy=FrictionPolicy(mode='steering'))
    bg = lambda w: next(m for m in w.modules if m.id == 'background')
    roots = matched_roots()
    assert {energy(s) for s in roots.values()} == {6.}
    for s in roots.values():
        idle.validate(s)
        assert list(bg(idle).events(s)) == list(bg(active).events(s))
    gas = roots['unassembled_preparation']
    assert any(e.target[2] > 0 for e in events(active, gas))
    assert any(e.target[7] > 0 for e in events(active, gas))
    assert len(idle.states) == len(active.states) == 2304


def test_policy_validation_cap_and_idle_aliases():
    with pytest.raises(ValueError):
        FrictionPolicy(edges=((0, 0),))
    with pytest.raises(ValueError):
        build_world(policy=FrictionPolicy(cost=3))
    with pytest.raises(RuntimeError):
        build_world(max_states=2303)
    a = compile_world(build_world(FrictionParameters(charge_capacity=1), FrictionPolicy(phi=0)))
    b = compile_world(build_world(FrictionParameters(charge_capacity=1),
                                 FrictionPolicy(mode='steering', steering_scope='native_events', region=(TRAP,), phi=0)))
    assert (a['Q']-b['Q']).nnz == 0


def test_sampled_subject_query_against_direct_history_and_occupations():
    q = csr_matrix([[-.5, .2, .3], [.4, -.5, .1], [.2, .2, -.4]])
    cadence = .25
    P = expm(q.toarray()*cadence)
    pi = np.linalg.solve(np.vstack([q.toarray().T[:2], np.ones(3)]), [0, 0, 1])
    weights, endpoint, residual = sampled_occupation(q, P, pi, 0, 12, cadence)
    actual = np.array([1., 0., 0.])
    total = np.zeros(3)
    for _ in range(12):
        total += actual
        actual = actual @ P
    assert weights == pytest.approx(total, abs=1e-10)
    assert endpoint == pytest.approx(actual, abs=1e-10)
    assert residual < 1e-10
    states = [(0,), (1,), (1,)]
    groups, future, rows = projected_rows(P, states, (0,))
    from omega_v2.testbed.analysis.observed_history import entropy_rows, exact_prefix_entropy
    bounds = projection_bounds(groups, future, rows, weights, float(weights @ entropy_rows(P)))
    exact = exact_prefix_entropy(P, [s[0] for s in states], 0, 12)
    assert bounds['lower_bits'] <= exact <= bounds['upper_bits']


def test_first_passage_retains_initial_target_mass():
    q = csr_matrix([[-.2, .2], [.1, -.1]])
    assert first_passage(q, np.array([0., 1.]), [False, True], 10) == pytest.approx(1.)
    assert first_passage(q, np.array([1., 0.]), [False, True], 10) == pytest.approx(1-exp(-2))
