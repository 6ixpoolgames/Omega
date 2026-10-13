"""Verify rebuildability before local untracking; never deletes or changes Git."""
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import sys,uuid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from omega_v2.testbed.workflow.manifest import freeze_bundle,atomic_json
from omega_v2.testbed.workflow.runner import run_frozen

ARTIFACTS={
    **{f'catalytic-binding-{b}':f'catalytic_binding_v0/barrier_{b}_kernels.npz' for b in (0,1,2)},
    'local-flow':'local_flow_v0/kernels.npz','fuel-flow':'fuel_flow_v0/kernels.npz',
    'thermal-binding-thermal':'thermal_binding_v0/thermal_kernels.npz',
    'thermal-binding-0.1':'thermal_binding_v0/mobile_0.1_kernels.npz',
    'thermal-binding-1.0':'thermal_binding_v0/mobile_1.0_kernels.npz',
    **{f'catalytic-history-{b}':f'catalytic_history_v0/barrier_{b}_histories.npz' for b in (0,1,2)},
}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('artifact',choices=ARTIFACTS)
    args=parser.parse_args();target=ROOT/'docs/research_notes/omega_v2'/ARTIFACTS[args.artifact]
    cfg={'artifact':args.artifact,'original':str(target),'live_root':str(ROOT),
         'original_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    out=ROOT/'results/local_runs/artifact_reconstruction'/(args.artifact+'-'+
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])
    files=list((ROOT/'omega_v2/finite').glob('*.py'))+list((ROOT/'omega_v2/validation').glob('*.py'))
    files+=list((ROOT/'omega_v2/testbed/workflow').glob('*.py'))
    files += [ROOT/p for p in ('omega_v2/__init__.py','omega_v2/testbed/__init__.py',
          'scripts/reconstruct_artifact.py','scripts/artifact_reconstruction_worker.py',
          'scripts/verify_artifact_reconstruction.py','scripts/run_bng_binding_calibration.py',
          'docs/implementation/artifact_reconstruction/spatial_binding_thermal_20261003.py')]
    freeze_bundle(ROOT,out,[p.relative_to(ROOT).as_posix() for p in files],cfg)
    profile=run_frozen(out,'scripts/artifact_reconstruction_worker.py',[str(out)],
                       {'seconds':120,'memory':1024**3,'output_cap':256*1024**2})
    atomic_json(out/'PROFILE.json',profile)
    print(json.dumps({'run':str(out),**profile}))
    return profile['exit_code']

if __name__=='__main__':raise SystemExit(main())
