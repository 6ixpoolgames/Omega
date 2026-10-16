import numpy as np
import pytest

from omega_v2.testbed.analysis.finite_classes import finite_history_bits
from omega_v2.testbed.analysis.observed_history import (
    averaged_observation_bounds,
    exact_prefix_entropy,
    history_bounds,
    projected_offset_bounds,
    sampled_occupations,
)
from omega_v2.testbed.experiments.signal_kills import (
    compare_intervals,
    limiting_order,
    local_verdict,
    qualify,
)


def test_binary_occupations_preserve_complete_history_not_stationary_approximation():
    p = np.array([[.8, .2], [0., 1.]])
    occupations = sampled_occupations(p, 0, [0, 1, 3, 10000])
    row_bits = finite_history_bits(p, 1)
    for count in (0, 1, 3, 10000):
        weights, endpoint = occupations[count]
        assert weights.sum() == pytest.approx(count)
        assert endpoint[0] == pytest.approx(.8**count)
        assert weights[0] == pytest.approx((1-.8**count)/.2)
    assert occupations[3][0] @ row_bits == pytest.approx(finite_history_bits(p, 3)[0])


def test_time_averaged_hidden_bounds_enclose_exact_nonmarkov_prefix():
    p = np.array([[.7, .2, .1], [.1, .4, .5], [.3, .2, .5]])
    labels = [0, 0, 1]
    weights, _ = sampled_occupations(p, 0, [4])[4]
    fast = averaged_observation_bounds(p, labels, weights)
    direct = history_bounds(p, labels, 0, 4)
    exact = exact_prefix_entropy(p, labels, 0, 4)
    assert fast['lower_bits'] == pytest.approx(direct['lower_bits'])
    assert fast['lower_bits'] <= exact+1e-12 <= fast['upper_bits']+1e-12
    assert fast['upper_bits'] <= finite_history_bits(p, 4)[0]+1e-12
    full = averaged_observation_bounds(p, [0, 1, 2], weights)
    assert full['lower_bits'] == pytest.approx(full['upper_bits'])


def test_qualification_rejects_self_label_and_directionless_information():
    registration = {'tracking': {'mi_threshold_bits': .001, 'direction_tolerance': 1e-6},
                    'disposition_threshold': .05, 'minimum_signal_time': .05,
                    'minimum_signal_fraction': .001, 'minimum_obstructed_index': .01}
    stats = {'tracking_counterfactual_breadth_drop_mi_bits': .02,
             'counterfactual_drop_probability_by_signal': [.1, .5],
             'escape_disposition_shift': .2, 'signal_occupancy_time': .5,
             'signal_fraction_of_live_time': .1,
             'operational_obstructed_suffering_index': .1}
    q = qualify(stats, registration)
    assert q['tracking'] and q['disposition'] and q['obstructed']
    q = qualify({**stats, 'counterfactual_drop_probability_by_signal': [.5, .1]}, registration)
    assert not q['tracking'] and not q['nontracking']
    assert not qualify({**stats, 'signal_occupancy_time': 0.}, registration)['disposition']


def test_uninstantiated_or_unresolved_comparisons_cannot_be_kills():
    worse = {'lower_bits': 10., 'upper_bits': 12.}
    better = [{'lower_bits': 8., 'upper_bits': 13.}, {'lower_bits': 7., 'upper_bits': 9.}]
    result = compare_intervals(worse, better, 1e-5)
    assert local_verdict(result, True) == 'unresolved'
    strict = compare_intervals(worse, [{'lower_bits': 1., 'upper_bits': 2.}], 1e-5)
    assert local_verdict(strict, False) == 'not_instantiated'
    assert local_verdict(strict, True) == 'adapter_relative_ranking_counterexample'


def test_common_limiting_rate_does_not_make_finite_offset_a_tie():
    assert limiting_order((1., 5.), [(1., 2.)], 1e-9, 1e-5) == 'strict_positive'
    assert limiting_order((.5, 500.), [(1., 2.)], 1e-9, 1e-5) == 'strict_negative'


def test_projected_offset_bounds_enclose_a_known_geometric_lifetime():
    from scipy.sparse import csr_matrix

    from omega_v2.testbed.analysis.finite_classes import analyze
    # Same death hazard in two hidden living states: observed lifetime is geometric.
    q = csr_matrix([[-.5, .3, .2], [.4, -.6, .2], [0., 0., 0.]])
    result = analyze(q, .25)
    bounds = projected_offset_bounds(result, [1, 1, 0], 0)
    survival = np.exp(-.2*.25)
    bernoulli = -(survival*np.log2(survival)+(1-survival)*np.log2(1-survival))
    exact_lifetime_entropy = bernoulli/(1-survival)
    assert bounds['lower_bits'] <= exact_lifetime_entropy+1e-9 <= bounds['upper_bits']+1e-9
    assert bounds['rate_per_step'] == 0.
    with pytest.raises(ValueError, match='resolve'):
        projected_offset_bounds(result, [0, 0, 0], 0)
