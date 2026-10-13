"""Engineering audits and bounded profiling; no policy search or verdicts."""
from __future__ import annotations
from dataclasses import replace
import json
from pathlib import Path
import time
import numpy as np
from scipy.linalg import expm
from scipy.sparse import bmat,coo_matrix,csr_matrix
from scipy.sparse.linalg import expm_multiply
from . import growing_population as g,controlled_slice as old
from .growing_reference import build_reference,assisted_events,_coarse
from .bng_network import transition,history_bits
from .rule_a_assessment import retention_profile

SPEC=old.ROOT/'docs/research_notes/lushness_testbed/growing_population'

def sparse_max(q):return float(max(abs(q.data),default=0))

def thermal_check(inv,policy,params):
    m=g.build(inv,policy,replace(params,chemical_potential=0))
    weights=np.array([g.degeneracy(s,inv)*np.exp(-g.energy(s)) for s in m['states']]);weights/=sum(weights)
    flux=m['Q'].multiply(weights[:,None]);error=sparse_max(flux-flux.T)
    if error>1e-11:raise AssertionError('Equilibrium flux mismatch')
    return error

def propagate(model,root,horizon):
    q=model['Q'];n=len(model['states']);names=['drive_work','bath_heat','gross_basal_birth','gross_assisted_birth',
        'gross_thermal_reconstruction','gross_built_loss','net_built','net_active','switches','gross_switch_fuel','gross_service_fuel']
    flux=csr_matrix(np.column_stack([model['flows'][k] for k in names]))
    augmented=bmat([[q,flux],[None,csr_matrix((len(names),len(names)))]],format='csr')
    initial=np.zeros(n+len(names));initial[root]=1
    final=expm_multiply(augmented.T*horizon,initial)
    dist=final[:n];result={k:float(v) for k,v in zip(names,final[n:])}
    st=model['states'];energy=np.array([g.energy(s) for s in st]);built=np.array([g.built(s) for s in st]);active=np.array([g.active(s) for s in st])
    result.update(mass_error=float(abs(sum(dist)-1)),initial_energy=float(energy[root]),final_energy=float(dist@energy),
                  initial_built=float(built[root]),final_built=float(dist@built),final_active=float(dist@active))
    result['energy_residual']=result['final_energy']-result['initial_energy']-result['drive_work']+result['bath_heat']
    result['population_residual']=result['final_built']-result['initial_built']-result['gross_basal_birth']-result['gross_assisted_birth']-result['gross_thermal_reconstruction']+result['gross_built_loss']
    if max(result['mass_error'],abs(result['energy_residual']),abs(result['population_residual']))>1e-9:
        raise AssertionError('Propagation ledger closure')
    return result

def exact_projection(inv,policy,params,delta):
    count=g.build(inv,policy,params);fine=build_reference(inv,policy,params)
    mapped=[count['index'][fine['histograms'][i]] for i in fine['projection']]
    r=coo_matrix((np.ones(len(mapped)),(np.arange(len(mapped)),mapped)),shape=(len(mapped),len(count['states']))).tocsr()
    derivative_error=sparse_max(fine['Q']@r-r@count['Q'])
    p_f=transition(fine['Q'].toarray(),delta);p_c=transition(count['Q'].toarray(),delta)
    projected=p_f@r
    semigroup_error=float(np.max(abs(projected-r@p_c)))
    # Projected endpoint rows have exactly the declared count readout entropy.
    h=lambda p:-(np.where(p>0,p*np.log2(np.maximum(p,1e-300)),0)).sum(axis=1)
    entropy_error=float(max(abs(h(projected)-np.asarray(r@h(p_c)).ravel())))
    if max(derivative_error,semigroup_error,entropy_error)>1e-10:raise AssertionError('Count projection mismatch')
    return {'fine_audit_states':len(mapped),'count_states':len(count['states']),
            'generator_error':derivative_error,'sampled_transition_error':semigroup_error,
            'projected_row_entropy_error':entropy_error,
            'scope':'count-history law exact; labelled-history entropy not claimed equal'}

def growth_witness(params,policy):
    inv=(3,1);s=((0,1,3,0),(0,0,0,0));chain=[]
    labelled=(((2,0,0),3,0),((0,),0,0))
    for parent,recipient in ((0,1),(1,2)):
        event=next(e for e in g.events(s,inv,policy,params) if e.family=='assisted_birth' and e.active_change==1)
        ref=next(ev for ev in assisted_events(labelled,inv,params)
                 if ev['compartment']==0 and ev['parent']==parent and ev['recipient']==recipient
                 and ev['target'][0][0][recipient]==2)
        if _coarse(ref['target'],inv)!=event.target:raise AssertionError('Specific parental route mismatches count law')
        labelled=ref['target'];per_pair=ref['rate']
        chain.append({'source':s,'target':event.target,'aggregate_rate':event.rate,
                      'example_parent_coordinate':parent,'recipient_coordinate':recipient,
                      'specified_pair_rate':per_pair,'fuel_consumed':s[0][2]-event.target[0][2],
                      'energy_change':g.energy(event.target)-g.energy(s),'heat':event.heat})
        s=event.target
    if s[0][1]!=3 or any(x['specified_pair_rate']<=0 or x['fuel_consumed']!=1 for x in chain):raise AssertionError('Recursive assistance missing')
    return {'chain':chain,'meaning':'lawful two-generation possibility witness; not a growth-rate or success-probability claim'}

def run(out):
    protocol=json.loads((SPEC/'SMOKE_PROTOCOL.json').read_text());params=g.Params(**protocol['parameters']);policy=protocol['policy']
    output={'scope':protocol['scope'],'cases':[],'checks':{}}
    for inv0 in protocol['cases']:
        inv=tuple(inv0);start=time.perf_counter();m=g.build(inv,policy,params,max_states=protocol['limits']['state_cap'])
        built_seconds=time.perf_counter()-start;q=m['Q'];st=m['states'];n=len(st)
        energies=np.array([g.energy(s) for s in st]);built=np.array([g.built(s) for s in st]);active=np.array([g.active(s) for s in st])
        row_error=float(max(abs(np.asarray(q.sum(axis=1)).ravel())))
        ledger_error=float(max(abs(q@energies-m['flows']['drive_work']+m['flows']['bath_heat'])))
        pop_error=float(max(abs(q@built-m['flows']['net_built'])))
        active_error=float(max(abs(q@active-m['flows']['net_active'])))
        if max(row_error,ledger_error,pop_error,active_error)>1e-10:raise AssertionError('Generator ledger')
        balance=thermal_check(inv,policy,params)
        if inv==(1,1):root=((0,1,0,0),(0,1,0,0))
        else:
            f0=min(3,inv[0]);root=((0,1,f0,0),(0,0,3-f0,0))
        ri=m['index'][root];e=g.energy(root)
        shell=np.array([g.energy(s)==e and all(x[3]==0 for x in s) for s in st])
        prior=np.array([g.degeneracy(s,inv) if on else 0 for s,on in zip(st,shell)],dtype=float);prior/=sum(prior)
        if abs(prior@energies-e)>1e-12:raise AssertionError('Preparation reference energy')
        begin=time.perf_counter();flux=propagate(m,ri,protocol['time']['smoke_horizon']);propagation_seconds=time.perf_counter()-begin
        record={'inventory':inv,'states':n,'stored_edges_including_diagonal':q.nnz,'build_seconds':built_seconds,
                'propagation_seconds':propagation_seconds,'csr_bytes':q.data.nbytes+q.indices.nbytes+q.indptr.nbytes,
                'dense_one_matrix_bytes':n*n*8,'thermal_balance_error':balance,'row_error':row_error,
                'generator_energy_error':ledger_error,'generator_population_error':pop_error,
                'generator_active_error':active_error,'root':root,'reference_shell_states':int(sum(shell)),
                'propagation':flux,'sampled_entropy_status':'unsupported_by_dense_path_above_1000_states'}
        if n<=protocol['limits']['dense_transition_state_cap']:
            begin=time.perf_counter();p=transition(q.toarray(),protocol['time']['cadence']);record['transition_seconds']=time.perf_counter()-begin
            steps=round(protocol['time']['smoke_horizon']/protocol['time']['cadence']);bits=history_bits(p,steps)
            record.update(sampled_entropy_status='exact_declared_count_readout',smoke_bits=float(bits[ri]))
        output['cases'].append(record)
        (out/'progress.json').write_text(json.dumps({'completed_inventories':len(output['cases']),'total':len(protocol['cases'])}))
    output['checks']['projection']=exact_projection(tuple(protocol['labelled_reference_inventory']),policy,params,protocol['time']['cadence'])
    model=g.build((1,1),policy,params);indices=[old.INDEX[tuple((1 if w else 2 if a else 0,f,gate) for w,a,f,gate in s)] for s in model['states']]
    oldparams=json.loads((old.SPEC/'PROTOCOL.json').read_text())['parameters'];qold,_=old.generator(policy,oldparams)
    legacy=float(np.max(abs(model['Q'].toarray()-qold[np.ix_(indices,indices)])))
    if legacy>1e-12:raise AssertionError('Legacy regression')
    output['checks']['legacy_generator_error']=legacy
    output['checks']['recursive_assistance']=growth_witness(params,policy)
    bill=protocol['additional_switch_bill_check'];output['checks']['switch_bill2_thermal_balance_error']=thermal_check((3,1),policy,replace(params,switch_tokens=bill))
    dry=((0,1,0,0),(0,0,0,0));drybirths=[x for x in g.events(dry,(3,1),policy,params) if x.family=='assisted_birth' and x.active_change>0]
    if drybirths:raise AssertionError('Unpaid assisted construction')
    output['checks']['zero_fuel_blocks_assisted_birth']=True
    qsmall=model['Q'].toarray();initial=np.zeros(len(qsmall));initial[model['index'][((0,1,0,0),(0,1,0,0))]]=1
    output['checks']['rule_a_small_count_readout']=retention_profile(qsmall,.25,(0.,.25,1.),{'root':initial})
    output['status']='passed_engineering_smoke'
    (out/'result.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    return output
