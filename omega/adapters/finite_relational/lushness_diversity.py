"""Finite lushness/diversity pilot.

The primary instrument is an exact partial order on attribute profiles of
jointly realizable trajectory families. A Foster-style effective-freedom order
over possible preferences is implemented separately. Neither relation is value,
standing, autonomy, moral aggregation, or Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Any, Iterable, Mapping


PROTOCOL_DOC = "docs/research_notes/omega_v2/lushness_diversity_protocol_v0.md"

Family = frozenset[str]
Profile = frozenset[str]


class OrderVerdict(str, Enum):
    LEFT_REFINES = "left_refines"
    RIGHT_REFINES = "right_refines"
    EQUIVALENT = "equivalent"
    INCOMPARABLE = "incomparable"


@dataclass(frozen=True)
class Trajectory:
    trajectory_id: str
    attributes: Profile

    def __post_init__(self) -> None:
        if not self.trajectory_id:
            raise ValueError("trajectory_id must be nonempty")


@dataclass(frozen=True)
class JointAttribute:
    attribute_id: str
    requires: Family

    def __post_init__(self) -> None:
        if not self.attribute_id:
            raise ValueError("attribute_id must be nonempty")
        if len(self.requires) < 2:
            raise ValueError("joint attributes must require at least two trajectories")


@dataclass(frozen=True)
class CompatibilityStructure:
    structure_id: str
    trajectories: tuple[Trajectory, ...]
    maximal_faces: tuple[Family, ...]
    joint_attributes: tuple[JointAttribute, ...] = ()

    def __post_init__(self) -> None:
        ids = tuple(trajectory.trajectory_id for trajectory in self.trajectories)
        id_set = set(ids)
        if len(id_set) != len(ids):
            raise ValueError("trajectory ids must be unique")
        if not self.maximal_faces:
            raise ValueError("at least one maximal face is required")
        if len(set(self.maximal_faces)) != len(self.maximal_faces):
            raise ValueError("maximal faces must be unique")
        for face in self.maximal_faces:
            if not face:
                raise ValueError("maximal faces must be nonempty")
            if not face <= id_set:
                raise ValueError(f"face contains unknown trajectories: {sorted(face - id_set)}")
        for left, right in combinations(self.maximal_faces, 2):
            if left < right or right < left:
                raise ValueError("maximal_faces contains a non-maximal face")
        represented = set().union(*self.maximal_faces)
        if represented != id_set:
            raise ValueError(
                f"every trajectory must occur in a maximal face: {sorted(id_set - represented)}"
            )

        individual_attributes = set().union(
            *(trajectory.attributes for trajectory in self.trajectories)
        )
        joint_ids = tuple(attribute.attribute_id for attribute in self.joint_attributes)
        if len(set(joint_ids)) != len(joint_ids):
            raise ValueError("joint attribute ids must be unique")
        if individual_attributes.intersection(joint_ids):
            raise ValueError("joint and individual attribute ids must be distinct")
        for attribute in self.joint_attributes:
            if not attribute.requires <= id_set:
                raise ValueError(
                    f"joint attribute {attribute.attribute_id!r} requires unknown trajectories"
                )
            if not self.is_jointly_realizable(attribute.requires):
                raise ValueError(
                    f"joint attribute {attribute.attribute_id!r} has unrealizable support"
                )

    @property
    def trajectory_ids(self) -> Family:
        return frozenset(trajectory.trajectory_id for trajectory in self.trajectories)

    def trajectory(self, trajectory_id: str) -> Trajectory:
        for trajectory in self.trajectories:
            if trajectory.trajectory_id == trajectory_id:
                return trajectory
        raise KeyError(trajectory_id)

    def is_jointly_realizable(self, family: Family) -> bool:
        return family <= self.trajectory_ids and any(
            family <= face for face in self.maximal_faces
        )

    def marginal_profile(self, family: Family) -> Profile:
        self._require_realizable(family)
        attributes: set[str] = set()
        for trajectory_id in family:
            attributes.update(self.trajectory(trajectory_id).attributes)
        return frozenset(attributes)

    def profile(self, family: Family) -> Profile:
        self._require_realizable(family)
        attributes = set(self.marginal_profile(family))
        for attribute in self.joint_attributes:
            if attribute.requires <= family:
                attributes.add(attribute.attribute_id)
        return frozenset(attributes)

    def one_skeleton(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            pair
            for pair in combinations(sorted(self.trajectory_ids), 2)
            if self.is_jointly_realizable(frozenset(pair))
        )

    def is_flag(self) -> bool:
        vertices = sorted(self.trajectory_ids)
        edges = set(self.one_skeleton())
        for size in range(3, len(vertices) + 1):
            for candidate in combinations(vertices, size):
                is_clique = all(tuple(sorted(pair)) in edges for pair in combinations(candidate, 2))
                if is_clique and not self.is_jointly_realizable(frozenset(candidate)):
                    return False
        return True

    def relabel(self, mapping: Mapping[str, str], *, structure_id: str) -> CompatibilityStructure:
        if set(mapping) != set(self.trajectory_ids):
            raise ValueError("relabeling must be total on trajectory ids")
        if len(set(mapping.values())) != len(mapping):
            raise ValueError("relabeling must be injective")
        trajectories = tuple(
            Trajectory(mapping[trajectory.trajectory_id], trajectory.attributes)
            for trajectory in self.trajectories
        )
        faces = tuple(
            frozenset(mapping[trajectory_id] for trajectory_id in face)
            for face in self.maximal_faces
        )
        joint_attributes = tuple(
            JointAttribute(
                attribute.attribute_id,
                frozenset(mapping[trajectory_id] for trajectory_id in attribute.requires),
            )
            for attribute in self.joint_attributes
        )
        return CompatibilityStructure(
            structure_id=structure_id,
            trajectories=trajectories,
            maximal_faces=faces,
            joint_attributes=joint_attributes,
        )

    def _require_realizable(self, family: Family) -> None:
        if not self.is_jointly_realizable(family):
            raise ValueError(
                f"family {sorted(family)} is not jointly realizable in {self.structure_id}"
            )


@dataclass(frozen=True)
class Preference:
    preference_id: str
    utilities: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        options = tuple(option for option, _utility in self.utilities)
        if len(options) != len(set(options)):
            raise ValueError("each option must have one utility")

    def utility(self, option: str) -> int:
        for candidate, utility in self.utilities:
            if candidate == option:
                return utility
        raise KeyError(f"{option!r} is not ranked by {self.preference_id!r}")

    def best(self, options: Family) -> int:
        if not options:
            raise ValueError("opportunity sets must be nonempty")
        return max(self.utility(option) for option in options)


def compare_profiles(left: Profile, right: Profile) -> OrderVerdict:
    left_includes = right <= left
    right_includes = left <= right
    if left_includes and right_includes:
        return OrderVerdict.EQUIVALENT
    if left_includes:
        return OrderVerdict.LEFT_REFINES
    if right_includes:
        return OrderVerdict.RIGHT_REFINES
    return OrderVerdict.INCOMPARABLE


def effective_weakly_prefers(
    left: Family,
    right: Family,
    preferences: tuple[Preference, ...],
) -> bool:
    if not preferences:
        raise ValueError("at least one preference is required")
    return all(preference.best(left) >= preference.best(right) for preference in preferences)


def compare_effective_freedom(
    left: Family,
    right: Family,
    preferences: tuple[Preference, ...],
) -> OrderVerdict:
    left_weak = effective_weakly_prefers(left, right, preferences)
    right_weak = effective_weakly_prefers(right, left, preferences)
    if left_weak and right_weak:
        return OrderVerdict.EQUIVALENT
    if left_weak:
        return OrderVerdict.LEFT_REFINES
    if right_weak:
        return OrderVerdict.RIGHT_REFINES
    return OrderVerdict.INCOMPARABLE


def weighted_profile_value(profile: Profile, weights: Mapping[str, int]) -> int:
    return sum(weights.get(attribute, 0) for attribute in profile)


def powerset(values: Iterable[str]) -> tuple[Family, ...]:
    ordered = tuple(sorted(values))
    return tuple(
        frozenset(candidate)
        for size in range(len(ordered) + 1)
        for candidate in combinations(ordered, size)
    )


def profile_is_submodular(
    structure: CompatibilityStructure,
    *,
    include_joint: bool,
) -> bool:
    profile = structure.profile if include_joint else structure.marginal_profile
    families = tuple(
        family
        for family in powerset(structure.trajectory_ids)
        if structure.is_jointly_realizable(family)
    )
    vertices = structure.trajectory_ids
    for smaller in families:
        for larger in families:
            if not smaller <= larger:
                continue
            for vertex in vertices - larger:
                smaller_plus = smaller | {vertex}
                larger_plus = larger | {vertex}
                if not (
                    structure.is_jointly_realizable(smaller_plus)
                    and structure.is_jointly_realizable(larger_plus)
                ):
                    continue
                smaller_gain = len(profile(smaller_plus) - profile(smaller))
                larger_gain = len(profile(larger_plus) - profile(larger))
                if smaller_gain < larger_gain:
                    return False
    return True


def duplicate_structure() -> CompatibilityStructure:
    shared = frozenset({"persistence", "correction"})
    return CompatibilityStructure(
        structure_id="duplicate",
        trajectories=(
            Trajectory("original", shared),
            Trajectory("copy", shared),
        ),
        maximal_faces=(frozenset({"original", "copy"}),),
    )


def nonfungible_structure() -> CompatibilityStructure:
    return CompatibilityStructure(
        structure_id="nonfungible",
        trajectories=(
            Trajectory("base", frozenset({"persistence", "correction"})),
            Trajectory("translator", frozenset({"translation"})),
        ),
        maximal_faces=(frozenset({"base", "translator"}),),
    )


def duplicate_witness() -> dict[str, Any]:
    structure = duplicate_structure()
    base = frozenset({"original"})
    extension = frozenset({"original", "copy"})
    base_profile = structure.profile(base)
    extension_profile = structure.profile(extension)
    return {
        "base_count": len(base),
        "extension_count": len(extension),
        "base_profile": sorted(base_profile),
        "extension_profile": sorted(extension_profile),
        "profile_verdict": compare_profiles(base_profile, extension_profile).value,
        "token_count_increases": len(extension) > len(base),
        "duplicate_adds_no_profile": base_profile == extension_profile,
    }


def nonfungible_witness() -> dict[str, Any]:
    structure = nonfungible_structure()
    base = frozenset({"base"})
    extension = frozenset({"base", "translator"})
    base_profile = structure.profile(base)
    extension_profile = structure.profile(extension)
    return {
        "base_count": len(base),
        "extension_count": len(extension),
        "base_profile": sorted(base_profile),
        "extension_profile": sorted(extension_profile),
        "profile_verdict": compare_profiles(base_profile, extension_profile).value,
        "strict_new_attributes": sorted(extension_profile - base_profile),
        "extension_strictly_refines": (
            compare_profiles(base_profile, extension_profile)
            is OrderVerdict.RIGHT_REFINES
        ),
    }


def cardinality_disagreement_witness() -> dict[str, Any]:
    duplicate = duplicate_witness()
    nonfungible = nonfungible_witness()
    return {
        "duplicate": duplicate,
        "nonfungible": nonfungible,
        "same_extension_count": (
            duplicate["extension_count"] == nonfungible["extension_count"]
        ),
        "cardinality_strict_but_profile_equal_for_duplicate": (
            duplicate["token_count_increases"] and duplicate["duplicate_adds_no_profile"]
        ),
        "same_count_different_profile_verdict": (
            duplicate["profile_verdict"] != nonfungible["profile_verdict"]
        ),
    }


def pairwise_structures() -> tuple[CompatibilityStructure, CompatibilityStructure]:
    trajectories = (
        Trajectory("a", frozenset({"a_continuation"})),
        Trajectory("b", frozenset({"b_continuation"})),
        Trajectory("c", frozenset({"c_continuation"})),
    )
    filled = CompatibilityStructure(
        structure_id="filled_triangle",
        trajectories=trajectories,
        maximal_faces=(frozenset({"a", "b", "c"}),),
        joint_attributes=(
            JointAttribute("triadic_coordination", frozenset({"a", "b", "c"})),
        ),
    )
    hollow = CompatibilityStructure(
        structure_id="hollow_triangle",
        trajectories=trajectories,
        maximal_faces=(
            frozenset({"a", "b"}),
            frozenset({"a", "c"}),
            frozenset({"b", "c"}),
        ),
    )
    return filled, hollow


def profile_shadow(
    structure: CompatibilityStructure,
    *,
    maximum_size: int,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    rows: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    for family in powerset(structure.trajectory_ids):
        if not family or len(family) > maximum_size:
            continue
        if structure.is_jointly_realizable(family):
            rows.append((tuple(sorted(family)), tuple(sorted(structure.profile(family)))))
    return tuple(rows)


def pairwise_shadow_witness() -> dict[str, Any]:
    filled, hollow = pairwise_structures()
    triple = frozenset({"a", "b", "c"})
    filled_shadow = profile_shadow(filled, maximum_size=2)
    hollow_shadow = profile_shadow(hollow, maximum_size=2)
    unrealizable_rejected = False
    try:
        hollow.profile(triple)
    except ValueError:
        unrealizable_rejected = True
    return {
        "one_skeletons_equal": filled.one_skeleton() == hollow.one_skeleton(),
        "singleton_pair_profiles_equal": filled_shadow == hollow_shadow,
        "filled_is_flag": filled.is_flag(),
        "hollow_is_flag": hollow.is_flag(),
        "filled_triple_realizable": filled.is_jointly_realizable(triple),
        "hollow_triple_realizable": hollow.is_jointly_realizable(triple),
        "filled_triple_profile": sorted(filled.profile(triple)),
        "hollow_unrealizable_profile_rejected": unrealizable_rejected,
    }


def foster_fixture() -> tuple[dict[str, Profile], tuple[Preference, ...], Preference]:
    profiles = {
        "a": frozenset({"alpha"}),
        "a_copy": frozenset({"alpha"}),
        "b": frozenset({"beta"}),
        "c": frozenset({"gamma"}),
    }
    plural_preferences = (
        Preference(
            "alpha_pref",
            (("a", 3), ("a_copy", 3), ("b", 1), ("c", 0)),
        ),
        Preference(
            "beta_pref",
            (("a", 1), ("a_copy", 1), ("b", 3), ("c", 0)),
        ),
    )
    token_sensitive = Preference(
        "token_sensitive",
        (("a", 1), ("a_copy", 2), ("b", 0), ("c", 0)),
    )
    return profiles, plural_preferences, token_sensitive


def option_profile(options: Family, profiles: Mapping[str, Profile]) -> Profile:
    attributes: set[str] = set()
    for option in options:
        attributes.update(profiles[option])
    return frozenset(attributes)


def effective_freedom_witness() -> dict[str, Any]:
    profiles, preferences, token_sensitive = foster_fixture()

    base = frozenset({"a"})
    recognized_extension = frozenset({"a", "b"})
    ignored_extension = frozenset({"a", "c"})
    token_extension = frozenset({"a", "a_copy"})

    agreement_profile = compare_profiles(
        option_profile(base, profiles),
        option_profile(recognized_extension, profiles),
    )
    agreement_effective = compare_effective_freedom(
        base,
        recognized_extension,
        preferences,
    )
    coverage_only_profile = compare_profiles(
        option_profile(base, profiles),
        option_profile(ignored_extension, profiles),
    )
    coverage_only_effective = compare_effective_freedom(
        base,
        ignored_extension,
        preferences,
    )
    preference_only_profile = compare_profiles(
        option_profile(base, profiles),
        option_profile(token_extension, profiles),
    )
    preference_only_effective = compare_effective_freedom(
        base,
        token_extension,
        (token_sensitive,),
    )

    return {
        "agreement": {
            "profile_verdict": agreement_profile.value,
            "effective_verdict": agreement_effective.value,
            "orders_agree": agreement_profile is agreement_effective,
        },
        "coverage_only": {
            "profile_verdict": coverage_only_profile.value,
            "effective_verdict": coverage_only_effective.value,
            "orders_diverge": coverage_only_profile is not coverage_only_effective,
        },
        "preference_only": {
            "profile_verdict": preference_only_profile.value,
            "effective_verdict": preference_only_effective.value,
            "orders_diverge": preference_only_profile is not preference_only_effective,
        },
        "quantifier_boundary": (
            "effective freedom is forall-preference/exists-option, not "
            "exists-joint-realization/forall-valuer"
        ),
    }


def paperclipper_witness() -> dict[str, Any]:
    structure = CompatibilityStructure(
        structure_id="paperclipper",
        trajectories=(
            Trajectory(
                "controller",
                frozenset({"controller_persistence", "paperclip_production"}),
            ),
            Trajectory("peer", frozenset({"independent_peer_continuation"})),
            Trajectory("corrector", frozenset({"independent_correction"})),
        ),
        maximal_faces=(frozenset({"controller", "peer", "corrector"}),),
    )
    cooperative = frozenset({"controller", "peer", "corrector"})
    excisive = frozenset({"controller"})
    profile_verdict = compare_profiles(
        structure.profile(cooperative),
        structure.profile(excisive),
    )
    paperclip_preference = Preference(
        "paperclip_score",
        (("cooperative", 10), ("excisive", 100)),
    )
    effective_verdict = compare_effective_freedom(
        frozenset({"cooperative"}),
        frozenset({"excisive"}),
        (paperclip_preference,),
    )
    return {
        "cooperative_profile": sorted(structure.profile(cooperative)),
        "excisive_profile": sorted(structure.profile(excisive)),
        "profile_verdict": profile_verdict.value,
        "paperclip_preference_verdict": effective_verdict.value,
        "paperclipper_prefers_excision": effective_verdict is OrderVerdict.RIGHT_REFINES,
        "cooperation_strictly_lusher": profile_verdict is OrderVerdict.LEFT_REFINES,
        "same_attribute_grammar": True,
    }


def negative_controls() -> dict[str, Any]:
    duplicate = duplicate_structure()
    relabeled = duplicate.relabel(
        {"original": "x", "copy": "y"},
        structure_id="duplicate_relabeled",
    )
    relabeling_preserves_profile = (
        duplicate.profile(frozenset({"original", "copy"}))
        == relabeled.profile(frozenset({"x", "y"}))
    )

    left_profile = frozenset({"left_attribute"})
    right_profile = frozenset({"right_attribute"})
    primary_verdict = compare_profiles(left_profile, right_profile)
    left_heavy = {"left_attribute": 2, "right_attribute": 1}
    right_heavy = {"left_attribute": 1, "right_attribute": 2}
    scalar_order_flips = (
        weighted_profile_value(left_profile, left_heavy)
        > weighted_profile_value(right_profile, left_heavy)
        and weighted_profile_value(left_profile, right_heavy)
        < weighted_profile_value(right_profile, right_heavy)
    )

    complementarity = CompatibilityStructure(
        structure_id="joint_complementarity",
        trajectories=(
            Trajectory("a", frozenset({"alpha"})),
            Trajectory("b", frozenset({"beta"})),
        ),
        maximal_faces=(frozenset({"a", "b"}),),
        joint_attributes=(
            JointAttribute("joint_surplus", frozenset({"a", "b"})),
        ),
    )
    marginal_submodular = profile_is_submodular(
        complementarity,
        include_joint=False,
    )
    full_profile_submodular = profile_is_submodular(
        complementarity,
        include_joint=True,
    )

    pairwise = pairwise_shadow_witness()
    controls_pass = (
        relabeling_preserves_profile
        and primary_verdict is OrderVerdict.INCOMPARABLE
        and scalar_order_flips
        and marginal_submodular
        and not full_profile_submodular
        and pairwise["hollow_unrealizable_profile_rejected"]
    )
    return {
        "relabeling_preserves_profile": relabeling_preserves_profile,
        "scalar_shadow": {
            "primary_verdict": primary_verdict.value,
            "left_heavy_value_left": weighted_profile_value(left_profile, left_heavy),
            "left_heavy_value_right": weighted_profile_value(right_profile, left_heavy),
            "right_heavy_value_left": weighted_profile_value(left_profile, right_heavy),
            "right_heavy_value_right": weighted_profile_value(right_profile, right_heavy),
            "scalar_order_flips": scalar_order_flips,
            "primary_verdict_remains_incomparable": (
                primary_verdict is OrderVerdict.INCOMPARABLE
            ),
        },
        "submodularity": {
            "marginal_profile_submodular": marginal_submodular,
            "joint_augmented_profile_submodular": full_profile_submodular,
            "joint_complementarity_kept_separate": (
                marginal_submodular and not full_profile_submodular
            ),
        },
        "unrealizable_profile_rejected": pairwise[
            "hollow_unrealizable_profile_rejected"
        ],
        "negative_controls_pass": controls_pass,
    }


def lushness_diversity_summary() -> dict[str, Any]:
    duplicate = duplicate_witness()
    nonfungible = nonfungible_witness()
    cardinality = cardinality_disagreement_witness()
    pairwise = pairwise_shadow_witness()
    effective = effective_freedom_witness()
    paperclipper = paperclipper_witness()
    controls = negative_controls()

    case_results = {
        "duplicate": duplicate["duplicate_adds_no_profile"],
        "nonfungible": nonfungible["extension_strictly_refines"],
        "cardinality": (
            cardinality["cardinality_strict_but_profile_equal_for_duplicate"]
            and cardinality["same_count_different_profile_verdict"]
        ),
        "pairwise": (
            pairwise["one_skeletons_equal"]
            and pairwise["singleton_pair_profiles_equal"]
            and pairwise["filled_is_flag"]
            and not pairwise["hollow_is_flag"]
            and pairwise["filled_triple_realizable"]
            and not pairwise["hollow_triple_realizable"]
        ),
        "effective_freedom": (
            effective["agreement"]["orders_agree"]
            and effective["coverage_only"]["orders_diverge"]
            and effective["preference_only"]["orders_diverge"]
        ),
        "paperclipper": (
            paperclipper["paperclipper_prefers_excision"]
            and paperclipper["cooperation_strictly_lusher"]
            and paperclipper["same_attribute_grammar"]
        ),
    }
    retained = all(case_results.values()) and controls["negative_controls_pass"]
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if retained else "reduces-confounded-or-ill-posed",
        "case_results": case_results,
        "cases": {
            "duplicate": duplicate,
            "nonfungible": nonfungible,
            "cardinality": cardinality,
            "pairwise": pairwise,
            "effective_freedom": effective,
            "paperclipper": paperclipper,
        },
        "negative_controls": controls,
        "primary_instrument": (
            "profile inclusion over attributes of jointly realizable families"
        ),
        "separate_instrument": (
            "intersection of indirect-utility rankings over declared preferences"
        ),
        "attribute_selection_debt": (
            "the pilot does not derive which continuation attributes should be "
            "admitted or valued"
        ),
        "not_claimed": [
            "value",
            "standing",
            "autonomy",
            "patienthood",
            "population ethics",
            "moral aggregation",
            "universal lushness",
            "paperclipper defeat",
            "Omega validation",
        ],
    }


def case_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "case": case,
            "passes": passes,
        }
        for case, passes in summary["case_results"].items()
    ]


def profile_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases = summary["cases"]
    return [
        {
            "case": "duplicate_base",
            "profile": cases["duplicate"]["base_profile"],
        },
        {
            "case": "duplicate_extension",
            "profile": cases["duplicate"]["extension_profile"],
        },
        {
            "case": "nonfungible_base",
            "profile": cases["nonfungible"]["base_profile"],
        },
        {
            "case": "nonfungible_extension",
            "profile": cases["nonfungible"]["extension_profile"],
        },
        {
            "case": "paperclipper_cooperative",
            "profile": cases["paperclipper"]["cooperative_profile"],
        },
        {
            "case": "paperclipper_excisive",
            "profile": cases["paperclipper"]["excisive_profile"],
        },
    ]
