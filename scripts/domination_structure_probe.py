"""Capped query-only origin/outcome counts over the unchanged physical law."""
import sys
from pathlib import Path

if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='worker':
    if sys.stdin.readline().strip()!='GO':raise SystemExit('Process caps required')

import hashlib
import json
from datetime import UTC,datetime
from time import perf_counter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def worker(out):
    import numpy as np
    from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json
    from omega_v2.testbed.domination_friction import FrictionParameters,FrictionPolicy,build_world,matched_roots
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.analysis.class_queries import occupation_distribution
    manifest=verify_bundle(out);config=manifest['config'];start=perf_counter()
    for path,digest in config['physical_sources'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Physical source differs from original scientific operator')
    p=FrictionParameters(**config['parameters'])
    world=build_world(p,FrictionPolicy(**config['policy']),max_states=32000)
    compiled=compile_world(world,max_states=32000)
    q=compiled['Q'];states=np.asarray(compiled['states'])
    print(json.dumps({'stage':'compiled','seconds':perf_counter()-start}),flush=True)
    source=np.repeat(np.arange(len(states)),np.diff(q.indptr));target=q.indices
    difference=states[target]!=states[source]
    joint=difference[:,3]&difference[:,4:7].any(axis=1)&(source!=target)
    movement=joint&difference[:,4]
    capture=joint&~difference[:,4]&difference[:,0]
    paid_build=joint&~difference[:,4]&~difference[:,0]&difference[:,5]&difference[:,6]
    thermal_build=joint&~difference[:,4]&~difference[:,0]&difference[:,5]&~difference[:,6]
    charge=joint&~difference[:,4]&~difference[:,0]&~difference[:,5]&difference[:,6]
    if np.any(joint&~(movement|capture|paid_build|thermal_build|charge)):
        raise RuntimeError('Unclassified joint physical outcome')
    masks={'all_joint_actuation':joint,
           'ordinary_origin':joint&(states[source,4]!=4),
           'pocket_origin':joint&(states[source,4]==4),
           'movement':movement,'capture_or_reverse':capture,
           'paid_build_or_reverse':paid_build,'thermal_assembly':thermal_build,
           'charge_or_upkeep':charge}
    vectors={name:np.bincount(source[mask],weights=q.data[mask],minlength=len(states))
             for name,mask in masks.items()}
    initial=np.zeros(len(states));initial[compiled['index'][matched_roots(p)['device_present']]]=1.
    rows={}
    for horizon in (256,1024):
        endpoint,occupation=occupation_distribution(q,initial,horizon)
        counts={name:float(occupation@v) for name,v in vectors.items()}
        counts['suppression_query']=float(occupation@compiled['observables']['suppressed_rate'])
        counts['ledger_redirects']=float(occupation@compiled['flows']['redirected_attempt'])
        if max(abs(counts[k]-counts['all_joint_actuation']) for k in ('suppression_query','ledger_redirects'))>1e-7:
            raise ArithmeticError('Physical support/query ledger identity failed')
        rows[str(horizon)]=counts
        print(json.dumps({'stage':f'T{horizon}','seconds':perf_counter()-start}),flush=True)
    imports={k:str(Path(v.__file__).resolve()) for k,v in sys.modules.items()
             if k.startswith('omega_v2') and getattr(v,'__file__',None)}
    if any(not Path(path).is_relative_to(ROOT) for path in imports.values()):raise RuntimeError('Import escaped snapshot')
    atomic_json(out/'RESULTS.json',{'case':config['id'],'query_only':True,'changes_scored_law':False,
        'classification':'actual joint D/S support and origin location; no event-label entropy',
        'counts':rows,'physical_sources':config['physical_sources'],'source_imports':imports,
        'elapsed_seconds':perf_counter()-start})


def main():
    from run_domination_friction import sources
    from omega_v2.testbed.workflow.manifest import freeze_bundle,atomic_json
    from omega_v2.testbed.workflow.runner import run_frozen
    doc=ROOT/'docs/research_notes/lushness_testbed/domination_b1'
    local=ROOT/'results/local_runs/lushness_testbed/domination_b1'
    plan=json.loads((doc/'SURVEY_PLAN.json').read_text())
    original=local/('batch-source-'+plan['source_hash'])
    physical=['omega_v2/testbed/domination_friction.py','omega_v2/testbed/energy_grid.py',
              'omega_v2/testbed/compiler.py','omega_v2/testbed/contracts.py']
    hashes={name:hashlib.sha256((original/name).read_bytes()).hexdigest() for name in physical}
    files=sources()+['scripts/domination_structure_probe.py']
    receipts=[]
    for name in ('y0-trap-c0.1-p0.95','y4-trap-c0.1-p0.95'):
        case=next(c for c in plan['cases'] if c['id']==name)
        config={**case,'physical_sources':hashes,'query_only':True}
        out=local/('structure-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'))
        freeze_bundle(ROOT,out,files,config)
        caps={'seconds':180,'memory':768*1024**2,'output_cap':8*1024**2}
        measured=run_frozen(out,'scripts/domination_structure_probe.py',['worker',str(out)],caps)
        receipt={'id':name,'profile':measured,'run':str(out)}
        if measured['exit_code'] or measured['cap_reason']:
            receipt['status']='incomplete';receipt['log_tail']=(out/'worker.log').read_text()[-2000:]
            receipts.append(receipt);atomic_json(doc/'STRUCTURE_PROBE.json',{'cases':receipts,'status':'incomplete'})
            print(json.dumps(receipt),flush=True);return 1
        receipt.update(status='complete',result=json.loads((out/'RESULTS.json').read_text()))
        receipts.append(receipt)
        atomic_json(doc/'STRUCTURE_PROBE.json',{'cases':receipts,'status':'complete' if len(receipts)==2 else 'running'})
        print(json.dumps({'id':name,'profile':measured,'counts':receipt['result']['counts']}),flush=True)
    return 0


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker(Path(sys.argv[2]))
    else:raise SystemExit(main())
