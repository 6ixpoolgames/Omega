"""Capped runner for preregistered assembly and controlled access slices."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import uuid
from run_bng_binding_calibration import capped

ROOT=Path(__file__).resolve().parents[1]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('fixture',choices=['assembly','controlled','smoke','access_extension','extension_smoke'])
    parser.add_argument('--factor',type=int,default=6)
    args=parser.parse_args()
    folder='controlled' if args.fixture=='smoke' else ('access_extension' if args.fixture=='extension_smoke' else args.fixture)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out=ROOT/'results/local_runs/lushness_testbed'/f'{args.fixture}-{stamp}'
    out.mkdir(parents=True)
    files=list((ROOT/f'docs/research_notes/lushness_testbed/{folder}').glob('*'))
    files+=list((ROOT/'omega_v2/testbed').glob('*.py'))
    files+=[ROOT/'scripts/run_access_slices.py',ROOT/'scripts/access_slices_worker.py',
            ROOT/'scripts/run_bng_binding_calibration.py',ROOT/'docs/research_notes/lushness_testbed/MEASUREMENT_r1.md']
    files+=list((ROOT/'tests').glob('test_*slice.py'))
    if folder=='access_extension':
        files.extend((ROOT/'docs/research_notes/lushness_testbed/controlled').glob('*'))
        files.extend((ROOT/'tests').glob('test_*assessment.py'))
        files.extend((ROOT/'tests').glob('test_access_extension.py'))
        files.extend((ROOT/'tests').glob('test_access_extension_report.py'))
        files.extend(ROOT/'scripts'/name for name in ('report_access_extension.py','run_access_extension_batch.py'))
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in files if p.is_file()}
    for relative in sources:
        target=out/'source'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
    engine=Path(importlib.util.find_spec('bionetgen').origin).parent/'bng-win'
    manifest={'fixture':args.fixture,'factor':args.factor if folder=='access_extension' else None,'sources':sources,'python':sys.version,'platform':platform.platform(),
              'engine_version':(engine/'VERSION').read_text().strip(),
              'engine_hashes':{p.relative_to(engine).as_posix():digest(p) for p in engine.rglob('*') if p.is_file()},
              'perl_hash':digest(Path('C:/Program Files/Git/usr/bin/perl.exe')),
              'packages':{n:importlib.metadata.version(n) for n in ('numpy','scipy','bionetgen')},
              'head':subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'caps':{'seconds':120,'memory_mib':1024,'output_mib':256}}
    manifest['input_hash']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result=capped([sys.executable,'-u',str(ROOT/'scripts/access_slices_worker.py'),args.fixture,str(out),str(args.factor)],out)
    (out/'PROFILE.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'execution_status.json').write_text(json.dumps({'status':'complete' if result['exit_code']==0 else 'incomplete',**result},indent=2)+'\n')
    artifacts=[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
               for p in out.rglob('*') if p.is_file() and p.name!='artifacts.json']
    (out/'artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
    print(json.dumps({'out':str(out),'input_hash':manifest['input_hash'],**result}),flush=True)
    return result['exit_code']

if __name__=='__main__':raise SystemExit(main())
