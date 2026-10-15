"""Exact physical and sampled-history outputs for the frozen cyclic experiment.

No semantic rewards or survival conditioning. Query-side monitors never enter
the physical state entropy. A deterministic pulse is a known boundary map.
"""
import numpy as np
from scipy.sparse import bmat, csr_matrix, eye
from scipy.sparse.linalg import expm_multiply

from ..robust_generativity import physical_readouts
from .class_queries import ClassQueries, pulse_kernel
from .generativity_depth import compile_monitor, detected_chain_profile, initial_distribution
from .generativity_robustness import closure_targets, depth_profile, pulse_readout
from .same_law_profile import fixed_jump_vectors


def activity_rows(Q, reference_time=1.):
    off = Q.copy(); off.setdiag(0.); off.eliminate_zeros()
    exits = -Q.diagonal()
    log_rate = off.copy(); log_rate.data *= np.log2(log_rate.data*reference_time)
    finite = exits*np.log2(np.e)-np.asarray(log_rate.sum(axis=1)).ravel()
    inverse = np.zeros_like(exits); np.divide(1., exits, out=inverse, where=exits > 0)
    jump = off.multiply(inverse[:, None]).tocsr()
    zero = np.flatnonzero(exits == 0)
    if len(zero):
        jump = jump.tolil(); jump[zero, zero] = 1.; jump = jump.tocsr()
    terms = jump.copy(); terms.data = -terms.data*np.log2(terms.data)
    marks = np.asarray(terms.sum(axis=1)).ravel()
    return exits, finite, jump, marks


def physical_profiles(compiled, roots, horizons, pulse=False, pulse_time=64.):
    """Simultaneous forward/occupation propagation, including pulse heat."""
    q = compiled['Q']; n = q.shape[0]
    names = list(roots)
    start = np.column_stack([roots[k] for k in names])
    matrix = bmat([[q.T, csr_matrix((n, n))], [eye(n), csr_matrix((n, n))]], format='csr')
    augmented = np.vstack([start, np.zeros_like(start)])
    kernel, release = pulse_kernel(compiled)
    boundary_heat = np.zeros(len(names))
    elapsed = 0.; pulsed = False
    checkpoints = sorted(set(horizons) | {pulse_time})
    targets = closure_targets(compiled)
    exits, finite, jump, marks = activity_rows(q)
    jump_vectors = fixed_jump_vectors(jump, marks, (8, 32, 128))
    rows = {k: {} for k in names}
    endpoints, occupations = {}, {}
    pulse_before = None
    for time in checkpoints:
        augmented = expm_multiply(matrix*(time-elapsed), augmented)
        final, occupation = augmented[:n], augmented[n:]
        if np.max(abs(final.sum(axis=0)-1.)) > 1e-9 or np.max(abs(occupation.sum(axis=0)-time)) > 1e-7:
            raise ArithmeticError('Physical timeline mass/occupation residual')
        endpoints[time] = final.copy(); occupations[time] = occupation.copy()
        if time in horizons:
            for col, name in enumerate(names):
                f, w = final[:, col], occupation[:, col]
                ledger = physical_readouts(compiled, f, w, roots[name], boundary_heat[col])
                bath_births = ledger.get('thermal_births', 0.)+ledger.get('unpowered_births', 0.)
                all_births = bath_births+ledger.get('paid_births', 0.)
                rows[name][str(time)] = {
                    'deadline': {k: float(f @ v) for k, v in compiled['observables'].items()},
                    'integrated': {k: float(w @ v) for k, v in compiled['observables'].items()},
                    'closure': {k: float(f @ v['mask']) for k, v in targets.items()},
                    'ledger': ledger, 'thermal_forward_fraction': bath_births/all_births if all_births else None,
                    'expected_jumps': float(w @ exits), 'finite_temporal_bits': float(w @ finite),
                    'expected_local_destination_surprisal': float(w @ (exits*marks))}
        if time == pulse_time:
            pulse_before = final.copy()
            if pulse:
                boundary_heat += final.T @ release
                augmented[:n] = (final.T @ kernel).T
                pulsed = True
        elapsed = time
    first_arrivals = {}
    # Killed-process probabilities, including reference roots initially in target.
    for target_name in ('loop', 'expanded'):
        mask = compiled['observables'][target_name] > 0
        keep = np.flatnonzero(~mask)
        killed = q[keep][:, keep].T.tocsr()
        mass = start[keep].copy(); previous = 0.
        record = {}
        for time in sorted({16., 64., 256.} & set(horizons)):
            mass = expm_multiply(killed*(time-previous), mass)
            record[str(time)] = {name: float(np.clip(1-mass[:, i].sum(), 0, 1)) for i, name in enumerate(names)}
            if pulse and time == pulse_time:
                mass = (mass.T @ kernel[keep][:, keep]).T
            previous = time
        first_arrivals[target_name] = record
    at_start = endpoints[pulse_time]
    at_end = endpoints[256.]
    loop = compiled['observables']['loop'] > 0
    keep = np.flatnonzero(loop)
    uninterrupted_start = at_start[keep].copy()
    if pulse:
        uninterrupted_start = (uninterrupted_start.T @ kernel[keep][:, keep]).T
    uninterrupted = expm_multiply(q[keep][:, keep].T*(256.-pulse_time), uninterrupted_start)
    for i, name in enumerate(names):
        rows[name]['persistence'] = {
            'tau_up': float(occupations[256.][:, i] @ loop),
            'post_startup_uptime_fraction': float((occupations[256.][:, i]-occupations[pulse_time][:, i]) @ loop)/(256.-pulse_time),
            'uninterrupted_loop_from_startup_probability': float(uninterrupted[:, i].sum()),
            'loop_at_startup': float(at_start[:, i] @ loop),
            'loop_at_primary_deadline': float(at_end[:, i] @ loop)}
    return {'rows': rows, 'names': names, 'endpoints': endpoints, 'occupations': occupations,
            'first_arrivals': first_arrivals, 'pulse_before': pulse_before,
            'pulse_after': (pulse_before.T @ kernel).T if pulsed else pulse_before,
            'fixed_jump_bits': {name: {k: float(roots[name] @ v) for k, v in jump_vectors.items()} for name in names},
            'closure_certificates': {k: v['certificate'] for k, v in targets.items()}}


def coordinate_rows(P, states, order=(1, 0, 5, 2, 3, 4)):
    """H(next coordinate | full past state, earlier next coordinates)."""
    n = len(states); previous = np.zeros(n); result = []
    for depth in range(1, len(order)+1):
        prefixes = [tuple(s[k] for k in order[:depth]) for s in states]
        labels = {key: i for i, key in enumerate(sorted(set(prefixes)))}
        ids = np.array([labels[key] for key in prefixes])
        mapping = csr_matrix((np.ones(n), (np.arange(n), ids)), shape=(n, len(labels)))
        entropy = np.empty(n)
        for lo in range(0, n, 32):
            values = P[lo:lo+32] @ mapping
            logs = np.zeros_like(values); np.log2(values, out=logs, where=values > 0)
            entropy[lo:lo+32] = -(values*logs).sum(axis=1)
        contribution = entropy-previous
        if min(contribution) < -1e-10:
            raise ArithmeticError('Coordinate conditional entropy is negative')
        result.append(contribution); previous = entropy
    return np.column_stack(result)


def history_value(queries, sampled, initial, horizon, pulse=False, pulse_time=64., pulse_after=None):
    if pulse and horizon > pulse_time:
        if pulse_after is None:
            raise ValueError('Post-pulse physical distribution required')
        return float(initial @ queries.finite(sampled, pulse_time)
                     +pulse_after @ queries.finite(sampled, horizon-pulse_time))
    return float(initial @ queries.finite(sampled, horizon))


def sampled_profiles(compiled, roots, physical, protocol, pulse=False):
    queries = ClassQueries(compiled['Q'])
    names = physical['names']; times = protocol['measurement']['horizons']
    out = {}
    pulse_time = protocol['measurement']['startup_checkpoint']
    for cadence in protocol['measurement']['cadences']:
        sampled = queries.sampled(cadence, protocol['max_kernel_bytes'])
        offset = queries.limiting_offset(sampled)
        base64 = queries.finite(sampled, pulse_time)
        vectors = {time: queries.finite(sampled, time) for time in times}
        postvectors = {time: queries.finite(sampled, time-pulse_time) for time in times if time > pulse_time} if pulse else {}
        profiles = {}
        for col, name in enumerate(names):
            initial = roots[name]; after = physical['pulse_after'][:, col]
            rate = float((after if pulse else initial) @ sampled['rate'])
            b = float(initial @ base64+after @ offset-pulse_time*rate) if pulse else float(initial @ offset)
            bits = {str(time): float(initial @ base64+after @ postvectors[time]) if pulse and time > pulse_time
                    else float(initial @ vectors[time]) for time in times}
            profiles[name] = {'bits': bits, 'limiting_rate': rate, 'limiting_offset': b,
                'tail_bits': {str(t): bits[str(t)]-t*rate-b for t in times}}
        row = {'profiles': profiles, 'poisson_residual': sampled['poisson_residual'],
               'harmonic_rate_residual': sampled['harmonic_rate_residual'],
               'kernel_residuals': sampled['kernel_diagnostics']}
        if cadence == protocol['measurement']['primary_cadence']:
            rewards = coordinate_rows(sampled['P'], compiled['states'])
            if max(abs(rewards.sum(axis=1)-sampled['g'])) > 1e-9:
                raise ArithmeticError('Coordinate decomposition does not sum to physical entropy')
            contributions = {name: {} for name in names}
            for col, label in enumerate(('packet', 'bank', 'unavailable', 'A', 'B', 'C')):
                solution = queries.reward_solution(sampled, rewards[:, col])
                for i, name in enumerate(names):
                    contributions[name][label] = history_value(queries, solution, roots[name], 256., pulse,
                                                              pulse_time, physical['pulse_after'][:, i])
            for name in names:
                if abs(sum(contributions[name].values())-profiles[name]['bits']['256']) > 1e-5:
                    raise ArithmeticError('Integrated coordinate decomposition failed')
            row['coordinate_bits_T256'] = contributions
        out[str(cadence)] = row
        del sampled, vectors, postvectors
    return out


def structural_queries(compiled, roots, pulse=False):
    initial = roots['seed']
    monitor = compile_monitor(compiled)
    lifted = initial_distribution(compiled, monitor, initial)
    depth = depth_profile(compiled, monitor, lifted, startup=64., horizon=256., pulse=pulse)
    projection = monitor['projection_residual']
    del monitor, lifted
    monitor = compile_monitor(compiled, 'any_start')
    lifted = initial_distribution(compiled, monitor, initial)
    if pulse:
        # Restart/failure conventions are applied to the prescribed pulse too.
        from ..contracts import Event
        from .generativity_depth import any_start_update
        targets = []
        for state in compiled['states']:
            t = list(state); t[3] -= min(1, t[3]); t = tuple(t)
            ev = Event('pulse', 'pulse', t, 1., (3,))
            for phase in range(3):
                m, _ = any_start_update(phase, state, ev)
                targets.append(compiled['index'][t]*3+m)
        from .class_queries import reward_integral
        first, count1 = reward_integral(monitor['Q'], lifted, monitor['completion_intensity'], 64.)
        after = np.bincount(targets, weights=first, minlength=len(lifted))
        _, count2 = reward_integral(monitor['Q'], after, monitor['completion_intensity'], 192.)
        ongoing = {'expected_detected_nonoverlapping_chains': count1+count2,
                   'detected_chain_rate': (count1+count2)/256., 'is_population_generation_rate': False}
    else:
        ongoing = detected_chain_profile(monitor, lifted, 256.)
    return {'initial_seed': depth, 'ongoing_detector': ongoing,
            'monitor_projection_residual': max(projection, monitor['projection_residual']),
            'pulse_recovery': pulse_readout(compiled, initial, 64., (16., 64., 128.)) if pulse else None}


def run_experiment(compiled, protocol, pulse=False):
    from ..robust_generativity import matched_roots
    roots = matched_roots(compiled)
    physical = physical_profiles(compiled, roots, protocol['measurement']['horizons'], pulse)
    sampled = sampled_profiles(compiled, roots, physical, protocol, pulse)
    structure = structural_queries(compiled, roots, pulse)
    return {'states': len(compiled['states']), 'physical': physical['rows'],
            'first_arrivals': physical['first_arrivals'], 'fixed_jump_bits': physical['fixed_jump_bits'],
            'fixed_jump_scope': 'maintained native Q, not equal physical durations or the prescribed pulse schedule',
            'closure_certificates': physical['closure_certificates'], 'sampled': sampled, 'structure': structure,
            'references': {name: {'support': int(np.count_nonzero(mu)),
                                  'initial_apparatus': float(mu @ compiled['observables']['apparatus']),
                                  'initial_loop': float(mu @ compiled['observables']['loop']),
                                  'energy': float(mu @ compiled['energy'])} for name, mu in roots.items()}}
