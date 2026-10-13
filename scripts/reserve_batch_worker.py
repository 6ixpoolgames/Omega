"""Verified capped worker for one frozen reserve policy search."""
from __future__ import annotations
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':raise SystemExit('Hard caps required')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import traceback,hashlib,json
from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json

def main():
    out=Path(sys.argv[1]).resolve();manifest=verify_bundle(out)
    if (out/'source').resolve()!=ROOT:raise RuntimeError('Frozen worker required')
    try:
        from omega_v2.testbed.experiments.reserve_batch import scientific
        cfg=manifest['config']['protocol'];registration=ROOT/cfg['registration']
        reg=json.loads(registration.read_text());entry=next(c for c in reg['cases'] if c['id']==cfg['id'])
        protocol_path=registration.parent/entry['file']
        if hashlib.sha256(protocol_path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Registration case hash mismatch')
        if json.loads(protocol_path.read_text())!=cfg:raise ValueError('Configuration differs from frozen case')
        result=scientific(cfg,lambda p:atomic_json(out/'progress.json',p))
        imports={};declared={s['path'] for s in manifest['sources']}
        for name,module in list(sys.modules.items()):
            if name=='omega_v2' or name.startswith('omega_v2.'):
                filename=getattr(module,'__file__',None)
                if filename:
                    path=Path(filename).resolve()
                    if not path.is_relative_to(ROOT):raise RuntimeError('Live source imported')
                    relative=path.relative_to(ROOT).as_posix()
                    if relative not in declared:raise RuntimeError('Undeclared source imported')
                    imports[name]=relative
        verify_bundle(out)
        atomic_json(out/'result.json',{**result,'protocol_sha256':entry['sha256'],
                                     'input_hash':manifest['input_hash'],'imported_sources':imports})
    except Exception as exc:
        atomic_json(out/'failure.json',{'type':type(exc).__name__,'reason':str(exc),
                                      'traceback':traceback.format_exc()})
        raise

if __name__=='__main__':main()
