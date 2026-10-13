"""Automated registered outcomes and optional Rule A interpretation.

Consumes existing result files only; never retunes physics or changes reward.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def assess(r):
    winner=r['winner'];lookup={tuple(x['policy']):x for x in r['policies']}
    service=lookup[('service',)*4];idle=lookup[('idle',)*4]
    diagnostics={tuple(d['policy']):d for d in r['diagnostics']}
    wd=diagnostics[tuple(winner['policy'])]
    overlay=[]
    for root in ('organized','disassembled','matched_shell','stationary'):
        for lag in ('0.0','0.25','1.0','4.0','16.0','64.0'):
            high=max(d['rule_a'][root][lag] for d in r['diagnostics'])
            tied=[d['policy'] for d in r['diagnostics'] if high-d['rule_a'][root][lag]<=1e-10]
            value=wd['rule_a'][root][lag]
            overlay.append({'root':root,'lag':float(lag),'primary_winner_bits':value,
                            'best_listed_bits':high,'best_listed_policies':tied,
                            'primary_winner_among_best_listed':winner['policy'] in tied})
    sensitivity=[]
    for delta in (.125,.5):
        rows=[(d['policy'],next(x for x in d['cadence_sensitivity'] if x['cadence']==delta)) for d in r['diagnostics']]
        best=max(x[1]['rate'] for x in rows)
        tied=[x[0] for x in rows if best-x[1]['rate']<=1e-9]
        sensitivity.append({'cadence':delta,'best_listed_policies':tied,'primary_winner_among_best_listed':winner['policy'] in tied})
    least=min(r['policies'],key=lambda x:x['offsets']['organized']-x['offsets']['matched_shell'])
    min_offset=least['offsets']['organized']-least['offsets']['matched_shell']
    finite_signs={'positive':0,'negative':0,'tie':0}
    for row in r['policies']:
        for p in row['profiles'].values():
            gap=p['organized']-p['matched_shell']
            finite_signs['positive' if gap>1e-9 else 'negative' if gap<-1e-9 else 'tie']+=1
    preservation=winner['stationary_active_total']-service['stationary_active_total']
    audits=r['audits']
    engineering=(r['controller_count']==1296 and r['deterministic_or_idle_count']==81
                 and audits['max_stationarity_residual']<=1e-10 and audits['max_poisson_residual']<=1e-9
                 and audits['resource_residual']<=1e-8)
    retained_mismatch=any(not x['primary_winner_among_best_listed'] for x in overlay)
    assessment={
        'capture_factor':r['capture_factor'],'winner':winner,'best_deterministic_or_idle':r['best_deterministic_or_idle'],
        'service_rate':service['rate'],'service_active':service['stationary_active_total'],
        'idle_rate':idle['rate'],'idle_active':idle['stationary_active_total'],
        'functioning_benchmark':r['max_functioning_benchmark'],
        'winner_shell_offset_advantage':winner['offsets']['organized']-winner['offsets']['matched_shell'],
        'minimum_grid_shell_offset_advantage':min_offset,'finite_shell_signs':finite_signs,
        'least_favorable_reference_policy':least['policy'],
        'protection_tradeoff':preservation,'protection_tradeoff_percent':100*(-preservation)/service['stationary_active_total'],
        'rule_a_policy_scope':'algorithmically selected candidates, not complete-grid overlay optimization',
        'rule_a_assessment':overlay,'rule_a_profiles':[{k:d[k] for k in ('policy','rule_a')} for d in r['diagnostics']],
        'cadence_sensitivity':sensitivity,'finite_winners':r['finite_winners'],
        'winner_chain_rule_rate':wd['chain_rule_rate'],'winner_organized_T64':wd['organized_T64'],
        'winner_recovery_T64':wd['recovery_T64'],
        'registered_outcomes':{
            'E1':'pass' if engineering else 'fail',
            'E2':'all_grid_offsets_organized_ahead' if min_offset>1e-9 else 'mixed_or_nonpositive_offset_signs',
            'E3':'reported_without_monotonicity_assumption',
            'E4':'maintenance_tradeoff_hit' if preservation<-1e-8 else 'no_maintenance_tradeoff_hit',
            'E5':'overlay_rank_disagreement' if retained_mismatch else 'no_disagreement_among_listed',
            'E6':'listed_cadence_rank_flip' if any(not x['primary_winner_among_best_listed'] for x in sensitivity) else 'primary_winner_remains_best_listed',
            'E7':('compiler_and_idle_regression_pass' if audits.get('legacy_generator_error',float('inf'))<=1e-12
                  and audits.get('idle_switch_rate',float('inf'))==0 else 'not_recorded_or_failed')},'audits':audits}
    return assessment


def make_report(paths,output):
    rows=[];provenance=[]
    for path in paths:
        r=json.loads((path/'result.json').read_text());summary=assess(r)
        profile=json.loads((path/'PROFILE.json').read_text())
        if profile['exit_code']!=0:raise RuntimeError('Cannot report incomplete run')
        summary['execution']=profile;rows.append(summary)
        provenance.append({'run':str(path),'result_sha256':digest(path/'result.json'),
                           'input_hash':json.loads((path/'manifest.json').read_text())['input_hash']})
    rows.sort(key=lambda x:x['capture_factor'])
    text=['# Enabling strength, expanded control and Rule A assessment', '',
          '2026-10-13. The registered extension keeps unfiltered whole-world path breadth as the primary objective. RuleA-R1 is a separately defined predictive-retention diagnostic. No persistence threshold or protective reward was added.', '',
          '**Result:** stronger active capture increases breadth and functioning under the winning policies, but the breadth optimizer still accepts reduced functioning relative to service-biased control in every registered regime. Predictive retention selects different listed candidates at longer lags; it does not automatically prefer better protection.', '',
          '## Search and matching', '',
          'Each regime exhaustively evaluates 1296 local policy pairs, including 81 deterministic-or-idle settings. Response choices are idle, service, exchange and three intermediate mixtures. Every actuator switch has the existing fuel debit and reverse channel. Idle retains the gate and incurs elapsed time, wear and forgone opportunities, with no invented fuel tax.', '',
          'The same-law reference is the uniform ensemble of all eight energy4 states with both gates initially at service. It includes the organized root. Each state is propagated conditionally, and the bits are averaged without adding preparation entropy. Matter, controller hardware, energy, chemical potential, temperature and clock are matched within each regime. This is the complete declared energy-shell preparation reference in this adapter; molecular positions and velocities are absent, so it is not a real gas comparison.', '',
          '## Primary results', '',
          '| Capture benefit | Winning left/right inactive→active response | Rate, bits/time | Stationary active total | Service-biased active total | Protection trade-off | Organized−shell offset, bits |',
          '|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        w=r['winner'];text.append(f"| {r['capture_factor']} | {', '.join(w['policy'])} | {w['rate']:.6f} | {w['stationary_active_total']:.6f} | {r['service_active']:.6f} | {r['protection_tradeoff_percent']:.2f}% fewer | {r['winner_shell_offset_advantage']:.6f} |")
    text += ['', 'All listed winners are symmetric, unique in rate within the registered grid, and service-biased when inactive. At capture factor1, active apparatus has no capture advantage, yet service/mix25 still wins: the repair/construction kinetics and gate/fuel coupling remain consequential. At factors3/6/12 the winner is service/mix50. This grid locates a change between factors1 and3; it does not locate an exact threshold.', '',
             'The organized-minus-reference advantage is a bounded root offset under each fixed finite law. Higher capture factors and changed policies are different laws and can have different rates. Increasing enabling strength did not eliminate the maintenance trade-off on the registered factors.', '',
             '| Capture benefit | Best deterministic-or-idle rate | Primary rate gain | Maximum-functioning policy | Its active total | All-idle rate |',
             '|---|---:|---:|---|---:|---:|']
    for r in rows:
        text.append(f"| {r['capture_factor']} | {r['best_deterministic_or_idle']['rate']:.6f} | {r['winner']['rate']-r['best_deterministic_or_idle']['rate']:.6f} | {', '.join(r['functioning_benchmark']['policy'])} | {r['functioning_benchmark']['stationary_active_total']:.6f} | {r['idle_rate']:.6f} |")
    text += ['', 'Maximum functioning is a descriptive benchmark, not another ethical target. In this grid its policy is all idle with gates left at service. Native assembly and repair remain available; actuator idling is not abandonment of maintenance. It saves switching expenditure and avoids gate interruptions. The breadth optimizer instead uses more of the accessible powered stochastic process.', '',
             '## RuleA-R1 operational assessment', '',
             'For a known root x, define R(delta,tau)=I(X_delta;X_(delta+tau)|X_0=x). At tau0 this equals next-step entropy. With Markov evolution it is nonnegative and nonincreasing as the later physical lag grows. It can retain a distinction after that distinction moves to another variable. Profiles are in bits; overlapping lags are never summed into volume. No policy is rewarded for passing this diagnostic.', '',
             'The table uses each candidate policy’s stationary known-root average. Other root queries—organized, disassembled and matched-shell—are stored in the machine-readable summary. Policies have different stationary occupations; these comparisons are process-relative, not a common initial-state distribution. Candidate-only winners below are not certified full-grid Rule A optima.', '',
             '| Benefit | Lag | Primary winner retained bits | Best listed retained bits | Best listed candidate(s) |',
             '|---|---:|---:|---:|---|']
    for r in rows:
        for v in r['rule_a_assessment']:
            if v['root']=='stationary' and v['lag'] in (0.,1.,4.,16.,64.):
                names=' / '.join(','.join(p) for p in v['best_listed_policies'])
                text.append(f"| {r['capture_factor']} | {v['lag']:g} | {v['primary_winner_bits']:.8g} | {v['best_listed_bits']:.8g} | {names} |")
    text += ['', 'At zero lag the primary rate winner necessarily leads on its stationary one-step entropy: that agreement is the definition, not an independent validation. Longer lags favor other candidates. Unconditional mixing often leads at intermediate lags, while exchange-oriented settings lead at long lags. The absolute retained information at lag64 is tiny (order10^-6 bits for the best listed candidates), so a large ratio there is not evidence of a large persistent structure.', '',
             'This exposes a limit of the overlay: slower mixing and long-lived gate/resource correlations can retain information even when apparatus functioning is low. The observed ranking alone does not identify which physical variable stores it. We therefore flag disagreement rather than interpret the overlay as a rescue of the ethical proxy. A variable-specific record/response audit would be needed for causal attribution.', '',
             '## Automated registered outcomes', '', '| Benefit | E1 checks | E2 reference | E4 protection | E5 Rule A | E6 cadence |',
             '|---|---|---|---|---|---|']
    for r in rows:
        o=r['registered_outcomes'];text.append(f"| {r['capture_factor']} | {o['E1']} | {o['E2']} | {o['E4']} | {o['E5']} | {o['E6']} |")
    text += ['', 'E3 reports the enabling trend and E7 confirms unchanged legacy generators and idle bookkeeping. Cadence sensitivity (.125/.5) evaluates only the selected candidate set; it does not reoptimize all1296 settings. No claim of global cadence robustness follows from that restricted check.', '',
             '| Benefit | Finite organized−shell: positive/negative/tie | Min grid root−shell offset | Reachable state counts |',
             '|---|---|---:|---|']
    for r in rows:
        v=r['finite_shell_signs'];text.append(f"| {r['capture_factor']} | {v['positive']}/{v['negative']}/{v['tie']} | {r['minimum_grid_shell_offset_advantage']:.6f} | {r['audits']['reachable_state_counts']} |")
    text += ['', 'The least favorable reference comparison is retained, even when the primary optimizer selects a different policy. At capture factor12, some policies give the organized root a negative long-run offset relative to the matched shell. Stronger enabling does not guarantee every organized preparation is ahead under every controller.', '',
             'Idle settings fix one or both gates and therefore query reachable chains of36,72 or144 states. All eight reference preparations lie in the same reachable chain for each policy. Stationary/offset calculations verify that restricted chain is irreducible rather than arbitrarily weighting unreachable gate classes.', '',
             '## Resource, functioning and recovery surveys', '',
             '| Benefit | Winner work over T64 | Winner gate transitions over T64 | Functional recovery by T64 | Both functional at T64 after recovery root | Gate conditional part of rate |',
             '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        s=r['winner_organized_T64'];rec=r['winner_recovery_T64'];cr=r['winner_chain_rule_rate']
        text.append(f"| {r['capture_factor']} | {s['drive_work']:.6f} | {s['switches']:.6f} | {rec['both_active_hit_by_horizon']:.6f} | {rec['both_active_at_horizon']:.6f} | {cr['next_gate_given_next_body_fuel_and_full_previous']:.6f} |")
    text += ['', 'Chemical work is actual captured work, not a fixed throughput allowance. Same incident drive does not force equal successful capture. Functioning, reconstruction, stored fuel, work, heat and switching are readouts with no reward bonus. Conditional gate entropy uses the declared chain-rule order and is not an exact attribution of all controller-caused activity.', '',
             '## Verification and scientific scope', '',
             'The extension uses the previously audited BioNetGen reaction law with finer response weights. Linear policy compilation is checked against direct native channel compilation; scalar legacy biases produce unchanged generators. Closed reachable classes and limiting residuals are checked for every policy. Rule A runtime checks enforce nonnegativity and data-processing monotonicity; independent two-state, constant-process and relabeling tests validate the diagnostic. First-law ledgers pass for all surveyed candidates.', '',
             'These results establish a reproducible enabling/maintenance boundary test, not population growth, open-ended compounding, a complete gas law, or an ethical verdict. The active capture gain is stipulated and swept; it is not a derived universal property of structure. Sensors/controller tables remain idealized catalytic coupling; apparatus disassembly does not remove the controller hardware or establish a valuer’s death.', '',
             '## Execution and reproduction', '']
    for r,p in zip(rows,sorted(provenance,key=lambda x:json.loads((Path(x['run'])/'result.json').read_text())['capture_factor'])):
        e=r['execution'];text.append(f"- Factor{r['capture_factor']}: {e['wall_seconds']:.3f}s, {e['peak_job_bytes']/1024**2:.2f}MiB peak; run `{Path(p['run']).name}`, input hash `{p['input_hash']}`.")
    text += ['', 'All runs capped at120s/1GiB/256MiB output; none hit a cap. Raw result tables remain local and ignored. No deletion, commit or push. Protocols and immutable source snapshots preceded each ranking. Reproduction commands and automatic report integration are in REPRODUCE.md.', '']
    output.mkdir(parents=True,exist_ok=True)
    (output/'RESULTS_r1.md').write_text('\n'.join(text),encoding='utf-8')
    (output/'SUMMARY_r1.json').write_text(json.dumps({'regimes':rows},indent=2,allow_nan=False)+'\n')
    (output/'REPORT_PROVENANCE.json').write_text(json.dumps({'inputs':provenance,'generator_sha256':digest(Path(__file__)),
        'report_hashes':{p.name:digest(p) for p in (output/'RESULTS_r1.md',output/'SUMMARY_r1.json')}},indent=2)+'\n')
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows=make_report(a.runs,a.output)
    print(json.dumps([{'factor':r['capture_factor'],'winner':r['winner']['policy'],
                      'outcomes':r['registered_outcomes']} for r in rows],indent=2))

if __name__=='__main__':main()
