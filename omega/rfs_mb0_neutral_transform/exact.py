from __future__ import annotations

from .extractors import Candidate, continuity_predicate
from .substrate import (
    NONPHASE_COORDS,
    NeutralSystem,
    State,
    block_relation_changed,
    relation_mu_changed,
    relation_nu_changed,
)

HORIZONS = (0, 1, 2, 4, 8, 12, 16)


def reachable(
    system: NeutralSystem,
    start: State,
    horizon: int,
    predicate=None,
) -> frozenset[State]:
    if predicate is not None and not predicate(start):
        return frozenset()
    seen = {start}
    frontier = {start}
    for _ in range(horizon):
        next_frontier: set[State] = set()
        for state in frontier:
            for target in system.edges[state]:
                if predicate is None or predicate(target):
                    next_frontier.add(target)
        next_frontier -= seen
        if not next_frontier:
            break
        seen.update(next_frontier)
        frontier = next_frontier
    return frozenset(seen)


def exact_frontier(
    system: NeutralSystem,
    start: State,
    horizon: int,
    predicate=None,
) -> frozenset[State]:
    if predicate is not None and not predicate(start):
        return frozenset()
    frontier = {start}
    for _ in range(horizon):
        next_frontier: set[State] = set()
        for state in frontier:
            for target in system.edges[state]:
                if predicate is None or predicate(target):
                    next_frontier.add(target)
        frontier = next_frontier
        if not frontier:
            break
    return frozenset(frontier)


def filtration_rows(system: NeutralSystem, mu: Candidate, nu: Candidate) -> list[dict[str, int | float | str]]:
    pred_mu = continuity_predicate(mu, system.initial_state)
    pred_nu = continuity_predicate(nu, system.initial_state)
    pred_joint = lambda state: pred_mu(state) and pred_nu(state)
    rows: list[dict[str, int | float | str]] = []
    for horizon in HORIZONS:
        f_mu = reachable(system, system.initial_state, horizon, pred_mu)
        f_nu = reachable(system, system.initial_state, horizon, pred_nu)
        f_joint = reachable(system, system.initial_state, horizon, pred_joint)
        exact_mu = exact_frontier(system, system.initial_state, horizon, pred_mu)
        exact_nu = exact_frontier(system, system.initial_state, horizon, pred_nu)
        exact_joint = exact_frontier(system, system.initial_state, horizon, pred_joint)
        endpoint_audit = endpoint_audit_metrics(system, mu, nu, exact_joint)
        min_singleton = min(len(f_mu), len(f_nu))
        exact_min_singleton = min(len(exact_mu), len(exact_nu))
        rows.append(
            {
                "H": horizon,
                "mu_count": len(f_mu),
                "nu_count": len(f_nu),
                "joint_count": len(f_joint),
                "exact_mu_count": len(exact_mu),
                "exact_nu_count": len(exact_nu),
                "exact_joint_count": len(exact_joint),
                "joint_over_min": len(f_joint) / max(1, min_singleton),
                "exact_joint_over_min": len(exact_joint) / max(1, exact_min_singleton),
                "mu_persists": int(bool(f_mu)),
                "nu_persists": int(bool(f_nu)),
                "joint_persists": int(bool(f_joint)),
                "exact_joint_persists": int(bool(exact_joint)),
                **endpoint_audit,
            }
        )
    geometry = geometry_fields(rows)
    transition = transition_delta_metrics(system, mu, nu)
    for row in rows:
        row.update(geometry)
        row.update(transition)
        row["result_bin"] = result_bin(system.family, row)
    return rows


def endpoint_audit_metrics(
    system: NeutralSystem, mu: Candidate, nu: Candidate, endpoints: frozenset[State]
) -> dict[str, int | float]:
    initial = system.initial_state
    pred_mu = continuity_predicate(mu, initial)
    pred_nu = continuity_predicate(nu, initial)
    if not endpoints:
        return {
            "endpoint_count": 0,
            "mean_changed_coordinate_count": 0.0,
            "mean_changed_nonphase_coordinate_count": 0.0,
            "mean_changed_mu_block_count": 0.0,
            "mean_changed_nu_block_count": 0.0,
            "mean_changed_outside_block_count": 0.0,
            "mu_signature_changed_fraction": 0.0,
            "nu_signature_changed_fraction": 0.0,
            "mu_exits_band_fraction": 0.0,
            "nu_exits_band_fraction": 0.0,
            "joint_exits_band_fraction": 0.0,
            "phase_only_change_fraction": 0.0,
            "nonphase_change_fraction": 0.0,
            "block_relation_changed_fraction": 0.0,
        }
    changed_counts = [_changed_coordinate_count(initial, endpoint, range(len(initial))) for endpoint in endpoints]
    changed_nonphase = [_changed_coordinate_count(initial, endpoint, range(NONPHASE_COORDS)) for endpoint in endpoints]
    changed_mu = [_changed_coordinate_count(initial, endpoint, mu.coordinate_block) for endpoint in endpoints]
    changed_nu = [_changed_coordinate_count(initial, endpoint, nu.coordinate_block) for endpoint in endpoints]
    union_block = set(mu.coordinate_block) | set(nu.coordinate_block)
    outside = [index for index in range(NONPHASE_COORDS) if index not in union_block]
    changed_outside = [_changed_coordinate_count(initial, endpoint, outside) for endpoint in endpoints]
    return {
        "endpoint_count": len(endpoints),
        "mean_changed_coordinate_count": _mean(changed_counts),
        "mean_changed_nonphase_coordinate_count": _mean(changed_nonphase),
        "mean_changed_mu_block_count": _mean(changed_mu),
        "mean_changed_nu_block_count": _mean(changed_nu),
        "mean_changed_outside_block_count": _mean(changed_outside),
        "mu_signature_changed_fraction": _rate(relation_mu_changed(initial, endpoint) for endpoint in endpoints),
        "nu_signature_changed_fraction": _rate(relation_nu_changed(initial, endpoint) for endpoint in endpoints),
        "mu_exits_band_fraction": _rate(not pred_mu(endpoint) for endpoint in endpoints),
        "nu_exits_band_fraction": _rate(not pred_nu(endpoint) for endpoint in endpoints),
        "joint_exits_band_fraction": _rate((not pred_mu(endpoint)) or (not pred_nu(endpoint)) for endpoint in endpoints),
        "phase_only_change_fraction": _rate(_changed_coordinate_count(initial, endpoint, range(NONPHASE_COORDS)) == 0 and endpoint[-1] != initial[-1] for endpoint in endpoints),
        "nonphase_change_fraction": _rate(_changed_coordinate_count(initial, endpoint, range(NONPHASE_COORDS)) > 0 for endpoint in endpoints),
        "block_relation_changed_fraction": _rate(block_relation_changed(initial, endpoint) for endpoint in endpoints),
    }


def geometry_fields(rows: list[dict[str, int | float | str]]) -> dict[str, int | float]:
    ordered = sorted(rows, key=lambda row: int(row["H"]))

    def first(metric: str) -> int:
        for row in ordered:
            if int(row[metric]) > 0:
                return int(row["H"])
        return -1

    first_mu = first("mu_count")
    first_nu = first("nu_count")
    first_joint = first("joint_count")
    first_nonphase_joint = first("nonphase_change_fraction")
    first_exact_mu = first("exact_mu_count")
    first_exact_nu = first("exact_nu_count")
    first_exact_joint = first("exact_joint_count")
    joint_counts = [(int(row["H"]), int(row["joint_count"])) for row in ordered]
    return {
        "first_mu_H": first_mu,
        "first_nu_H": first_nu,
        "first_joint_H": first_joint,
        "first_exact_mu_H": first_exact_mu,
        "first_exact_nu_H": first_exact_nu,
        "first_exact_joint_H": first_exact_joint,
        "first_nonphase_joint_H": first_nonphase_joint,
        "joint_delay": _delay(first_joint, max(first_mu, first_nu)),
        "exact_joint_delay": _delay(first_exact_joint, max(first_exact_mu, first_exact_nu)),
        "joint_flatline_flag": int(first_joint >= 0 and first_nonphase_joint < 0),
        "joint_saturates_early_flag": int(_last_change_h(joint_counts) <= 2 and int(ordered[-1]["joint_count"]) > 0),
        "last_joint_change_H": _last_change_h(joint_counts),
    }


def transition_delta_metrics(system: NeutralSystem, mu: Candidate, nu: Candidate) -> dict[str, int | float]:
    horizon = max(HORIZONS)
    remaining = horizon - 1
    pred_mu = continuity_predicate(mu, system.initial_state)
    pred_nu = continuity_predicate(nu, system.initial_state)
    pred_joint = lambda state: pred_mu(state) and pred_nu(state)
    base_mu = len(reachable(system, system.initial_state, horizon, pred_mu))
    base_nu = len(reachable(system, system.initial_state, horizon, pred_nu))
    base_joint = len(reachable(system, system.initial_state, horizon, pred_joint))
    deltas = []
    for target in system.edges[system.initial_state]:
        deltas.append(
            (
                len(reachable(system, target, remaining, pred_mu)) - base_mu,
                len(reachable(system, target, remaining, pred_nu)) - base_nu,
                len(reachable(system, target, remaining, pred_joint)) - base_joint,
            )
        )
    if not deltas:
        return {
            "local_mu_persists_joint_contracts_rate": 0.0,
            "local_nu_persists_joint_contracts_rate": 0.0,
            "min_joint_delta": 0,
        }
    return {
        "local_mu_persists_joint_contracts_rate": _rate(mu_delta >= 0 and joint_delta < 0 for mu_delta, _nu_delta, joint_delta in deltas),
        "local_nu_persists_joint_contracts_rate": _rate(nu_delta >= 0 and joint_delta < 0 for _mu_delta, nu_delta, joint_delta in deltas),
        "min_joint_delta": min(joint_delta for _mu_delta, _nu_delta, joint_delta in deltas),
    }


def result_bin(family: str, row: dict[str, int | float | str]) -> str:
    if family == "phase_cycle_control" and float(row["phase_only_change_fraction"]) > 0:
        return "phase_only_persistence"
    if family == "fixed_point_control" and int(row["joint_saturates_early_flag"]):
        return "fixed_point_persistence"
    if family == "equivalence_permissive_control":
        return "permissive_equivalence_artifact"
    if family == "equivalence_strict_control":
        return "strict_equivalence_artifact"
    if family in {"random_transform_control", "degree_preserving_transform_control"} and float(row["joint_over_min"]) < 0.75:
        return "random_control_mimic"
    if float(row["local_mu_persists_joint_contracts_rate"]) > 0:
        return "local_mu_persists_joint_contracts"
    if float(row["local_nu_persists_joint_contracts_rate"]) > 0:
        return "local_nu_persists_joint_contracts"
    if int(row["mu_persists"]) and int(row["nu_persists"]) and not int(row["joint_persists"]):
        return "singleton_overcall"
    if float(row["joint_over_min"]) < 0.75:
        return "pairwise_contracted"
    if int(row["joint_persists"]):
        return "pair_persists"
    if int(row["mu_persists"]) or int(row["nu_persists"]):
        return "singleton_persists"
    return "no_persistence"


def _changed_coordinate_count(initial: State, endpoint: State, coords: Iterable[int]) -> int:
    return sum(1 for coord in coords if initial[coord] != endpoint[coord])


def _mean(values: list[int | float]) -> float:
    return sum(float(value) for value in values) / len(values) if values else 0.0


def _rate(values: Iterable[bool]) -> float:
    items = list(values)
    return sum(1 for item in items if item) / len(items) if items else 0.0


def _delay(first_joint: int, first_singleton: int) -> int:
    if first_joint < 0 or first_singleton < 0:
        return -1
    return first_joint - first_singleton


def _last_change_h(series: list[tuple[int, int]]) -> int:
    last_h = series[0][0]
    last_value = series[0][1]
    for horizon, value in series[1:]:
        if value != last_value:
            last_h = horizon
            last_value = value
    return last_h

