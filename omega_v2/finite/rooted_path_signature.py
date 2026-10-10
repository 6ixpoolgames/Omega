"""Truncated Chen signatures for clocked, piecewise-linear path lifts.

This module is geometric instrumentation only. It assigns no path weights and
does not define an extent or a canonical metric.
"""

import math

import numpy as np


def _validate_levels(levels):
    if not levels:
        raise ValueError('At least the level-zero scalar is required')
    arrays = tuple(np.asarray(level, dtype=float) for level in levels)
    if arrays[0].shape != () or arrays[0] != 1:
        raise ValueError('Level zero must be the scalar one')
    if any(not np.all(np.isfinite(level)) for level in arrays):
        raise ValueError('Signature levels must be finite')
    if len(arrays) > 1:
        if arrays[1].ndim != 1 or arrays[1].size == 0:
            raise ValueError('Level one must be a nonempty coordinate vector')
        dim = arrays[1].size
        if any(level.shape != (dim**degree,)
               for degree, level in enumerate(arrays[1:], start=1)):
            raise ValueError('Signature levels must have consistent tensor dimensions')
    return arrays


def signature(increments: np.ndarray, degree: int) -> tuple[np.ndarray, ...]:
    """Return levels 0..degree of the piecewise-linear path signature.

    Tensor entries use lexicographic word order, equivalent to C-order
    flattening of each ``(dimension,) * level`` tensor.
    """
    increments = np.asarray(increments, dtype=float)
    if increments.ndim != 2 or increments.shape[1] == 0:
        raise ValueError('increments must be a 2D array with at least one coordinate')
    if not np.all(np.isfinite(increments)):
        raise ValueError('increments must be finite')
    if not isinstance(degree, (int, np.integer)) or isinstance(degree, (bool, np.bool_)):
        raise TypeError('degree must be an integer from 1 through 4')
    if not 1 <= degree <= 4:
        raise ValueError('degree must be from 1 through 4')

    dim = increments.shape[1]
    result = [np.asarray(1.0)] + [np.zeros(dim**level) for level in range(1, degree+1)]
    for increment in increments:
        updated = [np.asarray(1.0)]
        for level in range(1, degree+1):
            value = result[level].copy()
            for left_degree in range(level):
                right_degree = level-left_degree
                left = result[left_degree]
                # exp(increment) contributes increment^tensor(right_degree)/right_degree!.
                tensor_power = increment
                for _ in range(1, right_degree):
                    tensor_power = np.kron(tensor_power, increment)
                right = tensor_power / math.factorial(right_degree)
                value += np.kron(left, right)
            updated.append(value)
        result = updated
    return tuple(result)


def concatenate(left, right) -> tuple[np.ndarray, ...]:
    """Chen-concatenate two signatures of the same degree and dimension."""
    left, right = _validate_levels(left), _validate_levels(right)
    if len(left) != len(right):
        raise ValueError('Signatures must have the same degree')
    if len(left) > 1 and left[1].size != right[1].size:
        raise ValueError('Signatures must have the same coordinate dimension')
    result = [np.asarray(1.0)]
    for level in range(1, len(left)):
        value = np.zeros_like(left[level])
        for left_degree in range(level+1):
            value += np.kron(left[left_degree], right[level-left_degree])
        result.append(value)
    return tuple(result)


def retained_coordinates(levels, physical_dim: int):
    """Select words ending in a physical coordinate; coordinate 0 is time.

    Returns values and their words, each level in increasing order and each
    tensor in lexicographic word order. Mixed time/physical words are retained.
    """
    levels = _validate_levels(levels)
    if not isinstance(physical_dim, (int, np.integer)) or isinstance(
            physical_dim, (bool, np.bool_)) or physical_dim < 1:
        raise ValueError('physical_dim must be a positive integer')
    if len(levels) > 1 and levels[1].size != physical_dim+1:
        raise ValueError('physical_dim must match signature dimension minus time')
    values, words = [], []
    for degree, level in enumerate(levels[1:], start=1):
        for flat_index, value in enumerate(level):
            word = tuple(np.unravel_index(flat_index, (physical_dim+1,) * degree))
            if word[-1] > 0:
                values.append(float(value))
                words.append(word)
    return np.asarray(values, dtype=float), tuple(words)


def timed_state_increments(states: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Lift sampled states using separate time-advance and state-change steps.

    For each adjacent pair, append ``(dt, 0...)`` then ``(0, delta_state)``.
    This preserves clock timing without interpolating across a state jump.
    """
    states = np.asarray(states, dtype=float)
    times = np.asarray(times, dtype=float)
    if states.ndim != 2 or states.shape[0] == 0 or states.shape[1] == 0:
        raise ValueError('states must be a nonempty 2D array')
    if times.ndim != 1 or times.size != states.shape[0]:
        raise ValueError('times must have one value per state cut')
    if not np.all(np.isfinite(states)) or not np.all(np.isfinite(times)):
        raise ValueError('states and times must be finite')
    intervals = np.diff(times)
    if np.any(intervals < 0):
        raise ValueError('times must be nondecreasing')
    output = np.zeros((2*intervals.size, states.shape[1]+1), dtype=float)
    output[0::2, 0] = intervals
    output[1::2, 1:] = np.diff(states, axis=0)
    return output
