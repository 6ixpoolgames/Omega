"""Run tiny exact interference/breadth probes; keep raw output local."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.quantum_extent import circuit, evaluate


def main():
    results = []
    for phase_name, phase in [("0", 0), ("pi/2", np.pi / 2), ("pi", np.pi)]:
        for eta in [1.0, 0.5, 0.0]:
            for reader in ["signal", "joint", "eraser"]:
                result, _ = evaluate(*circuit(phase, eta, reader))
                result.update(phase=phase_name, eta=eta, reader=reader, checkpoints="z")
                results.append(result)
    for checkpoint in ["none", "zx"]:
        result, _ = evaluate(*circuit(checkpoints=checkpoint))
        result.update(phase="0", eta=1.0, reader="signal", checkpoints=checkpoint)
        results.append(result)
    errors = {key: max(row[key] for row in results) for key in [
        "born_error", "amplitude_reconstruction_error", "normalization_error", "trace_error"]}
    assert max(errors.values()) < 1e-12
    folder = Path("results/local_runs/quantum_extent_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"{len(results)} exact profiles; errors {errors}")
    for row in results:
        if (row["reader"] == "signal" or
                row["eta"] == 0 and row["reader"] in {"joint", "eraser"}):
            print(f"phase={row['phase']:4} eta={row['eta']} {row['reader']:6} "
                  f"checkpoint={row['checkpoints']:4} "
                  f"diag={row['fine_history_breadth']:.6f} "
                  f"spectral={row['spectral_breadth']:.6f} "
                  f"record={row['record_breadth']:.6f} "
                  f"p={np.round(row['record_probabilities'], 6)}")


if __name__ == "__main__":
    main()
