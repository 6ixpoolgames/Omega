"""Exact residual alternatives in the closed, fully occupied 2x2 lattice class.

Uses LatticeChemistry.events/apply without modifying its generator. Positions
cannot move in this invariant class; chemical states, fuel and channels can.
"""

from math import comb, exp, expm1

import numpy as np
from scipy.sparse import bmat, coo_matrix, csr_matrix, diags, eye, kron
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.lattice_chemistry import LatticeChemistry, State

POSITIONS = [(0, 0), (1, 0), (0, 1), (1, 1)]
PAIRS = [(0, 1), (0, 2), (1, 3), (2, 3)]


def state_index(state, capacity):
    internal = sum(int(s) << i for i, s in enumerate(state.internal))
    bonds = sum(1 << i for i, pair in enumerate(PAIRS) if pair in state.bonds)
    return (16 * internal + bonds) * (capacity + 1) + state.fuel


def exact_square(parameters):
    if parameters.side != 2 or parameters.particles != 4:
        raise ValueError("This exact class has four particles on a 2x2 lattice")
    model = LatticeChemistry(parameters)
    states, channels = [], []
    for internal in range(16):
        for bonds in range(16):
            for fuel in range(parameters.capacity + 1):
                states.append(State(POSITIONS.copy(), [(internal >> i) & 1 for i in range(4)],
                                    {p for i, p in enumerate(PAIRS) if (bonds >> i) & 1}, fuel))
    rows, cols, rates, forward_pairs = [], [], [], []
    for i, state in enumerate(states):
        assert state_index(state, parameters.capacity) == i
        events = model.events(state)
        recorded, forward = [], []
        for event in events:
            if event.kind == "move":
                raise AssertionError("Occupied square should be an invariant positional class")
            after = state.copy()
            model.apply(after, event)
            j = state_index(after, parameters.capacity)
            rows.append(i)
            cols.append(j)
            rates.append(event.rate)
            recorded.append({"to": j, "rate": event.rate, "kind": event.kind,
                             "members": event.members, "catalyst": event.catalyst})
            if event.kind in ("fuel", "catalytic") and event.members not in state.bonds:
                forward.append((j, event.rate, event.members))
        channels.append(recorded)
        forward_pairs.append(forward)
    n = len(states)
    off = coo_matrix((rates, (rows, cols)), shape=(n, n)).tocsr()
    escape = np.asarray(off.sum(axis=1)).ravel()
    q = off - diags(escape)
    multiplicity = coo_matrix((np.ones(len(rows), dtype=np.int64), (rows, cols)),
                              shape=(n, n)).tocsr()
    unique = multiplicity.copy()
    unique.data[:] = 1
    energy = np.array([model.energy(s) for s in states])
    weight = np.array([comb(parameters.capacity, s.fuel) for s in states]) * np.exp(-energy)
    equilibrium = weight / weight.sum()
    return {"model": model, "states": states, "channels": channels, "off": off,
            "q": q.tocsr(), "escape": escape, "multiplicity": multiplicity,
            "unique": unique, "energy": energy, "equilibrium": equilibrium,
            "forward_pairs": forward_pairs}


def support_profiles(unique, multiplicity, depth=8):
    """State balls and exact integer sequence counts up to this jump depth.

    These sequences retain event order; no concurrency quotient is imposed.
    """
    n = unique.shape[0]
    balls = [1 << i for i in range(n)]
    state_counts = [np.ones(n, dtype=np.int64)]
    walks, marked = [np.ones(n, dtype=np.int64)], [np.ones(n, dtype=np.int64)]
    for _ in range(depth):
        next_balls = []
        for i in range(n):
            mask = balls[i]
            for j in unique.indices[unique.indptr[i]:unique.indptr[i + 1]]:
                mask |= balls[int(j)]
            next_balls.append(mask)
        balls = next_balls
        state_counts.append(np.array([b.bit_count() for b in balls], dtype=np.int64))
        walks.append(unique @ walks[-1])
        marked.append(multiplicity @ marked[-1])
        if min(walks[-1].min(), marked[-1].min()) < 0:
            raise OverflowError("Integer count overflow; use smaller depth or big integers")
    return {"states_within_depth": np.stack(state_counts),
            "state_sequences_exact_depth": np.stack(walks),
            "channel_sequences_exact_depth": np.stack(marked)}


def propagate_with_events(q, initial, horizon):
    """Native state law plus exact mean cumulative jump count, by exponential."""
    n = q.shape[0]
    generator = bmat([[q.T, csr_matrix((n, 1))],
                      [csr_matrix((-q.diagonal()).reshape(1, n)), csr_matrix((1, 1))]],
                     format="csr")
    augmented = np.vstack([initial, np.zeros((1, initial.shape[1]))])
    result = expm_multiply(generator * horizon, augmented,
                          traceA=float(q.diagonal().sum() * horizon))
    return result[:n], result[n]


def counted_generator(q, depth):
    """N=0..depth layers and an absorbing overflow, with native escape rates."""
    n = q.shape[0]
    off = q - diags(q.diagonal())
    forward = diags(np.ones(depth), -1, shape=(depth + 1, depth + 1))
    inside = kron(eye(depth + 1), diags(q.diagonal())) + kron(forward, off.T)
    loss = csr_matrix(np.concatenate([np.zeros(n * depth), -q.diagonal()]).reshape(1, -1))
    return bmat([[inside, csr_matrix((n * (depth + 1), 1))],
                 [loss, csr_matrix((1, 1))]], format="csr")


def jump_distribution(generator, initial, horizon, depth):
    n, m = initial.shape
    augmented = np.zeros((n * (depth + 1) + 1, m))
    augmented[:n] = initial
    result = expm_multiply(generator * horizon, augmented,
                          traceA=float(generator.diagonal().sum() * horizon))
    layers = result[:-1].reshape(depth + 1, n, m)
    return layers, result[-1]


def two_wait_cdf(a, b, horizon):
    if horizon == 0:
        return 0.0
    if abs(a - b) < 1e-8 * max(a, b):
        return -expm1(-a * horizon) - a * horizon * exp(-a * horizon)
    return 1 - (b * exp(-a * horizon) - a * exp(-b * horizon)) / (b - a)


def two_forward_bindings(square, horizon):
    """Probability the next two native jumps bind distinct pairs using fuel.

    Thermal/switch/reverse events compete normally. Subsequent events after
    the first two are unrestricted. This is a joint-law diagnostic, not a task.
    """
    n = len(square["states"])
    result = np.zeros(n)
    for i, first in enumerate(square["forward_pairs"]):
        a = square["escape"][i]
        for j, rate1, pair1 in first:
            b = square["escape"][j]
            second = sum(rate2 for _, rate2, pair2 in square["forward_pairs"][j]
                         if pair2 != pair1)
            result[i] += rate1 / a * second / b * two_wait_cdf(a, b, horizon)
    return result


def preparations(square):
    capacity = square["model"].p.capacity
    n = len(square["states"])
    result = {"equilibrium": square["equilibrium"].copy()}
    refueled = np.zeros(n)
    for i, state in enumerate(square["states"]):
        after = state.copy()
        after.fuel = capacity
        refueled[state_index(after, capacity)] += result["equilibrium"][i]
    result["refueled_equilibrium"] = refueled
    for name, bonds in {"unbound": set(), "one_bond": {(0, 1)},
                        "adjacent_two": {(0, 1), (0, 2)},
                        "opposite_two": {(0, 1), (2, 3)},
                        "four_bonds": set(PAIRS)}.items():
        state = State(POSITIONS.copy(), [1] * 4, bonds, min(2, capacity))
        law = np.zeros(n)
        law[state_index(state, capacity)] = 1
        result[name] = law
    return result
