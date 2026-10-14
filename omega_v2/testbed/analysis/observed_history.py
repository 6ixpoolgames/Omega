"""Certified conditioning bounds for a deterministic observation of a Markov law.

The projected process is generally non-Markov. Never use a merged generator.
At each step H(Y_next|X_now) <= H(Y_next|Y_history) <= H(Y_next|Y_now).
Known initial physical state is conditioned throughout. No estimator/tail cutoff.
"""
import numpy as np


def entropy_rows(probabilities):
    p = np.asarray(probabilities, dtype=float)
    log = np.zeros_like(p)
    np.log2(p, out=log, where=p > 0)
    return -(p*log).sum(axis=-1)


def observation_map(labels):
    index = {}
    groups = []
    for label in labels:
        if label not in index:
            index[label] = len(index)
        groups.append(index[label])
    matrix = np.zeros((len(groups), len(index)))
    matrix[np.arange(len(groups)), groups] = 1.
    return matrix


def sampled_occupations(kernel, root, step_counts):
    """Exact sums of sampled state distributions by binary composition.

    No probability pruning, stationary replacement or truncated horizon.
    Returns sum_{t=0}^{n-1} delta_root P^t and delta_root P^n.
    """
    p = np.asarray(kernel, dtype=float)
    if (p.ndim != 2 or p.shape[0] != p.shape[1] or not np.isfinite(p).all()
            or p.min() < -1e-12 or np.max(abs(p.sum(axis=1)-1)) > 1e-10):
        raise ValueError('Valid sampled kernel required')
    if type(root) is not int or not 0 <= root < len(p):
        raise ValueError('Integer root required')
    if not step_counts or any(type(n) is not int or n < 0 for n in step_counts):
        raise ValueError('Nonempty nonnegative integer step counts required')
    powers, sums = [p], [np.eye(len(p))]
    for _ in range(1, max(step_counts).bit_length()):
        sums.append(sums[-1]+powers[-1] @ sums[-1])
        powers.append(powers[-1] @ powers[-1])
    result = {}
    for count in step_counts:
        distribution = np.zeros(len(p))
        distribution[root] = 1.
        occupation = np.zeros(len(p))
        for bit in range(count.bit_length()):
            if count & (1 << bit):
                occupation += distribution @ sums[bit]
                distribution = distribution @ powers[bit]
        if (abs(distribution.sum()-1) > 1e-8
                or abs(occupation.sum()-count) > 1e-8*max(1, count)):
            raise ArithmeticError('Binary sampled occupation mass failed')
        result[count] = (occupation, distribution)
    return result


def averaged_observation_bounds(kernel, labels, occupation):
    """Efficient HMM bounds using concavity of conditional entropy across time.

    Lower: sum H(Y_next|X_now). Upper: n H(Y_next|Y_now) under the
    time-averaged joint law, capped by exact full-history entropy. The upper
    bound can be looser than summing separate-time conditional entropies.
    """
    p = np.asarray(kernel, dtype=float)
    weights = np.asarray(occupation, dtype=float)
    if weights.shape != (len(p),) or weights.min() < -1e-10:
        raise ValueError('Nonnegative physical occupation required')
    obs = observation_map(labels)
    future = p @ obs
    lower = float(weights @ entropy_rows(future))
    joint = obs.T @ (weights[:, None]*future)
    marginal = joint.sum(axis=1)
    conditional = np.divide(joint, marginal[:, None], out=np.zeros_like(joint),
                            where=marginal[:, None] > 0)
    upper = min(float(marginal @ entropy_rows(conditional)),
                float(weights @ entropy_rows(p)))
    if lower > upper+1e-8:
        raise ArithmeticError('Averaged conditioning bounds inverted')
    return {'lower_bits': lower, 'upper_bits': upper,
            'method': 'hidden-state lower / time-averaged observation conditional upper',
            'projected_process_assumed_markov': False}


def projected_offset_bounds(analysis, labels, root):
    """Asymptotic offset bounds when observation resolves every recurrent state.

    Recurrent observations must be injective and disjoint from transient ones.
    This applies to hiding a living signal whose register is zero after death.
    It does not assume the projected live dynamics are Markov.
    """
    p, pi = analysis['P'], analysis['Pi']
    if pi is None:
        raise MemoryError('Full limiting projection required for offset bounds')
    recurrent = np.zeros(len(p), dtype=bool)
    for members in analysis['class_indices']:
        recurrent[members] = True
    recurrent_labels = [labels[i] for i in np.flatnonzero(recurrent)]
    transient_labels = {labels[i] for i in np.flatnonzero(~recurrent)}
    if (len(set(recurrent_labels)) != len(recurrent_labels)
            or set(recurrent_labels) & transient_labels):
        raise ValueError('Projection must resolve recurrent states distinctly')
    obs = observation_map(labels)
    future = p @ obs
    g = entropy_rows(future)
    # Sum of P^t - Pi, with its stationary component removed.
    fundamental = np.linalg.solve(np.eye(len(p))-p+pi, np.eye(len(p)))-pi
    occupation_offset = fundamental[root]
    transient_visits = np.where(recurrent, 0., occupation_offset)
    if transient_visits.min() < -1e-8:
        raise ArithmeticError('Negative transient occupation')
    transient_visits = np.maximum(transient_visits, 0.)
    lower = float(occupation_offset @ g)
    joint = obs.T @ (transient_visits[:, None]*future)
    marginal = joint.sum(axis=1)
    conditional = np.divide(joint, marginal[:, None], out=np.zeros_like(joint),
                            where=marginal[:, None] > 0)
    upper = (float(marginal @ entropy_rows(conditional))
             +float(occupation_offset[recurrent] @ g[recurrent]))
    upper = min(upper, float(analysis['offset'][root]))
    if lower > upper+1e-7:
        raise ArithmeticError('Projected offset bounds inverted')
    return {'lower_bits': lower, 'upper_bits': upper,
            'rate_per_step': float(analysis['rate_per_step'][root]),
            'method': 'resolved recurrent tail / hidden-state lower and averaged-live upper'}


def history_bounds(kernel, labels, root, steps):
    p = np.asarray(kernel, dtype=float)
    if (p.ndim != 2 or p.shape[0] != p.shape[1] or len(labels) != len(p)
            or not np.isfinite(p).all() or p.min() < -1e-12
            or np.max(abs(p.sum(axis=1)-1)) > 1e-10):
        raise ValueError("Valid sampled kernel and one observation per state required")
    if type(steps) is not int or steps < 0 or type(root) is not int or not 0 <= root < len(p):
        raise ValueError("Integer root and nonnegative integer steps required")
    obs = observation_map(labels)
    future = p @ obs
    fine_condition = entropy_rows(future)
    distribution = np.zeros(len(p))
    distribution[root] = 1.
    lower = upper = 0.
    for _ in range(steps):
        lower += float(distribution @ fine_condition)
        joint = obs.T @ (distribution[:, None]*future)
        marginal = joint.sum(axis=1)
        conditional = np.divide(joint, marginal[:, None], out=np.zeros_like(joint),
                                where=marginal[:, None] > 0)
        upper += float(marginal @ entropy_rows(conditional))
        distribution = distribution @ p
    if lower > upper+1e-9:
        raise ArithmeticError("Conditioning bounds inverted")
    return {"lower_bits": lower, "upper_bits": upper,
            "method": "full-hidden-state lower / last-observation upper",
            "projected_process_assumed_markov": False}


def exact_prefix_entropy(kernel, labels, root, steps, max_prefixes=100000):
    """Exact short-prefix HMM enumeration for validation; fail rather than prune."""
    p = np.asarray(kernel, dtype=float)
    obs = observation_map(labels)
    if type(steps) is not int or steps < 0 or max_prefixes < 1:
        raise ValueError("Nonnegative integer prefix length and positive budget required")
    branches = [np.eye(len(p))[root]]
    for _ in range(steps):
        next_branches = []
        for weights in branches:
            predicted = weights @ p
            for column in obs.T:
                candidate = predicted*column
                if candidate.sum() > 0:
                    if len(next_branches) >= max_prefixes:
                        raise MemoryError("Exact prefix budget; no probability pruning")
                    next_branches.append(candidate)
        branches = next_branches
    masses = np.array([x.sum() for x in branches])
    if abs(masses.sum()-1) > 1e-9:
        raise ArithmeticError("Prefix probability mass failed")
    return float(entropy_rows(masses))


def interval_comparison(a, b, tolerance):
    """Overlapping bounds are unresolved, never a compression tie."""
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Nonnegative finite tolerance required")
    for bounds in (a, b):
        if (not np.isfinite([bounds['lower_bits'], bounds['upper_bits']]).all()
                or bounds['lower_bits'] > bounds['upper_bits']):
            raise ValueError("Finite ordered entropy bounds required")
    low = a["lower_bits"]-b["upper_bits"]
    high = a["upper_bits"]-b["lower_bits"]
    if low > tolerance:
        verdict = "strict_positive"
    elif high < -tolerance:
        verdict = "strict_negative"
    elif low >= -tolerance and high <= tolerance:
        verdict = "compression_within_tolerance"
    else:
        verdict = "unresolved"
    return {"difference_lower": low, "difference_upper": high, "verdict": verdict}
