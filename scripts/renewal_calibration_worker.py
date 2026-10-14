"""Per-primary-law physical moment fit, before any scientific ranking."""
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
    from omega_v2.testbed.paid_sensing import SensorParameters
    from omega_v2.testbed.renewal import RenewalParameters, calibrate
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    law, p = manifest['config']['law'], manifest['config']['plan']
    fit = calibrate(SignalParameters(**law['physiology']), ExplorationParameters(**law['parameters']),
                    SensorParameters(**law['sensor']), RenewalParameters(**law['renewal']),
                    law['roots'], p['horizon'], p['relative_tolerance'])
    (out/'MATCHING_RESULTS.json').write_text(json.dumps({'input_hash': manifest['input_hash'],
        'source_hash': manifest['source_hash'], 'law': law, 'fit': fit}, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'law': law['id'], 'fit_success': fit['success'], 'relative_error': fit['relative_error']}), flush=True)
    return 0 if fit['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1])))
