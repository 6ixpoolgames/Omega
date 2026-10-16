"""Exact quantum eraser panel; never discard conditional outcomes."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.quantum_eraser import MODES, eraser_case


def main():
    rows = []
    summaries = []
    timing_error = 0.
    for mode in MODES:
        for leak in [0., np.pi/6, np.pi/4, np.pi/2]:
            group = []
            for phase in [0., np.pi/2, np.pi, 3*np.pi/2]:
                row, state = eraser_case(mode, leak, phase)
                rows.append(row)
                group.append(row)
                if mode == "eraser_delayed":
                    _, early = eraser_case("eraser_early", leak, phase)
                    timing_error = max(timing_error, float(np.max(abs(early-state))))
            signal_curve = [r["signal_probabilities"][0] for r in group]
            conditional_visibility = []
            for m in range(2):
                curve = [r["conditional_signal"][m][0] for r in group if r["conditional_signal"][m] is not None]
                conditional_visibility.append(None if not curve else (max(curve)-min(curve))/(max(curve)+min(curve)))
            summaries.append({"mode": mode, "leak_angle": leak,
                              "unconditional_visibility": (max(signal_curve)-min(signal_curve))/(max(signal_curve)+min(signal_curve)),
                              "conditional_visibilities": conditional_visibility,
                              "phase_zero_signal_breadth": group[0]["signal_breadth"],
                              "phase_zero_joint_breadth": group[0]["record_breadth"],
                              "path_record_trace_distance": group[0]["path_record_trace_distance"],
                              "specified_marker_readout_path_tv": group[0]["specified_marker_readout_path_tv"]})
    errors = {key: max(r[key] for r in rows) for key in rows[0] if key.endswith("_error")}
    errors["early_late_state_error"] = timing_error
    assert max(errors.values()) < 1e-12
    folder = Path("results/local_runs/quantum_eraser_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"results.json").write_text(json.dumps({"profiles": rows, "summaries": summaries, "errors": errors}, indent=2), encoding="utf-8")
    print(f"{len(rows)} exact profiles")
    for s in summaries:
        print(s)
    print("Errors:", errors)


if __name__ == "__main__":
    main()
