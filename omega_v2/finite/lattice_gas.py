"""FHP-I local stochastic collision/streaming gas on an axial triangular torus.

Six unit-speed exclusion channels at each site. A tick is simultaneous local
collision followed by streaming, with fresh independent choices at pair sites.
Reference: Frisch et al., Complex Systems 1 (1987), Figure 4 / section 2.2.
"""

from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product

import numpy as np
from scipy.sparse import csr_matrix

from omega_v2.finite.multiway import NativeStep

VELOCITIES = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
PAIRS = tuple((1 << d) | (1 << (d+3)) for d in range(3))
TRIPLES = (21, 42)


@lru_cache(maxsize=64)
def local_collision(mask):
    if not isinstance(mask, int) or not 0 <= mask < 64:
        raise ValueError("six-bit local configuration required")
    if mask in PAIRS:
        return tuple((other, .5) for other in PAIRS if other != mask)
    if mask in TRIPLES:
        return ((TRIPLES[1-TRIPLES.index(mask)], 1.),)
    return ((mask, 1.),)


def encode(particles, side):
    state = 0
    for x, y, d in particles:
        if not (0 <= x < side and 0 <= y < side and 0 <= d < 6):
            raise ValueError("invalid particle address")
        bit = 1 << (6*(y*side+x)+d)
        if state & bit:
            raise ValueError("duplicate occupied velocity channel")
        state |= bit
    return state


def decode(state, side):
    result = []
    while state:
        bit = state & -state
        index = bit.bit_length()-1
        site, d = divmod(index, 6)
        y, x = divmod(site, side)
        result.append((x, y, d))
        state ^= bit
    return tuple(result)


def conserved(state, side):
    particles = decode(state, side)
    return (len(particles), sum(VELOCITIES[d][0] for _, _, d in particles),
            sum(VELOCITIES[d][1] for _, _, d in particles))


@lru_cache(maxsize=16)
def _stream_bits(side):
    return tuple(1 << (6*(((y+dy) % side)*side+(x+dx) % side)+d)
                 for y in range(side) for x in range(side)
                 for d, (dx, dy) in enumerate(VELOCITIES))


def successors(state, side):
    sites = {}
    work = state
    while work:
        bit = work & -work
        index = bit.bit_length()-1
        site, d = divmod(index, 6)
        sites[site] = sites.get(site, 0) | (1 << d)
        work ^= bit
    streams = _stream_bits(side)
    partial = [(0, 1.)]
    for site, mask in sites.items():
        options = []
        for out, probability in local_collision(mask):
            target = 0
            while out:
                bit = out & -out
                target |= streams[6*site+bit.bit_length()-1]
                out ^= bit
            options.append((target, probability))
        partial = [(prefix | target, weight*probability)
                   for prefix, weight in partial for target, probability in options]
    result = {}
    for target, probability in partial:
        result[target] = result.get(target, 0.)+probability
    return result


def enumerate_sector(side, particles=4, momentum=(0, 0)):
    """All exclusion configurations at fixed N and physical vector momentum."""
    states = []
    for directions in combinations_with_replacement(range(6), particles):
        if tuple(sum(VELOCITIES[d][axis] for d in directions) for axis in (0, 1)) != momentum:
            continue
        occupancies = [(d, directions.count(d)) for d in range(6) if d in directions]
        placements = [tuple(combinations(range(side*side), n)) for _, n in occupancies]
        for locations in product(*placements):
            state = 0
            for (d, _), sites in zip(occupancies, locations, strict=True):
                for site in sites:
                    state |= 1 << (6*site+d)
            states.append(state)
    return sorted(states)


def exact_sector(side, particles=4, momentum=(0, 0)):
    states = enumerate_sector(side, particles, momentum)
    index = {s: i for i, s in enumerate(states)}
    indptr, indices, data = [0], [], []
    for state in states:
        for target, weight in successors(state, side).items():
            indices.append(index[target])
            data.append(weight)
        indptr.append(len(indices))
    p = csr_matrix((data, indices, indptr), shape=(len(states), len(states)))
    p.sort_indices()
    row_error = float(np.max(np.abs(np.asarray(p.sum(axis=1)).ravel()-1)))
    col_error = float(np.max(np.abs(np.asarray(p.sum(axis=0)).ravel()-1)))
    return states, index, p, {"row_error": row_error, "column_error": col_error}


class FHPAdapter:
    """Lazy adapter for the existing reusable multiway engine."""

    clock = "discrete"

    def __init__(self, side):
        if not isinstance(side, int) or side < 3:
            raise ValueError("torus side must be an integer >=3")
        self.side = side

    @property
    def identity(self):
        return {"type": "FHP-I", "schema": 1, "side": self.side,
                "clock": "collision-then-stream", "pair_probabilities": [.5, .5],
                "boundary": "periodic", "randomness": "independent-per-site-per-tick"}

    def canonical(self, state):
        if not isinstance(state, int) or not 0 <= state < 1 << (6*self.side*self.side):
            raise ValueError("invalid global configuration")
        return state

    def key(self, state):
        return self.canonical(state)

    def encode(self, state):
        return str(self.canonical(state))

    def decode(self, value):
        return self.canonical(int(value))

    def steps(self, state):
        for target, weight in successors(self.canonical(state), self.side).items():
            yield NativeStep(target, weight)
