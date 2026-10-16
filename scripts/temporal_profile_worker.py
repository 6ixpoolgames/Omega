"""Capped, frozen-source temporal profile; query clocks do not alter physics."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from itertools import pairwise
from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    protocol = manifest['config']['protocol']
    if mode != manifest['config']['mode'] or mode not in ('smoke', 'science'):
        raise ValueError('Mode mismatch')
    import numpy as np
    from scipy.linalg import expm

    from omega_v2.testbed.analysis.observed_history import (
        averaged_observation_bounds,
        entropy_rows,
        sampled_occupations,
    )
    from omega_v2.testbed.analysis.temporal_profile import (
        coefficients,
        count_entropy_bounds,
        crossover,
        expansion,
        fixed_jump_bits,
    )
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.signal_controls import build_world

    cases = protocol['cases']
    if mode == 'smoke':
        cases = [case for case in cases if case['id'] == protocol['smoke_case']]
    rows, comparisons = [], []
    maximum_residual = 0.
    for case in cases:
        worlds, cache = {}, {}
        for arm in protocol['arms']:
            compiled = compile_world(build_world(arm, SignalParameters(**case['parameters']),
                **({'on_rate': case['on_rate'], 'off_rate': case['off_rate']} if arm == 'B_R' else {})))
            root = int(compiled['index'][tuple(case['root'])])
            worlds[arm] = compiled, root
            coordinate = {str(t): coefficients(compiled['Q'], root, t, protocol['reference_time'])
                          for t in protocol['horizons']}
            count = count_entropy_bounds(compiled['Q'], root,
                **{k: protocol['count_query'][k] for k in
                   ('horizon', 'tail_budget', 'max_augmented_states')})
            fixed = fixed_jump_bits(compiled['Q'], root, protocol['fixed_jump_counts'])
            labels = [tuple(state[j] for j in (0, 1, 3, 4)) for state in compiled['states']]

            def evaluate(steps, horizon, arm=arm, compiled=compiled, root=root,
                         labels=labels, cache=cache):
                nonlocal maximum_residual
                key = arm, steps, horizon
                if key in cache:
                    return cache[key]
                kernel = expm(compiled['Q'].toarray()*(horizon/steps))
                occupation, final = sampled_occupations(kernel, root, [steps])[steps]
                residual = max(float(np.max(abs(kernel.sum(axis=1)-1))),
                               abs(float(final.sum())-1), abs(float(occupation.sum())/steps-1))
                maximum_residual = max(maximum_residual, residual)
                value = {'bits': float(occupation @ entropy_rows(kernel)), 'steps': steps,
                         'cadence': horizon/steps, 'residual': residual}
                if horizon/steps in (.125, .25, .5):
                    value['hidden_signal'] = averaged_observation_bounds(kernel, labels, occupation)
                cache[key] = value
                return value

            worlds[arm] += (evaluate,)
            profiles = {}
            cadences = protocol['cadences'] if mode == 'science' else [.5, .001953125]
            for t in protocol['horizons']:
                profiles[str(t)] = []
                for cadence in cadences:
                    value = evaluate(round(t/cadence), t)
                    estimate = expansion(coordinate[str(t)], cadence)
                    profiles[str(t)].append({**value, 'expansion_bits': estimate,
                                              'expansion_error_bits': value['bits']-estimate})
            row = {'parent': case['parent'], 'arm': arm, 'states': len(compiled['states'])}
            if mode == 'science':
                row.update({'coefficients': coordinate, 'count_entropy': count,
                            'fixed_jump_bits': fixed, 'profiles': profiles})
            else:
                row['scientific_scores'] = 'withheld from engineering gate'
            rows.append(row)
            print(json.dumps({'mode': mode, 'parent': case['parent'], 'arm': arm}), flush=True)
        if mode == 'science':
            for left, right in protocol['pairs']:
                a = next(row for row in rows if row['parent'] == case['parent'] and row['arm'] == left)
                b = next(row for row in rows if row['parent'] == case['parent'] and row['arm'] == right)
                for t in protocol['horizons']:
                    prediction = crossover(a['coefficients'][str(t)], b['coefficients'][str(t)])
                    profile = []
                    for av, bv in zip(a['profiles'][str(t)], b['profiles'][str(t)]):
                        item = {'cadence': av['cadence'], 'steps': av['steps'],
                                'delta_bits': av['bits']-bv['bits'],
                                'estimated_delta_bits': av['expansion_bits']-bv['expansion_bits'],
                                'pair_error_bits': av['expansion_error_bits']-bv['expansion_error_bits']}
                        if 'hidden_signal' in av:
                            item['hidden_delta_bounds'] = {
                                'lower_bits': av['hidden_signal']['lower_bits']-bv['hidden_signal']['upper_bits'],
                                'upper_bits': av['hidden_signal']['upper_bits']-bv['hidden_signal']['lower_bits']}
                        profile.append(item)
                    brackets = []
                    tol = protocol['tolerances']['bits']
                    for lo, hi in pairwise(profile):
                        if lo['delta_bits']*hi['delta_bits'] >= 0 or min(abs(lo['delta_bits']), abs(hi['delta_bits'])) <= tol:
                            continue
                        l, r = dict(lo), dict(hi)
                        iterations = 0
                        while r['steps']-l['steps'] > 1 and iterations < protocol['refinement']['max_iterations']:
                            n = (l['steps']+r['steps'])//2
                            difference = worlds[left][2](n, t)['bits']-worlds[right][2](n, t)['bits']
                            mid = {'steps': n, 'cadence': t/n, 'delta_bits': difference}
                            if difference*l['delta_bits'] > 0:
                                l = mid
                            else:
                                r = mid
                            iterations += 1
                        brackets.append({'coarse': [lo, hi], 'refined': [l, r],
                                         'iterations': iterations, 'adjacent_integer_schedules': r['steps']-l['steps'] == 1})
                    comparisons.append({'parent': case['parent'], 'pair': [left, right],
                                        'horizon': t, 'prediction': prediction,
                                        'profile': profile, 'crossing_brackets': brackets})
    if maximum_residual > protocol['tolerances']['residual']:
        raise ArithmeticError('Registered numerical gate failed')
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'complete', 'mode': mode, 'input_hash': manifest['input_hash'],
              'source_hash': manifest['source_hash'], 'maximum_residual': maximum_residual,
              'protocol': protocol, 'rows': rows, 'comparisons': comparisons, 'imports': imports}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
