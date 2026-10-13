"""Worker imports and executes only its verified snapshot under process caps."""
from __future__ import annotations
import sys
if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Process-tree resource caps required')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import json
import traceback
from omega_v2.testbed.workflow.manifest import verify_bundle, atomic_json


def main():
    out=Path(sys.argv[1]).resolve();manifest=verify_bundle(out)
    if (out/'source').resolve()!=ROOT:raise RuntimeError('Worker is not the frozen copy')
    try:
        from omega_v2.testbed.experiments.channel_comparison import engineering,scientific
        cfg=manifest['config'];mode=cfg['mode']
        result=(scientific(cfg['protocol'],lambda p:atomic_json(out/'progress.json',p))
                if mode=='scientific' else engineering(mode,cfg['engineering']))
        imports={}
        declared={r['path'] for r in manifest['sources']}
        for name,module in list(sys.modules.items()):
            if name=='omega_v2' or name.startswith('omega_v2.'):
                filename=getattr(module,'__file__',None)
                if filename:
                    path=Path(filename).resolve()
                    if not path.is_relative_to(ROOT):raise RuntimeError(f'Live source imported: {name}')
                    relative=path.relative_to(ROOT).as_posix()
                    if relative not in declared:raise RuntimeError(f'Unlisted source imported: {relative}')
                    imports[name]=relative
        verify_bundle(out)
        result.update(input_hash=manifest['input_hash'],imported_sources=imports)
        atomic_json(out/'result.json',result)
    except Exception as exc:
        atomic_json(out/'failure.json',{'status':'numerical_failure' if isinstance(exc,ArithmeticError) else 'failed',
                   'type':type(exc).__name__,'reason':str(exc),'traceback':traceback.format_exc()})
        raise

if __name__=='__main__':main()
