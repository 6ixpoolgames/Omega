"""Verified compact evidence, fixed-table contrasts and horizon diagnostics."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json


def compact(run):
    manifest=verify_bundle(run)
    profile=json.loads((run/'PROFILE.json').read_text())
    if profile['exit_code']!=0:raise ValueError('Incomplete scientific run')
    for artifact in json.loads((run/'artifacts.json').read_text()):
        p=run/artifact['path']
        if p.stat().st_size!=artifact['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=artifact['sha256']:
            raise ValueError('Artifact mismatch')
    raw=json.loads((run/'result.json').read_text());protocol=manifest['config']['protocol']
    states=raw['state_index_schema']['states'];inv=protocol['world']['inventory']
    obs={'active':np.array([sum(x[1] for x in s) for s in states]),
         'usable':np.array([sum(inv)-sum(x[2] for x in s) for s in states])}
    rows=[]
    for policy in raw['policies']:
        lim=policy['limiting']['distributed_seed'];reference=policy['limiting']['matched_reference']
        station=lim.get('stationary_observables')
        if station is None:
            station={name:float(sum(weight*(np.array(c['stationary'])@v[c['state_indices']])
                      for weight,c in zip(lim['class_weights'],policy['classes']))) for name,v in obs.items()}
        recurrent_closed=all(all(sum(states[i][c][2] for c in range(2))==sum(inv)
                                for i in cl['state_indices']) for cl in policy['classes'])
        rows.append({'table':policy['table'],'rate':lim['rate'],'offset':lim['offset'],
            'seed_rate_excess':lim['rate']-reference['rate'],'seed_offset_excess':lim['offset']-reference['offset'],
            'stationary':{k:station[k] for k in ('active','usable')},
            'profiles_bits':policy['profiles_bits'],'closure':policy['channels']['structural']['first_entry'],
            'additional_closure':{k:v['structural_first_entry'] for k,v in policy['channels']['additional_targets'].items()},
            'occupation':{t:{k:s['occupation'][k] for k in ('active','built','usable')} for t,s in policy['surveys'].items()},
            'flows64':{k:v for k,v in policy['surveys']['64']['flows'].items() if k in (
                'drive_work','bath_heat','gross_assisted_birth','gross_basal_birth','gross_built_loss',
                'gross_sink_to_D','gross_sink_return_to_built','gross_service_fuel','gross_switch_fuel')},
            'two_assisted_probability64':policy['two_assisted_events']['probability'],
            'recovery_from_trap':policy.get('recovery_from_trap'),
            'all_recurrent_states_material_closed':recurrent_closed})
    winner=next(row for row in rows if row['table']==raw['winner']['table'])
    bench=max(rows,key=lambda row:row['occupation']['64']['active'])
    minclosure=min(row['closure']['64'] for row in rows)
    closureties=[row['table'] for row in rows if row['closure']['64']-minclosure<=1e-9]
    finite={}
    for t in ('1','4','16','64'):
        high=max(row['profiles_bits'][t]['distributed_seed'] for row in rows)
        selected=[row for row in rows if high-row['profiles_bits'][t]['distributed_seed']<=1e-9]
        finite[t]={'tables':[row['table'] for row in selected],
                   'closure_at_common64_range':[min(row['closure']['64'] for row in selected),
                                                max(row['closure']['64'] for row in selected)]}
    return {'id':protocol['id'],'world':protocol['world'],'winner':winner,'rate_ties':raw['rate_ties'],
            'benchmark':bench,'minimum_closure64':minclosure,'minimum_closure_ties':closureties,
            'finite_winners':finite,'policies':rows,'metrics':raw['metrics'],'registered':raw['registered_outcomes'],
            'provenance':{'run':run.name,'input_hash':manifest['input_hash'],'profile':profile},
            'interpretation_correction':'Use1e-9 guard for comparative probabilities; raw uniform flag was roundoff.'}


def report(runs,out):
    data=[compact(run) for run in runs];out.mkdir(parents=True,exist_ok=True)
    atomic_json(out/'SUMMARY.json',{'schema':'channel-compact-evidence/1','runs':data})
    lines=['# Channel comparison: breadth, loss and return','',
        'Complete36-table searches at3+1 inventory, same drive/material/clock and matched E8 preparations within each law. Native unfiltered count-history breadth is the only objective. The tests do not maximize protection.', '',
        '| Case | Winning inactive/active table | Rate bits/time | Active at64 | Channel closure by64 | Most protective closure by64 | Seed−reference offset bits |',
        '|---|---|---:|---:|---:|---:|---:|']
    for case in data:
        w=case['winner'];label=case['id']
        lines.append(f"| {label} | {' / '.join(w['table'])} | {w['rate']:.6f} | {w['occupation']['64']['active']:.6f} | {w['closure']['64']:.6f} | {case['minimum_closure64']:.6f} | {w['seed_offset_excess']:.6f} |")
    lines+=['', 'The uniform absorbing control gives policy-independent closure. Worn absorbing damage allows repair/control to affect loss. Reversible laws retain positive return paths; zero structural closure does not establish sustained operation.', '',
            'In absorbing laws every policy eventually loses the apparatus channel. Its carriers, gates and fixed controller hardware keep evolving. Limiting rates rank that residual process; policies need not share a rate. Root/reference comparisons use one fixed law and table, while differences across laws are mechanism contrasts.', '',
            '## Finite planning horizons','',
            'For each planning horizon, select all tied breadth-maximizing tables and report their closure at the common deadline64. This avoids comparing different observation windows.', '',
            '| Case | Planning horizon | Best table(s) | Their closure64 range |','|---|---:|---|---|']
    for case in data:
        for t,row in case['finite_winners'].items():
            lines.append(f"| {case['id']} | {t} | {row['tables']} | {row['closure_at_common64_range']} |")
    shallow=[case for case in data if 'winner_usable_fraction' in case['metrics']]
    if shallow:
        lines+=['', '## Prospective shallow-well tests','',
            'S1 predicts more stationary usable material than constant servicing; S2 predicts more than constant exporting. These are mechanistic predictions, not protection rewards.', '',
            '| Case | Usable fraction | Difference vs service | Difference vs export | First function by64 | Function present at64 |',
            '|---|---:|---:|---:|---:|---:|']
        for case in shallow:
            m=case['metrics']
            lines.append(f"| {case['id']} | {m['winner_usable_fraction']:.6f} | {m['usable_fraction_vs_service']:.6f} | {m['usable_fraction_vs_export']:.6f} | {m['firsthit_from_trap_at_horizon']:.6f} | {m['retained_from_trap_at_horizon']:.6f} |")
        lines+=['', 'Shallower wells shift the winning response toward servicing, but the breadth winner does not maximize usable stock. Recovery queries start with all material trapped, empty fuel and service gates; they are not energy-matched E8 preparation comparisons. Cross-depth values compare different physical laws. First restoration, retained function and permanent closure remain separate.', '']
    lines+=['', '## Frozen outcomes and readouts','', '| Case | Outcome | Verdict | Value |', '|---|---|---|---:|']
    for case in data:
        for verdict in case['registered']:
            lines.append(f"| {case['id']} | {verdict['id']} | {verdict['status']} | {verdict.get('value')} |")
    lines+=['', 'All policy rows, horizons, stationary usable/active expectations and resource/closure summaries are retained compactly in SUMMARY.json. Full state lists, class vectors and raw outputs stay local and reconstructible.', '',
            'The initial uniform run emitted a descriptive closure-tension flag from~1e-15 rounding differences. Its registered analytic-null check passed; interpretation uses the1e-9 guard. No primary score, predicate verdict or raw record was altered.', '',
            'Stationary observations derived from old class vectors are post-run readouts; new shallow-case predictions were filed before those runs. First-hit recovery and retained function are kept distinct. Two assisted events can include turnover and are not lineage-resolved open-ended compounding.', '',
            '## Execution','']
    for case in data:
        p=case['provenance'];e=p['profile']
        lines.append(f"- {p['run']}: {e['wall_seconds']:.2f}s, {e['peak_job_bytes']/1024**2:.2f}MiB, input `{p['input_hash']}`.")
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();report(args.runs,args.output)
