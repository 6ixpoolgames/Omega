"""Physical readouts for W1/W2. Qualification thresholds remain unfrozen.

Counts explain native pathways; they are not entropy shares. The tracking
diagnostic uses a signal-disabled counterfactual to reduce self-cost confounding.
It remains a diagnostic, not a definition of phenomenal suffering.
"""
import numpy as np
from scipy.linalg import expm
from scipy.sparse import bmat, eye
from scipy.sparse.linalg import expm_multiply

from .observed_history import entropy_rows, observation_map


def occupation_integral(q, root, horizon):
    if not np.isfinite(horizon) or horizon <= 0:
        raise ValueError("Positive finite horizon required")
    n = q.shape[0]
    from scipy.sparse import csr_matrix
    augmented = bmat([[q.T, csr_matrix((n, n))],
                      [eye(n), csr_matrix((n, n))]], format="csr")
    start = np.zeros(2*n)
    start[root] = 1.
    final = expm_multiply(augmented*horizon, start)
    if abs(final[:n].sum()-1) > 1e-9 or abs(final[n:].sum()-horizon) > 1e-8:
        raise ArithmeticError("Occupation mass failed")
    return final[:n], final[n:]


def mutual_information(table):
    table = np.asarray(table, dtype=float)
    mass = table.sum()
    if mass <= 0:
        return None
    table = table/mass
    product = table.sum(axis=1)[:, None]*table.sum(axis=0)[None, :]
    mask = table > 0
    return float(np.sum(table[mask]*np.log2(table[mask]/product[mask])))


def physical_readouts(compiled, reference, root, horizon, window=1., decline_tolerance=1e-6,
                      prepared=None):
    """Reference is a signal-disabled world matched in environment and escape law."""
    if reference['metadata']['signal_mode'] != 'none':
        raise ValueError("Tracking reference must disable the signal")
    if (compiled['states'] != reference['states']
            or compiled['metadata']['escape_available'] != reference['metadata']['escape_available']
            or compiled['metadata']['parameters'] != reference['metadata']['parameters']):
        raise ValueError("Counterfactual physics must be matched")
    if not np.isfinite(window) or window <= 0 or decline_tolerance < 0:
        raise ValueError("Positive tracking window and nonnegative decline tolerance required")
    states = compiled['states']
    final, integral = occupation_integral(compiled['Q'], root, horizon)
    if prepared is None:
        p = expm(compiled['Q'].toarray()*window)
        ref_p = expm(reference['Q'].toarray()*window)
    else:
        p, ref_p = prepared
    # This declared local breadth is of future energy/location, not whole-field
    # entropy and not an entropy reward. Signal is disabled in the reference.
    ref_breadth = entropy_rows(ref_p @ observation_map([x[:2] for x in states]))
    baseline = np.array([ref_breadth[reference['index'][(e, loc, 0, z, patch)]]
                         for e, loc, s, z, patch in states])
    injury_table = np.zeros((2, 2))
    drop_table = np.zeros((2, 2))
    live_time = signal_time = obstructed_time = disposition_sum = feasible_time = 0.
    conditional_drop = np.zeros(2)
    signal_weights = np.zeros(2)
    obstructed_index = signal_intensity = 0.
    for i, state in enumerate(states):
        e, loc, signal, z, _patch = state
        if e == 0:
            continue
        weight = integral[i]
        live_time += weight
        signal_time += weight*signal
        injury_table[signal, int(loc == 0 and z == 1)] += weight
        drop = baseline < baseline[i]-decline_tolerance
        drop_table[signal, 1] += weight*float(p[i, drop].sum())
        drop_table[signal, 0] += weight*float(p[i, ~drop].sum())
        conditional_drop[signal] += weight*float(p[i] @ (baseline[i]-baseline))
        signal_weights[signal] += weight
        if loc == 0 and signal and not compiled['metadata']['escape_available']:
            obstructed_time += weight
        if loc != 0:
            continue

        def action_fraction(s, physical=state):
            e, loc, _, z, patch = physical
            events = [event for module in compiled['world'].modules
                      for event in module.events((e, loc, s, z, patch))
                      if event.family.startswith(('escape_', 'forage_'))]
            total = sum(event.rate for event in events)
            escape = sum(event.rate for event in events if event.family.startswith('escape_'))
            forage = total-escape
            return escape/total if total and forage > 0 and escape > 0 else None

        off, on = action_fraction(0), action_fraction(1)
        if off is not None and on is not None:
            feasible_time += weight
            disposition_sum += weight*(on-off)
            if signal:
                signal_intensity += weight*max(0., on-off)
                if not compiled['metadata']['escape_available']:
                    obstructed_index += weight*max(0., on-off)
    return {
        'live_occupancy_time': live_time, 'signal_occupancy_time': signal_time,
        'signal_fraction_of_live_time': signal_time/live_time if live_time else None,
        'survival_at_deadline': float(sum(final[i] for i, x in enumerate(states) if x[0])),
        'tracking_external_hazard_mi_bits': mutual_information(injury_table),
        'tracking_counterfactual_breadth_drop_mi_bits': mutual_information(drop_table),
        'mean_counterfactual_breadth_drop_by_signal': [
            float(conditional_drop[s]/signal_weights[s]) if signal_weights[s] else None
            for s in range(2)],
        'counterfactual_drop_probability_by_signal': [
            float(drop_table[s, 1]/drop_table[s].sum()) if drop_table[s].sum() else None
            for s in range(2)],
        'escape_disposition_shift': disposition_sum/feasible_time if feasible_time else None,
        'disposition_supported_occupancy_time': feasible_time,
        'obstructed_signal_time': obstructed_time,
        'signal_intensity_time': signal_intensity,
        'operational_obstructed_suffering_index': obstructed_index,
        'event_counts': {name: float(integral @ rate) for name, rate in compiled['flows'].items()},
        'tracking_window': window, 'tracking_decline_tolerance': decline_tolerance,
        'qualification': 'unscored: T/D thresholds and suffering index not scientifically frozen',
        'tracking_definition': 'MI with future drop in signal-disabled energy/location breadth',
        'event_counts_are_entropy_decomposition': False,
    }


def coordinate_shares(kernel, states, root, steps, order=(3, 4, 0, 1, 2)):
    """Exact destination chain-rule shares given the complete physical past.

Order: hazard, patch, energy, location, signal. Not native event attribution.
"""
    row_shares = coordinate_row_shares(kernel, states, order)
    distribution = np.zeros(len(states))
    distribution[root] = 1.
    total = np.zeros(len(order))
    for _ in range(steps):
        total += row_shares @ distribution
        distribution = distribution @ kernel
    return {'order': list(order), 'bits': total.tolist(),
            'interpretation': 'destination coordinates conditioned on full past; not event families'}


def coordinate_row_shares(kernel, states, order=(3, 4, 0, 1, 2)):
    """One-step chain-rule shares reusable with exact sampled occupations."""
    if tuple(sorted(order)) != tuple(range(len(states[0]))):
        raise ValueError("Order must include each physical coordinate exactly once")
    prefix_entropies = [np.zeros(len(states))]
    for k in range(1, len(order)+1):
        labels = [tuple(x[j] for j in order[:k]) for x in states]
        prefix_entropies.append(entropy_rows(kernel @ observation_map(labels)))
    return np.diff(np.array(prefix_entropies), axis=0)
