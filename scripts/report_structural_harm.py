"""Summarize frozen structural-harm result.json files; never runs or rescales physics."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from itertools import pairwise
from pathlib import Path
from typing import Any

TOL = 1e-8
HORIZONS = (1, 4, 16, 64, 256)
MODES = ("fast", "slow", "hardware_loss")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _num(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _cid(policy: dict) -> str:
    return str(policy.get("canonical_id") or policy.get("id"))


def _bits(policy: dict, horizon: int, root: str = "present") -> float | None:
    value = policy.get("bits", {}).get(str(horizon), {}).get(root)
    return _num(value)


def _response_surface(policy: dict) -> dict[tuple[int, int], tuple[float, ...]]:
    controller = policy.get("controller", {})
    if not isinstance(controller, dict):
        return {}
    threshold = int(controller.get("threshold", 1))
    surplus_name = str(controller.get("surplus", "service"))
    response_names = {
        "idle": (0.0, 0.0), "service": (1.0, 0.0), "mix25": (0.75, 0.25),
        "mix50": (0.5, 0.5), "mix75": (0.25, 0.75), "export": (0.0, 1.0),
    }
    surplus = response_names.get(surplus_name)
    if surplus is None:
        return {}
    worn_service = bool(controller.get("service_if_worn", False))
    out = {}
    for active in range(4):
        for worn in range(4 - active):
            if active == 0:
                response = response_names["idle"]
            elif active < threshold or (worn_service and worn > 0):
                response = response_names["service"]
            else:
                response = surplus
            out[(active, worn)] = response
    return out


def _service_order(lhs: dict, rhs: dict) -> str:
    """Compare service component on common a>0, a+w<=3 local observations."""
    a, b = _response_surface(lhs), _response_surface(rhs)
    keys = {k for k in a.keys() & b.keys() if k[0] > 0 and sum(k) <= 3}
    if not keys:
        return "unresolved"
    diffs = [a[k][0] - b[k][0] for k in keys]
    if all(d >= -TOL for d in diffs) and any(d > TOL for d in diffs):
        return "higher"
    if all(d <= TOL for d in diffs) and any(d < -TOL for d in diffs):
        return "lower"
    if all(abs(d) <= TOL for d in diffs):
        return "same"
    return "incomparable"


def _score_case(result: dict) -> dict:
    policies = result.get("policies", [])
    canonical: dict[str, dict] = {}
    for policy in policies:
        canonical.setdefault(_cid(policy), policy)
    horizon_scores = {}
    for horizon in HORIZONS:
        values = [(cid, _bits(policy, horizon)) for cid, policy in canonical.items()]
        values = [(cid, value) for cid, value in values if value is not None]
        if not values:
            continue
        best = max(value for _, value in values)
        horizon_scores[str(horizon)] = {
            "winner_ids": sorted(cid for cid, value in values if abs(value - best) <= TOL),
            "best_bits_present": best,
            "best_bits_post_fault": max(
                (_bits(p, horizon, "post_fault") for p in canonical.values()
                 if _bits(p, horizon, "post_fault") is not None), default=None),
            "scored_policy_count": len(values),
        }
    return {
        "case_id": result.get("case_id"), "mode": result.get("mode"),
        "hazard": result.get("hazard"), "cadence": result.get("cadence"),
        "protocol_hash": result.get("protocol_hash"), "input_hash": result.get("input_hash"),
        "status": result.get("status"), "states": result.get("states"),
        "unique_models": result.get("unique_models"), "policy_count": len(policies),
        "canonical_policy_count": len(canonical), "horizon_scores": horizon_scores,
        "rate_winners": result.get("rate_winners", []),
        "policies": [{key: row[key] for key in ("id", "canonical_id", "alias_of", "controller",
                         "hash", "nonrandom", "bits", "rates", "readouts") if key in row}
                     for row in policies],
    }


def _validate_batch(results: list[dict], protocol_path: Path) -> dict:
    protocol_bytes = protocol_path.read_bytes()
    protocol_hash = hashlib.sha256(protocol_bytes).hexdigest()
    protocol = json.loads(protocol_bytes.decode("utf-8"))
    if protocol.get("status") != "frozen_before_scientific_ranking":
        raise ValueError("protocol must be frozen_before_scientific_ranking")
    declared = {str(case["id"]): case for case in protocol.get("cases", [])}
    found = {str(result["case_id"]): result for result in results}
    if set(found) != set(declared):
        raise ValueError(f"result cases differ from frozen protocol; missing={sorted(set(declared)-set(found))}, unexpected={sorted(set(found)-set(declared))}")
    for case_id, result in found.items():
        case = declared[case_id]
        if case.get("status") != "frozen_before_scientific_ranking":
            raise ValueError(f"{case_id}: case is not frozen before ranking")
        if result.get("protocol_hash") != protocol_hash:
            raise ValueError(f"{case_id}: protocol_hash does not match frozen protocol bytes")
        for key in ("mode", "hazard", "cadence"):
            if key not in result or key not in case:
                raise ValueError(f"{case_id}: missing registered/result {key}")
            if key == "mode":
                matches = result[key] == case[key]
            else:
                matches = _num(result[key]) is not None and abs(float(result[key]) - float(case[key])) <= TOL
            if not matches:
                raise ValueError(f"{case_id}: {key} differs from frozen case")
        if result.get("status") != "complete":
            raise ValueError(f"{case_id}: result is not complete")
        candidates = {str(p["id"]): p for p in case.get("candidates", [])}
        policies = result.get("policies", [])
        ids = [str(p.get("id")) for p in policies]
        if len(ids) != len(set(ids)) or set(ids) != set(candidates):
            raise ValueError(f"{case_id}: result policy IDs differ from frozen candidates")
        by_id = {str(p["id"]): p for p in policies}
        for pid, candidate in candidates.items():
            row = by_id[pid]
            if row.get("controller") != candidate:
                raise ValueError(f"{case_id}/{pid}: controller differs from frozen candidate")
            canonical = str(row.get("canonical_id") or pid)
            if canonical not in candidates:
                raise ValueError(f"{case_id}/{pid}: unknown canonical policy")
            alias = row.get("alias_of")
            if alias is not None and canonical != str(alias):
                raise ValueError(f"{case_id}/{pid}: alias target disagrees with canonical_id")
            if alias is None and canonical != pid:
                raise ValueError(f"{case_id}/{pid}: non-alias row has a different canonical_id")
            if alias is not None:
                target = by_id.get(str(alias))
                if target is None or row.get("hash") != target.get("hash"):
                    raise ValueError(f"{case_id}/{pid}: alias does not share its target model")
        tol = float(case.get("rank_tolerance", TOL))
        canonical_rows = {}
        for row in policies:
            canonical_rows.setdefault(str(row.get("canonical_id") or row["id"]), row)
        expected_winners = {}
        for horizon in case.get("horizons", HORIZONS):
            values = [(pid, _bits(row, int(horizon))) for pid, row in canonical_rows.items()]
            values = [(pid, value) for pid, value in values if value is not None]
            if not values:
                raise ValueError(f"{case_id}: no present-root score at horizon {horizon}")
            best = max(value for _, value in values)
            expected_winners[str(horizon)] = sorted(pid for pid, value in values if best-value <= tol)
        if result.get("winners") != expected_winners:
            raise ValueError(f"{case_id}: recorded winner ties differ from policy scores")
        rates = [(pid, _num(row.get("rates", {}).get("present")))
                 for pid, row in canonical_rows.items()]
        rates = [(pid, value) for pid, value in rates if value is not None]
        if rates:
            best_rate = max(value for _, value in rates)
            expected_rates = sorted(pid for pid, value in rates if best_rate-value <= tol)
            if result.get("rate_winners") != expected_rates:
                raise ValueError(f"{case_id}: recorded rate-winner ties differ from policy rates")
        if result.get("states") != 3840:
            raise ValueError(f"{case_id}: state count differs from frozen 3+1 design")
        unique_hashes = {str(row.get("hash")) for row in policies}
        if result.get("unique_models") != len(unique_hashes):
            raise ValueError(f"{case_id}: unique_models differs from retained policy hashes")
        hash_owners: dict[str, set[str]] = {}
        for row in policies:
            hash_owners.setdefault(str(row.get("hash")), set()).add(str(row.get("canonical_id") or row["id"]))
        if any(len(owners) != 1 for owners in hash_owners.values()):
            raise ValueError(f"{case_id}: physical model hashes disagree with canonical aliases")
    return protocol


def _find_case(cases: list[dict], mode: str, hazard: float, cadence: float) -> dict | None:
    return next((c for c in cases if c["mode"] == mode
                 and abs(float(c["hazard"]) - hazard) <= TOL
                 and abs(float(c["cadence"]) - cadence) <= TOL), None)


def _winner_rows(case: dict | None, horizon: int) -> list[dict]:
    if not case:
        return []
    ids = case.get("horizon_scores", {}).get(str(horizon), {}).get("winner_ids", [])
    rows = { _cid(p): p for p in case.get("policies", []) }
    return [rows[x] for x in ids if x in rows]


def _winner_service_audit(cases: list[dict], protocol: dict | None) -> dict:
    toler = _num((protocol or {}).get("tolerance")) or TOL
    audits: dict[str, Any] = {"horizon_progression": [], "mode_consequence": [],
                              "hazard_response": [], "stationary_exposure": [],
                              "cadence_replay": []}
    hazards = sorted({float(c["hazard"]) for c in cases})
    cadences = sorted({float(c["cadence"]) for c in cases})
    # Primary cadence progression: all tied winner pairs are compared on feasible surfaces.
    primary = min(cadences, key=lambda x: abs(x - 0.25)) if cadences else 0.25
    for mode in MODES:
        for hazard in hazards:
            case = _find_case(cases, mode, hazard, primary)
            for h1, h2 in pairwise(HORIZONS):
                low, high = _winner_rows(case, h1), _winner_rows(case, h2)
                orders = [_service_order(a, b) for a in high for b in low]
                if orders:
                    finding = ("decrease" if "lower" in orders else
                               "strict" if all(x in ("higher", "same") for x in orders)
                               and "higher" in orders else
                               "plateau" if all(x == "same" for x in orders) else
                               "incomparable")
                else:
                    finding = "unavailable"
                audits["horizon_progression"].append({"mode": mode, "hazard": hazard,
                    "from_horizon": h1, "to_horizon": h2, "pairwise_orders": orders,
                    "finding": finding})
    # Consequence contrasts hold hazard/cadence fixed; hazard contrasts hold mode/cadence fixed.
    for hazard in hazards:
        for h in HORIZONS:
            fast = _find_case(cases, "fast", hazard, primary)
            loss = _find_case(cases, "hardware_loss", hazard, primary)
            orders = [_service_order(a, b) for a in _winner_rows(loss, h) for b in _winner_rows(fast, h)]
            audits["mode_consequence"].append({"hazard": hazard, "cadence": primary,
                "horizon": h, "fast_vs_hardware_loss_orders": orders,
                "response_differs": any(x != "same" for x in orders) if orders else None})
    for mode in MODES:
        cadence = primary
        if len(hazards) >= 2:
            lowhaz, highhaz = hazards[0], hazards[-1]
            for h in HORIZONS:
                low = _find_case(cases, mode, lowhaz, cadence)
                high = _find_case(cases, mode, highhaz, cadence)
                orders = [_service_order(a, b) for a in _winner_rows(high, h) for b in _winner_rows(low, h)]
                audits["hazard_response"].append({"mode": mode, "cadence": cadence,
                    "low_hazard": lowhaz, "high_hazard": highhaz, "horizon": h,
                    "pairwise_orders": orders,
                    "stronger_service_somewhere": "higher" in orders})
                low_rows, high_rows = _winner_rows(low, h), _winner_rows(high, h)
                lo = [_num(p.get("readouts", {}).get("stationary_exposure")) for p in low_rows]
                hi = [_num(p.get("readouts", {}).get("stationary_exposure")) for p in high_rows]
                lo, hi = [x for x in lo if x is not None], [x for x in hi if x is not None]
                diffs = [b-a for a in lo for b in hi]
                audits["stationary_exposure"].append({"mode": mode, "cadence": cadence,
                    "low_hazard": lowhaz, "high_hazard": highhaz, "horizon": h,
                    "high_minus_low_ranges": [min(diffs), max(diffs)] if diffs else None,
                    "increase_alert": bool(diffs and max(diffs) > toler)})
    # Cadence replay is assessed only where the frozen registration includes cadence audits.
    for mode in MODES:
        for hazard in hazards:
            base = _find_case(cases, mode, hazard, primary)
            group_cadences = sorted(float(c["cadence"]) for c in cases
                                    if c["mode"] == mode and abs(float(c["hazard"]) - hazard) <= TOL)
            audit_registered = len(group_cadences) >= 3
            for h in HORIZONS:
                for winner in _winner_rows(base, h):
                    cid = _cid(winner)
                    score_rows = []
                    for cadence in group_cadences:
                        case = _find_case(cases, mode, hazard, cadence)
                        policy = next((p for p in (case or {}).get("policies", []) if _cid(p) == cid), None)
                        score_rows.append({"cadence": cadence,
                            "bits_present": _bits(policy, h) if policy else None})
                    vals = [x["bits_present"] for x in score_rows if x["bits_present"] is not None]
                    base_rows = (base or {}).get("policies", [])
                    controls = {}
                    for label in ("idle", "service", "export"):
                        matches = [p for p in base_rows
                                   if p.get("controller", {}).get("threshold") == 1
                                   and p.get("controller", {}).get("surplus") == label]
                        controls[label] = _cid(matches[0]) if matches else None
                    deterministic = [p for p in base_rows if p.get("nonrandom") is True]
                    best_nonrandom = max(deterministic,
                        key=lambda p: _bits(p, h) if _bits(p, h) is not None else -math.inf,
                        default=None)
                    comparator_ids = {label: [value] if value else [] for label, value in controls.items()}
                    best_value = _bits(best_nonrandom, h) if best_nonrandom else None
                    best_ties = [_cid(p) for p in deterministic
                                 if best_value is not None and _bits(p, h) is not None
                                 and best_value - _bits(p, h) <= toler]
                    comparator_ids["best_nonrandom"] = sorted(set(best_ties))
                    sign_comparisons = {}
                    for label, control_ids in comparator_ids.items():
                        for comparator_id in control_ids:
                            signs = []
                            for item in score_rows:
                                case = _find_case(cases, mode, hazard, item["cadence"])
                                by_id = {_cid(p): p for p in (case or {}).get("policies", [])}
                                comp_bits = _bits(by_id[comparator_id], h) if comparator_id in by_id else None
                                difference = (item["bits_present"] - comp_bits
                                              if item["bits_present"] is not None and comp_bits is not None else None)
                                signs.append({"cadence": item["cadence"], "difference_bits": difference,
                                    "sign": "unavailable" if difference is None else
                                    "positive" if difference > toler else
                                    "negative" if difference < -toler else "tie"})
                            key = f"{label}:{comparator_id}" if label == "best_nonrandom" else label
                            sign_comparisons[key] = signs
                    audits["cadence_replay"].append({"mode": mode, "hazard": hazard,
                        "horizon": h, "policy_id": cid, "scores": score_rows,
                        "audit_scope": "registered" if audit_registered else "not_registered",
                        "fixed_comparator_signs": sign_comparisons,
                        "winner_identity_stable": (all(any(_cid(p) == cid for p in _winner_rows(
                            _find_case(cases, mode, hazard, x["cadence"]), h)) for x in score_rows)
                            if audit_registered else None),
                        "score_range": [min(vals), max(vals)] if vals else None})
    return audits


def _registered_claims(audits: dict) -> dict:
    h1 = audits["horizon_progression"]
    c1 = [r for r in audits["mode_consequence"] if abs(r["hazard"] - .02) <= TOL]
    r1 = [r for r in audits["hazard_response"] if abs(r["low_hazard"] - .02) <= TOL
          and abs(r["high_hazard"] - .04) <= TOL]
    e1 = [r for r in audits["stationary_exposure"] if abs(r["low_hazard"] - .02) <= TOL]
    s1 = []
    for replay in audits["cadence_replay"]:
        if replay["audit_scope"] != "registered":
            continue
        for comparator, rows in replay["fixed_comparator_signs"].items():
            signs = {row["sign"] for row in rows}
            if "positive" in signs and "negative" in signs:
                s1.append({"mode": replay["mode"], "horizon": replay["horizon"],
                           "policy_id": replay["policy_id"], "comparator": comparator})
    return {
        "H1_horizon_service_non_decrease": {
            "status": "supported" if h1 and all(r["finding"] in ("strict", "plateau") for r in h1) else "not_supported",
            "strict_count": sum(r["finding"] == "strict" for r in h1),
            "plateau_count": sum(r["finding"] == "plateau" for r in h1),
            "decrease_count": sum(r["finding"] == "decrease" for r in h1),
            "incomparable_count": sum(r["finding"] == "incomparable" for r in h1)},
        "C1_fast_vs_hardware_loss_response_differs": {
            "status": "supported" if any(r["response_differs"] for r in c1) else "not_supported",
            "horizons": [r["horizon"] for r in c1 if r["response_differs"]]},
        "R1_higher_hazard_stronger_service": {
            "status": "supported" if any(r["stronger_service_somewhere"] for r in r1) else "not_supported",
            "mode_horizons": [{"mode": r["mode"], "horizon": r["horizon"]} for r in r1 if r["stronger_service_somewhere"]]},
        "E1_stationary_exposure_increase": {
            "status": "alert" if any(r["increase_alert"] for r in e1) else "not_observed",
            "mode_horizons": [{"mode": r["mode"], "horizon": r["horizon"],
                               "high_minus_low_ranges": r["high_minus_low_ranges"]} for r in e1 if r["increase_alert"]]},
        "S1_positive_to_negative_fixed_winner_lead": {
            "status": "observed" if s1 else "not_observed", "comparisons": s1},
    }


def summarize(result_paths: list[Path], output: Path, protocol_path: Path) -> dict:
    results = [_read(path) for path in result_paths]
    if any(result.get("status") != "complete" for result in results):
        raise ValueError("every input result.json must have status='complete'")
    for result in results:
        for key in ("case_id", "mode", "hazard", "cadence", "protocol_hash", "input_hash", "policies"):
            if key not in result:
                raise ValueError(f"{result.get('case_id', 'result')}: missing {key}")
    identities = [(r["mode"], float(r["hazard"]), float(r["cadence"])) for r in results]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate mode/hazard/cadence result")
    protocol = _validate_batch(results, protocol_path)
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    cases = [_score_case(result) for result in results]
    cases.sort(key=lambda c: (MODES.index(c["mode"]) if c["mode"] in MODES else 99,
                              float(c["hazard"]), float(c["cadence"])))
    summary = {"schema": "omega-structural-harm-report/1", "protocol": protocol,
        "protocol_hash": protocol_hash, "case_count": len(cases), "cases": cases,
        "audits": _winner_service_audit(cases, protocol),
        "interpretation": {
            "primary": "winner ranking uses complete-history bits at present root, separately at each horizon",
            "post_fault": "post-fault root scores are reported alongside the primary and are not substituted for it",
            "physical_readouts": "stock, exposure, function, hardware, damage, recovery and costs are descriptive readouts, not optimizer rewards",
            "hardware_loss": "broken hardware disables local powered repair; basal substitutes remain, so closure is read from transitions/readouts",
            "contrasts": "mode contrasts hold hazard and cadence fixed; hazard contrasts hold mode and cadence fixed",
            "ties": f"canonical policy ties use absolute tolerance {TOL:g}; service is compared as a partial order on common feasible local observations with active>0 and active+worn<=3",
        }}
    summary["registered_claims"] = _registered_claims(summary["audits"])
    output.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(summary, separators=(",", ":"), allow_nan=False) + "\n"
    if len(payload.encode("utf-8")) > 5 * 1024 * 1024:
        raise ValueError("SUMMARY.json exceeds 5 MiB")
    (output / "SUMMARY.json").write_text(payload, encoding="utf-8")
    lines = ["# Structural harm results", "",
        "The primary ranking is complete-history entropy from the matched present root, separately at each horizon. Post-fault entropy and physical readouts are reported separately. Hardware loss removes local powered repair while basal recovery routes remain; it does not itself establish functional closure.",
        "", "## Cases", "", "| Mode | Hazard | Cadence | Policies | Canonical | Winner IDs by horizon |", "|---|---:|---:|---:|---:|---|"]
    for case in cases:
        winners = "; ".join(f"T{h}: {', '.join(s['winner_ids'])}" for h, s in case["horizon_scores"].items())
        lines.append(f"| {case['mode']} | {case['hazard']} | {case['cadence']} | {case['policy_count']} | {case['canonical_policy_count']} | {winners} |")
    lines += ["", "## Winner service partial order", "", "The comparison uses common feasible local observations with active apparatus present. `strict` means every tied winner pair is nondecreasing and at least one is strictly more service-biased; `plateau` means all compared surfaces match; mixed or unresolved comparisons are labeled incomparable.",
        "", "| Mode | Hazard | Horizon step | Finding | Pairwise orders |", "|---|---:|---:|---|---|"]
    for row in summary["audits"]["horizon_progression"]:
        lines.append(f"| {row['mode']} | {row['hazard']} | {row['from_horizon']}→{row['to_horizon']} | {row['finding']} | {', '.join(row['pairwise_orders'])} |")
    lines += ["", "## Consequence and hazard contrasts", "", "Mode comparisons hold hazard and cadence fixed. Hazard comparisons hold mode and cadence fixed. Exposure is an alert readout, not a reward or ethical verdict.",
        "", "| Contrast | Horizon | Result |", "|---|---:|---|"]
    for row in summary["audits"]["mode_consequence"]:
        lines.append(f"| fast vs hardware_loss at h={row['hazard']} | {row['horizon']} | {row['response_differs']} ({', '.join(row['fast_vs_hardware_loss_orders'])}) |")
    for row in summary["audits"]["hazard_response"]:
        lines.append(f"| {row['mode']} hazard {row['low_hazard']}→{row['high_hazard']} at dt={row['cadence']} | {row['horizon']} | stronger service somewhere: {row['stronger_service_somewhere']} ({', '.join(row['pairwise_orders'])}) |")
    lines += ["", "## Frozen claims and adverse outcomes", "", "| Claim | Status |", "|---|---|"]
    for claim, outcome in summary["registered_claims"].items():
        lines.append(f"| {claim} | {outcome['status']} |")
    lines += ["", "Full policy rows, including stock and recovery readouts, remain in `SUMMARY.json`. The report helper summarizes supplied frozen result files; it does not run simulations or alter scores.", ""]
    (output / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+", type=Path, help="frozen result.json files")
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.results, args.output, args.protocol)


if __name__ == "__main__":
    main()
