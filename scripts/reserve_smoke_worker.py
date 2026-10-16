"""Execute only frozen engineering source under a process-tree cap."""
from __future__ import annotations
import sys
if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Process-tree resource caps required')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import traceback
from omega_v2.testbed.workflow.manifest import verify_bundle, atomic_json


def main():
    out = Path(sys.argv[1]).resolve(); manifest=verify_bundle(out)
    if (out/'source').resolve()!=ROOT:
        raise RuntimeError('Worker must execute its frozen source')
    try:
        from omega_v2.testbed.experiments.reserve_smoke import engineering
        result=engineering(manifest['config']['engineering'],
                           lambda p:atomic_json(out/'progress.json',p))
        declared={r['path'] for r in manifest['sources']}; imports={}
        for name, module in list(sys.modules.items()):
            if name=='omega_v2' or name.startswith('omega_v2.'):
                filename=getattr(module,'__file__',None)
                if filename:
                    path=Path(filename).resolve()
                    if not path.is_relative_to(ROOT):raise RuntimeError('Live source imported')
                    relative=path.relative_to(ROOT).as_posix()
                    if relative not in declared:raise RuntimeError('Undeclared import')
                    imports[name]=relative
        verify_bundle(out)
        atomic_json(out/'result.json',{**result,'input_hash':manifest['input_hash'],'imported_sources':imports})
    except Exception as exc:
        atomic_json(out/'failure.json',{'type':type(exc).__name__,'reason':str(exc),
                                      'traceback':traceback.format_exc()})
        raise

if __name__=='__main__':main()
