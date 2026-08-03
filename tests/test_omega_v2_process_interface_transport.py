from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from omega_v2.experiments.process_interface_transport_v0 import (
    HORIZON,
    OUTFLOW_QUERY,
    block_transport_rows,
    crosscut_controls,
    factorization_rows,
    factorized_profile_rows,
    family_transport_rows,
    negative_control_rows,
    partition_validation_controls,
    refinement_controls,
    refinement_factorizations,
    refinement_system,
    run_experiment,
    several_minima_controls,
)
from omega_v2.finite.component_factorizations import (
    ComponentFactorization,
    FactorBlock,
    InterfaceTransportStatus,
    audit_intervention_transport,
    compare_interface_families,
    factorized_interface_profiles,
    identify_factorized_interfaces,
)
from omega_v2.finite.process_interfaces import (
    BinarySynchronousSystem,
    EvidenceMode,
)
from omega_v2.validation.process_interface_transport_v0 import (
    retain_process_interface_transport_v0,
)


def test_factor_block_rejects_empty_members() -> None:
    with pytest.raises(ValueError, match="nonempty"):
        FactorBlock("empty", ())


def test_factorization_rejects_overlap_and_omission() -> None:
    controls = partition_validation_controls()
    assert controls == {
        "empty_block_rejected": True,
        "overlap_rejected": True,
        "omission_rejected": True,
    }


def test_factorization_concretizes_and_represents_exact_unions() -> None:
    coarse, fine, _relabeled = refinement_factorizations()
    assert coarse.concretize(("core",)) == ("inside", "aux")
    assert fine.represent(("inside", "aux")) == (
        "inside_block",
        "aux_block",
    )
    assert coarse.represent(("inside",)) is None


def test_saturation_reports_unavoidably_added_members() -> None:
    crosscut = crosscut_controls()
    saturation = crosscut["source_ab_saturation"]
    assert saturation.exact is False
    assert saturation.requested_members == ("a", "b")
    assert saturation.saturated_members == ("a", "b", "c", "d")
    assert saturation.added_members == ("c", "d")


def test_refinement_decomposes_every_coarse_intervention() -> None:
    coarse, fine, _relabeled = refinement_factorizations()
    audit = audit_intervention_transport(coarse, fine)
    assert audit.exact is True
    transports = {
        transport.source_block_id: transport.target_block_ids
        for transport in audit.transports
    }
    assert transports == {
        "core": ("inside_block", "aux_block"),
        "environment": ("outside_block",),
    }


def test_merge_direction_is_not_an_exact_forward_transport() -> None:
    coarse, fine, _relabeled = refinement_factorizations()
    audit = audit_intervention_transport(fine, coarse)
    assert audit.exact is False
    inside_failure = next(
        failure
        for failure in audit.failures
        if failure.source_block_id == "inside_block"
    )
    assert inside_failure.added_target_members == ("aux",)


def test_crosscut_partitions_retain_failure_witnesses() -> None:
    crosscut = crosscut_controls()
    assert crosscut["forward"].exact is False
    assert crosscut["reverse"].exact is False
    assert len(crosscut["forward"].failures) == 2
    first = crosscut["forward"].failures[0]
    assert first.source_members == ("a", "b")
    assert first.added_target_members == ("c", "d")


def test_factorized_profiles_reuse_exact_primitive_features() -> None:
    system = refinement_system()
    coarse, fine, _relabeled = refinement_factorizations()
    coarse_profiles = factorized_interface_profiles(
        system,
        coarse,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    fine_profiles = factorized_interface_profiles(
        system,
        fine,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    coarse_core = next(
        profile
        for profile in coarse_profiles
        if profile.block_interface == ("core",)
    )
    fine_core = next(
        profile
        for profile in fine_profiles
        if profile.primitive_interface == ("inside", "aux")
    )
    assert (
        coarse_core.profile.structural_signature()
        == fine_core.profile.structural_signature()
    )


def test_block_relabeling_is_invariant() -> None:
    controls = refinement_controls()
    transport = controls["relabel_transport"]
    assert transport.status is InterfaceTransportStatus.INVARIANT
    assert transport.forward_intervention_audit.exact is True
    assert transport.reverse_intervention_audit.exact is True
    assert (
        transport.source_minimal_interfaces
        == transport.target_minimal_interfaces
        == (("inside",),)
    )


def test_coarse_to_fine_transport_is_refined() -> None:
    controls = refinement_controls()
    transport = controls["refined_transport"]
    assert transport.status is InterfaceTransportStatus.REFINED
    assert transport.source_minimal_interfaces == (("inside", "aux"),)
    assert transport.target_minimal_interfaces == (("inside",),)


def test_fine_to_coarse_transport_is_merged() -> None:
    controls = refinement_controls()
    transport = controls["merged_transport"]
    assert transport.status is InterfaceTransportStatus.MERGED
    assert transport.source_minimal_interfaces == (("inside",),)
    assert transport.target_minimal_interfaces == (("inside", "aux"),)


def test_refinement_retains_several_incomparable_minima() -> None:
    controls = several_minima_controls()
    transport = controls["transport"]
    assert transport.status is InterfaceTransportStatus.REFINED
    assert transport.source_minimal_interfaces == (("left", "right"),)
    assert set(transport.target_minimal_interfaces) == {
        ("left",),
        ("right",),
    }


def test_crosscut_is_obstructed_despite_same_observations() -> None:
    controls = crosscut_controls()
    assert controls["same_observational_signature"] is True
    assert (
        controls["transport"].status
        is InterfaceTransportStatus.OBSTRUCTED
    )
    assert controls["transport"].reason == "no_exact_family_transport"


def test_query_mismatch_is_obstructed() -> None:
    controls = refinement_controls()
    transport = controls["query_mismatch"]
    assert transport.status is InterfaceTransportStatus.OBSTRUCTED
    assert transport.reason == "query_mismatch"


def test_observation_only_transport_remains_unresolved() -> None:
    controls = refinement_controls()
    transport = controls["observational_transport"]
    assert transport.status is InterfaceTransportStatus.UNRESOLVED
    assert transport.reason == "causal_features_unknown"


def test_state_annotations_do_not_change_transport() -> None:
    controls = refinement_controls()
    transport = controls["annotation_transport"]
    assert transport.status is InterfaceTransportStatus.INVARIANT
    assert transport.reason == "equal_concrete_minimal_families"


def test_substrate_mismatch_is_obstructed() -> None:
    system = refinement_system()
    _coarse, fine, _relabeled = refinement_factorizations()
    left = identify_factorized_interfaces(
        system,
        fine,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    changed = BinarySynchronousSystem(
        system_id="changed_initial_support",
        component_ids=system.component_ids,
        transition_rows=system.transition_rows,
        initial_states=((0, 0, 0),),
    )
    right = identify_factorized_interfaces(
        changed,
        fine,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    transport = compare_interface_families(left, right)
    assert transport.status is InterfaceTransportStatus.OBSTRUCTED
    assert transport.reason == "substrate_mismatch"


def test_evidence_contract_mismatch_is_obstructed_when_resolved() -> None:
    system = refinement_system()
    _coarse, fine, _relabeled = refinement_factorizations()
    left = identify_factorized_interfaces(
        system,
        fine,
        OUTFLOW_QUERY,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    right = identify_factorized_interfaces(
        system,
        fine,
        OUTFLOW_QUERY,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON + 1,
    )
    transport = compare_interface_families(left, right)
    assert transport.status is InterfaceTransportStatus.OBSTRUCTED
    assert transport.reason == "evidence_contract_mismatch"


def test_factorized_profile_requires_matching_primitive_order() -> None:
    system = refinement_system()
    bad_order = ComponentFactorization.from_mapping(
        factorization_id="bad_order",
        primitive_ids=("aux", "inside", "outside"),
        blocks={
            "aux": ("aux",),
            "inside": ("inside",),
            "outside": ("outside",),
        },
    )
    with pytest.raises(ValueError, match="primitive order"):
        factorized_interface_profiles(
            system,
            bad_order,
            evidence_mode=EvidenceMode.INTERVENTIONAL,
            horizon=HORIZON,
        )


def test_complete_experiment_passes_without_kill_conditions() -> None:
    result = run_experiment()
    assert result["status"] == "retained"
    assert all(result["case_results"].values())
    assert not any(result["kill_conditions"].values())


def test_artifact_rows_retain_partitions_witnesses_and_families() -> None:
    result = run_experiment()
    assert factorization_rows(result)
    assert any(
        row["row_kind"] == "failure"
        and row["source_factorization_id"] == "crosscut_source"
        for row in block_transport_rows(result)
    )
    assert factorized_profile_rows(result)
    assert {
        row["status"] for row in family_transport_rows(result)
    } >= {"INVARIANT", "REFINED", "MERGED", "OBSTRUCTED", "UNRESOLVED"}
    assert all(row["passed"] for row in negative_control_rows(result))


def test_validation_retains_declared_artifacts(tmp_path: Path) -> None:
    result = retain_process_interface_transport_v0(tmp_path)
    assert result["status"] == "retained"
    expected = {
        "summary.json",
        "factorizations.csv",
        "block_transport.csv",
        "interface_profiles.csv",
        "family_transport.csv",
        "negative_controls.csv",
        "report.md",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected


def test_crosscut_fixture_uses_complete_boolean_product() -> None:
    controls = crosscut_controls()
    system = controls["system"]
    assert set(system.states) == set(itertools.product((0, 1), repeat=4))
