import itertools
import math
from dataclasses import replace

import numpy as np
import pytest
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply

from omega_v2.testbed import growing_population as legacy
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.modules.damage import events as damage_events
from omega_v2.testbed.modules.damage import module as damage_module
from omega_v2.testbed.modules.growth import build_world
from omega_v2.testbed.modules.material_sink import MaterialSink


def test_new_adapter_retains_the_two_consecutive_paid_assistance_route():
    world=build_world((3,1),policy=((1,0),(.75,.25))*2,
                      damage=MaterialSink(mode='absorbing',exposure=(0,1,0)))
    source=((0,1,0,2,0),(0,0,0,1,0));state=source
    for _ in range(2):
        event=next(e for module in world.modules for e in module.events(state)
                   if e.increments.get('gross_assisted_birth',0)>0)
        assert event.rate>0 and event.target[0][3]==state[0][3]-1
        state=event.target
    assert state[0][1]==3 and world.energy(state)==world.energy(source)
    with pytest.raises(RuntimeError):build_world((1000000,1),max_states=10)


def _damage_only_world(inventories, config):
    world = build_world(inventories, damage=config)
    return replace(world, modules=(damage_module(inventories, config),))


def _labeled_damage_reference(inventories, config):
    """Independent slot model: each material slot carries P/W/A/D directly."""
    local = [tuple((body, 0, 0) for body in itertools.product(range(4), repeat=m))
             for m in inventories]
    states = tuple(itertools.product(*local))
    index = {s: i for i, s in enumerate(states)}
    rows, cols, data = [], [], []
    for i, state in enumerate(states):
        total = 0.
        for c, (body, _f, _g) in enumerate(state):
            for slot, species in enumerate(body):
                if species < 3:
                    exposure = config.exposure[species]
                    if exposure:
                        changed = list(body); changed[slot] = 3
                        target = list(state); target[c] = (tuple(changed), 0, 0)
                        rate = config.rate * exposure
                        rows.append(i); cols.append(index[tuple(target)]); data.append(rate); total += rate
                elif config.mode == 'reversible':
                    for species, exposure in enumerate(config.exposure):
                        if not exposure: continue
                        energy = (0., 1., 2.)[species]
                        rate = config.rate*exposure*math.exp(config.energy-energy)
                        changed = list(body); changed[slot] = species
                        target = list(state); target[c] = (tuple(changed), 0, 0)
                        rows.append(i); cols.append(index[tuple(target)]); data.append(rate); total += rate
        rows.append(i); cols.append(i); data.append(-total)
    q = coo_matrix((data, (rows, cols)), shape=(len(states), len(states))).tocsr()
    # Project labeled categories to counts and the same five-coordinate codec.
    coarse = tuple((tuple((body.count(1), body.count(2), body.count(3), f, g)
                    for body, f, g in state)) for state in states)
    projected = tuple(dict.fromkeys(coarse)); pindex = {s: i for i, s in enumerate(projected)}
    r = coo_matrix((np.ones(len(states)), (np.arange(len(states)),
                    np.asarray([pindex[s] for s in coarse]))),
                   shape=(len(states), len(projected))).tocsr()
    return q, projected, r


def test_damage_module_lumps_from_independent_labeled_slot_generator():
    inv = (1, 1)
    config = MaterialSink(mode='reversible', rate=.17, energy=-.4,
                          exposure=(1., .35, .8))
    fine, projected, r = _labeled_damage_reference(inv, config)
    full = _damage_only_world(inv, config)
    coarse = compile_world(replace(full, states=projected))
    residual = fine @ r - r @ coarse['Q']
    assert np.max(np.abs(residual.data), initial=0.) < 1e-12


def test_uniform_absorbing_damage_has_analytic_all_material_loss_cdf():
    inv = (1, 1)
    lam, horizon = .23, 1.7
    config = MaterialSink(mode='absorbing', rate=lam, energy=-6., exposure=(1., 1., 1.))
    result = compile_world(_damage_only_world(inv, config))
    root = ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    start = np.zeros(len(result['states'])); start[result['index'][root]] = 1.
    endpoint = expm_multiply(result['Q'].T*horizon, start)
    full_loss = sum(p for state, p in zip(result['states'], endpoint)
                    if all(local[2] == m for local, m in zip(state, inv)))
    expected = (1-math.exp(-lam*horizon))**sum(inv)
    assert math.isclose(full_loss, expected, rel_tol=1e-12, abs_tol=1e-14)


def test_reversible_return_product_underflow_is_rejected():
    config = MaterialSink(mode='reversible', rate=1e-300, energy=-6.,
                          exposure=(1e-100, 0., 0.))
    state = ((0, 0, 1, 0, 0), (0, 0, 0, 0, 0))
    try:
        damage_events(state, (1, 1), config)
    except ArithmeticError as exc:
        assert 'underflow' in str(exc)
    else:
        raise AssertionError('positive reversible return law silently underflowed to zero')


def test_extended_adapter_reduces_to_legacy_growth_when_damage_is_disabled():
    policy = ((.25, .5), (.2, .4), (.6, .1), (.4, .3))
    for inv, token_bill in (((1, 1), 1), ((2, 1), 1), ((2, 1), 2)):
        params = replace(legacy.DEFAULT, switch_tokens=token_bill)
        new = compile_world(build_world(inv, policy=policy, params=params))
        old = legacy.build(inv, policy=policy, params=params)
        order = [old['index'][tuple((w, a, f, gate) for w, a, d, f, gate in state)]
                 for state in new['states']]
        assert np.max(np.abs((new['Q'] - old['Q'][order, :][:, order]).toarray()), initial=0.) < 1e-12
        for name, expected in old['flows'].items():
            actual = new['flows'].get(name, np.zeros(len(new['states'])))
            assert np.allclose(actual, expected[order], atol=1e-12, rtol=1e-12), name


def test_full_reversible_world_has_mu_zero_detailed_balance_and_energy_closure():
    params = replace(legacy.DEFAULT, chemical_potential=0.)
    config = MaterialSink(mode='reversible', rate=.04, energy=-2., exposure=(1., 1., 1.))
    result = compile_world(build_world((1, 1), policy=(1., 1., 1., 1.),
                                       params=params, damage=config))
    world = result['world']
    pi = np.asarray([world.degeneracy(s)*math.exp(-world.energy(s))
                     for s in result['states']], dtype=float)
    pi /= pi.sum()
    q = result['Q'].toarray()
    assert np.max(np.abs(pi[:, None]*q-(pi[:, None]*q).T)) < 1e-12
    assert np.max(np.abs(q @ result['energy'] - result['flows']['drive_work']
                          + result['flows']['bath_heat'])) < 1e-10
