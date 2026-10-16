import numpy as np
import pytest

from omega_v2.finite.path_covering import (
    cover_milp,
    cover_profile,
    jump_distance,
    markov_histories,
    project_law,
    sampled_distance,
)


def test_union_cover_counts_overlap_once_and_milp_agrees():
    paths = np.asarray([[0, 0], [0, 1], [1, 0], [1, 1]])
    weights = np.full(4, .25)
    distance = sampled_distance(paths, [.5, .5])
    exact = cover_profile(distance, weights, .5, [.75, 1])
    assert [r['upper'] for r in exact] == [1, 2]
    for alpha, row in zip((.75, 1), exact, strict=True):
        milp = cover_milp(distance, weights, .5, alpha)
        assert milp['optimal'] and milp['upper'] == row['upper']


def test_full_mass_cover_keeps_tiny_positive_branches():
    result = cover_profile(np.asarray([[0, 1], [1, 0]]), np.asarray([1-1e-14, 1e-14]),
                           0, [1])[0]
    assert result['upper'] == 2
    with pytest.raises(ValueError):
        cover_profile(np.asarray([[0]]), np.asarray([.9]), 0, [.9])


def test_projection_preserves_mass_and_global_relabeling_preserves_geometry():
    paths = np.asarray([[0, 0], [0, 1], [2, 2], [2, 3]])
    weights = np.asarray([.3, .2, .3, .2])
    projected, mass = project_law(paths, weights, [0, 1, 0, 1])
    assert projected.tolist() == [[0, 0], [0, 1]]
    assert np.allclose(mass, [.6, .4])
    assert np.array_equal(sampled_distance(paths, [.5, .5]),
                          sampled_distance(10+7*paths, [.5, .5]))


def test_reconvergence_prefix_remains_in_absolute_distance():
    a = ([0, .25, .75], [0, 1, 3])
    b = ([0, .25, .75], [0, 2, 3])
    assert jump_distance(a, b, 1) == jump_distance(a, b, 4) == .5
    subdivided = ([0, .1, .25, .5, .75], [0, 0, 1, 1, 3])
    assert jump_distance(a, subdivided, 4) == 0


def test_joint_law_not_reconstructed_from_one_time_marginals():
    slow_paths, slow_p = markov_histories([.5, .5], np.eye(2), 4)
    fast_paths, fast_p = markov_histories([.5, .5], np.full((2, 2), .5), 4)
    for paths, p in ((slow_paths, slow_p), (fast_paths, fast_p)):
        assert np.allclose(p @ paths, .5)
    slow = cover_profile(sampled_distance(slow_paths, [.25]*4), slow_p, .25, [.9])[0]
    fast = cover_profile(sampled_distance(fast_paths, [.25]*4), fast_p, .25, [.9])[0]
    assert slow['upper'] == 2 < fast['upper'] == 4
