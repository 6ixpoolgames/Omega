from itertools import pairwise

import numpy as np
import pytest

from omega_v2.finite.extent_probe_models import (
    deterministic_builder,
    independent_flips,
    reconvergent,
)
from omega_v2.finite.rooted_path_signature import retained_coordinates, signature
from omega_v2.finite.rooted_signature_moments import rooted_signature_moments


def _identity_features(state):
    return np.asarray(state, dtype=float)


def test_fair_bit_from_exact_root_has_native_first_and_second_moments():
    device = independent_flips(1, 0.5, 'fair')
    profile = rooted_signature_moments(device, (0,), _identity_features, horizon=1, degree=1)

    assert profile['words'] == ((1,),)
    assert profile['mean'] == pytest.approx([0.5])
    np.testing.assert_allclose(profile['second_moment'], [[0.5]])
    np.testing.assert_allclose(profile['covariance'], [[0.25]])
    assert profile['endpoints'] == pytest.approx({(0,): 0.5, (1,): 0.5})
    assert profile['mass'] == pytest.approx(1.0)


def test_deterministic_parallel_and_chain_have_zero_covariance_but_different_order():
    parallel = rooted_signature_moments(
        deterministic_builder('parallel'), (0, 0, 0), _identity_features, 3, degree=2
    )
    chain = rooted_signature_moments(
        deterministic_builder('chain'), (0, 0, 0), _identity_features, 3, degree=2
    )

    np.testing.assert_allclose(parallel['covariance'], 0, atol=1e-14)
    np.testing.assert_allclose(chain['covariance'], 0, atol=1e-14)
    assert parallel['mean'] != pytest.approx(chain['mean'])
    assert parallel['endpoints'] == pytest.approx({(1, 1, 1): 1.0})
    assert chain['endpoints'] == pytest.approx({(1, 1, 1): 1.0})


def test_terminal_wait_leaves_all_retained_moments_unchanged():
    device = reconvergent()
    at_completion = rooted_signature_moments(device, (0,), _identity_features, 2, degree=3)
    after_wait = rooted_signature_moments(device, (0,), _identity_features, 3, degree=3)

    assert at_completion['words'] == after_wait['words']
    np.testing.assert_allclose(after_wait['mean'], at_completion['mean'], atol=1e-14)
    np.testing.assert_allclose(after_wait['second_moment'], at_completion['second_moment'], atol=1e-14)
    np.testing.assert_allclose(after_wait['covariance'], at_completion['covariance'], atol=1e-14)


def test_two_tick_profile_matches_explicit_native_path_enumeration():
    device = independent_flips(1, 0.5, 'fair')
    profile = rooted_signature_moments(device, (0,), _identity_features, 2, degree=3)
    signatures = []
    probabilities = []
    for first in (0, 1):
        for second in (0, 1):
            states = (0, first, second)
            increments = []
            for source, target in pairwise(states):
                increments.extend(([1.0, 0.0], [0.0, float(target - source)]))
            values, words = retained_coordinates(signature(np.asarray(increments), 3), 1)
            assert words == profile['words']
            signatures.append(values)
            probabilities.append(0.25)
    signatures = np.asarray(signatures)
    expected_mean = np.einsum('i,ij->j', probabilities, signatures)
    expected_second = np.einsum('i,ij,ik->jk', probabilities, signatures, signatures)

    np.testing.assert_allclose(profile['mean'], expected_mean, atol=1e-14)
    np.testing.assert_allclose(profile['second_moment'], expected_second, atol=1e-14)


def test_invalid_root_is_rejected():
    device = independent_flips(1, 0.5, 'fair')
    with pytest.raises(ValueError, match='root'):
        rooted_signature_moments(device, (2,), _identity_features, 1)


@pytest.mark.parametrize('kwargs', [
    {'horizon': -1},
    {'horizon': 1, 'dt': 0},
    {'horizon': 1, 'degree': 0},
])
def test_invalid_profile_parameters_are_rejected(kwargs):
    device = independent_flips(1, 0.5, 'fair')
    options = {'horizon': 1}
    options.update(kwargs)
    with pytest.raises(ValueError):
        rooted_signature_moments(device, (0,), _identity_features, **options)
