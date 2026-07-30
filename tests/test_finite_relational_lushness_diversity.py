from pathlib import Path

import pytest

from omega.adapters.finite_relational.lushness_diversity import (
    OrderVerdict,
    cardinality_disagreement_witness,
    compare_effective_freedom,
    compare_profiles,
    duplicate_structure,
    duplicate_witness,
    effective_freedom_witness,
    lushness_diversity_summary,
    negative_controls,
    nonfungible_witness,
    pairwise_shadow_witness,
    pairwise_structures,
    paperclipper_witness,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_lushness_diversity import (
    render_report,
    run_finite_relational_lushness_diversity,
)


def test_duplicate_trajectory_adds_no_structural_profile() -> None:
    witness = duplicate_witness()

    assert witness["token_count_increases"] is True
    assert witness["duplicate_adds_no_profile"] is True
    assert witness["profile_verdict"] == OrderVerdict.EQUIVALENT.value


def test_nonfungible_attribute_strictly_expands_profile() -> None:
    witness = nonfungible_witness()

    assert witness["extension_strictly_refines"] is True
    assert witness["strict_new_attributes"] == ["translation"]
    assert witness["profile_verdict"] == OrderVerdict.RIGHT_REFINES.value


def test_cardinality_and_coverage_issue_different_verdicts() -> None:
    witness = cardinality_disagreement_witness()

    assert witness["same_extension_count"] is True
    assert witness["cardinality_strict_but_profile_equal_for_duplicate"] is True
    assert witness["same_count_different_profile_verdict"] is True


def test_pairwise_shadow_does_not_determine_joint_realizability() -> None:
    witness = pairwise_shadow_witness()

    assert witness["one_skeletons_equal"] is True
    assert witness["singleton_pair_profiles_equal"] is True
    assert witness["filled_is_flag"] is True
    assert witness["hollow_is_flag"] is False
    assert witness["filled_triple_realizable"] is True
    assert witness["hollow_triple_realizable"] is False
    assert witness["hollow_unrealizable_profile_rejected"] is True
    assert "triadic_coordination" in witness["filled_triple_profile"]


def test_unrealizable_family_has_no_profile() -> None:
    _filled, hollow = pairwise_structures()

    with pytest.raises(ValueError, match="not jointly realizable"):
        hollow.profile(frozenset({"a", "b", "c"}))


def test_effective_freedom_and_coverage_agree_only_when_linked() -> None:
    witness = effective_freedom_witness()

    assert witness["agreement"] == {
        "profile_verdict": OrderVerdict.RIGHT_REFINES.value,
        "effective_verdict": OrderVerdict.RIGHT_REFINES.value,
        "orders_agree": True,
    }
    assert witness["coverage_only"]["profile_verdict"] == OrderVerdict.RIGHT_REFINES.value
    assert witness["coverage_only"]["effective_verdict"] == OrderVerdict.EQUIVALENT.value
    assert witness["coverage_only"]["orders_diverge"] is True
    assert witness["preference_only"]["profile_verdict"] == OrderVerdict.EQUIVALENT.value
    assert (
        witness["preference_only"]["effective_verdict"]
        == OrderVerdict.RIGHT_REFINES.value
    )
    assert witness["preference_only"]["orders_diverge"] is True


def test_effective_freedom_is_an_incomplete_quasiorder() -> None:
    from omega.adapters.finite_relational.lushness_diversity import Preference

    preferences = (
        Preference("left", (("a", 2), ("b", 1))),
        Preference("right", (("a", 1), ("b", 2))),
    )

    assert (
        compare_effective_freedom(
            frozenset({"a"}),
            frozenset({"b"}),
            preferences,
        )
        is OrderVerdict.INCOMPARABLE
    )


def test_paperclipper_local_gain_and_global_contraction_coexist() -> None:
    witness = paperclipper_witness()

    assert witness["paperclipper_prefers_excision"] is True
    assert witness["cooperation_strictly_lusher"] is True
    assert witness["same_attribute_grammar"] is True
    assert witness["paperclip_preference_verdict"] == OrderVerdict.RIGHT_REFINES.value
    assert witness["profile_verdict"] == OrderVerdict.LEFT_REFINES.value


def test_negative_controls_keep_layers_separate() -> None:
    controls = negative_controls()

    assert controls["relabeling_preserves_profile"] is True
    assert controls["scalar_shadow"]["primary_verdict"] == OrderVerdict.INCOMPARABLE.value
    assert controls["scalar_shadow"]["scalar_order_flips"] is True
    assert controls["scalar_shadow"]["primary_verdict_remains_incomparable"] is True
    assert controls["submodularity"]["marginal_profile_submodular"] is True
    assert controls["submodularity"]["joint_augmented_profile_submodular"] is False
    assert controls["submodularity"]["joint_complementarity_kept_separate"] is True
    assert controls["unrealizable_profile_rejected"] is True
    assert controls["negative_controls_pass"] is True


def test_profile_order_is_partial_not_scalar() -> None:
    assert (
        compare_profiles(
            frozenset({"alpha"}),
            frozenset({"beta"}),
        )
        is OrderVerdict.INCOMPARABLE
    )
    assert (
        compare_profiles(
            frozenset({"alpha", "beta"}),
            frozenset({"alpha"}),
        )
        is OrderVerdict.LEFT_REFINES
    )


def test_structural_relabeling_preserves_duplicate_profile() -> None:
    original = duplicate_structure()
    relabeled = original.relabel(
        {"original": "renamed_original", "copy": "renamed_copy"},
        structure_id="renamed",
    )

    assert original.profile(frozenset({"original", "copy"})) == relabeled.profile(
        frozenset({"renamed_original", "renamed_copy"})
    )


def test_summary_retains_only_when_all_preregistered_cases_pass() -> None:
    summary = lushness_diversity_summary()

    assert summary["protocol_doc"].endswith("lushness_diversity_protocol_v0.md")
    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert summary["negative_controls"]["negative_controls_pass"] is True
    assert "universal lushness" in summary["not_claimed"]
    assert "paperclipper defeat" in summary["not_claimed"]


def test_validation_retains_machine_readable_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_lushness_diversity(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "retained"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "case_results.csv").exists()
    assert (run_root / "profiles.csv").exists()
    assert (run_root / "report.md").exists()

    case_rows = read_csv(run_root / "case_results.csv")
    assert len(case_rows) == 6
    assert {row["passes"] for row in case_rows} == {"True"}

    profile_rows = read_csv(run_root / "profiles.csv")
    assert {row["case"] for row in profile_rows} == {
        "duplicate_base",
        "duplicate_extension",
        "nonfungible_base",
        "nonfungible_extension",
        "paperclipper_cooperative",
        "paperclipper_excisive",
    }

    report = render_report(result)
    assert "Lushness Diversity Pilot v0 Report" in report
    assert "Verdict: retained" in report
    assert "Hollow structure is flag: False" in report
