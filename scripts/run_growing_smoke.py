"""Capped engineering smoke with frozen source snapshots; no optimizer."""
from __future__ import annotations
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
    spec=ROOT/'docs/research_notes/lushness_testbed/growing_population'
    protocol=json.loads((spec/'SMOKE_PROTOCOL.json').read_text())
    if protocol['status']!='frozen_engineering_only':raise RuntimeError('Unfrozen engineering protocol')
    out=ROOT/'results/local_runs/lushness_testbed'/('growing-smoke-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]);out.mkdir(parents=True)
    files=list(spec.glob('*'))+list((ROOT/'omega_v2/testbed').glob('*.py'))
    files += [ROOT/'scripts'/n for n in ('run_growing_smoke.py','growing_smoke_worker.py','run_bng_binding_calibration.py')]
    files += [ROOT/'tests/test_growing_population.py',ROOT/'docs/research_notes/lushness_testbed/controlled/PROTOCOL.json']
    files += [ROOT/'docs/research_notes/lushness_testbed/MEASUREMENT_r1.md']
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in files if p.is_file()}
    for name in sources:
        target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    manifest={'scope':'engineering smoke only','protocol':protocol,'sources':sources,'python':sys.version,
              'packages':{n:importlib.metadata.version(n) for n in ('numpy','scipy')},
              'head':subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    manifest['input_hash']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    caps=protocol['limits'];profile=capped([sys.executable,'-u',str(ROOT/'scripts/growing_smoke_worker.py'),str(out)],out,
          seconds=caps['wall_seconds'],memory=caps['memory_mib']*1024**2,output_cap=caps['output_mib']*1024**2)
    (out/'PROFILE.json').write_text(json.dumps(profile,indent=2)+'\n')
    (out/'status.json').write_text(json.dumps({'status':'passed' if profile['exit_code']==0 else 'incomplete',**profile},indent=2)+'\n')
    files=[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in out.rglob('*') if p.is_file() and p.name!='artifacts.json']
    (out/'artifacts.json').write_text(json.dumps(files,indent=2)+'\n')
    print(json.dumps({'out':str(out),'input_hash':manifest['input_hash'],**profile}),flush=True)
    return profile['exit_code']
if __name__=='__main__':raise SystemExit(main())
