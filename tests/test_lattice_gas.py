from collections import defaultdict

import pytest

from omega_v2.finite.lattice_gas import (
    VELOCITIES,
    conserved,
    decode,
    encode,
    local_collision,
    successors,
)


def _mask(*directions: int) -> int:
    return sum(1 << direction for direction in directions)


def _shift(state: int, side: int, dx: int, dy: int) -> int:
    return encode(
        (((x + dx) % side, (y + dy) % side, direction)
         for x, y, direction in decode(state, side)),
        side,
    )


def test_local_collision_conserves_and_is_doubly_stochastic():
    incoming_probability = defaultdict(float)

    for state in range(64):
        before = (
            state.bit_count(),
            sum(VELOCITIES[d][0] for d in range(6) if state & (1 << d)),
            sum(VELOCITIES[d][1] for d in range(6) if state & (1 << d)),
        )
        outcomes = local_collision(state)
        assert sum(probability for _, probability in outcomes) == pytest.approx(1)

        for output, probability in outcomes:
            after = (
                output.bit_count(),
                sum(VELOCITIES[d][0] for d in range(6) if output & (1 << d)),
                sum(VELOCITIES[d][1] for d in range(6) if output & (1 << d)),
            )
            assert after == before
            incoming_probability[output] += probability

    assert set(incoming_probability) == set(range(64))
    assert all(probability == pytest.approx(1) for probability in incoming_probability.values())


def test_head_on_pair_has_two_equally_likely_alternative_pairs():
    outcomes = dict(local_collision(_mask(0, 3)))
    assert outcomes == pytest.approx({_mask(1, 4): 0.5, _mask(2, 5): 0.5})


def test_alternating_triple_flips_deterministically():
    assert local_collision(_mask(0, 2, 4)) == ((_mask(1, 3, 5), 1.0),)
    assert local_collision(_mask(1, 3, 5)) == ((_mask(0, 2, 4), 1.0),)


def test_single_particle_streams_one_lattice_step():
    side = 5
    state = encode([(1, 2, 4)], side)
    vx, vy = VELOCITIES[4]
    expected = encode([((1 + vx) % side, (2 + vy) % side, 4)], side)
    assert successors(state, side) == {expected: 1.0}


def test_global_successors_conserve_and_preserve_probability_mass():
    side = 5
    state = encode([(0, 0, 0), (0, 0, 3), (2, 2, 1), (2, 2, 4)], side)
    outcomes = successors(state, side)

    assert sum(outcomes.values()) == pytest.approx(1)
    assert all(conserved(output, side) == conserved(state, side) for output in outcomes)


def test_successors_are_translation_equivariant():
    side = 3
    state = encode([(0, 0, 0), (0, 0, 3), (1, 2, 2), (2, 1, 5)], side)
    dx, dy = 1, 2

    shifted = successors(_shift(state, side, dx, dy), side)
    expected = {
        _shift(output, side, dx, dy): probability
        for output, probability in successors(state, side).items()
    }
    assert shifted == pytest.approx(expected)


def test_two_independent_head_on_pairs_branch_into_four_equal_outcomes():
    side = 5
    state = encode([(0, 0, 0), (0, 0, 3), (2, 2, 1), (2, 2, 4)], side)

    outcomes = successors(state, side)
    assert len(outcomes) == 4
    assert all(probability == pytest.approx(0.25) for probability in outcomes.values())
