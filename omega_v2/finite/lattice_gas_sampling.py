"""Vectorized trajectory sampling for the FHP-I lattice gas."""

import numpy as np

from omega_v2.finite.lattice_gas import PAIRS, TRIPLES, VELOCITIES


def from_bitstates(states, side):
    """Convert global integer bitstates to a ``(batch, side, side)`` uint8 array."""
    if not isinstance(side, int) or isinstance(side, bool) or side < 1:
        raise ValueError("side must be a positive integer")
    values = list(states)
    limit = 1 << (6 * side * side)
    if any(not isinstance(state, int) or isinstance(state, bool) or not 0 <= state < limit
           for state in values):
        raise ValueError("states must be nonnegative in-range Python integers")
    result = np.zeros((len(values), side, side), dtype=np.uint8)
    for row, state in enumerate(values):
        for site in range(side * side):
            result[row, site // side, site % side] = (state >> (6 * site)) & 63
    return result


def to_bitstates(batch):
    """Convert a batch of local six-bit masks to Python integer bitstates."""
    values = np.asarray(batch)
    if (values.ndim != 3 or values.dtype != np.uint8 or values.shape[1] != values.shape[2]
            or values.shape[1] < 1 or np.any(values > 63)):
        raise ValueError("batch must contain six-bit masks with shape (batch, side, side)")
    result = []
    for trajectory in values:
        state = 0
        for site, mask in enumerate(trajectory.flat):
            state |= int(mask) << (6 * site)
        result.append(state)
    return result


def step_batch(states, rng):
    """Apply one independent collision-then-stream tick to each trajectory.

    Returns the next batch and each trajectory's pair-site count before collision.
    """
    states = np.asarray(states)
    if (states.ndim != 3 or states.dtype != np.uint8 or states.shape[1] != states.shape[2]
            or states.shape[1] < 3):
        raise ValueError("states must be uint8 with shape (batch, side, side), side >= 3")
    if np.any(states > 63):
        raise ValueError("local masks must be in the range 0..63")
    if not hasattr(rng, "integers"):
        raise ValueError("rng must provide integers(low, high, size)")
    before = states
    pair_counts = np.isin(before, PAIRS).sum(axis=(1, 2), dtype=np.int64)

    # Build two collision tables: ordinary states and the two possible outcomes
    # at stochastic pair sites. Triple reversal is deterministic.
    table = np.arange(64, dtype=np.uint8)
    table[TRIPLES[0]] = TRIPLES[1]
    table[TRIPLES[1]] = TRIPLES[0]
    collided = table[before]
    for pair in PAIRS:
        alternatives = [candidate for candidate in PAIRS if candidate != pair]
        choose = rng.integers(0, 2, size=before.shape)
        collided[before == pair] = np.asarray(alternatives, dtype=np.uint8)[choose[before == pair]]

    streamed = np.zeros_like(collided)
    for direction, (dx, dy) in enumerate(VELOCITIES):
        bit = np.uint8(1 << direction)
        particles = (collided & bit) != 0
        moved = np.roll(particles, shift=(dy, dx), axis=(1, 2))
        streamed |= moved.astype(np.uint8) << np.uint8(direction)
    return streamed, pair_counts
