"""Sequential execution under the filed total budget; no case retuning."""
from __future__ import annotations
import json,subprocess,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json,verify_bundle
REG=ROOT/'docs/research_notes/lushness_testbed/reserve_batch_r1/PREREGISTRATION.json'

def main():
    reg=json.loads(REG.read_text());base=ROOT/'results/local_runs/lushness_testbed'
    completed={};spent=0.
    for folder in base.glob('reserve-batch-*'):
        if not (folder/'result.json').exists() or not (folder/'PROFILE.json').exists():continue
        data=json.loads((folder/'result.json').read_text());profile=json.loads((folder/'PROFILE.json').read_text())
        cid=data['case_id'];case=next((c for c in reg['cases'] if c['id']==cid),None)
        if case is None or profile['exit_code'] or profile['cap_reason']:continue
        manifest=verify_bundle(folder)
        if manifest['config']['protocol']!=json.loads((REG.parent/case['file']).read_text()):continue
        if data.get('protocol_sha256')!=case['sha256']:continue
        if cid in completed:raise RuntimeError('Multiple complete registered case runs; explicit selection required')
        completed[cid]=str(folder);spent+=profile['wall_seconds']
    start=time.monotonic();limit=reg['limits']['total_batch_seconds'];record=REG.parent/'EXECUTION_STATUS.json'
    for case in reg['cases']:
        path=REG.parent/case['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=case['sha256']:raise ValueError('Frozen case changed')
        if case['id'] in completed:continue
        remaining=int(limit-spent-(time.monotonic()-start))
        if remaining<1:raise TimeoutError('Filed batch budget exhausted')
        atomic_json(record,{'status':'running','completed':completed,'case':case['id'],'remaining_seconds':remaining})
        job=subprocess.run([sys.executable,str(ROOT/'scripts/run_reserve_case.py'),str(path),
                            '--remaining-seconds',str(remaining)],cwd=ROOT,text=True,capture_output=True)
        if job.stdout:print(job.stdout.strip(),flush=True)
        if job.returncode:
            if job.stderr:print(job.stderr,file=sys.stderr)
            atomic_json(record,{'status':'incomplete','completed':completed,'failed_case':case['id'],'exit_code':job.returncode})
            return job.returncode
        value=json.loads(job.stdout.strip().splitlines()[-1]);completed[case['id']]=value['run']
    atomic_json(record,{'status':'complete','completed':completed,'charged_seconds':spent+time.monotonic()-start})
    print(json.dumps({'status':'complete','runs':completed}),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
