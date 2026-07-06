from pathlib import Path

from omega.adapters.finite_relational.compensation_claim import (
    certified_compensation_witness,
    compensation_claim_summary,
    incomplete_compensation_witness,
    phantom_compensation_witness,
    uncertified_compensation_witness,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_compensation_claim import (
    render_report,
    run_finite_relational_compensation_claim,
)


def test_certified_same_frame_cover_defeats_nolp_refusal() -> None:
    witness = certified_compensation_witness()
    verdict = witness["verdict"]

    assert verdict["complete_cover"] is True
    assert verdict["certified"] is True
    assert verdict["certified_compensation"] is True
    assert verdict["nolp_refuses_contraction"] is False
    assert verdict["stability_label"] == "not_sampled"
    assert verdict["frame_scope"] == "same_frame"


def test_uncertified_cover_is_refused() -> None:
    witness = uncertified_compensation_witness()
    verdict = witness["verdict"]

    assert verdict["complete_cover"] is True
    assert verdict["certified"] is False
    assert verdict["certified_compensation"] is False
    assert verdict["nolp_refuses_contraction"] is True


def test_incomplete_cover_is_refused() -> None:
    witness = incomplete_compensation_witness()
    verdict = witness["verdict"]

    assert verdict["complete_cover"] is False
    assert verdict["certified"] is True
    assert verdict["certified_compensation"] is False
    assert verdict["nolp_refuses_contraction"] is True
    assert verdict["uncovered_facts"] == ["repair_capacity"]


def test_phantom_compensation_diverges_from_true_frame() -> None:
    witness = phantom_compensation_witness()

    assert witness["phantom_compensation_diverges"] is True
    assert witness["believed_verdict"]["certified_compensation"] is True
    assert witness["believed_verdict"]["nolp_refuses_contraction"] is False
    assert witness["true_verdict"]["certified_compensation"] is False
    assert witness["true_verdict"]["nolp_refuses_contraction"] is True


def test_compensation_claim_summary_retains_nolp_v0() -> None:
    summary = compensation_claim_summary()

    assert summary["protocol_doc"] == "docs/research_notes/omega_theory/compensation_claim_protocol_v0.md"
    assert summary["verdict"] == "retained"
    assert summary["kill_conditions_pass"] is True
    assert summary["kill_conditions"] == {
        "incomplete_cover_refused": True,
        "uncertified_cover_refused": True,
        "phantom_compensation_diverges": True,
        "same_frame_only": True,
    }
    assert "same-frame nonrecoverable contraction is refused" in summary["nolp_v0_read"]
    assert "cross-valuer compensation" in summary["not_claimed"]


def test_compensation_claim_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_compensation_claim(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "retained"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    rows = read_csv(run_root / "compensation_verdicts.csv")
    assert {row["case"] for row in rows} == {
        "certified_same_frame_cover",
        "uncertified_cover",
        "incomplete_cover",
        "phantom_believed",
        "phantom_true",
    }

    report = render_report(result)
    assert "CompensationClaim / NOLP v0 Report" in report
    assert "Phantom compensation diverges: True" in report
    assert "Kill conditions pass: True" in report
