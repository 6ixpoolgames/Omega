from dataclasses import replace
import numpy as np
from omega_v2.testbed import growing_population as g
from omega_v2.testbed.growing_comparison import specification,restrict,root_queries,solve_policy,survey_queries
from omega_v2.testbed.bng_network import history_bits

def test_matching_and_unsupported_gate_class_restriction():
    p,params=specification();policy=((0.,0.),)*4;model=g.build((3,1),policy,params)
    q,keep=restrict(model,policy,params);roots=root_queries(model,keep,p)
    assert len(q)==240 and max(abs(q.sum(axis=1)))<1e-12
    energies=np.array([g.energy(model['states'][i]) for i in keep])
    for v in roots.values():assert np.isclose(v.sum(),1) and np.isclose(v@energies,8)
    assert np.count_nonzero(roots['matched_reference'])>1
    q,keep=restrict(g.build((3,1),(0.,.5,0.,.5),replace(params,switch_tokens=2)),(0.,.5,0.,.5),replace(params,switch_tokens=2))
    assert len(q)==480

def test_finite_entropy_and_poisson_identity_with_idle_control():
    p,params=specification();policy=((0.,0.),)*4;model=g.build((3,1),policy,params)
    r,s=solve_policy(model,policy,params,p)
    value=history_bits(s['P'],4)
    for name,v in s['queries'].items():assert np.isclose(v@value,r['profiles']['1'][name])
    assert r['poisson_residual']<1e-9 and r['stationary_residual']<1e-10

def test_survey_reference_and_seed_ledger_closure():
    p,params=specification();model=g.build((3,1),(0.,.5,0.,.5),params)
    survey=survey_queries(model,p,1)
    assert survey['distributed_seed']['initial_built']==1
    assert survey['unassembled']['initial_built']==0
    for r in survey.values():
        assert np.isclose(r['initial_energy'],8)
        assert abs(r['energy_residual'])<1e-8 and abs(r['population_residual'])<1e-8
        assert 0<=r['at_least_three_built']<=r['hit_three_built_by_horizon']+1e-10<=1+1e-10
