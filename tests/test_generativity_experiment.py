import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix

from omega_v2.testbed.analysis.class_queries import ClassQueries
from omega_v2.testbed.analysis.finite_classes import finite_history_bits
from omega_v2.testbed.analysis.generativity_experiment import (
    coordinate_rows,
    history_value,
    physical_profiles,
)
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.robust_generativity import GenerativityParameters, build_world, matched_roots


def test_piecewise_history_includes_the_pre_pulse_prefix():
    q = csr_matrix([[-2., 2.], [1., -1.]])
    queries = ClassQueries(q); sampled = queries.sampled(.25)
    mu = np.array([1., 0.]); kernel = np.array([[0., 1.], [0., 1.]])
    after = mu @ expm(q.toarray()) @ kernel
    value = history_value(queries, sampled, mu, 3., True, 1., after)
    direct = mu @ finite_history_bits(sampled['P'], 4)+after @ finite_history_bits(sampled['P'], 8)
    assert abs(value-direct) < 1e-10
    assert value > after @ finite_history_bits(sampled['P'], 8)


def test_coordinate_conditional_rewards_sum_to_full_history():
    q = csr_matrix([[-3., 1., 2., 0.], [2., -3., 0., 1.], [1., 0., -3., 2.], [0., 1., 2., -3.]])
    states = [(e, r, 0, 0, 0, 0) for e in range(2) for r in range(2)]
    queries = ClassQueries(q); sampled = queries.sampled(.25)
    rows = coordinate_rows(sampled['P'], states)
    assert np.allclose(rows.sum(axis=1), sampled['g'], atol=1e-12)
    contributions = np.zeros(4)
    for coordinate in range(6):
        solved = queries.reward_solution(sampled, rows[:, coordinate])
        contributions += queries.finite(solved, 4.)
    assert np.allclose(contributions, finite_history_bits(sampled['P'], 16), atol=1e-10)


def test_pulsed_physical_timeline_keeps_native_energy_and_root_averages():
    c = compile_world(build_world(GenerativityParameters(capacity=3)))
    roots = matched_roots(c)
    output = physical_profiles(c, roots, [16, 64, 256], pulse=True)
    for name in roots:
        row = output['rows'][name]['256']
        assert abs(row['ledger']['energy_balance_residual']) < 1e-8
        assert abs(row['ledger']['bank_balance_residual']) < 1e-8
        assert row['deadline']['expanded'] == 0.
        assert 0 <= output['rows'][name]['persistence']['post_startup_uptime_fraction'] <= 1
    assert np.allclose(output['endpoints'][64], expm(c['Q'].toarray().T*64) @
                       np.column_stack([roots[k] for k in output['names']]), atol=1e-11)
