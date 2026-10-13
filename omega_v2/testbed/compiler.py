"""Compile native events once, aggregating outcomes without event-label entropy."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
import numpy as np
from scipy.sparse import coo_matrix
from .contracts import WorldSpec


def compile_world(world: WorldSpec, max_states=10000):
    st = world.states
    if len(st) > max_states:
        raise RuntimeError("State cap: law not truncated")
    if len(st) != len(set(st)) or not st:
        raise ValueError("World requires unique nonempty finite states")
    modules = sorted(world.modules, key=lambda m: m.id)
    if len({m.id for m in modules}) != len(modules):
        raise ValueError("Duplicate module IDs")
    available = set(world.metadata.get("fields", ()))
    provided = set()
    for module in modules:
        for name in module.provides:
            if name in provided:
                raise ValueError(f"Undeclared duplicate provision: {name}")
            provided.add(name)
    available |= provided
    for module in modules:
        if set(module.requires) - available:
            raise ValueError(f"Missing dependencies for {module.id}")
    index = {s: i for i, s in enumerate(st)}
    values = {name: np.array([fn(s) for s in st], dtype=float)
              for name, fn in world.observables.items()}
    energies = np.array([world.energy(s) for s in st], dtype=float)
    if not np.all(np.isfinite(energies)) or any(not np.all(np.isfinite(x)) for x in values.values()):
        raise ValueError("Nonfinite state observable")
    rows, cols, rates = [], [], []
    flows = defaultdict(lambda: np.zeros(len(st)))
    families, rules = set(), set()
    for i, s in enumerate(st):
        world.validate(s)
        total = 0.0
        for module in modules:
            for event in module.events(s):
                if not isfinite(event.rate) or event.rate < 0 or not isfinite(event.work):
                    raise ValueError("Nonfinite or negative native event")
                world.validate(event.target)
                if event.target not in index:
                    raise ValueError("Event exits declared state space; no reflecting truncation")
                if any(c < 0 or c >= len(s) for c in event.support):
                    raise ValueError("Invalid event support")
                changed = {c for c, (a, b) in enumerate(zip(s, event.target)) if a != b}
                if not changed <= set(event.support):
                    raise ValueError("Event update outside declared support")
                if not event.rule_id or not event.family:
                    raise ValueError("Stable rule and family IDs required")
                reserved = {"drive_work", "bath_heat", *[f"net_{name}" for name in values]}
                if event.family in reserved:
                    raise ValueError("Event family collides with an accounting field")
                if event.rate == 0:
                    continue
                j = index[event.target]
                if j == i:
                    raise ValueError("Unrecorded self events cannot create state-history breadth")
                rows.append(i); cols.append(j); rates.append(event.rate); total += event.rate
                families.add(event.family); rules.add(event.rule_id)
                flows[event.family][i] += event.rate
                flows["drive_work"][i] += event.rate * event.work
                flows["bath_heat"][i] += event.rate * (event.work - energies[j] + energies[i])
                for name, v in values.items():
                    flows[f"net_{name}"][i] += event.rate * (v[j] - v[i])
                for name, value in event.increments.items():
                    if name in reserved or name == event.family:
                        raise ValueError(f"Reserved accounting field: {name}")
                    if not isfinite(value):
                        raise ValueError("Nonfinite event ledger")
                    flows[name][i] += event.rate * value
        rows.append(i); cols.append(i); rates.append(-total)
    q = coo_matrix((rates, (rows, cols)), shape=(len(st), len(st))).tocsr()
    if max(abs(np.asarray(q.sum(axis=1)).ravel())) > 1e-10:
        raise ArithmeticError("Generator mass accounting")
    if max(abs(q @ energies - flows["drive_work"] + flows["bath_heat"])) > 1e-9:
        raise ArithmeticError("Energy ledger does not close")
    for name,v in values.items():
        if max(abs(q@v-flows[f'net_{name}']))>1e-9:
            raise ArithmeticError(f'Observable ledger does not close: {name}')
    return {"states": st, "index": index, "Q": q, "flows": dict(flows),
            "observables": values, "energy": energies, "families": sorted(families),
            "rules": sorted(rules), "world": world, "metadata": dict(world.metadata),
            "capabilities": {"finite_state": True, "sparse_propagation": True,
                             "native_event_sampling": True, "exact_entropy": "memory-gated"}}


def sample_events(world, root, horizon, rng, max_events=100000):
    """SSA using exactly the same registered event enumeration as compilation."""
    if not isfinite(horizon) or horizon < 0:
        raise ValueError("Negative horizon")
    world.validate(root)
    if horizon==0:return root,[]
    t, state, trace = 0.0, root, []
    for _ in range(max_events):
        events = [e for m in sorted(world.modules, key=lambda m: m.id) for e in m.events(state)]
        if any(not isfinite(e.rate) or e.rate<0 for e in events):raise ValueError('Invalid native rate')
        events=[e for e in events if e.rate>0]
        if not events:
            return state, trace
        weights = np.array([e.rate for e in events])
        t += rng.exponential(1 / weights.sum())
        if t > horizon:
            return state, trace
        event = events[rng.choice(len(events), p=weights / weights.sum())]
        world.validate(event.target)
        trace.append((t, event)); state = event.target
    raise RuntimeError("SSA event cap reached; trajectory incomplete")
