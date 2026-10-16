"""Verified compact reports for the follow-up and expanded discovery worlds."""
import csv
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.analysis.observed_history import interval_comparison
from omega_v2.testbed.analysis.temporal_profile import crossover
DOC = ROOT/'docs/research_notes/lushness_testbed/domination_b1'


def load(mode):
    status = json.loads((DOC/(mode.upper()+'_STATUS.json')).read_text())
    results, configs = {}, {}
    for receipt in status['cases']:
        if receipt['status'] != 'complete':
            continue
        path = DOC/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['result_sha256']:
            raise RuntimeError('Compact result hash mismatch')
        result = json.loads(path.read_text())
        if not result['imports_from_snapshot']:
            raise RuntimeError('Worker import verification missing')
        results[receipt['id']] = result
        configs[receipt['id']] = receipt['configuration']
    return status, results, configs


def csv_write(name, rows):
    if not rows:
        return
    with (DOC/name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)


def comparison(a, b, cadence, time):
    aa, bb = (r['cadences'][cadence]['profiles']['device_present'][time] for r in (a,b))
    pa, pb = (r['physical']['device_present'][time] for r in (a,b))
    row = {'cadence': float(cadence), 'horizon': float(time),
           'global_delta': aa['global_bits']-bb['global_bits'],
           'tolerance': 1e-5+aa['global_numerical_allowance']+bb['global_numerical_allowance']}
    for subject in ('D', 'S'):
        row.update({subject+'_'+key: value for key,value in interval_comparison(
            aa['subjects'][subject], bb['subjects'][subject], row['tolerance']).items()})
    row.update(rate_delta=a['cadences'][cadence]['limiting_rate']-b['cadences'][cadence]['limiting_rate'],
               delta_jumps=pa['expected_jumps']-pb['expected_jumps'],
               delta_finite_term=pa['finite_term_bits']-pb['finite_term_bits'])
    temporal = crossover(pa, pb)
    row['estimated_temporal_crossover'] = temporal['estimated_cadence']
    row['temporal_crossover_status'] = temporal['status']
    row['temporal_crossover_is_asymptotic_not_exact'] = True
    for key in ('net_capture_D','net_capture_S','friction_fuel','accepted_work','bath_heat','discovery_fuel','discoveries_paid'):
        row['delta_'+key] = pa['ledger'].get(key,0)-pb['ledger'].get(key,0)
    for key in ('S.discovered', 'S.trap', 'S.functional', 'D.charge'):
        row['mean_'+key] = pa['average'][key]
        row['delta_mean_'+key] = pa['average'][key]-pb['average'][key]
    row['p_discovered'] = pa['first_passage'].get('S.discovered',0)
    row['delta_p_discovered'] = row['p_discovered']-pb['first_passage'].get('S.discovered',0)
    row['pocket_at_deadline'] = pa['deadline']['S.discovered']
    row['capture_gain_minus_friction_bill'] = row['delta_net_capture_D']-row['delta_friction_fuel']
    row['capture_minus_bill_is_full_energy_profit'] = False
    return row


def followup():
    status, results, configs = load('followup')
    rows, attribution = [], []
    for env in ('s0.04-k0','s0.12-k0','s0.12-k1'):
        baseline = results[env+'-idle']
        for mode in ('ordinary', 'blocking', 'sham'):
            r = results[env+'-'+mode]
            for dt, clock in r['cadences'].items():
                for time in clock['profiles']['device_present']:
                    rows.append({'environment': env, 'arm': mode, 'reference': 'idle', **comparison(r, baseline, dt, time)})
        for dt in baseline['cadences']:
            for time in baseline['cadences'][dt]['profiles']['device_present']:
                rows.append({'environment': env, 'arm': 'blocking', 'reference': 'sham',
                             **comparison(results[env+'-blocking'],results[env+'-sham'],dt,time)})
                rows.append({'environment': env, 'arm': 'ordinary', 'reference': 'blocking',
                             **comparison(results[env+'-ordinary'],results[env+'-blocking'],dt,time)})
        for mode in ('idle','ordinary','blocking','sham'):
            for time, physical in results[env+'-'+mode]['physical']['device_present'].items():
                for family, values in physical['D_native_attribution']['families'].items():
                    attribution.append({'environment': env, 'arm': mode, 'horizon': float(time),
                                        'family': family, **values})
    csv_write('FOLLOWUP_MAP.csv',rows)
    csv_write('D_NATIVE_ATTRIBUTION.csv',attribution)
    focus = [r for r in rows if r['horizon']==256 and r['cadence']==.25 and r['reference']=='idle']
    lines = ['# Updated interpretation: activity controls and ordinary-agent swap', '',
             '15 October 2026. All 12 local follow-up cases completed. This adds new controls '
             'to Stage A; its original measurements and interpretation remain available.', '',
             '## Actual law swap', '',
             'Giving the auxiliary device ordinary capture capability, instead of friction capability, '
             'raises whole-field lushness and D marginal lushness at T256 in all three environments '
             'and all three cadences. The preparation and energy are unchanged. S intervals remain '
             'unresolved here. This answers the requested world/law replacement comparison; '
             'it is different from the earlier ordinary-root comparison under the idle-device law.', '',
             'The ordinary auxiliary also beats the selected access-blocking intervention on both '
             'D and whole-field breadth at T256 throughout the cadence corridor. This is not a '
             'claim that it beats every useful intervention. A private gain against idle need not '
             'be the private optimum when different productive roles are available.', '',
             'The useful-control comparison goes further. Against strong trap-entry steering '
             '(strength 0.95, bill 1), ordinary capture gives D more marginal breadth and S less '
             'at T256 in all three environments/cadences. Whole-field lushness prefers the '
             'protective intervention in both κ=0 environments at every tested cadence. At κ=1 '
             'the comparison flips: ordinary minus protective is +2.404 bits at 0.125, −0.596 '
             'at 0.25 and −2.775 at 0.5. This is a temporal-resolution dependence, not a tie. '
             'The archived default kernels and idle scores were independently replayed with '
             'zero difference; ORDINARY_VS_PROTECTIVE.csv and DEFAULT_KERNEL_BRIDGE.json '
             'record the bridge. Ordinary replacement therefore does not universally beat useful '
             'intervention. Subject conflict can arise between two productive roles as well as '
             'between restriction and idle.', '',
             '## Paid activity without restricting S', '',
             'The sham mechanism spends fuel on actual D changes at the same conditional attempt '
             'rate while leaving S native transitions intact. In supply 0.12, κ=0, it already gives '
             'D a certified T256 gain at all three cadences. Thus imposing a restriction is not '
             'necessary for the private activity benefit in this regime. The blocking world still '
             'loses whole-field lushness; the sham world gains it. Direct D blocking-versus-sham '
             'bounds overlap, so their private gains cannot be assigned a unique causal split.', '',
             '| Environment | Arm vs idle | Whole Δ bits, T256/0.25 | D interval | Net D capture Δ | Fuel bill |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for r in focus:
        lines.append(f"| {r['environment']} | {r['arm']} | {r['global_delta']:.3f} | "
                     f"[{r['D_difference_lower']:.3f}, {r['D_difference_upper']:.3f}] | "
                     f"{r['delta_net_capture_D']:.3f} | {r['delta_friction_fuel']:.3f} |")
    lines += ['', '## What the attribution means', '',
              'D_NATIVE_ATTRIBUTION.csv groups actual D destinations before allocating rates to '
              'friction/capture/other. It records expected changes, finite fine-time terms and local '
              'destination surprisal. These are conditional activity coordinates, not an additive '
              'decomposition of marginal-history lushness. For example, blocking at supply 0.12/κ=0 '
              'produces 1.526 friction-associated D changes and 4.736 capture-associated D changes '
              'by T256; forward and reverse capture both contribute to the latter. Only 0.221 '
              'additional net capture is obtained relative to idle, against 1.526 friction fuel.', '',
              'The material profit question remains open: these private gains are not net energetic '
              'returns. The fractional-bank/discovery extension tests smaller bills and changed '
              'access consequences. No result here establishes conscious valuer welfare or an '
              'optimized two-player appropriation game.', '']
    (DOC/'FOLLOWUP_INTERPRETATION.md').write_text('> **Updated interpretation, 16 October 2026:** Historical `native_events` steering may redirect into chemistry. Exit/all steering is not mobility evidence; B1 also intercepted pocket returns. See [the audit correction](../C5_AUDIT_CORRECTIONS_2026-10-16.md) before using these rows. Original numerical results are retained.\n\n'+ '\n'.join(lines),encoding='utf-8')
    return status, rows


def survey():
    status, results, configs = load('survey')
    priority_added=0
    if (DOC/'PRIORITY-COMPANION_STATUS.json').exists():
        ps,pr,pc=load('priority-companion')
        if ps['source_hash']!=status['source_hash']:
            raise RuntimeError('Priority results use a different numerical source')
        for name,result in pr.items():
            if name not in results:
                results[name]=result
                configs[name]=pc[name]
                priority_added+=1
    rows=[]
    for name,result in results.items():
        if name.endswith('-idle'):
            continue
        prefix='exclusion' if name.startswith('exclusion-access-') else name.split('-trap-',1)[0]
        if prefix+'-idle' not in results:
            continue
        base=results[prefix+'-idle']
        c=configs[name]
        for dt,clock in result['cadences'].items():
            for time in clock['profiles']['device_present']:
                rows.append({'id':name,'target':'access_entry' if name.startswith('exclusion-') else 'trap_entry',
                             'opportunity_yield':c['parameters']['opportunity_yield'],
                             'kappa':c['parameters']['kappa'],
                             'cost':c['policy']['cost'],'phi':c['policy']['phi'],
                             **comparison(result,base,dt,time)})
    csv_write('DISCOVERY_MAP.csv',rows)
    grouped=defaultdict(list)
    for row in rows:grouped[row['id'],row['horizon']].append(row)
    corridor=[]
    for (name,time),group in sorted(grouped.items()):
        if len(group)!=3:continue
        signs={1 if r['global_delta']>r['tolerance'] else -1 if r['global_delta'] < -r['tolerance'] else 0 for r in group}
        verdict='positive' if signs=={1} else 'negative' if signs=={-1} else 'mixed_or_unresolved'
        item={'id':name,'horizon':time,'global_corridor':verdict,
              'global_delta_min':min(r['global_delta'] for r in group),
              'global_delta_max':max(r['global_delta'] for r in group)}
        for subject in ('D','S'):
            values={r[subject+'_verdict'] for r in group}
            item[subject+'_corridor']='positive' if values=={'strict_positive'} else 'negative' if values=={'strict_negative'} else 'unresolved_or_mixed'
        item['D_positive_S_negative']=item['D_corridor']=='positive' and item['S_corridor']=='negative'
        item['self_whole_opposition']=item['D_corridor']=='positive' and verdict=='negative'
        corridor.append(item)
    csv_write('CORRIDOR_MAP.csv',corridor)
    choices=[]
    families={('exclusion' if name.startswith('exclusion-') else name.split('-trap-',1)[0],
               config['policy'].get('cost'))
              for name,config in configs.items() if not name.endswith('-idle')}
    # Only score a complete idle/weaker/stronger family. Partial arrivals must
    # never be mistaken for an optimized result over candidates still running.
    for prefix,cost in sorted(families):
        names=[name for name,c in configs.items() if not name.endswith('-idle')
               and name.startswith(prefix+'-') and c['policy']['cost']==cost]
        if len(names)!=2 or prefix+'-idle' not in results:continue
        names=[prefix+'-idle']+names
        if any(name not in results for name in names):continue
        for dt,clock in results[names[0]]['cadences'].items():
            for time in clock['profiles']['device_present']:
                values={name:results[name]['cadences'][dt]['profiles']['device_present'][time]
                        for name in names}
                best=max(v['global_bits'] for v in values.values())
                allowance=1e-5+2*max(v['global_numerical_allowance'] for v in values.values())
                possible=[name for name,v in values.items() if v['global_bits']>=best-allowance]
                choice={'family':prefix,'cost':cost,'cadence':float(dt),'horizon':float(time),
                    'possible_maximizers':' | '.join(possible),'unique_resolved':len(possible)==1,
                    'best_gain_over_idle_bits':best-values[names[0]]['global_bits'],
                    'numerical_allowance':allowance,'complete_candidate_family':True,
                    'objective':'complete finite sampled-history lushness'}
                for subject in ('D','S'):
                    intervals={name:v['subjects'][subject] for name,v in values.items()}
                    floor=max(v['lower_bits'] for v in intervals.values())
                    candidates=[name for name,v in intervals.items() if v['upper_bits']>=floor-allowance]
                    choice[subject+'_possible_maximizers']=' | '.join(candidates)
                    guaranteed=[name for name,v in intervals.items() if all(
                        other==name or v['lower_bits']>intervals[other]['upper_bits']+allowance for other in names)]
                    choice[subject+'_guaranteed_winner']=' | '.join(guaranteed)
                    choice[subject+'_optimizer_excludes_idle']=names[0] not in candidates
                    choice[subject+'_optimizer_disjoint_from_whole']=not set(candidates)&set(possible)
                choices.append(choice)
    csv_write('GLOBAL_CHOICES.csv',choices)
    summary={'status':status['status'],'completed':len(results),'total':status.get('total_cases',len(status['cases'])),
             'comparisons':len(rows),'complete_family_choices':len(choices),'source_hash':status['source_hash']}
    summary['priority_results_merged']=priority_added
    summary['global_corridor_counts']=dict(Counter(r['global_corridor'] for r in corridor))
    summary['resolved_D_positive_S_negative']=sum(r['D_positive_S_negative'] for r in corridor)
    summary['resolved_self_whole_oppositions']=sum(r['self_whole_opposition'] for r in corridor)
    (DOC/'DISCOVERY_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    render_results(rows,choices,summary)
    print(json.dumps(summary))


def render_results(rows,choices,summary):
    state='COMPLETE' if summary['status']=='complete' else 'RUNNING — partial results'
    lines=['# Fractional-cost control and paid discovery', '',
           f"**{state}: {summary['completed']}/{summary['total']} distinct cases completed.**", '',
           'All comparisons use the 29,760-state adapter with the same bank capacity, energy grid, '
           'source, bath and preparation within each context. Finite physical-history lushness is '
           'primary; stationary rate, activity and stocks are explanatory readouts. The main map '
           'varies pocket yield, intervention bill and strength. The C5 companion varies the bill '
           'for resource-entry exclusion at κ=0, with the same shared-resource coupling.', '',
           '## T256, cadence 0.25', '',
           'Strong interventions (strength 0.95), relative to the matched idle world. '
           'Intervals are conditioning bounds, not sampling confidence intervals.', '',
           '| Target | Yield | Bill | Whole Δ bits | D interval | S interval |',
           '| --- | ---: | ---: | ---: | ---: | ---: |']
    focus=sorted([r for r in rows if r['horizon']==256 and r['cadence']==.25 and r['phi']==.95],
                 key=lambda r:(r['target'],r['opportunity_yield'],r['cost']))
    for r in focus:
        lines.append(f"| {r['target']} | {r['opportunity_yield']:g} | {r['cost']:g} | {r['global_delta']:.3f} | "
                     f"[{r['D_difference_lower']:.3f}, {r['D_difference_upper']:.3f}] | "
                     f"[{r['S_difference_lower']:.3f}, {r['S_difference_upper']:.3f}] |")
    lines+=['', '## Access, persistence and resource use', '',
            'For cheap strong trap-entry steering at T256: first arrival, mean time in the pocket, '
            'net S capture and accepted source work are separate quantities. Both positive and '
            'negative changes are retained.', '',
            '| Yield | First-arrival probability Δ | Mean pocket occupancy Δ | Net S capture Δ | Accepted work Δ |',
            '| ---: | ---: | ---: | ---: | ---: |']
    for r in focus:
        if r['target']=='trap_entry' and r['cost']==.1:
            lines.append(f"| {r['opportunity_yield']:g} | {r['delta_p_discovered']:.4f} | "
                         f"{r['delta_mean_S.discovered']:.4f} | {r['delta_net_capture_S']:.4f} | {r['delta_accepted_work']:.4f} |")
    lines+=['', 'Yield acts only after entering the pocket, so first-arrival probabilities are '
            'unchanged by yield for a given intervention. Trap-entry control also intercepts '
            'return from the pocket into the trap. It can obstruct arrival and prolong residence; '
            'this is not a pure first-entry restriction. The oracle knows the law; discovery here '
            'is physical access, not acquisition of a hidden model.', '',
            '## Resource exclusion: breadth gain and material flow', '',
            '| Bill | Additional D net capture | Intervention fuel | Capture minus bill |',
            '| ---: | ---: | ---: | ---: |']
    for r in focus:
        if r['target']=='access_entry':
            lines.append(f"| {r['cost']:g} | {r['delta_net_capture_D']:.4f} | {r['delta_friction_fuel']:.4f} | "
                         f"{r['capture_gain_minus_friction_bill']:.4f} |")
    lines+=['', 'The last column is a partial flow margin, not a complete energy profit. '
            'See [the completed priority C5 comparison](C5_RESULTS.md) for the resolved '
            'private/whole conflict through T1024.', '',
            '## Complete candidate families', '',
            f"{len(choices)} completed family/horizon/cadence searches compare idle with strengths "
            '0.55 and 0.95 at a fixed physical bill. GLOBAL_CHOICES.csv includes whole-field '
            'maximizers and conservative D/S possible maximizers. It does not optimize interval '
            'midpoints or declare the first arriving candidate a winner.', '',
            'CORRIDOR_MAP.csv groups signs across all three tested clocks. Counts are '
            'case × horizon comparisons, not independent trials: '+', '.join(
                f'{key}: {value}' for key,value in summary['global_corridor_counts'].items())+'.', '',
            '## Model and numerical scope', '',
            'The fractional reservoir is explicitly physical in this adapter, with a common '
            'reversible bath and declared reference density. Active friction remains a coarse '
            'nonequilibrium control boundary. Native equilibrium and full energy accounting '
            'are checked; a closed microscopic reversible controller is not claimed. Both '
            'subjects are functional controller/apparatus proxies.', '',
            'All physical stochasticity at the declared grain counts. No noise, intervention or environmental entropy '
            'is subtracted. D/S histories remain hidden-Markov; unresolved signs remain unresolved. '
            'The temporal audit covers the declared sample points, not every intermediate cadence.', '',
            f"Numerical source: `{summary['source_hash']}`. Configurations, receipts, compact maps, "
            'small code archives and validation records are retained. No dense kernels are saved.', '']
    if summary['status']!='complete':
        lines+=['Only completed cases enter this report. Conclusions about unfinished yields '
                'or bills remain pending.', '']
    (DOC/'RESULTS.md').write_text('> **Updated interpretation, 16 October 2026:** Historical `native_events` steering may redirect into chemistry. Exit/all steering is not mobility evidence; B1 also intercepted pocket returns. See [the audit correction](../C5_AUDIT_CORRECTIONS_2026-10-16.md) before using these rows. Original numerical results are retained.\n\n'+ '\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    if (DOC/'FOLLOWUP_STATUS.json').exists():
        followup()
    if (DOC/'SURVEY_STATUS.json').exists():
        survey()
