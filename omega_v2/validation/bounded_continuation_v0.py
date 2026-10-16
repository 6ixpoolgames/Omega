"""Small exact audit of proposed lower/classical-upper extent limits."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.bounded_continuation import (
    echo_profiles,
    ensemble_controls,
    eraser_profile,
    holevo_extent,
    recorded_profile,
)
from omega_v2.finite.quantum_eraser import MODES


def main():
    overlap = []
    for c in (0., .5, 1/np.sqrt(2), 1.):
        vector = np.array([c, np.sqrt(1-c*c)])
        row = holevo_extent([.5, .5], [np.diag([1., 0.]), np.outer(vector, vector)])
        row["overlap"] = c
        overlap.append(row)
    result = {
        "overlap": overlap,
        "eraser": [eraser_profile(mode, angle) for mode in MODES
                   for angle in (0., np.pi/6, np.pi/4, np.pi/2)],
        "recorded": [recorded_profile(n) for n in (1, 2, 3)],
        "echo": echo_profiles(),
        "controls": ensemble_controls(),
    }
    folder = Path("results/local_runs/bounded_continuation_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Overlap:", [(r["overlap"], r["extent"]) for r in overlap])
    print("Recorded:", result["recorded"])
    print("Echo:", result["echo"])
    print("Controls:", result["controls"])
    for row in result["eraser"]:
        print(row["mode"], row["leak_angle"],
              {k: row[k]["extent"] for k in ("marker", "environment", "joint_record",
                                             "whole_conditional_system")})


if __name__ == "__main__":
    main()
