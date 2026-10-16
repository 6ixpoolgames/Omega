"""Test a propagated reference on the full complex history kernel."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from omega_v2.finite.coherent_reference import (
    pair_for,
    recorded_hops,
    reference_controls,
    reference_extent,
    spatial_reference,
)
from omega_v2.finite.quantum_extent import effective_number
from omega_v2.finite.spatial_futuresfield import spatial_setup


def main():
    cases = [("idle", 0., 0., 0.), ("spread_hold", np.pi/4, 0., 0.),
             ("echo", np.pi/4, -np.pi/4, 0.), ("through", np.pi/4, np.pi/4, 0.),
             ("unequal", np.pi/4, np.pi/6, 0.), ("phase", np.pi/4, np.pi/6, np.pi/2)]
    profiles = []
    for name, first, second, phase in cases:
        for marker in [0., np.pi/6, np.pi/4, np.pi/2]:
            psi, stages = spatial_setup(first, second, marker, phase)
            d, m = pair_for(psi, spatial_reference(), stages)
            row = reference_extent(d, m)
            row.update(case=name, marker=marker, spectral_control=reference_extent(d, np.eye(len(d)))["extent"],
                       trace_d_error=float(abs(np.trace(d)-1)), trace_m_error=float(abs(np.trace(m)-2)),
                       reference_dominance_minimum=float(np.linalg.eigvalsh(m-d).min()))
            assert 1-1e-10 <= row["extent"] <= 2+1e-10
            profiles.append(row)
    growth = []
    for n in range(1, 5):
        psi, reference, stages = recorded_hops(n)
        d, m = pair_for(psi, reference, stages)
        row = reference_extent(d, m)
        row.update(hops=n, classical_breadth=effective_number(d.diagonal().real),
                   offdiagonal_max=float(np.max(abs(d-np.diag(d.diagonal())))))
        growth.append(row)
    controls = reference_controls()
    assert max(v for k, v in controls.items() if k.endswith("_error")) < 1e-10
    folder = Path("results/local_runs/coherent_reference_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder/"results.json").write_text(json.dumps({"profiles": profiles, "recorded_growth": growth,
                                                 "controls": controls}, indent=2), encoding="utf-8")
    for row in profiles:
        print(f"{row['case']:12} marker={row['marker']:.6f} Vref={row['extent']:.6f} spectral={row['spectral_control']:.6f}")
    print("Recorded growth:", growth)
    print("Controls:", controls)


if __name__ == "__main__":
    main()
