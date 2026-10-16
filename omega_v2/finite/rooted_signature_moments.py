"""Exact rooted-law moments of truncated, time-augmented path signatures.

This is an exploratory profile over a finite native Markov device. It assigns
no scalar extent and does not average over cuts or initial conditions.
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import product
from math import isclose

import numpy as np
from scipy.sparse import csr_matrix

from .extent_probe_models import Device
from .rooted_path_signature import signature


def _validated_device(device: Device, root: tuple[int, ...], feature_map: Callable):
    states = tuple(device.states)
    state_set = set(states)
    if root not in state_set:
        raise ValueError('root must be a state in the device')
    if set(device.rows) != state_set:
        raise ValueError('device must provide exactly one transition row per state')

    features = {}
    physical_dim = None
    for state in states:
        value = np.asarray(feature_map(state), dtype=float)
        if value.ndim != 1 or value.size == 0 or not np.all(np.isfinite(value)):
            raise ValueError('feature_map must return a nonempty finite 1D vector')
        if physical_dim is None:
            physical_dim = value.size
        elif value.size != physical_dim:
            raise ValueError('feature_map must return the same dimension for every state')
        features[state] = value

    for state, outcomes in device.rows.items():
        if not outcomes:
            raise ValueError('every native transition row must be nonempty')
        probabilities = []
        for outcome in outcomes:
            probability = float(outcome.probability)
            if not np.isfinite(probability) or probability <= 0:
                raise ValueError('native outcome probabilities must be finite and positive')
            if outcome.target not in state_set:
                raise ValueError('every native transition target must be a device state')
            probabilities.append(probability)
        if not isclose(sum(probabilities), 1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f'native transition probabilities from {state!r} must sum to one')

    return features, physical_dim


def _word_basis(coordinate_dim: int, degree: int):
    words = [()]
    for level in range(1, degree + 1):
        words.extend(product(range(coordinate_dim), repeat=level))
    return tuple(words), {word: i for i, word in enumerate(words)}


def _linear_signature_update(segment_levels, words, word_index):
    """Sparse Chen multiplication by a fixed segment signature."""
    segment = np.concatenate([np.asarray(level).reshape(-1) for level in segment_levels])
    rows, columns, data = [], [], []
    for row, word in enumerate(words):
        for split in range(len(word) + 1):
            prefix, suffix = word[:split], word[split:]
            coefficient = float(segment[word_index[suffix]])
            if coefficient != 0.0:
                rows.append(row)
                columns.append(word_index[prefix])
                data.append(coefficient)
    return csr_matrix((data, (rows, columns)), shape=(len(words), len(words)))


def rooted_signature_moments(
    device: Device,
    root: tuple[int, ...],
    feature_map: Callable[[tuple[int, ...]], np.ndarray],
    horizon: int,
    degree: int = 3,
    dt: float = 1.0,
) -> dict:
    """Compute exact signature first and second moments from an exact root.

    At each native tick the lift first advances time by ``dt`` and then applies
    the target-minus-source physical feature increment. Probability mass and
    unnormalized moments are propagated by the device's native transition rows.
    """
    if not isinstance(horizon, (int, np.integer)) or isinstance(horizon, (bool, np.bool_)):
        raise TypeError('horizon must be an integer')
    if horizon < 0:
        raise ValueError('horizon must be a nonnegative integer')
    if not isinstance(degree, (int, np.integer)) or isinstance(degree, (bool, np.bool_)):
        raise TypeError('degree must be an integer')
    if not 1 <= degree <= 4:
        raise ValueError('degree must be an integer from 1 through 4')
    dt = float(dt)
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError('dt must be finite and positive')

    features, physical_dim = _validated_device(device, root, feature_map)
    coordinate_dim = physical_dim + 1  # coordinate zero is time
    words, word_index = _word_basis(coordinate_dim, int(degree))
    full_dimension = len(words)
    retained_words = tuple(word for word in words if word and word[-1] > 0)
    retained_indices = np.fromiter((word_index[word] for word in retained_words), dtype=int)

    zero = np.zeros(full_dimension)
    initial_signature = zero.copy()
    initial_signature[0] = 1.0
    mass = {state: 0.0 for state in device.states}
    first = {state: np.zeros(full_dimension) for state in device.states}
    second = {state: np.zeros((full_dimension, full_dimension)) for state in device.states}
    mass[root] = 1.0
    first[root] = initial_signature.copy()
    second[root][0, 0] = 1.0

    update_cache = {}
    for _ in range(int(horizon)):
        next_mass = {state: 0.0 for state in device.states}
        next_first = {state: np.zeros(full_dimension) for state in device.states}
        next_second = {
            state: np.zeros((full_dimension, full_dimension)) for state in device.states
        }
        for state in device.states:
            if mass[state] == 0.0:
                continue
            for outcome in device.rows[state]:
                target = outcome.target
                increment = features[target] - features[state]
                key = tuple(float(value) for value in increment)
                transform = update_cache.get(key)
                if transform is None:
                    path_increments = np.zeros((2, coordinate_dim))
                    path_increments[0, 0] = dt
                    path_increments[1, 1:] = increment
                    segment_levels = signature(path_increments, int(degree))
                    transform = _linear_signature_update(segment_levels, words, word_index)
                    update_cache[key] = transform

                probability = float(outcome.probability)
                next_mass[target] += probability * mass[state]
                transformed_first = transform @ first[state]
                next_first[target] += probability * transformed_first
                transformed_second_left = transform @ second[state]
                transformed_second = (transform @ transformed_second_left.T).T
                next_second[target] += probability * transformed_second
        mass, first, second = next_mass, next_first, next_second

    total_mass = sum(mass.values())
    if not isclose(total_mass, 1.0, rel_tol=1e-10, abs_tol=1e-10):
        raise ArithmeticError('native probability propagation did not preserve unit mass')

    full_mean = sum(first.values(), start=np.zeros(full_dimension))
    full_second = sum(
        second.values(), start=np.zeros((full_dimension, full_dimension))
    )
    mean = full_mean[retained_indices].copy()
    second_moment = full_second[np.ix_(retained_indices, retained_indices)].copy()
    covariance = second_moment - np.outer(mean, mean)
    endpoint_law = {state: probability for state, probability in mass.items() if probability > 0.0}

    return {
        'words': retained_words,
        'mean': mean,
        'second_moment': second_moment,
        'covariance': covariance,
        'endpoints': endpoint_law,
        'mass': total_mass,
    }
