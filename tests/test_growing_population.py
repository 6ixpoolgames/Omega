from dataclasses import replace
import numpy as np
import pytest
from scipy.sparse import coo_matrix
from omega_v2.testbed import growing_population as g,controlled_slice as old
from omega_v2.testbed.growing_reference import build_reference
from omega_v2.testbed.growing_smoke import propagate,growth_witness

POLICY=(0.,.5,0.,.5)

def test_small_world_is_exact_legacy_regression():
    model=g.build((1,1),POLICY)
    indices=[old.INDEX[tuple((1 if w else 2 if a else 0,f,gate) for w,a,f,gate in s)] for s in model['states']]
    import json
    params=json.loads((old.SPEC/'PROTOCOL.json').read_text())['parameters']
    q,_=old.generator(POLICY,params)
    assert np.max(abs(model['Q'].toarray()-q[np.ix_(indices,indices)]))<1e-12

@pytest.mark.parametrize('bill',[1,2])
def test_degeneracy_thermal_balance_and_all_ledger_closures(bill):
    model=g.build((2,1),POLICY,replace(g.DEFAULT,chemical_potential=0,switch_tokens=bill))
    q=model['Q'];st=model['states'];flow=model['flows']
    pi=np.array([g.degeneracy(s,(2,1))*np.exp(-g.energy(s)) for s in st]);pi/=sum(pi)
    flux=q.multiply(pi[:,None]);difference=flux-flux.T
    assert max(abs(difference.data),default=0)<1e-12
    for function,name in ((g.energy,None),(g.built,'net_built'),(g.active,'net_active')):
        derivative=q@np.array([function(s) for s in st])
        expected=flow['drive_work']-flow['bath_heat'] if name is None else flow[name]
        assert max(abs(derivative-expected))<1e-12

@pytest.mark.parametrize('bill',[1,2])
def test_independent_labelled_generator_lumps_exactly(bill):
    params=replace(g.DEFAULT,switch_tokens=bill)
    model=g.build((2,1),POLICY,params);reference=build_reference((2,1),POLICY,params)
    mapped=[model['index'][reference['histograms'][i]] for i in reference['projection']]
    r=coo_matrix((np.ones(len(mapped)),(np.arange(len(mapped)),mapped)),shape=(len(mapped),len(model['states']))).tocsr()
    difference=reference['Q']@r-r@model['Q']
    assert max(abs(difference.data),default=0)<1e-12

def test_parent_offspring_can_repeat_paid_assistance():
    inv=(3,1);s=((0,1,3,0),(0,0,0,0))
    births=[e for e in g.events(s,inv,POLICY) if e.family=='assisted_birth' and e.active_change==1]
    assert len(births)==1 and births[0].rate>0
    first=births[0]
    second=next(e for e in g.events(first.target,inv,POLICY) if e.family=='assisted_birth' and e.active_change==1)
    assert second.rate>0 and second.target[0][1]==3
    assert g.energy(s)==g.energy(first.target)==g.energy(second.target)
    assert s[0][2]-second.target[0][2]==2
    dry=((0,1,0,0),(0,0,0,0))
    assert not any(e.family=='assisted_birth' and e.active_change>0 for e in g.events(dry,inv,POLICY))
    witness=growth_witness(g.DEFAULT,POLICY)['chain']
    assert witness[0]['recipient_coordinate']==witness[1]['example_parent_coordinate']
    assert witness[1]['specified_pair_rate']>0

def test_native_integer_switch_bill_and_no_remote_information():
    s=((0,1,2,0),(0,0,1,0));params=replace(g.DEFAULT,switch_tokens=2)
    switches=[e for e in g.events(s,(3,1),POLICY,params) if e.family.startswith('switch')]
    assert switches and all(sum(y[2]-x[2] for x,y in zip(s,e.target)) in(-2,2) for e in switches)
    assert all(e.target[1]==s[1] for e in switches)
    changed=(s[0],(0,1,1,0))
    left=lambda x:[(e.family,e.target[0],e.rate) for e in g.events(x,(3,1),POLICY,params)
                   if e.family.startswith('switch') and e.target[0]!=x[0]]
    assert left(s)==left(changed)

def test_caps_raise_without_changing_world():
    with pytest.raises(RuntimeError):g.build((3,3),max_states=100)
    with pytest.raises(RuntimeError):build_reference((3,3),max_states=1000)

def test_integrated_population_report_includes_thermal_reconstruction():
    model=g.build((1,1),POLICY)
    root=model['index'][((0,1,0,0),(0,1,0,0))]
    survey=propagate(model,root,1)
    assert survey['gross_thermal_reconstruction']>0
    assert abs(survey['population_residual'])<1e-12
    assert abs(survey['energy_residual'])<1e-12
