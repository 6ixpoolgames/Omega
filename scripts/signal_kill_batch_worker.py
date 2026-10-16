"""Exact registered finite-history W1/W2 instrument, executed only in a snapshot."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from pathlib import Path
from time import perf_counter


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    protocol = manifest['config']['protocol']
    if protocol['status'] != 'frozen_before_scientific_ranking' or mode not in ('smoke', 'science'):
        raise ValueError('Registered experiment and declared mode required')
    if manifest['config']['mode'] != mode:
        raise ValueError('Execution mode differs from frozen manifest')
    import numpy as np
    from scipy.linalg import expm

    from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits
    from omega_v2.testbed.analysis.observed_history import (
        averaged_observation_bounds,
        exact_prefix_entropy,
        projected_offset_bounds,
        sampled_occupations,
    )
    from omega_v2.testbed.analysis.signal_readouts import coordinate_row_shares, physical_readouts
    from omega_v2.testbed.aversive_signals import SignalParameters, build_world
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.experiments.signal_kills import qualify

    cases = protocol['cases']
    if mode == 'smoke':
        cases = [case for case in cases if case['id'] in protocol['smoke_case_ids']]
    rows = []
    qreg = protocol['qualification']
    residual_max = 0.
    for case_number, case in enumerate(cases):
        parameters = SignalParameters(**case['parameters'])
        worlds = {arm: compile_world(build_world(arm, parameters)) for arm in case['arms']}
        for arm, compiled in worlds.items():
            ref_arm = 'B' if arm in ('A', 'B', 'C') else ('N' if case['family'] == 'W1' else 'N_prime')
            reference = worlds[ref_arm]
            root = compiled['index'][tuple(case['root'])]
            track_kernels = (expm(compiled['Q'].toarray()*qreg['tracking']['window']),
                             expm(reference['Q'].toarray()*qreg['tracking']['window']))
            diagnostics = {}
            for horizon in protocol['horizons']:
                readouts = physical_readouts(compiled, reference, root, horizon,
                    window=qreg['tracking']['window'],
                    decline_tolerance=qreg['tracking']['decline_tolerance'], prepared=track_kernels)
                readouts['qualification'] = qualify(readouts, qreg)
                readouts['physical_jump_count'] = sum(readouts['event_counts'][name]
                                                     for name in compiled['families'])
                diagnostics[str(horizon)] = readouts
            for cadence in protocol['cadences']:
                started = perf_counter()
                result = analyze(compiled['Q'], cadence, max_dense_bytes=128*1024**2)
                kernel = result['P']
                labels = [tuple(state[j] for j in (0, 1, 3, 4)) for state in compiled['states']]
                counts = [round(horizon/cadence) for horizon in protocol['horizons']]
                occupation = sampled_occupations(kernel, root, counts)
                row_shares = coordinate_row_shares(kernel, compiled['states'],
                                                   tuple(protocol['coordinate_order']))
                asymptotic = projected_offset_bounds(result, labels, root)
                horizons = {}
                for horizon, count in zip(protocol['horizons'], counts):
                    weights, endpoint = occupation[count]
                    full = float(weights @ result['row_entropy'])
                    hidden = averaged_observation_bounds(kernel, labels, weights)
                    shares = row_shares @ weights
                    chain_residual = abs(float(shares.sum())-full)
                    if chain_residual > protocol['tolerances']['residual']:
                        raise ArithmeticError('Destination chain-rule closure failed')
                    residual_max = max(residual_max, chain_residual)
                    if mode == 'smoke':
                        # Recompute a short prefix independently and with exact HMM enumeration.
                        short_weights, _ = sampled_occupations(kernel, root, [2])[2]
                        bounds = averaged_observation_bounds(kernel, labels, short_weights)
                        exact = exact_prefix_entropy(kernel, labels, root, 2, max_prefixes=50000)
                        reference_bits = finite_history_bits(kernel, 2)[root]
                        if (not bounds['lower_bits']-1e-9 <= exact <= bounds['upper_bits']+1e-9
                                or abs(short_weights @ result['row_entropy']-reference_bits) > 1e-9):
                            raise ArithmeticError('Independent exact-prefix check failed')
                    horizons[str(horizon)] = {
                        'resolved': {'lower_bits': full, 'upper_bits': full},
                        'signal_merged_bounds': hidden,
                        'coordinate_bits': shares.tolist(),
                        'endpoint_survival': float(sum(endpoint[i] for i, state in enumerate(
                            compiled['states']) if state[0])),
                        'readouts': diagnostics[str(horizon)],
                    }
                residual_max = max(residual_max, *result['residuals'].values())
                energy_residual = float(np.max(abs(compiled['Q'] @ compiled['energy']
                    -compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))
                residual_max = max(residual_max, energy_residual)
                row = {'case': case['id'], 'family': case['family'], 'arm': arm,
                       'cadence': cadence, 'states': len(compiled['states']),
                       'seconds': perf_counter()-started,
                       'numerical_residuals': {**result['residuals'], 'energy': energy_residual}}
                if mode == 'science':
                    row.update({'horizons': horizons,
                        'rate_bits_per_time': float(result['rate_per_step'][root]/cadence),
                        'resolved_offset': float(result['offset'][root]),
                        'merged_offset': asymptotic})
                else:
                    row['scientific_scores'] = 'withheld from engineering gate'
                rows.append(row)
        print(json.dumps({'mode': mode, 'case': case['id'], 'completed_rows': len(rows)}), flush=True)
    if residual_max > protocol['tolerances']['residual']:
        raise ArithmeticError('Registered numerical residual gate failed')
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'complete', 'mode': mode, 'input_hash': manifest['input_hash'],
              'source_hash': manifest['source_hash'], 'rows': rows,
              'maximum_numerical_residual': residual_max, 'imports': imports,
              'protocol': protocol}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
