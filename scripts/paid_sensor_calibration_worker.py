"""Frozen physical calibration: no history entropy is evaluated."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.exploration import ExplorationParameters
    from omega_v2.testbed.paid_sensing import SensorParameters, calibrate
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    p = manifest['config']['plan']
    fits = []
    for g in p['groups']:
        fit = calibrate(SignalParameters(**g['physiology']), ExplorationParameters(**g['parameters']),
                        SensorParameters(**g['sensor']), g['roots'], p['horizon'], p['relative_tolerance'])
        fits.append({'group': g['id'], **fit})
        print(json.dumps({'group': g['id'], 'success': fit['success'], 'relative_error': fit['relative_error']}), flush=True)
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    result = {'status': 'complete' if all(f['success'] for f in fits) else 'incomplete',
              'input_hash': manifest['input_hash'], 'source_hash': manifest['source_hash'], 'plan': p,
              'fits': fits, 'imports': imports}
    (out/'MATCHING_RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return 0 if result['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1])))
