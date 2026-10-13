import math
from itertools import product

import numpy as np

from omega_v2.testbed.contracts import WorldSpec
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.compiler import sample_events
from omega_v2.testbed.modules.shocks import ShockSpec, events, module


def _moments(ev):
    return tuple(sum(e.rate * e.increments[name] for e in ev)
                 for name in ('shock_active_hits', 'shock_worn_hits'))


def test_shock_modes_match_conditional_first_moments_and_material_balance():
    state = ((2, 3, 1, 0, 0), (1, 2, 0, 0, 0))
    inv = (8, 5)
    h, p = .7, .2
    for mode in ('independent', 'correlated'):
        ev = events(state, inv, ShockSpec(True, mode, h, p), trapenergy=-4.)
        active, worn = _moments(ev)
        assert math.isclose(active, h * sum(x[1] for x in state))
        assert math.isclose(worn, h * sum(x[0] for x in state))
        for e in ev:
            before = sum(x[0] + x[1] + x[2] for x in state)
            after = sum(x[0] + x[1] + x[2] for x in e.target)
            assert before == after
            assert e.work == e.increments['shock_energy_transfer']
            assert e.increments.get('gross_built_loss', 0.) == e.increments['shock_worn_hits']


def test_correlated_binomial_shocks_have_finite_independent_limit():
    state = ((2, 3, 0, 0, 0), (1, 0, 0, 0, 0))
    inv = (6, 2)
    h = .6
    small = events(state, inv, ShockSpec(True, 'correlated', h, 1e-5))
    # Single-hit outcomes approach rates h per exposed molecule; joint and
    # multiple-hit outcomes vanish, so the total event intensity stays finite.
    assert math.isclose(sum(e.rate for e in small), h * 6, rel_tol=3e-5)
    assert all(math.isfinite(e.rate) for e in small)
    assert math.isclose(_moments(small)[0], h * 3, rel_tol=1e-12)
    assert math.isclose(_moments(small)[1], h * 3, rel_tol=1e-12)


def test_correlated_shock_is_single_common_event_across_compartments():
    state = ((0, 1, 0, 0, 0), (0, 1, 0, 0, 0))
    ev = events(state, (1, 1), ShockSpec(True, 'correlated', .8, 1.))
    assert len(ev) == 1
    assert ev[0].rate == .8
    assert ev[0].target == (((1, 0, 0, 0, 0)), ((1, 0, 0, 0, 0)))
    assert ev[0].support == (0, 1)

    state = ((0, 2, 0, 0, 0), (0, 2, 0, 0, 0))
    correlated = events(state, (2, 2), ShockSpec(True, 'correlated', .8, .5))
    independent = events(state, (2, 2), ShockSpec(True, 'independent', .8, .5))
    cross = lambda outcomes: sum(e.rate * e.increments['shock_active_hits'] ** 2
                                 for e in outcomes)
    # Squared total hits contain the positive cross-compartment term only
    # when both compartments share one shock arrival.
    assert cross(correlated) > cross(independent)


def test_compiled_shock_energy_ledger_has_zero_bath_heat():
    inv = (1, 1)
    local = [(w, a, d, 0, 0) for w, a, d in product(range(2), repeat=3)
             if w + a + d <= 1]
    states = tuple(product(local, repeat=2))
    spec = ShockSpec(True, 'correlated', .4, .35)

    def energy(state):
        return sum(w + 2*a - 3*d for w, a, d, _f, _g in state)

    world = WorldSpec('shock-ledger', '1', states, lambda s: None, energy, {},
                      (module(inv, spec, trapenergy=-3.),),
                      metadata={'fields': ('material-PWA-D',)})
    result = compile_world(world)
    assert np.max(np.abs(result['flows']['bath_heat'])) < 1e-12
    assert np.allclose(result['flows']['drive_work'],
                       result['flows']['shock_energy_transfer'])


def test_disabled_shocks_emit_no_events():
    state = ((1, 1, 0, 0, 0), (0, 0, 0, 0, 0))
    assert events(state, (2, 2), ShockSpec(), -6.) == ()
    assert module((2, 2), ShockSpec()).events(state) == ()


def test_shared_sampler_matches_exact_common_shock_endpoint_law():
    from scipy.linalg import expm
    local=[(w,a,d,0,0) for w,a,d in product(range(2),repeat=3) if w+a+d<=1]
    states=tuple(product(local,repeat=2));spec=ShockSpec(True,'correlated',.4,.5)
    energy=lambda state:sum(w+2*a-3*d for w,a,d,f,g in state)
    world=WorldSpec('shock-sampler','1',states,lambda s:None,energy,{},
                    (module((1,1),spec,-3),),metadata={'fields':('material-PWA-D',)})
    model=compile_world(world);root=((0,1,0,0,0),(0,1,0,0,0))
    expected=expm(model['Q'].toarray()*.7)[model['index'][root]]
    n=2000;rng=np.random.default_rng(261013);counts=np.zeros(len(states))
    for _ in range(n):
        target,_=sample_events(world,root,.7,rng);counts[model['index'][target]]+=1
    assert np.all(abs(counts-n*expected)<=6*np.sqrt(n*expected*(1-expected))+2)
