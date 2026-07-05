from pathlib import Path

from omega.adapters.finite_relational import (
    adaptive_fixed_world_corridor_summary,
    adaptive_kernel,
    epistemically_load_bearing_actions,
    frozen_kernel,
    generate_adaptive_fixed_world_corridor_study,
    sound_update,
    successors,
    switching_kernel,
    truth_preservation_failures,
)
from omega.adapters.finite_relational.adaptive_fixed_world_corridor import (
    fake_drop_to_m0_update,
)
from omega.validation.finite_relational_adaptive_fixed_world_corridor import (
    render_report,
    run_finite_relational_adaptive_fixed_world_corridor,
)


def _case(case_id: str):
    study = generate_adaptive_fixed_world_corridor_study()
    return next(case for case in study.cases if case.case_id == case_id)


def test_sound_update_preserves_true_model_for_all_retained_cases() -> None:
    study = generate_adaptive_fixed_world_corridor_study()

    assert study.summary()["truth_preservation_failure_count"] == 0
    for case in study.cases:
        assert truth_preservation_failures(case, sound_update) == []


def test_learnable_ambiguity_expands_adaptive_beyond_switching() -> None:
    case = _case("learnable_ambiguity")
    start_info = (case.start, case.model_ids)

    assert case.start not in switching_kernel(case)
    assert start_info in adaptive_kernel(case)
    assert start_info not in frozen_kernel(case)
    assert epistemically_load_bearing_actions(case, start_info) == frozenset({"probe"})


def test_unlearnable_ambiguity_blocks_full_adaptive_start() -> None:
    case = _case("unlearnable_ambiguity")
    start_info = (case.start, case.model_ids)
    adaptive = adaptive_kernel(case)

    assert case.start not in switching_kernel(case)
    assert start_info not in adaptive
    assert (case.start, frozenset({"m0"})) in adaptive
    assert (case.start, frozenset({"m1"})) in adaptive
    assert epistemically_load_bearing_actions(case, start_info) == frozenset()


def test_fake_update_creates_phantom_corridor_state() -> None:
    case = _case("fake_update_phantom_corridor")
    fake_kernel = adaptive_kernel(case, fake_drop_to_m0_update)
    fake_failures = truth_preservation_failures(case, fake_drop_to_m0_update)

    assert ("p1", frozenset({"m0"})) in fake_kernel
    assert "bad" in successors(case, "m1", "p1", "stay0")
    assert any(
        failure["true_model"] == "m1"
        and failure["observed_successor"] == "p1"
        and failure["updated_models"] == ["m0"]
        for failure in fake_failures
    )


def test_adaptive_fixed_world_corridor_summary_targets_are_retained() -> None:
    summary = adaptive_fixed_world_corridor_summary()

    assert summary["case_count"] == 3
    assert summary["learnable_case_count"] == 1
    assert summary["unlearnable_case_count"] == 1
    assert summary["fake_update_case_count"] == 1
    assert summary["truth_preservation_failure_count"] == 0


def test_adaptive_fixed_world_corridor_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_adaptive_fixed_world_corridor(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["case_count"] == 3
    assert result["learnable_case_count"] == 1
    assert result["unlearnable_case_count"] == 1
    assert result["fake_update_case_count"] == 1

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Finite Relational Adaptive Fixed-World Corridor B2.1" in report
    assert "safe learning expands beyond switching" in report
    assert "fabricated identification creates phantom corridor" in report
