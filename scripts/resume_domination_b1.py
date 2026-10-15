"""Change concurrency without changing the recorded numerical source or cases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/research_notes/lushness_testbed/domination_b1'
LOCAL=ROOT/'results/local_runs/lushness_testbed/domination_b1'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--budget',type=float,default=14400)
    parser.add_argument('--ids',default='',help='Optional comma-separated frozen case IDs')
    parser.add_argument('--mode',default='survey')
    args=parser.parse_args()
    plan=json.loads((DOC/'SURVEY_PLAN.json').read_text())
    source=LOCAL/('batch-source-'+plan['source_hash'])
    payload={p.relative_to(source).as_posix():p.read_bytes() for p in source.rglob('*.py')}
    digest=hashlib.sha256(b''.join(p.encode()+b'\0'+payload[p] for p in sorted(payload))).hexdigest()
    if digest!=plan['source_hash']:raise RuntimeError('Immutable source mismatch')
    sys.path.insert(0,str(source/'scripts'))
    spec=importlib.util.spec_from_file_location('frozen_b1_coordinator',source/'scripts/run_domination_b1.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # ROOT remains the original immutable source for byte-for-byte bundles;
    # only destination paths and scheduler concurrency point to the workspace.
    module.DOC=DOC
    module.LOCAL=LOCAL
    cases=plan['cases']
    if args.ids:
        wanted=args.ids.split(',')
        by_id={case['id']:case for case in cases}
        if set(wanted)-set(by_id):raise ValueError('Unknown frozen case ID')
        cases=[by_id[name] for name in wanted]
    return module.execute(cases,args.mode,args.jobs,plan['caps']['seconds'],args.budget)

if __name__=='__main__':raise SystemExit(main())
