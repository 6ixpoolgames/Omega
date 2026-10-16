"""Capped scientific arm or numerical profile, with frozen source bundles."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from run_bng_binding_calibration import capped

ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['profile','full','no_assistance','no_capture_benefit','neither']);args=parser.parse_args()
    spec=ROOT/'docs/research_notes/lushness_testbed/growing_population'
    protocol=json.loads((spec/'COMPARISON_PROTOCOL.json').read_text())
    out=ROOT/'results/local_runs/lushness_testbed'/('growing-'+args.mode+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]);out.mkdir(parents=True)
    files=list(spec.glob('*.md'))+list(spec.glob('*PROTOCOL.json'))+list((ROOT/'omega_v2/testbed').glob('*.py'))
    files += [ROOT/'scripts'/name for name in ('run_growing_comparison.py','growing_comparison_worker.py','run_bng_binding_calibration.py')]
    files += list((ROOT/'tests').glob('test_growing*.py'))
    files += [ROOT/'docs/research_notes/lushness_testbed/MEASUREMENT_r1.md']
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in files if p.is_file()}
    for name in sources:
        target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    manifest={'mode':args.mode,'protocol':protocol,'sources':sources,'python':sys.version,
              'packages':{n:importlib.metadata.version(n) for n in ('numpy','scipy')},
              'head':subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    manifest['input_hash']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    caps=protocol['limits_per_arm'];result=capped([sys.executable,'-u',str(ROOT/'scripts/growing_comparison_worker.py'),args.mode,str(out)],out,
        seconds=caps['wall_seconds'],memory=caps['memory_mib']*1024**2,output_cap=caps['output_mib']*1024**2)
    (out/'PROFILE.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'status.json').write_text(json.dumps({'status':'complete' if result['exit_code']==0 else 'incomplete',**result},indent=2)+'\n')
    artifacts=[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in out.rglob('*') if p.is_file() and p.name!='artifacts.json']
    (out/'artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
    print(json.dumps({'out':str(out),'input_hash':manifest['input_hash'],**result}),flush=True)
    return result['exit_code']
if __name__=='__main__':raise SystemExit(main())
