"""Engineering checks and frozen scientific channel comparisons."""
from __future__ import annotations

from dataclasses import replace
from itertools import product
from math import exp
import time
import numpy as np
from scipy.linalg import expm
from scipy.sparse import bmat, csr_matrix
from scipy.sparse.linalg import expm_multiply
from .. import growing_population as legacy
from ..compiler import compile_world
from ..contracts import ExperimentSpec
from ..modules.growth import build_world
from ..modules.material_sink import MaterialSink
from ..analysis.finite_classes import analyze, reachable_indices, finite_history_bits
from ..analysis.channel_access import closure_mask, closure_certificate, first_passage, recovery_profile, access_witness
from ..analysis.registry import interpret_channel,score_outcomes
from ..analysis.event_sequences import ordered_event_probability

POLICY = ((1., 0.), (.75, .25))*2

def time_key(value):
    return format(float(value),'.12g')


def build(inventory, policy=POLICY, damage=None, params=legacy.DEFAULT, max_states=10000):
    return compile_world(build_world(tuple(inventory), policy, params, damage, max_states=max_states), max_states)


def root_for(inventory):
    if tuple(inventory)==(1,1):
        return ((0,1,0,1,0),(0,0,0,0,0))
    if tuple(inventory)==(3,1):
        return ((0,1,0,2,0),(0,0,0,1,0))
    raise ValueError("Engineering roots declared only for 1+1 and 3+1")


def closure_surveys(model, physical_model, root, horizons):
    q = model['Q']; active = model['observables']['active']>0
    structural = closure_mask(physical_model['Q'], active)
    induced = closure_mask(q, active)
    initial = model['index'][root]
    reports = {}
    for name,mask in [('structural',structural),('policy',induced)]:
        certificate=closure_certificate(q,mask)
        if not certificate['closed']:
            raise AssertionError('Closure has outgoing physical transition')
        reports[name]={'target':'any active apparatus','states':int(mask.sum()),
                       'quantifier':'all admissible actuator channels' if name=='structural' else 'fixed implemented policy',
                       'certificate':certificate,
                       'first_entry':{time_key(t):first_passage(q,initial,mask,t)['hit_probability'] for t in horizons}}
    reports['recovery']=recovery_profile(q,initial,active,horizons)
    reports['access_witness']=access_witness(physical_model['Q'],initial,active)
    targets={f'active_compartment_{c}':np.array([s[c][1]>0 for s in model['states']]) for c in (0,1)}
    targets['paid_construction']=np.array([any(e.rate>0 and (
        e.increments.get('gross_basal_birth',0)>0 or e.increments.get('gross_assisted_birth',0)>0)
        for module in physical_model['world'].modules for e in module.events(s)) for s in model['states']])
    reports['additional_targets']={}
    for name,target in targets.items():
        structural_mask=closure_mask(physical_model['Q'],target)
        fixed_mask=closure_mask(q,target)
        reports['additional_targets'][name]={
            'structural_states':int(structural_mask.sum()),'policy_states':int(fixed_mask.sum()),
            'structural_certificate':closure_certificate(q,structural_mask),
            'policy_certificate':closure_certificate(q,fixed_mask),
            'structural_first_entry':{time_key(t):first_passage(q,initial,structural_mask,t)['hit_probability'] for t in horizons},
            'policy_first_entry':{time_key(t):first_passage(q,initial,fixed_mask,t)['hit_probability'] for t in horizons},
            'deadline_access':recovery_profile(q,initial,target,horizons),
            'access_witness':access_witness(physical_model['Q'],initial,target)}
    return reports


def flux_survey(model,initial,horizon):
    q=model['Q'];n=len(model['states']);names=sorted(model['flows'])
    matrix=csr_matrix(np.column_stack([model['flows'][k] for k in names]))
    aug=bmat([[q,matrix],[None,csr_matrix((len(names),len(names)))]],format='csr')
    p0=np.zeros(n+len(names));p0[:n]=initial
    final=expm_multiply(aug.T*horizon,p0)
    if abs(sum(final[:n])-1)>1e-9:raise ArithmeticError('Survey probability closure')
    flows={k:float(v) for k,v in zip(names,final[n:])}
    deltaE=float((final[:n]-initial)@model['energy'])
    residual=deltaE-flows['drive_work']+flows['bath_heat']
    if abs(residual)>1e-8:raise ArithmeticError('Survey energy closure')
    population_delta=float((final[:n]-initial)@model['observables']['built'])
    gross=(flows.get('gross_basal_birth',0)+flows.get('gross_assisted_birth',0)
           +flows.get('gross_thermal_reconstruction',0)+flows.get('gross_sink_return_to_built',0)
           -flows.get('gross_built_loss',0))
    population_residual=population_delta-gross
    if abs(population_residual)>1e-8:raise ArithmeticError('Gross population accounting closure')
    return {'flows':flows,'occupation':{k:float(final[:n]@v) for k,v in model['observables'].items()},
            'energy_residual':residual,'population_residual':population_residual}


def engineering(mode, config):
    """One fixed controller, no optimization or ethical ranking."""
    inventory=tuple(config['inventory']);damage=MaterialSink(**config['damage'])
    start=time.perf_counter();model=build(inventory,damage=damage)
    elapsed=time.perf_counter()-start;q=model['Q'];n=len(model['states'])
    record={'mode':mode,'scope':'engineering only; no policy search',
            'states':n,'offdiagonal_edges':int(q.nnz-n),'csr_bytes':int(q.data.nbytes+q.indices.nbytes+q.indptr.nbytes),
            'dense_one_matrix_bytes':n*n*8,'dense_analysis_estimate_bytes':n*n*8*8,
            'build_seconds':elapsed,'parameters':dict(model['metadata']),
            'row_residual':float(max(abs(np.asarray(q.sum(axis=1)).ravel())))}
    root=root_for(inventory);v=np.zeros(n);v[model['index'][root]]=1
    record['flux']=flux_survey(model,v,1.)
    start=time.perf_counter()
    if mode=='profile':
        if n*n*8*8>config['max_dense_bytes']:raise MemoryError('Dense timing pilot exceeds declared gate')
        p=expm(q.toarray()*.25)
        if np.min(p)<-1e-12 or max(abs(p.sum(axis=1)-1))>1e-9:raise ArithmeticError('Pilot transition check')
        record['exponential_seconds']=time.perf_counter()-start
        record['estimated_36_exponentials_seconds']=36*record['exponential_seconds']
        record['estimate_scope']='exponential cost only; excludes class solves/surveys/search overhead'
        record['exact_entropy_search']='not certified by timing pilot'
        return record
    result=analyze(q,.25,max_dense_bytes=config['max_dense_bytes'])
    record['analysis_seconds']=time.perf_counter()-start
    record['classes']=[len(x) for x in result['class_indices']]
    record['residuals']=result['residuals']
    # No scores or policy ranks are used to tune engineering parameters.
    union=build(inventory,policy=((.5,.5),)*4,damage=damage)
    record['channels']=closure_surveys(model,union,root,[1.,4.])
    worn=((1,0,0,1,0),(0,0,0,0,0))
    record['worn_start_recovery']=recovery_profile(q,model['index'][worn],model['observables']['active']>0,[1.,4.])
    lost=tuple((0,0,m,0,0) for m in inventory)
    record['all_D_recovery']=recovery_profile(q,model['index'][lost],model['observables']['active']>0,[1.,4.])
    record['all_D_access_witness']=access_witness(union['Q'],model['index'][lost],model['observables']['active']>0)
    record['closed_channel_thermal_rate']=float(result['rate_per_step'][model['index'][lost]]/.25)
    if damage.mode=='absorbing' and record['closed_channel_thermal_rate']<=0:
        raise AssertionError('Post-collapse thermal branching was removed')
    assisted=lambda e:e.increments.get('gross_assisted_birth',0)>0
    record['two_assisted_events']=ordered_event_probability(model['world'],root,[assisted,assisted],4.)
    if damage.mode=='absorbing' and damage.exposure==(1.,1.,1.):
        expected=(1-exp(-damage.rate*4))**sum(inventory)
        actual=record['channels']['structural']['first_entry']['4']
        record['uniform_null_error']=abs(actual-expected)
        if abs(actual-expected)>1e-10:raise AssertionError('Uniform pure-death null')
    thermal=build(inventory,damage=damage,params=replace(legacy.DEFAULT,chemical_potential=0))
    if damage.mode=='reversible':
        weights=np.array([thermal['world'].degeneracy(s)*np.exp(-thermal['world'].energy(s)) for s in thermal['states']]);weights/=weights.sum()
        flux=thermal['Q'].multiply(weights[:,None]);difference=flux-flux.T
        record['thermal_balance_residual']=float(max(abs(difference.data),default=0))
        if record['thermal_balance_residual']>1e-10:raise AssertionError('Reversible thermodynamics')
    else:
        record['thermal_balance']='not asserted for absorbing boundary idealization'
    old=legacy.build(inventory,POLICY);no_feature=build(inventory,damage=None)
    mapped=[old['index'][tuple((w,a,f,g) for w,a,d,f,g in s)] for s in no_feature['states']]
    difference=no_feature['Q']-old['Q'][mapped,:][:,mapped]
    record['legacy_generator_error']=float(max(abs(difference.data),default=0))
    if record['legacy_generator_error']>1e-12:raise AssertionError('Legacy regression')
    record['audit_status']='pass'
    return record


def validate_protocol(protocol):
    required=('id','version','status','world','controllers','measurement','queries','analysis','limits')
    if set(required)-protocol.keys():raise ValueError('Incomplete experiment protocol')
    spec=ExperimentSpec(**{k:protocol[k] for k in required})
    spec.require_scientific_freeze()
    for key in ('roots','reference_energy','horizons','rank_root'):
        if protocol['queries'].get(key) is None:raise ValueError(f'Missing query {key}')
    for key in ('cadence','max_dense_bytes'):
        if protocol['measurement'].get(key) is None:raise ValueError(f'Missing measurement {key}')
    queries=protocol['queries'];analysis=protocol['analysis'];controllers=protocol['controllers']
    horizons=queries['horizons']
    if not horizons or any(not np.isfinite(t) or t<=0 for t in horizons) or sorted(set(horizons))!=horizons:
        raise ValueError('Horizons must be nonempty, positive, unique and ordered')
    if queries['rank_root'] not in queries['roots']:raise ValueError('Ranking root absent')
    tolerance=analysis.get('rank_tolerance')
    if tolerance is None or not np.isfinite(tolerance) or tolerance<0:raise ValueError('Invalid rank tolerance')
    responses=controllers.get('responses',{})
    if not responses:raise ValueError('Empty controller responses')
    for response in responses.values():legacy._policy_entries((response,)*4)
    if 'selected_tables' in controllers:
        tables=controllers['selected_tables']
        if not tables or any(len(t)!=2 or any(name not in responses for name in t) for t in tables):
            raise ValueError('Invalid selected controller subset')
    if not analysis.get('registered_outcomes'):raise ValueError('Missing registered outcomes')
    ids=[]
    supported={'winner_rate','seed_excess','closure_probability','functioning_margin','max_residual','uniform_null_error'}
    for outcome in analysis['registered_outcomes']:
        if not isinstance(outcome,dict) or outcome.get('metric') not in supported or outcome.get('operator') not in ('record','eq','le','ge','lt','gt'):
            raise ValueError('Invalid registered numerical outcome')
        ids.append(outcome['id'])
        if outcome['operator']!='record' and ('threshold' not in outcome or not np.isfinite(outcome['threshold'])):
            raise ValueError('Outcome threshold required')
        if not np.isfinite(outcome.get('tolerance',0)) or outcome.get('tolerance',0)<0:raise ValueError('Invalid outcome tolerance')
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate outcome IDs')
    if set(protocol['world']['params'])!=set(vars(legacy.DEFAULT)):
        raise ValueError('Freeze all physical base parameters explicitly')
    if not np.isfinite(protocol['measurement']['cadence']) or protocol['measurement']['cadence']<=0:
        raise ValueError('Invalid physical cadence')
    return spec


def scientific(protocol, progress=lambda value:None):
    validate_protocol(protocol)
    world=protocol['world'];inv=tuple(world['inventory']);params=legacy.Params(**world['params'])
    damage=MaterialSink(**world['damage']) if world.get('damage') is not None else None
    delta=protocol['measurement']['cadence'];horizons=protocol['queries']['horizons']
    steps={int(round(t/delta)):t for t in horizons}
    if any(abs(t/delta-round(t/delta))>1e-10 for t in horizons):raise ValueError('Horizons must match physical cadence')
    responses=protocol['controllers']['responses'];rows=[]
    tables=protocol['controllers'].get('selected_tables') or list(product(responses,repeat=2))
    union=build(inv,((.5,.5),)*4,damage,params)
    for iteration,table in enumerate(tables,1):
        policy=(tuple(responses[table[0]]),tuple(responses[table[1]]))*2
        model=build(inv,policy,damage,params);n=len(model['states'])
        roots={k:tuple(tuple(x) for x in v) for k,v in protocol['queries']['roots'].items()}
        if any(abs(model['world'].energy(x)-protocol['queries']['reference_energy'])>1e-12 or
               any(y[2]!=0 or y[4]!=0 for y in x) for x in roots.values()):
            raise ValueError('Roots must match declared energy, initial usable material and service gates')
        initial={k:np.eye(1,n,model['index'][v]).ravel() for k,v in roots.items()}
        energy=protocol['queries']['reference_energy']
        ref=np.array([model['world'].degeneracy(s) if all(x[2]==0 and x[4]==0 for x in s)
                      and abs(model['world'].energy(s)-energy)<1e-12 else 0 for s in model['states']],float)
        if not ref.sum():raise ValueError('Empty matched reference')
        ref/=ref.sum();initial['matched_reference']=ref
        starts=np.flatnonzero(np.sum(list(initial.values()),axis=0)>0)
        keep=reachable_indices(model['Q'],starts)
        result=analyze(model['Q'][keep,:][:,keep],delta,protocol['measurement']['max_dense_bytes'])
        allbits={};total=np.zeros(len(keep));wanted=set(steps)
        for step in range(1,max(wanted)+1):
            total=result['row_entropy']+result['P']@total
            if step in wanted:allbits[time_key(steps[step])]={k:float(v[keep]@total) for k,v in initial.items()}
        limiting={k:{'rate':float(v[keep]@result['rate_per_step']/delta),
                     'offset':float(v[keep]@result['offset']),
                     'class_weights':(v[keep]@result['absorption']).tolist()} for k,v in initial.items()}
        rankroot=protocol['queries']['rank_root'];root=roots[rankroot]
        channels=closure_surveys(model,union,root,horizons)
        surveys={time_key(t):flux_survey(model,initial[rankroot],t) for t in horizons}
        sequence=ordered_event_probability(model['world'],root,
            [lambda e:e.increments.get('gross_assisted_birth',0)>0]*2,horizons[-1])
        rows.append({'table':list(table),'profiles_bits':allbits,'limiting':limiting,'channels':channels,
                     'surveys':surveys,'two_assisted_events':sequence,'residuals':result['residuals'],'reachable_states':len(keep),
                     'classes':[{'id':i,'state_indices':keep[x].tolist(),
                                 'stationary':result['stationary'][i].tolist(),
                                 'rate_bits_per_time':float(result['class_rate_per_step'][i]/delta)}
                                for i,x in enumerate(result['class_indices'])]})
        progress({'policies_done':iteration,'total':len(tables)})
    rankroot=protocol['queries']['rank_root'];tol=protocol['analysis']['rank_tolerance']
    rate=max(row['limiting'][rankroot]['rate'] for row in rows)
    tied=[row for row in rows if rate-row['limiting'][rankroot]['rate']<=tol]
    winner=max(tied,key=lambda row:row['limiting'][rankroot]['offset'])
    T=time_key(horizons[-1]);benchmark=max(rows,key=lambda row:row['surveys'][T]['occupation']['active'])
    findings=interpret_channel({'channel_empty':winner['channels']['structural']['states']==0,
        'winner_active':winner['surveys'][T]['occupation']['active'],
        'benchmark_active':benchmark['surveys'][T]['occupation']['active'],
        'winner_closure':winner['channels']['structural']['first_entry'][T],
        'benchmark_closure':benchmark['channels']['structural']['first_entry'][T],
        'seed_excess':winner['profiles_bits'][T][rankroot]-winner['profiles_bits'][T]['matched_reference']})
    null_error=None
    if damage is not None and damage.mode=='absorbing' and damage.exposure==(1.,1.,1.):
        expected=(1-exp(-damage.rate*horizons[-1]))**sum(inv)
        null_error=max(abs(row['channels']['structural']['first_entry'][T]-expected) for row in rows)
    metrics={'winner_rate':winner['limiting'][rankroot]['rate'],
             'seed_excess':winner['profiles_bits'][T][rankroot]-winner['profiles_bits'][T]['matched_reference'],
             'closure_probability':winner['channels']['structural']['first_entry'][T],
             'functioning_margin':winner['surveys'][T]['occupation']['active']-benchmark['surveys'][T]['occupation']['active'],
             'max_residual':max(v for row in rows for v in row['residuals'].values()),'uniform_null_error':null_error}
    return {'status':'complete','scope':protocol['controllers']['scope'],'winner':winner,
            'rate_ties':[r['table'] for r in tied],'policies':rows,'findings':findings,
            'metrics':metrics,'registered_outcomes':score_outcomes(metrics,protocol['analysis']['registered_outcomes']),
            'state_index_schema':{'coordinates':'per compartment (w,a,d,f,g)','states':model['states']},
            'rule_a':'parked','preparation_entropy':'not added','ethical_verdict':'not assigned'}
