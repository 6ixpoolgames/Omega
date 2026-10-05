"""Naive counts on native rule-dependency histories; no modification of dynamics.

These are last-writer provenance graphs, not identified counterfactual causes.
Both the full graph and the projection omitting the shared fuel register are
retained. Initial facts are boundary conditions, not invented counted events.
"""

from bisect import bisect_right
from collections import Counter
from math import log2

from omega_v2.finite.lattice_damage import event_from_record, state_from_record


def bond_key(i, j):
    return ("bond", min(i, j), max(i, j))


def dependencies(model, state, event):
    """Physical rule reads and changed registers, with joint guards retained.

    This explicit adapter reads the formula's structural arguments, including
    zero/absent bond guards. It is not a finite-difference test of necessity.
    """
    members = event.members
    reads, writes = set(), set()
    if event.kind == "switch":
        i = members[0]
        reads.add(("internal", i))
        if model.p.bond_strength:
            reads.update(bond_key(i, j) for j in range(model.p.particles) if j != i)
            for a, b in state.bonds:
                if i in (a, b):
                    reads.add(("internal", b if a == i else a))
        writes.add(("internal", i))
    elif event.kind == "move":
        for i in members:
            reads.add(("position", i))
            reads.update(bond_key(i, j) for j in range(model.p.particles) if j != i)
            x, y = state.positions[i]
            dx, dy = event.direction
            reads.add(("occupant", x + dx, y + dy))
            writes.add(("position", i))
        before = {state.positions[i]: i for i in members}
        after = {(state.positions[i][0] + event.direction[0],
                  state.positions[i][1] + event.direction[1]): i for i in members}
        for pos in before.keys() | after.keys():
            if before.get(pos) != after.get(pos):
                writes.add(("occupant", *pos))
    else:
        i, j = members
        reads.update({("position", i), ("position", j), bond_key(i, j)})
        if model.p.bond_strength:
            reads.update({("internal", i), ("internal", j)})
        writes.add(bond_key(i, j))
        if event.kind in ("fuel", "catalytic"):
            reads.add(("fuel",))
            writes.add(("fuel",))
        if event.catalyst:
            a, b = event.catalyst
            reads.update({("position", a), ("position", b), ("internal", a),
                          ("internal", b), bond_key(a, b)})
    return reads, writes


def graph_profiles(parents, cuts, times):
    """Exact combinatorial counts on this declared DAG, not on all futures."""
    ancestors, reduced, depth, route_ending = [], [], [], []
    for i, pred in enumerate(parents):
        inherited = 0
        for p in pred:
            if p >= i:
                raise ValueError("Dependency must precede its child")
            inherited |= ancestors[p]
        mask = inherited
        for p in pred:
            mask |= 1 << p
        essential = [p for p in pred if not (inherited >> p) & 1]
        ancestors.append(mask)
        reduced.append(essential)
        depth.append(1 + max((depth[p] for p in essential), default=0))
        route_ending.append(1 + sum(route_ending[p] for p in essential))
    rows = []
    for cut in cuts:
        n = bisect_right(times, cut)
        edges = sum(len(v) for v in reduced[:n])
        pairs = sum(v.bit_count() for v in ancestors[:n])
        successors = [0] * n
        for pred in reduced[:n]:
            for p in pred:
                successors[p] += 1
        layers = Counter(depth[:n])
        routes = sum(route_ending[:n])
        # Reverse propagation gives unique descendants without double-counting
        # reconvergent routes within a source's cone.
        descendants = [0] * n
        for child in range(n - 1, -1, -1):
            for p in reduced[child]:
                descendants[p] |= descendants[child] | (1 << child)
        cone_sizes = [1 + v.bit_count() for v in descendants]
        rows.append({"time": cut, "events": n, "edges": edges,
                     "raw_dependency_edges": sum(len(v) for v in parents[:n]),
                     "ancestor_pairs": pairs, "cone_sum": n + pairs,
                     "mean_cone": (n + pairs) / n if n else 0.0,
                     "max_cone": max(cone_sizes, default=0),
                     "forks": sum(v >= 2 for v in successors),
                     "mergers": sum(len(v) >= 2 for v in reduced[:n]),
                     "roots": sum(not v for v in reduced[:n]),
                     "leaves": sum(v == 0 for v in successors),
                     "depth": max(depth[:n], default=0),
                     "layer_breadth": max(layers.values(), default=0),
                     "log2_routes": log2(routes) if routes else 0.0,
                     "routes_exact": str(routes)})
    return rows, reduced


def causal_count(model, trajectory, cuts=(0, 1, 5, 10, 20)):
    state = state_from_record(trajectory["initial"])
    last_writer, full, material, fuel_edges = {}, [], [], []
    times = []
    for index, record in enumerate(trajectory["events"]):
        event = event_from_record(record)
        reads, writes = dependencies(model, state, event)
        ordinary = {last_writer[k] for k in reads if k != ("fuel",) and k in last_writer}
        fuel = {last_writer[("fuel",)]} if ("fuel",) in reads and ("fuel",) in last_writer else set()
        full.append(sorted(ordinary | fuel))
        material.append(sorted(ordinary))
        fuel_edges.append(sorted(fuel - ordinary))
        model.apply(state, event)
        for key in writes:
            last_writer[key] = index
        times.append(float(record[0]))
    model.validate(state)
    if "final" in trajectory and state.key() != state_from_record(trajectory["final"]).key():
        raise AssertionError("Replay changed physical history")
    full_rows, reduced = graph_profiles(full, cuts, times)
    local_rows, local_reduced = graph_profiles(material, cuts, times)
    return {"full": full_rows, "without_fuel_register": local_rows,
            "parents": full, "parents_without_fuel": material,
            "reduced_parents": reduced, "reduced_parents_without_fuel": local_reduced,
            "fuel_only_direct_parents": fuel_edges}
