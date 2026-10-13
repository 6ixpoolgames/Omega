"""File a finite, prospective embodiment/shock batch before any rankings."""
from pathlib import Path
import hashlib
import json
import copy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/research_notes/lushness_testbed/channel_extension/embodiment_shocks'

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    base=json.loads((OUT.parent/'PROTOCOL_shallow_-1.json').read_text())
    cases=[('legacy_reversible','legacy',.003,'reversible',False,'independent',1.),
           ('embodied_reversible','embodied',.003,'reversible',False,'independent',1.),
           ('independent_reversible','embodied',.003,'reversible',True,'independent',1.),
           ('correlated_half_reversible','embodied',.003,'reversible',True,'correlated',.5),
           ('correlated_all_reversible','embodied',.003,'reversible',True,'correlated',1.),
           ('embodied_absorbing','embodied',.003,'absorbing',False,'independent',1.),
           ('frozen_gate_absorbing','embodied',0.,'absorbing',False,'independent',1.)]
    manifest={'id':'embodiment-shocks-r1','version':'1','status':'frozen_before_scientific_ranking',
      'selection':'trap -1 primary; h=.5*wear=.02, basal=.02*switch=.003, p=.5/1 chosen before rankings',
      'objective':'same native count-history rate then offset; no RuleA or survival reward',
      'reserve':'1-E[.5**A | A>0] under each winning stationary mixture; common hypothetical probe, independent of native shock clock',
      'hypotheses':[
        {'id':'E1-service','lhs':'embodied_reversible','rhs':'legacy_reversible','metric':'active_service_weight','operator':'ge'},
        {'id':'E2-common-tail','case':'embodied_absorbing','metric':'policy_rate_spread','operator':'le','threshold':1e-9},
        {'id':'E3-frozen-tail','case':'frozen_gate_absorbing','metric':'policy_rate_spread','operator':'gt','threshold':1e-9},
        {'id':'R1-half-reserve','lhs':'correlated_half_reversible','rhs':'independent_reversible','metric':'stationary_common_probe_reserve','operator':'ge'},
        {'id':'R1-all-reserve','lhs':'correlated_all_reversible','rhs':'independent_reversible','metric':'stationary_common_probe_reserve','operator':'ge'},
        {'id':'R2-exposure','lhs':'independent_reversible','rhs':'embodied_reversible','metric':'stationary_exposure','operator':'record','meaning':'increase is a mechanism flag; not automatically adverse'},
        {'id':'R3-horizon','case':'embodied_absorbing','metric':'closure64_horizon1_minus_horizon64','operator':'ge','threshold':0.}],
      'tolerance':1e-9,'cases':[]}
    for name,mode,basal,damage,on,shock,p in cases:
        cfg=copy.deepcopy(base);cfg['id']='embodiment-r1-'+name;cfg['version']='2'
        cfg['world']['actuation']={'mode':mode,'basal_rate':basal}
        cfg['world']['damage'].update(mode=damage,energy=-1)
        cfg['world']['shocks']={'enabled':on,'mode':shock,'hazard':.02 if on else 0.,'p':p}
        cfg['queries']['diagnostic_roots']={'all_trapped_diagnostic':[[0,0,3,0,0],[0,0,1,0,0]]}
        cfg['analysis']['reserve_probe_p']=.5
        cfg['analysis']['registered_outcomes']=[
          {'id':'N1-numerics','metric':'max_residual','operator':'le','threshold':1e-8},
          {'id':'N2-breadth','metric':'winner_rate','operator':'record'},
          {'id':'N3-closure','metric':'closure_probability','operator':'record'},
          {'id':'N4-tail-spread','metric':'policy_rate_spread','operator':'record'}]
        cfg['controllers']['scope']='all36 shared local tables, exact kernel+ledger aliases retained; actuator law declared'
        cfg['amendment']='embodiment_shocks/PREREGISTRATION.json'
        cfg['calibration']='Fixed ratios before rankings; 1+1 smoke and fixed-controller3+1 preflight only. No policy outcomes selected parameters.'
        cfg['scientific_question']='Does physically available actuation and matched correlated damage change native breadth optimization and access?'
        path=OUT/(name+'.json');payload=json.dumps(cfg,indent=2)+'\n'
        if path.exists() and path.read_text()!=payload:raise ValueError('Refuse overwrite differing frozen protocol')
        path.write_text(payload)
        manifest['cases'].append({'case':name,'file':path.name,'sha256':hashlib.sha256(payload.encode()).hexdigest()})
    payload=json.dumps(manifest,indent=2)+'\n';path=OUT/'PREREGISTRATION.json'
    if path.exists() and path.read_text()!=payload:raise ValueError('Refuse amended preregistration overwrite')
    path.write_text(payload)
    print(f'Frozen {len(cases)} cases; {path}')

if __name__=='__main__':prepare()
