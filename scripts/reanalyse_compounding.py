"""Retrospective temporal/activity query over every completed compounding law."""
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC=ROOT/'docs/research_notes/lushness_testbed/compounding'
BASE='docs/research_notes/lushness_testbed/compounding'


def main():
    summary=json.loads((DOC/'SUMMARY.json').read_text())
    status=json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if status['status']!='complete':
        raise RuntimeError('Completed scientific batch required')
    sources=set(); parent_records=[]
    for law in summary['protocol']['laws']:
        gate=status['laws'][law['id']]
        manifest=verify_bundle(gate['run'])
        for rec in manifest['sources']:
            if hashlib.sha256((ROOT/rec['path']).read_bytes()).hexdigest()!=rec['sha256']:
                raise RuntimeError(f"Physical scientific source differs: {rec['path']}")
            sources.add(rec['path'])
        record=next(v for v in summary['files'] if v['path']==f"laws/{law['id']}.json")
        if hashlib.sha256((DOC/record['path']).read_bytes()).hexdigest()!=record['sha256']:
            raise RuntimeError('Retained physical result differs from its receipt')
        sources.add(BASE+'/'+record['path'])
        parent_records.append({'law':law['id'],'input_hash':manifest['input_hash'],
                               'data_path':BASE+'/'+record['path'],'sha256':record['sha256']})
    plan_path=DOC/'ACTIVITY_QUERY_PLAN.json'
    if not plan_path.exists():
        atomic_json(plan_path,{'status':'frozen_before_additional_jump_queries','date':'2026-10-15',
                    'scope':'retrospective all24 laws; known outcomes, not new confirmatory science',
                    'parents':parent_records,'fixed_jump_counts':[8,32,128],
                    'pairs':[['loop','basal'],['loop','no_construction_assistance'],['loop','no_capture_assistance']],
                    'horizons':[16,64,256,1024],'roots':['seed','unorganized'],'reference_time':1.,
                    'random_length_joint_entropy':'not computed',
                    'caps':{'seconds':120,'memory':512*1024**2,'output_cap':32*1024**2}})
    plan=json.loads(plan_path.read_text())
    if plan['parents']!=parent_records:
        raise RuntimeError('Reanalysis parents changed')
    sources.update([BASE+'/ACTIVITY_QUERY_PLAN.json','scripts/compounding_activity_worker.py','scripts/reanalyse_compounding.py'])
    out=ROOT/'results/local_runs/lushness_testbed/compounding'/(
        'activity-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])
    freeze_bundle(ROOT,out,sorted(sources),{'plan':plan})
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    profile=run_frozen(out,'scripts/compounding_activity_worker.py',[str(out)],plan['caps'])
    complete=profile['exit_code']==0 and not profile['cap_reason']
    atomic_json(DOC/'ACTIVITY_STATUS.json',{'status':'complete' if complete else 'incomplete','run':str(out),'profile':profile})
    if complete:
        r=json.loads((out/'RESULTS.json').read_text())
        atomic_json(DOC/'ACTIVITY_REANALYSIS.json',r)
    print(json.dumps(profile,indent=2))
    return 0 if complete else 1


if __name__=='__main__':
    raise SystemExit(main())
