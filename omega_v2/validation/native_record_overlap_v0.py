"""Physical coherence endpoints, repeated records and query-refinement audit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.coherent_reference import recorded_hops
from omega_v2.finite.native_record_overlap import (
    analyze_records,
    delayed_record_echo,
    overlap_controls,
    record_copy_control,
)
from omega_v2.finite.quantum_extent import effective_number
from omega_v2.finite.spatial_futuresfield import spatial_setup


def main():
    interpolation = []
    for phi in [0., np.pi/6, np.pi/4, np.pi/2]:
        result, _, _ = analyze_records(*spatial_setup(np.pi/4, 0., phi), (1,), 2)
        result.update(marker=phi, analytic_extent=effective_number([(1+np.cos(phi))/2, (1-np.cos(phi))/2]))
        result["analytic_error"] = abs(result["overlap_extent"]-result["analytic_extent"])
        interpolation.append(result)
    growth = []
    for n in range(1, 5):
        psi, _, stages = recorded_hops(n)
        result, _, _ = analyze_records(psi, stages, range(1, n+1), n+1)
        result["hops"] = n
        growth.append(result)
    echo = {}
    for refined in [False, True]:
        result, _, _ = analyze_records(*delayed_record_echo(refined), (1,), 2)
        echo["refined" if refined else "endpoint"] = result
    actual_marker, _, _ = analyze_records(*spatial_setup(np.pi/4, -np.pi/4, np.pi/2), (1,), 2)
    controls = overlap_controls()
    copies = record_copy_control()
    results = {"interpolation": interpolation, "growth": growth, "delayed_record_echo": echo,
               "actual_midpoint_record": actual_marker, "copy_control": copies, "controls": controls}
    errors = [v for row in interpolation+growth+list(echo.values())+[actual_marker, copies, controls]
              for key, v in row.items() if key.endswith("_error")]
    assert max(errors) < 1e-12
    folder = Path("results/local_runs/native_record_overlap_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Interpolation:", [(r["marker"], r["overlap_extent"]) for r in interpolation])
    print("Growth (n,overlap,actual memory,record basis):", [(r["hops"], r["overlap_extent"],
          r["actual_record_rank_extent"], r["record_basis_breadth"]) for r in growth])
    print("Delayed-record echo:", echo)
    print("Actual midpoint record:", actual_marker)
    print("Copies:", copies)
    print("Controls:", controls)
    print("Maximum check error:", max(errors))


if __name__ == "__main__":
    main()
