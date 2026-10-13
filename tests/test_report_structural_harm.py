import hashlib
import json

import pytest

from scripts.report_structural_harm import summarize


def _policy(pid, surplus, score, exposure=0.2):
    return {
        "id": pid, "canonical_id": pid,
        "controller": {"id": pid, "threshold": 1, "surplus": surplus, "service_if_worn": False},
        "bits": {str(h): {"present": score, "post_fault": score - 0.1}
                 for h in (1, 4, 16, 64, 256)},
        "rates": {"present": score, "post_fault": score - 0.1},
        "nonrandom": True, "hash": pid,
        "readouts": {"stationary_exposure": exposure, "hardware64": 1.0,
                     "active64": 1.0, "function64": 1.0},
    }


def _result(case, mode, hazard, cadence, policy, protocol_hash):
    return {"status": "complete", "case_id": case, "mode": mode, "hazard": hazard,
            "cadence": cadence, "protocol_hash": protocol_hash, "input_hash": case,
            "policies": [policy], "rate_winners": [policy["id"]], "states": 3840,
            "unique_models": 1, "winners": {str(h): [policy["id"]]
                for h in (1, 4, 16, 64, 256)}}


def _batch(tmp_path):
    specs = [
        ("fast-low", "fast", .02, "service", 5., .2),
        ("fast-high", "fast", .04, "export", 6., .5),
        ("loss-low", "hardware_loss", .02, "export", 4., .2),
        ("loss-high", "hardware_loss", .04, "service", 5., .1),
    ]
    cases, results = [], []
    for case_id, mode, hazard, response, score, exposure in specs:
        policy = _policy(case_id, response, score, exposure)
        cases.append({"id": case_id, "status": "frozen_before_scientific_ranking",
                      "mode": mode, "hazard": hazard, "cadence": .25,
                      "rank_tolerance": 1e-8, "horizons": [1, 4, 16, 64, 256],
                      "candidates": [{"id": case_id, **policy["controller"]}]})
        results.append((case_id, mode, hazard, .25, policy))
    protocol = {"schema": "omega-structural-harm/1",
                "status": "frozen_before_scientific_ranking", "cases": cases,
                "predictions": {"H1": "", "C1": "", "R1": ""},
                "adverse": {"E1": "", "S1": ""}}
    protocol_path = tmp_path / "PROTOCOL.json"
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    paths = []
    for index, spec in enumerate(results):
        row = _result(*spec, protocol_hash)
        path = tmp_path / f"result-{index}.json"
        path.write_text(json.dumps(row), encoding="utf-8")
        paths.append(path)
    return paths, protocol_path


def _add_fast_high_service_reversal(paths, protocol_path):
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    case = next(c for c in protocol["cases"] if c["id"] == "fast-high")
    service = _policy("fast-high-service", "service", 5.)
    case["candidates"].append(service["controller"])
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    result_path = next(p for p in paths if json.loads(p.read_text(encoding="utf-8"))["case_id"] == "fast-high")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    service["bits"] = {str(h): {"present": 7. if h == 1 else 5., "post_fault": 4.9}
                        for h in (1, 4, 16, 64, 256)}
    service["rates"] = {"present": 1., "post_fault": .9}
    result["policies"].append(service)
    result["unique_models"] = 2
    result["winners"] = {"1": ["fast-high-service"],
                         **{str(h): ["fast-high"] for h in (4, 16, 64, 256)}}
    result["rate_winners"] = ["fast-high"]
    result["protocol_hash"] = protocol_hash
    for path in paths:
        row = json.loads(path.read_text(encoding="utf-8"))
        row["protocol_hash"] = protocol_hash
        if row["case_id"] == "fast-high":
            row = result
        path.write_text(json.dumps(row), encoding="utf-8")


def test_report_scores_primary_root_and_writes_compact_outputs(tmp_path):
    files, protocol_path = _batch(tmp_path)
    output = tmp_path / "report"
    summary = summarize(files, output, protocol_path)
    assert (output / "SUMMARY.json").exists()
    assert (output / "RESULTS.md").exists()
    fast = next(c for c in summary["cases"] if c["case_id"] == "fast-low")
    assert fast["horizon_scores"]["64"]["winner_ids"] == ["fast-low"]
    assert fast["horizon_scores"]["64"]["best_bits_post_fault"] == pytest.approx(4.9)
    assert "physical_readouts" in summary["interpretation"]
    assert any(row["response_differs"] for row in summary["audits"]["mode_consequence"])
    assert summary["registered_claims"]["R1_higher_hazard_stronger_service"]["status"] == "supported"
    assert summary["registered_claims"]["E1_stationary_exposure_increase"]["status"] == "alert"


def test_report_rejects_mismatched_protocol_hash(tmp_path):
    paths, protocol_path = _batch(tmp_path)
    row = json.loads(paths[0].read_text(encoding="utf-8"))
    row["protocol_hash"] = "wrong"
    paths[0].write_text(json.dumps(row), encoding="utf-8")
    with pytest.raises(ValueError, match="protocol_hash does not match"):
        summarize(paths, tmp_path / "report", protocol_path)


def test_report_rejects_missing_registered_case(tmp_path):
    paths, protocol_path = _batch(tmp_path)
    with pytest.raises(ValueError, match="result cases differ"):
        summarize(paths[:-1], tmp_path / "report", protocol_path)


def test_hazard_response_uses_higher_minus_lower_service_order(tmp_path):
    paths, protocol_path = _batch(tmp_path)
    summary = summarize(paths, tmp_path / "report", protocol_path)
    fast = [row for row in summary["audits"]["hazard_response"] if row["mode"] == "fast"]
    loss = [row for row in summary["audits"]["hazard_response"] if row["mode"] == "hardware_loss"]
    assert all(row["pairwise_orders"] == ["lower"] for row in fast)
    assert all(row["pairwise_orders"] == ["higher"] for row in loss)


def test_h1_covers_both_hazards_and_unregistered_cadence_is_unassessed(tmp_path):
    paths, protocol_path = _batch(tmp_path)
    _add_fast_high_service_reversal(paths, protocol_path)
    summary = summarize(paths, tmp_path / "report", protocol_path)
    h1 = summary["registered_claims"]["H1_horizon_service_non_decrease"]
    assert h1["decrease_count"] > 0
    high_hazard_replays = [r for r in summary["audits"]["cadence_replay"]
                           if r["hazard"] == .04]
    assert high_hazard_replays
    assert all(r["audit_scope"] == "not_registered" for r in high_hazard_replays)
    assert all(r["winner_identity_stable"] is None for r in high_hazard_replays)
