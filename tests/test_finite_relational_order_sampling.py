from pathlib import Path

from omega.adapters.finite_relational.order_sampling import (
    expansion_order_invariant_witness,
    loss_order_fragility_witness,
    loss_order_dependency_witness,
    order_sampling_summary,
    pathological_order_witness,
    two_fact_orders,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_order_sampling import (
    render_report,
    run_finite_relational_order_sampling,
)


def test_loss_comparison_depends_on_declared_fact_order() -> None:
    witness = loss_order_dependency_witness()

    assert witness["classification"] == "dependent"
    verdicts = {row["order_id"]: row["verdict"] for row in witness["rows"]}
    assert verdicts["discrete"] is False
    assert verdicts["local_below_joint"] is False
    assert verdicts["joint_below_local"] is True


def test_expansion_comparison_is_invariant_in_sampled_orders() -> None:
    witness = expansion_order_invariant_witness()

    assert witness["classification"] == "invariant_true"
    assert {row["verdict"] for row in witness["rows"]} == {True}


def test_adjacent_order_flip_is_fragile() -> None:
    witness = loss_order_fragility_witness()

    assert witness["classification"] == "fragile"
    assert witness["adjacent_pairs"] == [["local_below_joint", "joint_below_local"]]


def test_soundness_violation_is_pathological() -> None:
    witness = pathological_order_witness()

    assert witness["classification"] == "pathological"
    assert witness["rows"][0]["soundness_violation"] is True


def test_sampled_orders_are_reflexive_and_transitive() -> None:
    for order in two_fact_orders():
        for fact in order.facts:
            assert order.leq(fact, fact)


def test_order_sampling_summary_calibrates() -> None:
    summary = order_sampling_summary()

    assert summary["protocol_doc"] == "docs/research_notes/omega_theory/order_sampling_harness_protocol_v0.md"
    assert summary["verdict"] == "calibrated"
    assert summary["loss_dependency_witness"]["classification"] == "dependent"
    assert summary["loss_fragility_witness"]["classification"] == "fragile"
    assert summary["pathological_order_witness"]["classification"] == "pathological"
    assert summary["expansion_invariant_witness"]["classification"] == "invariant_true"
    assert summary["kill_conditions_pass"] is True
    assert all(summary["kill_conditions"].values())
    assert "correct fact order" in summary["not_claimed"]


def test_order_sampling_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_order_sampling(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "calibrated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    rows = read_csv(run_root / "order_sampling_rows.csv")
    assert {row["classification"] for row in rows} == {
        "dependent",
        "fragile",
        "pathological",
        "invariant_true",
    }

    report = render_report(result)
    assert "Order Sampling Harness v0 Report" in report
    assert "Loss comparison classification: dependent" in report
    assert "Fragility classification: fragile" in report
