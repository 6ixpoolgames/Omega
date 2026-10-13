import hashlib
import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "report_reserve_batch.py"
spec = importlib.util.spec_from_file_location("reserve_report", MODULE)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def policy(pid, canonical, bits, *, nonconstant=False, rate=0.0, root="reference"):
    return {"id": pid, "canonical_id": canonical, "rank_root": root,
            "bits": {"1": {root: bits}}, "limiting": {root: {"rate": rate, "offset": 0}},
            "nonconstant_reachable": nonconstant,
            "audit_surface": [{"active": 0, "worn": 0, "response": [0, 1]},
                              {"active": 1, "worn": 0, "response": [1, 0]},
                              {"active": 2, "worn": 0, "response": [0, 1]},
                              {"active": 4, "worn": 0, "response": [0, 1]}]}


def test_scores_use_selected_root_and_deduplicate_aliases():
    result = {"winners": {"1": ["a"]}, "rate_winners": ["a", "b"], "policies": [
        policy("a", "a", 5, rate=2), policy("alias", "a", 5, rate=2),
        {**policy("b", "b", 3, rate=2), "bits": {"1": {"other": 99, "reference": 3}}}]}
    scored = report._score_case(result)
    assert scored["canonical_policy_count"] == 2
    assert scored["horizon_scores"]["1"]["winner_ids"] == ["a"]
    assert scored["rate_winner_regret"]["1"]["regret_by_rate_winner"] == {"a": 0, "b": 2}


def test_strict_gain_uses_explicit_reachable_flag_and_excludes_inactive_surface():
    result = {"policies": [policy("constant", "constant", 4),
                            policy("nonconstant", "nonconstant", 4, nonconstant=True)]}
    assert report._strict_gain(result)["1"]["strict_gain"] is False
    result["policies"][1]["bits"]["1"]["reference"] = 4.100001
    assert report._strict_gain(result)["1"]["strict_gain"] is True
    sig = report._response_signature(result["policies"][1])
    assert all(active > 0 and active+worn <= 3 for active, worn, _ in sig)


def test_service_partial_order_uses_only_common_reachable_support():
    a = policy("a", "a", 0)
    b = policy("b", "b", 0)
    a["audit_surface"] = [{"active": 0, "worn": 0, "response": [0, 1]},
                           {"active": 1, "worn": 0, "response": [1, 0]},
                           {"active": 2, "worn": 0, "response": [1, 0]},
                           {"active": 3, "worn": 0, "response": [0, 1], "reachable": False},
                           {"active": 4, "worn": 0, "response": [0, 1]}]
    b["audit_surface"] = [{"active": 0, "worn": 0, "response": [1, 0]},
                           {"active": 1, "worn": 0, "response": [0, 1]},
                           {"active": 2, "worn": 0, "response": [0, 1]},
                           {"active": 4, "worn": 0, "response": [1, 0]}]
    assert report._surface_order(a, b) == "higher"
    assert report._surface_order(b, a) == "lower"
    assert all(active != 3 for active, _, _ in report._response_signature(a))


def test_frozen_registration_checks_actual_protocol_bytes(tmp_path):
    protocol = tmp_path / "case.json"
    protocol.write_text("{}", encoding="utf-8")
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    reg = {"status": "frozen_before_scientific_ranking", "tolerance": 1e-8, "cases": [
        {"id": str(i), "law_id": "law", "cadence": .25, "file": "case.json", "sha256": digest}
        for i in range(9)]}
    report._validate_registration(tmp_path / "registration.json", reg)
    reg["cases"][0]["sha256"] = "bad"
    try:
        report._validate_registration(tmp_path / "registration.json", reg)
    except ValueError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("changed registered protocol was accepted")


def test_adaptation_audits_use_claim_direction_and_all_primary_horizons():
    def case(law, cadence, policies):
        return {"law_id": law, "cadence": cadence,
                "winners": {h: [p["canonical_id"]] for h, p in policies.items()},
                "policies": list(policies.values())}

    def winner(pid, service, active=1, exposure=1):
        p = policy(pid, pid, 1, nonconstant=True)
        p["audit_surface"] = [{"active": 1, "worn": 0, "response": [service, 1-service], "reachable": True}]
        p["readouts"] = {"active64": active, "exposure64": exposure, "stationary_exposure": exposure}
        return p

    data = {}
    horizons = ("1", "4", "16", "64", "256")
    for law, services, active, exposure in (("independent_002", [0, .2, .4, .6, .8], 1, 2),
                                             ("correlated_002", [.1, .3, .5, .7, .9], 2, 3),
                                             ("independent_004", [.2, .4, .6, .8, 1], 3, 5),
                                             ("absorbing", [.1, .3, .5, .7, .9], 0, 1),
                                             ("no_shock", [0, .2, .4, .6, .8], 2, 1)):
        policies = {h: winner(f"policy-{h}", service, active, exposure)
                    for h, service in zip(horizons, services)}
        # Canonical IDs here are horizon-specific, as selected fixed candidates are in the runner.
        data[law] = case(law, .25, policies)
    audits = report._batch_audits(data)
    assert all(x["status"] == "higher" for x in audits["matched_risk_winner_surfaces"])
    assert all(x["status"] == "higher" for x in audits["hazard_winner_surfaces"])
    assert len(audits["horizon_winner_surfaces"]) == 20
    assert all(x["status"] == "higher" for x in audits["horizon_winner_surfaces"])
    assert [x["horizon"] for x in audits["sentinel_winner_surfaces"]] == list(horizons)
    assert all(x["active64_prediction"] == "fail" for x in audits["sentinel_winner_surfaces"])
    assert all(x["stationary_difference_high_minus_low_range"] == [3, 3]
               for x in audits["exposure_diagnostic"]["winner_pairs"])
    assert len(audits["exposure_diagnostic"]["fixed_policy_replay"]) == 5
    assert "independent_002_policy_row" not in audits["exposure_diagnostic"]["fixed_policy_replay"][0]


def test_cadence_comparator_self_comparison_is_labeled():
    policies = [policy("same", "same", 2)]
    raw = {}
    for cadence in (.125, .25, .5):
        raw[f"n{cadence}"] = {"law_id": "no_shock", "cadence": cadence,
            "winners": {"1": ["same"]}, "policies": policies,
            "fixed_comparators": {"idle": ["same"], "service": [], "export": [], "best_nonrandom": {"1": "same"}}}
    audits = report._batch_audits(raw)
    findings = [x["finding"] for x in audits["fixed_primary_policy_signs"] if x["winner_id"] == x["comparator_id"]]
    assert findings and set(findings) == {"self_comparison"}


def test_summary_matches_registered_case_and_keeps_zeros(tmp_path):
    regdir = tmp_path / "registration"
    regdir.mkdir()
    cases = []
    for i in range(9):
        protocol = regdir / f"c{i}.json"
        payload = {"case": i}
        protocol.write_text(json.dumps(payload), encoding="utf-8")
        cases.append({"id": f"c{i}", "law_id": "law", "cadence": .25,
                      "file": protocol.name, "sha256": hashlib.sha256(protocol.read_bytes()).hexdigest()})
    regfile = regdir / "registration.json"
    regfile.write_text(json.dumps({"status": "frozen_before_scientific_ranking", "tolerance": 1e-8, "cases": cases}), encoding="utf-8")
    runs = []
    for i in range(9):
        run = tmp_path / f"run{i}"
        run.mkdir()
        config_protocol = json.loads((regdir / f"c{i}.json").read_text())
        # Use actual workspace-relative paths for the manifest check by temporarily setting ROOT.
        report.ROOT = tmp_path
        manifest_sources = [{"path": p.relative_to(tmp_path).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in [regfile, *sorted(regdir.glob("c*.json"))]]
        (run / "manifest.json").write_text(json.dumps({"sources": manifest_sources,
            "config": {"protocol": config_protocol}}), encoding="utf-8")
        result = {"case_id": f"c{i}", "law_id": "law", "cadence": .25, "rank_root": "reference",
                  "policies": [policy("p", "p", 0)], "winners": {"1": ["p"]},
                  "rate_winners": ["p"], "max_residual": 0, "status": "complete"}
        (run / "result.json").write_text(json.dumps(result), encoding="utf-8")
        (run / "status.json").write_text(json.dumps({"status": "complete"}), encoding="utf-8")
        runs.append(run)
    summary = report.summarize(runs, regfile, tmp_path / "out")
    assert summary["case_count"] == 9
    assert summary["cases"]["c0"]["horizon_scores"]["1"]["best_bits"] == 0
    assert (tmp_path / "out" / "SUMMARY.json").exists()
