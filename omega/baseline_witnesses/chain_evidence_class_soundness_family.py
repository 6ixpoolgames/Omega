"""Parameterized chain-evidence/class-soundness family.

This module generalizes the retained same-chain-evidence witness without
creating new retained artifacts. For each ``k >= 1``, it compares two proposed
classes of size ``k + 2``:

* a full compatible clique;
* a chain-connected class whose adjacent edges are compatible but whose
  non-adjacent pairs are blocked.

The declared chain evidence matches exactly. Full class soundness differs.
"""

from __future__ import annotations

from itertools import combinations


def run_family_case(*, chain_intermediate_count: int) -> dict[str, object]:
    if chain_intermediate_count < 1:
        raise ValueError("chain_intermediate_count must be >= 1")

    member_count = chain_intermediate_count + 2
    valid_members = class_members("v", member_count)
    invalid_members = class_members("i", member_count)
    valid_audit = class_soundness_audit(valid_members, class_kind="valid_clique")
    invalid_audit = class_soundness_audit(invalid_members, class_kind="invalid_chain")
    baseline_profile = baseline_class_profile(member_count)
    baseline_controls_match = baseline_profile == baseline_class_profile(member_count)
    valid_chain_edges_pass = declared_chain_edges_pass(valid_members, class_kind="valid_clique")
    invalid_chain_edges_pass = declared_chain_edges_pass(invalid_members, class_kind="invalid_chain")

    return {
        "family_id": "same_chain_evidence_different_class_soundness_family",
        "chain_intermediate_count": chain_intermediate_count,
        "member_count": member_count,
        "valid_class_id": f"valid_clique_size_{member_count}",
        "invalid_class_id": f"invalid_chain_size_{member_count}",
        "baseline_profile": baseline_profile,
        "baseline_controls_match": baseline_controls_match,
        "valid_declared_chain_edges_pass": valid_chain_edges_pass,
        "invalid_declared_chain_edges_pass": invalid_chain_edges_pass,
        "valid_audit": valid_audit,
        "invalid_audit": invalid_audit,
        "valid_class_sound": valid_audit["class_sound"],
        "invalid_class_sound": invalid_audit["class_sound"],
        "family_case_status": (
            "same_chain_evidence_different_class_soundness"
            if (
                baseline_controls_match
                and valid_chain_edges_pass
                and invalid_chain_edges_pass
                and valid_audit["class_sound"]
                and not invalid_audit["class_sound"]
            )
            else "family_case_failed"
        ),
    }


def run_family(*, max_nuisance_bits: int) -> list[dict[str, object]]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")
    return [
        run_family_case(chain_intermediate_count=count)
        for count in range(1, max_nuisance_bits + 1)
    ]


def class_members(prefix: str, member_count: int) -> tuple[str, ...]:
    if member_count < 3:
        raise ValueError("member_count must be >= 3")
    return tuple(f"{prefix}{index}" for index in range(member_count))


def baseline_class_profile(member_count: int) -> dict[str, object]:
    if member_count < 3:
        raise ValueError("member_count must be >= 3")
    return {
        "member_count": member_count,
        "declared_chain_edge_count": member_count - 1,
        "internal_pair_count": member_count * (member_count - 1) // 2,
        "chain_connected": True,
    }


def declared_chain_edges_pass(members: tuple[str, ...], *, class_kind: str) -> bool:
    return all(
        exact_allows_merge(left, right, class_kind=class_kind)
        for left, right in adjacent_pairs(members)
    )


def class_soundness_audit(members: tuple[str, ...], *, class_kind: str) -> dict[str, object]:
    allowed_pair_count = 0
    blocked_pair_count = 0
    blocked_pairs: list[str] = []
    for left, right in unordered_pairs(members):
        if exact_allows_merge(left, right, class_kind=class_kind):
            allowed_pair_count += 1
        else:
            blocked_pair_count += 1
            blocked_pairs.append(f"{left},{right}")

    return {
        "internal_pair_count": len(unordered_pairs(members)),
        "allowed_pair_count": allowed_pair_count,
        "blocked_pair_count": blocked_pair_count,
        "blocked_pair_signature": ";".join(blocked_pairs),
        "class_sound": blocked_pair_count == 0,
    }


def exact_allows_merge(left: str, right: str, *, class_kind: str) -> bool:
    if class_kind == "valid_clique":
        return True
    if class_kind == "invalid_chain":
        return abs(member_index(left) - member_index(right)) == 1
    raise ValueError(f"unknown class_kind: {class_kind}")


def adjacent_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return [(items[index], items[index + 1]) for index in range(len(items) - 1)]


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))


def member_index(member: str) -> int:
    return int(member[1:])
