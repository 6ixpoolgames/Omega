"""Neutral, conservative catalytic-depth queries over native reaction routes.

The initial-seed monitor never restarts. The optional any-start detector counts
non-overlapping certified completions and can miss arbitrarily many true chains.
Neither monitor state nor reaction-route labels enter physical history entropy.
"""
import numpy as np
from scipy.sparse import coo_matrix

WAIT, LINK1, LINK2, SUCCESS, FAILURE = range(5)


def eligible(state):
    return tuple(state[2:5]) == (1, 0, 0)


def initial_update(phase, state, event):
    """Deterministic native-event update; success/failure are permanent flags."""
    t = event.target
    if phase in (SUCCESS, FAILURE):
        return phase
    if phase == WAIT:
        if not eligible(state):
            return FAILURE
        if event.family == 'paid_assisted_A_to_B':
            return LINK1
        return WAIT if eligible(t) else FAILURE
    if phase == LINK1:
        if state[3] != 1 or state[4] != 0:
            return FAILURE
        if event.family == 'paid_assisted_B_to_C':
            return LINK2
        return LINK1 if t[3] == 1 and t[4] == 0 else FAILURE
    if phase == LINK2:
        if state[4] != 1:
            return FAILURE
        if event.family == 'paid_assisted_C_to_A':
            return SUCCESS
        return LINK2 if t[4] == 1 else FAILURE
    raise ValueError('Unknown primary monitor state')


def any_start_update(phase, state, event):
    """Three phases; failures/completions return to WAIT, no same-event restart."""
    if phase == WAIT:
        return (LINK1, 0.) if eligible(state) and event.family == 'paid_assisted_A_to_B' else (WAIT, 0.)
    next_phase = initial_update(phase, state, event)
    if next_phase == SUCCESS:
        return WAIT, 1.
    return (WAIT if next_phase == FAILURE else next_phase), 0.


def compile_monitor(compiled, mode='initial_seed'):
    """Sparse (X, query-state) generator, exactly projecting to physical Q.

    States are indexed physical_index * phases + monitor_index. Native channels
    may share an endpoint while advancing the query differently. This is a
    query over reaction mechanisms, not additional distinguishable outcomes.
    """
    if mode not in ('initial_seed', 'any_start'):
        raise ValueError('Unknown monitor')
    world, index, q = compiled['world'], compiled['index'], compiled['Q']
    phases = 5 if mode == 'initial_seed' else 3
    size = len(world.states)*phases
    rows, cols, rates = [], [], []
    completions = np.zeros(size)
    for i, state in enumerate(world.states):
        events = [event for module in world.modules for event in module.events(state)]
        for m in range(phases):
            source = i*phases+m
            for event in events:
                if mode == 'initial_seed':
                    target_m, count = initial_update(m, state, event), 0.
                else:
                    target_m, count = any_start_update(m, state, event)
                rows.append(source); cols.append(index[event.target]*phases+target_m); rates.append(event.rate)
                completions[source] += event.rate*count
            rows.append(source); cols.append(source); rates.append(q[i, i])
    lifted = coo_matrix((rates, (rows, cols)), shape=(size, size)).tocsr()
    projection = coo_matrix((np.ones(size), (np.arange(size), np.repeat(np.arange(len(world.states)), phases))),
                            shape=(size, len(world.states))).tocsr()
    error = lifted @ projection-projection @ q
    residual = float(np.max(np.abs(error.data))) if error.nnz else 0.
    if residual > 1e-10:
        raise ArithmeticError('Query monitor changes the physical generator')
    return {'Q': lifted, 'phases': phases, 'projection': projection,
            'projection_residual': residual, 'completion_intensity': completions,
            'mode': mode, 'entropy_eligible': False}


def initial_distribution(compiled, monitor, physical_initial):
    n, phases = len(compiled['states']), monitor['phases']
    v = np.asarray(physical_initial, dtype=float)
    if v.shape != (n,) or np.min(v) < 0 or abs(v.sum()-1) > 1e-10:
        raise ValueError('Normalized physical initial distribution required')
    result = np.zeros(n*phases)
    for i, state in enumerate(compiled['states']):
        phase = WAIT if monitor['mode'] == 'any_start' or eligible(state) else FAILURE
        result[i*phases+phase] = v[i]
    return result


def success_joint(endpoint, monitor, physical_mask):
    if monitor['mode'] != 'initial_seed':
        raise ValueError('An ongoing detector has no permanent success flag')
    values = np.asarray(endpoint).reshape((-1, monitor['phases']))
    return float(values[np.asarray(physical_mask, dtype=bool), SUCCESS].sum())


def detected_chain_profile(monitor, initial_lifted, horizon):
    """Finite-window lower-bound detection intensity; not population genealogy."""
    if monitor['mode'] != 'any_start' or not np.isfinite(horizon) or horizon <= 0:
        raise ValueError('Any-start detector and positive finite horizon required')
    from .class_queries import reward_integral
    final, count = reward_integral(monitor['Q'], initial_lifted,
                                  monitor['completion_intensity'], horizon)
    if count < -1e-10 or abs(final.sum()-1.) > 1e-9:
        raise ArithmeticError('Detector completion query failed')
    return {'expected_detected_nonoverlapping_chains': max(0., count),
            'detected_chain_rate': max(0., count)/horizon,
            'is_population_generation_rate': False}
