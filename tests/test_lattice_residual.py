from math import exp, factorial

import numpy as np
from scipy.sparse import csr_matrix

from omega_v2.finite.lattice_chemistry import Parameters
from omega_v2.finite.lattice_residual import (
    counted_generator,
    exact_square,
    jump_distribution,
    preparations,
    propagate_with_events,
    support_profiles,
    two_forward_bindings,
)


def test_native_square_is_reversible_and_matched_preparations_have_equal_energy():
    square = exact_square(Parameters(side=2, particles=4, capacity=2, catalytic_barrier=2))
    q, pi = square["q"], square["equilibrium"]
    assert len(pi) == 768
    assert np.max(np.abs(np.asarray(q.sum(axis=1)))) < 1e-12
    flux = q.multiply(pi[:, None])
    assert np.max(np.abs((flux-flux.T).data)) < 1e-12
    p = preparations(square)
    assert p["adjacent_two"] @ square["energy"] == p["opposite_two"] @ square["energy"]


def test_jump_law_retains_poisson_tail_without_renormalizing():
    q = csr_matrix([[-2., 2.], [2., -2.]])
    initial = np.array([[1.], [0.]])
    layers, tail = jump_distribution(counted_generator(q, 4), initial, .7, 4)
    expected = np.array([exp(-1.4) * 1.4**n / factorial(n) for n in range(5)])
    assert np.allclose(layers.sum(axis=1).ravel(), expected)
    assert np.isclose(tail[0], 1 - expected.sum())
    p, jumps = propagate_with_events(q, initial, .7)
    assert np.isclose(p.sum(), 1) and np.isclose(jumps[0], 1.4)


def test_parallel_channel_count_does_not_change_unique_state_support():
    unique = csr_matrix(np.array([[0, 1], [1, 0]], dtype=np.int64))
    profiles = support_profiles(unique, 2 * unique, 5)
    assert np.array_equal(profiles["states_within_depth"][:, 0], [1, 2, 2, 2, 2, 2])
    assert np.array_equal(profiles["state_sequences_exact_depth"][:, 0], np.ones(6))
    assert np.array_equal(profiles["channel_sequences_exact_depth"][:, 0], 2**np.arange(6))


def test_two_bindings_respect_shared_fuel_and_native_clock():
    small = exact_square(Parameters(side=2, particles=4, capacity=1, catalytic_barrier=2))
    assert np.allclose(two_forward_bindings(small, 1), 0)
    large = exact_square(Parameters(side=2, particles=4, capacity=4, catalytic_barrier=2))
    p = preparations(large)
    law = two_forward_bindings(large, 1)
    assert np.all(law >= 0) and np.all(law <= 1)
    assert p["adjacent_two"] @ law > 0
    assert np.allclose(two_forward_bindings(large, 0), 0)
