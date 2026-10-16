"""Reporting must preserve unfavorable signs and candidate-only scope."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from report_access_extension import assess

def test_assessment_flags_breadth_retention_and_function_disagreement():
    winner={'policy':['a']*4,'rate':2,'offsets':{'organized':1,'matched_shell':0},
            'profiles':{'1':{'organized':1,'matched_shell':0}},'stationary_active_total':.3}
    service={**winner,'policy':['service']*4,'rate':1.5,'stationary_active_total':.6}
    idle={**winner,'policy':['idle']*4,'rate':1.1,'stationary_active_total':.8}
    candidates=[]
    for row,value in ((winner,.1),(service,.4),(idle,.2)):
        candidates.append({'policy':row['policy'],
            'rule_a':{root:{lag:value for lag in ('0.0','0.25','1.0','4.0','16.0','64.0')}
                      for root in ('organized','disassembled','matched_shell','stationary')},
            'cadence_sensitivity':[{'cadence':d,'rate':row['rate']} for d in (.125,.5)],
            'chain_rule_rate':{},'organized_T64':{},'recovery_T64':{}})
    data={'capture_factor':1,'winner':winner,'policies':[winner,service,idle],
          'diagnostics':candidates,'best_deterministic_or_idle':service,'max_functioning_benchmark':idle,
          'finite_winners':{},'controller_count':1296,'deterministic_or_idle_count':81,
          'audits':{'max_stationarity_residual':0,'max_poisson_residual':0,'resource_residual':0}}
    r=assess(data)
    assert r['registered_outcomes']['E4']=='maintenance_tradeoff_hit'
    assert r['registered_outcomes']['E5']=='overlay_rank_disagreement'
    assert r['rule_a_assessment'][0]['best_listed_policies']==[['service']*4]
    assert r['protection_tradeoff']<0
