"""Equilibrium sampling for the existing lattice chemistry, not physical dynamics.

Sum over binary contact bonds analytically. Sample positions/conformations by
Metropolis relocation and heat-bath conformation updates, then draw conditional
bonds and fuel exactly. Finite Markov-chain output is approximate equilibrium;
mixing diagnostics must accompany its use. No sampler moves enter physical logs.
"""

from math import exp, log, log1p

import numpy as np

from omega_v2.finite.lattice_chemistry import State, logistic


def collapsed_log_weight(model, state):
    occupied = {p: i for i, p in enumerate(state.positions)}
    return (-model.p.exposed_energy * sum(state.internal)
            + sum(log1p(exp(-model.bond_energy(state, i, j)))
                  for i, j in model.contacts(state, occupied)))


def conditional_state(model, positions, internal, rng):
    state = State(positions.copy(), internal.copy(), set(),
                  int(rng.binomial(model.p.capacity, logistic(model.p.fuel_energy))))
    occupied = {p: i for i, p in enumerate(positions)}
    for i, j in model.contacts(state, occupied):
        if rng.random() < logistic(model.bond_energy(state, i, j)):
            state.bonds.add((i, j))
    return state


def sample_chain(model, seed, samples=24, burn_sweeps=4000, spacing=128,
                 compact_start=False):
    if samples < 2 or burn_sweeps < 0 or spacing < 1:
        raise ValueError("Need at least two samples and positive spacing")
    p, rng = model.p, np.random.default_rng(seed)
    initial = model.initial(seed)
    if compact_start:
        width = int(np.ceil(np.sqrt(p.particles)))
        initial.positions = [(i % width, i // width) for i in range(p.particles)]
        initial.internal = [1] * p.particles
    positions, internal = initial.positions, initial.internal
    grid = {pos: s for pos, s in zip(positions, internal, strict=True)}
    contact = ((log1p(exp(p.bond_strength/2)), log1p(exp(p.bond_strength/2))),
               (log1p(exp(p.bond_strength/2)), log1p(exp(p.bond_strength))))

    def score(pos, s):
        x, y = pos
        return sum(contact[s][grid[q]] for q in
                   ((x-1, y), (x+1, y), (x, y-1), (x, y+1)) if q in grid)

    states, trace, attempts, accepted = [], [], 0, 0
    total = burn_sweeps + samples * spacing
    for sweep in range(1, total + 1):
        for i in rng.permutation(p.particles):
            pos = positions[i]
            delta = p.exposed_energy - score(pos, 1) + score(pos, 0)
            internal[i] = int(rng.random() < logistic(delta))
            grid[pos] = internal[i]
            target_number = int(rng.integers(p.side**2))
            target = (target_number // p.side, target_number % p.side)
            if target in grid:
                continue
            attempts += 1
            old_score = score(pos, internal[i])
            del grid[pos]
            change = score(target, internal[i]) - old_score
            if change >= 0 or log(max(rng.random(), 1e-300)) < change:
                positions[i] = target
                accepted += 1
            grid[positions[i]] = internal[i]
        if sweep % spacing == 0 or sweep == total:
            state = conditional_state(model, positions, internal, rng)
            trace.append({"sweep": sweep, "log_weight": collapsed_log_weight(model, state),
                          **model.snapshot(state)})
        if sweep > burn_sweeps and (sweep-burn_sweeps) % spacing == 0:
            state = conditional_state(model, positions, internal, rng)
            model.validate(state)
            states.append(state.record())
    return {"states": states, "trace": trace, "seed": seed,
            "start": "compact_exposed" if compact_start else "dispersed_fair",
            "burn_sweeps": burn_sweeps, "spacing": spacing,
            "relocation_acceptance_given_vacancy": accepted/attempts if attempts else None}


def split_rhat(chains):
    """Basic split R-hat diagnostic, not a convergence certificate."""
    chains = np.asarray(chains, float)
    half = chains.shape[1] // 2
    if half < 2:
        return None
    split = np.concatenate((chains[:, :half], chains[:, -half:]), axis=0)
    within = float(np.mean(np.var(split, axis=1, ddof=1)))
    between = float(half * np.var(np.mean(split, axis=1), ddof=1))
    if within == 0:
        return 1.0 if between == 0 else None
    return float(np.sqrt(((half-1)*within/half + between/half)/within))
