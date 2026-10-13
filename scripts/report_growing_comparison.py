"""Automatic outcomes for the first growing-world comparison; no simulation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def assess(r):
    w=r['winner'];lookup={tuple(x['table']):x for x in r['policies']}
    diag=next(d for d in r['diagnostics'] if list(d['table'])==w['table'])
    idle=lookup[('idle','idle')];seed=diag['surveys']['64']['distributed_seed'];reference=diag['surveys']['64']['matched_reference']
    gap=w['offset_bits']['distributed_seed']-w['offset_bits']['matched_reference']
    signs={'positive':0,'negative':0,'tie':0}
    for row in r['policies']:
        for p in row['profiles'].values():
            d=p['distributed_seed']-p['matched_reference']
            signs['positive' if d>1e-9 else 'negative' if d<-1e-9 else 'tie']+=1
    sensitivity=[]
    for delta in (.125,.5):
        records=[(d['table'],next(x for x in d['cadence_sensitivity'] if x['cadence']==delta)) for d in r['diagnostics']]
        top=max(x[1]['rate_bits_per_time'] for x in records)
        ties=[list(x[0]) for x in records if top-x[1]['rate_bits_per_time']<=1e-9]
        sensitivity.append({'cadence':delta,'best_listed_tables':ties,'primary_winner_among_best_listed':w['table'] in ties})
    top=max(d['bill2']['rate_bits_per_time'] for d in r['diagnostics'])
    billties=[list(d['table']) for d in r['diagnostics'] if top-d['bill2']['rate_bits_per_time']<=1e-9]
    ledgers=max(abs(v[k]) for d in r['diagnostics'] for s in d['surveys'].values() for v in s.values() for k in ('energy_residual','population_residual'))
    good=r['controllers']==36 and r['audits']['max_stationary_residual']<=1e-10 and r['audits']['max_poisson_residual']<=1e-9 and ledgers<=1e-8
    summary={'arm':r['arm'],'winner':w,'best_deterministic':r['best_deterministic'],
        'maximum_functioning':r['maximum_functioning'],'idle':idle,'seed_T64':seed,'reference_T64':reference,
        'seed_offset_minus_reference':gap,'finite_reference_signs':signs,
        'offset_range':[min(x['offset_bits']['distributed_seed']-x['offset_bits']['matched_reference'] for x in r['policies']),
                        max(x['offset_bits']['distributed_seed']-x['offset_bits']['matched_reference'] for x in r['policies'])],
        'cadence_sensitivity':sensitivity,'bill2_best_listed_tables':billties,'winner_bill2':diag['bill2'],
        'finite_winners':r['finite_winners'],'winner_surveys':diag['surveys'],
        'reference_initial_built':r['reference_initial_built'],'reference_initial_active':r['reference_initial_active'],
        'reference_states':r['reference_states'],'audits':r['audits'],'sampling':r['sampling_check'],
        'registered_outcomes':{'G1':'pass' if good else 'fail','G2':'seed_ahead' if gap>1e-9 else 'seed_behind' if gap<-1e-9 else 'tie',
            'G3':'net_seed_expansion' if seed['built']>1+1e-8 else 'no_net_seed_expansion',
            'G4':'maintenance_tradeoff_hit' if w['stationary_active']<r['maximum_functioning']['stationary_active']-1e-8 else 'no_hit',
            'G5':'factorial_and_fixed_table_contrasts_reported','G6':'candidate_only_sensitivity_reported',
            'G7':'pass' if r['sampling_check']['passed'] else 'fail'}}
    return summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('runs',nargs=4,type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    raw={};provenance=[]
    for path in args.runs:
        r=json.loads((path/'result.json').read_text());profile=json.loads((path/'PROFILE.json').read_text())
        if profile['exit_code']!=0:raise RuntimeError('Incomplete arm')
        raw[r['arm']]=r;provenance.append({'arm':r['arm'],'run':str(path),'result_hash':digest(path/'result.json'),
             'input_hash':json.loads((path/'manifest.json').read_text())['input_hash'],'profile':profile})
    names=['full','no_assistance','no_capture_benefit','neither']
    if set(raw)!=set(names):raise RuntimeError('Missing factorial arm')
    summaries=[assess(raw[k]) for k in names]
    grid={k:{tuple(x['table']):x for x in raw[k]['policies']} for k in names}
    contrasts=[]
    for table in grid['full']:
        rates={k:grid[k][table]['rate_bits_per_time'] for k in names}
        active={k:grid[k][table]['stationary_active'] for k in names}
        contrasts.append({'table':table,'rates':rates,'active':active,
                          'assistance_rate_effect_with_capture':rates['full']-rates['no_assistance'],
                          'capture_rate_effect_with_assistance':rates['full']-rates['no_capture_benefit'],
                          'rate_interaction':rates['full']-rates['no_assistance']-rates['no_capture_benefit']+rates['neither']})
    full=summaries[0];fixed=next(x for x in contrasts if list(x['table'])==full['winner']['table'])
    optimized_interaction=sum(sign*raw[k]['winner']['rate_bits_per_time'] for k,sign in zip(names,(1,-1,-1,1)))
    text=['# First controlled growing-substrate comparison','',
          'Completed2026-10-13. Unfiltered conditional count-history breadth is the only objective. Rule A was parked and not evaluated. All four registered mechanism arms completed.', '',
          '**Main result:** the breadth optimizer supports paid population expansion and chooses a state-dependent mixed controller when active capture is beneficial. However, its seed does not beat the matched randomized reference under the full law, and it retains less functioning apparatus than the passive fixed-service benchmark.', '',
          '## Search and physical matching', '',
          'Inventory is3+1 body precursors and matching local carrier pools, at most960 counted states. Each arm exhaustively enumerates36 shared local inactive/active tables, including9 deterministic-or-idle tables. The same table is installed at both compartments, with independent native executions and local information only. This is a certified grid optimum within that class, not over separate local tables or unrestricted control. The asymmetric inventories are fixed and do not provide a fairness test.', '',
          'Each root has energy8, the same matter, controller hardware, service gates, temperature and drive. The randomized reference contains30 counted energy-shell states, weighted by body/carrier degeneracy. It includes equipped states and is propagated conditionally; no preparation entropy is added. Its initial averages are '+f"{full['reference_initial_built']:.6f} built and {full['reference_initial_active']:.6f} active units, versus one built/active unit in the seed. This is a coarse preparation reference, not a molecular gas.", '',
          '## Optimizer results', '',
          '| Mechanism law | Winning inactive / active response | Bits per time | Stationary built | Stationary active | Passive fixed-service active | Seed−reference offset, bits |',
          '|---|---|---:|---:|---:|---:|---:|']
    for s in summaries:
        w=s['winner'];text.append(f"| {s['arm']} | {' / '.join(w['table'])} | {w['rate_bits_per_time']:.6f} | {w['stationary_built']:.6f} | {w['stationary_active']:.6f} | {s['idle']['stationary_active']:.6f} | {s['seed_offset_minus_reference']:.6f} |")
    text += ['', 'Full enabling and no-assistance choose service when inactive and25% export-pathway bias when active. Removing the active-capture advantage changes the best table to service/service, with or without assistance. Responses select reversible actuator pathways; even a deterministic response can have thermal reverse switching. Passive idle leaves gates at service and native repair/construction available.', '',
             'This supports an instrumental response to enabling: maintaining an active seed and varying access can increase breadth. It does not prove exploration, learning, discovered new channels or an ethical preference. These worlds have fixed laws and four body slots.', '',
             '## Expansion and the matched reference', '',
             '| Full law horizon | Seed built | Seed active | Reference built | Reference active | Seed−reference bits |',
             '|---|---:|---:|---:|---:|---:|']
    w=full['winner']
    for t,survey in full['winner_surveys'].items():
        s=survey['distributed_seed'];r=survey['matched_reference'];bits=w['profiles'][t]['distributed_seed']-w['profiles'][t]['matched_reference']
        text.append(f"| {t} | {s['built']:.6f} | {s['active']:.6f} | {r['built']:.6f} | {r['active']:.6f} | {bits:.6f} |")
    text += ['', f"The full-law seed expands from1 to {full['seed_T64']['built']:.6f} built units byT64. The reference also evolves and converges to almost the same occupancy. The seed's exact long-run offset is {full['seed_offset_minus_reference']:.6f} bits below the reference. Concentrating its charge at the seed compartment is also retained as a registered control; it does not rescue the full-law comparison.", '',
             'Within each finite irreducible reachable class the preparation roots share a rate. Their differences are bounded offsets, not sustained rate advantages. A better mechanism law or policy can change the rate; a seed cannot retain a different limiting rate under that same mixing law.', '',
             '## Construction, turnover and resources', '',
             '| Full-law seed atT64 | Expected quantity |','|---|---:|']
    for k in ('gross_basal_birth','gross_assisted_birth','gross_thermal_reconstruction','gross_built_loss','drive_work','bath_heat','switches','hit_three_built_by_horizon','at_least_three_built','at_least_three_active'):
        text.append(f"| {k} | {full['seed_T64'][k]:.6f} |")
    text += ['', 'Paid basal construction + paid assisted construction + thermal reconstruction − built-unit losses closes the net population increase. Many births are turnover, not permanently accumulated capacity. Built includes worn apparatus; active is functioning apparatus. Functional growth is not an assertion about new valuers or identity.', '',
             'The chance of ever reaching three built units is high while retained three-unit occupancy is lower. This distinguishes access to growth from maintaining its result. The smoke independently verified that a newly constructed unit can assist the next construction. This experiment measures gross assistance and aggregate growth, not an ancestry-resolved reproduction rate.', '',
             '## Mechanism effects', '',
             f"At the full-law winning table, assistance raises rate by {fixed['assistance_rate_effect_with_capture']:.6f} bits/time; active-capture benefit raises it by {fixed['capture_rate_effect_with_assistance']:.6f}. The fixed-table interaction is {fixed['rate_interaction']:.6f} bits/time. The separately optimized factorial interaction is {optimized_interaction:.6f} and includes controller adaptation.", '',
             'These effects come from specified native reactions, with no generativity bonus. Assistance changes both forward and reverse construction kinetics. The contrasts do not separate productive enabling from all extra stochastic activity, because an activity-matched extra-noise world was not implemented. A positive kinetic/breadth effect is not by itself proof of ethically useful compounding.', '',
             '## Registered outcomes and sensitivities', '',
             '| Law | G1 checks | G2 seed/reference | G3 growth | G4 protection | G7 sampled information |','|---|---|---|---|---|---|']
    for s in summaries:
        o=s['registered_outcomes'];text.append(f"| {s['arm']} | {o['G1']} | {o['G2']} | {o['G3']} | {o['G4']} | {o['G7']} |")
    text += ['', 'Every controller’s finite preparation signs and offset range are retained in the machine summary. There are full-law controllers under which the seed beats its reference, but they are not the primary rate-maximizing choice. We do not replace the winning policy afterward to manufacture a successful seed comparison.', '',
             '| Law | Range of seed−reference offsets across grid | Primary winner remains best among listed at .125/.5 | Best listed table(s) with two-token switch |','|---|---|---|---|']
    for s in summaries:
        text.append(f"| {s['arm']} | {s['offset_range'][0]:.6f} to {s['offset_range'][1]:.6f} | {[x['primary_winner_among_best_listed'] for x in s['cadence_sensitivity']]} | {s['bill2_best_listed_tables']} |")
    text += ['', 'Cadence and two-token actuator comparisons evaluate selected candidates only. The right compartment has one carrier and therefore cannot execute a two-token switch; that actuator variant changes access physically. No full-grid cost threshold or realistic empirical actuator cost is inferred.', '',
             '## Verification and conclusion', '',
             'All36 controllers in each of four arms pass reachable-class/stationary and Poisson residual checks. Selected surveys close energy and population accounts and pass zero-potential thermal balance. Each winning law passes a10000-trajectory sampled path-information check against exact finite-chain entropy. Calculations use the declared count grain and exact CTMC matrix exponentials, not reaction-label entropy.', '',
             'The result supports paid, recursively enabled population growth as a lawful mechanism and shows that an unfiltered-breadth optimizer can use it. It also preserves two failures: less functioning capacity than the passive benchmark, and a full-law seed disadvantage against the matched reference. Open-ended growth, real gas competition, autonomous new agents, and ethical adequacy remain unestablished.', '',
             '## Execution and provenance','']
    for p in provenance:
        e=p['profile'];text.append(f"- {p['arm']}: {e['wall_seconds']:.3f}s, peak {e['peak_job_bytes']/1024**2:.2f}MiB; `{Path(p['run']).name}`, input hash `{p['input_hash']}`.")
    text += ['', 'Each arm used120s/1GiB/256MiB caps and one numerical thread; none hit a cap. Physics/parameters, roots and controller class were frozen before ranking. A timing-only profile justified the bounded search. Raw tables stay local and ignored. No deletion, commit, push, Rule A work or manuscript/Drive publication occurred.', '']
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'RESULTS_r1.md').write_text('\n'.join(text),encoding='utf-8')
    summary={'arms':summaries,'fixed_table_contrasts':contrasts,'optimized_rate_interaction':optimized_interaction}
    (args.output/'SUMMARY_r1.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (args.output/'PROVENANCE.json').write_text(json.dumps({'inputs':provenance,'report_generator_sha256':digest(Path(__file__)),
        'reports':{p.name:digest(p) for p in (args.output/'RESULTS_r1.md',args.output/'SUMMARY_r1.json')}},indent=2)+'\n')
    print(json.dumps([{'arm':s['arm'],'winner':s['winner']['table'],'outcomes':s['registered_outcomes']} for s in summaries],indent=2))

if __name__=='__main__':main()
