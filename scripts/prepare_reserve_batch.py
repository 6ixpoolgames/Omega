"""File a prospective horizon-primary reserve batch before scientific ranking."""
from pathlib import Path
import copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.controllers.reserve import candidate_family
OUT=ROOT/'docs/research_notes/lushness_testbed/reserve_batch_r1'

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    base=json.loads((ROOT/'docs/research_notes/lushness_testbed/channel_extension/embodiment_shocks/embodied_reversible.json').read_text())
    laws=[('no_shock','reversible',False,'independent',0.),
          ('independent_002','reversible',True,'independent',.02),
          ('correlated_002','reversible',True,'correlated',.02),
          ('independent_004','reversible',True,'independent',.04),
          ('absorbing','absorbing',False,'independent',0.)]
    reg={'id':'reserve-batch-r1','status':'frozen_before_scientific_ranking','date':'2026-10-14',
        'primary':'complete conditional history bits at each physical horizon',
        'secondary':'rate then offset; full failure/recovery/tail retained',
        'horizons':[1,4,16,64,256],'primary_cadence':.25,'tolerance':1e-8,
        'comparison':'same fixed-law policy family; law changes explicitly distinguished',
        'adaptation_scope':'left compartment only; right capacity1 cannot resolve reserve/worn while active',
        'predictions':[
            {'id':'A1','type':'strict_nonconstant_gain','laws':['independent_002','correlated_002','independent_004'],'per':'each horizon','meaning':'a reachable nonconstant reserve/worn law strictly beats six constant controls'},
            {'id':'A2','type':'risk_service_surface','lhs':'independent_004','rhs':'independent_002','per':'each horizon','meaning':'all tied winners have no lower service on common reachable active/worn states, with some strict increase'},
            {'id':'A3','type':'correlation_service_surface','lhs':'correlated_002','rhs':'independent_002','per':'each horizon','meaning':'same pointwise service partial order as A2'},
            {'id':'A4','type':'longer_horizon_service_surface','law_scope':'five primary laws','meaning':'successive horizon winners increase service; mixed/tied sets unresolved'},
            {'id':'A5','type':'sentinel_reserve','lhs':'absorbing','rhs':'no_shock','metric':'active64','per':'each horizon winner','meaning':'absorbing winner holds more common-deadline active stock; mechanism contrast not isolated irreversibility'},
            {'id':'D1','type':'exposure_diagnostic','lhs':'independent_004','rhs':'independent_002','metric':'stationary_exposure','meaning':'increase is an alert, not an ethical failure; fixed-policy replay retained'},
            {'id':'S1','type':'fixed_pair_temporal_sign','laws':['no_shock','correlated_002'],'cadences':[.125,.25,.5],
             'comparators':['idle','service','export','best_nonrandom'],'meaning':'fixed primary winner/control identities; certified positive-negative flip is sensitivity; tie loses strict robustness'}],
        'limits':{'per_job_seconds':600,'memory_mib':1024,'output_mib':256,'numeric_threads':1,
                  'concurrent_jobs':1,'total_batch_seconds':3600},
        'selection':'Case range from draft before optimization;22declared18effective from smoke, no outcomes used to choose parameters.',
        'cases':[]}
    for law,mode,on,shock,h in laws:
        for delta in ([.125,.25,.5] if law in ('no_shock','correlated_002') else [.25]):
            case_id=f'reserve-r1-{law}-dt{delta:g}';cfg=copy.deepcopy(base)
            cfg.update(id=case_id,version='1',law_id=law,date='2026-10-14')
            cfg['world']['damage'].update(mode=mode,energy=-1)
            cfg['world']['shocks']={'enabled':on,'mode':shock,'hazard':h,'p':1.}
            cfg['controllers']={'candidates':[p.manifest() for p in candidate_family(3)],
                                'scope':'22 frozen shared active/worn threshold controllers; exact physical aliases retained'}
            cfg['measurement']['cadence']=delta
            cfg['queries']['horizons']=[1,4,16,64,256]
            cfg['queries']['common_deadline']=64.
            cfg['queries']['recovery_root']=[[1,0,0,2,0],[0,0,0,1,0]]
            cfg['queries'].pop('diagnostic_roots',None)
            cfg['analysis']={'primary':'complete conditional history bits at each horizon','rank_tolerance':1e-8,
                'residual_tolerance':1e-8,'probe_p':.5,'rule_a':'parked',
                'root_mixture':'matched reference is expected known-root conditional history entropy',
                'retention':'first entry to function followed by no later exit through64, diagnostic only'}
            cfg['limits']={'wall_seconds':600,'memory_mib':1024,'output_mib':256,'numeric_threads':1}
            cfg['registration']='docs/research_notes/lushness_testbed/reserve_batch_r1/PREREGISTRATION.json'
            cfg['calibration']='Fixed reserve2mix50worn controller capped3+1smoke20.085s482.86MiB;18unique. No ranking used.'
            cfg.pop('amendment',None)
            path=OUT/(case_id+'.json');payload=(json.dumps(cfg,sort_keys=True,separators=(',',':'))+'\n').encode()
            if path.exists() and path.read_bytes()!=payload:raise ValueError('Refuse overwrite changed frozen case')
            path.write_bytes(payload)
            reg['cases'].append({'id':case_id,'law_id':law,'cadence':delta,'file':path.name,
                                 'sha256':hashlib.sha256(payload).hexdigest()})
    path=OUT/'PREREGISTRATION.json';payload=(json.dumps(reg,indent=2)+'\n').encode()
    if path.exists() and path.read_bytes()!=payload:raise ValueError('Refuse overwrite changed registration')
    path.write_bytes(payload);print(f'Frozen{len(reg["cases"])}prospective cases:{path}')

if __name__=='__main__':prepare()
