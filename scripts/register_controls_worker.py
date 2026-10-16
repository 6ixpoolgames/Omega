"""Frozen four-arm register-control instrument. No retuning after ranking."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    protocol = manifest['config']['protocol']
    if mode not in ('smoke', 'science') or protocol['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen scientific registration required')
    if manifest['config']['mode'] != mode:
        raise ValueError('Mode differs from frozen manifest')
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
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.signal_controls import build_world, moments

    cases = protocol['cases']
    if mode == 'smoke':
        cases = [case for case in cases if case['id'] in protocol['smoke_cases']]
    rows = []
    residual_max = 0.
    for case in cases:
        p = SignalParameters(**case['parameters'])
        for arm in protocol['arms']:
            compiled = compile_world(build_world(arm, p,
                **({'on_rate': case['on_rate'], 'off_rate': case['off_rate']} if arm == 'B_R' else {})))
            actual_parameters = SignalParameters(**compiled['metadata']['parameters'])
            reference = compile_world(build_world('B', actual_parameters))
            root = compiled['index'][tuple(case['root'])]
            window = protocol['qualification']['tracking']['window']
            track_kernels = (expm(compiled['Q'].toarray()*window),
                             expm(reference['Q'].toarray()*window))
            diagnostics = {}
            moment_profiles = {}
            for horizon in protocol['horizons']:
                diagnostics[str(horizon)] = physical_readouts(compiled, reference, root, horizon,
                    window=window,
                    decline_tolerance=protocol['qualification']['tracking']['decline_tolerance'],
                    prepared=track_kernels)
                moment_profiles[str(horizon)] = moments(compiled, root, horizon)
            for cadence in protocol['cadences']:
                result = analyze(compiled['Q'], cadence, max_dense_bytes=128*1024**2)
                kernel = result['P']
                labels = [tuple(state[j] for j in (0, 1, 3, 4)) for state in compiled['states']]
                counts = [round(horizon/cadence) for horizon in protocol['horizons']]
                occupation = sampled_occupations(kernel, root, counts)
                share_rows = coordinate_row_shares(kernel, compiled['states'],
                                                    tuple(protocol['coordinate_order']))
                asymptotic = projected_offset_bounds(result, labels, root)
                profiles = {}
                for horizon, count in zip(protocol['horizons'], counts):
                    weights, _ = occupation[count]
                    full = float(weights @ result['row_entropy'])
                    shares = share_rows @ weights
                    residual_max = max(residual_max, abs(float(shares.sum())-full))
                    profiles[str(horizon)] = {
                        'resolved': {'lower_bits': full, 'upper_bits': full},
                        'signal_merged_bounds': averaged_observation_bounds(kernel, labels, weights),
                        'coordinate_bits': shares.tolist(),
                        'readouts': diagnostics[str(horizon)], 'moments': moment_profiles[str(horizon)]}
                if mode == 'smoke':
                    weights, _ = sampled_occupations(kernel, root, [2])[2]
                    bounds = averaged_observation_bounds(kernel, labels, weights)
                    exact = exact_prefix_entropy(kernel, labels, root, 2, max_prefixes=50000)
                    if (not bounds['lower_bits']-1e-9 <= exact <= bounds['upper_bits']+1e-9
                            or abs(weights @ result['row_entropy']-finite_history_bits(kernel, 2)[root]) > 1e-9):
                        raise ArithmeticError('Independent short-prefix reference failed')
                energy_error = float(np.max(abs(compiled['Q'] @ compiled['energy']
                    -compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))
                residual_max = max(residual_max, energy_error, *result['residuals'].values())
                row = {'case': case['id'], 'parent': case['parent'], 'arm': arm,
                       'cadence': cadence, 'upkeep_ratio': case['upkeep_ratio'],
                       'states': len(compiled['states']),
                       'residuals': {**result['residuals'], 'energy': energy_error}}
                if mode == 'science':
                    row.update({'horizons': profiles,
                        'rate_bits_per_time': float(result['rate_per_step'][root]/cadence),
                        'resolved_offset': float(result['offset'][root]), 'merged_offset': asymptotic})
                else:
                    row['scientific_scores'] = 'withheld from engineering gate'
                rows.append(row)
        print(json.dumps({'mode': mode, 'case': case['id'], 'completed_rows': len(rows)}), flush=True)
    if residual_max > protocol['tolerances']['residual']:
        raise ArithmeticError('Registered numerical gate failed')
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'complete', 'mode': mode, 'input_hash': manifest['input_hash'],
              'source_hash': manifest['source_hash'], 'maximum_residual': residual_max,
              'rows': rows, 'protocol': protocol, 'imports': imports}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
