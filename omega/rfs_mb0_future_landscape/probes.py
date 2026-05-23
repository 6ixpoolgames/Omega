from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .substrate import MODULUS, LandscapeSystem, State

Signature = tuple[object, ...]


@dataclass(frozen=True)
class Probe:
    name: str
    mode: str
    fn: Callable[[State], Signature]


def generate_probes(system: LandscapeSystem, sigma: int = 2) -> tuple[Probe, ...]:
    if system.family == "permissive_probe_control":
        return (Probe("probe_permissive_constant", "permissive", lambda _s: ("all",)),)
    if system.family == "strict_probe_control":
        return (Probe("probe_strict_state", "strict", lambda s: tuple(s)),)
    probes: list[Probe] = [
        Probe("projection_q0", "projection", lambda s: (s[0],)),
        Probe("projection_q1", "projection", lambda s: (s[1],)),
        Probe("projection_q2", "projection", lambda s: (s[2],)),
        Probe("relation_q0_q1", "pair_relation", lambda s: ((s[0] - s[1]) % MODULUS,)),
        Probe("relation_q1_q2", "pair_relation", lambda s: ((s[1] - s[2]) % MODULUS,)),
        Probe("parity_q0_q1_q2", "modular_relation", lambda s: ((s[0] + s[1] + s[2]) % 2,)),
    ]
    return tuple(probes[: max(1, min(len(probes), sigma * 3))])

