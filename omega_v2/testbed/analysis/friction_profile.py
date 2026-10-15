"""Global physical histories and certified subject-history bounds.

Projected histories remain hidden-Markov. Bounds and coordinate attribution
are queries over the unchanged physical kernel, never substitute generators.
"""
import numpy as np
from scipy.sparse.linalg import LinearOperator, expm_multiply, gmres, splu

from ..domination_friction import B_FIELDS, D_FIELDS, S_FIELDS, projection
from .class_queries import ClassQueries, occupation_distribution
from .observed_history import entropy_rows
from .temporal_profile import coefficient_rows


def sampled_occupation(Q, P, pi, root, steps, cadence):
    """Exact sampled occupancy via an irreducible transpose Poisson query.

    sum P^t delta_root = steps*pi + (I-P.T+pi*1.T)^-1(root-endpoint).
    Fails on a non-unique stationary class rather than substituting a law.
    """
    n = Q.shape[0]
    if type(steps) is not int or steps < 0 or not 0 <= root < n:
        raise ValueError('Valid integer root and step count required')
    start = np.zeros(n)
    start[root] = 1.
    endpoint = expm_multiply(Q.T*(steps*cadence), start)
    rhs = start-endpoint
    pinned = (-Q.T).tolil()
    pinned.rows[-1] = list(range(n))
    pinned.data[-1] = [1.]*n
    lu = splu(pinned.tocsc())

    def action(v):
        return v-P.T @ v+pi*v.sum()

    def precondition(v):
        b = v/cadence
        b[-1] = v.sum()
        return lu.solve(b)

    correction, info = gmres(LinearOperator((n, n), matvec=action), rhs,
                             M=LinearOperator((n, n), matvec=precondition),
                             rtol=1e-11, atol=1e-12, restart=30, maxiter=150)
    occupancy = steps*pi+correction
    residual = float(max(abs(action(correction)-rhs)))
    if (info != 0 or residual > 1e-8 or min(occupancy) < -1e-8
            or abs(occupancy.sum()-steps) > 1e-8*max(1, steps)):
        raise ArithmeticError('Sampled subject-history occupation failed')
    return occupancy, endpoint, residual


def projected_rows(P, states, fields):
    labels = [projection(s, fields) for s in states]
    index = {x: i for i, x in enumerate(dict.fromkeys(labels))}
    groups = np.array([index[x] for x in labels])
    # Group destination columns without a dense N-by-G incidence matrix.
    future = np.zeros((len(states), len(index)))
    np.add.at(future.T, groups, P.T)
    return groups, future, entropy_rows(future)


def projection_bounds(groups, future, conditional_rows, occupations, full_bits):
    joint = np.zeros((future.shape[1], future.shape[1]))
    np.add.at(joint, groups, occupations[:, None]*future)
    weights = joint.sum(axis=1)
    conditional = np.divide(joint, weights[:, None], out=np.zeros_like(joint),
                            where=weights[:, None] > 0)
    lower = float(occupations @ conditional_rows)
    upper = min(float(weights @ entropy_rows(conditional)), full_bits)
    if lower > upper+1e-7:
        raise ArithmeticError('Subject-history bounds inverted')
    return {'lower_bits': lower, 'upper_bits': max(lower, upper),
            'method': 'full-hidden-state conditioning lower / averaged projected conditional upper',
            'projected_process_assumed_markov': False}


def first_passage(Q, initial, mask, horizon):
    remaining = np.flatnonzero(~np.asarray(mask, dtype=bool))
    if not len(remaining):
        return 1.
    mass = expm_multiply(Q[remaining][:, remaining].T*horizon, initial[remaining]).sum()
    return float(1-mass)


def two_observation_rows(P, groups, future):
    """Joint law of Y1,Y2 conditional on X0; no history pruning.

    Its conditional entropy H(Y2|Y1,X0) tightens the one-observation lower
    bound. Pooling this law by Y0 yields an upper bound conditioned on two
    actual observations, without assuming their process is Markov.
    """
    n, g = future.shape
    joint = np.empty((n, g, g))
    for y in range(g):
        mask = groups == y
        joint[:, y, :] = P[:, mask] @ future[mask]
    conditional = np.divide(joint, future[:, :, None], out=np.zeros_like(joint),
                            where=future[:, :, None] > 0)
    rows = np.sum(future*entropy_rows(conditional), axis=1)
    if max(abs(joint.sum(axis=(1, 2))-1)) > 1e-9:
        raise ArithmeticError('Two-observation probability mass failed')
    return joint, rows


def two_observation_bounds(groups, joint, rows, occupation_before_last,
                           first_entropy, previous):
    pooled = np.zeros((joint.shape[1], joint.shape[1], joint.shape[1]))
    np.add.at(pooled, groups, occupation_before_last[:, None, None]*joint)
    weights = pooled.sum(axis=2)
    conditional = np.divide(pooled, weights[:, :, None], out=np.zeros_like(pooled),
                            where=weights[:, :, None] > 0)
    lower = max(previous['lower_bits'], float(first_entropy+occupation_before_last @ rows))
    upper = min(previous['upper_bits'], float(first_entropy+np.sum(weights*entropy_rows(conditional))))
    if lower > upper+1e-7:
        raise ArithmeticError('Two-observation bounds inverted')
    return {'lower_bits': lower, 'upper_bits': max(lower, upper),
            'method': 'two-observation conditioning, intersected with one-observation bounds',
            'one_observation_bounds': {k: previous[k] for k in ('lower_bits', 'upper_bits')},
            'projected_process_assumed_markov': False}


def profile(compiled, roots, cadences=(.125, .25, .5), horizons=(16, 64, 256, 1024),
            max_kernel_bytes=160*1024**2, subject_depth=1):
    states, Q = compiled['states'], compiled['Q']
    solver = ClassQueries(Q)
    if len(solver.classes) != 1 or len(solver.transient):
        raise ValueError('First subject-bound backend requires an irreducible world')
    pi = solver.stationary[0]
    roots = {name: compiled['index'][tuple(s)] for name, s in roots.items()}
    result = {'states': len(states), 'metadata': compiled['metadata'], 'cadences': {},
              'physical': {}, 'energy_residual': float(max(abs(
                  Q @ compiled['energy']-compiled['flows']['drive_work']
                  +compiled['flows']['bath_heat']))),
              'subject_bounds_can_be_unresolved': True}
    exits, finite, jump = coefficient_rows(Q)
    native_mark = exits*entropy_rows(jump)
    for name, root in roots.items():
        initial = np.zeros(len(states))
        initial[root] = 1.
        physical = {}
        for time in horizons:
            endpoint, occupation = occupation_distribution(Q, initial, time)
            ledger = {key: float(occupation @ value) for key, value in compiled['flows'].items()}
            deadline = {key: float(endpoint @ value) for key, value in compiled['observables'].items()}
            average = {key: float(occupation @ value/time) for key, value in compiled['observables'].items()}
            energy_error = float(endpoint @ compiled['energy']-compiled['energy'][root]
                                 -ledger['drive_work']+ledger['bath_heat'])
            arrivals = {key: first_passage(Q, initial, compiled['observables'][key] > 0, time)
                        for key in ('S.access', 'S.construction', 'S.trap')}
            physical[str(time)] = {'ledger': ledger, 'deadline': deadline, 'average': average,
                                   'first_passage': arrivals, 'integrated_energy_residual': energy_error,
                                   'expected_jumps': float(occupation @ exits),
                                   'finite_term_bits': float(occupation @ finite),
                                   'destination_surprisal_bits': float(occupation @ native_mark),
                                   'reference_time': 1., 'horizon': time,
                                   'suppressed_attempts': float(occupation @ compiled['observables']['suppressed_rate'])}
        result['physical'][name] = physical
    for cadence in cadences:
        sampled = solver.sampled(cadence, max_kernel_bytes)
        P = sampled['P']
        projections = {}
        for subject, fields in (('D', D_FIELDS), ('S', S_FIELDS), ('DS', D_FIELDS+S_FIELDS),
                                ('background', B_FIELDS), ('DB', D_FIELDS+B_FIELDS),
                                ('SB', S_FIELDS+B_FIELDS)):
            projections[subject] = projected_rows(P, states, fields)
        if subject_depth not in (1, 2):
            raise ValueError('Supported certified subject depths: 1 or 2')
        tighter = {subject: two_observation_rows(P, *projections[subject][:2])
                   for subject in ('D', 'S')} if subject_depth == 2 else {}
        row = {'profiles': {}, 'limiting_rate': sampled['class_rates'][0],
               'poisson_residual': sampled['poisson_residual'],
               'kernel_diagnostics': sampled['kernel_diagnostics']}
        for name, root in roots.items():
            scores = {}
            for time in horizons:
                if abs(time/cadence-round(time/cadence)) > 1e-9:
                    raise ValueError('Integral sampled horizon required')
                occupations, _, residual = sampled_occupation(
                    Q, P, pi, root, round(time/cadence), cadence)
                full = float(solver.finite(sampled, time)[root])
                subjects = {subject: projection_bounds(*projections[subject], occupations, full)
                            for subject in ('D', 'S', 'DS')}
                if tighter:
                    start = np.zeros(len(states))
                    start[root] = 1.
                    before_last = occupations-expm_multiply(Q.T*(time-cadence), start)
                    for subject, (joint, lower_rows) in tighter.items():
                        groups, _, single_rows = projections[subject]
                        subjects[subject] = two_observation_bounds(
                            groups, joint, lower_rows, before_last, single_rows[root], subjects[subject])
                d, s, ds = (subjects[x] for x in ('D', 'S', 'DS'))
                mi = {'lower_bits': max(0., d['lower_bits']+s['lower_bits']-ds['upper_bits']),
                      'upper_bits': min(d['upper_bits'], s['upper_bits'],
                                        d['upper_bits']+s['upper_bits']-ds['lower_bits']),
                      'definition': 'I(D history; S history | common exact initial frame)',
                      'joint_DS_excludes_background': True}
                gB = projections['background'][2]
                gDB, gSB = projections['DB'][2], projections['SB'][2]
                hB = float(occupations @ gB)
                hDB, hSB = float(occupations @ gDB), float(occupations @ gSB)
                allowance = time/cadence*sampled['poisson_residual']+1e-7
                if abs(float(occupations @ sampled['g'])-full) > allowance+1e-7:
                    raise ArithmeticError('Physical-history identity failed')
                scores[str(time)] = {'global_bits': full, 'subjects': subjects,
                    'intertwining_bounds': mi,
                    'coordinate_orders': {
                        'background,D,S': {'background': hB, 'D': hDB-hB, 'S': full-hDB},
                        'background,S,D': {'background': hB, 'S': hSB-hB, 'D': full-hSB}},
                    'coordinate_shares_are_not_subject_objectives': True,
                    'sampled_occupation_residual': residual, 'global_numerical_allowance': allowance}
            row['profiles'][name] = scores
        result['cadences'][str(cadence)] = row
    return result
