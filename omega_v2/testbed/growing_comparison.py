"""Finite controlled growth comparison; unfiltered count-history breadth only."""
from __future__ import annotations
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import time
import numpy as np
from scipy.linalg import solve
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply
from . import growing_population as g,controlled_slice as old
from .growing_smoke import propagate,thermal_check
from .bng_network import transition

SPEC=old.ROOT/'docs/research_notes/lushness_testbed/growing_population'

def specification():
    p=json.loads((SPEC/'COMPARISON_PROTOCOL.json').read_text())
    if p['status']!='frozen_before_scientific_ranking':raise RuntimeError('Protocol not frozen')
    base=json.loads((SPEC/p['parameters_from']).read_text())['parameters']
    return p,g.Params(**base)

def restrict(model,policy,params):
    inv=model['inventory'];responses=g._policy_entries(policy)
    fixed=[params.switch_tokens>inv[c] or all(sum(responses[2*c+i])==0 for i in (0,1)) for c in (0,1)]
    keep=np.array([i for i,s in enumerate(model['states']) if all(not fixed[c] or s[c][3]==0 for c in (0,1))])
    q=model['Q'][keep,:][:,keep].toarray()
    if max(abs(q.sum(axis=1)))>1e-10:raise AssertionError('Restricted class not closed')
    return q,keep

def root_queries(model,keep,p):
    st=model['states'];map_sub={x:i for i,x in enumerate(keep)}
    queries={}
    for name,state in p['roots'].items():
        s=tuple(tuple(x) for x in state)
        if g.energy(s)!=8:raise AssertionError('Unmatched energy')
        v=np.zeros(len(keep));v[map_sub[model['index'][s]]]=1;queries[name]=v
    reference=np.array([g.degeneracy(st[i],model['inventory']) if g.energy(st[i])==8
                        and all(x[3]==0 for x in st[i]) else 0 for i in keep],dtype=float)
    if sum(reference)==0:raise AssertionError('Empty reference')
    reference/=sum(reference);queries['matched_reference']=reference
    return queries

def solve_policy(model,policy,params,p,delta=None):
    q,keep=restrict(model,policy,params);delta=p['clock']['primary_cadence'] if delta is None else delta
    begin=time.perf_counter();pt=transition(q,delta);exponential_seconds=time.perf_counter()-begin
    entropy=old.entropy_rows(pt);pi=old.stationary(q);h=float(pi@entropy)
    z=solve(np.eye(len(q))-pt+np.ones((len(q),1))*pi[None,:],entropy-h)
    residual=float(max(abs(z-pt@z-entropy+h)))
    if residual>1e-9:raise ArithmeticError('Offset residual')
    roots=root_queries(model,keep,p);bits=np.zeros(len(q));profiles={}
    steps={round(t/delta):t for t in p['clock']['horizons']}
    for n in range(1,max(steps)+1):
        bits=entropy+pt@bits
        if n in steps:profiles[str(steps[n])]={k:float(v@bits) for k,v in roots.items()}
    st=[model['states'][i] for i in keep]
    record={'rate_bits_per_time':h/delta,'offset_bits':{k:float(v@z) for k,v in roots.items()},
            'profiles':profiles,'states':len(q),'stationary_built':float(pi@np.array([g.built(s) for s in st])),
            'stationary_active':float(pi@np.array([g.active(s) for s in st])),
            'stationary_flows':{k:float(pi@v[keep]) for k,v in model['flows'].items()},
            'stationary_residual':float(max(abs(pi@q))),'poisson_residual':residual,
            'exponential_seconds':exponential_seconds}
    return record,{'q':q,'P':pt,'pi':pi,'keep':keep,'queries':roots}

def select(rows):
    high=max(x['rate_bits_per_time'] for x in rows)
    tied=[x for x in rows if high-x['rate_bits_per_time']<=1e-9]
    return max(tied,key=lambda x:x['offset_bits']['distributed_seed']),[x['table'] for x in tied]

def survey_queries(model,p,horizon):
    names=['drive_work','bath_heat','gross_basal_birth','gross_assisted_birth','gross_thermal_reconstruction',
           'gross_built_loss','switches','gross_switch_fuel','gross_service_fuel']
    q=model['Q'];n=len(model['states']);flux=csr_matrix(np.column_stack([model['flows'][k] for k in names]))
    from scipy.sparse import bmat
    augmented=bmat([[q,flux],[None,csr_matrix((len(names),len(names)))]],format='csr')
    queries=root_queries(model,np.arange(n),p);initial=np.zeros((n+len(names),len(queries)))
    for c,v in enumerate(queries.values()):initial[:n,c]=v
    final=expm_multiply(augmented.T*horizon,initial)
    e=np.array([g.energy(s) for s in model['states']]);b=np.array([g.built(s) for s in model['states']]);a=np.array([g.active(s) for s in model['states']])
    reports={}
    for c,(name,v) in enumerate(queries.items()):
        d=final[:n,c];r={k:float(value) for k,value in zip(names,final[n:,c])}
        r.update(built=float(d@b),active=float(d@a),energy=float(d@e),
                 initial_built=float(v@b),initial_active=float(v@a),initial_energy=float(v@e),
                 at_least_three_built=float(d@(b>=3)),at_least_three_active=float(d@(a>=3)))
        r['population_residual']=r['built']-r['initial_built']-r['gross_basal_birth']-r['gross_assisted_birth']-r['gross_thermal_reconstruction']+r['gross_built_loss']
        r['energy_residual']=r['energy']-r['initial_energy']-r['drive_work']+r['bath_heat']
        if max(abs(r['population_residual']),abs(r['energy_residual']))>1e-8:raise AssertionError('Survey ledger closure')
        reports[name]=r
    killed=q.tolil();targets=np.flatnonzero(b>=3)
    for i in targets:killed[i,:]=0
    probabilities=expm_multiply(killed.tocsr().T*horizon,initial[:n,:])
    for c,name in enumerate(queries):reports[name]['hit_three_built_by_horizon']=float(probabilities[targets,c].sum())
    return reports

def profile(out):
    """Numerical timing only; no entropy or ranking inspected."""
    p,params=specification();policy=((1.,0.),(.5,.5),(1.,0.),(.5,.5))
    start=time.perf_counter();model=g.build(tuple(p['inventory']),policy,params);buildtime=time.perf_counter()-start
    q,_=restrict(model,policy,params)
    start=time.perf_counter();pt=transition(q,.25);exptime=time.perf_counter()-start
    start=time.perf_counter();pi=old.stationary(q);stat_time=time.perf_counter()-start
    start=time.perf_counter();rhs=np.sin(np.arange(len(q)));rhs-=pi@rhs
    solve(np.eye(len(q))-pt+np.ones((len(q),1))*pi[None,:],rhs);offset_time=time.perf_counter()-start
    start=time.perf_counter();v=np.zeros(len(q))
    for _ in range(256):v=rhs+pt@v
    horizon_time=time.perf_counter()-start
    record={'states':len(q),'build_seconds':buildtime,'exponential_seconds':exptime,'stationary_seconds':stat_time,
            'offset_seconds':offset_time,'256_matvec_seconds':horizon_time,
            'estimated_primary_36_policy_seconds':36*(buildtime+exptime+stat_time+offset_time+horizon_time),
            'scope':'timing-only; estimate excludes selected surveys and controls'}
    (out/'profile_kernel.json').write_text(json.dumps(record,indent=2)+'\n');return record

def run(out,arm):
    p,base=specification()
    if arm not in p['mechanism_arms']:raise ValueError('Unregistered arm')
    params=replace(base,**p['mechanism_arms'][arm]);inventory=tuple(p['inventory'])
    responses={k:tuple(v) for k,v in p['controller_responses'].items()};rows=[]
    for i,(inactive,active) in enumerate(product(responses,repeat=2),1):
        policy=(responses[inactive],responses[active])*2;model=g.build(inventory,policy,params)
        r,_=solve_policy(model,policy,params,p);rows.append({'table':[inactive,active],**r})
        (out/'progress.json').write_text(json.dumps({'arm':arm,'policies_done':i,'total':36}))
    winner,tied=select(rows);det=[r for r in rows if all(x in ('idle','service','export') for x in r['table'])]
    bestdet,_=select(det);bestactive=max(rows,key=lambda r:r['stationary_active'])
    chosen={tuple(r['table']) for r in (winner,bestdet,bestactive)}
    chosen.update((x,x) for x in ('idle','service','mix50'));chosen.add(('service','mix50'))
    diagnostics=[]
    for table in sorted(chosen):
        policy=(responses[table[0]],responses[table[1]])*2;model=g.build(inventory,policy,params)
        surveys={str(t):survey_queries(model,p,t) for t in p['clock']['horizons']}
        clock=[]
        for delta in p['clock']['sensitivity_cadences']:
            r,_=solve_policy(model,policy,params,p,delta);clock.append({'cadence':delta,**r})
        bill=replace(params,switch_tokens=2);billmodel=g.build(inventory,policy,bill)
        billrecord,_=solve_policy(billmodel,policy,bill,p)
        diagnostics.append({'table':table,'surveys':surveys,'cadence_sensitivity':clock,'bill2':billrecord,
                            'thermal_balance_error':thermal_check(inventory,policy,params)})
    table=winner['table'];policy=(responses[table[0]],responses[table[1]])*2;model=g.build(inventory,policy,params)
    _,solver=solve_policy(model,policy,params,p);pt=solver['P'];keep=solver['keep']
    root=tuple(tuple(x) for x in p['roots']['distributed_seed']);root_sub=int(np.flatnonzero(keep==model['index'][root])[0])
    rng=np.random.default_rng(p['seed']);N=10000;positions=np.full(N,root_sub);info=np.zeros(N);cdf=np.cumsum(pt,axis=1);cdf[:,-1]=1
    for _ in range(16):
        # Chunk rows to bound temporary memory while sampling the same law.
        for start in range(0,N,1000):
            sl=slice(start,start+1000);current=positions[sl];u=rng.random(len(current))
            target=(u[:,None]>cdf[current]).sum(axis=1);info[sl]-=np.log2(pt[current,target]);positions[sl]=target
    expected=winner['profiles']['4']['distributed_seed'];se=float(info.std(ddof=1)/np.sqrt(N))
    sampling={'mean':float(info.mean()),'exact':expected,'standard_error':se,'passed':bool(abs(info.mean()-expected)<=6*se)}
    if not sampling['passed']:raise AssertionError('Sampled path-information check')
    reference=solver['queries']['matched_reference'];energies=np.array([g.energy(model['states'][i]) for i in keep])
    if abs(reference@energies-8)>1e-12:raise AssertionError('Reference energy')
    result={'experiment':p['id'],'arm':arm,'parameters':vars(params),'controllers':36,'winner':winner,
            'rate_optimal_set':tied,'best_deterministic':bestdet,'maximum_functioning':bestactive,
            'finite_winners':{str(t):max(rows,key=lambda r:r['profiles'][str(t)]['distributed_seed'])['table'] for t in p['clock']['horizons']},
            'policies':rows,'diagnostics':diagnostics,'reference_states':int(np.count_nonzero(reference)),
            'reference_initial_built':float(reference@np.array([g.built(model['states'][i]) for i in keep])),
            'reference_initial_active':float(reference@np.array([g.active(model['states'][i]) for i in keep])),
            'sampling_check':sampling,
            'audits':{'max_stationary_residual':max(r['stationary_residual'] for r in rows),
                      'max_poisson_residual':max(r['poisson_residual'] for r in rows),
                      'reachable_state_counts':sorted({r['states'] for r in rows})},
            'rule_a':'parked, not evaluated','optimization_scope':p['controller_scope']}
    (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result
