"""Numerically compare a fresh rebuild, using a hard-capped frozen snapshot."""
from __future__ import annotations
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':
    raise SystemExit('Hard caps required')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import hashlib
import traceback
from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json


def main():
    out=Path(sys.argv[1]).resolve();manifest=verify_bundle(out)
    if (out/'source').resolve()!=ROOT:raise RuntimeError('Frozen source required')
    cfg=manifest['config']
    try:
        from reconstruct_artifact import rebuild,verify
        target=Path(cfg['original']).resolve();base=Path(cfg['live_root']).resolve()
        if not target.is_relative_to(base):raise ValueError('Original path outside workspace')
        if hashlib.sha256(target.read_bytes()).hexdigest()!=cfg['original_sha256']:
            raise AssertionError('Original evidence changed')
        arrays=rebuild(cfg['artifact']);checks=verify(arrays,target)
        verify_bundle(out)
        atomic_json(out/'verification.json',{'status':'verified','artifact':cfg['artifact'],
                    'original_sha256':cfg['original_sha256'],'checks':checks,
                    'input_hash':manifest['input_hash']})
    except Exception as exc:
        atomic_json(out/'failure.json',{'type':type(exc).__name__,'reason':str(exc),
                                      'traceback':traceback.format_exc()})
        raise

if __name__=='__main__':main()
