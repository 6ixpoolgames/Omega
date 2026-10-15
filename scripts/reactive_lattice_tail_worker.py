"""Post-run horizon audit; no changed physics or rescoring of filed predictions."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from pathlib import Path


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    import numpy as np
    from scipy.sparse.linalg import expm_multiply

    from omega_v2.testbed.analysis.same_law_profile import IrreducibleQueries
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.reactive_lattice import (
        LatticeParameters,
        build_world,
        organized_root,
        reference_masks,
    )
    from omega_v2.testbed.workflow.manifest import verify_bundle

    manifest = verify_bundle(out)
    config = manifest['config']
    p = LatticeParameters(**config['law']['parameters'])
    c = compile_world(build_world(p))
    query = IrreducibleQueries(c['Q'])
    seed = np.zeros(len(c['states']))
    seed[c['index'][organized_root(p)]] = 1.
    refs = reference_masks(c, organized_root(p))
    b = []
    residuals = []
    for dt in config['cadences']:
        sampled = query.sampled(dt, [1024])
        b.append(sampled['offset'])
        residuals.append(sampled['residuals']['poisson'])
    offsets = np.column_stack(b)
    rows, horizons = [], []
    for t in [1024]+config['extension_horizons']:
        backward = expm_multiply(c['Q']*t, offsets)
        bounds = np.ptp(backward, axis=0)
        accuracy = np.array([2*round(t/dt)*r for dt, r in zip(config['cadences'], residuals)])
        # Oscillation bounds every difference of root-mixture expectations of
        # exp(QT)b. Validated floating-point residuals are reported separately.
        horizons.append({'horizon': t, 'global_tail_oscillation': bounds.tolist(),
                         'sampled_poisson_accumulated_pair_error_bound': accuracy.tolist()})
        for j, dt in enumerate(config['cadences']):
            for name, mu in refs.items():
                contrast = seed-mu
                offset = float(contrast @ offsets[:, j])
                tail = float(contrast @ backward[:, j])
                rows.append({'reference': name, 'cadence': dt, 'horizon': t,
                    'delta_bits': offset-tail, 'delta_offset': offset,
                    'actual_tail_bits': tail, 'all_root_tail_oscillation': float(bounds[j]),
                    'sampled_poisson_error_bound': float(accuracy[j])})
        print(json.dumps({'law': config['law']['id'], 'horizon': t,
                          'max_global_tail': float(bounds.max())}), flush=True)
        if t > 1024 and max(bounds+accuracy) < config['tail_tolerance_bits']:
            break
    result = {'law': config['law'], 'rows': rows, 'horizons': horizons,
        'converged_at_last_query': bool(max(bounds+accuracy) < config['tail_tolerance_bits']),
        'last_horizon': t, 'input_hash': manifest['input_hash'],
        'source_hash': manifest['source_hash'],
        'scope': 'retrospective finite-history continuation and numerical tail audit; original predictions unchanged',
        'proof_scope': 'Markov oscillation bound plus validated numerical residuals; not interval-arithmetic certification'}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
