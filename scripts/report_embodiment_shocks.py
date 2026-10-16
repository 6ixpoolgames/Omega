"""Verify and compact the preregistered embodiment/shock batch."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from analyze_channel_batch import compact
from omega_v2.testbed.analysis.registry import score_outcomes
from omega_v2.testbed.workflow.manifest import atomic_json

def summarize(runs,registration,out):
    registration=registration.resolve()
    reg=json.loads(registration.read_text());records={}
    for case in reg['cases']:
        # The preregistration generator hashes UTF-8 text before Windows writes
        # CRLF. Frozen source manifests separately verify actual on-disk bytes.
        payload=(registration.parent/case['file']).read_text(encoding='utf-8').encode('utf-8')
        if hashlib.sha256(payload).hexdigest()!=case['sha256']:raise ValueError('Preregistration protocol mismatch')
    for run in runs:
        data=compact(run);raw=json.loads((run/'result.json').read_text())
        name=data['id'].removeprefix('embodiment-r1-')
        definition=next(c for c in reg['cases'] if c['case']==name)
        snapshot=json.loads((run/'manifest.json').read_text())
        registration_path=registration.relative_to(ROOT).as_posix()
        frozen_registration=next(s for s in snapshot['sources'] if s['path']==registration_path)
        if frozen_registration['sha256']!=hashlib.sha256(registration.read_bytes()).hexdigest():
            raise ValueError('Preregistration differs from the frozen source bundle')
        frozen=snapshot['config']['protocol']
        if frozen!=json.loads((registration.parent/definition['file']).read_text()):raise ValueError('Run protocol differs from registered case')
        policy_map={tuple(p['table']):p for p in raw['policies']}
        for row in data['policies']:
            original=policy_map[tuple(row['table'])]
            row['shock_readout']=original['shock_readout'];row['alias_of']=original.get('alias_of')
            row['diagnostic_root_limiting']={k:{'rate':v['rate'],'offset':v['offset']} for k,v in original['limiting'].items() if k=='all_trapped_diagnostic'}
        w=data['winner'];survey=policy_map[tuple(w['table'])]['shock_readout']
        activeweight=frozen['controllers']['responses'][w['table'][1]][0]
        probe=survey['common_probe_stationary']['function_loss_given_pre_active']
        values={'active_service_weight':activeweight,'stationary_exposure':survey['exposed_expected'],
                'stationary_common_probe_reserve':None if probe is None else 1-probe,
                'policy_rate_spread':raw['metrics']['policy_rate_spread'],
                'closure64_horizon1_minus_horizon64':data['finite_winners']['1']['closure_at_common64_range'][1]-data['finite_winners']['64']['closure_at_common64_range'][1]}
        data['upgrade_metrics']=values;data['unique_kernels']=raw['unique_kernels']
        data['winner_shock_readout']=survey;records[name]=data
    if set(records)!=set(c['case'] for c in reg['cases']):raise ValueError('Incomplete registered batch')
    verdicts=[]
    for pred in reg['hypotheses']:
        metric=pred['metric']
        if 'lhs' in pred:
            lhs=records[pred['lhs']]['upgrade_metrics'][metric];rhs=records[pred['rhs']]['upgrade_metrics'][metric]
            value=None if lhs is None or rhs is None else lhs-rhs
            threshold=0.
        else:value=records[pred['case']]['upgrade_metrics'][metric];threshold=pred['threshold']
        spec={'id':pred['id'],'metric':'comparison','operator':pred['operator'],'threshold':threshold,'tolerance':reg['tolerance']}
        verdicts.extend(score_outcomes({'comparison':value},[spec]))
    out.mkdir(parents=True,exist_ok=True)
    atomic_json(out/'SUMMARY.json',{'schema':'embodiment-shocks-compact/1','registration':reg,'cases':records,'registered_comparisons':verdicts})
    lines=['# Embodied control and matched shocks','',
      'Seven frozen exhaustive36-table searches. Exact equal-kernel and equal-ledger aliases are retained; only unique models are evaluated. Native sampled physical count histories remain the sole objective, ranked by long-run rate then root offset. Random damage is included.','',
      '| Case | Winner inactive / active | Unique models | Rate bits/time | Active at64 | Closure64 | Stationary exposed | Stationary function probability | Common-probe conditional reserve |',
      '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for name,c in records.items():
        w=c['winner'];m=c['upgrade_metrics'];reserve=m['stationary_common_probe_reserve']
        inactive='inoperative' if name!='legacy_reversible' else w['table'][0]
        presence=c['winner_shock_readout']['active_before_mass']
        lines.append(f"| {name} | {inactive} / {w['table'][1]} | {c['unique_kernels']} | {w['rate']:.6f} | {w['occupation']['64']['active']:.6f} | {w['closure']['64']:.6f} | {m['stationary_exposure']:.6f} | {presence:.6f} | {'undefined' if reserve is None else f'{reserve:.6f}'} |")
    lines+=['','## Prospective comparisons','','| Hypothesis | Verdict | Value (difference where applicable) |','|---|---|---:|']
    for v in verdicts:lines.append(f"| {v['id']} | {v['status']} | {v['value']} |")
    lines+=['','Reserve uses one identical hypothetical .5 hit-probability shock across all winning state distributions: probability that some active apparatus remains, conditional on function before the probe. It avoids comparing different native shock severities as though their per-arrival risks were directly interchangeable. Native-clock risks are retained separately. Absorbing stationary function is absent; inspect finite-deadline diagnostics instead.','',
      'Increasing exposure is a diagnostic flag. It does not prove the optimizer farms damage: more machinery can also produce more useful continuation. Family event flux is not an additive decomposition of sampled-state entropy. Independent and correlated damage have equal conditional first moments, but distinct laws and distinct history breadth.','',
      'Conditional reserve can improve while function is present less often. Read its registered verdict alongside stationary function probability and unconditional post-probe function probability (the product of function probability and conditional reserve), not as proof of improved overall resilience. Embodied inactive instructions are all physically equivalent; their printed raw table names are alias labels without operational meaning.','',
      'Basal gate relaxation is policy-independent and thermally symmetric because gate energy is zero. Commanded switching has its existing fuel accounting and requires a/M functioning capacity. Separate controller memory/sensing is not modeled. The chemical boundary and passive carrier motion continue after apparatus collapse. No tail subtraction or survival bonus is used.','',
      'Shocks are an external nonequilibrium energy boundary. Their signed energy transfers are kept separate from chemical drive work; thermal balance is asserted only for the isolated thermal modules, not the driven shocked world. Four material slots cannot establish open-ended compounding. The matched preparation reference is a coarse count ensemble, not molecular gas.','',
      '## Standard controls','','| Case | Passive idle rate | Always service rate | Always export rate | Half/half rate | Best service/export deterministic rate |','|---|---:|---:|---:|---:|---:|']
    for name,c in records.items():
        rowmap={tuple(r['table']):r for r in c['policies']}
        rates=[rowmap[(x,x)]['rate'] for x in ('idle','service','export','mix50')]
        best=max(r['rate'] for r in c['policies'] if all(t in ('service','export') for t in r['table']))
        lines.append('| '+name+' | '+' | '.join(f'{x:.6f}' for x in [*rates,best])+' |')
    lines+=['','## Provenance','']
    for c in records.values():
        p=c['provenance'];e=p['profile']
        lines.append(f"- {p['run']}: {e['wall_seconds']:.2f}s, {e['peak_job_bytes']/1024**2:.2f}MiB; input `{p['input_hash']}`.")
    lines+=['','Full compact policy profiles, aliases, failures and diagnostic roots are in SUMMARY.json. Raw state/class vectors remain ignored local artifacts. No prior run has been overwritten or rescored.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('runs',nargs='+',type=Path)
    parser.add_argument('--registration',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();summarize(args.runs,args.registration,args.output)
