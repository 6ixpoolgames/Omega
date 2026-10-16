"""All roots reuse one native Q; root averaging adds no preparation entropy."""
import json


def calibrate_numerics(compiled):
    from omega_v2.testbed.analysis.same_law_profile import IrreducibleQueries
    queries = IrreducibleQueries(compiled['Q'])
    tested = queries.sampled(.25, [1])
    return {'sampled_identity_residuals': tested['residuals'],
            'stationary_mass_error': float(abs(queries.pi.sum()-1)),
            'rankings_inspected': False}


def science(out, manifest):
    import numpy as np
    from scipy.sparse.linalg import expm_multiply, spsolve

    from omega_v2.testbed.analysis.channel_access import first_passage
    from omega_v2.testbed.analysis.same_law_profile import IrreducibleQueries, fixed_jump_vectors
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.reactive_lattice import (
        LatticeParameters,
        build_world,
        organized_root,
        reference_masks,
    )

    config = manifest['config']
    protocol = config['protocol']
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise RuntimeError('Science requires frozen protocol')
    p = LatticeParameters(**config['law']['parameters'])
    c = compile_world(build_world(p))
    query = IrreducibleQueries(c['Q'])
    root = organized_root(p)
    seed = np.zeros(len(c['states']))
    seed[c['index'][root]] = 1.
    refs = reference_masks(c, root)
    initials = {'seed': seed, **refs}
    exits, finite, jump, mark = query.activity()
    jvectors = fixed_jump_vectors(jump, mark)
    rows = []
    all_vectors = {}
    for cadence in protocol['cadences']:
        sampled = query.sampled(cadence, protocol['horizons'])
        all_vectors[str(cadence)] = sampled['vectors']
        for name, mu in initials.items():
            rows.append({'reference': name, 'cadence': cadence, 'rate': sampled['rate'],
                'offset': float(mu @ sampled['offset']),
                'scores': {t: float(mu @ vector) for t, vector in sampled['vectors'].items()},
                'residuals': sampled['residuals']})
        print(json.dumps({'law': config['law']['id'], 'cadence': cadence,
                          'numerical_residual': max(sampled['residuals'].values())}), flush=True)
    initial_matrix = np.column_stack(list(initials.values()))
    physical = {name: {} for name in initials}
    maximum_residual = 0.
    for horizon in protocol['horizons']:
        endpoints = expm_multiply(c['Q'].T*horizon, initial_matrix)
        for column, (name, mu) in enumerate(initials.items()):
            final = endpoints[:, column]
            w, residual = query.occupation(mu, final, horizon)
            energy_error = abs((final-mu) @ c['energy']-w @ c['flows']['drive_work']+w @ c['flows']['bath_heat'])
            maximum_residual = max(maximum_residual, residual, float(energy_error), abs(final.sum()-1))
            value = {'expected_jumps': float(w @ exits), 'finite_temporal_term': float(w @ finite),
                     'destination_surprisal_integral': float(w @ (exits*mark)),
                     'energy_balance_residual': float(energy_error),
                     'deadline': {k: float(final @ v) for k, v in c['observables'].items()},
                     'flows': {k: float(w @ v) for k, v in c['flows'].items()}}
            physical[name][str(horizon)] = value
    assembly = {}
    for target_name in ('G1', 'G2', 'G3'):
        target = c['observables'][target_name] > .5
        outside = np.flatnonzero(~target)
        if target.any():
            mean = np.zeros(len(target))
            mean[outside] = spsolve(-c['Q'][outside][:, outside].tocsc(), np.ones(len(outside)))
            mean_residual = float(np.max(abs(c['Q'][outside][:, outside] @ mean[outside]+1))) if len(outside) else 0.
            if mean_residual > 1e-7 or mean.min() < -1e-8:
                raise ArithmeticError('First-passage mean solve residual')
        else:
            mean = None
        assembly[target_name] = {}
        for name, mu in initials.items():
            assembly[target_name][name] = {'mass_at_zero': float(mu @ target),
                'mean_time': float(mu @ mean) if mean is not None else None,
                'unreachable_mass': 0. if mean is not None else 1.,
                'hit_probability': {str(t): float(first_passage(c['Q'], mu, target, t)['hit_probability'])
                                    for t in protocol['horizons']},
                'deadline_occupancy': {str(t): physical[name][str(t)]['deadline'][target_name]
                                       for t in protocol['horizons']}}
    contrasts = []
    for cadence, vectors in all_vectors.items():
        for name, mu in refs.items():
            support = mu > 0
            for t, vector in vectors.items():
                differences = vector[c['index'][root]]-vector[support]
                contrasts.append({'reference': name, 'cadence': float(cadence), 'horizon': int(t),
                    'delta_bits': float(seed @ vector-mu @ vector),
                    'individual_root_delta_min': float(differences.min()),
                    'individual_root_delta_max': float(differences.max()),
                    'seed_beats_reference_mass': float(mu[support] @ (differences > protocol['tolerances']['bits']))})
    if maximum_residual > 1e-7:
        raise ArithmeticError('Physical integration numerical gate failed')
    result = {'status': 'complete', 'law': config['law'], 'states': len(c['states']),
        'input_hash': manifest['input_hash'], 'source_hash': manifest['source_hash'],
        'initial_energy': c['world'].energy(root), 'density': p.monomers/p.sites,
        'rows': rows, 'contrasts': contrasts, 'physical': physical, 'assembly': assembly,
        'fixed_jump_bits': {name: {k: float(mu @ v) for k, v in jvectors.items()} for name, mu in initials.items()},
        'stationary': {'observables': {k: float(query.pi @ v) for k, v in c['observables'].items()},
                       'flows': {k: float(query.pi @ v) for k, v in c['flows'].items()},
                       'expected_jumps_per_time': float(query.pi @ exits),
                       'embedded_jump_entropy_per_jump': float(query.pi @ (exits*mark)/(query.pi @ exits))},
        'maximum_physical_residual': maximum_residual,
        'provenance_note': 'G3 means two simultaneous bonds; paid-versus-thermal origin is diagnosed by native flows, not physical labels',
        'random_length_joint_entropy': 'not computed; fixed jumps compare different physical durations'}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
