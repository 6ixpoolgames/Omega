"""Sequential capped regimes followed by automatic outcomes/Rule A reporting."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from report_access_extension import make_report

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    protocol=json.loads((ROOT/'docs/research_notes/lushness_testbed/access_extension/PROTOCOL.json').read_text())
    paths=[]
    for factor in protocol['active_capture_factors']:
        child=subprocess.run([sys.executable,str(ROOT/'scripts/run_access_slices.py'),'access_extension','--factor',str(factor)],
                             cwd=ROOT,text=True,capture_output=True,timeout=140)
        if child.returncode:
            print(child.stdout);print(child.stderr,file=sys.stderr)
            raise SystemExit('Regime failed: no successful-batch report generated')
        execution=json.loads(child.stdout.strip().splitlines()[-1]);paths.append(Path(execution['out']))
        print(json.dumps({'factor':factor,**execution}),flush=True)
    output=args.report or (ROOT/'results/local_runs/lushness_testbed'/('extension-report-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))
    rows=make_report(paths,output)
    (output/'BATCH.json').write_text(json.dumps({'protocol':'controlled-access-extension-r1','runs':[str(p) for p in paths]},indent=2)+'\n')
    print(json.dumps({'report':str(output),'factors':len(rows),'policies_per_factor':1296}),flush=True)

if __name__=='__main__':main()
