"""Finite colonization-axis discovery harness.

This module implements the preregistered v0 witness search for a possible
cross-scale viable-refinement coordinate. It is a finite audit harness, not a
theory of lushness, value, agency, identity, or Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from typing import Any


HORIZONS = (1, 2, 3)
LABELS = ("a", "b")
PROTOCOL_DOC = "docs/research_notes/omega_theory/colonization_axis_protocol_v0.md"


@dataclass(frozen=True)
class FiniteSystem:
    system_id: str
    states: tuple[str, ...]
    start: str
    viable: frozenset[str]
    transitions: dict[tuple[str, str], str]
    declared_joint_behavior: str = "neutral"


Partition = tuple[tuple[str, ...], ...]
Chain = tuple[Partition, ...]


def branching_system() -> FiniteSystem:
    states = ("b00", "b01", "b10", "b11")
    transitions = {
        ("b00", "a"): "b01",
        ("b01", "a"): "b00",
        ("b10", "a"): "b11",
        ("b11", "a"): "b10",
        ("b00", "b"): "b10",
        ("b10", "b"): "b00",
        ("b01", "b"): "b11",
        ("b11", "b"): "b01",
    }
    return FiniteSystem(
        system_id="branching_B",
        states=states,
        start="b00",
        viable=frozenset(states),
        transitions=transitions,
        declared_joint_behavior="joint_neutral",
    )


def basin_system() -> FiniteSystem:
    states = ("f0", "f1", "f2", "f3")
    transitions = {
        ("f0", "a"): "f1",
        ("f1", "a"): "f2",
        ("f2", "a"): "f3",
        ("f3", "a"): "f0",
        ("f0", "b"): "f2",
        ("f2", "b"): "f1",
        ("f1", "b"): "f3",
        ("f3", "b"): "f0",
    }
    return FiniteSystem(
        system_id="basin_F",
        states=states,
        start="f0",
        viable=frozenset(states),
        transitions=transitions,
        declared_joint_behavior="joint_neutral",
    )


def branching_joint_variant() -> FiniteSystem:
    base = branching_system()
    return FiniteSystem(
        system_id="branching_B_joint_variant",
        states=base.states,
        start=base.start,
        viable=base.viable,
        transitions=base.transitions,
        declared_joint_behavior="joint_contracts",
    )


def control_panel(system: FiniteSystem) -> dict[str, Any]:
    word_counts = {str(h): viable_word_count(system, h) for h in HORIZONS}
    h3_count = word_counts[str(max(HORIZONS))]
    return {
        "system_id": system.system_id,
        "viable_state_count": len(system.viable),
        "start_in_corridor": system.start in system.viable,
        "viable_word_counts": word_counts,
        "recurrence_class_count": recurrence_class_count(system),
        "own_maintenance_score": own_maintenance_score(system),
        "entropy_proxy_h3": round(math.log2(max(1, h3_count)), 6),
        "leading_lambda_proxy": leading_lambda_proxy(system),
    }


def viable_word_count(system: FiniteSystem, horizon: int) -> int:
    count = 0
    for word in itertools.product(LABELS, repeat=horizon):
        state = system.start
        ok = state in system.viable
        for label in word:
            state = system.transitions[(state, label)]
            ok = ok and state in system.viable
        if ok:
            count += 1
    return count


def recurrence_class_count(system: FiniteSystem) -> int:
    viable_states = set(system.viable)
    adjacency = {
        state: {
            system.transitions[(state, label)]
            for label in LABELS
            if system.transitions[(state, label)] in viable_states
        }
        for state in viable_states
    }
    remaining = set(viable_states)
    classes = 0
    while remaining:
        seed = next(iter(remaining))
        forward = reachable(seed, adjacency)
        reverse_graph = {
            state: {src for src, tgts in adjacency.items() if state in tgts}
            for state in viable_states
        }
        backward = reachable(seed, reverse_graph)
        scc = forward & backward
        classes += 1
        remaining -= scc
    return classes


def reachable(start: str, adjacency: dict[str, set[str]]) -> set[str]:
    seen = {start}
    frontier = [start]
    while frontier:
        state = frontier.pop()
        for nxt in adjacency[state]:
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def own_maintenance_score(system: FiniteSystem) -> int:
    return sum(
        1
        for state in system.viable
        for label in LABELS
        if system.transitions[(state, label)] == state
    )


def leading_lambda_proxy(system: FiniteSystem) -> str:
    row_sums = {
        sum(1 for label in LABELS if system.transitions[(state, label)] in system.viable)
        for state in system.viable
    }
    if len(row_sums) == 1:
        return str(next(iter(row_sums)))
    return "not_computed"


def set_partitions(items: tuple[str, ...]) -> list[Partition]:
    if not items:
        return [tuple()]
    first, *rest = items
    rest_partitions = set_partitions(tuple(rest))
    out: list[Partition] = []
    for partition in rest_partitions:
        out.append(normalize_partition(((first,), *partition)))
        for idx in range(len(partition)):
            blocks = [tuple(block) for block in partition]
            blocks[idx] = tuple(sorted((*blocks[idx], first)))
            out.append(normalize_partition(tuple(blocks)))
    unique = {partition_signature(partition): partition for partition in out}
    return [unique[key] for key in sorted(unique)]


def normalize_partition(partition: Partition) -> Partition:
    blocks = [tuple(sorted(block)) for block in partition if block]
    return tuple(sorted(blocks, key=lambda block: (block[0], len(block), block)))


def partition_signature(partition: Partition) -> str:
    return "|".join(",".join(block) for block in normalize_partition(partition))


def cell_count_signature(chain: Chain) -> tuple[int, ...]:
    return tuple(len(level) for level in chain)


def certified_partitions(system: FiniteSystem) -> list[Partition]:
    viable_items = tuple(sorted(system.viable))
    return [
        partition
        for partition in set_partitions(viable_items)
        if is_certified_partition(system, partition)
    ]


def is_certified_partition(system: FiniteSystem, partition: Partition) -> bool:
    cell_by_state = {
        state: idx
        for idx, block in enumerate(partition)
        for state in block
    }
    if set(cell_by_state) != set(system.viable):
        return False
    for block in partition:
        for label in LABELS:
            target_cells = {
                cell_by_state[system.transitions[(state, label)]]
                for state in block
            }
            if len(target_cells) != 1:
                return False
    return True


def refines(fine: Partition, coarse: Partition) -> bool:
    coarse_cell_by_state = {
        state: idx
        for idx, block in enumerate(coarse)
        for state in block
    }
    for block in fine:
        containing = {coarse_cell_by_state[state] for state in block}
        if len(containing) != 1:
            return False
    return True


def certified_chains(system: FiniteSystem) -> list[Chain]:
    partitions = certified_partitions(system)
    chains: list[Chain] = []
    for length in range(2, len(system.viable) + 1):
        for chain in itertools.permutations(partitions, length):
            counts = cell_count_signature(chain)
            if counts != tuple(sorted(counts)) or len(set(counts)) != len(counts):
                continue
            if all(refines(chain[idx + 1], chain[idx]) for idx in range(len(chain) - 1)):
                chains.append(chain)
    unique = {chain_signature(chain): chain for chain in chains}
    return [unique[key] for key in sorted(unique)]


def chain_signature(chain: Chain) -> str:
    return " -> ".join(partition_signature(level) for level in chain)


def profile_summary(system: FiniteSystem) -> dict[str, Any]:
    chains = certified_chains(system)
    signatures = sorted(cell_count_signature(chain) for chain in chains)
    return {
        "system_id": system.system_id,
        "certified_partition_count": len(certified_partitions(system)),
        "certified_chain_count": len(chains),
        "chain_cell_count_signatures": ["-".join(map(str, sig)) for sig in signatures],
        "max_chain_depth": max((len(sig) for sig in signatures), default=0),
        "has_two_level_surplus_chain": (1, 2, 4) in signatures,
    }


def colonization_refines(left: FiniteSystem, right: FiniteSystem) -> dict[str, Any]:
    left_chains = certified_chains(left)
    right_chains = certified_chains(right)
    for l_chain in left_chains:
        for r_chain in right_chains:
            match = chain_surplus_match(cell_count_signature(l_chain), cell_count_signature(r_chain))
            if match["refines"]:
                return {
                    "left": left.system_id,
                    "right": right.system_id,
                    "refines": True,
                    "left_signature": "-".join(map(str, cell_count_signature(l_chain))),
                    "right_signature": "-".join(map(str, cell_count_signature(r_chain))),
                    **match,
                }
    return {
        "left": left.system_id,
        "right": right.system_id,
        "refines": False,
        "left_signature": "",
        "right_signature": "",
        "strict_surplus": False,
        "matched_levels": [],
    }


def chain_surplus_match(left_counts: tuple[int, ...], right_counts: tuple[int, ...]) -> dict[str, Any]:
    if not left_counts or not right_counts:
        return {"refines": False, "strict_surplus": False, "matched_levels": []}
    if left_counts[0] != right_counts[0] or left_counts[-1] != right_counts[-1]:
        return {"refines": False, "strict_surplus": False, "matched_levels": []}
    matched: list[dict[str, int]] = []
    right_idx = 0
    strict = False
    for left_idx, left_count in enumerate(left_counts):
        while right_idx + 1 < len(right_counts) and right_counts[right_idx + 1] <= left_count:
            right_idx += 1
        right_count = right_counts[right_idx]
        if left_count < right_count:
            return {"refines": False, "strict_surplus": False, "matched_levels": matched}
        if left_count > right_count:
            strict = True
        matched.append(
            {
                "left_level": left_idx,
                "left_cells": left_count,
                "right_level": right_idx,
                "right_cells": right_count,
            }
        )
    hit_right = {row["right_level"] for row in matched}
    return {
        "refines": hit_right == set(range(len(right_counts))) and strict,
        "strict_surplus": strict,
        "matched_levels": matched,
    }


def control_panels_match(left: FiniteSystem, right: FiniteSystem) -> bool:
    left_panel = {k: v for k, v in control_panel(left).items() if k != "system_id"}
    right_panel = {k: v for k, v in control_panel(right).items() if k != "system_id"}
    return left_panel == right_panel


def scalar_summary(counts: tuple[int, ...]) -> dict[str, Any]:
    ratios: list[float] = []
    for before, after in zip(counts, counts[1:]):
        ratios.append(after / before if before else math.inf)
    return {
        "level_count": len(counts),
        "max_branching_ratio": max(ratios) if ratios else 0.0,
    }


def scalar_shadow_check() -> dict[str, Any]:
    left = (1, 3, 6)
    right = (1, 2, 6)
    match = chain_surplus_match(left, right)
    return {
        "left_signature": "-".join(map(str, left)),
        "right_signature": "-".join(map(str, right)),
        "left_scalar": scalar_summary(left),
        "right_scalar": scalar_summary(right),
        "scalar_equal": scalar_summary(left) == scalar_summary(right),
        "order_separates": match["refines"],
        "read": "chain order separates these signatures while level count and max branching ratio match",
    }


def converse_witness_attempt() -> dict[str, Any]:
    left = branching_system()
    right = branching_joint_variant()
    return {
        "left": left.system_id,
        "right": right.system_id,
        "same_control_panel": control_panels_match(left, right),
        "same_colonization_profile": profile_summary(left)["chain_cell_count_signatures"]
        == profile_summary(right)["chain_cell_count_signatures"],
        "joint_behavior_differs": left.declared_joint_behavior != right.declared_joint_behavior,
        "read": "same colonization profile does not determine a declared joint-behavior field",
    }


def colonization_axis_summary() -> dict[str, Any]:
    branching = branching_system()
    basin = basin_system()
    controls_match = control_panels_match(branching, basin)
    refinement = colonization_refines(branching, basin)
    reverse = colonization_refines(basin, branching)
    scalar_shadow = scalar_shadow_check()
    converse = converse_witness_attempt()
    lens_audit = {
        "registered_chains_certified": all(
            is_certified_partition(branching, level)
            for chain in certified_chains(branching)
            for level in chain
        )
        and all(
            is_certified_partition(basin, level)
            for chain in certified_chains(basin)
            for level in chain
        ),
        "strict_surplus_has_chain_transport": refinement["refines"],
        "presentation_relative_caveat": (
            "v0 audits registered certified chains; it does not prove a global lens-invariance theorem"
        ),
    }
    gauntlet_passes = (
        lens_audit["registered_chains_certified"]
        and lens_audit["strict_surplus_has_chain_transport"]
        and converse["same_colonization_profile"]
        and converse["joint_behavior_differs"]
        and scalar_shadow["scalar_equal"]
        and scalar_shadow["order_separates"]
    )
    verdict = "separated" if controls_match and refinement["refines"] and gauntlet_passes else "reduces-or-ill-posed"
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": verdict,
        "candidate_pair": {
            "left": branching.system_id,
            "right": basin.system_id,
            "state_bound_satisfied": len(branching.states) <= 12 and len(basin.states) <= 12,
            "control_panel_equal": controls_match,
            "left_control_panel": control_panel(branching),
            "right_control_panel": control_panel(basin),
            "left_profile": profile_summary(branching),
            "right_profile": profile_summary(basin),
            "left_refines_right": refinement,
            "right_refines_left": reverse,
        },
        "demotion_gauntlet": {
            "lens_presentation_audit": lens_audit,
            "converse_witness_attempt": converse,
            "scalar_shadow_check": scalar_shadow,
            "gauntlet_passes": gauntlet_passes,
        },
        "not_claimed": [
            "lushness",
            "value",
            "moral standing",
            "agency",
            "identity",
            "global lens invariance theorem",
            "Omega validation",
        ],
    }


def control_panel_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    pair = summary["candidate_pair"]
    left = pair["left_control_panel"]
    right = pair["right_control_panel"]
    rows: list[dict[str, Any]] = []
    for key in left:
        if key == "system_id":
            continue
        rows.append(
            {
                "metric": key,
                "left": left[key],
                "right": right[key],
                "relation": "equal",
                "holds": left[key] == right[key],
            }
        )
    return rows


def profile_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    pair = summary["candidate_pair"]
    return [
        {
            "system_id": pair["left"],
            **pair["left_profile"],
        },
        {
            "system_id": pair["right"],
            **pair["right_profile"],
        },
    ]
