"""Hard-capped physical-moment matching; no entropy or scientific ranking."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.signal_controls import calibrate
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    plan = manifest['config']['plan']
    if plan['status'] != 'frozen_before_physical_matching':
        raise ValueError('Frozen matching plan required')
    fits = []
    for case in plan['parents']:
        result = calibrate(SignalParameters(**case['parameters']), case['root'],
                           plan['horizon'], plan['relative_tolerance'])
        fits.append({'parent': case['id'], **result})
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'complete' if all(fit['success'] for fit in fits) else 'matching_failed',
              'input_hash': manifest['input_hash'], 'source_hash': manifest['source_hash'],
              'plan': plan, 'fits': fits, 'imports': imports}
    (out/'MATCHING_RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n',
                                           encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
