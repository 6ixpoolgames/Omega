"""Frozen smoke/science worker; numerical imports wait for Job Object GO."""
from __future__ import annotations

import sys
if __name__ == "__main__" and sys.stdin.readline().strip() != "GO":
    raise SystemExit("Parent must install hard caps before numerical imports")

import hashlib
import json
from pathlib import Path


CONFIG_REL = "docs/research_notes/lushness_testbed/maintained_resource/PROTOCOL.json"


def main(output: Path, mode: str) -> int:
    source_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source_root))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(output)
    protocol_path = source_root / CONFIG_REL
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if mode == "science" and protocol.get("status") != "frozen_before_scientific_ranking":
        raise RuntimeError("Scientific worker requires a frozen protocol")
    if mode == "smoke" and protocol.get("status") != "draft_engineering_gate":
        raise RuntimeError("Smoke snapshot must retain draft protocol status")

    # All numerical imports happen after the cap runner assigned the worker and
    # released this GO gate.
    import numpy as np
    from scipy.linalg import expm
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse import csr_matrix
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.maintained_resource import (
        EMPTY, LOCKED, USABLE, WASTE, STATES, build_world, energy, roots,
    )

    source_hashes = {row["path"]: row["sha256"] for row in manifest["sources"]}
    imports = {}
    for name, module in sorted(sys.modules.items()):
        if not name.startswith("omega_v2") or not getattr(module, "__file__", None):
            continue
        path = Path(module.__file__).resolve()
        try:
            rel = path.relative_to(source_root).as_posix()
        except ValueError as exc:
            raise RuntimeError(f"Omega import escaped frozen source: {name} -> {path}") from exc
        if rel not in source_hashes:
            raise RuntimeError(f"Imported source absent from frozen manifest: {rel}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source_hashes[rel]:
            raise RuntimeError(f"Imported source hash mismatch: {rel}")
        imports[name] = {"path": rel, "sha256": digest}

    capable = build_world(True)
    ablated = build_world(False)
    cap_model = compile_world(capable, max_states=32)
    abl_model = compile_world(ablated, max_states=32)
    qcap, qabl = cap_model["Q"].toarray(), abl_model["Q"].toarray()
    if mode == "smoke":
        if len(STATES) != protocol["states"]:
            raise AssertionError("State forecast differs from draft config")
        p = expm(qcap * 0.05)
        if np.min(p) < -1e-12 or np.max(abs(p.sum(axis=1) - 1)) > 1e-10:
            raise ArithmeticError("Smoke transition is not stochastic")
        for label, root in (("organized", roots()["organized"]),
                            ("unorganized", roots()["unorganized"])):
            vec = np.zeros(len(STATES)); vec[cap_model["index"][root]] = 1
            if abs((vec @ p).sum() - 1) > 1e-12:
                raise ArithmeticError(f"Root mass not conserved: {label}")
        for model, q in ((cap_model, qcap), (abl_model, qabl)):
            if np.max(abs(q @ model["energy"] - model["flows"]["drive_work"]
                          + model["flows"]["bath_heat"])) > 1e-9:
                raise ArithmeticError("Energy ledger failed")
        recurrent_classes = {}
        for label, q in (("capable", qcap), ("ablated", qabl)):
            count, _ = connected_components(csr_matrix((q > 0).astype(np.int8)),
                                            directed=True, connection="strong")
            recurrent_classes[label] = int(count)
            if count != 1:
                raise ArithmeticError(f"Expected one recurrent class for {label}; got {count}")
        result = {
            "status": "engineering_smoke_pass", "states": len(STATES),
            "roots": {k: {"state": v, "energy": energy(v)} for k, v in roots().items()},
            "capable_generator_nnz": int(np.count_nonzero(qcap)),
            "ablated_generator_nnz": int(np.count_nonzero(qabl)),
            "short_transition_row_error": float(max(abs(p.sum(axis=1) - 1))),
            "capable_energy_ledger_residual": float(max(abs(qcap @ cap_model["energy"]
                - cap_model["flows"]["drive_work"] + cap_model["flows"]["bath_heat"]))),
            "ablated_energy_ledger_residual": float(max(abs(qabl @ abl_model["energy"]
                - abl_model["flows"]["drive_work"] + abl_model["flows"]["bath_heat"]))),
            "recurrent_class_count": recurrent_classes,
            "source_verification": {"input_hash": manifest["input_hash"], "imports": imports},
            "ranking_or_scientific_readout": False,
        }
        (output / "smoke.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                                            encoding="utf-8")
        print(json.dumps({"status": result["status"], "states": len(STATES),
                          "generator_nnz": result["capable_generator_nnz"]}), flush=True)
        return 0

    # Scientific comparison begins only in a distinct frozen bundle/run.
    delta_grid = protocol["cadences"]
    horizons = protocol["horizons"]
    horizon_max = max(horizons)
    case_worlds = {"capable": (cap_model, qcap), "paid_path_ablated": (abl_model, qabl)}
    root_map = roots()

    def stationary(q):
        matrix = q.T.copy(); rhs = np.zeros(len(q))
        matrix[-1, :] = 1.0; rhs[-1] = 1.0
        pi = np.linalg.solve(matrix, rhs)
        if min(pi) < -1e-10 or max(abs(pi @ q)) > 1e-9:
            raise ArithmeticError("Stationary distribution failed")
        return pi

    def finite_profile(q, pi, root, delta):
        trans = expm(q * delta)
        if np.min(trans) < -1e-12 or max(abs(trans.sum(axis=1) - 1)) > 1e-10:
            raise ArithmeticError("Invalid sampled transition")
        safe = np.maximum(trans, 0.0)
        row_h = -np.sum(np.where(safe > 0, safe * np.log2(np.maximum(safe, 1e-300)), 0), axis=1)
        stationary_rate = float(pi @ row_h / delta)
        wanted = {int(round(t / delta)): t for t in horizons}
        state = np.zeros(len(q)); state[root] = 1.0
        entropy = 0.0; rows = {}
        for n in range(1, max(wanted) + 1):
            entropy += float(state @ row_h)
            state = state @ trans
            if n in wanted:
                rows[str(wanted[n])] = {"history_entropy_bits": entropy,
                                         "endpoint_distribution_entropy_bits": float(
                                             -np.sum(np.where(state > 0, state * np.log2(np.maximum(state, 1e-300)), 0)))}
        return stationary_rate, rows

    def first_passage(q, start_index, target_resource, horizon):
        killed = q.copy()
        for j, state in enumerate(STATES):
            if state[0] == target_resource:
                killed[:, j] = 0.0
        p0 = np.zeros(len(q)); p0[start_index] = 1.0
        survive = float(p0 @ expm(killed * horizon) @ np.ones(len(q)))
        return max(0.0, min(1.0, 1.0 - survive))

    def integrated_counts(q, rate, start_index, horizon):
        n = len(q); block = np.zeros((n + 1, n + 1)); block[:n, :n] = q
        block[:n, n] = rate
        p0 = np.zeros(n); p0[start_index] = 1.0
        return float(p0 @ expm(block * horizon)[:n, n])

    results = {}
    for law, (model, q) in case_worlds.items():
        pi = stationary(q)
        adjacency = csr_matrix((q > 0).astype(np.int8))
        nclasses, labels = connected_components(adjacency, directed=True, connection="strong")
        class_sizes = np.bincount(labels).tolist()
        case_roots = ["organized", "unorganized"] if law == "capable" else ["matched_ablation"]
        law_data = {"recurrent_class_count": int(nclasses), "recurrent_class_sizes": class_sizes,
                    "stationary_state_entropy_rate_by_cadence": {}, "cases": {}}
        for delta in delta_grid:
            h, _ = finite_profile(q, pi, 0, delta)
            law_data["stationary_state_entropy_rate_by_cadence"][str(delta)] = h
        for root_label in case_roots:
            root = root_map[root_label]; i = model["index"][root]
            per_cadence = {}
            for delta in delta_grid:
                hrate, profiles = finite_profile(q, pi, i, delta)
                per_cadence[str(delta)] = {"stationary_entropy_rate_bits_per_time": hrate,
                                            "finite_profiles": profiles}
            family_flux = {}
            for family in ("paid_release", "basal_release", "downstream_use", "maintenance",
                           "resource_inlet", "locked_export", "waste_export",
                           "carrier_recharge", "carrier_export", "stored_fuel_energy_consumed",
                           "drive_work", "bath_heat"):
                vector = model["flows"].get(family, np.zeros(len(q)))
                family_flux[family] = {"stationary_rate": float(pi @ vector),
                                       "expected_integral_to_Tmax": integrated_counts(q, vector, i, horizon_max)}
            nominal_resource_offer = model["metadata"]["boundary_prescription"]["resource_inlet"]
            nominal_carrier_offer = model["metadata"]["boundary_prescription"]["carrier_recharge"]
            pi_empty = float(pi @ model["observables"]["resource_present"])
            pi_charge = float(pi @ model["observables"]["charged_carrier"])
            family_flux["resource_inlet_opportunity"] = {
                "nominal_offer_rate": nominal_resource_offer,
                "accepted_stationary_flux": family_flux["resource_inlet"]["stationary_rate"],
                "offer_while_full_rate": nominal_resource_offer * pi_empty,
            }
            family_flux["carrier_recharge_opportunity"] = {
                "nominal_offer_rate": nominal_carrier_offer,
                "accepted_stationary_flux": family_flux["carrier_recharge"]["stationary_rate"],
                "offer_while_full_rate": nominal_carrier_offer * pi_charge,
            }
            law_data["cases"][root_label] = {
                "root": root, "root_energy": energy(root), "profiles_by_cadence": per_cadence,
                "stationary_functioning_apparatus": float(pi @ model["observables"]["apparatus"]),
                "stationary_precursor": float(pi @ model["observables"]["precursor"]),
                "first_passage_by_Tmax": {
                    "usable_resource": first_passage(q, i, USABLE, horizon_max),
                    "downstream_used": first_passage(q, i, WASTE, horizon_max)},
                "fluxes_and_costs": family_flux,
            }
        results[law] = law_data

    capable = results["capable"]; ablated = results["paid_path_ablated"]
    comparisons = {"same_law_root_profiles": {}, "paid_path_vs_ablation": {"cadence_entropy_rate_differences": {}}}
    for delta in delta_grid:
        c_org = capable["cases"]["organized"]["profiles_by_cadence"][str(delta)]
        c_un = capable["cases"]["unorganized"]["profiles_by_cadence"][str(delta)]
        a_org = ablated["cases"]["matched_ablation"]["profiles_by_cadence"][str(delta)]
        comparisons["same_law_root_profiles"][str(delta)] = {
            str(t): c_org["finite_profiles"][str(t)]["history_entropy_bits"]
                    - c_un["finite_profiles"][str(t)]["history_entropy_bits"]
            for t in horizons}
        comparisons["paid_path_vs_ablation"]["cadence_entropy_rate_differences"][str(delta)] = (
            c_org["stationary_entropy_rate_bits_per_time"]
            - a_org["stationary_entropy_rate_bits_per_time"])
    deltas = list(comparisons["paid_path_vs_ablation"]["cadence_entropy_rate_differences"].values())
    comparisons["paid_path_vs_ablation"]["positive_at_every_tested_cadence"] = all(x > 0 for x in deltas)
    result = {
        "status": "scientific_comparison_complete",
        "scope": "bounded driven mechanism toy; not established chemistry or open-ended expansion",
        "protocol": protocol, "input_hash": manifest["input_hash"], "imports": imports,
        "cadences": delta_grid, "horizons": horizons,
        "law_results": results, "comparisons": comparisons,
        "notes": ["Whole physical count state, including apparatus, precursor, and charged carrier, is scored.",
                  "No reservoir-access reward, churn subtraction, or no-op boundary event is added.",
                  "Same-law roots share the identical generator; capability/ablation is an explicit between-law comparison.",
                  "Accepted boundary fluxes and work are reported separately from nominal offer rates."],
    }
    (output / "comparison.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                                               encoding="utf-8")
    (output / "status.json").write_text(json.dumps({"status": result["status"],
        "positive_delta_h_all_cadences": comparisons["paid_path_vs_ablation"]["positive_at_every_tested_cadence"]}, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "positive_delta_h_all_cadences":
                      comparisons["paid_path_vs_ablation"]["positive_at_every_tested_cadence"]}), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in ("smoke", "science"):
        raise SystemExit("usage: maintained_resource_worker.py OUTPUT_DIR smoke|science")
    raise SystemExit(main(Path(sys.argv[1]).resolve(), sys.argv[2]))
