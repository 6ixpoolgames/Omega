import numpy as np
import pytest

from omega_v2.finite.lattice_gas import PAIRS, TRIPLES, conserved, successors
from omega_v2.finite.lattice_gas_sampling import from_bitstates, step_batch, to_bitstates


class FixedRng:
    def __init__(self, choice):
        self.choice = choice

    def integers(self, low, high, size):
        assert (low, high) == (0, 2)
        return np.full(size, self.choice, dtype=np.int64)


def test_bitstate_roundtrip():
    states = [0, (1 << 0) | (1 << 17), (1 << 53) | (1 << 5)]
    assert to_bitstates(from_bitstates(states, 3)) == states


def test_pair_collision_choices_match_exact_successors():
    for pair in PAIRS:
        state = pair  # pair at origin
        batch = from_bitstates([state], 3)
        outcomes = set()
        for choice in (0, 1):
            next_batch, counts = step_batch(batch, FixedRng(choice))
            assert counts.tolist() == [1]
            outcomes.add(to_bitstates(next_batch)[0])
        assert outcomes == set(successors(state, 3))


def test_triple_reversal_and_conservation():
    state = TRIPLES[0] | (1 << (6 * 4 + 1))
    batch = from_bitstates([state], 4)
    after, counts = step_batch(batch, np.random.default_rng(4))
    assert counts.tolist() == [0]
    assert conserved(state, 4) == conserved(to_bitstates(after)[0], 4)


def test_sampled_pair_counts_match_stochastic_exact_propagation():
    root = sum(1 << (6 * (y * 3 + x) + d)
               for x, y, d in ((0, 0, 0), (0, 0, 3), (1, 0, 1), (1, 1, 4)))
    joint = {(root, 0): 1.0}
    for _ in range(4):
        updated = {}
        for (state, total), weight in joint.items():
            pairs = sum(((state >> (6 * site)) & 63) in PAIRS for site in range(9))
            for target, probability in successors(state, 3).items():
                key = (target, total + pairs)
                updated[key] = updated.get(key, 0.0) + weight * probability
        joint = updated
    distribution = {}
    for (_, total), probability in joint.items():
        distribution[total] = distribution.get(total, 0.0) + probability
    exact_mean = sum(total * probability for total, probability in distribution.items())
    exact_variance = sum((total - exact_mean) ** 2 * probability
                         for total, probability in distribution.items())
    assert exact_variance > 0

    samples = 4096
    batch = from_bitstates([root] * samples, 3)
    totals = np.zeros(samples, dtype=np.int64)
    rng = np.random.default_rng(20261007)
    for _ in range(4):
        batch, counts = step_batch(batch, rng)
        totals += counts
    standard_error = totals.std(ddof=1) / np.sqrt(samples)
    assert abs(totals.mean() - exact_mean) < 6 * standard_error


def test_streaming_moves_each_direction_with_periodic_wrap():
    side = 4
    for direction, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 1), (-1, 0),
                                           (0, -1), (1, -1))):
        state = 1 << (6 * (side - 1) + direction)
        after, _ = step_batch(from_bitstates([state], side), np.random.default_rng(0))
        expected_site = ((dy % side) * side + (side - 1 + dx) % side)
        assert to_bitstates(after) == [1 << (6 * expected_site + direction)]


@pytest.mark.parametrize("bad", [np.zeros((2, 3, 3), dtype=np.int64),
                                  np.zeros((2, 3, 4), dtype=np.uint8),
                                  np.zeros((2, 2, 2), dtype=np.uint8)])
def test_rejects_invalid_batches(bad):
    with pytest.raises(ValueError):
        step_batch(bad, np.random.default_rng(0))
