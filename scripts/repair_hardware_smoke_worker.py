"""Engineering only: fixed policy, no scientific ranking."""
import sys

if __name__ == "__main__" and sys.stdin.readline().strip() != "GO":
    raise SystemExit("Caps must be installed before imports")

import json
from pathlib import Path
from time import perf_counter


def main(out, exact=False):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    import numpy as np
    from scipy.linalg import expm
    from scipy.sparse.linalg import expm_multiply

    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.modules.repair_hardware import RepairHardware, build_world
    rows = []
    policy = ((.5, .5),) * 4
    for mode in ("fast", "slow", "hardware_loss"):
        started = perf_counter()
        world = build_world((1, 1), policy=policy, config=RepairHardware(mode=mode))
        compiled = compile_world(world)
        q = compiled["Q"]
        kernel = expm(q.toarray() * .25)
        root = ((0, 1, 0, 1, 0), (0, 1, 0, 1, 0), (1, 1))
        probability = np.zeros(len(world.states))
        probability[compiled["index"][root]] = 1
        for _ in range(16):
            probability = probability @ kernel
        row = {"mode": mode, "states": len(world.states), "seconds": perf_counter()-started,
                   "generator_mass_residual": float(np.max(np.abs(q.sum(axis=1)))),
                   "kernel_mass_residual": float(np.max(np.abs(kernel.sum(axis=1)-1))),
                   "probability_mass_residual": float(abs(probability.sum()-1)),
                   "minimum_kernel_entry": float(kernel.min()),
                   "energy_residual": float(np.max(np.abs(q @ compiled["energy"]
                         - compiled["flows"]["drive_work"] + compiled["flows"]["bath_heat"])))}
        if max(row[key] for key in ("generator_mass_residual", "kernel_mass_residual",
                                    "probability_mass_residual", "energy_residual")) > 1e-9:
            raise ArithmeticError("Smoke numerical invariant failed")
        if kernel.min() < -1e-12:
            raise ArithmeticError("Negative transition probability")
        rows.append(row)
    # Profile the intended larger schema sparsely without ranking or allocating
    # a dense transition matrix. Exact-entropy memory is a separate future gate.
    started = perf_counter()
    world = build_world((3, 1), policy=policy,
                        config=RepairHardware(mode="hardware_loss"))
    compiled = compile_world(world)
    root = ((0, 3, 0, 3, 0), (0, 1, 0, 1, 0), (1, 1))
    probability = np.zeros(len(world.states))
    probability[compiled["index"][root]] = 1
    probability = expm_multiply(compiled["Q"].T * 4, probability)
    residual = float(abs(probability.sum() - 1))
    if residual > 1e-9 or probability.min() < -1e-12:
        raise ArithmeticError("Larger sparse propagation failed")
    rows.append({"mode": "hardware_loss_3+1_sparse_feasibility",
                 "states": len(world.states), "seconds": perf_counter()-started,
                 "probability_mass_residual": residual,
                 "dense_kernel_bytes": len(world.states)**2 * 8,
                 "exact_entropy_memory_gate": "not yet profiled"})
    if exact:
        from omega_v2.testbed.analysis.blocked_entropy import profile
        started = perf_counter()
        result = profile(compiled['Q'], {'root': compiled['index'][root]}, .25,
                         [1, 4, 16, 64, 256])
        rows.append({'mode': 'hardware_loss_3+1_exact_entropy_feasibility',
                     'seconds': perf_counter()-started, 'states': len(result['keep']),
                     'classes': result['classes'], 'residuals': result['residuals'],
                     'finite_score_check': 'computed; withheld from engineering selection'})
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith("omega_v2") and getattr(module, "__file__", None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError("Unfrozen Omega import")
    result = {"status": "engineering_smoke_complete", "input_hash": manifest["input_hash"],
                  "policy": "fixed half-service/half-export; no ranking", "rows": rows,
                  "imports": imports}
    (out / "RESULTS.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), len(sys.argv) > 2 and sys.argv[2] == 'exact')
