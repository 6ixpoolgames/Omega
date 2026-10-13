"""Horizon-primary exhaustive search of the frozen reserve controller family."""
from __future__ import annotations

import json
import numpy as np
from scipy.sparse import bmat,csr_matrix
from scipy.sparse.linalg import expm_multiply
from .. import growing_population as legacy
from ..compiler import compile_world
from ..controllers.reserve import ReservePolicy
from ..modules.growth import build_world
from ..modules.material_sink import MaterialSink
from ..modules.actuation import ActuationSpec
from ..modules.shocks import ShockSpec
from ..analysis.finite_classes import analyze,reachable_indices
from ..analysis.channel_access import closure_mask,closure_certificate,first_passage,recovery_profile
from .reserve_smoke import fingerprint
from .channel_comparison import flux_survey,time_key


def tied_ids(rows,score,tolerance):
    unique={r['canonical_id']:r for r in rows}
    top=max(score(r) for r in unique.values())
    return sorted(k for k,r in unique.items() if top-score(r)<=tolerance)


def validate(protocol):
    if protocol.get('status')!='frozen_before_scientific_ranking':
        raise ValueError('Frozen prospective protocol required')
    if protocol['analysis']['primary']!='complete conditional history bits at each horizon':
        raise ValueError('Horizon-primary objective required')
    if protocol['queries']['rank_root'] not in protocol['queries']['roots']:
        raise ValueError('Missing ranking root')
    delta=protocol['measurement']['cadence'];hs=protocol['queries']['horizons']
    if delta<=0 or hs!=sorted(set(hs)) or any(t<=0 or abs(t/delta-round(t/delta))>1e-10 for t in hs):
        raise ValueError('Invalid physical horizon/cadence')
    if not 0<protocol['analysis']['rank_tolerance']<=1e-6:
        raise ValueError('Invalid numerical ranking tolerance')
    policies=[ReservePolicy(**p) for p in protocol['controllers']['candidates']]
    if not policies or len({p.id for p in policies})!=len(policies) or len(policies)>48:
        raise ValueError('Invalid frozen candidate family')
    expected=set(vars(legacy.DEFAULT))
    if set(protocol['world']['params'])!=expected:raise ValueError('Physical parameters must all be frozen')
    return policies


def retained_first_entry(q,initial,active,T):
    """Query-only killed process: first return to function, then no later exit."""
    inactive=np.flatnonzero(~active);on=np.flatnonzero(active);order=np.r_[inactive,on]
    kernel=bmat([[q[inactive][:,inactive],q[inactive][:,on]],
                 [csr_matrix((len(on),len(inactive))),q[on][:,on]]],format='csr')
    final=expm_multiply(kernel.T*T,initial[order])
    value=float(final[len(inactive):].sum())
    if not -1e-10<=value<=1+1e-10:raise ArithmeticError('Retained recovery outside probability range')
    return float(np.clip(value,0,1))


def scientific(protocol,progress=lambda value:None):
    policies=validate(protocol);world=protocol['world'];inv=tuple(world['inventory'])
    params=legacy.Params(**world['params']);sink=MaterialSink(**world['damage'])
    actuator=ActuationSpec(**world['actuation']);shock=ShockSpec(**world['shocks'])
    def build(p):return compile_world(build_world(inv,p,params,sink,actuation=actuator,shocks=shock))
    physical=build(ReservePolicy('support-union',surplus='mix50'))
    n=len(physical['states']);active=physical['observables']['active']>0
    closed=closure_mask(physical['Q'],active)
    roots={k:tuple(tuple(x) for x in value) for k,value in protocol['queries']['roots'].items()}
    initial={k:np.eye(1,n,physical['index'][state]).ravel() for k,state in roots.items()}
    energy=protocol['queries']['reference_energy']
    if any(abs(physical['world'].energy(s)-energy)>1e-12 for s in roots.values()):
        raise ValueError('Preparation energies differ from registered match')
    ref=np.array([physical['world'].degeneracy(s) if all(x[2]==0 and x[4]==0 for x in s)
                  and abs(physical['world'].energy(s)-energy)<1e-12 else 0. for s in physical['states']])
    if not ref.sum():raise ValueError('Empty matched reference')
    ref/=ref.sum();initial['matched_reference']=ref
    rankroot=protocol['queries']['rank_root'];p0=initial[rankroot]
    diagnostic=tuple(tuple(x) for x in protocol['queries']['recovery_root'])
    recovery_initial=np.eye(1,n,physical['index'][diagnostic]).ravel()
    delta=protocol['measurement']['cadence'];hs=protocol['queries']['horizons']
    steps={int(round(t/delta)):t for t in hs};deadline=protocol['queries']['common_deadline']
    rows=[];cache={};tol=protocol['analysis']['rank_tolerance'];maximum_residual=0.
    for index,policy in enumerate(policies,1):
        model=build(policy);key=fingerprint(model)
        if key in cache:
            canonical=cache[key]
            rows.append({**canonical,'id':policy.id,'controller':policy.manifest(),
                         'alias_of':canonical['id']})
            progress({'completed':index,'total':len(policies),'unique':len(cache),'phase':'alias'})
            continue
        progress({'completed':index-1,'total':len(policies),'unique':len(cache),'phase':'solve','policy':policy.id})
        q=model['Q'];result=analyze(q,delta,protocol['measurement']['max_dense_bytes'])
        residual=max(result['residuals'].values());maximum_residual=max(maximum_residual,residual)
        if residual>protocol['analysis']['residual_tolerance']:raise ArithmeticError('Numerical residual gate')
        finite=np.zeros(n);bits={}
        for step in range(1,max(steps)+1):
            finite=result['row_entropy']+result['P']@finite
            if step in steps:bits[time_key(steps[step])]={k:float(v@finite) for k,v in initial.items()}
        limiting={k:{'rate':float(v@result['rate_per_step']/delta),'offset':float(v@result['offset'])}
                  for k,v in initial.items()}
        stationary=np.zeros(n);weights=p0@result['absorption']
        for weight,members,pi in zip(weights,result['class_indices'],result['stationary']):
            stationary[members]+=weight*pi
        cert=closure_certificate(q,closed)
        if not cert['closed']:raise ArithmeticError('Structural closure is not closed')
        hit=first_passage(q,p0,closed,deadline)['hit_probability']
        endpoint=expm_multiply(q.T*deadline,p0)
        if min(endpoint)<-1e-12 or abs(endpoint.sum()-1)>1e-9:raise ArithmeticError('Probability accounting')
        flux=flux_survey(model,p0,deadline)
        recovery=recovery_profile(q,recovery_initial,active,[deadline])[str(float(deadline))]
        retained=retained_first_entry(q,recovery_initial,active,deadline)
        if retained>recovery['hit_probability']+1e-9:raise ArithmeticError('Retention exceeds first entry')
        a=model['observables']['active'];built=model['observables']['built']
        function=float(stationary[active].sum());p=protocol['analysis']['probe_p']
        remaining=float(stationary[active]@(1-p**a[active]))
        left_surface=policy.audit_vector(inv[0]);keep=reachable_indices(q,[model['index'][roots[rankroot]]])
        reachable_obs={(model['states'][i][0][1],model['states'][i][0][0]) for i in keep}
        left_surface=[{**row,'reachable':(row['active'],row['worn']) in reachable_obs} for row in left_surface]
        responses={tuple(row['response']) for row in left_surface if row['reachable'] and row['active']>0}
        nonconstant=len(responses)>1
        nonrandom=all(tuple(r['response']) in ((0.,0.),(1.,0.),(0.,1.)) for r in left_surface)
        row={'id':policy.id,'canonical_id':policy.id,'rank_root':rankroot,
             'controller':policy.manifest(),'kernel_ledger_hash':key,
             'audit_surface':left_surface,'nonconstant_reachable':nonconstant,'nonrandom':nonrandom,
             'bits':bits,'limiting':limiting,'residuals':result['residuals'],
             'readouts':{'closure64':hit,'function64':float(endpoint[active].sum()),
                'active64':float(endpoint@a),'exposure64':float(endpoint@built),
                'stationary_active':float(stationary@a),'stationary_exposure':float(stationary@built),
                'stationary_function':function,
                'common_probe_conditional_reserve':remaining/function if function>1e-12 else None,
                'common_probe_unconditional_retained':remaining,
                'recovery_firsthit64':recovery['hit_probability'],
                'recovery_endpoint64':recovery['endpoint_target_probability'],
                'recovery_retained64':retained,'recovery_occupation64':recovery['integrated_target_occupation'],
                'costs64':flux['flows'],'accounting_residuals':{'energy':flux['energy_residual'],
                                                              'population':flux['population_residual']}}}
        cache[key]=row;rows.append(row)
        # Dense state matrices never enter the result/cache or the public report.
        del result
        progress({'completed':index,'total':len(policies),'unique':len(cache),'phase':'complete'})
    winners={time_key(t):tied_ids(rows,lambda r:r['bits'][time_key(t)][rankroot],tol) for t in hs}
    rate_winners=tied_ids(rows,lambda r:r['limiting'][rankroot]['rate'],tol)
    bestoffset=max(r['limiting'][rankroot]['offset'] for r in cache.values() if r['id'] in rate_winners)
    rate_winners=[k for k in rate_winners if bestoffset-cache[next(h for h,r in cache.items() if r['id']==k)]['limiting'][rankroot]['offset']<=tol]
    by_id={r['id']:r for r in rows}
    controls={name:[by_id['constant-'+name]['canonical_id']] for name in ('idle','service','export')}
    nonrandom_rows=[r for r in rows if r['nonrandom']]
    controls['best_nonrandom']={time_key(t):tied_ids(nonrandom_rows,
        lambda r:r['bits'][time_key(t)][rankroot],tol) for t in hs}
    return {'status':'complete','case_id':protocol['id'],'law_id':protocol['law_id'],'cadence':delta,
            'rank_root':rankroot,'policies':rows,'winners':winners,'rate_winners':rate_winners,
            'unique_models':len(cache),'states':n,'max_residual':maximum_residual,
            'fixed_comparators':controls,
            'reference_law':{'support_size':int(np.count_nonzero(ref)),'sha256':__import__('hashlib').sha256(ref.tobytes()).hexdigest(),
                             'meaning':'expected conditional history bits, not entropy of a hidden-root mixture'},
            'recovery_root':{'state':diagnostic,'energy':physical['world'].energy(diagnostic),'scope':'diagnostic only, not E8 matched objective'}}
