"""Native-weight trajectory covers. No fitted state distance or physical policy search."""

from itertools import pairwise, product
from math import ceil

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, eye, hstack, vstack


def project_law(paths, weights, mapping):
    """Push a full finite history law through one common physical observation map."""
    result = {}
    for path, weight in zip(paths, weights, strict=True):
        key = tuple(mapping[int(s)] for s in path)
        result[key] = result.get(key, 0.0) + float(weight)
    keys = sorted(result)
    return np.asarray(keys, dtype=int), np.asarray([result[k] for k in keys])


def markov_histories(initial, kernel, observations):
    """Exact finite sampled-time law, not an enumeration of continuous jump histories."""
    rows = []
    weights = []
    for path in product(range(len(initial)), repeat=observations):
        weight = initial[path[0]]
        for a, b in pairwise(path):
            weight *= kernel[a, b]
        if weight > 0:  # Exact structural zeros only; no probability threshold.
            rows.append(path)
            weights.append(weight)
    return np.asarray(rows, dtype=int), np.asarray(weights, dtype=float)


def sampled_distance(paths, durations):
    """Integral for the declared piecewise-held observations, in physical time units."""
    paths = np.asarray(paths)
    durations = np.asarray(durations, dtype=float)
    return np.einsum('ijk,k->ij', paths[:, None, :] != paths[None, :, :], durations)


def _validate(distance, weights, alpha):
    distance = np.asarray(distance, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if distance.ndim != 2 or distance.shape[0] != len(weights):
        raise ValueError('One target row per probability is required')
    if np.any(weights <= 0) or not np.isclose(weights.sum(), 1, atol=1e-12, rtol=0):
        raise ValueError('Retain the normalized native law, including failed/rare paths')
    if not 0 < alpha <= 1:
        raise ValueError('alpha must be in (0,1]')
    return distance, weights


def _greedy(incidence, weights, alpha):
    covered = np.zeros(len(weights), dtype=bool)
    selected = []
    while float(weights[covered].sum()) < alpha - 1e-12:
        gains = (weights * ~covered) @ incidence
        index = int(gains.argmax())
        if gains[index] <= 0:
            raise ValueError('Admissible centers cannot cover requested probability')
        selected.append(index)
        covered |= incidence[:, index]
    return selected


def cover_milp(distance, weights, epsilon, alpha, seconds=8.0):
    """Certified finite-problem optimum or explicitly bounded incumbent, not population N."""
    distance, weights = _validate(distance, weights, alpha)
    incidence = distance <= epsilon + 1e-12
    n, m = incidence.shape
    a = csr_matrix(incidence.astype(float))
    if alpha == 1:
        # Tiny positive masses still require coverage. Never rely on mass tolerance here.
        objective = np.ones(m)
        integrality = np.ones(m)
        constraints = LinearConstraint(a, np.ones(n), np.full(n, np.inf))
    else:
        objective = np.r_[np.ones(m), np.zeros(n)]
        integrality = np.r_[np.ones(m), np.zeros(n)]
        matrix = vstack((hstack((-a, eye(n))),
                         csr_matrix(np.r_[np.zeros(m), weights][None, :])))
        constraints = LinearConstraint(matrix, np.r_[np.full(n, -np.inf), alpha],
                                       np.r_[np.zeros(n), np.inf])
    result = milp(objective, integrality=integrality,
                  bounds=Bounds(np.zeros(len(objective)), np.ones(len(objective))),
                  constraints=constraints,
                  options={'time_limit': seconds, 'mip_rel_gap': 0.0})
    selected = None if result.x is None else list(np.flatnonzero(result.x[:m] > .5))
    if selected is None or weights[incidence[:, selected].any(axis=1)].sum() < alpha-1e-9:
        selected = _greedy(incidence, weights, alpha)
    mass = float(weights[incidence[:, selected].any(axis=1)].sum())
    dual = getattr(result, 'mip_dual_bound', None)
    lower = ceil(float(dual)-1e-7) if dual is not None and np.isfinite(dual) else 1
    upper = len(selected)
    return {'lower': lower, 'upper': upper, 'optimal': lower == upper,
            'mass': mass, 'centers': [int(i) for i in selected],
            'method': 'milp', 'status': int(result.status)}


def cover_profile(distance, weights, epsilon, alphas, brute_limit=18):
    """Solve all probability depths for a fixed ball geometry; save actual witnesses."""
    distance, weights = _validate(distance, weights, alphas[0])
    incidence = distance <= epsilon + 1e-12
    masks = []
    representatives = []
    for j in range(incidence.shape[1]):
        mask = sum(1 << int(i) for i in np.flatnonzero(incidence[:, j]))
        if mask not in masks:
            masks.append(mask)
            representatives.append(j)
    if len(masks) == len(weights) and all(mask.bit_count() == 1 for mask in masks):
        order = np.argsort(-weights, kind='stable')
        cumulative = np.cumsum(weights[order])
        output = []
        for alpha in alphas:
            k = len(weights) if alpha == 1 else int(np.searchsorted(cumulative, alpha-1e-12))+1
            targets = {int(i) for i in order[:k]}
            centers = [representatives[j] for j, mask in enumerate(masks)
                       if mask.bit_length()-1 in targets]
            output.append({'lower': k, 'upper': k, 'optimal': True,
                           'mass': float(cumulative[k-1]), 'centers': centers,
                           'method': 'disjoint_balls', 'status': 0})
        return output
    if len(masks) > brute_limit:
        return [cover_milp(distance, weights, epsilon, alpha) for alpha in alphas]
    # Enumerate codebooks, not samples from the law. Union mass retains all overlaps.
    m = len(masks)
    unions = [0] * (1 << m)
    mass_cache = {0: 0.0}
    best = [(-1.0, 0)] * (m+1)
    best[0] = (0.0, 0)
    all_targets = (1 << len(weights))-1
    full_min = m+1
    full_witness = 0
    for subset in range(1, 1 << m):
        bit = subset & -subset
        union = unions[subset ^ bit] | masks[bit.bit_length()-1]
        unions[subset] = union
        if union not in mass_cache:
            indices = [i for i in range(len(weights)) if (union >> i) & 1]
            mass_cache[union] = float(weights[indices].sum())
        mass = mass_cache[union]
        k = subset.bit_count()
        if mass > best[k][0]:
            best[k] = (mass, subset)
        if union == all_targets and k < full_min:
            full_min, full_witness = k, subset
    output = []
    for alpha in alphas:
        if alpha == 1:
            k, subset = full_min, full_witness
            mass = float(weights.sum())
        else:
            k = next(k for k, (mass, _) in enumerate(best) if mass >= alpha-1e-12)
            mass, subset = best[k]
        centers = [representatives[j] for j in range(m) if (subset >> j) & 1]
        output.append({'lower': k, 'upper': k, 'optimal': True, 'mass': mass,
                       'centers': centers, 'method': 'exhaustive_codebooks', 'status': 0})
    return output


def sample_telegraph(rate, horizon, count, seed, stationary=True):
    """Actual CTMC jump times; each path is (change times, right-continuous states)."""
    rng = np.random.default_rng(seed)
    result = []
    for _ in range(count):
        state = int(rng.integers(2)) if stationary else 0
        times, states = [0.0], [state]
        time = 0.0
        while rate > 0:
            time += float(rng.exponential(1/rate))
            if time >= horizon:
                break
            state ^= 1
            times.append(time)
            states.append(state)
        result.append((times, states))
    return result


def jump_distance(a, b, horizon):
    """Exact integrated mismatch on two supplied piecewise-constant physical paths."""
    at, av = a
    bt, bv = b
    i = j = 0
    time = total = 0.0
    while time < horizon:
        an = at[i+1] if i+1 < len(at) else horizon
        bn = bt[j+1] if j+1 < len(bt) else horizon
        end = min(an, bn, horizon)
        total += (end-time) * (av[i] != bv[j])
        if an == end and i+1 < len(at):
            i += 1
        if bn == end and j+1 < len(bt):
            j += 1
        time = end
    return float(total)


def jump_distances(paths, centers, horizon):
    return np.asarray([[jump_distance(a, b, horizon) for b in centers] for a in paths])


def wilson(successes, trials, z=1.959963984540054):
    p = successes/trials
    divisor = 1+z*z/trials
    midpoint = (p+z*z/(2*trials))/divisor
    radius = z*np.sqrt(p*(1-p)/trials+z*z/(4*trials*trials))/divisor
    return [float(midpoint-radius), float(midpoint+radius)]
