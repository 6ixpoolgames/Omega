import numpy as np
import pytest
from scipy.linalg import expm
from scipy.sparse import csr_matrix
from omega_v2.testbed.analysis.uniformized_entropy import entropy_cadences
from omega_v2.testbed.analysis.observed_history import entropy_rows


@pytest.mark.parametrize('speed', [.01, 1, 100])
@pytest.mark.parametrize('threads', [1, 3])
def test_complete_state_entropy_agrees_with_dense_exponential(speed, threads):
    rng = np.random.default_rng(15)
    q = rng.uniform(0, 1, (11,11))*speed
    np.fill_diagonal(q,0)
    np.fill_diagonal(q,-q.sum(axis=1))
    result=entropy_cadences(csr_matrix(q), [.125,.25,.5], block_rows=3, threads=threads)
    for time,(actual,diagnostics) in result.items():
        expected=entropy_rows(expm(q*time))
        assert max(abs(actual-expected)) < diagnostics['row_entropy_error_bits']+1e-11
        assert diagnostics['poisson_tail'] <= 1e-15
        assert diagnostics['kernel_mass'] < 1e-11


def test_tail_allowance_covers_deliberately_looser_numerical_approximation():
    q=csr_matrix([[-1,1,0],[0,-1,1],[1,0,-1]])
    result=entropy_cadences(q,[.5],tail_budget=1e-7)
    actual,diag=result[.5]
    expected=entropy_rows(expm(q.toarray()*.5))
    assert max(abs(actual-expected)) <= diag['row_entropy_error_bits']+1e-13


def test_terminal_and_reducible_states_are_preserved():
    q=csr_matrix([[-1,1,0],[0,0,0],[0,0,0]])
    actual,diag=entropy_cadences(q,[.25])[.25]
    assert actual[1:] == pytest.approx([0,0],abs=1e-14)
    assert actual == pytest.approx(entropy_rows(expm(q.toarray()*.25)),abs=1e-13)
    assert diag['uniformization_clock_is_query_only']


def test_checkpoint_resume_verifies_bytes_and_invalidates_for_changed_law(tmp_path):
    q=csr_matrix([[-1,1,0],[0,-1,1],[1,0,-1]])
    first=entropy_cadences(q,[.125,.25],block_rows=1,cache_dir=tmp_path,threads=2)
    again=entropy_cadences(q,[.125,.25],block_rows=1,cache_dir=tmp_path)
    assert again[.25][1]['cached_blocks']==3
    assert again[.25][0] == pytest.approx(first[.25][0],abs=1e-14)
    bad=next(tmp_path.rglob('*.npz'))
    bad.write_bytes(b'partial write')
    repaired=entropy_cadences(q,[.125,.25],block_rows=1,cache_dir=tmp_path)
    assert repaired[.25][1]['cached_blocks']==2
    assert repaired[.25][0] == pytest.approx(first[.25][0],abs=1e-14)
    changed=entropy_cadences(q*2,[.125,.25],block_rows=1,cache_dir=tmp_path)
    assert changed[.25][1]['cached_blocks']==0
    assert changed[.25][0] == pytest.approx(entropy_rows(expm(q.toarray()*.5)),abs=1e-13)
