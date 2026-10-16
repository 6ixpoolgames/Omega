"""Render compact verified engineering evidence or scientific readout summaries."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json


def report(runs,output):
    rows=[];provenance=[]
    for run in runs:
        manifest=verify_bundle(run)
        profile=json.loads((run/'PROFILE.json').read_text())
        if profile['exit_code']!=0:
            rows.append({'status':'incomplete','run':run.name,'profile':profile});continue
        for entry in json.loads((run/'artifacts.json').read_text()):
            path=run/entry['path']
            if path.stat().st_size!=entry['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
                raise ValueError('Artifact hash mismatch')
        result=json.loads((run/'result.json').read_text())
        rows.append(result)
        provenance.append({'run':run.name,'input_hash':manifest['input_hash'],'profile':profile})
    output.mkdir(parents=True,exist_ok=True)
    atomic_json(output/'SUMMARY.json',{'results':rows})
    atomic_json(output/'PROVENANCE.json',provenance)
    lines=['# Channel extension — verified execution evidence','',
           'Engineering runs validate mechanisms and numerical capability. They do not establish an optimized policy or an ethical verdict.', '',
           '| Mode | States | Build seconds | Analysis/exponential seconds | Peak MiB | Status |',
           '|---|---:|---:|---:|---:|---|']
    for i,row in enumerate(rows):
        profile=next((p['profile'] for p in provenance if p['input_hash']==row.get('input_hash')),{})
        peak=profile.get('peak_job_bytes')
        lines.append(f"| {row.get('mode','scientific')} | {row.get('states','—')} | {row.get('build_seconds',0):.3f} | {row.get('analysis_seconds',row.get('exponential_seconds',0)):.3f} | {peak/1024**2 if peak else 0:.2f} | {row.get('audit_status',row.get('status','completed'))} |")
    lines += ['', 'Detailed closure, recovery, resource ledgers, numerical residuals and imported snapshot paths are retained in SUMMARY.json. Absorbing sinks are declared kinetic idealizations; reversible trapping retains rare returns. Thermal branching continues after apparatus closure.', '',
              'Rule A is parked. Functioning margin is a descriptive survey. No protection bonus or automatic ethical label is added.', '',
              'Profile estimates cover measured operations only; large-state entropy search and a scientific parameter grid require a separately frozen protocol.', '']
    for row in rows:
        if 'winner' not in row:continue
        lines += ['## Frozen scientific comparison','',f"Search scope: {row['scope']}.",
                  f"Winning shared inactive/active table: {row['winner']['table']}.", '',
                  '| Registered outcome | Metric | Value | Verdict |','|---|---|---:|---|']
        for verdict in row['registered_outcomes']:
            lines.append(f"| {verdict['id']} | {verdict['metric']} | {verdict.get('value')} | {verdict['status']} |")
        lines += ['', '| Table | Root | Rate bits/time | Offset bits |', '|---|---|---:|---:|']
        for policy in row['policies']:
            for root,lim in policy['limiting'].items():
                lines.append(f"| {policy['table']} | {root} | {lim['rate']:.6f} | {lim['offset']:.6f} |")
        lines += ['', 'Interpretive readouts:']+[f"- {f['text']}" for f in row['findings']]+['']
    (output/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('runs',nargs='+',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();report(args.runs,args.output)
