from __future__ import annotations

import json

from omega.agency_diamond.baselines import (
    find_baseline_collisions,
    required_collision_status,
    strictness_status,
    strictness_witnesses,
)
from omega.agency_diamond.examples import midscale_cases
from omega.agency_diamond.generated import evaluate_generated_variants
from omega.agency_diamond.metrics import evaluate_case
from omega.agency_diamond.run_hardening import run_hardening
from omega.agency_diamond.transport import transport_pilot
from omega.validation.agency_diamond_hardening import run_agency_diamond_hardening


def test_baseline_collision_and_strictness_witnesses_pass():
    metrics = [evaluate_case(case) for case in midscale_cases()]

    collisions = find_baseline_collisions(metrics)
    collision_status = required_collision_status(collisions)
    strictness = strictness_witnesses(metrics)

    assert all(collision_status.values())
    assert all(strictness_status(strictness).values())
    assert {
        witness.name
        for witness in strictness
    } == {
        "recurrence_does_not_imply_feedback_advantage",
        "control_does_not_imply_feedback_advantage",
        "feedback_advantage_does_not_imply_reflexive_maintenance",
        "live_success_does_not_determine_joint_effect",
        "joint_effect_does_not_imply_reflexive_maintenance",
    }


def test_generated_variants_preserve_profiles_under_relabel_and_decoys():
    result = evaluate_generated_variants(seeds=(11, 17, 23))

    assert result["variant_count"] == 24
    assert result["case_count"] == 120
    assert result["all_profiles_preserved"] is True


def test_transport_pilot_accepts_sound_quotient_and_rejects_bad_merges():
    result = transport_pilot()

    assert result["all_transport_checks_passed"] is True
    checks = result["checks"]
    assert checks["positive_quotient_constructible"] is True
    assert checks["positive_profile_preserved"] is True
    assert checks["incompatible_need_merge_rejected"] is True
    assert checks["cold_hot_merge_rejected"] is True


def test_hardening_runner_writes_summary_and_report(tmp_path):
    summary = run_hardening(tmp_path)

    assert summary["status"] == "PASS"
    assert summary["decision_gate"] == {
        "required_baseline_collisions_found": True,
        "strictness_witnesses_passed": True,
        "generated_profiles_preserved": True,
        "transport_controls_passed": True,
    }
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "report.md").exists()
    retained = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert retained["status"] == "PASS"


def test_hardening_validation_entrypoint_uses_timestamped_run_root(tmp_path):
    summary = run_agency_diamond_hardening(out_root=tmp_path)

    assert summary["status"] == "PASS"
    summary_path = next(tmp_path.glob("*/summary.json"))
    assert json.loads(summary_path.read_text(encoding="utf-8"))["status"] == "PASS"
