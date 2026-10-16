"""Verified physical ledgers and signed marginal bounds for C5 upgrade batches."""
import argparse
import hashlib
import json
from pathlib import Path
import report_continuation_controls as shared
import archive_domination_b1_sources as archive

ROOT=Path(__file__).resolve().parents[1]
shared.BASE=ROOT/'docs/research_notes/lushness_testbed/c5_upgrade'

def main(study):
    doc,status,results,configs,maximum=shared.load(study)
    rows=[];physical=[]
    for key,result in results.items():
        cfg=configs[key]
        if study=='supplied-pump':reference='passive'
        elif study in ('pump','loss'):
            reference='passive-loss'+format(cfg['extension']['irreversible_loss'],'g')
        elif study=='opportunity':
            reference='source'+format(cfg['extension']['local_source'],'g')+'-field0'
        elif study=='cost-boundary':reference='passive-bill'+format(cfg['transfer_policy']['cost'],'g')
        else:reference='idle'
        if reference not in results:continue
        base=results[reference]
        group=shared.difference(key,result,base,{'reference':reference})
        for row in group:
            c=result['cadences'][str(row['cadence'])]
            b=base['cadences'][str(row['cadence'])]
            for subject in ('D','S'):
                if 'subject_rate_bounds' in c and 'subject_rate_bounds' in b:
                    bounds=c['subject_rate_bounds'][subject];bb=b['subject_rate_bounds'][subject]
                    row[subject+'_rate_lower']=bounds['lower_bits_per_time']-bb['upper_bits_per_time']
                    row[subject+'_rate_upper']=bounds['upper_bits_per_time']-bb['lower_bits_per_time']
                    if result is base:row[subject+'_rate_lower']=row[subject+'_rate_upper']=0.
            p=result['physical']['device_present'][str(int(row['horizon']))]
            bp=base['physical']['device_present'][str(int(row['horizon']))]
            for k in ('D.owned_energy','S.owned_energy','S.access_device','S.lost_material'):
                if k in p['deadline']:row['delta_deadline_'+k]=p['deadline'][k]-bp['deadline'][k]
        rows+=group
        for h,p in result['physical']['device_present'].items():
            physical.append({'id':key,'horizon':float(h),'states':result['states'],
                'expected_jumps':p['expected_jumps'],'fine_time_finite_bits':p['finite_term_bits'],
                **{'ledger.'+k:v for k,v in p['ledger'].items()},
                **{'deadline.'+k:v for k,v in p['deadline'].items()},
                **{'average.'+k:v for k,v in p['average'].items()},
                **{'first_passage.'+k:v for k,v in p['first_passage'].items()}})
    shared.write_csv(doc/'COMPARISONS.csv',rows)
    shared.write_csv(doc/'PHYSICAL.csv',physical)
    focus=[r for r in rows if r['cadence']==.25 and r['horizon']==256]
    lines=[f'# C5 {study}: results','',f"Status: **{status['status']}**; {len(results)}/{status['total_cases']} cases verified.",'',
        'Finite sampled-history lushness is primary. D/S intervals bound marginal histories; unresolved intervals are not midpoint rankings.',
        'Random activity, transport reversals, thermal assembly and background events all count. Work and realized activity are not automatically matched.',
        '', '## T256 at cadence 0.25', '',
        '| Case | Reference | Whole Δ bits | D difference interval | S difference interval | Full rate Δ |',
        '| --- | --- | ---: | --- | --- | ---: |']
    for r in focus:
        lines.append(f"| {r['id']} | {r['reference']} | {r['whole_delta']:+.5f} | [{r['D_lower']:+.5f}, {r['D_upper']:+.5f}] | [{r['S_lower']:+.5f}, {r['S_upper']:+.5f}] | {r['rate_delta']:+.6f} |")
    lines+=['','## Physical mechanism at T256','']
    if study in ('pump','loss','supplied-pump'):
        lines+=['| Case | Net D transport | Net fuel charging bill | D owned energy | S owned energy | S function, time mean | Permanent loss probability |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
        for p in physical:
            if p['horizon']!=256:continue
            lines.append(f"| {p['id']} | {p.get('ledger.pump_transport_D',0):+.6f} | {p.get('ledger.pump_charging_net_bill',0):+.6f} | {p['deadline.D.owned_energy']:.6f} | {p['deadline.S.owned_energy']:.6f} | {p['average.S.functional']:.6f} | {p.get('deadline.S.lost_material',0):.6f} |")
        lines+=['','Transport and charging are signed net quantities; reverse events and refunds remain in the full ledger. A mode name alone does not certify profit or help.']
        lines+=['','## Stationary flow and marginal-rate bounds at cadence 0.25','',
                '| Case | D transport / time | Fuel charging bill / time | D history rate bounds | S history rate bounds |',
                '| --- | ---: | ---: | --- | --- |']
        for key,r in results.items():
            ledger=r['stationary_ledger'];rates=r['cadences']['0.25']['subject_rate_bounds']
            d,s=rates['D'],rates['S']
            lines.append(f"| {key} | {ledger.get('pump_transport_D',0):+.9f} | {ledger.get('pump_charging_net_bill',0):+.9f} | [{d['lower_bits_per_time']:.6f}, {d['upper_bits_per_time']:.6f}] | [{s['lower_bits_per_time']:.6f}, {s['upper_bits_per_time']:.6f}] |")
        lines+=['','Stationary flow can differ in direction from a finite cumulative flow. Marginal-rate intervals are hidden-Markov conditioning bounds in bits/time, not full-field rates or projected Markov estimates.']
    if study in ('opportunity','opportunity-active'):
        lines+=['| Case | Paid builds | Reverse builds | Thermal builds | Thermal losses | Access capture net | Upkeep net | Device at deadline | Device first arrival |',
                '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for p in physical:
            if p['horizon']!=256:continue
            gross=p.get('ledger.access.thermal_assembly',0);net=p.get('ledger.S_energy_by_family.access.thermal_assembly',0)
            lines.append(f"| {p['id']} | {p.get('ledger.access_build_forward',0):.5f} | {p.get('ledger.access_build_reverse',0):.5f} | {(gross+net)/2:.5f} | {(gross-net)/2:.5f} | {p.get('ledger.access_capture_net',0):+.5f} | {p.get('ledger.access_upkeep_net',0):+.5f} | {p['deadline.S.access_device']:.5f} | {p['first_passage.S.access_device']:.5f} |")
        lines+=['','An independent packet source is present in every comparison arm. Source work is recorded in PHYSICAL.csv. Thermal births/losses follow from the gross thermal-event count and its signed unit device-energy change. The device is a passive coarse access structure with reversible construction, thermal assembly and bank-exchange overhead; paid builds do not certify exclusive ancestry of its capture.']
    if study in ('audit-controls','cost-boundary'):
        lines+=['| Case | D owned energy | S owned energy | Physical bill | Net receiver transfer | D time-mean function | S time-mean function |',
                '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
        for p in physical:
            if p['horizon']!=256:continue
            bill=p.get('ledger.extract_net_bill',0) if study=='cost-boundary' else p.get('ledger.friction_fuel',0)
            lines.append(f"| {p['id']} | {p['deadline.D.owned_energy']:.6f} | {p['deadline.S.owned_energy']:.6f} | {bill:.6f} | {p.get('ledger.transfer_D',0):+.6f} | {p['average.D.functional']:.6f} | {p['average.S.functional']:.6f} |")
        lines+=['','Owned-energy columns are endpoint stocks. Per-family integrated changes independently close against them; source capture minus intervention bill is not substituted for that full balance. The driven-debit and ordinary apparatus arms use their declared physical mechanisms, not equal realized fuel or activity.']
        if study=='cost-boundary':lines+=['Physical bill is signed receiver-path handling loss minus reverse refunds; net receiver transfer includes the transfer module\'s bank changes. At bill one the forward receiver pathway gives D zero net bank increment; above one it debits D as well as S. These are boundary probes, not necessarily material appropriation.']
    lines+=['','## Verification and scope','',f'Maximum checked numerical/resource residual: {maximum:.3g}.',
        'COMPARISONS.csv retains every tested horizon and cadence, expected-jump and fine-time differences, and marginal-rate difference bounds where available. PHYSICAL.csv retains full signed energy and event ledgers.',
        'The destination-surprisal diagnostic is not entropy of the entire random-length jump history. No continuous-time invariant scalar is inferred from three cadences.',
        f"Frozen numerical source: `{status['source_hash']}`. Receipts verify imports, configurations, checksums and caps.",'']
    if study=='loss':
        lines+=['The permanent sink removes S apparatus capability; S movement, banks and the environmental process continue. Residual history rates describe those surviving processes, not preservation of the lost capability.',
            'Lower loss probability can arise from less time with vulnerable apparatus. Read it alongside functional uptime; it is not by itself evidence of stronger protection.','']
    (doc/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    validation={'status':status['status'],'verified_cases':len(results),'planned_cases':status['total_cases'],
        'source_hash':status['source_hash'],'maximum_checked_residual':maximum,
        'receipts_and_caps_verified':True,'source_imports_verified':True,
        'comparison_sha256':hashlib.sha256((doc/'COMPARISONS.csv').read_bytes()).hexdigest(),
        'physical_sha256':hashlib.sha256((doc/'PHYSICAL.csv').read_bytes()).hexdigest()}
    (doc/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    archive.DOC=doc;archive.LOCAL=ROOT/'results/local_runs/lushness_testbed'/('c5_upgrade_'+study)
    archive.main()
    print(json.dumps({'study':study,'cases':len(results),'comparisons':len(rows),'residual':maximum}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('study')
    main(parser.parse_args().study)
