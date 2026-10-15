import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix

from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits
from omega_v2.testbed.analysis.same_law_profile import IrreducibleQueries


def test_all_root_poisson_scores_offsets_and_occupations_match_dense():
    q = csr_matrix([[-1.2, 1., .2], [.4, -.7, .3], [.1, .8, -.9]])
    query = IrreducibleQueries(q)
    dense = analyze(q, .25)
    result = query.sampled(.25, [1, 4])
    assert np.max(abs(query.pi-dense['stationary'][0])) < 1e-12
    assert np.max(abs(result['offset']-dense['offset'])) < 1e-8
    for t in (1, 4):
        assert np.max(abs(result['vectors'][str(t)]-finite_history_bits(dense['P'], t*4))) < 1e-8
        initial = np.array([.3, .7, 0.])
        final = initial @ expm(q.toarray()*t)
        occupation, residual = query.occupation(initial, final, t)
        assert residual < 1e-12
        assert abs(occupation.sum()-t) < 1e-12


def test_exact_identity_for_unequal_rates_and_long_horizons():
    q = csr_matrix([[-.01, .01], [5., -5.]])
    query = IrreducibleQueries(q)
    result = query.sampled(.125, [16, 256])
    dense = analyze(q, .125)
    for t in (16, 256):
        assert np.max(abs(result['vectors'][str(t)]-finite_history_bits(dense['P'], t*8))) < 1e-7
