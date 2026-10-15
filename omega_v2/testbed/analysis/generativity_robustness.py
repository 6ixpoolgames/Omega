"""Physical functioning, graph closure, pulses and joint path queries.

All statistics are descriptive; none changes the objective or the native Q.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply

from ..contracts import Event
from .channel_access import closure_certificate, closure_mask
from .class_queries import pulse_kernel, reward_integral
from .generativity_depth import SUCCESS, initial_update, success_joint


def closure_targets(compiled):
    result = {}
    for name in ('loop', 'expanded'):
        mask = closure_mask(compiled['Q'], compiled['observables'][name] > 0)
        certificate = closure_certificate(compiled['Q'], mask)
        if not certificate['closed']:
            raise ArithmeticError('Closure set has an outgoing edge')
        result[name] = {'mask': mask, 'certificate': certificate}
    return result


def endpoint(Q, initial, duration):
    if not np.isfinite(duration) or duration < 0:
        raise ValueError('Nonnegative finite duration required')
    values = np.asarray(expm_multiply(Q.T*duration, initial)).ravel()
    if not np.all(np.isfinite(values)) or min(values) < -1e-10 or abs(values.sum()-initial.sum()) > 1e-9:
        raise ArithmeticError('Propagation failed probability conservation')
    return np.maximum(values, 0.)


def pulse_readout(compiled, initial, pulse_time=64., delays=(16., 64., 128.)):
    """Joint pre-function AND endpoint restoration; initial failures remain."""
    before = endpoint(compiled['Q'], initial, pulse_time)
    kernel, release = pulse_kernel(compiled)
    functional = compiled['observables']['loop'] > 0
    pre_mass = float(before @ functional)
    selected_after = np.asarray((before*functional) @ kernel).ravel()
    all_after = np.asarray(before @ kernel).ravel()
    result = {'pre_function_probability': pre_mass, 'released_energy': float(before @ release), 'delays': {}}
    for delay in delays:
        restored = endpoint(compiled['Q'], selected_after, delay)
        all_endpoint = endpoint(compiled['Q'], all_after, delay)
        joint = float(restored @ functional)
        result['delays'][str(delay)] = {'pre_function_and_endpoint_recovery': joint,
            'conditional_endpoint_recovery': joint/pre_mass if pre_mass else None,
            'unconditional_endpoint_function': float(all_endpoint @ functional)}
    return result


def lifted_pulse(compiled, monitor):
    """Prescribed damage also advances/fails pending lineage queries."""
    if monitor['mode'] != 'initial_seed':
        raise ValueError('Initial-seed pulse query required')
    phases = monitor['phases']
    targets = []
    for state in compiled['states']:
        t = list(state); t[3] -= min(1, t[3]); t = tuple(t)
        event = Event('prescribed_pulse', 'prescribed_pulse', t, 1., (3,))
        for m in range(phases):
            targets.append(compiled['index'][t]*phases+initial_update(m, state, event))
    n = len(targets)
    return coo_matrix((np.ones(n), (np.arange(n), targets)), shape=(n, n)).tocsr()


def depth_profile(compiled, monitor, initial_lifted, startup=64., horizon=256., pulse=False):
    """Initial-seed success, retained expansion and the stronger same-path event."""
    if monitor['mode'] != 'initial_seed' or not 0 <= startup <= horizon:
        raise ValueError('Initial-seed query with valid checkpoints required')
    q, phases = monitor['Q'], monitor['phases']
    at_start = endpoint(q, initial_lifted, startup)
    depth_at_start = success_joint(at_start, monitor, np.ones(len(compiled['states']), dtype=bool))
    closure = closure_targets(compiled)['loop']['mask']
    loop = compiled['observables']['loop'] > 0
    expanded = compiled['observables']['expanded'] > 0
    selected = at_start.reshape((-1, phases)).copy()
    selected[:, :SUCCESS] = 0.; selected[:, SUCCESS+1:] = 0.
    selected[~loop | closure, :] = 0.
    selected = selected.ravel()
    if pulse:
        kernel = lifted_pulse(compiled, monitor)
        at_start = np.asarray(at_start @ kernel).ravel()
        selected = np.asarray(selected @ kernel).ravel()
    at_end = endpoint(q, at_start, horizon-startup)
    selected_end = endpoint(q, selected, horizon-startup)
    # Graph closure is absorbing. Endpoint exclusion therefore also excludes
    # paths that ever entered closure after the startup checkpoint.
    return {'depth_by_startup': depth_at_start,
            'depth_by_deadline': success_joint(at_end, monitor, np.ones(len(loop), dtype=bool)),
            'depth_and_retained_expansion': success_joint(at_end, monitor, expanded),
            'depth_by_startup_loop_then_expansion_no_closure': success_joint(selected_end, monitor, expanded & ~closure)}


def uptime(compiled, initial, horizon):
    final, time = reward_integral(compiled['Q'], initial, compiled['observables']['loop'], horizon)
    return {'expected_functional_uptime': time, 'uptime_fraction': time/horizon if horizon else None,
            'deadline_loop_probability': float(final @ compiled['observables']['loop'])}
