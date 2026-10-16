"""Verified signed maps for corrected steering and matched transfer controls."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import verify_bundle
BASE=ROOT/'docs/research_notes/lushness_testbed/continuation_controls'


def write_csv(path,rows):
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)


def load(study):
    doc=BASE/study;status=json.loads((doc/'SURVEY_STATUS.json').read_text())
    results,configs={},{}
    maximum=0.
    for receipt in status['cases']:
        if receipt['status']!='complete':continue
        m=verify_bundle(Path(receipt['run']))
        if m['config']!=receipt['configuration'] or receipt['profile']['cap_reason'] or receipt['profile']['exit_code']:
            raise ValueError('Run receipt/configuration mismatch')
        payload=(doc/'cases'/(receipt['identity']+'.json')).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=receipt['result_sha256']:raise ValueError('Output checksum mismatch')
        r=json.loads(payload)
        if not r['imports_from_snapshot']:raise ValueError('Import source escaped snapshot')
        results[receipt['id']]=r;configs[receipt['id']]=receipt['configuration']
        errors=[r['energy_residual'],r.get('stationary_residual',0),*r.get('owned_energy_validation',{}).values()]
        errors.extend(x['integrated_energy_residual'] for x in r['physical']['device_present'].values())
        for clock in r['cadences'].values():
            errors.extend([clock['poisson_residual'],clock['kernel_diagnostics'].get('kernel_mass',0)])
            for score in clock['profiles']['device_present'].values():
                errors.append(score['sampled_occupation_residual'])
                if any(v['lower_bits']>v['upper_bits']+1e-7 for v in score['subjects'].values()):
                    raise ArithmeticError('Inverted subject bounds')
        maximum=max(maximum,*map(abs,errors))
    if maximum>1e-6:raise ArithmeticError('Numerical/resource envelope exceeded')
    return doc,status,results,configs,maximum


def difference(key,r,b,extra):
    rows=[]
    for clock,c in r['cadences'].items():
        for horizon,s in c['profiles']['device_present'].items():
            ref=b['cadences'][clock]['profiles']['device_present'][horizon]
            p=r['physical']['device_present'][horizon];bp=b['physical']['device_present'][horizon]
            row={'id':key,**extra,'cadence':float(clock),'horizon':float(horizon),
                 'whole_delta':s['global_bits']-ref['global_bits'],
                 'tolerance':s['global_numerical_allowance']+ref['global_numerical_allowance'],
                 'rate_delta':c['limiting_rate']-b['cadences'][clock]['limiting_rate'],
                 'delta_jumps':p['expected_jumps']-bp['expected_jumps'],
                 'delta_finite_term':p['finite_term_bits']-bp['finite_term_bits'],
                 'delta_S_capture':p['ledger'].get('net_capture_S',0)-bp['ledger'].get('net_capture_S',0),
                 'delta_total_work':p['ledger']['drive_work']-bp['ledger']['drive_work'],
                 'delta_boundary_work':p['ledger'].get('transfer_boundary_work',0)-bp['ledger'].get('transfer_boundary_work',0),
                 'delta_S_function':p['average']['S.functional']-bp['average']['S.functional'],
                 'delta_pocket_arrival':p['first_passage'].get('S.discovered',0)-bp['first_passage'].get('S.discovered',0),
                 'delta_pocket_residence':p['average']['S.discovered']-bp['average']['S.discovered']}
            for subject in ('D','S'):
                lo=s['subjects'][subject]['lower_bits']-ref['subjects'][subject]['upper_bits']
                hi=s['subjects'][subject]['upper_bits']-ref['subjects'][subject]['lower_bits']
                row[subject+'_lower']=lo if r is not b else 0.
                row[subject+'_upper']=hi if r is not b else 0.
            value=row['whole_delta'];eps=row['tolerance']
            row['whole_sign']='positive' if value>eps else 'negative' if value< -eps else 'unresolved'
            rows.append(row)
    return rows


def main(study):
    doc,status,results,configs,maximum=load(study)
    rows=[];matching=[];contrasts=[]
    text=[f'# {"Corrected movement steering" if study=="steering" else "Matched transfer flow"}: results','',
          f"Status: **{status['status']}**, {len(results)}/{status['total_cases']} cases verified.",'',
          'Finite sampled-history lushness is primary. Subject intervals are conditioning bounds. No random events are subtracted.','']
    if study=='steering':
        refs={c['parameters']['opportunity_yield']:key for key,c in configs.items() if c['policy']['phi']==0}
        for key,r in results.items():
            cfg=configs[key];y=cfg['parameters']['opportunity_yield'];policy=cfg['policy']
            if policy['phi']==0 or y not in refs:continue
            rows+=difference(key,r,results[refs[y]],{'yield':y,'mode':policy['mode'],'strength':policy['phi']})
        text+=['## T256, cadence 0.25, relative to idle','',
               '| Yield | Mode | Strength | Whole Δ | S bounds | Pocket arrival Δ | S net capture Δ |',
               '| ---: | --- | ---: | ---: | --- | ---: | ---: |']
        for r in sorted(rows,key=lambda r:(r['yield'],r['mode'],r['strength'])):
            if r['cadence']==.25 and r['horizon']==256:
                text.append(f"| {r['yield']:g} | {r['mode']} | {r['strength']:g} | {r['whole_delta']:.4f} | [{r['S_lower']:.4f}, {r['S_upper']:.4f}] | {r['delta_pocket_arrival']:.4f} | {r['delta_S_capture']:.4f} |")
        # Adjacent yield sign brackets: no interpolation presented as a root.
        for mode,strength in (('steering',.55),('steering',.95),('blocking',.95)):
            for cadence in (.125,.25,.5):
                for horizon in (16.,64.,256.,1024.):
                    group=sorted([r for r in rows if r['mode']==mode and r['strength']==strength and r['cadence']==cadence and r['horizon']==horizon],key=lambda r:r['yield'])
                    for a,b in zip(group,group[1:]):
                        if {a['whole_sign'],b['whole_sign']}=={'positive','negative'}:
                            contrasts.append({'mode':mode,'strength':strength,'cadence':cadence,'horizon':horizon,
                                'yield_lower':a['yield'],'yield_upper':b['yield'],
                                'delta_lower':a['whole_delta'],'delta_upper':b['whole_delta']})
        write_csv(doc/'SIGN_BRACKETS.csv',contrasts)
        text+=['',f'Adjacent tested-yield sign brackets: **{len(contrasts)}** (mode × strength × clock × horizon; not independent trials).',
               '', 'Only movement is redirected. Native chemistry and pocket-to-trap return retain their rates at the same physical state. Active steering is still the original coarse driven boundary, not the paired transfer chemistry. The declared half-unit energy grid differs from the old tenth-unit map. No claim extends beyond the tested yield range or clocks.']
    else:
        refs={c['matching']['fraction']:key for key,c in configs.items() if c['matching']['zero_net']}
        text+=['## Physical matching at T256','',
               '| Point | Affinity | Assistance | Gross F+R | Net F−R | Boundary work |',
               '| --- | ---: | ---: | ---: | ---: | ---: |']
        for key,r in results.items():
            cfg=configs[key];m=cfg['matching'];p=cfg['transfer_policy']
            ledger=r['physical']['device_present']['256']['ledger']
            forward,reverse=ledger['extract_forward'],ledger['extract_reverse']
            gross,net=forward+reverse,forward-reverse
            error=abs(gross-m['target_gross'])
            if error>2e-5 or (m['zero_net'] and abs(net)>2e-5):raise ArithmeticError('Science run does not meet physical flux match')
            matching.append({'id':key,**m,'gross':gross,'net':net,'gross_error':error,
                             'affinity':p['affinity'],'assistance':p['assistance'],
                             'boundary_work':ledger['transfer_boundary_work'],
                             'total_work':ledger['drive_work'],'native_source_input':2*ledger['source'],
                             'all_channels_net_transfer_D':ledger['transfer_D'],
                             'all_channels_net_transfer_S':ledger['transfer_S'],
                             'basal_cooperation_net':ledger['cooperate_forward']-ledger['cooperate_reverse']})
            text.append(f"| {key} | {p['affinity']:.5f} | {p['assistance']:.5f} | {gross:.6f} | {net:.6f} | {ledger['transfer_boundary_work']:.6f} |")
            if m['fraction'] in refs:
                rows+=difference(key,r,results[refs[m['fraction']]],{'fraction':m['fraction'],
                                 'affinity':p['affinity'],'assistance':p['assistance'],'net_at_T256':net,
                                 'gross_at_T256':gross,'zero_net_reference':refs[m['fraction']]})
        if len(refs)==2:
            lo,hi=sorted(refs)
            contrasts=difference('high-zero-minus-low-zero',results[refs[hi]],results[refs[lo]],{'comparison':'turnover at net zero; matching applies at T256 only'})
        write_csv(doc/'MATCHING.csv',matching);write_csv(doc/'ZERO_NET_TURNOVER.csv',contrasts)
        text+=['','## T256, cadence 0.25, relative to matched-gross zero-net point','',
               '| Point | Whole Δ bits | D bounds | S bounds | Total world jumps Δ |',
               '| --- | ---: | --- | --- | ---: |']
        for r in rows:
            if r['cadence']==.25 and r['horizon']==256:
                text.append(f"| {r['id']} | {r['whole_delta']:.5f} | [{r['D_lower']:.5f}, {r['D_upper']:.5f}] | [{r['S_lower']:.5f}, {r['S_upper']:.5f}] | {r['delta_jumps']:.5f} |")
        text+=['','Gross extraction-pair exchange is matched at T256 only. Total world activity, work input, thermal flux and entropy are not matched. The affinity is an explicit additional external work boundary; comparisons are not equal-work or D-funded policy choices. The two zero-net points compare extraction-pair volume at zero net flow in that pair. Small basal cooperation flows remain: MATCHING.csv also gives total transfers across all channels. At other horizons net flows need not be zero. This control does not assign a unique entropy contribution to taking or erase the original unmatched rankings.']
    write_csv(doc/'COMPARISONS.csv',rows)
    text+=['',f'Largest checked numerical/resource residual: {maximum:.3g}.',
           '',f"Numerical source: `{status['source_hash']}`. Exact source, configurations and receipts are retained; no full kernels are stored."]
    (doc/'RESULTS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    summary={'status':status['status'],'completed':len(results),'total':status['total_cases'],
             'comparisons':len(rows),'maximum_checked_residual':maximum,
             'sign_brackets':len(contrasts) if study=='steering' else None,'source_hash':status['source_hash']}
    (doc/'VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('study',choices=['steering','flow'])
    main(parser.parse_args().study)
