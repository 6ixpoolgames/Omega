import json
import numpy as np
from omega_v2.testbed.controlled_slice import (
    SPEC, STATES, INDEX, energy, channels, generator, ROOT_ORGANIZED, ROOT_DISASSEMBLED,
)

PARAMS=json.loads((SPEC/'PROTOCOL.json').read_text())['parameters']

def test_matching_and_state_space():
    assert len(STATES)==144
    assert energy(STATES[ROOT_ORGANIZED])==energy(STATES[ROOT_DISASSEMBLED])==4

def test_local_detailed_balance_and_support():
    ch=channels((0.,.5,1.,.5),PARAMS)
    for f,r in zip(ch[::2],ch[1::2]):
        assert f.target==r.source and f.source==r.target
        assert all(f.source[c]==f.target[c] for c in (0,1) if c not in f.support)
        if f.rate:
            assert np.isclose(np.log(f.rate/r.rate),f.work-energy(f.target)+energy(f.source))
        else: assert r.rate==0

def test_energy_generator_and_equilibrium():
    q,flows=generator((.5,)*4,PARAMS)
    energies=np.array([energy(s) for s in STATES])
    assert np.max(abs(q@energies-flows['drive_work']+flows['bath_heat']))<1e-12
    assert np.max(abs(q.sum(axis=1)))<1e-12
    eq,_=generator((.5,)*4,{**PARAMS,'chemical_potential':0.})
    pi=np.exp(-energies);pi/=sum(pi)
    assert np.max(abs(pi[:,None]*eq-(pi[:,None]*eq).T))<1e-12

def test_no_free_build_or_remote_observation():
    # Changing right's local policy leaves all left-only channels unchanged.
    a=channels((.5,0.,0.,0.),PARAMS);b=channels((.5,0.,1.,1.),PARAMS)
    assert [c for c in a if c.support==(0,)]==[c for c in b if c.support==(0,)]
    for c in a:
        if c.family in ('build','repair') and c.target[c.support[0]][0]==2:
            local=c.support[0]
            assert c.source[local][1]==1 and c.target[local][1]==0

def test_relabeling_compartments_transports_policy():
    pol=(0.,.5,1.,0.)
    q,_=generator(pol,PARAMS);r,_=generator(pol[2:]+pol[:2],PARAMS)
    swap=[INDEX[(s[1],s[0])] for s in STATES]
    assert np.max(abs(q-r[np.ix_(swap,swap)]))<1e-12
