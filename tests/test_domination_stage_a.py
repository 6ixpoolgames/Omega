from math import exp

import numpy as np
import pytest
from scipy.linalg import expm

from omega_v2.testbed.domination_friction import (
    FrictionParameters, FrictionPolicy, build_world, physical_energy)
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.analysis.friction_profile import (
    projected_rows, projection_bounds, two_observation_rows, two_observation_bounds)
from omega_v2.testbed.analysis.observed_history import exact_prefix_entropy, entropy_rows


def test_explicit_edges_and_all_mobility_steer_have_real_alternatives():
    p = FrictionPolicy(edges=((0, 1), (2, 3)))
    assert p.targets(0, 1) and p.targets(2, 3) and not p.targets(1, 0)
    world = build_world(policy=FrictionPolicy(mode='steering', direction='all', region=(0, 1, 2, 3)))
    state = (1, 0, 1, 2, 0, 1, 1, 1)
    events = [e for m in world.modules for e in m.events(state)]
    redirected = [e for e in events if e.family == 'friction.steer']
    assert redirected
    assert all(e.target[4] == state[4] and e.target[3] == 1 for e in redirected)
    assert all(e.target != state for e in events)


@pytest.mark.parametrize('shift', [-1., 1.])
def test_conservative_field_accounts_for_device_formation_and_dark_balance(shift):
    p = FrictionParameters(charge_capacity=1, drive=False, field_shift=shift, field_location=1)
    w = build_world(p, FrictionPolicy(phi=0))
    c = compile_world(w)
    weights = np.array([w.degeneracy(s)*exp(-p.beta*physical_energy(s, p)) for s in w.states])
    weights /= weights.sum()
    balance = c['Q'].multiply(weights[:, None])
    assert max(abs((balance-balance.T).data), default=0) < 1e-12
    assert max(abs(c['Q'] @ c['energy']-c['flows']['drive_work']+c['flows']['bath_heat'])) < 1e-11
    x = (0, 0, 0, 0, 1, 0, 0, 0)
    y = (*x[:7], 1)
    assert physical_energy(y, p)-physical_energy(x, p) == pytest.approx(1+shift)


@pytest.mark.parametrize('root', [0, 1, 2])
@pytest.mark.parametrize('steps', [1, 2, 4, 6])
def test_two_observation_bounds_enclose_exact_hidden_history_and_tighten(root, steps):
    q = np.array([[-.5, .2, .3], [.4, -.5, .1], [.2, .2, -.4]])
    P = expm(q*.7)
    groups, future, rows = projected_rows(P, [(0,), (1,), (1,)], (0,))
    start = np.eye(3)[root]
    occupation = np.zeros(3)
    for _ in range(steps):
        occupation += start
        start = start @ P
    previous = projection_bounds(groups, future, rows, occupation, float(occupation @ entropy_rows(P)))
    joint, conditional_rows = two_observation_rows(P, groups, future)
    before_last = occupation-np.linalg.matrix_power(P, steps-1)[root]
    tighter = two_observation_bounds(groups, joint, conditional_rows, before_last, rows[root], previous)
    exact = exact_prefix_entropy(P, [0, 1, 1], root, steps)
    assert previous['lower_bits']-1e-10 <= tighter['lower_bits'] <= exact+1e-10
    assert exact <= tighter['upper_bits']+1e-10 <= previous['upper_bits']+2e-10
