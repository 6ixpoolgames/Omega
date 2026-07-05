from pathlib import Path

from omega.adapters.finite_relational.closure_attribution_v21 import (
    closure_attribution_v21_summary,
)
from omega.validation.finite_relational_closure_guard_v215 import (
    render_report,
    run_finite_relational_closure_guard_v215,
)


def test_closure_guard_v215_proof_backs_all_v21_surplus() -> None:
    summary = closure_attribution_v21_summary()
    aggregate = summary["aggregate"]

    assert summary["case_count"] == 204
    assert aggregate["surplus_fact_count"] == 2567
    assert aggregate["theorem_backed_fact_count"] == 2567
    assert aggregate["classifier_only_fact_count"] == 0
    assert aggregate["residual_fact_count"] == 0
    assert aggregate["proof_status_counts"] == {"guard_verified": 2567}
    assert (
        aggregate["theorem_counts"][
            "closure.guard.process_coherence_entails_bounded_profile_invariance"
        ]
        == 202
    )
    assert (
        aggregate["theorem_counts"][
            "closure.guard.step_lifting_implies_bounded_path_lifting"
        ]
        == 444
    )


def test_closure_guard_v215_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_closure_guard_v215(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["case_count"] == 204
    assert result["aggregate"]["surplus_fact_count"] == 2567
    assert result["aggregate"]["theorem_backed_fact_count"] == 2567
    assert result["aggregate"]["classifier_only_fact_count"] == 0
    assert result["aggregate"]["residual_fact_count"] == 0

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Finite Relational Closure Guard Attribution v2.1.5" in report
    assert "Theorem-backed facts: 2567" in report
    assert "Classifier-only facts: 0" in report
    assert "Residual facts: 0" in report
