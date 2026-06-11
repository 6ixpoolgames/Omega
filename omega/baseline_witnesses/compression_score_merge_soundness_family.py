"""Parameterized compression-score/merge-soundness family.

This module generalizes the retained same-compression-score witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a two-class abstraction keyed by declared bit ``a`` with two-class
abstractions keyed by each nuisance bit ``n_i``.

The compression summaries match exactly. Merge soundness differs because the
declared exact profile allows merges only when fragments share ``a``.
"""

from __future__ import annotations

from itertools import combinations


Assignment = dict[str, str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    fragments = state_space(nuisance_bit_count)
    sound = declared_abstraction(fragments)
    unsound = nuisance_abstraction(fragments, nuisance_index)
    sound_profile = compression_profile(sound, fragments)
    unsound_profile = compression_profile(unsound, fragments)
    sound_audit = merge_soundness_audit(sound, fragments)
    unsound_audit = merge_soundness_audit(unsound, fragments)

    compression_scores_match = (
        sound_profile["simple_compression_score"]
        == unsound_profile["simple_compression_score"]
    )
    sound_merge_sound = sound_audit["unsound_merge_count"] == 0
    unsound_merge_sound = unsound_audit["unsound_merge_count"] == 0

    return {
        "family_id": "same_compression_score_different_merge_soundness_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "fragment_count": len(fragments),
        "sound_abstraction_id": "classes_by_declared_a",
        "unsound_abstraction_id": f"classes_by_nuisance_n{nuisance_index + 1}",
        "exact_profile_rule": "same declared a allows merge; different declared a blocks merge",
        "sound_profile": sound_profile,
        "unsound_profile": unsound_profile,
        "compression_scores_match": compression_scores_match,
        "sound_audit": sound_audit,
        "unsound_audit": unsound_audit,
        "sound_abstraction_merge_sound": sound_merge_sound,
        "unsound_abstraction_merge_sound": unsound_merge_sound,
        "family_case_status": (
            "same_compression_score_different_merge_soundness"
            if compression_scores_match and sound_merge_sound and not unsound_merge_sound
            else "family_case_failed"
        ),
    }


def run_family(*, max_nuisance_bits: int) -> list[dict[str, object]]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")
    return [
        run_family_case(nuisance_bit_count=count, nuisance_index=index)
        for count in range(1, max_nuisance_bits + 1)
        for index in range(count)
    ]


def state_space(nuisance_bit_count: int) -> tuple[str, ...]:
    if nuisance_bit_count < 1:
        raise ValueError("nuisance_bit_count must be >= 1")
    bit_count = 1 + nuisance_bit_count
    return tuple(format(value, f"0{bit_count}b") for value in range(2**bit_count))


def declared_abstraction(fragments: tuple[str, ...]) -> Assignment:
    return {fragment: f"A{fragment[0]}" for fragment in fragments}


def nuisance_abstraction(fragments: tuple[str, ...], nuisance_index: int) -> Assignment:
    if not fragments:
        raise ValueError("fragments must be nonempty")
    nuisance_bit_count = len(fragments[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {fragment: f"N{nuisance_index + 1}_{fragment[coordinate]}" for fragment in fragments}


def compression_profile(assignment: Assignment, fragments: tuple[str, ...]) -> dict[str, object]:
    class_sizes = sorted(class_size_map(assignment).values())
    return {
        "fragment_count": len(fragments),
        "class_count": len(class_sizes),
        "assignment_count": len(assignment),
        "class_size_signature": ";".join(str(size) for size in class_sizes),
        "simple_compression_score": (
            f"classes:{len(class_sizes)}|"
            f"sizes:{';'.join(str(size) for size in class_sizes)}"
        ),
    }


def merge_soundness_audit(assignment: Assignment, fragments: tuple[str, ...]) -> dict[str, object]:
    same_class_pair_count = 0
    allowed_same_class_pair_count = 0
    unsound_merge_count = 0
    unsound_pairs: list[str] = []
    for left, right in unordered_pairs(fragments):
        same_class = assignment[left] == assignment[right]
        exact_allows = exact_allows_merge(left, right)
        if same_class:
            same_class_pair_count += 1
            if exact_allows:
                allowed_same_class_pair_count += 1
            else:
                unsound_merge_count += 1
                unsound_pairs.append(f"{left},{right}")

    return {
        "same_class_pair_count": same_class_pair_count,
        "allowed_same_class_pair_count": allowed_same_class_pair_count,
        "unsound_merge_count": unsound_merge_count,
        "unsound_pair_signature": ";".join(unsound_pairs),
        "merge_sound": unsound_merge_count == 0,
    }


def exact_allows_merge(left: str, right: str) -> bool:
    return left[0] == right[0]


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))


def class_size_map(assignment: Assignment) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for class_id in assignment.values():
        sizes[class_id] = sizes.get(class_id, 0) + 1
    return sizes
