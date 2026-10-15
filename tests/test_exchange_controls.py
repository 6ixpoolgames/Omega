from dataclasses import replace
from math import exp
import numpy as np
import pytest
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import (
    FrictionParameters, FrictionPolicy, _mobility, matched_roots)
from omega_v2.testbed.resource_transfer import TransferPolicy, build_world, transfer_events
from omega_v2.testbed.analysis.flow_matching import TransferFlux


def test_movement_only_never_redirects_into_chemistry_and_preserves_native_chemistry():
    p=FrictionParameters(discovery=True)
    policy=FrictionPolicy(mode='steering',phi=.95,cost=1,edges=((0,2),(1,2),(3,2)),
                          steering_scope='movement_only')
    state=(1,0,1,1,0,1,1,1)
    events=list(_mobility(state,p,policy))
    redirected=[e for e in events if e.family=='friction.steer']
    assert redirected
    assert all(e.target[4] in (1,3) and e.target[5:]==state[5:] for e in redirected)
    passive=list(_mobility(state,p,replace(policy,phi=0)))
    chemistry=lambda es:[e for e in es if e.family.startswith('S.') and e.family!='S.move']
    assert chemistry(events)==chemistry(passive)
    pocket=(1,0,1,1,4,1,1,1)
    assert list(_mobility(pocket,p,policy))==list(_mobility(pocket,p,replace(policy,phi=0)))


@pytest.mark.parametrize('affinity',[-3,3])
def test_driven_affinity_has_real_work_and_dark_equilibrium(affinity):
    p=FrictionParameters(charge_capacity=1,d_energy_capacity=2,d_energy_quantum=.5)
    policy=TransferPolicy(mode='extract',affinity=affinity)
    state=(1,0,1,1,0,1,1,1)
    event=next(e for e in transfer_events(state,p,policy) if e.increments.get('extract_forward'))
    reverse=next(e for e in transfer_events(event.target,p,policy) if e.increments.get('extract_reverse'))
    assert event.work==affinity and reverse.work==-affinity
    native=next(e for e in transfer_events(state,p,replace(policy,affinity=0)) if e.increments.get('extract_forward'))
    assert event.rate/native.rate==pytest.approx(exp(p.beta*affinity/2))
    world=build_world(replace(p,drive=False),policy)
    compiled=compile_world(world)
    w=np.array([world.degeneracy(s)*exp(-p.beta*world.energy(s)) for s in world.states]);w/=w.sum()
    flux=compiled['Q'].multiply(w[:,None])
    assert max(abs((flux-flux.T).data),default=0)<1e-12
    driven=compile_world(build_world(p,policy))
    assert max(abs(driven['Q']@driven['energy']-driven['flows']['drive_work']+driven['flows']['bath_heat']))<1e-12


def test_calibration_template_matches_independent_compiler_and_event_counts():
    p=FrictionParameters(charge_capacity=1,d_energy_capacity=2,d_energy_quantum=.5)
    template=TransferFlux(p)
    for A in (-1.3,.7):
        world=build_world(p,TransferPolicy(mode='extract',assistance=.3,affinity=A))
        actual=compile_world(world)
        Q,f,r=template.kernel(.3,A)
        assert max(abs((Q-actual['Q']).data),default=0)<1e-12
        assert max(abs(f-actual['flows']['extract_forward']))<1e-12
        assert max(abs(r-actual['flows']['extract_reverse']))<1e-12
