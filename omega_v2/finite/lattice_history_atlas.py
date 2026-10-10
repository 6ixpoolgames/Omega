"""History occurrences with shared, complete native residual processes.

Canonicalization removes particle ID bookkeeping only; positions, reservoir
allocation and all event channels remain. No rotation or physical-state
quotient, no claim that a count of cached residuals is lushness.
"""

import hashlib
import json
from dataclasses import asdict
from itertools import pairwise
from math import log

import numpy as np
from scipy.linalg import expm

from omega_v2.finite.lattice_causal_count import dependencies
from omega_v2.finite.lattice_chemistry import Event, State
from omega_v2.finite.lattice_compartment import LocalEvent, LocalState


def state_from_record(record):
    args = ([tuple(p) for p in record["positions"]], list(record["internal"]),
            {tuple(p) for p in record["bonds"]})
    if "fuels" in record:
        return LocalState(*args, list(record["fuels"]), list(record["wastes"]))
    return State(*args, record["fuel"])


def event_from_record(record):
    data = dict(record)
    for key in ("members", "direction", "catalyst", "reservoir"):
        if key in data:
            data[key] = tuple(data[key])
    return LocalEvent(**data) if "reservoir" in data else Event(**data)


def canonical_state(state):
    order = sorted(range(len(state.positions)), key=state.positions.__getitem__)
    renaming = {old: new for new, old in enumerate(order)}
    positions = [state.positions[i] for i in order]
    internal = [state.internal[i] for i in order]
    bonds = {tuple(sorted((renaming[i], renaming[j]))) for i, j in state.bonds}
    if isinstance(state, LocalState):
        canonical = LocalState(positions, internal, bonds, state.fuels.copy(), state.wastes.copy())
    else:
        canonical = State(positions, internal, bonds, state.fuel)
    return canonical, renaming


def rule_dependencies(model, state, event):
    if event.kind == "hop":
        src, dst = event.reservoir
        # Destination count does not set the outgoing propensity, but its old
        # value enters the new count. Preserve both rate and update provenance.
        registers = {(event.species, src), (event.species, dst)}
        return registers, registers.copy()
    reads, writes = dependencies(model, state, event)
    if isinstance(state, LocalState) and event.kind in ("fuel", "catalytic"):
        reads.discard(("fuel",))
        writes.discard(("fuel",))
        c, = event.reservoir
        # One count sets the rate; both old counts enter the local update.
        reads.update({("F", c), ("W", c)})
        writes.update({("F", c), ("W", c)})
    return reads, writes


class HistoryAtlas:
    def __init__(self, model):
        self.model = model
        self.configuration = {"chemistry": asdict(model.p)}
        if hasattr(model, "reservoir"):
            self.configuration["reservoir"] = asdict(model.reservoir)
            self.configuration["resolved_volumes"] = model.volumes
        self.law_id = hashlib.sha256(json.dumps(self.configuration, sort_keys=True).encode()).hexdigest()
        self.index, self.states, self.channels = {}, [], []

    def intern(self, state):
        state, renaming = canonical_state(state)
        key = state.key()
        if key not in self.index:
            self.index[key] = len(self.states)
            self.states.append(state)
            channels = []
            for event in self.model.events(state):
                after = state.copy()
                self.model.apply(after, event)
                canonical, successor_map = canonical_state(after)
                reads, writes = rule_dependencies(self.model, state, event)
                channels.append({"event": asdict(event), "successor": canonical.record(),
                                 "successor_particle_map": successor_map,
                                 "reads": sorted(reads), "writes": sorted(writes)})
            self.channels.append(channels)
        return self.index[key], renaming

    def record(self):
        return {"law_id": self.law_id, "configuration": self.configuration,
                "residuals": [{"state": s.record(), "channels": c}
                              for s, c in zip(self.states, self.channels, strict=True)]}

    def prefixes(self, initial, depth):
        """Finite marked unfolding. Weights are jump-chain cylinder weights.

        Escape rates and native channel rates permit timed cylinder integration;
        the product of jump-choice probabilities is not a finite-horizon weight.
        """
        if depth < 0:
            raise ValueError("Nonnegative depth required")
        root, root_map = self.intern(initial)
        nodes = [{"parent": None, "residual": root, "depth": 0,
                  "particle_map": root_map,
                  "embedded_weight": 1., "event": None, "clock_rates": [], "rates": []}]
        for node_id, node in enumerate(nodes):
            if node["depth"] == depth:
                continue
            state = self.states[node["residual"]]
            events = self.model.events(state)
            escape = sum(e.rate for e in events)
            for e in events:
                after = state.copy()
                self.model.apply(after, e)
                target, mapping = self.intern(after)
                nodes.append({"parent": node_id, "residual": target, "depth": node["depth"]+1,
                              "particle_map": mapping,
                              "embedded_weight": node["embedded_weight"]*e.rate/escape,
                              "event": asdict(e), "clock_rates": node["clock_rates"]+[escape],
                              "rates": node["rates"]+[e.rate]})
        return nodes


def prefix_probability(node, horizon):
    """Specified next n marked events completed by T, arbitrary later future."""
    if horizon < 0:
        raise ValueError("Nonnegative horizon required")
    n = len(node["rates"])
    q = np.zeros((n+1, n+1))
    for i, (escape, rate) in enumerate(zip(node["clock_rates"], node["rates"], strict=True)):
        q[i, i], q[i, i+1] = -escape, rate
    return float(expm(q*horizon)[0, n])


def simulate_history(atlas, initial, seed, cuts=(0, 1, 5, 10), event_limit=1_000_000):
    if not cuts or cuts[0] < 0 or any(a >= b for a, b in pairwise(cuts)):
        raise ValueError("Strictly increasing nonnegative cuts required")
    model = atlas.model
    model.validate(initial)
    state, rng = initial.copy(), np.random.default_rng(seed)
    time, cut, log_density = 0., 0, 0.
    logs, snapshots, counts, last_writer = [], [], {}, {}
    depth = dict.fromkeys(state.bonds, 0)
    maximum_depth = 0
    while cut < len(cuts):
        events = model.events(state)
        total = sum(e.rate for e in events)
        next_time = time+rng.exponential(1/total) if total else float("inf")
        while cut < len(cuts) and cuts[cut] <= next_time:
            residual, mapping = atlas.intern(state)
            snapshots.append({"time": cuts[cut], "residual": residual,
                              "particle_map": mapping, **model.snapshot(state),
                              "counts": counts.copy(), "events": len(logs),
                              "max_construction_depth": maximum_depth,
                              "live_construction_depth": max(depth.values(), default=0),
                              "log_path_density": log_density-total*(cuts[cut]-time)})
            cut += 1
        if cut == len(cuts):
            break
        if len(logs) >= event_limit:
            raise RuntimeError("Event limit: incomplete trajectory, not discarded or renormalized")
        i = min(int(np.searchsorted(np.cumsum([e.rate for e in events]), rng.random()*total)),
                len(events)-1)
        event = events[i]
        reads, writes = rule_dependencies(model, state, event)
        parents = sorted({last_writer[k] for k in reads if k in last_writer})
        bound = event.members in state.bonds
        name = event.kind
        if name in ("fuel", "thermal", "catalytic"):
            name += "_reverse" if bound else "_forward"
            if bound:
                del depth[event.members]
            else:
                depth[event.members] = depth[event.catalyst]+1 if event.catalyst else 0
                maximum_depth = max(maximum_depth, depth[event.members])
        counts[name] = counts.get(name, 0)+1
        log_density += log(event.rate)-total*(next_time-time)
        logs.append({"time": next_time, "event": asdict(event), "parents": parents,
                     "reads": sorted(reads), "writes": sorted(writes)})
        for key in writes:
            last_writer[key] = len(logs)-1
        model.apply(state, event)
        time = next_time
    model.validate(state)
    assert initial.fuel-state.fuel == sum(counts.get(k+"_forward", 0)
                                          - counts.get(k+"_reverse", 0)
                                          for k in ("fuel", "catalytic"))
    assert len(state.bonds)-len(initial.bonds) == sum(counts.get(k+"_forward", 0)
                                                    - counts.get(k+"_reverse", 0)
                                                    for k in ("thermal", "fuel", "catalytic"))
    return {"law_id": atlas.law_id, "seed": seed, "initial": initial.record(),
            "final": state.record(), "events": logs, "snapshots": snapshots,
            "weight_note": "native SSA sample; log_path_density uses event-time Lebesgue density"}
