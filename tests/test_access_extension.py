import numpy as np
from omega_v2.testbed import controlled_slice as w
from omega_v2.testbed.access_extension import load_protocol,basis,compile_policy,SHELL,evaluate

def test_linear_compiler_is_same_as_paid_channel_law():
    _,p=load_protocol();linear=basis(p)
    for pol in (((0.,0.),)*4,((1.,0.),(.25,.75),(0.,1.),(.75,.25))):
        full,sub,keep=compile_policy(pol,p,linear)
        native,flows=w.generator(pol,p)
        assert np.max(abs(full-native))<1e-12
        assert np.max(abs(full@np.array([w.energy(s) for s in w.STATES])-flows['drive_work']+flows['bath_heat']))<1e-12

def test_idle_reachable_class_and_matched_reference():
    _,p=load_protocol();q,sub,keep=compile_policy(((0.,0.),)*4,p)
    assert len(keep)==36 and len(SHELL)==8
    assert set(SHELL).issubset(set(keep))
    assert w.ROOT_ORGANIZED in SHELL and w.ROOT_DISASSEMBLED in SHELL
    for i,s in enumerate(w.STATES):
        for j in np.flatnonzero(q[i]>0):assert (s[0][2],s[1][2])==(w.STATES[j][0][2],w.STATES[j][1][2])
    result,pi,ref=evaluate(sub,keep,.25,[1])
    assert np.isclose(ref.sum(),1) and np.count_nonzero(ref)==8
    assert result['states']==36

def test_legacy_generator_and_partial_idle_closure():
    _,p=load_protocol()
    legacy=((1.,0.),(.5,.5),(1.,0.),(.5,.5))
    full,sub,keep=compile_policy(legacy,p)
    prior,_=w.generator((0.,.5,0.,.5),p)
    assert np.max(abs(full-prior))<1e-12 and len(keep)==144
    _,sub,keep=compile_policy(((0.,0.),(0.,0.),(1.,0.),(1.,0.)),p)
    assert len(keep)==72 and np.max(abs(sub.sum(axis=1)))<1e-12
