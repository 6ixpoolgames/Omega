"""The law swap against useful control, with an explicit old/new kernel audit."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.domination_friction import FrictionParameters,FrictionPolicy,build_world
from omega_v2.testbed.analysis.observed_history import interval_comparison
from omega_v2.testbed.analysis.temporal_profile import crossover
from report_domination_b1 import load,DOC,csv_write


def main():
    olddoc=ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'
    source=ROOT/'results/local_runs/lushness_testbed/domination_stage_a/batch-source-67427275b3680bd03ecaa8f91435847164ae0177efa05e56e0e9d1fd42ba8159'
    name='omega_v2.testbed._stage_a_model_audit'
    spec=importlib.util.spec_from_file_location(name,source/'omega_v2/testbed/domination_friction.py')
    legacy=importlib.util.module_from_spec(spec);sys.modules[name]=legacy;spec.loader.exec_module(legacy)
    oldstatus=json.loads((olddoc/'SURVEY_STATUS.json').read_text())
    receipts={r['id']:r for r in oldstatus['cases']}
    _,new,_=load('followup')
    def original(name):
        receipt=receipts[name];p=olddoc/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=receipt['result_sha256']:
            raise RuntimeError('Stage A result hash mismatch')
        return json.loads(p.read_text())
    rows=[];residuals=[];score_residuals=[]
    for supply,kappa in ((.04,0),(.12,0),(.12,1)):
        prefix=f's{supply:g}-k{kappa}'
        lp=legacy.FrictionParameters(supply=supply,kappa=kappa)
        p=FrictionParameters(supply=supply,kappa=kappa)
        oldw=legacy.build_world(lp,legacy.FrictionPolicy(mode='steering',region=(2,),phi=.95,cost=1))
        neww=build_world(p,FrictionPolicy(mode='steering',region=(2,),phi=.95,cost=1))
        a,b=(compile_world(w) for w in (oldw,neww))
        assert a['states']==b['states']
        delta=a['Q']-b['Q']
        residuals.append(float(max(abs(delta.data),default=0.)))
        assert residuals[-1]<1e-12
        protective=original(prefix+'-trap_entry-steering-p0.95-c1')
        oldidle=original(prefix+'-idle')
        ordinary=new[f's{supply}-k{kappa}-ordinary']
        idle=new[f's{supply}-k{kappa}-idle']
        for dt,clock in ordinary['cadences'].items():
            for time,aa in clock['profiles']['device_present'].items():
                bb=protective['cadences'][dt]['profiles']['device_present'][time]
                score_residuals.append(abs(idle['cadences'][dt]['profiles']['device_present'][time]['global_bits']
                    -oldidle['cadences'][dt]['profiles']['device_present'][time]['global_bits']))
                row={'supply':supply,'kappa':kappa,'cadence':float(dt),'horizon':float(time),
                     'ordinary_minus_protective_global':aa['global_bits']-bb['global_bits']}
                temporal=crossover(ordinary['physical']['device_present'][time],
                                   protective['physical']['device_present'][time])
                row.update(delta_jumps=temporal['delta_jumps'],delta_finite_term=temporal['delta_finite_bits'],
                           estimated_crossover=temporal['estimated_cadence'],
                           crossover_is_asymptotic_not_exact=True)
                for subject in ('D','S'):
                    row.update({subject+'_'+key:value for key,value in interval_comparison(
                        aa['subjects'][subject],bb['subjects'][subject],1e-5).items()})
                rows.append(row)
    assert max(score_residuals)<1e-7
    csv_write('ORDINARY_VS_PROTECTIVE.csv',rows)
    (DOC/'DEFAULT_KERNEL_BRIDGE.json').write_text(json.dumps({
        'default_kernel_max_differences':residuals,'idle_score_replay_max_error_bits':max(score_residuals),
        'contexts':3,'physical_state_order_identical':True,
        'comparison':'ordinary auxiliary law minus trap-entry steering phi .95 cost 1',
        'new_law_source':'FOLLOWUP_STATUS.json','protective_source':'../domination_stage_a/SURVEY_STATUS.json'},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(rows),'kernel_max':max(residuals),'score_replay_error':max(score_residuals)}))

if __name__=='__main__':main()
