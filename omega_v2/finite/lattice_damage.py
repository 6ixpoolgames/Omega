"""Native bond-failure observations; no changes to the 2D chemical generator."""

import numpy as np

from omega_v2.finite.lattice_chemistry import Event, State


def state_from_record(record):
    return State([tuple(p) for p in record["positions"]], list(record["internal"]),
                 {tuple(b) for b in record["bonds"]}, record["fuel"])


def event_from_record(record):
    _, kind, members, direction, catalyst, rate = record
    return Event(kind, tuple(members), rate, tuple(direction), tuple(catalyst))


def state_at(model, trajectory, time):
    state = state_from_record(trajectory["initial"])
    for record in trajectory["events"]:
        if record[0] > time:
            break
        model.apply(state, event_from_record(record))
    return state


def connected(state, pair, exclude_pair=False):
    start, target = pair
    edges = state.bonds - {pair} if exclude_pair else state.bonds
    seen, stack = {start}, [start]
    while stack:
        i = stack.pop()
        for a, b in edges:
            j = b if a == i else a if b == i else None
            if j is not None and j not in seen:
                if j == target:
                    return True
                seen.add(j)
                stack.append(j)
    return False


def native_failure(model, before, seed, templates_only=False):
    """Sample an edge conditional on a thermal break at this state.

    Keep the state's total hazard for flux-weighted averaging across states.
    Sampling one edge uniformly instead would define a different experiment.
    """
    candidates = [e for e in model.events(before)
                  if e.kind == "thermal" and e.members in before.bonds]
    all_hazard = sum(e.rate for e in candidates)
    if templates_only:
        active = {e.catalyst for e in model.events(before)
                  if e.kind == "catalytic" and e.members not in before.bonds}
        candidates = [e for e in candidates if e.members in active]
    total = sum(e.rate for e in candidates)
    if total == 0:
        return {"total_hazard": 0.0, "all_thermal_failure_hazard": all_hazard, "selected": None}
    weights = np.array([e.rate for e in candidates]) / total
    e = candidates[int(np.random.default_rng(seed).choice(len(candidates), p=weights))]
    after = before.copy()
    model.apply(after, e)
    model.validate(after)
    lost_targets = [x for x in model.events(before)
                    if x.kind == "catalytic" and x.catalyst == e.members
                    and x.members not in before.bonds]
    return {"total_hazard": total, "all_thermal_failure_hazard": all_hazard,
            "selected": e, "after": after,
            "edge_probability_given_state": e.rate / total,
            "is_bridge": not connected(after, e.members),
            "template_targets_before": len(lost_targets),
            "lost_template_formation_rate": sum(x.rate for x in lost_targets),
            "energy_change": model.energy(after) - model.energy(before)}


def probe_coordinates(model, before, pair):
    side = model.p.side
    cells = [(x, y) for x in range(side) for y in range(side)]
    edges = [(a, b) for a in cells for b in ((a[0] + 1, a[1]), (a[0], a[1] + 1))
             if b[0] < side and b[1] < side]
    endpoints = [before.positions[i] for i in pair]
    distances = [min(abs(x - a) + abs(y - b) for a, b in endpoints) for x, y in cells]
    cell_index = {pos: i for i, pos in enumerate(cells)}
    edge_distances = [min(distances[cell_index[a]], distances[cell_index[b]]) for a, b in edges]
    return {"cells": cells, "edges": edges, "cell_distances": distances,
            "edge_distances": edge_distances}


def projection(model, state, pair, coordinates):
    occupied = {pos: state.internal[i] + 1 for i, pos in enumerate(state.positions)}
    # Each cell reads empty/concealed/exposed, never a particle identity.
    cell_features = np.eye(3)[[occupied.get(pos, 0) for pos in coordinates["cells"]]]
    physical_bonds = {frozenset((state.positions[i], state.positions[j])) for i, j in state.bonds}
    edge_features = np.array([frozenset(e) in physical_bonds for e in coordinates["edges"]], float)
    bound = pair in state.bonds
    linked = connected(state, pair)
    alternate = connected(state, pair, exclude_pair=True)
    events = model.events(state)
    fresh_formations = [e for e in events if e.kind == "catalytic"
                        and e.members not in state.bonds and e.members != pair]
    return {"cells": cell_features, "edges": edge_features,
            "readouts": {"original_bond_present": float(bound),
                         "endpoints_connected": float(linked),
                         "alternate_path_present": float(alternate),
                         "bonds_other_than_original": len(state.bonds) - int(bound),
                         "fuel": state.fuel,
                         "other_catalytic_formation_rate": sum(e.rate for e in fresh_formations)},
            "joint_recovery_state": int(bound) + 2 * int(alternate)}


def observe(model, trajectory, pair, coordinates, cuts):
    state = state_from_record(trajectory["initial"])
    cursor, paired_forms, first_bond, first_connection = 0, 0, None, None
    first_loss_after_bond, ever_formed = None, False
    if pair in state.bonds:
        first_bond, ever_formed = 0.0, True
    if connected(state, pair):
        first_connection = 0.0
    out = []
    for time in cuts:
        while cursor < len(trajectory["events"]) and trajectory["events"][cursor][0] <= time:
            record = trajectory["events"][cursor]
            e = event_from_record(record)
            was_bound = pair in state.bonds
            if e.kind == "catalytic" and e.members == pair and not was_bound:
                paired_forms += 1
            model.apply(state, e)
            bound = pair in state.bonds
            if bound and first_bond is None:
                first_bond, ever_formed = record[0], True
            if was_bound and not bound and ever_formed and first_loss_after_bond is None:
                first_loss_after_bond = record[0]
            if first_connection is None and connected(state, pair):
                first_connection = record[0]
            cursor += 1
        view = projection(model, state, pair, coordinates)
        snapshot = trajectory["snapshots"][len(out)]
        view["readouts"].update({
            "ever_original_bond": float(first_bond is not None),
            "ever_connected": float(first_connection is not None),
            "lost_again_after_bond": float(first_loss_after_bond is not None),
            "net_fuel_used": trajectory["initial"]["fuel"] - state.fuel,
            "other_catalytic_formations": snapshot["catalytic_forward"] - paired_forms,
        })
        out.append(view)
    return out


def squared_response(x, y):
    """Unbiased squared difference of expected features, using independent arms.

    Negative estimates are sampling fluctuation and are retained. This is a
    diagnostic of the supplied projections, not total variation or lushness.
    """
    x, y = np.asarray(x), np.asarray(y)
    return float(np.sum((x.mean(axis=0) - y.mean(axis=0)) ** 2)
                 - np.sum(x.var(axis=0, ddof=1)) / len(x)
                 - np.sum(y.var(axis=0, ddof=1)) / len(y))
