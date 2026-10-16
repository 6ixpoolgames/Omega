"""Capped flow-only calibration or frozen equal-accepted-work comparison."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from dataclasses import replace
from pathlib import Path


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    import numpy as np
    from scipy.optimize import brentq

    from omega_v2.testbed.analysis.finite_classes import _stationary
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.compounding import CompoundingParameters, build_world
    from omega_v2.testbed.workflow.manifest import verify_bundle

    manifest = verify_bundle(out)
    config = manifest['config']
    if config['mode'] != 'calibration':
        from compounding_worker import main as existing_worker
        return existing_worker(out)

    curves, functions = [], {}
    for capacity in config['capacities']:
        for mechanism in ('loop', 'basal'):
            p = CompoundingParameters(capacity=capacity)

            def accepted(rate, parameters=p, arm=mechanism):
                c = compile_world(build_world(replace(parameters, supply_rate=rate), arm))
                pi = _stationary(c['Q'])
                return float(pi @ c['flows']['resource_work'])

            functions[(capacity, mechanism)] = accepted
            supplies = np.geomspace(*config['source_bracket'], config['calibration_samples'])
            values = [accepted(float(s)) for s in supplies]
            if min(np.diff(values)) < -config['flow_tolerance']:
                raise RuntimeError('Nonmonotone flow calibration requires a new physical matching plan')
            curves.append({'capacity': capacity, 'mechanism': mechanism,
                           'supply': supplies.tolist(), 'accepted_work': values})
    lower = max(row['accepted_work'][0] for row in curves)
    upper = min(row['accepted_work'][-1] for row in curves)
    if upper-lower < 100*config['flow_tolerance']:
        raise RuntimeError('No adequate common feasible accepted-work range')
    targets = [lower+fraction*(upper-lower) for fraction in config['interior_fractions']]
    matches = []
    for capacity in config['capacities']:
        for target in targets:
            for mechanism in ('loop', 'basal'):
                fn = functions[(capacity, mechanism)]
                rate = brentq(lambda r, f=fn, value=target: f(r)-value,
                              *config['source_bracket'], xtol=1e-12)
                flow = fn(rate)
                if abs(flow-target) > config['flow_tolerance']:
                    raise ArithmeticError('Accepted-work matching failed')
                matches.append({'capacity': capacity, 'mechanism': mechanism, 'target': target,
                                'supply_rate': rate, 'accepted_work': flow,
                                'absolute_match_error': abs(flow-target)})
    result = {'status': 'complete', 'input_hash': manifest['input_hash'],
              'source_hash': manifest['source_hash'], 'rankings_inspected': False,
              'common_interval': [lower, upper], 'targets': targets,
              'curves': curves, 'matches': matches,
              'monotonicity_scope': 'checked calibration points, not a global analytic proof'}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
