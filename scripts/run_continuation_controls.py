"""Movement-only opportunity test and finite-window matched transfer controls."""
import argparse
import hashlib
import json
from pathlib import Path
import run_domination_b1 as engine

ROOT=Path(__file__).resolve().parents[1]
previous_sources=engine.sources
engine.sources=lambda: previous_sources()+['scripts/run_continuation_controls.py',
    'scripts/flow_calibration_worker.py','scripts/domination_b1_worker.py']

def configure(study):
    engine.DOC=ROOT/'docs/research_notes/lushness_testbed/continuation_controls'/study
    engine.LOCAL=ROOT/'results/local_runs/lushness_testbed'/('continuation_controls_'+study)

def steering(smoke=False):
    parameters={'discovery':True,'kappa':1,'charge_capacity':2,
                'd_energy_capacity':3,'d_energy_quantum':.5}
    common={'entropy_backend':'uniformized','entropy_threads':2,'block_rows':128}
    result=[]
    for y in (0,1,4,16):
        p={**parameters,'opportunity_yield':y}
        for mode,phi in (('idle',0),('steering',.55),('steering',.95),('blocking',.95)):
            policy={'mode':mode if mode!='idle' else 'blocking','phi':phi,'cost':.5,
                    'edges':[[0,2],[1,2],[3,2]],'steering_scope':'movement_only'}
            result.append({**common,'id':f'y{y}-{mode}-{phi:g}', 'parameters':p,'policy':policy})
    if smoke:
        case=next(c for c in result if c['id']=='y4-steering-0.95')
        case={**case,'id':'movement-smoke','parameters':{**case['parameters'],
                     'charge_capacity':1,'d_energy_capacity':2},'cadences':[.25],'horizons':[16,64]}
        return [case]
    return result

def flow_parameters():
    return {'charge_capacity':2,'d_energy_capacity':3,'d_energy_quantum':.5}

def flow(smoke=False):
    status=json.loads((engine.DOC/'CALIBRATION_STATUS.json').read_text())
    receipt=status['cases'][0]
    if status['status']!='complete':raise RuntimeError('Physical calibration incomplete')
    payload=(engine.DOC/'cases'/(receipt['identity']+'.json')).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=receipt['result_sha256']:
        raise RuntimeError('Calibration checksum differs')
    calibration=json.loads(payload)
    result=[{'id':point['id'],'parameters':flow_parameters(),
             'transfer_policy':{'mode':'extract','cost':.5,'assistance':point['assistance'],
                                'affinity':point['affinity']},
             'matching':{'target_gross':point['target_gross'],'fraction':point['fraction'],
                         'zero_net':point.get('zero_net',False),'horizon':256},
             'entropy_backend':'uniformized','entropy_threads':2,'block_rows':128}
            for point in calibration['points']]
    if smoke:
        result=[{**result[0],'id':'flow-smoke','cadences':[.25],'horizons':[16,64]}]
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['steering-smoke','steering-map','calibration','flow-smoke','flow-map'])
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--seconds',type=float,default=300)
    parser.add_argument('--budget',type=float,default=3600)
    args=parser.parse_args()
    if not 1<=args.jobs<=2:raise ValueError('One or two capped workers')
    configure('steering' if args.mode.startswith('steering') else 'flow')
    if args.mode=='calibration':
        cases=[{'id':'finite-flux-calibration','parameters':flow_parameters()}]
        worker='scripts/flow_calibration_worker.py'
    else:
        cases=steering(args.mode.endswith('smoke')) if args.mode.startswith('steering') else flow(args.mode.endswith('smoke'))
        worker='scripts/domination_b1_worker.py'
    mode='survey' if args.mode.endswith('map') else 'smoke' if args.mode.endswith('smoke') else 'calibration'
    raise SystemExit(engine.execute(cases,mode,args.jobs,args.seconds,args.budget,worker=worker))
