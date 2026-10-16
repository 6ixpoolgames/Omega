"""Capped engineering gate, followed by frozen compounding-boundary science."""
import argparse
import hashlib
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.compounding import CompoundingParameters
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/compounding'
DOC = ROOT/BASE


def sources():
    return ([path.relative_to(ROOT).as_posix() for path in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py','scripts/run_bng_binding_calibration.py',
               'scripts/compounding_worker.py','scripts/run_compounding.py',BASE+'/SPEC.md'])


def output(mode, name):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    return ROOT/'results/local_runs/lushness_testbed/compounding'/f'{mode}-{name}-{stamp}'


def engineering():
    caps = {'seconds':120,'memory':512*1024**2,'output_cap':32*1024**2}
    out = output('engineering','capacity-profile')
    freeze_bundle(ROOT, out, sources(), {'mode':'engineering','capacities':[4,16,32], 'caps':caps})
    profile = run_frozen(out,'scripts/compounding_worker.py',[str(out)],caps)
    complete = profile['exit_code']==0 and not profile['cap_reason']
    status = {'status':'complete' if complete else 'incomplete','run':str(out),'profile':profile}
    atomic_json(DOC/'ENGINEERING_STATUS.json',status)
    if complete:
        atomic_json(DOC/'ENGINEERING_PROFILE.json',json.loads((out/'RESULTS.json').read_text()))
    print(json.dumps(status,indent=2))
    return 0 if complete else 1


def prepare():
    gate=json.loads((DOC/'ENGINEERING_STATUS.json').read_text())
    if gate['status']!='complete':
        raise RuntimeError('Largest-capacity exact smoke required')
    manifest=verify_bundle(gate['run'])
    if any(hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']
           for record in manifest['sources']):
        raise RuntimeError('Engineering sources changed; rerun engineering before freezing')
    if (DOC/'PROTOCOL.json').exists():
        raise FileExistsError('Protocol already frozen')
    rows=[]
    for damage in (.005,.02):
        for cost in (1.5,2.,2.5):
            for packet in (2.,3.,4.):
                p=CompoundingParameters(capacity=8,damage_rate=damage,construction_cost=cost,packet_energy=packet)
                rows.append({'id':f'M8-c{cost:g}-y{packet:g}-d{damage:g}','kind':'boundary','parameters':vars(p)})
        for capacity in (4,16,32):
            p=CompoundingParameters(capacity=capacity,damage_rate=damage)
            rows.append({'id':f'M{capacity}-c2-y3-d{damage:g}','kind':'capacity','parameters':vars(p)})
    p={'status':'frozen_before_scientific_ranking','date':'2026-10-15','laws':rows,
       'mechanisms':['loop','no_construction_assistance','no_capture_assistance','basal'],
       'roots':{'seed':[6,1,1],'unorganized':[8,1,0]},'horizons':[16,64,256,1024],
       'cadences':[.25,.125,.5],'primary_cadence':.25,'primary_horizon':64,
       'coordinate_order':[1,0,2],'funding_marker':.9,'thermal_marker':.05,
       'expansion_probability_marker':.5,'mean_apparatus_marker':1.,
       'tolerances':{'bits':1e-5,'rate':1e-8,'physical':1e-8,'ledger':1e-7},
       'caps':{'seconds':180,'memory':512*1024**2,'output_cap':32*1024**2},'total_seconds':3600,
       'predictions':{'P1':'some M8 point operates with retained apparatus above both single ablations',
                      'P2':'P1 points have positive loop-basal rate at all cadences',
                      'P3':'central low-damage retained apparatus and rate increase across M4/8/16/32',
                      'P4':'greater isolated damage lowers retained apparatus at every M8 cost/yield pair'}}
    atomic_json(DOC/'PROTOCOL.json',p)
    print('Scientific protocol frozen; no rankings inspected')
    return 0


def science():
    p=json.loads((DOC/'PROTOCOL.json').read_text())
    path=DOC/'SCIENCE_STATUS.json'
    status=json.loads(path.read_text()) if path.exists() else {'laws':{}}
    engineering=json.loads((DOC/'ENGINEERING_STATUS.json').read_text())
    engineering_sources=verify_bundle(engineering['run'])['sources']
    for law in p['laws']:
        if status['laws'].get(law['id'],{}).get('status')=='complete':
            continue
        used=sum(v['profile']['wall_seconds'] for v in status['laws'].values())
        if used+p['caps']['seconds']>p['total_seconds']:
            raise RuntimeError('Total budget leaves insufficient room for another complete case')
        out=output('science',law['id'])
        manifest=freeze_bundle(ROOT,out,sources()+[BASE+'/PROTOCOL.json'],{'mode':'science','law':law,'protocol':p})
        comparable=[record for record in manifest['sources'] if record['path']!=BASE+'/PROTOCOL.json']
        if comparable!=engineering_sources:
            raise RuntimeError('Scientific sources differ from capped engineering profile')
        profile=run_frozen(out,'scripts/compounding_worker.py',[str(out)],p['caps'])
        complete=profile['exit_code']==0 and not profile['cap_reason']
        status['laws'][law['id']]={'status':'complete' if complete else 'incomplete','run':str(out),'profile':profile}
        atomic_json(DOC/'SCIENCE_STATUS.json',status)
        print(json.dumps({'law':law['id'],**profile}),flush=True)
        if not complete:
            return 1
    status['status']='complete'
    atomic_json(path,status)
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['engineering','prepare','science'])
    raise SystemExit(globals()[parser.parse_args().mode]())
