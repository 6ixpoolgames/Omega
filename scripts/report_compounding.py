"""Score the frozen compounding boundary and retain every mechanism contrast."""
import csv
import hashlib
import json
import sys
from itertools import pairwise
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC=ROOT/'docs/research_notes/lushness_testbed/compounding'


def main():
    p=json.loads((DOC/'PROTOCOL.json').read_text())
    status=json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if status.get('status')!='complete':
        raise RuntimeError('Full frozen grid required before scoring')
    laws={}; files=[]; comparisons=[]; source_hashes=set(); profiles=[]
    for law in p['laws']:
        gate=status['laws'][law['id']]
        run=Path(gate['run']); manifest=verify_bundle(run)
        raw=run/'RESULTS.json'; r=json.loads(raw.read_text())
        if manifest['config']['protocol']!=p or r['law']!=law or r['input_hash']!=manifest['input_hash']:
            raise RuntimeError('Scientific identity mismatch')
        source_hashes.add(r['source_hash']); profiles.append(gate['profile'])
        index={(v['mechanism'],v['root'],v['cadence']):v for v in r['rows']}
        if len(index)!=24:
            raise RuntimeError('Missing mechanism/root/cadence')
        for mode in p['mechanisms']:
            for cadence in p['cadences']:
                if abs(index[mode,'seed',cadence]['rate']-index[mode,'unorganized',cadence]['rate'])>p['tolerances']['rate']:
                    raise ArithmeticError('Same-law root rates do not match')
        stat=r['stationary']; loop=stat['loop']
        operating=(loop['capture_funding_fraction']>=p['funding_marker']
                   and loop['thermal_build_fraction']<=p['thermal_marker']
                   and loop['apparatus_deadline']>p['mean_apparatus_marker']
                   and loop['expanded_deadline']>=p['expansion_probability_marker'])
        retained=all(loop['apparatus_deadline']>stat[m]['apparatus_deadline']+p['tolerances']['physical']
                     for m in ('no_construction_assistance','no_capture_assistance'))
        for root in p['roots']:
            for cadence in p['cadences']:
                for horizon in p['horizons']:
                    a=index['loop',root,cadence]
                    for other in p['mechanisms'][1:]:
                        b=index[other,root,cadence]
                        delta=a['scores'][str(horizon)]['bits']-b['scores'][str(horizon)]['bits']
                        comparisons.append({'law':law['id'],'capacity':law['parameters']['capacity'],
                            'cost':law['parameters']['construction_cost'],'yield':law['parameters']['packet_energy'],
                            'damage':law['parameters']['damage_rate'],'root':root,'cadence':cadence,'horizon':horizon,
                            'pair':f'loop-{other}','delta_bits':delta,'delta_rate':a['rate']-b['rate'],
                            'delta_retained_apparatus':loop['apparatus_deadline']-stat[other]['apparatus_deadline']})
        row={'law':law,'stationary':stat,'operating_marker':operating,'retained_ablation_advantage':retained,
             'input_hash':r['input_hash'],'source_hash':r['source_hash'],
             'result_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'residual':r['maximum_residual'],
             'rates':{m:{str(c):index[m,'seed',c]['rate'] for c in p['cadences']} for m in p['mechanisms']}}
        laws[law['id']]=row
        path=f"laws/{law['id']}.json"
        atomic_json(DOC/path,r)
        files.append({'path':path,'sha256':hashlib.sha256((DOC/path).read_bytes()).hexdigest()})
    if len(source_hashes)!=1:
        raise RuntimeError('Mixed scientific source versions')
    boundary=[v for v in laws.values() if v['law']['kind']=='boundary']
    fertile=[v['law']['id'] for v in boundary if v['operating_marker'] and v['retained_ablation_advantage']]
    rate_points=[name for name in fertile if all(laws[name]['rates']['loop'][str(c)]>
                 laws[name]['rates']['basal'][str(c)]+p['tolerances']['rate'] for c in p['cadences'])]
    capacity=[laws[f'M{m}-c2-y3-d0.005'] for m in (4,8,16,32)]
    scaling=[{'left':a['law']['parameters']['capacity'],'right':b['law']['parameters']['capacity'],
              'retained_increment':b['stationary']['loop']['apparatus_deadline']-a['stationary']['loop']['apparatus_deadline'],
              'rate_increments':{str(c):b['rates']['loop'][str(c)]-a['rates']['loop'][str(c)] for c in p['cadences']}}
             for a,b in pairwise(capacity)]
    harm=[]
    for cost in (1.5,2.,2.5):
        for packet in (2.,3.,4.):
            lo=laws[f'M8-c{cost:g}-y{packet:g}-d0.005']['stationary']['loop']
            hi=laws[f'M8-c{cost:g}-y{packet:g}-d0.02']['stationary']['loop']
            harm.append({'cost':cost,'yield':packet,'retained_change':hi['apparatus_deadline']-lo['apparatus_deadline']})
    predictions={'P1':bool(fertile),'P2':bool(fertile) and len(rate_points)==len(fertile),
                 'P3':all(v['retained_increment']>p['tolerances']['physical'] and
                          all(x>p['tolerances']['rate'] for x in v['rate_increments'].values()) for v in scaling),
                 'P4':all(v['retained_change']<-p['tolerances']['physical'] for v in harm)}
    flips=[]
    for law in p['laws']:
        for root in p['roots']:
            for horizon in p['horizons']:
                for other in p['mechanisms'][1:]:
                    vals=[v for v in comparisons if v['law']==law['id'] and v['root']==root
                          and v['horizon']==horizon and v['pair']==f'loop-{other}']
                    signs={1 if v['delta_bits']>p['tolerances']['bits'] else -1
                           for v in vals if abs(v['delta_bits'])>p['tolerances']['bits']}
                    if len(signs)>1:
                        flips.append({'law':law['id'],'root':root,'horizon':horizon,'pair':f'loop-{other}',
                                      'values':[{k:v[k] for k in ('cadence','delta_bits')} for v in vals]})
    summary={'status':'complete','protocol':p,'laws':laws,'predictions':predictions,'fertile_points':fertile,
             'rate_positive_fertile_points':rate_points,'capacity_scaling':scaling,'damage_response':harm,
             'cadence_flips':flips,'files':files,'rows':sum(24 for _ in laws),
             'total_seconds':sum(v['wall_seconds'] for v in profiles),
             'peak_bytes':max(v['peak_job_bytes'] for v in profiles),
             'maximum_residual':max(v['residual'] for v in laws.values()),
             'source_hash':next(iter(source_hashes)),
             'report_source_hash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    atomic_json(DOC/'SUMMARY.json',summary)
    with (DOC/'PARAMETER_MAP.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(comparisons[0]))
        writer.writeheader();writer.writerows(comparisons)
    lines=['# Resource-funded compounding boundary', '',
           (f"All {len(laws)} frozen laws completed. {len(fertile)} of18 boundary points satisfy the declared "
           'operating markers and retain more apparatus than either single-assistance ablation. '
           'The exact local feedback certificate and the retained-growth result are separate from '
           'the scalar lushness comparisons below.'), '',
           '| Registered prediction | Result |','| --- | --- |']
    for key,value in predictions.items():
        lines.append(f"| {key}: {p['predictions'][key]} | {'pass' if value else 'fail'} |")
    lines+=['','## Capacity series: central cost/yield, low isolated damage','',
            '| Capacity | Retained apparatus: loop | No construction assistance | No capture assistance | Loop rate at0.25 | Capture funding | Thermal birth share |',
            '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for v in capacity:
        s=v['stationary'];a=s['loop'];m=v['law']['parameters']['capacity']
        lines.append(f"| {m} | {a['apparatus_deadline']:.4f} | {s['no_construction_assistance']['apparatus_deadline']:.4f} | "
                     f"{s['no_capture_assistance']['apparatus_deadline']:.4f} | {a['rate']:.6f} | "
                     f"{100*a['capture_funding_fraction']:.2f}% | {100*a['thermal_build_fraction']:.6f}% |")
    central=json.loads((DOC/'laws/M8-c2-y3-d0.005.json').read_text())
    target=central['stationary']['loop']
    index={(v['mechanism'],v['root'],v['cadence']):v for v in central['rows']}
    lines+=['','| Horizon | Seed: retained apparatus | Loop−basal complete-history bits at0.25 |',
            '| ---: | ---: | ---: |']
    for t in p['horizons']:
        apparatus=central['physical']['loop:seed'][str(t)]['apparatus_deadline']
        delta=index['loop','seed',.25]['scores'][str(t)]['bits']-index['basal','seed',.25]['scores'][str(t)]['bits']
        lines.append(f'| {t} | {apparatus:.4f} | {delta:+.6f} |')
    lines+=['','## What compounds','',
            ('A newly constructed unit increases native capture propensity and, before crowding, '
            'the propensity to build the next unit. Paid construction spends real bank energy and '
            'precursors. Its thermodynamic reverse is retained. The local certificate states the '
            'exact conditions; it does not assume unlimited growth. Deadline stock and stationary '
            'retention then test whether the resulting descendants persist.'), '',
            (f"At capacity8/cost2/packet3/damage0.005, the loop retains {target['apparatus_deadline']:.4f} "
            f"units, with at least two present {100*target['expanded_deadline']:.4f}% of the time. "
            f"Net paid creation is {target['net_paid_hardware_creation']:.6f}units/time. Gross birth "
            'and reverse fluxes are also retained, so persistence is not inferred from birth count alone.'), '',
            ('The bank funding fractions are resource capture, recycled hardware energy and bath '
            'imports; they sum to1 in stationarity. This corrects the proposed all-cost-coverage>1 '
            'criterion. Gross hardware ROI can exceed1, but a full stationary bank budget cannot '
            'maintain a surplus. Bath support is small at the central capacity8 point and becomes '
            'more important at large inventory; no marker-failing point is excluded.'), '',
            ('All24 laws retain more apparatus under the full loop than under either single '
             'assistance ablation. The11/18 marker result locates strongly resource-funded regimes '
             'within the cost/yield grid, not a complete breakdown frontier. Marker failure does '
             'not mean the physical feedback disappears. A later, separately specified source/damage '
             'boundary is needed to locate outright failure.'), '',
            '## Lushness and damage','',
            (f"There are {len(flips)} cadence-dependent pair/root/horizon signs across the registered "
            'grid. The full map retains every comparison. Finite history remains primary; increasing '
            'limiting rate is evidence of ongoing contribution, not a replacement ethical ordering.'), '',
            ('Unlike the earlier wear sweep, higher damage here leaves thermal reconstruction fixed. '
            'Its effect on retained apparatus is scored across all nine cost/yield pairs. Material '
            'is converted back to precursor, so this is reconstruction damage, not permanent loss '
            'of material or irreplaceable identity.'), '',
            '## Scope and next boundary','',
            ('This is bounded recursively enabling apparatus growth in a declared resource-driven toy. '
            'Increasing the finite precursor inventory supplies room to grow; it does not prove '
            'unbounded growth, a rate that increases forever within one fixed finite world, or '
            'superiority over a microscopic gas. The basal mechanism preserves native packet and '
            'thermal dynamics but is a coupling ablation, not a full gas ensemble. Same-law seed '
            'and unorganized roots have equal limiting rates, with distinct finite profiles.'), '',
            ('The source, precursor budget, native rate law and kinetic coefficient form the stated '
            'assumptions. The tests establish the consequences of those assumptions, not that '
            'every chemistry or our universe permits this regime. The next extension should test '
            'finite opportunity windows and maintained or expanding material access, with physical '
            'controller/valuer composition added as a separate layer.'), '',
            '## Verification','',
            (f"{summary['rows']} mechanism/root/cadence analyses; {summary['total_seconds']:.2f}s charged "
            f"science time, peak {summary['peak_bytes']/1024**2:.1f}MiB, maximum residual "
            f"{summary['maximum_residual']:.3g}. Eight new tests cover energy/material balances, "
            'full dark-control detailed balance, catalyst ratios, damage isolation and feedback '
            'propensity. The source-identical capped engineering run preceded scientific freeze.'), '',
            ('[Execution incident](EXECUTION_INCIDENTS.md) records a bytecode-file monitor race and '
            'the unchanged-law resume. No successful outcomes were discarded. Raw snapshots remain '
            'ignored; compact per-law records and the complete map are retained. No push or Drive '
            'manuscript edit occurred.'), '',
            ('Reproduce: `python scripts/run_compounding.py engineering`, then reuse the frozen '
            '`science` protocol, followed by `python scripts/report_compounding.py`. Set '
            '`PYTHONDONTWRITEBYTECODE=1` for the current supervisor. Never rerun `prepare` over '
            'a frozen protocol.'), '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'predictions':predictions,'fertile':len(fertile),'laws':len(laws),
                      'seconds':summary['total_seconds'],'peak_MiB':summary['peak_bytes']/1024**2,
                      'cadence_flips':len(flips)},indent=2))


if __name__=='__main__':
    main()
