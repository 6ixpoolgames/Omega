from pathlib import Path

from omega.adapters.finite_relational.bounded_behavioral_logic import (
    FormulaKind,
    bounded_behavioral_logic_summary,
    characteristic_correspondence_witness,
    characteristic_formula,
    derived_basis_parity_witness,
    forcing_grammar_system,
    formula_uses_disjunction,
    grammar_adequacy_witness,
    presentation_witness,
    signature_refines,
    signature_satisfies,
    structural_state_parity_witness,
)
from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    behavior_signature,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_bounded_behavioral_logic import (
    render_report,
    run_finite_relational_bounded_behavioral_logic,
)


def test_structural_signature_refinement_matches_state_relation() -> None:
    witness = structural_state_parity_witness()

    assert witness["ordered_state_pairs"] > 0
    assert witness["mismatches"] == []
    assert witness["parity"] is True


def test_data_derived_basis_matches_representative_basis() -> None:
    witness = derived_basis_parity_witness()

    assert witness["duplicate_representatives_removed"] > 0
    assert witness["mismatches"] == []
    assert witness["parity"] is True


def test_characteristic_formula_matches_structural_refinement() -> None:
    witness = characteristic_correspondence_witness()

    assert witness["ordered_type_pairs"] > 0
    assert witness["mismatches"] == []
    assert witness["correspondence"] is True


def test_multi_outcome_characteristic_formula_uses_disjunction() -> None:
    system = forcing_grammar_system()
    source = behavior_signature(system, "source_ab", 1)
    outsider = behavior_signature(system, "outsider_c", 1)
    formula = characteristic_formula(source)

    assert formula.kind is FormulaKind.AND
    assert formula_uses_disjunction(formula) is True
    assert signature_satisfies(source, formula) is True
    assert signature_refines(source, outsider) is False
    assert signature_satisfies(outsider, formula) is False


def test_grammar_audit_detects_need_for_disjunction() -> None:
    witness = grammar_adequacy_witness()

    assert witness["target_multi_outcome_mismatch_present"] is True
    assert witness["conjunction_only_sufficient"] is False
    assert witness["disjunction_required_on_fixture"] is True
    assert witness["full_grammar_mismatches"] == []
    assert witness["full_grammar_recovers_preorder"] is True


def test_relabeling_preserves_signature_profile_and_certificate() -> None:
    witness = presentation_witness()

    assert witness == {
        "horizon": 2,
        "signatures_equal": True,
        "profiles_equal": True,
        "certificate_truth_preserved": True,
    }


def test_summary_separates_correctness_from_discovery() -> None:
    summary = bounded_behavioral_logic_summary()

    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert summary["evidence_classification"]["risky_prediction"] == []
    assert summary["predecessor_evidence_reclassification"]["risky_retained_result"] == [
        "adaptive fixed-world behavior strictly refines switching behavior"
    ]


def test_validation_retains_machine_readable_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_bounded_behavioral_logic(out_root=tmp_path)

    assert result["status"] == "PASS"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "case_results.csv").exists()
    assert (run_root / "certificate_correspondence.csv").exists()
    assert (run_root / "grammar_adequacy.csv").exists()
    assert (run_root / "report.md").exists()

    grammar_rows = read_csv(run_root / "grammar_adequacy.csv")
    assert {row["grammar"] for row in grammar_rows} == {
        "conjunction_only",
        "with_disjunction",
    }

    report = render_report(result)
    assert "Bounded Behavioral Logic v0 Report" in report
    assert "Disjunction required on retained fixture: True" in report
