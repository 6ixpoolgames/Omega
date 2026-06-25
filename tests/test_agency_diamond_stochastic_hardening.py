from pathlib import Path

from omega.agency_diamond.run_stochastic_hardening import run_stochastic_hardening
from omega.agency_diamond.stochastic_hardening import (
    constant_observation_ablation,
    false_positive_search,
    fragile_average_feedback_system,
    robust_ambiguity_summary,
    robust_profile,
    stochastic_ablation_probe_summary,
    stochastic_hardening_summary,
)
from omega.agency_diamond.stochastic_examples import (
    STOCHASTIC_HORIZONS,
    stochastic_blind_cases,
)
from omega.agency_diamond.stochastic_metrics import evaluate_stochastic_system
from omega.validation.agency_diamond_stochastic_hardening import (
    run_agency_diamond_stochastic_hardening,
)


def test_false_positive_search_retains_deformer_controls() -> None:
    cases = stochastic_blind_cases()
    metrics = [
        evaluate_stochastic_system(
            case.system,
            horizon=horizon,
            case_id=f"blind__seed{case.seed}_h{horizon}",
        )
        for case in cases
        for horizon in STOCHASTIC_HORIZONS
    ]
    result = false_positive_search(metrics, tuple(case.system for case in cases))
    assert all(witness.passed for witness in result["witnesses"])
    retained = result["retained_false_positive_controls"]
    assert retained["high_live_without_feedback"] is not None
    assert retained["stochasticity_without_control"] is not None
    assert retained["feedback_without_reflexive"] is not None
    assert retained["negative_joint_with_feedback"] is not None


def test_stochastic_ablation_probes_are_causally_sensitive() -> None:
    systems = tuple(case.system for case in stochastic_blind_cases())
    result = stochastic_ablation_probe_summary(systems)
    assert all(result["probe_status"].values())
    obs = next(
        witness
        for witness in result["witnesses"]
        if witness["name"] == "stochastic_observation_ablation_reduces_feedback"
    )
    assert obs["details"]["original_feedback"] != obs["details"]["ablated_feedback"]

    source = next(system for system in systems if system.family == "stochastic_feedback")
    ablated = constant_observation_ablation(source)
    assert ablated is not None
    assert len(ablated.observations) == 1


def test_robust_ambiguity_profiles_keep_average_and_worst_case_separate() -> None:
    result = robust_ambiguity_summary()
    assert all(result["hypothesis_status"].values())
    fragile = result["fragile_average_metric"]
    robust_fragile = result["profiles"]["fragile_average_feedback_not_robust"]
    assert fragile["feedback_advantage"] != "0"
    assert robust_fragile["robust_feedback_advantage"] == "0"
    assert result["profiles"]["robust_feedback_positive"]["robust_feedback_advantage"] != "0"
    assert result["profiles"]["robust_reflexive_positive"]["robust_reflexive_advantage"] != "0"


def test_fragile_average_feedback_system_is_the_robust_negative_control() -> None:
    system = fragile_average_feedback_system()
    average = evaluate_stochastic_system(system, horizon=1)
    robust = robust_profile(system, horizon=1)
    assert average.feedback_advantage > 0
    assert robust.robust_feedback_advantage == 0


def test_stochastic_hardening_summary_and_validation_retain_outputs(tmp_path: Path) -> None:
    summary = stochastic_hardening_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())

    direct = run_stochastic_hardening(tmp_path / "direct")
    assert direct["status"] == "PASS"
    assert (tmp_path / "direct" / "summary.json").exists()
    assert (tmp_path / "direct" / "report.md").exists()

    validation = run_agency_diamond_stochastic_hardening(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    run_dirs = [path for path in (tmp_path / "validation").iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "summary.json").exists()
    assert (run_dirs[0] / "report.md").exists()
