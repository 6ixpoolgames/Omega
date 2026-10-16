"""Generic policy assay: full histories and bounded actual marginal histories.

Two-observation queries stream over the intermediate observation. They avoid
the N*G*G tensor used by the original small-world query, with identical bounds.
"""
import numpy as np
from scipy.sparse.linalg import expm_multiply

from .blocked_entropy import sampled_kernel
from .expanded_friction_profile import coefficients
from .friction_profile import projected_rows, projection_bounds, sampled_occupation
from .observed_history import entropy_rows
from .streamed_history import StreamedQueries


def two_observation_summary(P, groups, future, occupations):
    """Return lower reward rows and pooled two-observation upper totals.

occupations maps query names to sum_{t=0}^{n-2} Pr(X_t) (or pi for a
stationary-rate bound). No physical state, monitor, or action label is added.
"""
    n, g = future.shape
    order = np.argsort(groups, kind='stable')
    sorted_groups = groups[order]
    unique, starts = np.unique(sorted_groups, return_index=True)
    if not np.array_equal(unique, np.arange(g)):
        raise ValueError('Contiguous observation labels required')
    rows = np.zeros(n)
    uppers = {name: 0. for name in occupations}
    for y in range(g):
        mask = groups == y
        joint = P[:, mask] @ future[mask]
        probability = future[:, y]
        conditional = np.divide(joint, probability[:, None], out=np.zeros_like(joint),
                                where=probability[:, None] > 0)
        rows += probability*entropy_rows(conditional)
        for name, occupation in occupations.items():
            pooled = np.add.reduceat((occupation[:, None]*joint)[order], starts, axis=0)
            weights = pooled.sum(axis=1)
            distribution = np.divide(pooled, weights[:, None], out=np.zeros_like(pooled),
                                     where=weights[:, None] > 0)
            uppers[name] += float(weights @ entropy_rows(distribution))
    return rows, uppers


def profile(world, compiled, initial, cadences, horizons, depth=2, progress=lambda x: None):
    if depth not in (1, 2):
        raise ValueError('Supported subject bound depths are one and two')
    Q, states = compiled['Q'], compiled['states']
    solver = StreamedQueries(Q)
    start = compiled['index'][initial]
    result = {'states': len(states), 'metadata': world.metadata, 'cadences': {}, 'physical': {},
              'stationary_residual': solver.stationary_residual,
              'energy_residual': float(max(abs(Q @ compiled['energy']
                  -compiled['flows']['drive_work']+compiled['flows']['bath_heat']))),
              'subject_depth': depth, 'subject_intervals_are_not_midpoint_rankings': True}
    exits, finite, marks = coefficients(Q)
    result['stationary_ledger'] = {k: float(solver.pi @ v) for k, v in compiled['flows'].items()}
    result['stationary_observables'] = {k: float(solver.pi @ v) for k, v in compiled['observables'].items()}
    for time in horizons:
        endpoint, occupation, residual = solver.continuous_occupation(start, time)
        ledger = {k: float(occupation @ v) for k, v in compiled['flows'].items()}
        deadline = {k: float(endpoint @ v) for k, v in compiled['observables'].items()}
        owned_residual = {}
        for sub in ('D', 'S'):
            owned_residual[sub] = abs(deadline[sub+'.owned_energy']
                -world.observables[sub+'.owned_energy'](initial)
                -sum(v for k, v in ledger.items() if k.startswith(sub+'_energy_by_family.')))
        if max(owned_residual.values()) > 1e-7:
            raise ArithmeticError('Owned-energy ledger did not close')
        result['physical'][str(time)] = {'ledger': ledger, 'deadline': deadline,
            'average': {k: float(occupation @ v/time) for k, v in compiled['observables'].items()},
            'expected_jumps': float(occupation @ exits), 'finite_term_bits': float(occupation @ finite),
            'destination_surprisal_bits': float(occupation @ marks),
            'occupation_residual': residual, 'owned_energy_residual': owned_residual,
            'integrated_energy_residual': float(endpoint @ compiled['energy']-compiled['energy'][start]
                -ledger['drive_work']+ledger['bath_heat'])}
    for cadence in cadences:
        progress('sampled kernel dt'+str(cadence))
        P, g, diagnostics = sampled_kernel(Q, cadence, block_rows=128, max_kernel_bytes=192*1024**2)
        sampled = solver.sampled(cadence, entropy_payload=(g, diagnostics))
        occupations, before_last, full = {}, {}, {}
        v0 = np.eye(1, len(states), start).ravel()
        residuals = {}
        for time in horizons:
            occupation, _, residual = sampled_occupation(Q, P, solver.pi, start, round(time/cadence), cadence)
            occupations[str(time)] = occupation
            previous = occupation-expm_multiply(Q.T*(time-cadence), v0)
            if previous.min() < -1e-7:
                raise ArithmeticError('Negative two-observation occupation')
            before_last[str(time)] = np.maximum(previous, 0.)
            full[str(time)] = float(solver.finite(sampled, time)[start])
            residuals[str(time)] = residual
            if abs(float(occupation @ g)-full[str(time)]) > 1e-6:
                raise ArithmeticError('Finite-history identity failed')
        row = {'limiting_rate': sampled['rate'], 'poisson_residual': sampled['poisson_residual'],
               'kernel_diagnostics': diagnostics, 'profiles': {}, 'subject_rate_bounds': {}}
        projections = {sub: projected_rows(P, states, fields)
                       for sub, fields in world.metadata['subjects'].items()}
        for time in horizons:
            key = str(time)
            row['profiles'][key] = {'global_bits': full[key], 'subjects': {},
                                   'sampled_occupation_residual': residuals[key]}
        for sub, (groups, future, lower_rows) in projections.items():
            for time in horizons:
                key = str(time)
                row['profiles'][key]['subjects'][sub] = projection_bounds(
                    groups, future, lower_rows, occupations[key], full[key])
            stationary = projection_bounds(groups, future, lower_rows, solver.pi, sampled['rate']*cadence)
            if depth == 2 and sub in ('D', 'S'):
                progress('two-observation '+sub+' dt'+str(cadence))
                r2, upper2 = two_observation_summary(P, groups, future, {**before_last, 'stationary': solver.pi})
                for time in horizons:
                    key = str(time)
                    bounds = row['profiles'][key]['subjects'][sub]
                    lo = max(bounds['lower_bits'], float(lower_rows[start]+before_last[key] @ r2))
                    hi = min(bounds['upper_bits'], float(lower_rows[start]+upper2[key]))
                    if lo > hi+1e-7:
                        raise ArithmeticError('Two-observation bounds inverted')
                    bounds.update(lower_bits=lo, upper_bits=max(lo, hi),
                                  method='two-observation HMM conditioning bounds; no Markov projection')
                stationary['lower_bits'] = max(stationary['lower_bits'], float(solver.pi @ r2))
                stationary['upper_bits'] = min(stationary['upper_bits'], upper2['stationary'])
                if stationary['lower_bits'] > stationary['upper_bits']+1e-7:
                    raise ArithmeticError('Stationary subject bounds inverted')
            row['subject_rate_bounds'][sub] = {
                'lower_bits_per_time': stationary['lower_bits']/cadence,
                'upper_bits_per_time': max(stationary['lower_bits'], stationary['upper_bits'])/cadence}
        result['cadences'][str(cadence)] = row
        del P
    return result
