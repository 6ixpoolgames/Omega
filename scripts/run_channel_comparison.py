"""Freeze source, run one capped channel job, index its immutable artifacts."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import re
from pathlib import Path
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import freeze_bundle,atomic_json,verify_bundle,semantic_keys
from omega_v2.testbed.workflow.runner import run_frozen
from omega_v2.testbed.workflow.artifacts import ArtifactIndex
from omega_v2.testbed.experiments.channel_comparison import validate_protocol


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['smoke','profile','preflight','scientific'])
    parser.add_argument('--arm',choices=['uniform_absorbing','worn_absorbing','worn_reversible'],default='uniform_absorbing')
    parser.add_argument('--protocol',type=Path)
    parser.add_argument('--actuation',choices=['legacy','embodied'],default='legacy')
    parser.add_argument('--basal-rate',type=float,default=0.)
    parser.add_argument('--shock-mode',choices=['disabled','independent','correlated'],default='disabled')
    parser.add_argument('--hazard',type=float,default=0.)
    parser.add_argument('--hit-probability',type=float,default=1.)
    parser.add_argument('--trap-energy',type=float)
    parser.add_argument('--seconds',type=int)
    args=parser.parse_args()
    spec=ROOT/'docs/research_notes/lushness_testbed/channel_extension'
    if args.mode=='scientific':
        if args.protocol is None:parser.error('--protocol required for scientific mode')
        protocol=json.loads(args.protocol.read_text());validate_protocol(protocol)
        config={'mode':'scientific','protocol':protocol}
        limits=protocol['limits']
    else:
        protocol=json.loads((spec/'ENGINEERING_PROTOCOL.json').read_text())
        damage=protocol['damage_arms'][args.arm]
        damage=dict(damage)
        if args.trap_energy is not None:damage['energy']=args.trap_energy
        config={'mode':args.mode,'engineering':{'inventory':[3,1] if args.mode in ('profile','preflight') else [1,1],
            'damage':damage,'max_dense_bytes':protocol['max_dense_bytes'],
            'actuation':{'mode':args.actuation,'basal_rate':args.basal_rate},
            'shocks':{'enabled':args.shock_mode!='disabled','mode':'independent' if args.shock_mode=='disabled' else args.shock_mode,'hazard':args.hazard,'p':args.hit_probability}},'engineering_protocol':protocol}
        limits=dict(protocol['limits'])
        if args.seconds is not None:limits['wall_seconds']=args.seconds
        config['engineering_caps']=limits
    config['runtime']={'python':sys.version,'packages':{k:importlib.metadata.version(k) for k in ('numpy','scipy')}}
    label=re.sub(r'[^a-zA-Z0-9_.-]','-',protocol['id']) if args.mode=='scientific' else args.arm
    runid='channel-'+args.mode+'-'+label+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out=ROOT/'results/local_runs/lushness_testbed'/runid
    files=list((ROOT/'omega_v2/testbed').rglob('*.py'))+[ROOT/'omega_v2/__init__.py']
    files += [ROOT/'scripts'/name for name in ('channel_comparison_worker.py','run_channel_comparison.py',
              'report_channel_comparison.py','run_bng_binding_calibration.py')]
    files += list(spec.rglob('*.json'))
    relative=[p.relative_to(ROOT).as_posix() for p in files if p.is_file()]
    manifest=freeze_bundle(ROOT,out,relative,config)
    # Source groups keep report/readout edits out of the physical operator key.
    sources={'operator':{'runtime':config['runtime']},'query':{},'analysis':{}}
    for row in manifest['sources']:
        name=row['path']
        group='analysis' if name.endswith('registry.py') or name.startswith('scripts/report_') else (
            'query' if '/experiments/' in name or name.endswith('channel_access.py') else 'operator')
        sources[group][name]=row['sha256']
    identity=protocol if args.mode=='scientific' else {
        'world':config['engineering'],'controllers':protocol['controller'],
        'measurement':{'cadence':protocol['cadence']},'queries':{'mode':args.mode},'analysis':{'version':'engineering1'}}
    keys=semantic_keys(identity['world'],identity['controllers'],identity['measurement'],identity['queries'],identity['analysis'],sources)
    atomic_json(out/'CACHE_KEYS.json',keys)
    index=ArtifactIndex(out.parent/'registry.sqlite')
    index.register_run(runid,status='active',manifest=manifest,input_hash=manifest['input_hash'],cache_key=keys['query_hash'])
    atomic_json(out/'status.json',{'status':'active'})
    execution=run_frozen(out,'scripts/channel_comparison_worker.py',[str(out)],
        {'seconds':limits['wall_seconds'],'memory':limits['memory_mib']*1024**2,'output_cap':limits['output_mib']*1024**2})
    status='complete' if execution['exit_code']==0 else ('cap_hit' if execution['cap_reason'] else 'failed')
    if execution['exit_code']!=0 and (out/'failure.json').exists() and not execution['cap_reason']:
        failure=json.loads((out/'failure.json').read_text())
        if failure.get('status')=='numerical_failure':status='numerical_failure'
        if failure.get('type')=='MemoryError':status='cap_hit'
    atomic_json(out/'PROFILE.json',execution);atomic_json(out/'status.json',{'status':status,**execution})
    index.set_status(runid,status)
    artifacts=[]
    for path in sorted(out.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:continue
        row={'path':path.relative_to(out).as_posix(),'bytes':path.stat().st_size,
             'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};artifacts.append(row)
        index.register_artifact(runid+':'+row['path'],path,bytes=row['bytes'],sha256=row['sha256'],
            retention='evidence',run_id=runid,pinned=True)
    atomic_json(out/'artifacts.json',artifacts)
    verify_bundle(out)
    print(json.dumps({'run':str(out),'status':status,**execution}))
    return execution['exit_code']

if __name__=='__main__':raise SystemExit(main())
