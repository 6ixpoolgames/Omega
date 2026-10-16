"""Finite two-voxel closed SchlÃ¶gl reaction-diffusion master equation.

This is an RDME adaptation of the published SchlÃ¶gl reaction mechanism, not
the exclusion-based lattice-gas automaton in Boon et al. States are ordered
as (A0, X0, B0, A1, X1, B1), with unit voxel volume.
"""

from math import factorial

import numpy as np


def _weak_compositions(total, slots):
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _weak_compositions(total - first, slots - 1):
            yield (first,) + rest


def build_model(k, d):
    """Return the 105-state active closed component and its CTMC generator.

    Local propensities in each voxel are A->X: a, X->A: x,
    B+2X->3X: k*b*x*(x-1), and the reverse:
    k*x*(x-1)*(x-2). The unimolecular rate constant is 1. Each molecule diffuses to the other voxel
    at rate d, independently of species. Chemical combinatorial factorials
    are absorbed into k as declared in the protocol.
    """
    if k < 0 or d < 0:
        raise ValueError("k and d must be nonnegative")

    states = []
    for state in _weak_compositions(4, 6):
        if state[0] + state[1] + state[3] + state[4] >= 2:
            states.append(state)
    states = sorted(states)
    index = {state: i for i, state in enumerate(states)}
    nstates = len(states)
    q = np.zeros((nstates, nstates), dtype=float)
    activity = np.zeros(nstates, dtype=float)
    forward = np.zeros(nstates, dtype=float)
    reverse = np.zeros(nstates, dtype=float)
    x_count = np.zeros(nstates, dtype=float)

    for i, state in enumerate(states):
        rates = {}

        def add(target, rate, row_rates=rates):
            if rate <= 0:
                return
            target = tuple(target)
            if target not in index:
                raise RuntimeError("transition left the declared active component")
            row_rates[target] = row_rates.get(target, 0.0) + rate

        for offset in (0, 3):
            a, x, b = state[offset:offset + 3]

            target = list(state)
            target[offset] -= 1
            target[offset + 1] += 1
            add(target, float(a))

            target = list(state)
            target[offset] += 1
            target[offset + 1] -= 1
            add(target, float(x))

            target = list(state)
            target[offset + 1] += 1
            target[offset + 2] -= 1
            f_rate = k * b * x * (x - 1)
            add(target, f_rate)
            forward[i] += f_rate

            target = list(state)
            target[offset + 1] -= 1
            target[offset + 2] += 1
            r_rate = k * x * (x - 1) * (x - 2)
            add(target, r_rate)
            reverse[i] += r_rate

        for species in (0, 1, 2):
            left = state[species]
            right = state[species + 3]
            target = list(state)
            target[species] -= 1
            target[species + 3] += 1
            add(target, d * left)

            target = list(state)
            target[species] += 1
            target[species + 3] -= 1
            add(target, d * right)

        activity[i] = sum(rates.values())
        for target, rate in rates.items():
            j = index[target]
            q[i, j] += rate
            q[i, i] -= rate
        x_count[i] = state[1] + state[4]

    weights = np.array([
        np.prod([1.0 / factorial(n) for n in state])
        for state in states
    ])
    pi = weights / weights.sum()

    return {
        "states": states,
        "index": index,
        "q": q,
        "pi": pi,
        "observables": {
            "activity": activity,
            "forward": forward,
            "reverse": reverse,
            "x_count": x_count,
        },
    }
