from __future__ import annotations

import json
from dataclasses import replace

import pytest

from omega.agency_diamond.examples import MID_SCALE_HORIZONS, canonical_battery, midscale_cases, thermostat
from omega.agency_diamond.metrics import evaluate_case
from omega.agency_diamond.model import simulate_live, simulate_replay, validate_system
from omega.agency_diamond.run_midscale import run_midscale
from omega.validation.agency_diamond_midscale import run_agency_diamond_midscale


EXPECTED_SYSTEM_IDS = {
    "passive_attractor",
    "driven_cycle",
    "open_loop_controller",
    "thermostat",
    "adaptive_controller",
    "self_restoring_controller",
    "cooperative_controller",
    "dominant_horizon_controller",
}


def test_midscale_battery_covers_expected_cases_and_separates_nulls():
    systems = canonical_battery()
    assert {system.system_id for system in systems} == EXPECTED_SYSTEM_IDS

    cases = midscale_cases()
    assert len(cases) == len(EXPECTED_SYSTEM_IDS) * len(MID_SCALE_HORIZONS)

    metrics = [evaluate_case(case) for case in cases]
    by_system = {
        system_id: [metric for metric in metrics if metric.system_id == system_id]
        for system_id in EXPECTED_SYSTEM_IDS
    }

    assert all(metric.control_reach_count == 0 for metric in by_system["passive_attractor"])
    assert all(metric.control_reach_count == 0 for metric in by_system["driven_cycle"])
    assert any(metric.recurrence_detected for metric in by_system["driven_cycle"])

    assert all(
        metric.feedback_advantage == 0
        for metric in by_system["open_loop_controller"]
    )
    assert any(
        metric.control_reach_count > 0
        for metric in by_system["open_loop_controller"]
    )

    assert all(
        metric.reflexive_advantage is None
        for metric in by_system["thermostat"]
    )
    assert any(
        metric.feedback_advantage > 0
        for metric in by_system["thermostat"]
    )

    assert any(
        metric.reflexive_advantage is not None and metric.reflexive_advantage > 0
        for metric in by_system["self_restoring_controller"]
    )
    assert any(
        metric.joint_effect_delta is not None and metric.joint_effect_delta > 0
        for metric in by_system["cooperative_controller"]
    )
    assert any(
        metric.joint_effect_delta is not None and metric.joint_effect_delta < 0
        for metric in by_system["dominant_horizon_controller"]
    )


def test_live_vs_replay_uses_nominal_actions_as_matched_open_loop_control():
    system = thermostat()
    nominal_trace = simulate_live(system, scenario="nominal", horizon=2)
    assert nominal_trace.actions == ("idle", "idle")

    live_trace = simulate_live(system, scenario="cold_start", horizon=2)
    replay_trace = simulate_replay(
        system,
        scenario="cold_start",
        replay_actions=nominal_trace.actions,
    )

    assert live_trace.final_state == "ok"
    assert replay_trace.final_state == "fail"


def test_model_validation_rejects_malformed_surfaces():
    system = thermostat()

    with pytest.raises(ValueError, match="undeclared observations"):
        validate_system(replace(system, observe={**system.observe, "ok": "unknown"}))

    bad_transition = {
        scenario: {
            state: dict(by_action)
            for state, by_action in by_state.items()
        }
        for scenario, by_state in system.transition.items()
    }
    bad_transition["nominal"]["ok"]["idle"] = "outside"
    with pytest.raises(ValueError, match="undeclared targets"):
        validate_system(replace(system, transition=bad_transition))

    with pytest.raises(ValueError, match="live policy"):
        validate_system(replace(system, live_policy={"ok": "idle"}))


def test_midscale_runner_writes_retained_artifacts(tmp_path):
    summary = run_midscale(tmp_path)

    assert summary["status"] == "PASS"
    assert summary["case_count"] == 40
    assert all(summary["prespecified_checks"].values())

    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    assert metrics_path.exists()
    assert report_path.exists()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert len(metrics) == 40
    assert "Synthetic finite agency-layer pilot only" in report_path.read_text(
        encoding="utf-8"
    )


def test_validation_entrypoint_uses_timestamped_run_root(tmp_path):
    summary = run_agency_diamond_midscale(out_root=tmp_path)

    assert summary["status"] == "PASS"
    assert summary["case_count"] == 40
    summary_path = next(tmp_path.glob("*/summary.json"))
    assert json.loads(summary_path.read_text(encoding="utf-8"))["status"] == "PASS"
