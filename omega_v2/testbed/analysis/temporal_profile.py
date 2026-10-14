"""Temporal-resolution diagnostics for a fixed finite non-explosive CTMC.

The divergent coefficient is expected state-changing jump count. F is a
reference-dependent finite term, not organization or a replacement objective.
Counting augmentation is query-side only; overflow probability is retained.
"""
import numpy as np
from scipy.sparse import bmat, diags
from scipy.sparse.linalg import expm_multiply
from scipy.stats import poisson

from .finite_classes import _generator, finite_history_bits, reachable_indices
from .observed_history import entropy_rows
from .signal_readouts import occupation_integral


def coefficient_rows(Q, reference_time=1.):
    if not np.isfinite(reference_time) or reference_time <= 0:
        raise ValueError('Positive finite reference time required')
    q = _generator(Q)
    exits = -q.diagonal()
    off = q.copy()
    off.setdiag(0.)
    off.eliminate_zeros()
    logs = off.copy()
    logs.data = off.data*np.log2(off.data*reference_time)
    finite = exits*np.log2(np.e)-np.asarray(logs.sum(axis=1)).ravel()
    jump = off.toarray()
    np.divide(jump, exits[:, None], out=jump, where=exits[:, None] > 0)
    zero = np.flatnonzero(exits == 0)
    jump[zero, zero] = 1.  # deterministic terminal padding, no clock/entropy
    return exits, finite, jump


def coefficients(Q, root, horizon, reference_time=1.):
    q = _generator(Q)
    exits, finite, jump = coefficient_rows(q, reference_time)
    _, occupation = occupation_integral(q, root, horizon)
    local_mark = exits*entropy_rows(jump)
    return {'expected_jumps': float(occupation @ exits),
            'finite_term_bits': float(occupation @ finite),
            'expected_native_destination_surprisal_bits': float(occupation @ local_mark),
            'horizon': horizon, 'reference_time': reference_time,
            'mark_readout_is_random_length_sequence_entropy': False}


def expansion(coordinate, cadence):
    if not np.isfinite(cadence) or cadence <= 0:
        raise ValueError('Positive finite cadence required')
    return (coordinate['expected_jumps']*np.log2(coordinate['reference_time']/cadence)
            +coordinate['finite_term_bits'])


def crossover(left, right, tolerance=1e-10):
    if left['reference_time'] != right['reference_time'] or left['horizon'] != right['horizon']:
        raise ValueError('Matched horizon and clock reference required')
    dn = left['expected_jumps']-right['expected_jumps']
    df = left['finite_term_bits']-right['finite_term_bits']
    if abs(dn) <= tolerance:
        return {'delta_jumps': dn, 'delta_finite_bits': df,
                'status': 'finite-term ordering' if abs(df) > tolerance else 'degenerate',
                'estimated_cadence': None, 'log2_estimated_cadence': None}
    log_cadence = float(np.log2(left['reference_time'])+df/dn)
    cadence = float(2.**log_cadence) if -1022 < log_cadence < 1023 else None
    return {'delta_jumps': dn, 'delta_finite_bits': df, 'status': 'asymptotic estimate',
            'estimated_cadence': cadence, 'log2_estimated_cadence': log_cadence,
            'not_an_exact_finite_cadence_crossing': True}


def fixed_jump_bits(Q, root, jump_counts=(8, 32, 128)):
    _, _, jump = coefficient_rows(Q)
    return {str(count): float(finite_history_bits(jump, count)[root]) for count in jump_counts}


def count_entropy_bounds(Q, root, horizon, tail_budget=1e-10, max_augmented_states=100000):
    """H(N_T) from count-resolved CTMC with a retained overflow cell.

    Poisson uniformization bounds N_T above. At cap K we retain P(N>=K),
    not condition on N<K. Geometric maximum entropy bounds unresolved tail
    entropy using E[N]<=lambda*T. No event count is added to lushness.
    """
    q_full = _generator(Q)
    keep = reachable_indices(q_full, root)
    root = int(np.flatnonzero(keep == root)[0])
    q = q_full[keep][:, keep]
    if not 0 < tail_budget < 1 or not np.isfinite(horizon) or horizon <= 0:
        raise ValueError('Positive horizon and probability tail budget required')
    maximum_exit = float(max(-q.diagonal()))
    mean_bound = maximum_exit*horizon
    if mean_bound == 0:
        return {'lower_bits': 0., 'upper_bits': 0., 'count_cap': 0,
                'overflow_mass': 0., 'poisson_tail_bound': 0., 'augmented_states': q.shape[0],
                'probability_mass_residual': 0., 'query_not_added_to_physical_entropy': True}
    cap = int(poisson.isf(tail_budget, mean_bound))+1
    while poisson.sf(cap-1, mean_bound) > tail_budget:
        cap += 1
    n = q.shape[0]
    if n*(cap+1) > max_augmented_states:
        raise MemoryError('Count-query augmentation exceeds declared budget; no truncation')
    off = q.copy()
    off.setdiag(0.)
    off.eliminate_zeros()
    hold = diags(q.diagonal())
    blocks = [[None]*(cap+1) for _ in range(cap+1)]
    for count in range(cap):
        blocks[count][count] = hold
        blocks[count][count+1] = off
    blocks[cap][cap] = q  # complete physical dynamics continue in the overflow cell
    augmented = bmat(blocks, format='csr')
    initial = np.zeros(n*(cap+1))
    initial[root] = 1.
    final = expm_multiply(augmented.T*horizon, initial)
    pmf = final.reshape(cap+1, n).sum(axis=1)
    mass_error = float(abs(pmf.sum()-1))
    if mass_error > 1e-9 or pmf.min() < -1e-12:
        raise ArithmeticError('Count-query probability mass failed')
    lower = float(entropy_rows(pmf))
    delta = float(poisson.sf(cap-1, mean_bound))
    mean = mean_bound/delta
    geometric_entropy = np.log2(mean+1)+mean*np.log1p(1/mean)/np.log(2.)
    tail_entropy = float(delta*geometric_entropy)
    return {'lower_bits': lower, 'upper_bits': lower+tail_entropy,
            'count_cap': cap, 'overflow_mass': float(pmf[-1]),
            'poisson_tail_bound': delta, 'tail_entropy_bound_bits': tail_entropy,
            'augmented_states': n*(cap+1), 'probability_mass_residual': mass_error,
            'query_not_added_to_physical_entropy': True,
            'separately_conditioned_mark_and_timing_entropy': 'not computed'}
