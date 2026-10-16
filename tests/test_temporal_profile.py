import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.stats import poisson

from omega_v2.testbed.analysis.temporal_profile import (
    coefficients,
    count_entropy_bounds,
    crossover,
    expansion,
    fixed_jump_bits,
)


def test_one_jump_fine_expansion_matches_exact_finite_history():
    rate, horizon = 2., 3.
    q = csr_matrix([[-rate, rate], [0., 0.]])
    coordinate = coefficients(q, 0, horizon)
    expected = 1-np.exp(-rate*horizon)
    assert coordinate['expected_jumps'] == pytest.approx(expected)
    assert coordinate['finite_term_bits'] == pytest.approx(expected*(np.log2(np.e)-np.log2(rate)))
    errors = []
    for count in (300, 3000, 30000):
        cadence = horizon/count
        survival = np.exp(-rate*cadence)
        bit = -(survival*np.log2(survival)+(1-survival)*np.log2(1-survival))
        exact = expected*bit/(1-survival)
        errors.append(abs(exact-expansion(coordinate, cadence)))
    assert errors[2] < errors[1] < errors[0]
    assert fixed_jump_bits(q, 0, (1, 8)) == {'1': 0., '8': 0.}


def test_reference_time_covariance_preserves_profile_and_crossover():
    a = csr_matrix([[-2., 2.], [1., -1.]])
    b = csr_matrix([[-1., 1.], [1., -1.]])
    old_a, old_b = coefficients(a, 0, 3., 1.), coefficients(b, 0, 3., 1.)
    new_a, new_b = coefficients(a, 0, 3., 7.), coefficients(b, 0, 3., 7.)
    assert new_a['finite_term_bits'] == pytest.approx(old_a['finite_term_bits']-old_a['expected_jumps']*np.log2(7))
    assert expansion(old_a, .01) == pytest.approx(expansion(new_a, .01))
    assert crossover(old_a, old_b)['estimated_cadence'] == pytest.approx(crossover(new_a, new_b)['estimated_cadence'])


def test_count_query_has_correct_poisson_entropy_without_treating_clock_as_physics():
    q = csr_matrix([[-2., 2.], [2., -2.]])
    bounds = count_entropy_bounds(q, 0, 3.)
    exact = float(poisson.entropy(6.)/np.log(2))
    assert bounds['lower_bits']-1e-9 <= exact <= bounds['upper_bits']+1e-9
    assert bounds['poisson_tail_bound'] <= 1e-10
    assert bounds['upper_bits']-bounds['lower_bits'] < 1e-7
    assert bounds['query_not_added_to_physical_entropy']
    with pytest.raises(MemoryError):
        count_entropy_bounds(q, 0, 3., max_augmented_states=1)


def test_absorbed_process_count_entropy_is_bernoulli_not_padded_jumps():
    q = csr_matrix([[-2., 2.], [0., 0.]])
    bounds = count_entropy_bounds(q, 0, 1.)
    probability = np.exp(-2)
    exact = -(probability*np.log2(probability)+(1-probability)*np.log2(1-probability))
    assert bounds['lower_bits'] == pytest.approx(exact)
    zero = count_entropy_bounds(csr_matrix([[0.]]), 0, 1.)
    assert zero['lower_bits'] == zero['upper_bits'] == 0.
