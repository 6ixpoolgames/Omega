"""Exact all-root finite-history vectors without storing binary matrix powers.

For one irreducible Q, solve sampled Poisson b-Pb=g-h and use
ell_n=n*h+b-exp(Q*n*delta)b. Blocking and Krylov solves preserve all states;
residual gates are numerical safeguards, not pruning of physical paths.
"""
import numpy as np
from scipy.sparse.linalg import LinearOperator, expm_multiply, gmres, splu

from .blocked_entropy import sampled_kernel
from .finite_classes import _closed_classes, _generator


class IrreducibleQueries:
    def __init__(self, Q):
        self.q = _generator(Q)
        n = self.q.shape[0]
        classes, _ = _closed_classes(self.q)
        if len(classes) != 1 or len(classes[0]) != n:
            raise ValueError('This query backend requires an irreducible native law')
        self.factor = splu((-self.q[:-1, :-1]).tocsc())
        self.pi = np.r_[self.factor.solve(self.q[-1, :-1].toarray().ravel(), trans='T'), 1.]
        self.pi /= self.pi.sum()
        if self.pi.min() < -1e-10:
            raise ArithmeticError('Stationary distribution negative')
        self.stationary_residual = float(np.max(abs(self.pi @ self.q)))
        if self.stationary_residual > 1e-9:
            raise ArithmeticError('Stationary solve residual')

    def poisson(self, f):
        f = np.asarray(f)
        centered = f-self.pi @ f
        solution = np.r_[self.factor.solve(centered[:-1]), 0.]
        solution -= self.pi @ solution
        if np.max(abs(-self.q @ solution-centered)) > 1e-7:
            raise ArithmeticError('Continuous Poisson residual')
        return solution

    def occupation(self, initial, final, horizon):
        # wQ=mu(T)-mu(0), sum(w)=T; solve the zero-sum correction.
        difference = np.asarray(initial)-np.asarray(final)
        z = np.r_[self.factor.solve(difference[:-1], trans='T'), 0.]
        z -= z.sum()*self.pi
        w = horizon*self.pi+z
        residual = float(np.max(abs(w @ self.q-(final-initial))))
        if residual > 1e-7 or w.min() < -1e-7 or abs(w.sum()-horizon) > 1e-7:
            raise ArithmeticError('Exact occupation residual')
        return w, residual

    def sampled(self, delta, horizons, max_kernel_bytes=160*1024**2):
        p, g, residuals = sampled_kernel(self.q, delta, block_rows=32,
                                         max_kernel_bytes=max_kernel_bytes)
        h = float(self.pi @ g)
        n = len(g)
        operator = LinearOperator((n, n), matvec=lambda v, kernel=p: v-kernel @ v+np.full(n, self.pi @ v))
        preconditioner = LinearOperator((n, n),
            matvec=lambda v: self.poisson(v)/delta+np.full(n, self.pi @ v))
        rhs = g-h
        b, info = gmres(operator, rhs, M=preconditioner, x0=self.poisson(g)/delta,
                        rtol=1e-10, atol=1e-11, restart=40, maxiter=100)
        if info:
            raise ArithmeticError(f'Sampled Poisson solver failed: {info}')
        b -= self.pi @ b
        residuals['poisson'] = float(np.max(abs(b-p @ b-rhs)))
        residuals['stationarity'] = self.stationary_residual
        residuals['stationary_kernel'] = float(np.max(abs(self.pi @ p-self.pi)))
        residuals['poisson_normalization'] = float(abs(self.pi @ b))
        if max(residuals.values()) > 1e-7:
            raise ArithmeticError(f'Exact sampled query residuals: {residuals}')
        del p, operator, preconditioner
        vectors = {}
        for t in horizons:
            steps = round(t/delta)
            if abs(steps*delta-t) > 1e-10:
                raise ValueError('Physical horizon must be an integer sampling schedule')
            vectors[str(t)] = steps*h+b-expm_multiply(self.q*t, b)
        return {'vectors': vectors, 'offset': b, 'rate': h/delta, 'residuals': residuals}

    def activity(self):
        off = self.q.copy()
        off.setdiag(0.)
        off.eliminate_zeros()
        exits = -self.q.diagonal()
        log_rates = off.copy()
        log_rates.data *= np.log2(off.data)
        finite = exits*np.log2(np.e)-np.asarray(log_rates.sum(axis=1)).ravel()
        jump = off.multiply((1/exits)[:, None]).tocsr()
        log_marks = jump.copy()
        log_marks.data = -jump.data*np.log2(jump.data)
        mark = np.asarray(log_marks.sum(axis=1)).ravel()
        return exits, finite, jump, mark


def fixed_jump_vectors(jump, row_entropy, counts=(8, 32, 128)):
    total = np.zeros(len(row_entropy))
    vectors = {}
    for k in range(1, max(counts)+1):
        total = row_entropy+jump @ total
        if k in counts:
            vectors[str(k)] = total.copy()
    return vectors
