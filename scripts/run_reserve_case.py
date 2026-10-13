"""Freeze and hard-cap one registered reserve case, retaining all failure statuses."""
from __future__ import annotations
import argparse,json,sys,uuid,importlib.metadata
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import freeze_bundle,atomic_json,verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen
from omega_v2.testbed.experiments.reserve_batch import validate

def main():
    parser=argparse.ArgumentParser();parser.add_argument('protocol',type=Path)
    parser.add_argument('--remaining-seconds',type=int);args=parser.parse_args()
    cfg=json.loads(args.protocol.read_text());validate(cfg)
    out=ROOT/'results/local_runs/lushness_testbed'/('reserve-batch-'+cfg['id']+'-'+
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])
    files=list((ROOT/'omega_v2/testbed').rglob('*.py'))+[ROOT/'omega_v2/__init__.py']
    files += [ROOT/'scripts'/x for x in ('run_reserve_case.py','reserve_batch_worker.py','run_bng_binding_calibration.py')]
    files += list((ROOT/'docs/research_notes/lushness_testbed/reserve_batch_r1').glob('*.json'))
    runtime={'python':sys.version,'packages':{p:importlib.metadata.version(p) for p in ('numpy','scipy')}}
    freeze_bundle(ROOT,out,[p.relative_to(ROOT).as_posix() for p in files],{'protocol':cfg,'runtime':runtime})
    limits=cfg['limits'];ceiling=limits['wall_seconds']
    if args.remaining_seconds is not None:
        if args.remaining_seconds<1:raise ValueError('Batch time budget exhausted')
        ceiling=min(ceiling,args.remaining_seconds)
    profile=run_frozen(out,'scripts/reserve_batch_worker.py',[str(out)],
        {'seconds':ceiling,'memory':limits['memory_mib']*1024**2,'output_cap':limits['output_mib']*1024**2})
    atomic_json(out/'PROFILE.json',profile)
    atomic_json(out/'status.json',{'status':'complete' if not profile['exit_code'] else 'cap_hit' if profile['cap_reason'] else 'failed'})
    verify_bundle(out);print(json.dumps({'run':str(out),**profile}))
    return profile['exit_code']

if __name__=='__main__':raise SystemExit(main())
