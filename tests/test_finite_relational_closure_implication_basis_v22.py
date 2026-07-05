from pathlib import Path

from omega.adapters.finite_relational import generate_closure_implication_basis_v22
from omega.adapters.finite_relational.closure_implication_basis_v22 import (
    closure_implication_basis_v22_summary,
)
from omega.validation.finite_relational_closure_implication_basis_v22 import (
    render_report,
    run_finite_relational_closure_implication_basis_v22,
)


def test_closure_implication_basis_v22_guard_accounts_all_implications() -> None:
    families = generate_closure_implication_basis_v22()
    summary = closure_implication_basis_v22_summary()
    aggregate = summary["aggregate"]

    assert len(families) == 4
    assert summary["case_count"] == 204
    assert aggregate["implication_count"] == 2567
    assert aggregate["guard_accounted_implication_count"] == 2567
    assert aggregate["classifier_only_implication_count"] == 0
    assert aggregate["residual_implication_count"] == 0
    assert aggregate["unique_seed_implication_count"] == 56
    assert aggregate["unique_guard_implication_count"] == 87
    assert aggregate["seed_antecedent_size_counts"] == {"0": 754, "1": 1813}
    assert aggregate["guard_antecedent_size_counts"] == {"0": 754, "1": 1813}
    assert (
        aggregate["basis_kind_counts"]["process_coherence_profile_guard"] == 202
    )
    assert aggregate["basis_kind_counts"]["step_to_path_guard"] == 444


def test_closure_implication_basis_v22_validation_retains_report(
    tmp_path: Path,
) -> None:
    result = run_finite_relational_closure_implication_basis_v22(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["case_count"] == 204
    assert result["aggregate"]["implication_count"] == 2567
    assert result["aggregate"]["guard_accounted_implication_count"] == 2567
    assert result["aggregate"]["classifier_only_implication_count"] == 0
    assert result["aggregate"]["residual_implication_count"] == 0

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Finite Relational Closure Implication Basis v2.2" in report
    assert "Guard-accounted implications: 2567" in report
    assert "Classifier-only implications: 0" in report
    assert "Residual implications: 0" in report
