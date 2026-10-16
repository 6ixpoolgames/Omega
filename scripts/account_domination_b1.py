"""Separate completed science, numerical calibration and stopped executions."""
from datetime import datetime,timedelta,UTC
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/domination_b1'
LOCAL=ROOT/'results/local_runs/lushness_testbed/domination_b1'


def main():
    status=json.loads((DOC/'SURVEY_STATUS.json').read_text())
    science={r['identity']:r for r in status['cases'] if r['status']=='complete'}
    priority=DOC/'PRIORITY-COMPANION_STATUS.json'
    if priority.exists():
        for r in json.loads(priority.read_text())['cases']:
            if r['status']=='complete':science[r['identity']]=r
    recorded={}
    for path in (DOC/'receipts').glob('*.json'):
        r=json.loads(path.read_text());recorded[str(Path(r['run']).resolve())]=r
    starts=[];ends=[]
    for r in science.values():
        match=re.search(r'(\d{8}T\d{12}Z)$',Path(r['run']).name)
        if not match:raise ValueError('Run timestamp missing')
        time=datetime.strptime(match[1],'%Y%m%dT%H%M%S%fZ').replace(tzinfo=UTC)
        starts.append(time);ends.append(time+timedelta(seconds=r['profile']['wall_seconds']))
    unreceipted=[]
    for manifest in LOCAL.glob('*/manifest.json'):
        folder=manifest.parent
        if str(folder.resolve()) in recorded or (folder/'RESULTS.json').exists():continue
        m=json.loads(manifest.read_text())
        unreceipted.append({'run':str(folder),'case':m['config'].get('id'),
                            'last_progress':(folder/'worker.log').read_text()[-800:] if (folder/'worker.log').exists() else '',
                            'elapsed_not_inferred_from_last_progress':True})
    # A running worker also has no receipt. Only classify these as potentially
    # stopped/unreceipted until the final batch state and execution notes agree.
    storage={str(base.relative_to(ROOT)):sum(p.stat().st_size for p in base.rglob('*') if p.is_file())
             for base in (DOC,LOCAL)}
    summary={'status':status['status'],'unique_science_completed':len(science),
        'science_source_hash':status['source_hash'],
        'science_worker_wall_seconds':sum(r['profile']['wall_seconds'] for r in science.values()),
        'worker_wall_is_not_CPU_time':True,
        'science_wall_span_seconds':(max(ends)-min(starts)).total_seconds() if starts else None,
        'science_first_start':min(starts).isoformat() if starts else None,
        'science_last_end':max(ends).isoformat() if ends else None,
        'science_peak_job_bytes':max((r['profile']['peak_job_bytes'] for r in science.values()),default=0),
        'other_receipted_executions':[{'id':r['id'],'status':r['status'],'profile':r['profile']}
            for r in recorded.values() if r['identity'] not in science],
        'unreceipted_bundles':unreceipted,'storage_bytes':storage,
        'timing_scope':'Completed scientific worker sum excludes calibration/stopped work; wall span includes scheduling gaps and restarts.',
        'large_kernels_retained':False}
    (DOC/'EXECUTION_ACCOUNT.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('status','unique_science_completed','science_worker_wall_seconds','science_wall_span_seconds','science_peak_job_bytes')}))


if __name__=='__main__':main()
