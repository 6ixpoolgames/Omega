"""Capped frozen-source feedback smoke or prospective mechanism comparison."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Hard caps required')

from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
    manifest = verify_bundle(out)
    config = manifest['config']['protocol']
    if config['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen prospective prescription required')
    import numpy as np
    from scipy.sparse import bmat, eye
    from scipy.sparse.linalg import expm_multiply

    from omega_v2.testbed.analysis.blocked_entropy import profile
    from omega_v2.testbed.analysis.channel_access import first_passage
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.composition import compose_worlds
    from omega_v2.testbed.resource_feedback import ResourceFeedbackParameters, build_world

    if mode == 'smoke':
        small_params = config['cases'][0]['parameters']
        small = build_world(ResourceFeedbackParameters(**small_params))
        large = build_world(ResourceFeedbackParameters(**{**small_params,
                           'apparatus_capacity': 2, 'carrier_capacity': 2}))
        model = compile_world(compose_worlds({'small': small, 'large': large}))
        root = ((1, 1, 0), (1, 1, 0))
        result = profile(model['Q'], {'root': model['index'][root]}, .25, [1, 4, 64])
        atomic_json(out/'result.json', {'status': 'engineering_complete', 'states': len(model['states']),
                                      'numerical_residuals': result['residuals'],
                                      'scores': 'withheld; no comparison or selection'})
        return
    rows = []
    for case in config['cases']:
        parameters = ResourceFeedbackParameters(**case['parameters'])
        model = compile_world(build_world(parameters))
        q, n = model['Q'], len(model['states'])
        roots = {'organized': (1, 1, 0), 'unorganized': (1, 0, 1)}
        indices = {name: model['index'][root] for name, root in roots.items()}
        result = profile(q, indices, case['cadence'], config['horizons'])
        pi = result['stationary']['organized']
        stationary = np.zeros(n)
        stationary[result['keep']] = pi
        root = np.zeros(n)
        root[indices['organized']] = 1
        zero = q*0
        integrated = expm_multiply(bmat([[q.T, zero], [eye(n), zero]], format='csr')*64,
                                    np.r_[root, np.zeros(n)])
        final, occupancy = integrated[:n], integrated[n:]
        if abs(final.sum()-1) > 1e-9:
            raise ArithmeticError('Endpoint mass')
        flows = {key: float(occupancy @ value) for key, value in model['flows'].items()}
        meanflows = {key: float(stationary @ value) for key, value in model['flows'].items()}
        deficit = np.zeros(n)
        deficit[model['index'][(1, 0, 0)]] = 1
        recovered = expm_multiply(q.T*64, deficit)
        function = model['observables']['apparatus'] > 0
        construction = first_passage(q, root, model['observables']['apparatus'] >= 2, 64)['hit_probability'] if parameters.apparatus_capacity > 1 else None
        row = {'case': case, 'bits': result['bits'], 'rates': result['rates'],
               'classes': result['classes'], 'states': n,
               'root_energies': {key: model['world'].energy(value) for key, value in roots.items()},
               'stationary_apparatus': float(stationary @ model['observables']['apparatus']),
               'stationary_function': float(stationary[function].sum()),
               'stationary_charged': float(stationary @ model['observables']['charged_carrier']),
               'stationary_flows': meanflows, 'flows64': flows,
               'recovery_firsthit64': first_passage(q, deficit, function, 64)['hit_probability'],
               'recovery_endpoint64': float(recovered[function].sum()),
               'growth_to_two_hit64': construction, 'residuals': result['residuals'],
               'energy_residual64': float(final @ model['energy']-root @ model['energy']
                                        -flows['drive_work']+flows['bath_heat'])}
        rows.append(row)
        atomic_json(out/'progress.json', {'completed': len(rows), 'total': len(config['cases'])})
    imported = {name: str(module.__file__) for name, module in sys.modules.items()
                if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imported.values()):
        raise RuntimeError('Unfrozen import')
    verify_bundle(out)
    atomic_json(out/'result.json', {'status': 'complete', 'rows': rows,
                                  'input_hash': manifest['input_hash'], 'imports': imported})


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
