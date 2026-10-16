import numpy as np
import pytest

from omega_v2.testbed.analysis.observed_history import (
    averaged_observation_bounds,
    sampled_occupations,
)
from omega_v2.testbed.analysis.renewal_profile import (
    SampledHorizons,
    coordinate_shares,
    hidden_bounds,
    hidden_prepared,
    horizon_estimate,
    reachable_world,
)
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.renewal import build_world


def test_sparse_observation_sums_recover_independent_bit_entropies():
    p, q = .2, .7
    probabilities = np.array([(1-p)*(1-q), (1-p)*q, p*(1-q), p*q])
    kernel = np.tile(probabilities, (4, 1))
    states = [(0, 0), (0, 1), (1, 0), (1, 1)]
    shares = coordinate_shares(kernel, states, (0, 1))
    hp = -p*np.log2(p)-(1-p)*np.log2(1-p)
    hq = -q*np.log2(q)-(1-q)*np.log2(1-q)
    assert shares == pytest.approx(np.tile([[hp], [hq]], (1, 4)))
    query = SampledHorizons(kernel, 2048)
    for count in (13, 2048):
        weights, final = query.occupation(0, count)
        assert final == pytest.approx(probabilities)
        assert weights @ shares.sum(axis=0) == pytest.approx(count*(hp+hq))
        a, b = sampled_occupations(kernel, 0, [count])[count]
        assert weights == pytest.approx(a)
        assert final == pytest.approx(b)
    labels = [s[0] for s in states]
    fast = hidden_bounds(hidden_prepared(kernel, labels), weights)
    slow = averaged_observation_bounds(kernel, labels, weights)
    assert fast['lower_bits'] == pytest.approx(slow['lower_bits'])
    assert fast['upper_bits'] == pytest.approx(slow['upper_bits'])


def test_reachable_restriction_excludes_only_unreachable_hazard_location():
    world = compile_world(build_world())
    roots = [(8, 1, 0, 1, 1, 0, 1), (8, 1, 0, 1, 0, 1, 1)]
    reachable = reachable_world(world, roots)
    assert reachable['full_state_count'] == 864
    assert len(reachable['states']) == 576
    assert all(state[1] in (1, 2) for state in reachable['states'])
    assert np.max(abs(np.asarray(reachable['Q'].sum(axis=1)).ravel())) < 1e-12
    assert horizon_estimate(2.-1., -10.-5.)['estimate'] == 15.
    assert horizon_estimate(0., 1.)['estimate'] is None
