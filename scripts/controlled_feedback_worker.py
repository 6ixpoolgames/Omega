"""Frozen full-model-information evaluation; native actions are costed."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Hard caps required')

from pathlib import Path


def main(out, mode):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
    manifest = verify_bundle(out)
    protocol = manifest['config']['protocol']
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Prospective freeze required')
    import numpy as np
    from scipy.sparse import bmat, eye
    from scipy.sparse.linalg import expm_multiply

    from omega_v2.testbed.analysis.blocked_entropy import profile
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.controlled_feedback import (
        ControlledFeedbackController,
        ControlledFeedbackParameters,
        build_world,
    )
    from omega_v2.testbed.resource_feedback import ResourceFeedbackParameters

    cases = protocol['cases'] if mode == 'science' else [protocol['cases'][3]]
    results = []
    for case in cases:
        rows = []
        policies = case['policies'] if mode == 'science' else [case['policies'][21]]
        for candidate in policies:
            policy = ControlledFeedbackController(**candidate)
            params = ControlledFeedbackParameters(resource=ResourceFeedbackParameters(**case['parameters']),
                      controller=policy, command_switch=protocol['switch'], gate_relaxation=protocol['relaxation'])
            model = compile_world(build_world(params))
            q, n = model['Q'], len(model['states'])
            root = tuple(protocol['rank_root'])
            result = profile(q, {'root': model['index'][root]}, case['cadence'], protocol['horizons'])
            p0 = np.zeros(n); p0[model['index'][root]] = 1
            zero = q*0
            integrated = expm_multiply(bmat([[q.T,zero],[eye(n),zero]],format='csr')*protocol['deadline'],
                                        np.r_[p0,np.zeros(n)])
            endpoint, occupation = integrated[:n], integrated[n:]
            costs = {key: float(occupation@value) for key,value in model['flows'].items()}
            active = model['observables']['apparatus']
            gate = model['observables']['gate']
            if abs(endpoint.sum()-1) > 1e-9:
                raise ArithmeticError('Probability accounting')
            rows.append({'id': policy.id, 'responses': policy.responses,
                         'bits': {time: value['root'] for time,value in result['bits'].items()},
                         'rate': result['rates']['root'], 'active64': float(endpoint@active),
                         'function64': float(endpoint[active>0].sum()), 'use_gate64': float(endpoint@gate),
                         'stationary_active': float(result['stationary']['root']@active[result['keep']]),
                         'costs64': costs, 'residuals': result['residuals']})
        tolerance = protocol['rank_tolerance']
        winners = {str(t): sorted(r['id'] for r in rows if max(x['bits'][str(t)] for x in rows)
                                 -r['bits'][str(t)] <= tolerance) for t in protocol['horizons']}
        results.append({'case': case, 'rows': rows, 'winners': winners})
        atomic_json(out/'progress.json', {'completed_cases': len(results), 'total_cases': len(cases)})
    verify_bundle(out)
    atomic_json(out/'result.json', {'status': 'complete' if mode == 'science' else 'engineering_complete',
                                  'cases': results if mode == 'science' else 'scores withheld',
                                  'input_hash': manifest['input_hash']})


if __name__ == '__main__':
    main(Path(sys.argv[1]),sys.argv[2])
