from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from omega_v2.experiments.process_interface_identifiability_v0 import (
    CENSUS_FEATURES,
    HORIZON,
    common_driver_control,
    copied_record_control,
    exact_independence_census,
    identification_controls,
    memory_injectivity_control,
    observational_nonidentifiability_control,
    process_interface_identifiability_summary,
)
from omega_v2.finite.process_interfaces import (
    FEATURE_FIELDS,
    BinarySynchronousSystem,
    EvidenceMode,
    IdentificationStatus,
    coordinate_influence_witnesses,
    identify_process_interfaces,
    profile_process_interface,
)
from omega_v2.validation.process_interface_identifiability_v0 import (
    render_report,
    run_process_interface_identifiability_v0,
)


def test_binary_system_requires_a_total_boolean_product() -> None:
    with pytest.raises(ValueError, match="total and functional"):
        BinarySynchronousSystem(
            system_id="partial",
            component_ids=("x", "y"),
            transition_rows=(((0, 0), (0, 0)),),
            initial_states=((0, 0),),
        )


def test_every_nonempty_proper_interface_is_profiled() -> None:
    system = BinarySynchronousSystem.from_update_function(
        system_id="three_components",
        component_ids=("a", "b", "c"),
        update=lambda state: (state[1], state[2], state[0]),
        initial_states=tuple(itertools.product((0, 1), repeat=3)),
    )
    result = identify_process_interfaces(
        system,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )

    assert len(result.profiles) == 2**3 - 2
    assert {profile.interface for profile in result.profiles} == {
        ("a",),
        ("b",),
        ("c",),
        ("a", "b"),
        ("a", "c"),
        ("b", "c"),
    }


def test_observation_does_not_fabricate_causal_features() -> None:
    controls = identification_controls()
    result = controls["observational"]

    assert result.status is IdentificationStatus.UNRESOLVED
    for profile in result.profiles:
        assert profile.persistent_variation
        assert profile.latent_state_multiplicity
        assert all(
            profile.feature(feature) is None
            for feature in (
                "internal_influence",
                "incoming_influence",
                "outgoing_influence",
                "record_acquisition",
                "record_sensitive_outflow",
                "continuation_influence",
            )
        )


def test_intervention_evidence_identifies_one_minimal_interface() -> None:
    result = identification_controls()["identified"]

    assert result.status is IdentificationStatus.IDENTIFIED
    assert result.retained_minimal_interfaces == (("inside",),)
    assert ("inside",) in result.certified_interfaces
    assert ("outside",) in result.rejected_interfaces
    inside = next(
        profile for profile in result.profiles if profile.interface == ("inside",)
    )
    assert inside.continuation_witness is not None


def test_symmetric_fixture_remains_set_identified() -> None:
    result = identification_controls()["set_identified"]

    assert result.status is IdentificationStatus.SET_IDENTIFIED
    assert result.retained_minimal_interfaces == (("left",), ("right",))


def test_annotations_are_ignored_and_renaming_is_covariant() -> None:
    controls = identification_controls()

    assert controls["annotation_invariant"]
    assert controls["annotation_edges_invariant"]
    assert controls["renaming_covariant"]
    assert controls["annotated"].state_atoms
    assert controls["feature_dependent"]


def test_influence_edges_retain_exact_intervention_witnesses() -> None:
    system = identification_controls()["identified_system"]
    witnesses = coordinate_influence_witnesses(system)

    assert witnesses
    for witness in witnesses:
        source_index = system.component_index[witness.source_component]
        target_index = system.component_index[witness.target_component]
        differing = [
            index
            for index, (left, right) in enumerate(
                zip(
                    witness.source_state,
                    witness.intervened_state,
                    strict=True,
                )
            )
            if left != right
        ]
        assert differing == [source_index]
        assert (
            system.step(witness.source_state)[target_index]
            != system.step(witness.intervened_state)[target_index]
        )


def test_common_driver_does_not_create_descendant_causation() -> None:
    control = common_driver_control()

    assert control["descendants_correlated"]
    assert control["driver_edges_present"]
    assert control["descendant_edge_absent"]


def test_copied_record_does_not_inherit_source_effect() -> None:
    control = copied_record_control()

    assert control["copy_tracks_source_update"]
    assert control["copy_tracks_output"]
    assert control["copy_to_output_edge_absent"]
    assert control["copy_outgoing_influence"] is False
    assert not control["copy_primary_certified"]


def test_observational_equivalence_does_not_imply_intervention_equivalence() -> None:
    control = observational_nonidentifiability_control()

    assert control["observationally_equivalent"]
    assert not control["interventionally_equivalent"]
    assert control["observational_profiles_equal"]
    assert control["observational_status_left"] == "UNRESOLVED"
    assert control["observational_status_right"] == "UNRESOLVED"
    assert control["inside_interventional_profiles_differ"]


def test_exact_census_enumerates_all_rules_and_audits_isolation() -> None:
    census = exact_independence_census()

    assert census["enumerated_rule_count"] == 256
    assert census["expected_rule_count"] == 256
    assert census["joint_signature_count"] == 28
    assert all(
        len(row["transition_targets"].split("|")) == 4
        for row in census["rows"]
    )
    assert census["record_acquisition_composite_holds"]
    assert set(census["feature_results"]) == set(CENSUS_FEATURES)

    for feature, details in census["feature_results"].items():
        assert details["verdict"] == "ISOLATED"
        left_code, right_code = details["witness_codes"]
        left = census["profiles"][left_code]
        right = census["profiles"][right_code]
        assert left.feature(feature) != right.feature(feature)
        assert all(
            left.feature(other) == right.feature(other)
            for other in CENSUS_FEATURES
            if other != feature
        )


def test_record_acquisition_is_the_declared_composite() -> None:
    census = exact_independence_census()

    assert all(
        profile.record_acquisition
        == (
            profile.incoming_influence
            and profile.latent_state_multiplicity
        )
        for profile in census["profiles"].values()
    )


def test_memory_erasure_control_separates_copy_from_xor() -> None:
    control = memory_injectivity_control()

    assert not control["copy_update"].conditionally_injective
    assert len(control["copy_update"].collisions) == 2
    assert not control["copy_closed_loop"].injective
    assert control["copy_closed_loop"].image_size == 2
    assert control["xor_update"].conditionally_injective
    assert control["xor_update"].collisions == ()
    assert control["xor_closed_loop"].injective
    assert control["xor_closed_loop"].image_size == 4
    assert control["world_dynamics_shared"]


def test_interface_profile_rejects_whole_system_as_an_interface() -> None:
    system = identification_controls()["identified_system"]

    with pytest.raises(ValueError, match="nonempty proper"):
        profile_process_interface(
            system,
            system.component_ids,
            evidence_mode=EvidenceMode.INTERVENTIONAL,
            horizon=HORIZON,
        )


def test_summary_retains_every_preregistered_control() -> None:
    summary = process_interface_identifiability_summary()

    assert summary["status"] == "retained"
    assert summary["verdict"] == "finite_process_interfaces_set_identified"
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert set(summary["independence_census"]["feature_results"]) == set(
        CENSUS_FEATURES
    )
    assert set(summary["primary_query"]["required_true"]) <= set(FEATURE_FIELDS)
    assert "valuerhood" in summary["claim_boundary"]


def test_validation_writes_every_preregistered_artifact(
    tmp_path: Path,
) -> None:
    result = run_process_interface_identifiability_v0(out_root=tmp_path)
    run_root = Path(result["run_root"])

    assert result["status"] == "retained"
    assert {path.name for path in run_root.iterdir()} == {
        "summary.json",
        "interface_profiles.csv",
        "identification_results.csv",
        "influence_edges.csv",
        "independence_census.csv",
        "independence_witnesses.csv",
        "negative_controls.csv",
        "memory_injectivity.csv",
        "report.md",
    }
    report = render_report(result)
    assert "Interventional status: IDENTIFIED" in report
    assert "Symmetric status: SET_IDENTIFIED" in report
    assert "Enumerated systems: 256/256" in report
