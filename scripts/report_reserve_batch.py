"""Compact and score retained reserve-batch results; does not run simulations."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-8
EXPECTED_CASES = 9


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _cases(reg: dict) -> list[dict]:
    cases = reg.get("cases", [])
    if isinstance(cases, dict):
        return [dict(v, case_id=k) if isinstance(v, dict) else {"case_id": k} for k, v in cases.items()]
    return cases


def _case_id(case: dict) -> str:
    return str(case.get("id", case.get("case_id", case.get("case", ""))))


def _canonical(p: dict) -> str:
    return str(p.get("canonical_id") or p.get("id"))


def _number(x: Any) -> float | None:
    try:
        n = float(x)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def _hkey(h: Any) -> str:
    return str(h)


def _bits(p: dict, h: Any) -> float | None:
    horizons = p.get("bits", {}).get(_hkey(h), p.get("bits", {}).get(str(float(h)), {}))
    if not isinstance(horizons, dict):
        return None
    root = p.get("rank_root")
    return _number(horizons.get(root)) if root is not None else None


def _rate(p: dict) -> float | None:
    root = p.get("rank_root")
    entry = p.get("limiting", {}).get(root, {})
    return _number(entry.get("rate")) if isinstance(entry, dict) else None


def _policy_rows(result: dict) -> list[dict]:
    return list(result.get("policies", []))


def _validate_registration(reg_path: Path, reg: dict) -> None:
    cases = _cases(reg)
    if len(cases) != EXPECTED_CASES:
        raise ValueError(f"registration must contain {EXPECTED_CASES} cases; found {len(cases)}")
    if reg.get("status") != "frozen_before_scientific_ranking":
        raise ValueError("registration status must be frozen_before_scientific_ranking")
    if not _number(reg.get("tolerance")):
        raise ValueError("registration must declare numeric tolerance")
    for c in cases:
        f, expected = c.get("file"), c.get("sha256")
        if not f or not expected or not c.get("law_id") or "cadence" not in c:
            raise ValueError(f"case registration incomplete: {_case_id(c)}")
        payload = (reg_path.parent / f).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"registered protocol hash mismatch: {f}")


def _manifest_check(run: Path, reg_path: Path, case: dict, all_cases: list[dict]) -> None:
    mp = run / "manifest.json"
    if not mp.exists():
        raise ValueError(f"missing frozen run manifest: {run}")
    manifest = _read(mp)
    sources = manifest.get("sources", [])
    def check_source(path: Path) -> None:
        rel = path.resolve().relative_to(ROOT.resolve()).as_posix()
        item = next((s for s in sources if s.get("path") == rel), None)
        if item is None or item.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"missing or changed frozen source {rel} in {run}")
    check_source(reg_path)
    for registered_case in all_cases:
        check_source((reg_path.parent / registered_case["file"]).resolve())
    protocol = (reg_path.parent / case["file"]).resolve()
    registered = json.loads(protocol.read_text(encoding="utf-8"))
    if manifest.get("config", {}).get("protocol") != registered:
        raise ValueError(f"run protocol differs from registered case in {run}")


def _winner_ids(result: dict, horizon: Any) -> list[str]:
    winners = result.get("winners", {})
    if isinstance(winners, dict):
        raw = winners.get(_hkey(horizon), winners.get(str(float(horizon)), []))
    else:
        raw = []
    return [str(x) for x in raw]


def _score_case(result: dict) -> dict:
    rows = _policy_rows(result)
    bycanon: dict[str, dict] = {}
    for p in rows:
        bycanon.setdefault(_canonical(p), p)
    horizons = list(result.get("winners", {}).keys()) or ["1", "4", "16", "64", "256"]
    hor = {}
    for h in horizons:
        scored = [(c, _bits(p, h)) for c, p in bycanon.items()]
        scored = [(c, v) for c, v in scored if v is not None]
        if scored:
            best = max(v for _, v in scored)
            hor[str(h)] = {"winner_ids": sorted(c for c, v in scored if abs(v-best) <= TOL),
                           "best_bits": best, "rows_scored": len(scored)}
    rate_ids = result.get("rate_winners", [])
    rate_rows = [bycanon[x] for x in rate_ids if x in bycanon]
    regrets = {}
    for h in horizons:
        best_all = hor.get(str(h), {}).get("best_bits")
        values = [(p.get("canonical_id", p.get("id")), _bits(p, h)) for p in rate_rows]
        values = [(cid, v) for cid, v in values if v is not None]
        if values and best_all is not None:
            regrets[str(h)] = {"best_horizon_bits": best_all,
                "rate_winner_bits": {cid: v for cid, v in values},
                "regret_by_rate_winner": {cid: best_all-v for cid, v in values},
                "regret_min": min(best_all-v for _, v in values),
                "regret_max": max(best_all-v for _, v in values)}
    return {"case_id": result.get("case_id"), "law_id": result.get("law_id"),
            "cadence": result.get("cadence"), "rank_root": result.get("rank_root"),
            "policy_count": len(rows), "canonical_policy_count": len(bycanon),
            "policies": rows, "horizon_scores": hor, "rate_winner_regret": regrets,
            "max_residual": result.get("max_residual"),
            "nonconstant_reachable": result.get("nonconstant_reachable"),
            "protocol_sha256": result.get("protocol_sha256"),
            "source_manifest": result.get("source_manifest"),
            "residuals": result.get("residuals"),
            "readouts": result.get("readouts"),
            "winners": result.get("winners"), "rate_winners": rate_ids}


def _strict_gain(result: dict, tolerance: float = TOL) -> dict:
    rows = {}
    for p in _policy_rows(result):
        rows.setdefault(_canonical(p), p)
    constant_ids = set()
    nonconstant_ids = set()
    for cid, p in rows.items():
        if p.get("nonconstant_reachable") is True:
            nonconstant_ids.add(cid)
        else:
            constant_ids.add(cid)
    out = {}
    horizons = set.union(*(set(p.get("bits", {})) for p in rows.values())) if rows else set()
    for h in sorted(horizons, key=lambda x: float(x)):
        constants = [_bits(rows[c], h) for c in constant_ids]
        constants = [x for x in constants if x is not None]
        best_const = max(constants) if constants else None
        gains = [_bits(rows[c], h) for c in nonconstant_ids]
        gains = [x-best_const for x in gains if x is not None and best_const is not None]
        out[h] = {"best_constant_bits": best_const,
                  "best_nonconstant_gain_bits": max(gains) if gains else None,
                  "strict_gain": bool(gains and max(gains) > tolerance)}
    return out


def _response_signature(p: dict) -> tuple:
    surface = p.get("audit_surface", [])
    return tuple(sorted((int(x.get("active", -1)), int(x.get("worn", -1)),
                          tuple(x.get("response", []))) for x in surface
                         if x.get("reachable", True) is not False and int(x.get("active", 0)) > 0
                         and int(x.get("active", 0))+int(x.get("worn", 0)) <= 3))


def _surface_order(a: dict, b: dict) -> str:
    # service is response[0]; compare only the declared reachable support a+w<=3, a>0.
    am = {(int(x[0]), int(x[1])): x[2] for x in _response_signature(a)}
    bm = {(int(x[0]), int(x[1])): x[2] for x in _response_signature(b)}
    keys = {(x,y) for x,y in am.keys() & bm.keys() if x > 0 and x+y <= 3}
    if not keys: return "unresolved"
    ds = [float(am[k][0])-float(bm[k][0]) for k in keys if am[k] and bm[k]]
    if len(ds) != len(keys): return "unresolved"
    if all(d >= -TOL for d in ds) and any(d > TOL for d in ds): return "higher"
    if all(d <= TOL for d in ds) and any(d < -TOL for d in ds): return "lower"
    if all(abs(d) <= TOL for d in ds): return "same"
    return "mixed"


def _batch_audits(raw_cases: dict[str, dict], tolerance: float = TOL) -> dict:
    """Score the prespecified fixed-policy cadence and matched-risk response audits."""
    output: dict[str, Any] = {"fixed_primary_policy_signs": [], "matched_risk_winner_surfaces": [],
                              "hazard_winner_surfaces": [], "horizon_winner_surfaces": [],
                              "sentinel_winner_surfaces": [], "strict_nonconstant_gains": {},
                              "exposure_diagnostic": {"winner_pairs": [], "fixed_policy_replay": []}}
    # By construction the family has five primary cases and two extra cadence audits
    # for no_shock and correlated_002. Use law/cadence metadata, not fragile filenames.
    groups: dict[tuple[str, float], dict] = {}
    for cid, result in raw_cases.items():
        law = result.get("law_id")
        cadence = _number(result.get("cadence"))
        if law is not None and cadence is not None:
            groups[(str(law), cadence)] = result
        if cadence == .25 and law in ("independent_002", "correlated_002", "independent_004"):
            output["strict_nonconstant_gains"][cid] = _strict_gain(result, tolerance)

    # Fixed primary winners, idle/service/export, and best nonrandom are held constant
    # across cadence. Comparator IDs may be explicitly registered in the result.
    for law in ("no_shock", "correlated_002"):
        primary = groups.get((law, .25))
        if not primary:
            continue
        controls = primary.get("fixed_comparators", {})
        for label in ("idle", "service", "export"):
            ids = controls.get(label, [])
            controls[label] = ids if isinstance(ids, list) else ([ids] if ids else [])
        common_horizons = set(primary.get("winners", {}))
        for horizon in sorted(common_horizons, key=float):
            winners = _winner_ids(primary, horizon)
            for winner_id in winners:
                dynamic = controls.get("best_nonrandom", {})
                dynamic_id = dynamic.get(str(horizon), dynamic.get(str(float(horizon)))) if isinstance(dynamic, dict) else dynamic
                comparisons = {label: controls.get(label, []) for label in ("idle", "service", "export")}
                comparisons["best_nonrandom"] = dynamic_id if isinstance(dynamic_id, list) else ([dynamic_id] if dynamic_id else [])
                for label, comparator_ids in comparisons.items():
                    for comparator_id in comparator_ids:
                        signs = []
                        for cadence in (.125, .25, .5):
                            other = groups.get((law, cadence))
                            omap = {_canonical(p): p for p in _policy_rows(other or {})}
                            lhs = _bits(omap[winner_id], horizon) if winner_id in omap else None
                            rhs = _bits(omap[comparator_id], horizon) if comparator_id in omap else None
                            d = None if lhs is None or rhs is None else lhs-rhs
                            sign = "unavailable" if d is None else "positive" if d > tolerance else "negative" if d < -tolerance else "tie"
                            signs.append({"cadence": cadence, "winner_bits": lhs, "comparator_bits": rhs,
                                          "difference_bits": d, "sign": sign})
                        labels = [x["sign"] for x in signs]
                        reversal = "positive" in labels and "negative" in labels
                        output["fixed_primary_policy_signs"].append({"law_id": law, "winner_id": winner_id,
                            "comparator_id": comparator_id, "comparator": label, "horizon": horizon,
                            "cadence_signs": signs, "positive_negative_reversal": reversal,
                            "finding": "self_comparison" if winner_id == comparator_id else
                                       "temporal_resolution_sensitivity" if reversal else
                                       "loss_of_strict_robustness" if "tie" in labels else "no_certified_reversal"})

    def winner_signatures(law: str, cadence: float, horizon: str) -> list[tuple[str, dict]]:
        r = groups.get((law, cadence))
        if not r: return []
        rows = {_canonical(p): p for p in _policy_rows(r)}
        return [(cid, rows[cid]) for cid in _winner_ids(r, horizon) if cid in rows]

    for cadence in (.25,):
        for horizon in ("1", "4", "16", "64", "256"):
            indep = winner_signatures("independent_002", cadence, horizon)
            corr = winner_signatures("correlated_002", cadence, horizon)
            if indep and corr:
                vals = [_surface_order(c, i) for _, c in corr for _, i in indep]
                output["matched_risk_winner_surfaces"].append({"horizon": horizon,
                    "independent_winners": [x for x, _ in indep], "correlated_winners": [x for x, _ in corr],
                    "service_order": vals, "status": "higher" if all(x == "higher" for x in vals) else
                    "lower" if all(x == "lower" for x in vals) else "same" if all(x == "same" for x in vals) else "mixed/inconclusive"})
            low = winner_signatures("independent_002", cadence, horizon)
            high = winner_signatures("independent_004", cadence, horizon)
            if low and high:
                vals = [_surface_order(h, l) for _, h in high for _, l in low]
                output["hazard_winner_surfaces"].append({"horizon": horizon,
                    "lower_hazard_winners": [x for x, _ in low], "higher_hazard_winners": [x for x, _ in high],
                    "service_order": vals, "status": "higher" if all(x == "higher" for x in vals) else
                    "lower" if all(x == "lower" for x in vals) else "same" if all(x == "same" for x in vals) else "mixed/inconclusive"})
        if cadence == .25:
            primary_laws = ("no_shock", "independent_002", "correlated_002", "independent_004", "absorbing")
            horizons = ("1", "4", "16", "64", "256")
            for law in primary_laws:
                for short_h, long_h in pairwise(horizons):
                    short = winner_signatures(law, cadence, short_h)
                    long = winner_signatures(law, cadence, long_h)
                    if short and long:
                        vals = [_surface_order(l, s) for _, l in long for _, s in short]
                        output["horizon_winner_surfaces"].append({"law_id": law,
                            "short_horizon": short_h, "long_horizon": long_h,
                            "short_winners": [x for x, _ in short], "long_winners": [x for x, _ in long],
                            "service_order": vals, "status": "higher" if all(x == "higher" for x in vals) else
                            "lower" if all(x == "lower" for x in vals) else "same" if all(x == "same" for x in vals) else "mixed/inconclusive"})
            for sentinel_horizon in ("1", "4", "16", "64", "256"):
                sentinel = winner_signatures("absorbing", cadence, sentinel_horizon)
                reversible = winner_signatures("no_shock", cadence, sentinel_horizon)
                if sentinel and reversible:
                    vals = [_surface_order(s, r) for _, s in sentinel for _, r in reversible]
                    sent_active = [_number(p.get("readouts", {}).get("active64")) for _, p in sentinel]
                    ref_active = [_number(p.get("readouts", {}).get("active64")) for _, p in reversible]
                    sent_active = [v for v in sent_active if v is not None]
                    ref_active = [v for v in ref_active if v is not None]
                    interval = None
                    verdict = "unavailable"
                    if sent_active and ref_active:
                        interval = {"min_difference": min(sent_active)-max(ref_active),
                                    "max_difference": max(sent_active)-min(ref_active)}
                        verdict = "pass" if interval["min_difference"] > tolerance else "fail" if interval["max_difference"] <= tolerance else "mixed/inconclusive"
                    output["sentinel_winner_surfaces"].append({"horizon": sentinel_horizon,
                        "sentinel_winners": [x for x, _ in sentinel], "no_shock_winners": [x for x, _ in reversible],
                        "service_order": vals, "active64_difference_interval": interval,
                        "active64_prediction": verdict,
                        "interpretation": "different declared laws; not an irreversibility-only contrast"})

    for low in raw_cases.values():
        if low.get("law_id") != "independent_002" or low.get("cadence") != .25: continue
        high = next((r for r in raw_cases.values() if r.get("law_id") == "independent_004" and r.get("cadence") == .25), None)
        if high is None: continue
        lowmap = {_canonical(p): p for p in _policy_rows(low)}
        highmap = {_canonical(p): p for p in _policy_rows(high)}
        for cid in sorted(lowmap.keys() & highmap.keys()):
            lv = _number(lowmap[cid].get("readouts", {}).get("exposure64"))
            hv = _number(highmap[cid].get("readouts", {}).get("exposure64"))
            ls = _number(lowmap[cid].get("readouts", {}).get("stationary_exposure"))
            hs = _number(highmap[cid].get("readouts", {}).get("stationary_exposure"))
            output["exposure_diagnostic"]["fixed_policy_replay"].append({"policy_id": cid,
                "low_case_id": low.get("case_id"), "high_case_id": high.get("case_id"),
                "stationary_exposure_low": ls, "stationary_exposure_high": hs,
                "stationary_difference_high_minus_low": None if ls is None or hs is None else hs-ls,
                "exposure64_low_secondary": lv, "exposure64_high_secondary": hv,
                "exposure64_difference_high_minus_low": None if lv is None or hv is None else hv-lv})
        for horizon in ("1", "4", "16", "64", "256"):
            lo_winners = winner_signatures("independent_002", .25, horizon)
            hi_winners = winner_signatures("independent_004", .25, horizon)
            vals, winner_pair_rows = [], []
            for hid, hp in hi_winners:
                for lid, lp in lo_winners:
                    hs = _number(hp.get("readouts", {}).get("stationary_exposure"))
                    ls = _number(lp.get("readouts", {}).get("stationary_exposure"))
                    he = _number(hp.get("readouts", {}).get("exposure64"))
                    le = _number(lp.get("readouts", {}).get("exposure64"))
                    if hs is not None and ls is not None:
                        vals.append(hs-ls)
                    winner_pair_rows.append({"higher_hazard_winner": hid, "higher_hazard_stationary_exposure": hs,
                        "lower_hazard_winner": lid, "lower_hazard_stationary_exposure": ls,
                        "stationary_difference_high_minus_low": None if hs is None or ls is None else hs-ls,
                        "exposure64_high_secondary": he, "exposure64_low_secondary": le,
                        "exposure64_difference_high_minus_low": None if he is None or le is None else he-le})
            if winner_pair_rows:
                output["exposure_diagnostic"]["winner_pairs"].append({"horizon": horizon,
                    "higher_hazard_winners": [x for x, _ in hi_winners],
                    "lower_hazard_winners": [x for x, _ in lo_winners], "pairs": winner_pair_rows,
                    "stationary_difference_high_minus_low_range": [min(vals), max(vals)] if vals else None,
                    "interpretation": "diagnostic only; evaluate alongside fixed-policy replay and access/cost readouts"})
    return output


def summarize(run_paths: list[Path], registration: Path, output: Path) -> dict:
    registration = registration.resolve()
    reg = _read(registration)
    _validate_registration(registration, reg)
    expected = {_case_id(c) for c in _cases(reg) if _case_id(c)}
    raw_cases = {}
    case_map = {_case_id(c): c for c in _cases(reg)}
    for run in run_paths:
        run = run.resolve()
        status_file = run / "status.json"
        if not status_file.exists() or _read(status_file).get("status") != "complete":
            raise ValueError(f"run status is not complete: {run}")
        raw = _read(run / "result.json")
        if raw.get("status") != "complete":
            raise ValueError(f"result status is not complete: {run}")
        cid = str(raw.get("case_id", ""))
        if not cid: raise ValueError(f"missing case_id in {run}")
        if cid in raw_cases: raise ValueError(f"duplicate case_id {cid}")
        if expected and cid not in expected: raise ValueError(f"unregistered case_id {cid}")
        entry = case_map.get(cid)
        if entry:
            _manifest_check(run, registration, entry, _cases(reg))
        if entry:
            for k in ("law_id", "cadence"):
                if k in entry and raw.get(k) != entry[k]: raise ValueError(f"{cid}: {k} differs from registration")
        raw_cases[cid] = raw
    if expected and set(raw_cases) != expected:
        raise ValueError(f"incomplete batch: missing {sorted(expected-set(raw_cases))}")
    if not expected and len(raw_cases) != EXPECTED_CASES:
        raise ValueError(f"expected {EXPECTED_CASES} complete case results, found {len(raw_cases)}")
    scored = {cid: _score_case(r) for cid, r in raw_cases.items()}
    for cid, r in raw_cases.items():
        if r.get("cadence") == .25 and r.get("law_id") in ("independent_002", "correlated_002", "independent_004"):
            scored[cid]["registered_threshold_strict_gain"] = _strict_gain(r)
    # Pair audit surface for the matched correlated vs independent laws and h=.02 cases.
    surface_pairs = []
    for cid, r in raw_cases.items():
        if r.get("law_id") not in ("independent_002", "correlated_002") or r.get("cadence") != .25: continue
        rows = {_canonical(p): p for p in _policy_rows(r)}
        for wid in _winner_ids(r, 64):
            if wid in rows:
                surface_pairs.append({"case_id": cid, "policy_id": wid,
                    "signature": _response_signature(rows[wid]), "readouts": rows[wid].get("readouts", {})})
    # Retain complete machine-readable rows, including zeros/failures, and no trajectory arrays.
    output.mkdir(parents=True, exist_ok=True)
    summary = {"schema": "reserve-batch-compact/1", "registration": reg, "cases": scored,
               "case_count": len(scored), "surface_audit_rows": surface_pairs,
               "batch_audits": _batch_audits(raw_cases, _number(reg.get("tolerance")) or TOL),
               "interpretation": {"exposure": "diagnostic only; increase is not an ethical verdict",
                 "active64": "sentinel comparison is not an irreversibility claim",
                 "cadence": "cadence changes are temporal-resolution findings, not full-grain robustness",
                 "rate_regret": "per-rate-winner shortfall from the best horizon-specific score"}}
    compact_json = json.dumps(summary, separators=(",", ":"), allow_nan=False)+"\n"
    if len(compact_json.encode("utf-8")) > 5*1024*1024:
        raise ValueError("compact summary exceeds the 5 MiB publication limit")
    (output / "SUMMARY.json").write_text(compact_json, encoding="utf-8")
    (output / "README.md").write_text("# Reserve batch report\n\nSee [RESULTS.md](RESULTS.md) for the compact case overview and [SUMMARY.json](SUMMARY.json) for every retained policy row and registered audit. This report summarizes existing run outputs; it does not launch or rescore simulations.\n", encoding="utf-8")
    lines = ["# Reserve batch results", "", "All registered compact policy rows are retained in `SUMMARY.json`, including aliases, zeros, and failed/nonconverged entries. Ranking deduplicates by canonical policy ID. Primary scores are horizon-specific bits; asymptotic rate is secondary.", "",
             "| Case | Law | Cadence | Policies | Canonical | Horizons with winners | Max residual |", "|---|---|---:|---:|---:|---:|---:|"]
    for cid, c in scored.items():
        lines.append(f"| {cid} | {c['law_id']} | {c['cadence']} | {c['policy_count']} | {c['canonical_policy_count']} | {len(c['horizon_scores'])} | {c['max_residual']} |")
    lines += ["", "## Horizon winners", "", "| Case | Horizon | Canonical winner IDs | Best bits |", "|---|---:|---|---:|"]
    for cid, c in scored.items():
        for horizon, score in sorted(c["horizon_scores"].items(), key=lambda item: float(item[0])):
            lines.append(f"| {cid} | {horizon} | {', '.join(score['winner_ids'])} | {score['best_bits']:.8g} |")
    gains = summary["batch_audits"]["strict_nonconstant_gains"]
    if gains:
        lines += ["", "## Registered nonconstant-response comparisons", "", "| Case | Horizon | Best constant bits | Best reachable nonconstant gain (bits) | Strict gain |", "|---|---:|---:|---:|---|"]
        for cid, horizon_rows in gains.items():
            for horizon, value in horizon_rows.items():
                lines.append(f"| {cid} | {horizon} | {value['best_constant_bits']} | {value['best_nonconstant_gain_bits']} | {value['strict_gain']} |")
    sentinel_rows = summary["batch_audits"]["sentinel_winner_surfaces"]
    lines += ["", "## Absorbing sentinel active64 prediction", "", "| Horizon | Winner active64 difference interval | Prediction |", "|---:|---:|---|"]
    for row in sentinel_rows:
        interval = row["active64_difference_interval"]
        shown = "unavailable" if interval is None else f"[{interval['min_difference']:.8g}, {interval['max_difference']:.8g}]"
        lines.append(f"| {row['horizon']} | {shown} | {row['active64_prediction']} |")
    lines += ["", "The sentinel comparison uses different declared physical laws and does not isolate irreversibility.", "",
              "## Exposure diagnostic", "", "| Horizon | Stationary exposure difference, h=.04 minus h=.02 |", "|---:|---:|"]
    for row in summary["batch_audits"]["exposure_diagnostic"]["winner_pairs"]:
        span = row["stationary_difference_high_minus_low_range"]
        shown = "unavailable" if span is None else f"[{span[0]:.8g}, {span[1]:.8g}]"
        lines.append(f"| {row['horizon']} | {shown} |")
    findings = summary["batch_audits"]["fixed_primary_policy_signs"]
    finding_counts = {key: sum(row["finding"] == key for row in findings)
                      for key in sorted({row["finding"] for row in findings})}
    lines += ["", "Exposure differences are diagnostic. Fixed-policy replay metrics and full policy rows are retained by case and canonical ID in `SUMMARY.json`.",
              "", "## Fixed-policy cadence audit", "", "Finding counts: " + ", ".join(f"{k}={v}" for k, v in finding_counts.items()) + ".",
              "Self-comparisons are labeled separately. Cadence changes address temporal resolution, not full grain robustness."]
    lines += ["", "Exposure is a diagnostic and does not by itself establish harm. Cadence audits address temporal resolution only; they do not establish full grain robustness.", ""]
    (output / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--registration", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    summarize(args.runs, args.registration, args.output)


if __name__ == "__main__":
    main()
