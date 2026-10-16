"""Memory bounded physical histories for the fractional-bank/discovery adapter."""
import numpy as np
from scipy.sparse.linalg import expm_multiply
from ..domination_friction import D_FIELDS, S_FIELDS, B_FIELDS
from .friction_profile import projection_bounds, first_passage
from .friction_attribution import activity_rows, integrate
from .streamed_history import StreamedQueries, projection_future, entropy_stream_cadences


def coefficients(Q):
    q = Q.tocsr().copy()
    q.setdiag(0)
    q.eliminate_zeros()
    exits = np.asarray(q.sum(axis=1)).ravel()
    logq = q.copy()
    logq.data *= np.log2(logq.data)
    sums = np.asarray(logq.sum(axis=1)).ravel()
    finite = exits*np.log2(np.e)-sums
    mark = exits*np.log2(np.maximum(exits, 1e-300))-sums
    return exits, finite, mark


def profile(world, compiled, roots, cadences, horizons, block_rows=32, progress=lambda x: None,
            entropy_backend='exponential', entropy_threads=1, entropy_cache=None):
    states, Q = compiled['states'], compiled['Q']
    progress('stationarity')
    solver = StreamedQueries(Q,allow_transients=world.metadata.get('allow_transients',False))
    roots = {k: compiled['index'][tuple(v)] for k, v in roots.items()}
    result = {'states': len(states), 'metadata': compiled['metadata'], 'cadences': {},
              'physical': {}, 'subject_bounds_can_be_unresolved': True,
              'backend': 'streamed-full-kernel / sparse Poisson / one-observation HMM bounds',
              'stationary_residual': solver.stationary_residual,
              'energy_residual': float(max(abs(Q @ compiled['energy']
                  -compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))}
    exits, finite, mark = coefficients(Q)
    attribution = activity_rows(world)
    for name, root in roots.items():
        initial = np.zeros(len(states))
        initial[root] = 1.
        result['physical'][name] = {}
        for time in horizons:
            progress(f'physical {name} T{time}')
            endpoint, occupation, residual = solver.continuous_occupation(root, time)
            ledger = {k: float(occupation @ v) for k, v in compiled['flows'].items()}
            deadline = {k: float(endpoint @ v) for k, v in compiled['observables'].items()}
            average = {k: float(occupation @ v/time) for k, v in compiled['observables'].items()}
            arrival_keys=['S.access','S.construction','S.trap','S.discovered']+[
                k for k in ('S.access_device','S.lost_material') if k in compiled['observables']]
            arrivals = {k: first_passage(Q, initial, compiled['observables'][k] > 0, time)
                        for k in arrival_keys}
            result['physical'][name][str(time)] = {
                'ledger': ledger, 'deadline': deadline, 'average': average,
                'first_passage': arrivals, 'occupation_residual': residual,
                'integrated_energy_residual': float(endpoint @ compiled['energy']
                    -compiled['energy'][root]-ledger['drive_work']+ledger['bath_heat']),
                'expected_jumps': float(occupation @ exits),
                'finite_term_bits': float(occupation @ finite),
                'destination_surprisal_bits': float(occupation @ mark),
                'D_native_attribution': integrate(attribution, occupation),
                'reference_time': 1., 'horizon': time,
                'suppressed_attempts': float(occupation @ compiled['observables']['suppressed_rate'])}
    progress('full entropy all cadences')
    if entropy_backend == 'exponential':
        entropy = entropy_stream_cadences(Q, cadences, block_rows)
    elif entropy_backend == 'uniformized':
        from .uniformized_entropy import entropy_cadences
        entropy = entropy_cadences(Q, cadences, block_rows, threads=entropy_threads,
                                  cache_dir=entropy_cache,progress=progress)
    else:
        raise ValueError('Unknown entropy backend')
    result['entropy_backend'] = entropy_backend
    for cadence in cadences:
        sampled = solver.sampled(cadence, block_rows, entropy[cadence])
        progress(f'subject projections dt{cadence}')
        subjects=world.metadata.get('subjects',{'D':D_FIELDS,'S':S_FIELDS,'background':B_FIELDS})
        projections = {subject: projection_future(Q, states, subjects[subject], cadence)
                       for subject in ('D','S','background')}
        row = {'profiles': {}, 'limiting_rate': sampled['rate'],
               'poisson_residual': sampled['poisson_residual'],
               'kernel_diagnostics': sampled['diagnostics']}
        row['subject_rate_bounds']={}
        for subject in ('D','S'):
            bounds=projection_bounds(*projections[subject],solver.pi,sampled['rate']*cadence)
            row['subject_rate_bounds'][subject]={
                'lower_bits_per_time':bounds['lower_bits']/cadence,
                'upper_bits_per_time':bounds['upper_bits']/cadence,
                'method':'stationary HMM conditioning bounds, not projected Markov entropy'}
        for name, root in roots.items():
            row['profiles'][name] = {}
            for time in horizons:
                occupations, residual = solver.sampled_occupation(root, time, cadence)
                full = float(solver.finite(sampled, time)[root])
                allowance = time/cadence*(sampled['poisson_residual']
                    +sampled['diagnostics'].get('row_entropy_error_bits', 0.))+1e-6
                if abs(float(occupations @ sampled['g'])-full) > allowance+1e-6:
                    raise ArithmeticError('Streamed entropy/occupation identity failed')
                subjects = {s: projection_bounds(*projections[s], occupations, full)
                            for s in ('D', 'S', 'background')}
                d, s, b = (subjects[k] for k in ('D', 'S', 'background'))
                ds = {'lower_bits': max(d['lower_bits'], s['lower_bits'], full-b['upper_bits']),
                      'upper_bits': min(full, d['upper_bits']+s['upper_bits']),
                      'method': 'joint-history chain-rule bounds; no merged generator'}
                if ds['lower_bits'] > ds['upper_bits']+1e-6:
                    raise ArithmeticError('Joint subject bounds inverted')
                subjects['DS'] = ds
                row['profiles'][name][str(time)] = {
                    'global_bits': full, 'subjects': subjects,
                    'intertwining_bounds': {
                        'lower_bits': max(0., d['lower_bits']+s['lower_bits']-ds['upper_bits']),
                        'upper_bits': max(0., min(d['upper_bits'], s['upper_bits'],
                            d['upper_bits']+s['upper_bits']-ds['lower_bits'])),
                        'definition': 'I(D history; S history | common exact initial frame)',
                        'joint_DS_excludes_background': True},
                    'sampled_occupation_residual': residual,
                    'global_numerical_allowance': allowance}
            progress(f'finished dt{cadence} {name}')
        result['cadences'][str(cadence)] = row
    return result
