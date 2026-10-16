"""Engineering profile on both capacities with hard process-tree caps."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    import numpy as np

    from omega_v2.testbed.analysis.finite_classes import analyze
    from omega_v2.testbed.analysis.renewal_profile import (
        SampledHorizons,
        coordinate_shares,
        hidden_bounds,
        hidden_prepared,
        reachable_world,
    )
    from omega_v2.testbed.analysis.signal_readouts import occupation_integral
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.renewal import RenewalParameters, build_world, physical_readouts
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    rows = []
    for capacity in manifest['config']['capacities']:
        roots = [(8, 1, 0, 1, 1, 0, 1), (8, 1, 0, 1, 0, 1, 1)]
        start = perf_counter()
        compiled = reachable_world(compile_world(build_world('R', renewal=RenewalParameters(capacity=capacity))), roots)
        build_seconds = perf_counter()-start
        start = perf_counter()
        result = analyze(compiled['Q'], .25, max_dense_bytes=256*1024**2)
        solve_seconds = perf_counter()-start
        start = perf_counter()
        cache = SampledHorizons(result['P'], 16384)
        shares = coordinate_shares(result['P'], compiled['states'], (3, 4, 5, 0, 1, 2, 6))
        hidden = hidden_prepared(result['P'], [tuple(s[j] for j in (0, 1, 3, 4, 5, 6)) for s in compiled['states']])
        residual = max(result['residuals'].values())
        for root in roots:
            root_index = compiled['index'][root]
            for t in manifest['config']['horizons']:
                weights, _ = cache.occupation(root_index, round(t/.25))
                residual = max(residual, abs(float(weights @ result['row_entropy'])-float((shares @ weights).sum())))
                hidden_bounds(hidden, weights)
        query_seconds = perf_counter()-start
        start = perf_counter()
        prepared = occupation_integral(compiled['Q'], compiled['index'][roots[0]], 64.)
        physical_readouts(compiled, compiled['index'][roots[0]], 64., prepared=prepared)
        physical_seconds = perf_counter()-start
        energy_error = float(np.max(abs(compiled['Q'] @ compiled['energy']-compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))
        residual = max(residual, energy_error)
        if residual > 1e-8:
            raise ArithmeticError('Engineering residual failed')
        rows.append({'capacity': capacity, 'full_states': compiled['full_state_count'], 'reachable_states': len(compiled['states']),
                     'closed_classes': len(result['class_indices']), 'build_seconds': build_seconds,
                     'solve_seconds': solve_seconds, 'query_seconds': query_seconds,
                     'physical_seconds': physical_seconds, 'maximum_residual': residual,
                     'scientific_scores': 'withheld; no controller comparison'})
        print(json.dumps(rows[-1]), flush=True)
        del result, cache, shares, hidden, compiled
    imports = {name: str(m.__file__) for name, m in sys.modules.items() if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    (out/'RESULTS.json').write_text(json.dumps({'status': 'complete', 'input_hash': manifest['input_hash'], 'rows': rows}, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
