"""Blocked sampled kernel and sparse class/Poisson queries, including sinks.

No ergodic shortcut: closed classes determine a harmonic rate vector. A single
anchor per recurrent class fixes Poisson gauge; transient rows remain intact.
Full finite-history entropy is T*r + b - exp(Q*T)b at integral sampled horizons.
"""
import numpy as np
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import LinearOperator, expm_multiply, gmres, splu

from .blocked_entropy import sampled_kernel
from .finite_classes import _closed_classes, _generator


class ClassQueries:
    def __init__(self, Q):
        self.q = _generator(Q)
        self.n = self.q.shape[0]
        self.classes, _ = _closed_classes(self.q)
        self.transient = np.setdiff1d(np.arange(self.n), np.concatenate(self.classes))
        self.stationary = []
        for members in self.classes:
            qc = self.q[members][:, members]
            if len(members) == 1:
                pi = np.ones(1)
            else:
                # A normalization equation avoids dividing by the probability
                # of an arbitrarily chosen, potentially extremely rare state.
                matrix = qc.T.tolil()
                matrix.rows[-1] = list(range(len(members)))
                matrix.data[-1] = [1.]*len(members)
                rhs = np.zeros(len(members)); rhs[-1] = 1.
                pi = splu(matrix.tocsc()).solve(rhs)
            if min(pi) < -1e-10 or max(abs(np.asarray(pi @ qc).ravel())) > 1e-8:
                raise ArithmeticError('Recurrent stationary solve failed')
            self.stationary.append(np.maximum(pi, 0.)/np.maximum(pi, 0.).sum())
        # Residual at a deleted equation is amplified by 1/pi(anchor). Anchor
        # the most probable state, rather than a rare arbitrary last state.
        self.anchors = np.array([c[int(np.argmax(pi))] for c, pi in
                                 zip(self.classes, self.stationary)], dtype=int)
        self.transient_lu = (splu(self.q[self.transient][:, self.transient].tocsc())
                             if len(self.transient) else None)
        pinned = (-self.q).tolil()
        for anchor in self.anchors:
            pinned.rows[anchor] = [int(anchor)]
            pinned.data[anchor] = [1.]
        self.preconditioner = splu(pinned.tocsc())

    def sampled(self, cadence, max_kernel_bytes=160*1024**2):
        P, g, diagnostics = sampled_kernel(self.q, cadence, max_kernel_bytes=max_kernel_bytes)
        solution = self.reward_solution({'P': P, 'cadence': cadence}, g)
        return {**solution, 'P': P, 'g': g, 'cadence': cadence,
                'kernel_diagnostics': diagnostics}

    def reward_solution(self, sampled, g):
        """Exact additive sampled reward using the same class-aware equation."""
        P, cadence = sampled['P'], sampled['cadence']
        g = np.asarray(g, dtype=float)
        rate = np.zeros(self.n)
        class_rates = []
        for members, pi in zip(self.classes, self.stationary):
            r = float(pi @ g[members])/cadence
            class_rates.append(r); rate[members] = r
        if len(self.transient):
            rate[self.transient] = self.transient_lu.solve(-np.asarray(self.q[self.transient] @ rate).ravel())
        rhs = g-cadence*rate
        rhs[self.anchors] = 0.

        def action(v):
            value = v-P @ v
            value[self.anchors] = v[self.anchors]
            return value

        def precondition(v):
            scaled = v/cadence
            scaled[self.anchors] = v[self.anchors]
            return self.preconditioner.solve(scaled)

        iterations = []
        offset, info = gmres(LinearOperator((self.n, self.n), matvec=action), rhs,
                            M=LinearOperator((self.n, self.n), matvec=precondition),
                            rtol=1e-11, atol=1e-12, maxiter=150, restart=30,
                            callback=iterations.append, callback_type='pr_norm')
        poisson = offset-P @ offset-g+cadence*rate
        residual = float(max(abs(poisson)))
        harmonic = float(max(abs(self.q @ rate)))
        if info != 0 or residual > 1e-7 or harmonic > 1e-8:
            raise ArithmeticError(f'Class Poisson solve failed: info={info}, residual={residual}')
        return {'rate': rate, 'offset_gauge': offset, 'cadence': cadence,
                'class_rates': class_rates, 'poisson_residual': residual,
                'harmonic_rate_residual': harmonic, 'iterations': len(iterations)}

    def finite(self, sampled, horizon):
        steps = horizon/sampled['cadence']
        if not np.isfinite(horizon) or horizon < 0 or abs(steps-round(steps)) > 1e-9:
            raise ValueError('Nonnegative integral sampled horizon required')
        b = sampled['offset_gauge']
        return horizon*sampled['rate']+b-expm_multiply(self.q*horizon, b)

    def limiting_offset(self, sampled):
        # Pinned gauge is not mean-zero. Remove its harmonic class extension.
        b = sampled['offset_gauge']
        harmonic = np.zeros(self.n)
        for members, pi in zip(self.classes, self.stationary):
            harmonic[members] = pi @ b[members]
        if len(self.transient):
            harmonic[self.transient] = self.transient_lu.solve(-np.asarray(self.q[self.transient] @ harmonic).ravel())
        return b-harmonic


def pulse_kernel(compiled, mode='one_B'):
    """External prescribed pulse; no random clock or query flag in physics."""
    if mode not in ('one_B', 'all_B'):
        raise ValueError('Unknown pulse')
    targets, released = [], []
    energy = compiled['world'].metadata['parameters']['apparatus_energy']
    for state in compiled['states']:
        n = min(1, state[3]) if mode == 'one_B' else state[3]
        t = list(state); t[3] -= n
        targets.append(compiled['index'][tuple(t)]); released.append(n*energy)
    n = len(targets)
    return csr_matrix((np.ones(n), (np.arange(n), targets)), shape=(n, n)), np.array(released)


def reward_integral(Q, initial, reward, horizon):
    """Expected integral of any state reward, without adding it to entropy."""
    from scipy.sparse import bmat
    n = len(initial)
    matrix = bmat([[Q.T, csr_matrix((n, 1))],
                   [csr_matrix(np.asarray(reward).reshape(1, n)), csr_matrix((1, 1))]], format='csr')
    endpoint = expm_multiply(matrix*horizon, np.r_[initial, 0.])
    return endpoint[:-1], float(endpoint[-1])


def occupation_distribution(Q, initial, horizon):
    """Full expected occupation for an arbitrary normalized root distribution."""
    from scipy.sparse import bmat
    n = Q.shape[0]
    v = np.asarray(initial, dtype=float)
    if (v.shape != (n,) or not np.all(np.isfinite(v)) or min(v) < 0
            or abs(v.sum()-1.) > 1e-10 or not np.isfinite(horizon) or horizon < 0):
        raise ValueError('Normalized finite initial distribution and horizon required')
    augmented = bmat([[Q.T, csr_matrix((n, n))], [eye(n), csr_matrix((n, n))]], format='csr')
    result = expm_multiply(augmented*horizon, np.r_[v, np.zeros(n)])
    if abs(result[:n].sum()-1.) > 1e-9 or abs(result[n:].sum()-horizon) > 1e-8:
        raise ArithmeticError('Occupation conservation failed')
    return result[:n], result[n:]
