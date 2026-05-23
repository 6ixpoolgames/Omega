from __future__ import annotations

from .landscape import HORIZONS, exact_frontier, signature_distribution
from .probes import Probe
from .substrate import LandscapeSystem, generate_system


def null_distribution_by_h(system: LandscapeSystem, probe: Probe) -> dict[int, dict[object, int]]:
    null_system = generate_system(system.seed + 919_191, "degree_preserving_control")
    start = system.states[(system.seed + len(probe.name)) % len(system.states)]
    return {h: signature_distribution(exact_frontier(null_system, start, h), probe) for h in HORIZONS}

