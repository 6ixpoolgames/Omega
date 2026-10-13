"""Capped worker; waits for Job Object assignment before numerical imports."""
from __future__ import annotations

import sys
if __name__ == "__main__" and sys.stdin.readline().strip() != "GO":
    raise SystemExit("Parent must verify frozen sources and install caps before release")

import hashlib
import json
from pathlib import Path


def main(output: Path) -> int:
    source_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source_root))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(output)
    source_hashes = {row["path"]: row["sha256"] for row in manifest["sources"]}

    # These numerical imports occur only after the cap runner sends GO.
    import numpy as np
    from scipy.linalg import expm
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.locked_resource import build_world, describe, make_root

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

    world = build_world()
    if len(world.states) > 32:
        raise RuntimeError("Smoke state cap exceeded; no truncation attempted")
    model = compile_world(world, max_states=32)
    q = model["Q"].toarray()
    transition = expm(q * 0.05)
    row_error = float(max(abs(transition.sum(axis=1) - 1)))
    if np.min(transition) < -1e-12 or row_error > 1e-10:
        raise ArithmeticError("Short-time transition is not stochastic")
    index = model["index"]
    roots = {}
    for label, root in (("organized", make_root(True)), ("unorganized", make_root(False))):
        p0 = np.zeros(len(world.states)); p0[index[root]] = 1.0
        p1 = p0 @ transition
        roots[label] = {
            "root_energy": float(model["energy"][index[root]]),
            "mass_after_short_propagation": float(p1.sum()),
            "expected_fuel_after_short_propagation": float(p1 @ model["observables"]["fuel"]),
            "expected_product_after_short_propagation": float(p1 @ model["observables"]["product"]),
        }
    result = {
        "status": "engineering_smoke_pass",
        "fixture": describe(),
        "transition": {"cadence": 0.05, "minimum_entry": float(transition.min()),
                       "max_row_sum_error": row_error},
        "roots": roots,
        "ledger_residuals": {
            "energy": float(max(abs(q @ model["energy"] - model["flows"]["drive_work"]
                                     + model["flows"]["bath_heat"]))),
            "fuel_inventory_energy": float(max(abs(q @ model["observables"]["fuel_inventory_energy"]
                                                   + model["flows"]["stored_fuel_energy_consumed"]))),
            "external_drive_work_max": float(max(abs(model["flows"]["drive_work"]))),
        },
        "resources": {"states": len(world.states), "dense_matrix_bytes": int(q.nbytes)},
        "source_verification": {"input_hash": manifest["input_hash"], "imports": imports},
        "ranking_or_scientific_readout": False,
    }
    (output / "smoke.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                                        encoding="utf-8")
    print(json.dumps({"status": result["status"], "states": len(world.states),
                      "max_row_sum_error": row_error,
                      "source_imports_verified": len(imports)}), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: locked_resource_smoke_worker.py OUTPUT_DIR")
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
