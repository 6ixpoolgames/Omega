"""Exact interaction-selection, refinement and quantum extent comparison."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np

from omega_v2.finite.interaction_selected_history import (
    PAULI,
    competing_case,
    conserved_axes,
    environment_preparation_control,
    physical_orientation_control,
    representation_controls,
    single_axis_case,
)
from omega_v2.finite.quantum_readers import local_gate, record_retention


def main():
    started = perf_counter()
    single = [single_axis_case(g, m, angle)
              for m in [1, 2, 3]
              for g in [0, np.pi/16, np.pi/8, np.pi/4, np.pi/2]
              for angle in [0, .37, np.pi/2]]
    competing = [competing_case(r, mode) for r in [0, .25, 1, 4]
                 for mode in ["ZX", "XZ", "simultaneous"]]
    controls = representation_controls()
    z = local_gate(PAULI[2], 0, 3)
    parallel = [z @ local_gate(PAULI[1], j, 3) for j in [1, 2]]
    results = {
        "single_axis": single, "competing": competing,
        "representation": controls,
        "physical_orientation": physical_orientation_control(),
        "environment_preparation": environment_preparation_control(),
        "parallel_selection": conserved_axes(parallel, 3),
        "retention": {mode: record_retention(mode) for mode in ["retain", "uncompute", "transfer"]},
    }
    results["runtime_seconds"] = perf_counter()-started
    errors = {key: max(row[key] for row in single) for key in [
        "born_error", "amplitude_reconstruction_error", "normalization_error", "trace_error",
        "analytic_overlap_error", "analytic_coherence_error"]}
    errors.update(controls["errors"])
    if max(abs(value) for value in errors.values()) >= 1e-10:
        raise AssertionError(f"Exact reconstruction failure: {errors}")
    results["max_errors"] = errors
    folder = Path("results/local_runs/interaction_selected_history_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"45 aligned profiles,12 competing cases; runtime {results['runtime_seconds']:.3f}s")
    print("m, g/pi, commutant dimension, source coherence, env trace distance, diagonal, spectral, output, observational")
    for row in single:
        if row["angle"] == 0:
            print(row["copies"], round(row["coupling"]/np.pi, 4), row["selection"]["dimension"],
                  *[round(row[k], 6) for k in ["relative_source_coherence", "environment_trace_distance",
                    "fine_history_breadth", "spectral_breadth", "record_breadth", "observational_extent"]])
    print("competition: ratio mode null-dimension, Z-output/X-output, ZZ-spectrum/XX-spectrum")
    for row in competing:
        print(row["ratio"], row["mode"], row["selection"]["dimension"],
              *[round(row["readouts"][axis][key], 6) for key in ["record_breadth", "spectral_breadth"]
                for axis in ["ZZ", "XX"]])
    print("refinements", controls["refinements"])
    print("errors", errors)
    print("blank observational", controls["original"]["observational_extent"],
          controls["blank"]["observational_extent"])
    print("environment preparation", {
        name: {k: row[k] for k in ["conditional_overlap_magnitude", "environment_trace_distance",
                                   "spectral_breadth", "record_breadth"]}
        for name, row in results["environment_preparation"].items()})


if __name__ == "__main__":
    main()
