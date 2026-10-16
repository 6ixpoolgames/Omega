"""Bounded audit of additive invariants in the FHP-I even-torus update."""

import json
from pathlib import Path

import numpy as np
from scipy.linalg import null_space

from omega_v2.finite.lattice_gas import (
    PAIRS,
    TRIPLES,
    VELOCITIES,
    encode,
    local_collision,
)
from omega_v2.finite.lattice_gas_sampling import from_bitstates, step_batch
from omega_v2.validation.lattice_gas_scaling_v0 import uniform_sector

OUT = Path("results/local_runs/fhp_invariant_audit_v0")


def invariant_basis(side, eigenvalue=1):
    """Orthonormal additive coefficients whose values scale by eigenvalue.

    Single particles enforce free streaming. Pair/triple rows enforce equality
    of every stochastic/deterministic collision outcome after streaming.
    These local constraints are sufficient for every global configuration.
    """
    slots = 6 * side * side
    rows = []

    def slot(x, y, d):
        return 6 * ((y % side) * side + (x % side)) + d

    for y in range(side):
        for x in range(side):
            for d, (dx, dy) in enumerate(VELOCITIES):
                row = np.zeros(slots)
                row[slot(x + dx, y + dy, d)] += 1
                row[slot(x, y, d)] -= eigenvalue
                rows.append(row)
            for mask in (*PAIRS, *TRIPLES):
                outcomes = [tuple(d for d in range(6) if out >> d & 1)
                            for out, _ in local_collision(mask)]
                before = tuple(d for d in range(6) if mask >> d & 1)
                for other in outcomes:
                    row = np.zeros(slots)
                    for d in other:
                        dx, dy = VELOCITIES[d]
                        row[slot(x + dx, y + dy, d)] += 1
                    for d in before:
                        row[slot(x, y, d)] -= eigenvalue
                    rows.append(row)
    return null_space(np.asarray(rows), rcond=1e-10)


def occupancy(state, side):
    return np.fromiter(((state >> i) & 1 for i in range(6 * side * side)),
                       dtype=float)


def alternating_values(state, side):
    masks = np.array([(state >> (6 * site)) & 63
                      for site in range(side * side)], dtype=np.int64).reshape(side, side)
    n = np.stack([((masks >> d) & 1) for d in range(6)], axis=-1)
    xsign = (-1.) ** np.arange(side)[None, :]
    ysign = (-1.) ** np.arange(side)[:, None]
    return np.array([
        np.sum(ysign * (n[:, :, 1] + n[:, :, 2] - n[:, :, 4] - n[:, :, 5])),
        np.sum(xsign * (n[:, :, 0] - n[:, :, 2] - n[:, :, 3] + n[:, :, 5])),
        np.sum(xsign * ysign * (n[:, :, 0] + n[:, :, 1] - n[:, :, 3] - n[:, :, 4])),
    ])


def prep(side, density, kind):
    particles = []
    for y in range(side):
        for x in range(side):
            active = ((x % 2 == 0 and y % 2 == 0) if density == .5
                      else (x + y) % 2 == 0)
            if kind in ("pair_grid", "aimed_grid") and active:
                d = (x + y) % 3
                particles.extend(((x, y, d), (x, y, d + 3)))
    if kind == "aimed_grid":
        particles = [((x - VELOCITIES[d][0]) % side,
                      (y - VELOCITIES[d][1]) % side, d) for x, y, d in particles]
    return encode(particles, side)


def thermal_states(side, number, samples, rng):
    # Same uniform fixed-N, zero-vector-momentum sampling scheme as scaling run.
    batch, _ = uniform_sector(side, number, samples, rng)
    states = []
    for masks in batch:
        state = 0
        for site, mask in enumerate(masks.flat):
            state |= int(mask) << (6 * site)
        states.append(state)
    return states


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261007)
    panels = []
    for side in (6, 12):
        basis = invariant_basis(side, 1)
        alternating = invariant_basis(side, -1)
        # Verify the claimed invariants on all local update cases and sampled
        # global states, including the actual published preparations.
        checks = 0
        for density in (.5, 1.):
            number = int(side * side * density)
            for kind in ("pair_grid", "aimed_grid"):
                root = prep(side, density, kind)
                nxt, _ = step_batch(from_bitstates([root] * 8, side), rng)
                for after in nxt:
                    next_state = sum(int(mask) << (6 * site)
                                     for site, mask in enumerate(after.flat))
                    assert np.max(np.abs(basis.T @ (occupancy(next_state, side) -
                                                   occupancy(root, side)))) < 1e-8
                    assert np.max(np.abs(alternating.T @ (occupancy(next_state, side) +
                                                        occupancy(root, side)))) < 1e-8
                    assert np.array_equal(alternating_values(next_state, side),
                                          -alternating_values(root, side))
                    checks += 1
            states = thermal_states(side, number, 128, rng)
            nxt, _ = step_batch(from_bitstates(states, side), rng)
            for state, after in zip(states, nxt, strict=True):
                next_state = sum(int(mask) << (6 * site)
                                 for site, mask in enumerate(after.flat))
                assert np.max(np.abs(basis.T @ (occupancy(next_state, side) -
                                               occupancy(state, side)))) < 1e-8
                assert np.max(np.abs(alternating.T @ (occupancy(next_state, side) +
                                                    occupancy(state, side)))) < 1e-8
                assert np.array_equal(alternating_values(next_state, side),
                                      -alternating_values(state, side))
                checks += 1
            prep_scores = {}
            alternating_scores = {}
            for kind in ("pair_grid", "aimed_grid"):
                z = basis.T @ occupancy(prep(side, density, kind), side)
                prep_scores[kind] = float(np.linalg.norm(z))
                alternating_scores[kind] = float(np.linalg.norm(
                    alternating.T @ occupancy(prep(side, density, kind), side)))
            thermal_scores = np.array([np.linalg.norm(basis.T @ occupancy(s, side))
                                       for s in states])
            thermal_alternating = np.array([np.linalg.norm(
                alternating.T @ occupancy(s, side)) for s in states])
            panels.append({"side": side, "density": density, "particles": number,
                           "invariant_dimension": int(basis.shape[1]),
                           "conventional_NPxPy_dimension": 3,
                           "additional_additive_dimensions": int(basis.shape[1] - 3),
                           "period_two_alternating_dimension": int(alternating.shape[1]),
                           "alternating_projection_norms": alternating_scores,
                           "thermal_alternating_projection_norm": {
                               "mean": float(thermal_alternating.mean()),
                               "sd": float(thermal_alternating.std(ddof=1)),
                               "min": float(thermal_alternating.min()),
                               "max": float(thermal_alternating.max())},
                           "prep_projection_norms": prep_scores,
                           "thermal_projection_norm": {
                               "mean": float(thermal_scores.mean()),
                               "sd": float(thermal_scores.std(ddof=1)),
                               "min": float(thermal_scores.min()),
                               "max": float(thermal_scores.max())},
                           "thermal_samples": len(states)})
        # Side12 local and sampled checks run above; dimensions are global.
        assert basis.shape[1] == 3 and alternating.shape[1] == 3
        panels[-1]["verified_transition_checks_this_side"] = checks
    result = {"rule": "FHP-I collision then streaming", "even_tori": [6, 12],
              "seed": 20261007, "panels": panels}
    (OUT / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
