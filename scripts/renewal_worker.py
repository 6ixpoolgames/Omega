"""One frozen law per capped worker; shared kernels, compact physical tables."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    import numpy as np
    from scipy.linalg import expm

    from omega_v2.testbed.analysis.channel_access import first_passage
    from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits
    from omega_v2.testbed.analysis.renewal_profile import (
        SampledHorizons,
        coordinate_shares,
        hidden_bounds,
        hidden_prepared,
        horizon_estimate,
        reachable_world,
    )
    from omega_v2.testbed.analysis.signal_readouts import occupation_integral
    from omega_v2.testbed.analysis.temporal_profile import coefficient_rows
    from omega_v2.testbed.aversive_signals import SignalParameters
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.exploration import ExplorationParameters
    from omega_v2.testbed.paid_sensing import SensorParameters
    from omega_v2.testbed.renewal import RenewalParameters, build_world, physical_readouts
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    p, law = manifest['config']['protocol'], manifest['config']['law']
    if mode != manifest['config']['mode'] or p['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen mode/protocol mismatch')
    roots = [{'id': f'main{i}', 'state': root, 'kind': 'primary'} for i, root in enumerate(law['roots'])]
    roots += [{'id': f'prep{i}', 'state': root, 'kind': 'matched_preparation'}
              for i, root in enumerate(law.get('preparation_roots', []))]
    depleted = (0, 1, 0, 1, 0, 1, 0)
    compiled_reference = None
    rows, physical, stationary, recovery, probes = [], {}, {}, {}, []
    residual_max = 0.
    for arm in p['arms']:
        params = {**law['parameters'], 'coupling': p['coupling'] if arm.endswith('X') else 0.}
        compiled = reachable_world(compile_world(build_world(arm[0], SignalParameters(**law['physiology']),
            ExplorationParameters(**params), SensorParameters(**law['sensor']), RenewalParameters(**law['renewal']))),
            [r['state'] for r in roots]+[depleted])
        q = compiled['Q']
        if arm == 'R0':
            compiled_reference = compiled
        exits, finite, _ = coefficient_rows(q)
        hardware_module = next(m for m in compiled['world'].modules if m.id == 'apparatus-construction')
        assisted_build = np.zeros(len(compiled['states']))
        for i, state in enumerate(compiled['states']):
            gain = law['renewal']['autocatalytic_gain']*state[6]
            for event in hardware_module.events(state):
                if event.family == 'paid_construction':
                    assisted_build[i] += event.rate*gain/(1+gain)
        for root in roots:
            ref = f"{arm}:{root['id']}"
            root_index = int(compiled['index'][tuple(root['state'])])
            physical[ref] = {}
            for t in p['horizons'] if mode == 'science' else [64]:
                prepared = occupation_integral(q, root_index, t)
                values = physical_readouts(compiled, root_index, t, prepared=prepared)
                values['nominal_offered_work'] = t*compiled['metadata']['nominal_offered_work_rate']
                values['construction_with_existing_hardware'] = values.get('construction_assisted_by_hardware', 0.)
                values['incremental_autocatalytic_construction'] = float(prepared[1] @ assisted_build)
                physical[ref][str(t)] = {'readouts': values, 'expected_jumps': float(prepared[1] @ exits),
                                         'finite_term_bits': float(prepared[1] @ finite)}
        if mode == 'science':
            recovery[arm] = {}
            target = compiled['observables']['functional'] > 0
            for t in p['horizons']:
                result = first_passage(q, int(compiled['index'][depleted]), target, t)
                final, occ = occupation_integral(q, int(compiled['index'][depleted]), t)
                recovery[arm][str(t)] = {'hit_probability': result['hit_probability'],
                                         'deadline_functionality': float(final @ target),
                                         'functional_time': float(occ @ target)}
        energy_error = float(np.max(abs(q @ compiled['energy']-compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))
        for cadence in p['cadences'] if mode == 'science' else [.25]:
            analysis = analyze(q, cadence, max_dense_bytes=256*1024**2)
            residual_max = max(residual_max, energy_error, *analysis['residuals'].values())
            cache = SampledHorizons(analysis['P'], round(p['horizon_query_maximum']/cadence))
            shares = coordinate_shares(analysis['P'], compiled['states'], p['coordinate_order'])
            hidden = hidden_prepared(analysis['P'], [tuple(s[j] for j in p['hidden_fields']) for s in compiled['states']])
            for root in roots:
                root_index = int(compiled['index'][tuple(root['state'])])
                pi = np.zeros(len(compiled['states']))
                for class_id, members in enumerate(analysis['class_indices']):
                    pi[members] += analysis['absorption'][root_index, class_id]*analysis['stationary'][class_id]
                ref = f"{arm}:{root['id']}"
                if ref not in stationary:
                    values = physical_readouts(compiled, root_index, 1., prepared=(pi, pi), stationary=True)
                    values['nominal_offered_work_rate'] = compiled['metadata']['nominal_offered_work_rate']
                    values['construction_with_existing_hardware'] = values.get('construction_assisted_by_hardware', 0.)
                    values['incremental_autocatalytic_construction'] = float(pi @ assisted_build)
                    marker = p['operating_marker']
                    values['operating_regime'] = bool(values['functional_deadline'] >= marker['stationary_functionality']
                        and values.get('hardware_paid_construction', 0.) >= marker['paid_construction_rate'])
                    stationary[ref] = values
                profiles = {}
                for t in p['horizons']:
                    weights, _ = cache.occupation(root_index, round(t/cadence))
                    bits = float(weights @ analysis['row_entropy'])
                    attribution = shares @ weights
                    residual_max = max(residual_max, abs(float(attribution.sum())-bits))
                    profiles[str(t)] = {'bits': bits, 'coordinate_bits': attribution.tolist(),
                                         'hidden_bit': hidden_bounds(hidden, weights)}
                row = {'arm': arm, 'root': root, 'cadence': cadence,
                       'physical_ref': ref, 'full_states': compiled['full_state_count'], 'reachable_states': len(compiled['states']),
                       'closed_classes': len(analysis['class_indices'])}
                if mode == 'science':
                    row.update({'profiles': profiles, 'rate_bits_per_time': float(analysis['rate_per_step'][root_index]/cadence),
                                'offset_bits': float(analysis['offset'][root_index]),
                                'stationary_coordinate_rate': (shares @ pi/cadence).tolist(),
                                'stationary_hidden_bounds': {k: value/cadence for k, value in hidden_bounds(hidden, pi).items()
                                                             if k in ('lower_bits', 'upper_bits')}})
                else:
                    weights, _ = cache.occupation(root_index, 2)
                    if abs(float(weights @ analysis['row_entropy'])-finite_history_bits(analysis['P'], 2)[root_index]) > 1e-9:
                        raise ArithmeticError('Independent short-step reference failed')
                    row['scientific_scores'] = 'withheld'
                if mode == 'science' and arm == 'IX' and root['kind'] == 'primary':
                    reference_row = next(v for v in rows if v['arm'] == 'R0' and v['root']['id'] == root['id'] and v['cadence'] == cadence)
                    estimate = horizon_estimate(row['rate_bits_per_time']-reference_row['rate_bits_per_time'],
                                                row['offset_bits']-reference_row['offset_bits'], p['tolerances']['rate'])
                    query = {'root': root['id'], 'cadence': cadence, 'comparison': 'IX-R0', 'estimate': estimate, 'exact_probes': []}
                    predicted = estimate['estimate']
                    if predicted is not None and 0 < predicted <= p['horizon_query_maximum']:
                        reference_kernel = expm(compiled_reference['Q'].toarray()*cadence)
                        reference_root = int(compiled_reference['index'][tuple(root['state'])])
                        for multiplier in p['horizon_probe_estimate_multipliers']:
                            count = max(1, round(predicted*multiplier/cadence))
                            if count*cadence > p['horizon_query_maximum']:
                                continue
                            weights, _ = cache.occupation(root_index, count)
                            difference = float(weights @ analysis['row_entropy'])-float(finite_history_bits(reference_kernel, count)[reference_root])
                            query['exact_probes'].append({'steps': count, 'horizon': count*cadence, 'delta_bits': difference})
                        del reference_kernel
                    probes.append(query)
                rows.append(row)
            del cache, shares, hidden, analysis
        print(json.dumps({'mode': mode, 'law': law['id'], 'arm': arm, 'rows': len(rows)}), flush=True)
    if residual_max > p['tolerances']['residual']:
        raise ArithmeticError('Frozen residual gate failed')
    imports = {name: str(m.__file__) for name, m in sys.modules.items() if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    result = {'status': 'complete', 'mode': mode, 'input_hash': manifest['input_hash'], 'source_hash': manifest['source_hash'],
              'law': law, 'maximum_residual': residual_max, 'rows': rows}
    if mode == 'science':
        result.update({'physical': physical, 'stationary': stationary, 'recovery': recovery, 'horizon_probes': probes})
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
