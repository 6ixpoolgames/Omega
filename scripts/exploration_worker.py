"""Frozen exact comparison; no outcome labels or free exploration reward."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import hashlib
import json
from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    p = manifest['config']['protocol']
    if mode != manifest['config']['mode'] or p['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen mode/registration mismatch')
    import numpy as np

    from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits
    from omega_v2.testbed.analysis.observed_history import (
        averaged_observation_bounds,
        sampled_occupations,
    )
    from omega_v2.testbed.analysis.signal_readouts import coordinate_row_shares, occupation_integral
    from omega_v2.testbed.analysis.temporal_profile import coefficient_rows
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.exploration import ExplorationParameters, build_world

    cases = p['cases'] if mode == 'science' else [c for c in p['cases'] if c['id'] == p['smoke_case']]
    rows, maximum_residual, aliases = [], 0., {}
    for case in cases:
        for arm in p['arms']:
            compiled = compile_world(build_world(arm, SignalParameters(**case['physiology']),
                                                 ExplorationParameters(**case['parameters'])))
            root = int(compiled['index'][tuple(case['root'])])
            q = compiled['Q']
            key = hashlib.sha256(q.data.tobytes()+q.indices.tobytes()+q.indptr.tobytes()).hexdigest()
            alias = aliases.get(key)
            aliases.setdefault(key, [case['id'], arm])
            exits, finite, _ = coefficient_rows(q, p['temporal_reference'])
            continuous = {}
            for t in p['horizons']:
                final, occ = occupation_integral(q, root, t)
                obs = compiled['observables']
                physical = {'survival': float(final @ obs['alive']), 'lifetime': float(occ @ obs['alive']),
                            'signal_time': float(occ @ obs['signal_occupancy']),
                            'stock0_time': float(occ @ obs['stock0']), 'stock1_time': float(occ @ obs['stock1']),
                            'nominal_offered_work': t*compiled['metadata']['nominal_offered_work_rate']}
                physical.update({name: float(occ @ values) for name, values in compiled['flows'].items()
                                 if not name.startswith('net_')})
                continuous[str(t)] = {'physical': physical, 'expected_jumps': float(occ @ exits),
                                      'finite_term_bits': float(occ @ finite)}
            energy_error = float(np.max(abs(q @ compiled['energy']-compiled['flows']['drive_work']
                                            +compiled['flows']['bath_heat'])))
            for cadence in p['cadences'] if mode == 'science' else [.25]:
                result = analyze(q, cadence, max_dense_bytes=128*1024**2)
                counts = [round(t/cadence) for t in p['horizons']]
                occupation = sampled_occupations(result['P'], root, counts)
                shares = coordinate_row_shares(result['P'], compiled['states'], tuple(p['coordinate_order']))
                labels = [tuple(s[j] for j in p['hidden_fields']) for s in compiled['states']]
                profiles = {}
                for t, count in zip(p['horizons'], counts):
                    weights, _ = occupation[count]
                    bits = float(weights @ result['row_entropy'])
                    coordinate_bits = shares @ weights
                    maximum_residual = max(maximum_residual, abs(float(coordinate_bits.sum())-bits))
                    profiles[str(t)] = {**continuous[str(t)], 'bits': bits,
                                        'coordinate_bits': coordinate_bits.tolist(),
                                        'hidden_signal': averaged_observation_bounds(result['P'], labels, weights)}
                maximum_residual = max(maximum_residual, energy_error, *result['residuals'].values())
                if mode == 'smoke':
                    weights, _ = sampled_occupations(result['P'], root, [2])[2]
                    if abs(weights @ result['row_entropy']-finite_history_bits(result['P'], 2)[root]) > 1e-9:
                        raise ArithmeticError('Independent short-step reference failed')
                row = {'case': case['id'], 'arm': arm, 'cadence': cadence, 'states': len(compiled['states']),
                       'kernel_hash': key, 'kernel_alias': alias,
                       'residuals': {**result['residuals'], 'energy': energy_error}}
                if mode == 'science':
                    row.update({'profiles': profiles, 'rate_bits_per_time': float(result['rate_per_step'][root]/cadence),
                                'offset_bits': float(result['offset'][root])})
                else:
                    row['scientific_scores'] = 'withheld from engineering gate'
                rows.append(row)
        print(json.dumps({'mode': mode, 'case': case['id'], 'rows': len(rows)}), flush=True)
    if maximum_residual > p['tolerances']['residual']:
        raise ArithmeticError('Registered residual gate failed')
    imports = {name: str(m.__file__) for name, m in sys.modules.items()
               if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'complete', 'mode': mode, 'input_hash': manifest['input_hash'],
              'source_hash': manifest['source_hash'], 'maximum_residual': maximum_residual,
              'unique_generators': len(aliases), 'rows': rows, 'protocol': p, 'imports': imports}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
