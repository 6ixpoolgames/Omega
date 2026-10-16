"""Whole-law composition checks, not independence inferred from diamonds."""

import math
from dataclasses import dataclass

import numpy as np

from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw


@dataclass(frozen=True)
class FactorizationAudit:
    holds: bool
    cartesian: bool
    max_error: float | None
    marginal_error: float | None
    reason: str
    local_laws: tuple[FiniteContinuationLaw, ...] = ()


@dataclass(frozen=True)
class ProjectionAudit:
    markov: bool
    max_error: float
    groups: tuple[object, ...]
    projected_law: FiniteContinuationLaw | None


def audit_projection(law, projection, *, atol=1e-12):
    """Strong lumpability check: does a declared frame have its own Markov law?

    Failure does not remove the frame. Its time-dependent readouts still come
    from the full native process; replacing them with this smaller kernel would
    lose dependence on the unobserved physical state.
    """
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    values = tuple(projection(state) for state in law.states)
    groups = tuple(dict.fromkeys(values))
    index = {value: i for i, value in enumerate(groups)}
    assignment = np.zeros((len(values), len(groups)))
    for i, value in enumerate(values):
        assignment[i, index[value]] = 1.
    aggregated = law.operator @ assignment
    operator = np.zeros((len(groups), len(groups)))
    references, error = {}, 0.
    for i, value in enumerate(values):
        if value not in references:
            references[value] = aggregated[i]
            operator[index[value]] = aggregated[i]
        error = max(error, float(np.max(np.abs(aggregated[i] - references[value]))))
    markov = error <= atol
    if law.clock == "continuous":
        # Reconstruct the conservative diagonal from nonnegative cross-group
        # rates; summing a generator row can leave tiny roundoff at a one-group
        # projection, where the correct generator is exactly zero.
        np.fill_diagonal(operator, 0.)
        np.fill_diagonal(operator, -operator.sum(axis=1))
    # A tuple wrapper preserves a projected configuration as one categorical
    # coordinate; it does not choose a Euclidean embedding of the group labels.
    projected = (FiniteContinuationLaw(tuple((value,) for value in groups), operator,
                                      clock=law.clock) if markov else None)
    return ProjectionAudit(markov, error, groups, projected)


def audit_factorization(law, blocks, *, atol=1e-12):
    """Test the complete finite K product / Q sum on a physical partition.

    All native coordinates must be retained. A non-Cartesian domain cannot
    certify independent components. This is relative to the supplied finite
    state law; hidden apparatus or omitted environment is not thereby checked.
    """
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    blocks = tuple(tuple(block) for block in blocks)
    width = len(law.states[0])
    indices = tuple(i for block in blocks for i in block)
    if (len(blocks) < 2 or any(not block for block in blocks)
            or any(not isinstance(i, int) or isinstance(i, bool) for i in indices)
            or len(indices) != width or set(indices) != set(range(width))):
        raise ValueError("blocks must partition all native coordinates into >=2 nonempty regions")
    projections = [tuple(tuple(state[i] for i in block) for state in law.states)
                   for block in blocks]
    alphabets = [tuple(dict.fromkeys(values)) for values in projections]
    locations = tuple(tuple(alphabet.index(values[s]) for alphabet, values
                            in zip(alphabets, projections, strict=True))
                      for s in range(len(law.states)))
    expected_size = math.prod(map(len, alphabets))
    if expected_size != len(law.states) or len(set(locations)) != expected_size:
        return FactorizationAudit(False, False, None, None,
                                  "native domain is not the Cartesian product of the regions")
    local_laws, marginal_error = [], 0.
    for component, alphabet in enumerate(alphabets):
        local = np.zeros((len(alphabet), len(alphabet)))
        representatives = {}
        for i, location in enumerate(locations):
            local_source = location[component]
            marginal = np.zeros(len(alphabet))
            for j, target in enumerate(locations):
                if law.clock == "discrete" or target[component] != local_source:
                    marginal[target[component]] += law.operator[i, j]
            if law.clock == "continuous":
                marginal[local_source] = -marginal.sum()
            if local_source not in representatives:
                representatives[local_source] = marginal
                local[local_source] = marginal
            marginal_error = max(marginal_error, float(np.max(
                np.abs(marginal - representatives[local_source]))))
        local_laws.append(FiniteContinuationLaw(alphabet, local, clock=law.clock))
    error = 0.
    for i, source in enumerate(locations):
        for j, target in enumerate(locations):
            if law.clock == "discrete":
                expected = math.prod(local.operator[a, b] for local, a, b in
                                     zip(local_laws, source, target, strict=True))
            else:
                expected = sum(local_laws[k].operator[source[k], target[k]]
                               for k in range(len(blocks))
                               if all(source[m] == target[m] for m in range(len(blocks)) if m != k))
            error = max(error, abs(float(law.operator[i, j]) - expected))
    holds = bool(max(error, marginal_error) <= atol)
    return FactorizationAudit(holds, True, float(error), marginal_error,
                              "whole finite law factorizes" if holds else
                              "contextual rates/probabilities or joint updates violate factorization",
                              tuple(local_laws) if holds else ())


@dataclass(frozen=True)
class SquareAudit:
    first_rates: tuple[float, float]
    residual_rates: tuple[float, float]
    two_orders_exist: bool
    rate_preserving: bool
    statement: str = "local two-update witness only; not an independence certificate"


def audit_square(law, root, left, right, *, atol=1e-12):
    """Check two concrete disjoint-coordinate updates and their residual rates.

    left/right are native target configurations reached by each first update.
    Their combined configuration is derived by applying both changed-coordinate
    sets. Missing states/transitions are zero. Other enabled rules remain in the
    law. A successful square still says nothing about untested contexts or triples.
    """
    if not math.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    root, left, right = tuple(root), tuple(left), tuple(right)
    index = {state: i for i, state in enumerate(law.states)}
    if root not in index or left not in index or right not in index:
        raise ValueError("square configurations must belong to the native law")
    a = {i for i, (x, y) in enumerate(zip(root, left, strict=True)) if x != y}
    b = {i for i, (x, y) in enumerate(zip(root, right, strict=True)) if x != y}
    if not a or not b or a & b:
        raise ValueError("square needs two nonempty disjoint physical updates")
    joint = tuple(left[i] if i in a else right[i] for i in range(len(root)))
    def entry(source, target):
        return 0. if target not in index else float(law.operator[index[source], index[target]])
    first = entry(root, left), entry(root, right)
    residual = entry(right, joint), entry(left, joint)
    exists = min(first + residual) > 0
    return SquareAudit(first, residual, exists,
                       exists and bool(np.allclose(first, residual, atol=atol, rtol=0.)))
