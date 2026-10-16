"""Prospective matched-impairment comparison with physical repair hardware."""
from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import expm_multiply

from ..analysis.blocked_entropy import profile
from ..analysis.channel_access import closure_mask, first_passage, recovery_profile
from ..compiler import compile_world
from ..controllers.reserve import ReservePolicy
from ..growing_population import Params
from ..modules.repair_hardware import RepairHardware, build_world
from .channel_comparison import flux_survey
from .reserve_batch import retained_first_entry, tied_ids
from .reserve_smoke import fingerprint


def physical_roots(config):
    present = tuple(tuple(part) for part in config['present_root'])
    left = list(present[0])
    if left[1] < 1:
        raise ValueError('Present must permit the registered left fault')
    left[0] += 1
    left[1] -= 1
    hardware = (0, present[2][1]) if config['mode'] == 'hardware_loss' else present[2]
    return {'present': present, 'post_fault': (tuple(left), present[1], hardware)}


def validate(config):
    if config.get('status') != 'frozen_before_scientific_ranking':
        raise ValueError('Scientific freeze required')
    if config['mode'] not in ('fast', 'slow', 'hardware_loss'):
        raise ValueError('Unknown consequence')
    if config['primary'] != 'complete conditional history bits at each horizon':
        raise ValueError('Horizon-primary contract required')
    policies = [ReservePolicy(**p) for p in config['candidates']]
    if len({p.id for p in policies}) != len(policies) or not policies:
        raise ValueError('Invalid frozen family')
    physical_roots(config)
    Params(**config['params'])
    return policies


def scientific(config, progress=lambda value: None):
    policies = validate(config)
    inv = tuple(config['inventory'])
    params = Params(**config['params'])
    damage = RepairHardware(mode=config['mode'], hazard=config['hazard'],
                            slow_factor=config['slow_factor'],
                            hardware_energy=config['hardware_energy'])
    roots = physical_roots(config)
    rows, cache = [], {}
    tol = config['rank_tolerance']
    for count, policy in enumerate(policies, 1):
        progress({'phase': 'compile', 'policy': policy.id, 'completed': count-1,
                  'total': len(policies)})
        model = compile_world(build_world(inv, policy=policy, params=params, config=damage))
        key = fingerprint(model)
        if key in cache:
            rows.append({**cache[key], 'id': policy.id, 'controller': policy.manifest(),
                         'alias_of': cache[key]['id']})
            continue
        q = model['Q']
        indices = {name: model['index'][root] for name, root in roots.items()}
        progress({'phase': 'entropy', 'policy': policy.id, 'completed': count-1,
                  'total': len(policies)})
        result = profile(q, indices, config['cadence'], config['horizons'],
                         config['block_rows'], config['max_kernel_bytes'])
        n = len(model['states'])
        p0 = np.zeros(n)
        p0[indices['present']] = 1
        deadline = config['deadline']
        endpoint = expm_multiply(q.T*deadline, p0)
        if abs(endpoint.sum()-1) > 1e-9 or endpoint.min() < -1e-12:
            raise ArithmeticError('Endpoint probability accounting')
        active = model['observables']['active'] > 0
        closure = closure_mask(q, active)
        hardware = model['observables']['repair_hardware']
        # Restoration means regaining the original left reserve, not merely
        # any function: the post-fault root still has one active unit.
        restored = np.array([state[0][1] >= roots['present'][0][1] for state in model['states']])
        recovery = recovery_profile(q, indices['post_fault'], restored, [deadline])[str(float(deadline))]
        retention = retained_first_entry(q, np.eye(1, n, indices['post_fault']).ravel(),
                                         restored, deadline)
        if retention > recovery['hit_probability']+1e-9:
            raise ArithmeticError('Retention exceeds restoration hit')
        stationary = np.zeros(n)
        stationary[result['keep']] = result['stationary']['present']
        flux = flux_survey(model, p0, deadline)
        surface = policy.audit_vector(inv[0])
        nonrandom = all(tuple(r['response']) in ((0., 0.), (1., 0.), (0., 1.)) for r in surface)
        row = {'id': policy.id, 'canonical_id': policy.id, 'controller': policy.manifest(),
               'hash': key, 'bits': result['bits'], 'rates': result['rates'],
               'classes': result['classes'], 'reachable_states': len(result['keep']),
               'residuals': result['residuals'], 'nonrandom': nonrandom,
               'readouts': {
                   'active64': float(endpoint @ model['observables']['active']),
                   'exposure64': float(endpoint @ model['observables']['built']),
                   'function64': float(endpoint[active].sum()),
                   'left_function64': float(endpoint @ np.array([s[0][1] > 0 for s in model['states']])),
                   'hardware64': float(endpoint @ hardware),
                   'hardware_loss_hit64': (first_passage(q, p0, hardware < 2, deadline)['hit_probability']
                                           if np.any(hardware[result['keep']] < 2) else 0.),
                   'closure64': (first_passage(q, p0, closure, deadline)['hit_probability']
                                 if np.any(closure[result['keep']]) else 0.),
                   'post_fault_firsthit64': recovery['hit_probability'],
                   'post_fault_endpoint64': recovery['endpoint_target_probability'],
                   'post_fault_retained64': retention,
                   'stationary_active': float(stationary @ model['observables']['active']),
                   'stationary_exposure': float(stationary @ model['observables']['built']),
                   'stationary_hardware': float(stationary @ hardware),
                   'stationary_function': float(stationary[active].sum()),
                   'costs64': flux['flows'],
                   'accounting_residuals': {'energy': flux['energy_residual'],
                                            'population': flux['population_residual']}}}
        cache[key] = row
        rows.append(row)
        progress({'phase': 'complete', 'completed': count, 'total': len(policies),
                  'unique': len(cache)})
    winners = {str(t): tied_ids(rows, lambda row, t=t: row['bits'][str(t)]['present'], tol)
               for t in config['horizons']}
    return {'status': 'complete', 'case_id': config['id'], 'mode': config['mode'],
            'hazard': config['hazard'], 'cadence': config['cadence'],
            'policies': rows, 'winners': winners, 'unique_models': len(cache), 'states': n,
            'rate_winners': tied_ids(rows, lambda row: row['rates']['present'], tol),
            'root_energies': {name: model['world'].energy(root) for name, root in roots.items()},
            'recovery_target': 'left active count at least original present reserve',
            'post_fault_scope': 'conditional physical fault; hardware-loss energy differs'}
