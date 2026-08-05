"""Finite exact fixtures for the Omega v2 projected-sector floor."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

from omega_v2.finite.projected_sector import (
    DeclaredIndependence,
    DiamondAudit,
    FiniteHistory,
    FiniteProjection,
    FiniteSystemIsomorphism,
    FiniteTransitionSystem,
    ProjectionProfile,
    SectorProfile,
    audit_commuting_diamonds,
    histories_commute_in_audited_diamond,
    histories_exactly_equal,
    histories_project_to_same_levels,
    histories_relabeling_equivalent,
    mutual_projected_reachability_is_equivalence,
    projected_components,
    projected_condensation_edges,
    projected_reachability_is_preorder,
    projection_profile,
    sector_profile,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/projected_sector_floor_protocol_v0.md"
)
PROTOCOL_COMMIT = "62fb6c9"
EXTENDABILITY_HORIZON = 3
EXPECTED_TRANSITION_ROWS = {
    "terminating_disintegration": (
        ("root", "split_left", "left"),
        ("root", "split_right", "right"),
        ("left", "decay", "dust"),
        ("right", "decay", "dust"),
    ),
    "recurrent_cycle": (
        ("a", "next", "b"),
        ("b", "next", "a"),
    ),
    "genuine_nonconfluent_branch": (
        ("root", "choose_left", "left"),
        ("root", "choose_right", "right"),
    ),
    "commuting_diamond": (
        ("root", "a", "left"),
        ("root", "b", "right"),
        ("left", "b", "joined"),
        ("right", "a", "joined"),
    ),
    "null_projection": (
        ("a", "next", "b"),
        ("b", "next", "a"),
    ),
    "one_sided_source": (
        ("s0", "step", "s1"),
        ("s1", "step", "s2"),
    ),
    "janus_source": (
        ("center", "toward_left", "left"),
        ("center", "toward_right", "right"),
    ),
}


@dataclass(frozen=True)
class ProjectedSectorFixture:
    """One support system with one declared projection and independence table."""

    fixture_id: str
    purpose: str
    system: FiniteTransitionSystem[str, str]
    projection: FiniteProjection[str]
    independence: DeclaredIndependence[str]

    def __post_init__(self) -> None:
        if not self.fixture_id or not self.purpose:
            raise ValueError("fixture id and purpose must be nonempty")
        self.projection.validate(self.system)
        if set(self.independence.labels) != set(self.system.labels):
            raise ValueError("fixture independence interface must match labels")


def _projection(
    projection_id: str,
    states: tuple[str, ...],
    levels: tuple[int, ...],
) -> FiniteProjection[str]:
    if len(states) != len(levels):
        raise ValueError("projection states and levels must have equal length")
    return FiniteProjection(
        projection_id=projection_id,
        states=states,
        rows=tuple(zip(states, levels, strict=True)),
    )


def terminating_disintegration_fixture() -> ProjectedSectorFixture:
    states = ("root", "left", "right", "dust")
    labels = ("split_left", "split_right", "decay")
    system = FiniteTransitionSystem(
        system_id="terminating_confluent_disintegration",
        states=states,
        labels=labels,
        transitions=(
            ("root", "split_left", "left"),
            ("root", "split_right", "right"),
            ("left", "decay", "dust"),
            ("right", "decay", "dust"),
        ),
    )
    return ProjectedSectorFixture(
        fixture_id="terminating_disintegration",
        purpose="terminating confluent law with lawful disintegration",
        system=system,
        projection=_projection(
            "disintegration_depth",
            states,
            (0, 1, 1, 2),
        ),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def recurrent_cycle_fixture() -> ProjectedSectorFixture:
    states = ("a", "b")
    labels = ("next",)
    system = FiniteTransitionSystem(
        system_id="recurrent_two_cycle",
        states=states,
        labels=labels,
        transitions=(("a", "next", "b"), ("b", "next", "a")),
    )
    return ProjectedSectorFixture(
        fixture_id="recurrent_cycle",
        purpose="recurrent nonbranching control under a non-null projection",
        system=system,
        projection=_projection("cycle_index", states, (0, 1)),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def genuine_nonconfluent_fixture() -> ProjectedSectorFixture:
    states = ("root", "left", "right")
    labels = ("choose_left", "choose_right")
    system = FiniteTransitionSystem(
        system_id="genuine_nonconfluent_branch",
        states=states,
        labels=labels,
        transitions=(
            ("root", "choose_left", "left"),
            ("root", "choose_right", "right"),
        ),
    )
    return ProjectedSectorFixture(
        fixture_id="genuine_nonconfluent_branch",
        purpose="terminating branch with no common descendant",
        system=system,
        projection=_projection("branch_depth", states, (0, 1, 1)),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def commuting_diamond_fixture() -> ProjectedSectorFixture:
    states = ("root", "left", "right", "joined")
    labels = ("a", "b")
    system = FiniteTransitionSystem(
        system_id="independent_commuting_diamond",
        states=states,
        labels=labels,
        transitions=(
            ("root", "a", "left"),
            ("root", "b", "right"),
            ("left", "b", "joined"),
            ("right", "a", "joined"),
        ),
    )
    return ProjectedSectorFixture(
        fixture_id="commuting_diamond",
        purpose="declared independent actions close at one target",
        system=system,
        projection=_projection("diamond_depth", states, (0, 1, 1, 2)),
        independence=DeclaredIndependence(
            labels=labels,
            pairs=(("a", "b"),),
        ),
    )


def null_projection_fixture() -> ProjectedSectorFixture:
    states = ("a", "b")
    labels = ("next",)
    system = FiniteTransitionSystem(
        system_id="null_projection_cycle",
        states=states,
        labels=labels,
        transitions=(("a", "next", "b"), ("b", "next", "a")),
    )
    return ProjectedSectorFixture(
        fixture_id="null_projection",
        purpose="recurrent dynamics under a projection with no directional content",
        system=system,
        projection=_projection("constant_projection", states, (0, 0)),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def one_sided_source_fixture() -> ProjectedSectorFixture:
    states = ("s0", "s1", "s2")
    labels = ("step",)
    system = FiniteTransitionSystem(
        system_id="one_sided_source",
        states=states,
        labels=labels,
        transitions=(("s0", "step", "s1"), ("s1", "step", "s2")),
    )
    return ProjectedSectorFixture(
        fixture_id="one_sided_source",
        purpose="positive-only chain with one source and one sink class",
        system=system,
        projection=_projection("chain_depth", states, (0, 1, 2)),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def janus_source_fixture() -> ProjectedSectorFixture:
    states = ("left", "center", "right")
    labels = ("toward_left", "toward_right")
    system = FiniteTransitionSystem(
        system_id="janus_source",
        states=states,
        labels=labels,
        transitions=(
            ("center", "toward_left", "left"),
            ("center", "toward_right", "right"),
        ),
    )
    return ProjectedSectorFixture(
        fixture_id="janus_source",
        purpose="one state emits in both projection polarities",
        system=system,
        projection=_projection("janus_coordinate", states, (-1, 0, 1)),
        independence=DeclaredIndependence(labels=labels, pairs=()),
    )


def projected_sector_fixtures() -> tuple[ProjectedSectorFixture, ...]:
    return (
        terminating_disintegration_fixture(),
        recurrent_cycle_fixture(),
        genuine_nonconfluent_fixture(),
        commuting_diamond_fixture(),
        null_projection_fixture(),
        one_sided_source_fixture(),
        janus_source_fixture(),
    )


def _fixture_analysis(
    fixture: ProjectedSectorFixture,
) -> dict[str, object]:
    sector = sector_profile(
        fixture.system,
        horizon=EXTENDABILITY_HORIZON,
        independence=fixture.independence,
    )
    projection = projection_profile(fixture.system, fixture.projection)
    components = projected_components(fixture.system, fixture.projection)
    edges = projected_condensation_edges(fixture.system, fixture.projection)
    diamond_audit = audit_commuting_diamonds(
        fixture.system,
        fixture.independence,
    )
    return {
        "fixture": fixture,
        "sector": sector,
        "projection": projection,
        "components": components,
        "condensation_edges": edges,
        "diamond_audit": diamond_audit,
        "projected_reach_preorder": projected_reachability_is_preorder(
            fixture.system,
            fixture.projection,
        ),
        "mutual_reach_equivalence": (
            mutual_projected_reachability_is_equivalence(
                fixture.system,
                fixture.projection,
            )
        ),
    }


def _history_controls(
    analyses: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    diamond_fixture = analyses["commuting_diamond"]["fixture"]
    if not isinstance(diamond_fixture, ProjectedSectorFixture):
        raise TypeError("commuting diamond fixture has the wrong type")
    audit = analyses["commuting_diamond"]["diamond_audit"]
    if not isinstance(audit, DiamondAudit):
        raise TypeError("commuting diamond audit has the wrong type")
    if len(audit.diamonds) != 1:
        raise ValueError("commuting fixture must retain exactly one diamond")
    diamond = audit.diamonds[0]
    left_history = diamond.left_history
    right_history = diamond.right_history

    source_fixture = analyses["one_sided_source"]["fixture"]
    if not isinstance(source_fixture, ProjectedSectorFixture):
        raise TypeError("one-sided fixture has the wrong type")
    target_system = FiniteTransitionSystem(
        system_id="renamed_one_sided_source",
        states=("q0", "q1", "q2"),
        labels=("advance",),
        transitions=(
            ("q0", "advance", "q1"),
            ("q1", "advance", "q2"),
        ),
    )
    target_projection = _projection(
        "renamed_chain_depth",
        target_system.states,
        (0, 1, 2),
    )
    isomorphism = FiniteSystemIsomorphism(
        isomorphism_id="one_sided_relabeling",
        state_rows=(("s0", "q0"), ("s1", "q1"), ("s2", "q2")),
        label_rows=(("step", "advance"),),
    )
    source_history = FiniteHistory(
        states=("s0", "s1", "s2"),
        labels=("step", "step"),
    )
    target_history = FiniteHistory(
        states=("q0", "q1", "q2"),
        labels=("advance", "advance"),
    )

    return {
        "diamond_left": left_history,
        "diamond_right": right_history,
        "diamond_exact_equal": histories_exactly_equal(
            left_history,
            right_history,
        ),
        "diamond_projected_equal": histories_project_to_same_levels(
            left_history,
            diamond_fixture.projection,
            right_history,
            diamond_fixture.projection,
        ),
        "diamond_commuting_equivalent": (
            histories_commute_in_audited_diamond(
                left_history,
                right_history,
                audit,
            )
        ),
        "relabel_source": source_history,
        "relabel_target": target_history,
        "relabel_exact_equal": False,
        "relabeling_equivalent": histories_relabeling_equivalent(
            source_fixture.system,
            target_system,
            isomorphism,
            source_history,
            target_history,
        ),
        "relabel_projected_equal": histories_project_to_same_levels(
            source_history,
            source_fixture.projection,
            target_history,
            target_projection,
        ),
        "target_system": target_system,
        "target_projection": target_projection,
        "isomorphism": isomorphism,
    }


def _contains_forbidden_coherence_key(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).lower() in {"coherent", "coherence"}
            or _contains_forbidden_coherence_key(item)
            for key, item in value.items()
        )
    if isinstance(value, (tuple, list)):
        return any(_contains_forbidden_coherence_key(item) for item in value)
    return False


def projected_sector_floor_summary() -> dict[str, Any]:
    fixtures = projected_sector_fixtures()
    analyses = {
        fixture.fixture_id: _fixture_analysis(fixture)
        for fixture in fixtures
    }
    histories = _history_controls(analyses)

    disintegration = analyses["terminating_disintegration"]["sector"]
    recurrent = analyses["recurrent_cycle"]["sector"]
    nonconfluent = analyses["genuine_nonconfluent_branch"]["sector"]
    diamond_sector = analyses["commuting_diamond"]["sector"]
    diamond_audit = analyses["commuting_diamond"]["diamond_audit"]
    null_projection = analyses["null_projection"]["projection"]
    one_sided = analyses["one_sided_source"]["projection"]
    janus = analyses["janus_source"]["projection"]
    if not all(
        isinstance(profile, SectorProfile)
        for profile in (
            disintegration,
            recurrent,
            nonconfluent,
            diamond_sector,
        )
    ):
        raise TypeError("sector analysis produced an unexpected profile type")
    if not all(
        isinstance(profile, ProjectionProfile)
        for profile in (null_projection, one_sided, janus)
    ):
        raise TypeError("projection analysis produced an unexpected profile type")
    if not isinstance(diamond_audit, DiamondAudit):
        raise TypeError("diamond analysis produced an unexpected audit type")

    case_results = {
        "seven_preregistered_fixtures_retained": len(fixtures) == 7,
        "all_fixture_transition_rows_retained_exactly": all(
            fixture.system.transitions
            == EXPECTED_TRANSITION_ROWS[fixture.fixture_id]
            for fixture in fixtures
        ),
        "all_projected_reach_relations_are_preorders": all(
            bool(analysis["projected_reach_preorder"])
            for analysis in analyses.values()
        ),
        "all_mutual_projected_reach_relations_are_equivalences": all(
            bool(analysis["mutual_reach_equivalence"])
            for analysis in analyses.values()
        ),
        "all_projected_condensations_are_acyclic": all(
            bool(
                isinstance(analysis["projection"], ProjectionProfile)
                and analysis["projection"].condensation_acyclic
            )
            for analysis in analyses.values()
        ),
        "termination_matches_absence_of_recurrent_components": all(
            bool(
                isinstance(analysis["sector"], SectorProfile)
                and analysis["sector"].terminating
                == (not analysis["sector"].recurrent_components)
            )
            for analysis in analyses.values()
        ),
        "terminating_disintegration_is_confluent": (
            disintegration.terminating
            and disintegration.locally_confluent
            and disintegration.globally_confluent
            and not disintegration.recurrent_components
            and disintegration.branching_state_count == 1
        ),
        "recurrent_cycle_is_recurrent_and_nonbranching": (
            not recurrent.terminating
            and len(recurrent.recurrent_components) == 1
            and recurrent.branching_state_count == 0
        ),
        "genuine_branch_is_nonconfluent": (
            nonconfluent.terminating
            and not nonconfluent.locally_confluent
            and not nonconfluent.globally_confluent
        ),
        "commuting_diamond_closes": (
            diamond_sector.locally_confluent
            and diamond_sector.globally_confluent
            and len(diamond_audit.diamonds) == 1
            and not diamond_audit.failures
        ),
        "diamond_exact_histories_remain_distinct": (
            not histories["diamond_exact_equal"]
        ),
        "diamond_histories_share_one_projection": bool(
            histories["diamond_projected_equal"]
        ),
        "diamond_histories_are_commuting_equivalent": bool(
            histories["diamond_commuting_equivalent"]
        ),
        "declared_relabeling_preserves_history": (
            not histories["relabel_exact_equal"]
            and bool(histories["relabeling_equivalent"])
            and bool(histories["relabel_projected_equal"])
        ),
        "null_projection_remains_null": (
            null_projection.polarity.value == "NULL"
            and null_projection.level_transition_count == 2
        ),
        "one_sided_source_remains_positive_only": (
            one_sided.polarity.value == "POSITIVE_ONLY"
            and one_sided.projected_source_component_count == 1
            and one_sided.projected_sink_component_count == 1
        ),
        "janus_source_remains_bidirectional": (
            janus.polarity.value == "BIDIRECTIONAL"
            and janus.janus_sources == ("center",)
        ),
        "partial_and_nondeterministic_systems_are_admitted": (
            disintegration.sink_state_count == 1
            and disintegration.branching_state_count == 1
        ),
    }
    preliminary_public = {
        "fixtures": [
            {
                "fixture_id": fixture.fixture_id,
                "purpose": fixture.purpose,
                "sector": analyses[fixture.fixture_id]["sector"].as_dict(),
                "projection": (
                    analyses[fixture.fixture_id]["projection"].as_dict()
                ),
            }
            for fixture in fixtures
        ],
        "case_results": case_results,
    }
    case_results["no_single_coherence_boolean_emitted"] = (
        not _contains_forbidden_coherence_key(preliminary_public)
    )

    kill_conditions = {
        "fixture_transition_rows_changed": not case_results[
            "all_fixture_transition_rows_retained_exactly"
        ],
        "projected_reachability_failed_preorder": not case_results[
            "all_projected_reach_relations_are_preorders"
        ],
        "mutual_reachability_failed_equivalence": not case_results[
            "all_mutual_projected_reach_relations_are_equivalences"
        ],
        "projected_condensation_contains_cycle": not case_results[
            "all_projected_condensations_are_acyclic"
        ],
        "terminating_disintegration_reported_nonconfluent": not case_results[
            "terminating_disintegration_is_confluent"
        ],
        "genuine_branch_reported_confluent": not case_results[
            "genuine_branch_is_nonconfluent"
        ],
        "commuting_diamond_not_detected": not case_results[
            "commuting_diamond_closes"
        ],
        "exact_diamond_histories_were_merged": not case_results[
            "diamond_exact_histories_remain_distinct"
        ],
        "null_projection_received_directional_polarity": not case_results[
            "null_projection_remains_null"
        ],
        "partial_or_nondeterministic_system_rejected": not case_results[
            "partial_and_nondeterministic_systems_are_admitted"
        ],
        "single_coherence_boolean_emitted": not case_results[
            "no_single_coherence_boolean_emitted"
        ],
    }
    status = "retained" if not any(kill_conditions.values()) else "failed"
    verdict = (
        "projected_order_retained_and_sector_properties_separate"
        if status == "retained"
        else "projected_sector_floor_failed"
    )
    return {
        "status": status,
        "verdict": verdict,
        "protocol_doc": PROTOCOL_DOC,
        "protocol_commit": PROTOCOL_COMMIT,
        "extendability_horizon": EXTENDABILITY_HORIZON,
        "fixture_count": len(fixtures),
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite support-level projection, reachability, history, "
            "termination, recurrence, confluence, and commutation only; "
            "not persistence, identity, observerhood, agency, valuerhood, "
            "value, Omega compatibility, or moral license."
        ),
        "public_compression": (
            "A projection turns a finite transition sector into an ordered "
            "continuation view, but it does not create persistence, identity, "
            "or value. Termination, recurrence, confluence, and independent "
            "commutation remain distinct properties."
        ),
        "_objects": {
            "fixtures": fixtures,
            "analyses": analyses,
            "histories": histories,
        },
    }


def fixture_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    rows = []
    analyses = summary["_objects"]["analyses"]
    for fixture in summary["_objects"]["fixtures"]:
        sector = analyses[fixture.fixture_id]["sector"]
        projection = analyses[fixture.fixture_id]["projection"]
        rows.append(
            {
                "fixture_id": fixture.fixture_id,
                "system_id": fixture.system.system_id,
                "purpose": fixture.purpose,
                "states": "|".join(fixture.system.states),
                "labels": "|".join(fixture.system.labels),
                "transition_rows": json.dumps(fixture.system.transitions),
                "projection_id": fixture.projection.projection_id,
                "projection_rows": json.dumps(fixture.projection.rows),
                "terminating": sector.terminating,
                "polarity": projection.polarity.value,
            }
        )
    return rows


def sector_profile_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    analyses = summary["_objects"]["analyses"]
    for fixture in summary["_objects"]["fixtures"]:
        profile = analyses[fixture.fixture_id]["sector"]
        retained = profile.as_dict()
        rows.append({"fixture_id": fixture.fixture_id, **retained})
    return rows


def projection_profile_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    analyses = summary["_objects"]["analyses"]
    for fixture in summary["_objects"]["fixtures"]:
        profile = analyses[fixture.fixture_id]["projection"]
        retained = profile.as_dict()
        retained["janus_sources"] = "|".join(
            state for state in profile.janus_sources
        )
        rows.append({"fixture_id": fixture.fixture_id, **retained})
    return rows


def projected_component_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    analyses = summary["_objects"]["analyses"]
    for fixture in summary["_objects"]["fixtures"]:
        components = analyses[fixture.fixture_id]["components"]
        edges = set(analyses[fixture.fixture_id]["condensation_edges"])
        for index, component in enumerate(components):
            levels = tuple(
                fixture.projection.level(state) for state in component
            )
            rows.append(
                {
                    "fixture_id": fixture.fixture_id,
                    "component_index": index,
                    "states": "|".join(component),
                    "minimum_level": min(levels),
                    "maximum_level": max(levels),
                    "incoming_component_count": sum(
                        target == index for _source, target in edges
                    ),
                    "outgoing_component_count": sum(
                        source == index for source, _target in edges
                    ),
                }
            )
    return rows


def history_comparison_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    histories = summary["_objects"]["histories"]
    return [
        {
            "comparison_id": "commuting_diamond_paths",
            "left_states": "|".join(histories["diamond_left"].states),
            "left_labels": "|".join(histories["diamond_left"].labels),
            "right_states": "|".join(histories["diamond_right"].states),
            "right_labels": "|".join(histories["diamond_right"].labels),
            "exact_equal": histories["diamond_exact_equal"],
            "relabeling_equivalent": "not_evaluated",
            "commuting_diamond_equivalent": histories[
                "diamond_commuting_equivalent"
            ],
            "projected_equal": histories["diamond_projected_equal"],
        },
        {
            "comparison_id": "one_sided_declared_relabeling",
            "left_states": "|".join(histories["relabel_source"].states),
            "left_labels": "|".join(histories["relabel_source"].labels),
            "right_states": "|".join(histories["relabel_target"].states),
            "right_labels": "|".join(histories["relabel_target"].labels),
            "exact_equal": histories["relabel_exact_equal"],
            "relabeling_equivalent": histories["relabeling_equivalent"],
            "commuting_diamond_equivalent": "not_evaluated",
            "projected_equal": histories["relabel_projected_equal"],
        },
    ]


def commuting_diamond_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    analyses = summary["_objects"]["analyses"]
    for fixture in summary["_objects"]["fixtures"]:
        audit = analyses[fixture.fixture_id]["diamond_audit"]
        for diamond in audit.diamonds:
            rows.append(
                {
                    "fixture_id": fixture.fixture_id,
                    "source": diamond.source,
                    "left_label": diamond.left_label,
                    "right_label": diamond.right_label,
                    "left_state": diamond.left_state,
                    "right_state": diamond.right_state,
                    "target": diamond.target,
                }
            )
    return rows


def summary_digest(summary: Mapping[str, Any]) -> str:
    public = {
        key: value for key, value in summary.items() if key != "_objects"
    }
    payload = json.dumps(
        public,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
