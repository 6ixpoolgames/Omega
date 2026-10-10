"""Finite exploratory count-once content/access profile, classical sector.

Records are truth tables over eight retained source assignments. A partition is
an information key, never an identification of physical states. Every route
keeps its program and residual; probability is on sources, not on programs.
"""

from dataclasses import dataclass
from itertools import combinations, product
from math import isclose, isfinite, log2

INPUTS = tuple(product((0, 1), repeat=3))
FULL = 255


def bits(values):
    return sum(int(v) << i for i, v in enumerate(values))


SOURCES = tuple(bits(x[j] for x in INPUTS) for j in range(3))


def rows(registers):
    return tuple(tuple((r >> x) & 1 for r in registers) for x in range(8))


def check_law(weights):
    if len(weights) != 8 or any(not isfinite(p) or p < 0 for p in weights):
        raise ValueError("Expected eight finite nonnegative source probabilities")
    if not isclose(sum(weights), 1, abs_tol=1e-12, rel_tol=0):
        raise ValueError("Source law must sum to one; no silent renormalization")


def entropy(values, weights):
    check_law(weights)
    mass = {}
    for value, p in zip(values, weights, strict=True):
        mass[value] = mass.get(value, 0) + p
    return -sum(p * log2(p) for p in mass.values() if p)


def partition(registers):
    names = {}
    return tuple(names.setdefault(v, len(names)) for v in rows(registers))


def information(registers, weights):
    # Deterministic records: I(X;R) = H(R). No stochastic records are omitted:
    # a random fault must be included in X before using this finite interface.
    rr = rows(registers)
    h = entropy(rr, weights)
    individual = sum(
        entropy(tuple(x[j] for x in INPUTS), weights)
        + h
        - entropy(tuple((x[j], r) for x, r in zip(INPUTS, rr, strict=True)), weights)
        for j in range(3)
    )
    return {"bits": h, "syn": h - individual, "volume": 2 ** (h - entropy(INPUTS, weights))}


def native_frames(records, weights):
    frames = []
    for mask in range(1 << len(records)):
        subset = tuple(r for i, r in enumerate(records) if mask & (1 << i))
        frames.append({"mask": mask, "size": mask.bit_count(), **information(subset, weights)})
    return frames


@dataclass(frozen=True)
class Route:
    outputs: tuple[int, ...]
    used: int
    steps: int
    ccx: int
    program: tuple[int, ...]

    @property
    def cost(self):
        return self.used.bit_count(), self.steps, self.ccx


def gate_language(nrecords, noutputs):
    gates = []
    for target in range(noutputs):
        available = [i for i in range(nrecords + noutputs) if i != nrecords + target]
        for n in range(3):
            for controls in combinations(available, n):
                for polarity in product((0, 1), repeat=n):
                    gates.append((target, tuple(zip(controls, polarity, strict=True))))
    return tuple(gates)


def apply(records, outputs, gate):
    target, controls = gate
    values = records + outputs
    active = FULL
    for c, polarity in controls:
        active &= values[c] if polarity else values[c] ^ FULL
    result = list(outputs)
    result[target] ^= active
    return tuple(result)


def enumerate_routes(records, *, depth=2, noutputs=2):
    """All reachable states in the specified language/bound, including early stop.

    Inputs are read-only; two physical output blanks are allocated throughout.
    Operations are reversible X/CNOT/Toffoli with either control polarity.
    Bills retain steps and two-control operations separately. No free readout.
    """
    if depth < 0 or noutputs < 1 or any(not 0 <= r <= FULL for r in records):
        raise ValueError("Invalid finite apparatus")
    gates = gate_language(len(records), noutputs)
    start = Route((0,) * noutputs, 0, 0, 0, ())
    found = [start]
    frontier = [start]
    seen = {(start.outputs, start.used, start.ccx)}
    for step in range(1, depth + 1):
        next_frontier = []
        for old in frontier:
            for g, gate in enumerate(gates):
                output = apply(records, old.outputs, gate)
                used = old.used
                for c, _ in gate[1]:
                    if c < len(records):
                        used |= 1 << c
                ccx = old.ccx + (len(gate[1]) == 2)
                key = output, used, ccx
                if key in seen:
                    continue
                seen.add(key)
                new = Route(output, used, step, ccx, old.program + (g,))
                found.append(new)
                next_frontier.append(new)
        frontier = next_frontier
    return gates, found


def content_frontiers(routes):
    """Count an information partition once; retain all nondominated route witnesses."""
    groups = {}
    for i, route in enumerate(routes):
        groups.setdefault(partition(route.outputs), []).append(i)
    return [
        {
            "partition": key,
            "routes": [
                i
                for i in ids
                if not any(
                    routes[j].cost != routes[i].cost
                    and all(a <= b for a, b in zip(routes[j].cost, routes[i].cost, strict=True))
                    for j in ids
                )
            ],
        }
        for key, ids in sorted(groups.items())
    ]


def envelope(routes, weights, *, nrecords, depth):
    """Max jointly delivered information at each budget, not a sum over routes.

    This is an existential access envelope, not actual policy selection or a
    complete aggregation of all locations. The separate partition/route catalog
    exposes differences the scalar cells lose. Incompatible routes are not joined.
    """
    h = [entropy(rows(r.outputs), weights) for r in routes]
    hx = entropy(INPUTS, weights)
    profile = []
    for size, steps, ccx in product(range(nrecords + 1), range(depth + 1), range(depth + 1)):
        ids = [
            i
            for i, r in enumerate(routes)
            if all(a <= b for a, b in zip(r.cost, (size, steps, ccx), strict=True))
        ]
        best = max(ids, key=lambda i: h[i])
        profile.append(
            {
                "budget": [size, steps, ccx],
                "bits": h[best],
                "volume": 2 ** (h[best] - hx),
                "route": best,
            }
        )
    return profile
