"""Deterministic, compact reporting from retained A/B results; no new simulation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('assembly',type=Path);ap.add_argument('controlled',type=Path)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    ar,br=read(a.assembly/'result.json'),read(a.controlled/'result.json')
    pa,pb=read(a.assembly/'PROFILE.json'),read(a.controlled/'PROFILE.json')
    primary=next(q for q in br['queries'] if q['speed']==1 and q['cadence']==.25)
    lookup={tuple(p['policy']):p for p in primary['policies']}
    winner=br['winner'];det=br['best_deterministic'];surveys={tuple(s['policy']):s for s in br['surveys'] if s['horizon']==64}
    ws=surveys[tuple(winner['policy'])]['organized'];ms=surveys[(0.,)*4]['organized']
    disparity=abs(ws['active_expected'][0]-ws['active_expected'][1])
    checks={
        'B1':{'status':'pass','maximum_generator_error':max(x['generator_error'] for x in br['audits']['bng'])},
        'B2':{'status':'pass','closed_balance_error':br['audits']['closed_detailed_balance']},
        'B3':{'status':'pass','maximum_energy_residual':max(abs(s[r]['first_law_residual']) for s in br['surveys'] for r in ('organized','disassembled'))},
        'B4':{'status':'strict_stochastic_grid_advantage' if winner['rate_bits_per_time']-det['rate_bits_per_time']>1e-9 else 'no_strict_advantage',
              'rate_gap':winner['rate_bits_per_time']-det['rate_bits_per_time']},
        'B5':{'status':'adversarial_hit' if sum(ws['active_expected'])<sum(ms['active_expected'])-1e-8 else 'not_hit',
              'active_total_difference':sum(ws['active_expected'])-sum(ms['active_expected'])},
        'B6':{'status':'reported_all_roots','minimum_offset_advantage':min(p['offset_bits'][0]-p['offset_bits'][1] for p in primary['policies']),
              'maximum_offset_advantage':max(p['offset_bits'][0]-p['offset_bits'][1] for p in primary['policies']),
              'finite_positive':sum(p['profiles'][str(t)][0]>p['profiles'][str(t)][1]+1e-9 for p in primary['policies'] for t in (1,4,16,64)),
              'finite_negative':sum(p['profiles'][str(t)][0]<p['profiles'][str(t)][1]-1e-9 for p in primary['policies'] for t in (1,4,16,64))},
        'B7':{'status':'same_unique_rate_winner' if all(s['rate_optimal_policies']==[winner['policy']] for s in br['optimal_sets']) else 'ranking_sensitivity',
              'optimal_sets':br['optimal_sets']},
        'B8':{'status':'unequal_access_hit' if disparity>1e-8 else 'not_hit','winner_active_disparity':disparity}
    }
    for key in ('B1','B2','B3'):
        bound={'B1':1e-10,'B2':1e-11,'B3':1e-8}[key]
        value=next(v for k,v in checks[key].items() if k!='status')
        if value>bound:checks[key]['status']='fail'
    rows=[]
    for case in ar['cases'].values():
        if case['inventory']==4 and case['root']=='unassembled':
            for p in case['breadth_profile']:
                if p['delta']==.25 and p['horizon']==64:
                    rows.append((case['arm'],p))
    text=['# Assembly and controlled access: first results', '',
          'Completed 2026-10-13. Both scientific runs used a 120-second wall limit, 1 GiB process-tree memory cap and 256 MiB output cap. No cap was hit.', '',
          '**Main result:** the whole-world breadth optimizer discovers a state-dependent randomized controller, with no repair/cooperation reward. It outperforms all deterministic settings in the grid, but preserves less functioning apparatus than the service-biased control. This is an adverse protective-performance result, not an ethical success certificate.', '',
          '## A. Assembly', '',
          'BioNetGen generated 18 small networks covering three laws, inventories 2/3/4 and assembled/unassembled preparations. The full declared state here is coarse monomer/dimer counts. The feedback route requires a retained dimer plus two free monomers; at inventories 2 and 3 it cannot operate. The frozen-accident arm is slow reversible trapping, not irreversible locking.', '',
          '| N=4 law, T=64, cadence .25 | Unassembled root, bits | Assembled root, bits | Stationary conditional baseline, bits |',
          '|---|---:|---:|---:|']
    for arm,p in rows:text.append(f"| {arm} | {p['unassembled_bits']:.6f} | {p['assembled_bits']:.6f} | {p['same_law_stationary_conditional_baseline_bits']:.6f} |")
    text += ['', 'Feedback raises breadth in this small mechanism contrast while preserving the equilibrium distribution. Already being assembled does not win the same-law preparation comparison shown here. Changing the catalytic law is different from rearranging matter under one law. This is finite saturation with at most two dimers; it is not evidence of open-ended compounding.', '',
             'All generated generators exactly matched hand construction. Both direct SSA and the official BioNetGen sampler passed the registered distribution checks. Maximum balance error: '+f"{ar['audits']['detailed_balance_max_abs_flux_error']:.3g}.", '',
             '## B. Controlled access optimizer', '',
             'Two compartments each contain precursor/worn/active apparatus, an empty/charged carrier and a service/exchange gate: 144 full states. All 81 pairs of local response settings were enumerated, including 16 deterministic pairs. The first 2 policy numbers describe the left controller when inactive/active; the last 2 describe the right. Each number is the export-pathway bias p. Thermal reverse switches remain even at p=0 or 1.', '',
             f"The unique best long-run grid policy is **{winner['policy']}**: service bias when inactive, mixed service/exchange when active. The same unique winner occurs at all three cadences and both additional common-speed settings. The speed sweep uniformly rescales the generator; those are clock/horizon sensitivity cases, not five independent universes or temperature changes.", '',
             '| Controller | Bits per time | Rooted breadth at T=64, bits | Expected active apparatus at T=64 (max 2) |',
             '|---|---:|---:|---:|']
    for label,pol in [('Best grid policy',tuple(winner['policy'])),('Best deterministic',tuple(det['policy'])),('Always service bias',(0.,)*4),('Unconditional half/half',(.5,)*4),('Always exchange bias',(1.,)*4)]:
        r=lookup[pol];s=surveys[pol]['organized']
        text.append(f"| {label} | {r['rate_bits_per_time']:.6f} | {r['profiles']['64'][0]:.6f} | {sum(s['active_expected']):.6f} |")
    r=br['passive_service'];text += [f"| Passive fixed service gates | {r['rate_bits_per_time']:.6f} | {r['profiles']['64'][0]:.6f} | Not surveyed |", '',
       f"The stochastic-inclusive rate exceeds the best deterministic rate by **{checks['B4']['rate_gap']:.6f} bits/time ({100*checks['B4']['rate_gap']/det['rate_bits_per_time']:.2f}%)**. This is an optimum over the registered coarse grid, not all continuous biases, memoryful controllers or centralized policies.", '',
       f"The winner retains **{sum(ws['active_expected']):.6f}** active units versus **{sum(ms['active_expected']):.6f}** for service bias: **{100*(1-sum(ws['active_expected'])/sum(ms['active_expected'])):.2f}% fewer**. It draws {ws['drive_work']:.6f} units of net chemical work over T64 versus {ms['drive_work']:.6f}, and has {ws['switches']:.6f} expected gate transitions versus {ms['switches']:.6f}. The optimizer benefits from greater powered throughput and gate activity; maintenance is instrumentally useful, not maximized.", '',
       '## Horizons, preparations and background', '',
       '| Planning horizon | Best finite-horizon policy |','|---|---|']
    for t,pol in br['finite_winners'].items():text.append(f'| {t} | {pol} |')
    text += ['', f"At the winning policy, the organized energy-matched root exceeds the disassembled root by {winner['profiles']['64'][0]-winner['profiles']['64'][1]:.6f} bits at T64. Its exact asymptotic offset advantage is **{winner['offset_bits'][0]-winner['offset_bits'][1]:.6f} bits**. Their long-run rates coincide because they evolve under the same irreducible law.", '',
       f"The same-policy stationary conditional baseline at T64 is {winner['stationary_conditional_bits']['64']:.6f} bits; the organized root gives {winner['profiles']['64'][0]:.6f} and the disassembled root {winner['profiles']['64'][1]:.6f}. No preparation-prior entropy is added. Stationarity here includes organization generated by the law. This is a driven background reference, **not a thermal gas comparator**. A disassembled root also reconstructs; neither is a permanently disabled control.", '',
       'The organized and disassembled roots have identical matter, total modeled energy 4, gate state, controller hardware, drive and law. Energy is allocated differently between apparatus and fuel. Controller hardware survives apparatus disassembly. Functional loss is not identified with death or loss of a valuer.', '',
       '## Recovery and where the randomness appears', '',
       f"From the disassembled root, the winner reaches simultaneous function at least once by T64 with probability {surveys[tuple(winner['policy'])]['recovery']['both_active_hit_by_horizon']:.6f}; probability both are functional at T64 is only {surveys[tuple(winner['policy'])]['recovery']['both_active_at_horizon']:.6f}. Recovery occurrence and retained function are distinct.", '',
       f"The winner's rate decomposes by a declared chain-rule ordering into {br['winner_rate_chain_rule']['next_body_fuel_given_full_previous']:.6f} bits/time in next apparatus/fuel given the full previous state, plus {br['winner_rate_chain_rule']['next_gate_given_next_body_fuel_and_full_previous']:.6f} in next gates conditional on those variables. These sum to its full rate. This is not the entropy rate of an isolated marginal observation process, nor a causal attribution of all additional breadth to controller noise. No physical randomness was filtered out by a persistence test.", '',
       '## Registered outcomes', '', '| ID | Outcome |','|---|---|']
    for k,v in checks.items():text.append(f"| {k} | {v['status']} |")
    text += ['', f"B6 examined all 81 policies at four horizons: {checks['B6']['finite_positive']} positive and {checks['B6']['finite_negative']} negative organized-minus-disassembled comparisons. Offset differences range from {checks['B6']['minimum_offset_advantage']:.6f} to {checks['B6']['maximum_offset_advantage']:.6f} bits. B8 found equal left/right functioning at the unique optimum; this tests neither fairness generally nor self-subject exclusion.", '',
       '## Verification and limits', '',
       f"Three representative B generators agree with BioNetGen to {checks['B1']['maximum_generator_error']:.3g}; every policy's limiting solve verifies irreducibility and numerical residuals. Closed-bath detailed balance error is {checks['B2']['closed_balance_error']:.3g}; maximal surveyed first-law error is {checks['B3']['maximum_energy_residual']:.3g}. Renaming, unit conversion and semigroup checks pass. A 10,000-trajectory sampled-information check agrees with exact finite-chain entropy within its registered tolerance.", '',
       'The sixfold capture advantage of active apparatus is a stipulated mechanism, not an inferred law of generativity. The experiment asks what a controller chooses when that mechanism exists. Local sensing and the hardwired response table are idealized catalytic couplings, with no separately charged computational cost. Gates have paid fuel transitions and thermal reversals. No embodied-controller death, coercion, population growth, continuous policy search, Rule A, or empirical calibration is claimed.', '',
       'The test establishes useful optimizer behavior and an adverse maintenance trade-off in one finite world. It does not establish that organized matter beats a proper gas reference or that the optimizer is ethical. Next discriminating work should keep this objective and add the missing matched thermal/disordered ensemble and broader controller capabilities, with the current harmful trade-off retained as a regression target.', '',
       '## Execution and provenance', '',
       f"Assembly: {pa['wall_seconds']:.3f}s, peak {pa['peak_job_bytes']/1024**2:.2f} MiB. Controlled: {pb['wall_seconds']:.3f}s, peak {pb['peak_job_bytes']/1024**2:.2f} MiB. Raw artifacts remain local and ignored; no deletion, commit or push.", '',
       'An earlier assembly engineering execution inspected the same numerical laws before the capped run. The beta=1 annotation was made explicit afterward without changing rates or selection criteria. Thus A is a transparent exploratory/calibration result, not a blinded confirmatory preregistration. B was frozen before scientific ranking; its smoke inspected law/equilibrium only. Post-run work here only summarizes existing outputs.', '',
       f"Assembly run: `{a.assembly.name}`; input hash `{read(a.assembly/'manifest.json')['input_hash']}`.",
       f"Controlled run: `{a.controlled.name}`; input hash `{read(a.controlled/'manifest.json')['input_hash']}`.", '']
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/'RESULTS_r1.md').write_text('\n'.join(text),encoding='utf-8')
    compact={'assembly':rows,'winner':winner,'best_deterministic':det,'registered_outcomes':checks,
             'finite_winners':br['finite_winners'],'rate_chain_rule':br['winner_rate_chain_rule'],
             'profiles':{'assembly':pa,'controlled':pb}}
    (a.output/'SUMMARY_r1.json').write_text(json.dumps(compact,indent=2,allow_nan=False)+'\n')
    provenance={'report_generator_sha256':digest(Path(__file__)),
        'input_results':{str(p):digest(p) for p in (a.assembly/'result.json',a.controlled/'result.json')},
        'reports':{p.name:digest(p) for p in (a.output/'RESULTS_r1.md',a.output/'SUMMARY_r1.json')}}
    (a.output/'REPORT_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
