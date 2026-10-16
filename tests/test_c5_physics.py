from dataclasses import replace
from math import exp
import numpy as np
import pytest
from scipy.linalg import expm
from scipy.sparse import csr_matrix
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import FrictionParameters,FrictionPolicy,build_world,d_bank,s_bank
from omega_v2.testbed.physical_extensions import ExtensionSpec,build_world as extended,root
from omega_v2.testbed.analysis.streamed_history import StreamedQueries


def check_balance(world,p):
    c=compile_world(world,max_states=32000)
    weights=np.array([world.degeneracy(s)*exp(-p.beta*world.energy(s)) for s in world.states]);weights/=weights.sum()
    flux=c['Q'].multiply(weights[:,None])
    assert max(abs((flux-flux.T).data),default=0)<1e-12
    assert max(abs(c['Q']@c['energy']-c['flows']['drive_work']+c['flows']['bath_heat']))<1e-12


@pytest.mark.parametrize('feature',['pump','opportunity','loss'])
def test_extended_dark_physics_including_controller_and_multisite_field(feature):
    p=FrictionParameters(drive=False,charge_capacity=1,discovery=feature=='opportunity',
                         d_energy_capacity=2,d_energy_quantum=.5,field_shift=.7,
                         field_locations=(1,2))
    x=ExtensionSpec(pump=feature=='pump',pump_mode='extract',opportunity=feature=='opportunity',
                    irreversible_loss=.02 if feature=='loss' else 0)
    check_balance(extended(p,x),p)


def test_symmetric_fractional_banks_and_paid_discovery_have_correct_energy():
    p=FrictionParameters(drive=False,charge_capacity=1,d_energy_capacity=1,d_energy_quantum=.5,
                         s_energy_capacity=1,s_energy_quantum=.5,discovery=True)
    check_balance(build_world(p,FrictionPolicy(phi=0),max_states=10000),p)
    s=(1,0,1,0,2,1,2,1)
    events=[e for m in build_world(p,FrictionPolicy(phi=0),max_states=10000).modules for e in m.events(s)
            if e.family=='S.discovery_paid']
    assert events and events[0].target[6]==0


def test_pump_fuel_is_paid_by_D_and_each_leg_has_its_reverse():
    p=FrictionParameters(charge_capacity=1,d_energy_capacity=2,d_energy_quantum=.5)
    w=extended(p,ExtensionSpec(pump=True,pump_mode='extract'))
    f=w.metadata['fields'].index('D.pump_fuel')
    s=(1,0,1,2,0,1,1,1,0)
    ev=[e for m in w.modules if m.id=='funded-pump' for e in m.events(s)]
    charge=next(e for e in ev if e.increments.get('pump_charge_forward'))
    assert charge.target[3]==s[3]-1 and charge.target[f]==1 and charge.work==0
    assert w.energy(charge.target)==pytest.approx(w.energy(s))
    pump=next(e for m in w.modules if m.id=='funded-pump' for e in m.events(charge.target)
              if e.increments.get('pump_extract_forward'))
    assert pump.target[3]==charge.target[3]+2 and pump.target[6]==0 and pump.target[f]==0
    assert pump.work==0 and w.energy(pump.target)-w.energy(charge.target)==pytest.approx(-.5)
    reverse=[e for m in w.modules if m.id=='funded-pump' for e in m.events(pump.target)]
    assert any(e.target==charge.target for e in reverse)


def test_constructed_access_costs_resource_and_can_function_after_departure():
    p=FrictionParameters(discovery=True,charge_capacity=1,d_energy_capacity=1,d_energy_quantum=1)
    w=extended(p,ExtensionSpec(opportunity=True,fuel_energy=1))
    a=w.metadata['fields'].index('S.access_device');r=w.metadata['fields'].index('pocket.packet')
    s=(1,0,1,0,4,1,1,1,1,0)
    events=[e for m in w.modules if m.id=='constructed-access' for e in m.events(s)]
    build=next(e for e in events if e.increments.get('access_build_forward'))
    assert build.target[a]==1 and build.target[6]==0
    away=list(build.target);away[4]=3;away=tuple(away)
    captures=[e for m in w.modules if m.id=='constructed-access' for e in m.events(away)
              if e.increments.get('access_capture_forward')]
    assert captures and captures[0].target[r]==0 and captures[0].target[6]==1
    assert w.metadata['subjects']['S'][-1]==a and r in w.metadata['subjects']['background']


def test_irreversible_loss_removes_reconstruction_material_but_not_environment():
    p=FrictionParameters(charge_capacity=1)
    w=extended(p,ExtensionSpec(irreversible_loss=.02,fuel_energy=1))
    start=root(w,p)
    hit=next(e for m in w.modules if m.id=='material-sink' for e in m.events(start))
    assert hit.target[5]==0 and hit.target[-1]==1
    future=[e for m in w.modules for e in m.events(hit.target)]
    assert future and all(e.target[5]==0 and e.target[-1]==1 for e in future)


def test_single_closed_class_sparse_queries_allow_transients_without_discarding_them():
    Q=csr_matrix([[-.3,.3],[0.,0.]])
    with pytest.raises(ValueError):StreamedQueries(Q)
    solver=StreamedQueries(Q,allow_transients=True)
    cadence=.25;P=expm(Q.toarray()*cadence)
    g=-np.sum(np.where(P>0,P*np.log2(np.maximum(P,1e-300)),0),axis=1)
    sampled=solver.sampled(cadence,2,(g,{'row_entropy_error_bits':0.}))
    actual=solver.finite(sampled,2.)[0]
    direct=0.;v=np.array([1.,0.])
    for _ in range(8):direct+=v@g;v=v@P
    assert actual==pytest.approx(direct,abs=1e-8)


@pytest.mark.parametrize('bill',[1.,1.5])
def test_transfer_boundary_bills_preserve_dark_balance_with_symmetric_grids(bill):
    from omega_v2.testbed.resource_transfer import TransferPolicy,build_world as transfer
    p=FrictionParameters(drive=False,d_energy_capacity=3,d_energy_quantum=.5,
                         s_energy_capacity=2,s_energy_quantum=.5)
    check_balance(transfer(p,TransferPolicy(mode='extract',cost=bill),max_states=12000),p)
