"""Full-history entropy without allocating a dense full-state kernel.

The physical generator is unchanged. Exponentials are evaluated in row blocks;
stationary and Poisson queries use sparse iterative operators. Subject bounds
are hidden-Markov conditioning bounds, not substitute coarse generators.
"""
import numpy as np
from scipy.sparse import eye
from scipy.sparse.linalg import LinearOperator, expm_multiply, gmres, spilu

from .finite_classes import _closed_classes, _generator
from .observed_history import entropy_rows


def entropy_stream(Q, cadence, block_rows=32):
    n = Q.shape[0]
    g = np.empty(n)
    mass = negative = 0.
    for lo in range(0, n, block_rows):
        hi = min(n, lo+block_rows)
        start = np.zeros((n, hi-lo))
        start[np.arange(lo, hi), np.arange(hi-lo)] = 1.
        block = expm_multiply(Q.T*cadence, start).T
        mass = max(mass, float(max(abs(block.sum(axis=1)-1))))
        negative = min(negative, float(block.min()))
        if mass > 1e-10 or negative < -1e-12:
            raise ArithmeticError('Streamed probability residual')
        block[block < 0] = 0
        block /= block.sum(axis=1, keepdims=True)
        g[lo:hi] = entropy_rows(block)
    return g, {'kernel_mass': mass, 'negative_probability': abs(negative),
               'full_kernel_stored': False, 'block_rows': block_rows}


def entropy_stream_cadences(Q, cadences, block_rows=128):
    """Reuse each block's evolution across clocks; no intermediate kernel saved."""
    clocks = sorted(set(cadences))
    if not clocks or min(clocks) <= 0:
        raise ValueError('Positive clocks required')
    n = Q.shape[0]
    rows = {t: np.empty(n) for t in clocks}
    mass = negative = 0.
    for lo in range(0, n, block_rows):
        hi = min(n, lo+block_rows)
        block = np.zeros((n, hi-lo))
        block[np.arange(lo, hi), np.arange(hi-lo)] = 1.
        previous = 0.
        for clock in clocks:
            block = expm_multiply(Q.T*(clock-previous), block)
            mass = max(mass, float(max(abs(block.sum(axis=0)-1))))
            negative = min(negative, float(block.min()))
            if mass > 1e-10 or negative < -1e-12:
                raise ArithmeticError('Multi-clock streamed probability residual')
            block[block < 0] = 0
            block /= block.sum(axis=0, keepdims=True)
            rows[clock][lo:hi] = entropy_rows(block.T)
            previous = clock
    diagnostics = {'kernel_mass': mass, 'negative_probability': abs(negative),
                   'full_kernel_stored': False, 'block_rows': block_rows,
                   'cadences_evolved_together': clocks}
    return {t: (g, diagnostics.copy()) for t, g in rows.items()}


class StreamedQueries:
    def __init__(self, Q, allow_transients=False):
        self.q = _generator(Q)
        n = self.n = Q.shape[0]
        classes, _ = _closed_classes(self.q)
        if len(classes) != 1 or (len(classes[0]) != n and not allow_transients):
            raise ValueError('Streamed backend currently requires an irreducible law')
        self.seed = np.full(n, 1/n)
        self.transpose_factor = spilu((-self.q.T+.02*eye(n)).tocsc(),
                                      drop_tol=1e-5, fill_factor=12)
        self.row_factor = spilu((-self.q+.02*eye(n)).tocsc(),
                                drop_tol=1e-5, fill_factor=12)
        self.stationary_operator = LinearOperator((n, n),
            matvec=lambda v: -self.q.T @ v+self.seed*v.sum())
        pi, info = gmres(self.stationary_operator, self.seed,
                         M=LinearOperator((n, n), matvec=self.transpose_factor.solve),
                         rtol=1e-12, atol=1e-13, restart=50, maxiter=200)
        pi /= pi.sum()
        residual = max(abs(self.q.T @ pi))
        if info or pi.min() < -1e-10 or residual > 1e-9:
            raise ArithmeticError(f'Streamed stationarity failed: {info}, {residual}')
        self.pi = np.maximum(pi, 0)
        self.pi /= self.pi.sum()
        self.stationary_residual = float(residual)

    def continuous_occupation(self, root, horizon):
        start = np.eye(1, self.n, root).ravel()
        end = expm_multiply(self.q.T*horizon, start)
        correction, info = gmres(self.stationary_operator, start-end,
            M=LinearOperator((self.n, self.n), matvec=self.transpose_factor.solve),
            rtol=1e-11, atol=1e-12, restart=50, maxiter=200)
        correction -= correction.sum()*self.pi
        total = horizon*self.pi+correction
        residual = float(max(abs(self.q.T @ total-end+start)))
        if info or total.min() < -1e-7 or residual > 1e-7 or abs(total.sum()-horizon) > 1e-7:
            raise ArithmeticError('Streamed physical occupation failed')
        return end, total, residual

    def sampled(self, cadence, block_rows=32, entropy_payload=None):
        g, diagnostics = (entropy_stream(self.q, cadence, block_rows)
                          if entropy_payload is None else entropy_payload)
        h = float(self.pi @ g)
        action = lambda v: v-expm_multiply(self.q*cadence, v)+np.full(self.n, self.pi @ v)
        precondition = lambda v: self.row_factor.solve(v/cadence)+np.full(self.n, self.pi @ v)
        offset, info = gmres(LinearOperator((self.n, self.n), matvec=action), g-h,
            M=LinearOperator((self.n, self.n), matvec=precondition),
            rtol=1e-11, atol=1e-12, restart=40, maxiter=150)
        offset -= self.pi @ offset
        residual = float(max(abs(action(offset)-g+h)))
        if info or residual > 1e-7:
            raise ArithmeticError(f'Streamed sampled Poisson failed: {info}, {residual}')
        return {'g': g, 'offset': offset, 'rate': h/cadence, 'cadence': cadence,
                'poisson_residual': residual, 'diagnostics': diagnostics}

    def finite(self, sampled, horizon):
        if abs(horizon/sampled['cadence']-round(horizon/sampled['cadence'])) > 1e-9:
            raise ValueError('Integral sampled horizon required')
        b = sampled['offset']
        return horizon*sampled['rate']+b-expm_multiply(self.q*horizon, b)

    def sampled_occupation(self, root, horizon, cadence):
        start = np.eye(1, self.n, root).ravel()
        end = expm_multiply(self.q.T*horizon, start)
        action = lambda v: v-expm_multiply(self.q.T*cadence, v)+self.pi*v.sum()
        precondition = lambda v: self.transpose_factor.solve(v/cadence)
        correction, info = gmres(LinearOperator((self.n, self.n), matvec=action), start-end,
            M=LinearOperator((self.n, self.n), matvec=precondition),
            rtol=1e-11, atol=1e-12, restart=40, maxiter=150)
        total = (horizon/cadence)*self.pi+correction
        residual = float(max(abs(action(correction)-start+end)))
        if info or total.min() < -1e-7 or residual > 1e-8 or abs(total.sum()-horizon/cadence) > 1e-6:
            raise ArithmeticError('Streamed sampled occupation failed')
        return total, residual


def projection_future(Q, states, fields, cadence):
    labels = [tuple(s[i] for i in fields) for s in states]
    index = {x: i for i, x in enumerate(dict.fromkeys(labels))}
    groups = np.array([index[x] for x in labels])
    obs = np.zeros((len(states), len(index)))
    obs[np.arange(len(states)), groups] = 1
    future = expm_multiply(Q*cadence, obs)
    if future.min() < -1e-12 or max(abs(future.sum(axis=1)-1)) > 1e-10:
        raise ArithmeticError('Streamed projected probability residual')
    future[future < 0] = 0
    future /= future.sum(axis=1, keepdims=True)
    return groups, future, entropy_rows(future)
