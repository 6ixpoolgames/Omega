"""Exact tiny spatial probe; raw data stays ignored locally."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.spatial_futuresfield import analyze, representation_checks, spatial_setup


def main():
    cases = [
        ("idle", 0., 0., 0.),
        ("spread_hold", np.pi / 4, 0., 0.),
        ("echo", np.pi / 4, -np.pi / 4, 0.),
        ("through", np.pi / 4, np.pi / 4, 0.),
        ("unequal", np.pi / 4, np.pi / 6, 0.),
        ("phase", np.pi / 4, np.pi / 6, np.pi / 2),
    ]
    results = []
    for name, first, second, phase in cases:
        for marker in [0., np.pi / 6, np.pi / 4, np.pi / 2]:
            result, _, _ = analyze(*spatial_setup(first, second, marker, phase))
            result.update(case=name, first=first, second=second, marker=marker, phase=phase)
            expected = np.cos(first)**2 * np.cos(second)**2 + np.sin(first)**2 * np.sin(second)**2
            expected -= 2 * np.cos(first) * np.sin(first) * np.cos(second) * np.sin(second) * np.cos(marker) * np.cos(phase)
            result["analytic_born_error"] = float(abs(result["site_probabilities"][-1][0] - expected))
            results.append(result)
    controls = representation_checks()
    errors = {key: max(r[key] for r in results) for key in results[0] if key.endswith("_error")}
    assert max(errors.values()) < 1e-12
    assert max(v for k, v in controls.items() if k.endswith("_error")) < 1e-12
    folder = Path("results/local_runs/spatial_futuresfield_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps({"profiles": results, "controls": controls,
                                                   "errors": errors}, indent=2), encoding="utf-8")
    print(f"{len(results)} profiles; {sum(r['candidate_extent'] is None for r in results)} invalid signed extents")
    for r in results:
        print(f"{r['case']:12} marker={r['marker']:.6f} q={np.round(r['q'], 6)} "
              f"V={r['candidate_extent']} site={r['site_breadths'][-1]:.6f} "
              f"joint={r['joint_endpoint_breadth']:.6f}")
    print("Errors:", errors)
    print("Controls:", controls)


if __name__ == "__main__":
    main()
