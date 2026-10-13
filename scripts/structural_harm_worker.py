"""Hard-capped worker executing only a verified prospective case."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Hard caps required')

import json
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(out):
    from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
    manifest = verify_bundle(out)
    config = manifest['config']['case']
    protocol = json.loads((ROOT / config['registration']).read_text(encoding='utf-8'))
    if config not in protocol['cases']:
        raise ValueError('Case differs from frozen registration')
    try:
        from omega_v2.testbed.experiments.structural_harm import scientific
        result = scientific(config, lambda value: atomic_json(out/'progress.json', value))
        declared = {row['path'] for row in manifest['sources']}
        for name, module in list(sys.modules.items()):
            if name.startswith('omega_v2') and getattr(module, '__file__', None):
                path = Path(module.__file__).resolve()
                if not path.is_relative_to(ROOT) or path.relative_to(ROOT).as_posix() not in declared:
                    raise RuntimeError('Unfrozen Omega import')
        verify_bundle(out)
        atomic_json(out/'result.json', {**result, 'input_hash': manifest['input_hash'],
                                       'protocol_hash': manifest['config']['protocol_hash']})
    except Exception as exc:
        atomic_json(out/'failure.json', {'type': type(exc).__name__, 'reason': str(exc),
                                        'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main(Path(sys.argv[1]))
