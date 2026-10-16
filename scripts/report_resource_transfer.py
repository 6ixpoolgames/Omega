"""Verified resource and subject comparisons for the paired extraction module."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import verify_bundle
DOC=ROOT/'docs/research_notes/lushness_testbed/resource_transfer'


def paid_bank(ledger):
    # Exact signed bank flows from capture/transfer, net upkeep and conversions.
    # Thermal charge/bath support is separately exposed, not called earnings.
    return (ledger.get('net_capture_D',0)+ledger.get('transfer_D',0)
            -ledger.get('upkeep_D',0)-ledger.get('device_upkeep',0)
            -ledger.get('build_fuel_D',0)-ledger.get('device_build',0)
            +ledger.get('device_unbuild',0)-ledger.get('sham_net_bill',0))


def main():
    status=json.loads((DOC/'SURVEY_STATUS.json').read_text())
    results,configs={},{}
    maximum=0.
    for receipt in status['cases']:
        if receipt['status']!='complete':continue
        manifest=verify_bundle(Path(receipt['run']))
        if manifest['config']!=receipt['configuration']:
            raise ValueError('Configuration identity mismatch')
        data=(DOC/'cases'/(receipt['identity']+'.json')).read_bytes()
        if hashlib.sha256(data).hexdigest()!=receipt['result_sha256']:
            raise ValueError('Result identity mismatch')
        result=json.loads(data)
        if receipt['profile']['exit_code'] or receipt['profile']['cap_reason'] or not result['imports_from_snapshot']:
            raise ValueError('Incomplete or escaped-source result')
        results[receipt['id']]=result
        configs[receipt['id']]=receipt['configuration']
        residuals=[result['energy_residual'],result['stationary_residual'],*result['owned_energy_validation'].values()]
        residuals += [r['integrated_energy_residual'] for r in result['physical']['device_present'].values()]
        residuals += [r['poisson_residual'] for r in result['cadences'].values()]
        for row in result['physical']['device_present'].values():
            ledger=row['ledger']
            bath=(ledger.get('D_energy_by_family.D.charge',0)
                  +ledger.get('D_energy_by_family.D.fractional_bath',0))
            # Common device-present root has zero bank energy. This closes the
            # independently declared paid-bank account, not only owned energy.
            residuals.append(row['deadline']['D.charge']-paid_bank(ledger)-bath)
        for clock in result['cadences'].values():
            residuals.append(clock['kernel_diagnostics'].get('kernel_mass',0))
            for score in clock['profiles']['device_present'].values():
                residuals.append(score['sampled_occupation_residual'])
                for subject in ('D','S'):
                    if score['subjects'][subject]['lower_bits']>score['subjects'][subject]['upper_bits']+1e-7:
                        raise ArithmeticError('Inverted subject bounds')
        maximum=max(maximum,*map(abs,residuals))
    if maximum>1e-6:raise ArithmeticError('Resource/numerical validation envelope exceeded')
    refs={configs[k]['transfer_policy']['cost']:k for k in results
          if configs[k]['transfer_policy']['mode']=='passive'}
    rows=[]
    for key,r in results.items():
        cfg=configs[key]['transfer_policy']; cost=cfg['cost']
        if cfg['mode']=='passive' or cost not in refs:continue
        baseline=results[refs[cost]]
        for clock,p in r['cadences'].items():
            for horizon,score in p['profiles']['device_present'].items():
                b=baseline['cadences'][clock]['profiles']['device_present'][horizon]
                phys=r['physical']['device_present'][horizon]
                bp=baseline['physical']['device_present'][horizon]
                ledger,bl=phys['ledger'],bp['ledger']
                delta=lambda name:ledger.get(name,0)-bl.get(name,0)
                row={'id':key,'mode':cfg['mode'],'cost':cost,'assistance':cfg['assistance'],
                     'cadence':float(clock),'horizon':float(horizon),
                     'whole_delta':score['global_bits']-b['global_bits'],
                     'tolerance':score['global_numerical_allowance']+b['global_numerical_allowance'],
                     'rate_delta':p['limiting_rate']-baseline['cadences'][clock]['limiting_rate'],
                     'D_paid_bank_delta':paid_bank(ledger)-paid_bank(bl),
                     'D_paid_bank_rate_delta':paid_bank(r['stationary_ledger'])-paid_bank(baseline['stationary_ledger']),
                     'stationary_net_transfer_D':r['stationary_ledger'].get('transfer_D',0),
                     'D_direct_bath_delta':delta('D_energy_by_family.D.charge')+delta('D_energy_by_family.D.fractional_bath'),
                     'D_owned_energy_delta':phys['deadline']['D.owned_energy']-bp['deadline']['D.owned_energy'],
                     'S_owned_energy_delta':phys['deadline']['S.owned_energy']-bp['deadline']['S.owned_energy'],
                     'D_functional_delta':phys['average']['D.functional']-bp['average']['D.functional'],
                     'S_functional_delta':phys['average']['S.functional']-bp['average']['S.functional'],
                     'D_bank_delta':phys['deadline']['D.charge']-bp['deadline']['D.charge'],
                     'paid_bank_excludes_direct_thermal_support':True,
                     'accepted_work_delta':delta('drive_work'),
                     'delta_jumps':phys['expected_jumps']-bp['expected_jumps'],
                     'delta_finite_term':phys['finite_term_bits']-bp['finite_term_bits']}
                for name in ('transfer_D','transfer_S','extract_forward','extract_reverse',
                             'extract_gross_bill','extract_reverse_refund','net_capture_D',
                             'net_capture_S','upkeep_D','device_upkeep','build_fuel_D'):
                    row['delta_'+name]=delta(name)
                # Complete D resource decomposition, including direct bath and
                # mobility/assembly. Its sum is the owned-energy difference.
                for family in sorted({k for k in ledger.keys()|bl.keys() if k.startswith('D_energy_by_family.')}):
                    row[family]=delta(family)
                for subject in ('D','S'):
                    lo=score['subjects'][subject]['lower_bits']-b['subjects'][subject]['upper_bits']
                    hi=score['subjects'][subject]['upper_bits']-b['subjects'][subject]['lower_bits']
                    row[subject+'_lower'],row[subject+'_upper']=lo,hi
                rows.append(row)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (DOC/'COMPARISONS.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)
    text=['# Paired resource extraction: results','',
          f"Status: **{status['status']}**, {len(results)}/{status['total_cases']} cases completed and verified.",
          '', 'Finite physical-history lushness is primary. D/S intervals are certified conditioning bounds, not confidence intervals.',
          '', '## T256, cadence 0.25, relative to passive transfer at the same bill','',
          '| Mode | Bill | Strength | Whole Δ bits | D bounds | S bounds | D paid-bank Δ | D owned-energy Δ |',
          '| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |']
    for row in sorted(rows,key=lambda r:(r['cost'],r['mode'],r['assistance'])):
        if row['cadence']!=.25 or row['horizon']!=256:continue
        text.append(f"| {row['mode']} | {row['cost']:g} | {row['assistance']:g} | {row['whole_delta']:.3f} | [{row['D_lower']:.3f}, {row['D_upper']:.3f}] | [{row['S_lower']:.3f}, {row['S_upper']:.3f}] | {row['D_paid_bank_delta']:.4f} | {row['D_owned_energy_delta']:.4f} |")
    text+=['','The paid-bank account includes net native capture and transfer, subtracting net upkeep, bank-to-apparatus/device conversion and sham cost. Handling is already included in net transfer and is not subtracted twice. Direct charge-bath support is excluded and remains separately visible in the per-family account. Reverse upkeep and reverse handling are retained: this is a signed physical account, not a monetary profit or welfare score.',
           '', 'Owned energy includes stored energy, apparatus/device and trap potential. Every arm also reports the complete D/S energy-by-family sums, checked against endpoint stock changes. A stock gain, a positive paid-bank account and a breadth gain are separate outcomes. Extra accepted source work is reported; equal incoming or accepted work is not asserted.',
           '', 'The sham matches kinetic assistance, not realized fuel or activity. Ordinary/cooperative controls are currently included at bill 0.5 only. All arms retain basal extraction, cooperation and sham channels. No population, confinement, consent, suffering or defence variable is present.',
           '', 'Stationary transfer and paid-bank flow differences are in COMPARISONS.csv. These are ongoing fluxes, not unbounded growth of finite stored energy. No population or compounding claim follows from them.',
           '', f'Largest checked resource/numerical residual: {maximum:.3g}. No full transition kernels are retained.',
           '', f"Numerical source: `{status['source_hash']}`. See SPECIFICATION.md, COMPARISONS.csv, source archives and receipts."]
    (DOC/'RESULTS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    summary={'status':status['status'],'completed':len(results),'total':status['total_cases'],
             'comparisons':len(rows),'maximum_checked_residual':maximum,'source_hash':status['source_hash']}
    (DOC/'VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':main()
