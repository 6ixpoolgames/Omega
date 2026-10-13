import math
from dataclasses import replace

import numpy as np

from omega_v2.testbed import growing_population as legacy
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.modules.actuation import ActuationSpec
from omega_v2.testbed.modules.growth import build_world
from omega_v2.testbed.modules.material_sink import MaterialSink


def _events(world, state):
    return [e for module in world.modules for e in module.events(state)]


def test_legacy_actuation_default_is_exact_legacy_growth():
    policy = ((.25, .5), (.2, .4), (.6, .1), (.4, .3))
    world = compile_world(build_world((1, 1), policy=policy))
    old = legacy.build((1, 1), policy=policy)
    order = [old['index'][tuple((w, a, f, gate) for w, a, d, f, gate in state)]
             for state in world['states']]
    assert np.array_equal(world['Q'].toarray(), old['Q'][order, :][:, order].toarray())


def test_embodied_zero_and_full_active_commanded_gate_rates():
    policy = (1., 1., 1., 1.)
    legacy_world = build_world((1, 1), policy=policy)
    embodied = build_world((1, 1), policy=policy,
                           actuation=ActuationSpec('embodied'))
    no_active = ((0, 0, 0, 1, 0), (0, 0, 0, 0, 0))
    assert not [e for e in _events(embodied, no_active) if e.family.startswith('switch')]
    full = ((0, 1, 0, 1, 0), (0, 0, 0, 0, 0))
    commanded = lambda w: [e for e in _events(w, full) if e.family.startswith('switch')]
    by_target_old = {e.target: e.rate for e in commanded(legacy_world)}
    by_target_new = {e.target: e.rate for e in commanded(embodied)}
    assert by_target_new == by_target_old


def test_basal_flips_are_symmetric_policy_free_and_do_not_change_fuel():
    state = ((0, 0, 0, 1, 0), (0, 0, 0, 0, 1))
    spec = ActuationSpec('legacy', basal_rate=.003)
    worlds = [build_world((1, 1), policy=p, actuation=spec)
              for p in ((0.,)*4, (1.,)*4)]
    relaxation = [[e for e in _events(w, state) if e.family == 'gate_relaxation']
                  for w in worlds]
    assert len(relaxation[0]) == len(relaxation[1]) == 2
    assert [(e.target, e.rate, e.work) for e in relaxation[0]] == [
        (e.target, e.rate, e.work) for e in relaxation[1]]
    assert all(e.rate == .003 and e.work == 0 for e in relaxation[0])
    assert all(sum(x[3] for x in e.target) == sum(x[3] for x in state)
               for e in relaxation[0])


def test_embodied_switch_scaling_preserves_each_forward_reverse_ratio():
    policy = (.5, .5, .5, .5)
    params = replace(legacy.DEFAULT, switch_tokens=1)
    old = build_world((1, 1), policy=policy, params=params)
    new = build_world((1, 1), policy=policy, params=params,
                      actuation=ActuationSpec('embodied'))
    # A gate-open/closed pair with one active unit has the same factor in both states.
    closed = ((0, 1, 0, 1, 0), (0, 0, 0, 0, 0))
    opened = ((0, 1, 0, 0, 1), (0, 0, 0, 0, 0))
    old_forward = next(e.rate for e in _events(old, closed)
                       if e.family.startswith('switch') and e.target == opened)
    old_reverse = next(e.rate for e in _events(old, opened)
                       if e.family.startswith('switch') and e.target == closed)
    new_forward = next(e.rate for e in _events(new, closed)
                       if e.family.startswith('switch') and e.target == opened)
    new_reverse = next(e.rate for e in _events(new, opened)
                       if e.family.startswith('switch') and e.target == closed)
    assert math.isclose(new_forward / new_reverse, old_forward / old_reverse)
    assert math.isclose(new_forward, old_forward)


def test_all_damaged_embodied_kernel_is_policy_independent_with_basal_relaxation():
    damage = MaterialSink(mode='absorbing', exposure=(0., 0., 0.))
    policies = ((0.,)*4, (1.,)*4, (.2, .8, .4, .6))
    compiled = [compile_world(build_world((1, 1), policy=p, damage=damage,
                                          actuation=ActuationSpec('embodied', .003)))
                for p in policies]
    rows = [i for i, state in enumerate(compiled[0]['states'])
            if all(local[2] == 1 for local in state)]
    for result in compiled[1:]:
        for i in rows:
            assert np.array_equal(compiled[0]['Q'].getrow(i).toarray(),
                                  result['Q'].getrow(i).toarray())
    assert 'gate_relaxation' in compiled[0]['families']
