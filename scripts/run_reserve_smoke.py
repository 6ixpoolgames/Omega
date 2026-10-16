"""Snapshot and hard-cap one engineering job; never run policy optimization."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import freeze_bundle,atomic_json,verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inventory',choices=['1+1','3+1'],default='1+1')
    args=parser.parse_args(); inv=[int(x) for x in args.inventory.split('+')]
    config={'mode':'engineering_smoke_only','engineering':{'inventory':inv,
        'fixed_controller':{'id':'reserve-2-mix50-worn-service','threshold':2,
                            'surplus':'mix50','service_if_worn':True},
        'shocks':{'enabled':True,'mode':'correlated','hazard':.02,'p':1.},
        'cadence':.25,'horizons':[1.,4.,16.,64.,256.],'common_deadline':64.,
        'max_dense_bytes':768*1024**2},
        'limits':{'wall_seconds':120,'memory_mib':1024,'output_mib':256,'numeric_threads':1},
        'runtime':{'python':sys.version,'packages':{x:importlib.metadata.version(x) for x in ('numpy','scipy')}}}
    label='reserve-smoke-'+args.inventory+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out=ROOT/'results/local_runs/lushness_testbed'/label
    files=list((ROOT/'omega_v2/testbed').rglob('*.py'))+[ROOT/'omega_v2/__init__.py']
    files += [ROOT/'scripts'/x for x in ('run_reserve_smoke.py','reserve_smoke_worker.py','run_bng_binding_calibration.py')]
    files += list((ROOT/'docs/research_notes/lushness_testbed/next_expansions').glob('*.md'))
    freeze_bundle(ROOT,out,[p.relative_to(ROOT).as_posix() for p in files],config)
    execution=run_frozen(out,'scripts/reserve_smoke_worker.py',[str(out)],
                         {'seconds':120,'memory':1024**3,'output_cap':256*1024**2})
    status='complete' if execution['exit_code']==0 else 'cap_hit' if execution['cap_reason'] else 'failed'
    atomic_json(out/'PROFILE.json',execution);atomic_json(out/'status.json',{'status':status})
    verify_bundle(out)
    print(json.dumps({'run':str(out),'status':status,**execution}))
    return execution['exit_code']

if __name__=='__main__':raise SystemExit(main())
