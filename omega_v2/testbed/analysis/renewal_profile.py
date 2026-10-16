"""Exact reachable restriction, sparse observation sums and reusable horizons."""
import numpy as np
from scipy.sparse import csr_matrix

from .finite_classes import reachable_indices
from .observed_history import entropy_rows


def reachable_world(compiled, roots):
    starts = [compiled['index'][tuple(root)] for root in roots]
    keep = reachable_indices(compiled['Q'], starts)
    outside = np.ones(len(compiled['states']), dtype=bool)
    outside[keep] = False
    if compiled['Q'][keep][:, outside].nnz:
        raise ArithmeticError('Cannot exclude a positive-rate physical extension')
    result = dict(compiled)
    result.update({'states': tuple(compiled['states'][i] for i in keep),
                   'Q': compiled['Q'][keep][:, keep], 'energy': compiled['energy'][keep],
                   'observables': {k: v[keep] for k, v in compiled['observables'].items()},
                   'flows': {k: v[keep] for k, v in compiled['flows'].items()},
                   'full_state_count': len(compiled['states'])})
    result['index'] = {state: i for i, state in enumerate(result['states'])}
    return result


def observation(labels):
    indices, groups = {}, []
    for label in labels:
        groups.append(indices.setdefault(label, len(indices)))
    n = len(groups)
    return csr_matrix((np.ones(n), (np.arange(n), groups)), shape=(n, len(indices)))


def coordinate_shares(kernel, states, order):
    prefix, entropies = [], [np.zeros(len(states))]
    for coordinate in order[:-1]:
        prefix.append(coordinate)
        obs = observation([tuple(state[j] for j in prefix) for state in states])
        future = np.asarray((obs.T @ kernel.T).T)
        entropies.append(entropy_rows(future))
    entropies.append(entropy_rows(kernel))
    return np.diff(np.array(entropies), axis=0)


def hidden_prepared(kernel, labels):
    obs = observation(labels)
    future = np.asarray((obs.T @ kernel.T).T)
    return obs, future, entropy_rows(future), entropy_rows(kernel)


def hidden_bounds(prepared, weights):
    obs, future, row_lower, row_full = prepared
    joint = np.asarray(obs.T @ (weights[:, None]*future))
    marginal = joint.sum(axis=1)
    conditional = np.divide(joint, marginal[:, None], out=np.zeros_like(joint), where=marginal[:, None] > 0)
    lower = float(weights @ row_lower)
    upper = min(float(marginal @ entropy_rows(conditional)), float(weights @ row_full))
    if lower > upper+1e-8:
        raise ArithmeticError('Hidden conditioning bounds failed')
    return {'lower_bits': min(lower, upper), 'upper_bits': max(lower, upper),
            'projected_process_assumed_markov': False}


class SampledHorizons:
    """Binary exact powers shared across roots, horizons and crossover queries."""
    def __init__(self, kernel, maximum_count):
        self.powers, self.sums = [kernel], [np.eye(len(kernel))]
        self.maximum_count = maximum_count
        for _ in range(1, maximum_count.bit_length()):
            self.sums.append(self.sums[-1]+self.powers[-1] @ self.sums[-1])
            self.powers.append(self.powers[-1] @ self.powers[-1])

    def occupation(self, root, count):
        if not 0 <= count <= self.maximum_count:
            raise ValueError('Query exceeds frozen horizon budget')
        state = np.zeros(len(self.powers[0]))
        state[root] = 1.
        weights = np.zeros_like(state)
        for bit in range(count.bit_length()):
            if count & (1 << bit):
                weights += state @ self.sums[bit]
                state = state @ self.powers[bit]
        if abs(state.sum()-1) > 1e-8 or abs(weights.sum()-count) > 1e-8*max(1, count):
            raise ArithmeticError('Exact binary horizon mass failed')
        return weights, state


def horizon_estimate(delta_rate, delta_offset, tolerance=1e-8):
    if abs(delta_rate) <= tolerance:
        return {'status': 'equal-rate; offset diagnostic', 'estimate': None}
    estimate = -delta_offset/delta_rate
    return {'status': 'asymptotic estimate' if estimate > 0 else 'no positive asymptotic crossing',
            'estimate': float(estimate), 'exact_finite_horizon_root': False}
