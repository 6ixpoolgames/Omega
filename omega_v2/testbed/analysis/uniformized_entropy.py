"""Certified Poisson-series approximation of complete sampled-state entropy.

Uniformization is a numerical query, not a physical clock or added event label.
No physical states are removed. The omitted Poisson tail bounds total variation
of every normalized row, hence its Shannon-entropy error by continuity.
"""
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.sparse import eye
from scipy.linalg.blas import daxpy
from scipy.stats import poisson
from .finite_classes import _generator
from .observed_history import entropy_rows


def entropy_cadences(Q, cadences, block_rows=128, tail_budget=1e-15, threads=1,
                     cache_dir=None, progress=lambda x: None):
    q = _generator(Q)
    clocks = sorted(set(cadences))
    if not clocks or min(clocks) <= 0 or not 0 < tail_budget < 1e-6:
        raise ValueError('Positive clocks and a small positive tail budget required')
    if type(block_rows) is not int or block_rows <= 0:
        raise ValueError('Positive row block size required')
    if type(threads) is not int or not 1 <= threads <= 8:
        raise ValueError('One to eight bounded block threads supported')
    n = q.shape[0]
    rate = float(max(-q.diagonal()))
    if rate == 0:
        return {t: (np.zeros(n), {'row_entropy_error_bits': 0., 'poisson_tail': 0.,
                                'full_kernel_stored': False}) for t in clocks}
    R = (eye(n)+q/rate).tocsr()
    R.eliminate_zeros()
    if min(R.data, default=0.) < -1e-14:
        raise ArithmeticError('Uniformization matrix is not stochastic')
    transition = R.T.tocsr()
    degree = int(poisson.isf(tail_budget, rate*max(clocks)))
    if degree < 0:
        raise ArithmeticError('Invalid Poisson degree')
    while poisson.sf(degree, rate*max(clocks)) > tail_budget:
        degree += 1
    weights = {t: poisson.pmf(np.arange(degree+1), rate*t) for t in clocks}
    tails = {t: float(poisson.sf(degree, rate*t)) for t in clocks}
    rows = {t: np.empty(n) for t in clocks}
    cache=None
    if cache_dir is not None:
        from .entropy_checkpoints import EntropyBlocks
        cache=EntropyBlocks(cache_dir,q,clocks,tail_budget,version='poisson-csr-fused-2')
    def one(lo):
        hi = min(n, lo+block_rows)
        saved=cache.load(lo,hi) if cache else None
        if saved is not None:
            values,residual=saved
            return lo,hi,{t:values[i] for i,t in enumerate(clocks)},residual,True
        powers = np.zeros((n, hi-lo))
        powers[np.arange(lo, hi), np.arange(hi-lo)] = 1.
        sums = {t: powers*weights[t][0] for t in clocks}
        for k in range(1, degree+1):
            powers = transition @ powers
            for t in clocks:
                # Fused addition avoids a full probability-block temporary.
                sums[t] = daxpy(powers.reshape(-1),sums[t].reshape(-1),
                                a=weights[t][k]).reshape(powers.shape)
        block_rows_result = {}
        mass_residual = 0.
        for t, matrix in sums.items():
            totals = matrix.sum(axis=0)
            residual = float(max(abs(totals-(1-tails[t]))))
            mass_residual = max(mass_residual, residual)
            if residual > 1e-11 or matrix.min() < -1e-13:
                raise ArithmeticError('Poisson-series probability residual')
            matrix[matrix < 0] = 0.
            matrix /= matrix.sum(axis=0, keepdims=True)
            block_rows_result[t] = entropy_rows(matrix.T)
        if cache:
            cache.save(lo,hi,np.stack([block_rows_result[t] for t in clocks]),mass_residual)
        return lo, hi, block_rows_result, mass_residual,False
    mass_residual = 0.
    cached=0
    with ThreadPoolExecutor(max_workers=threads) as pool:
        for lo, hi, values, residual, reused in pool.map(one, range(0,n,block_rows)):
            for t in clocks:
                rows[t][lo:hi] = values[t]
            mass_residual = max(mass_residual,residual)
            cached+=int(reused)
            if hi==n or lo//block_rows%16==0:
                progress(f'entropy rows {hi}/{n}; cached blocks {cached}')
    result = {}
    for t in clocks:
        # Analytic truncation error only. Floating arithmetic residual is
        # reported independently, as with the other exponential backend.
        delta = tails[t]
        binary = (-delta*np.log2(delta)-(1-delta)*np.log1p(-delta)/np.log(2)) if delta > 0 else 0.
        allowance = binary+delta*np.log2(max(1, n-1))
        result[t] = (rows[t], {'poisson_degree': degree, 'poisson_tail': delta,
            'row_entropy_error_bits': float(allowance), 'kernel_mass': mass_residual,
            'full_kernel_stored': False, 'block_rows': block_rows,
            'block_threads': threads,
            'cached_blocks': cached, 'checkpoint_query_key': cache.key if cache else None,
            'uniformization_clock_is_query_only': True})
    return result
