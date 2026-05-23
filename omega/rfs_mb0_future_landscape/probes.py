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
    probe_family: str
    arity: int


def generate_probes(system: LandscapeSystem, sigma: int = 2) -> tuple[Probe, ...]:
    modulus = int(system.metadata.get("alphabet_size", system.metadata.get("modulus", MODULUS)))
    if system.family == "permissive_probe_control":
        return (Probe("probe_permissive_constant", "permissive", lambda _s: ("all",), "control_permissive", 0),)
    if system.family == "strict_probe_control":
        return (Probe("probe_strict_state", "strict", lambda s: tuple(s), "control_strict", len(system.states[0])),)
    probes: list[Probe] = []
    coordinate_count = len(system.states[0])
    for coord in range(coordinate_count):
        probes.append(
            Probe(
                f"coord_{coord}",
                "projection",
                lambda s, coord=coord: (s[coord],),
                "single_coordinate_projection",
                1,
            )
        )
    if sigma >= 2:
        for left in range(coordinate_count):
            for right in range(coordinate_count):
                if left == right:
                    continue
                probes.append(
                    Probe(
                        f"ordered_pair_{left}_{right}",
                        "ordered_pair",
                        lambda s, left=left, right=right: (s[left], s[right]),
                        "pairwise_ordered_projection",
                        2,
                    )
                )
        for left in range(coordinate_count):
            for right in range(left + 1, coordinate_count):
                probes.append(
                    Probe(
                        f"moddiff_{left}_{right}",
                        "pair_relation",
                        lambda s, left=left, right=right, modulus=modulus: ((s[left] - s[right]) % modulus,),
                        "pairwise_modular_difference",
                        2,
                    )
                )
                probes.append(
                    Probe(
                        f"equal_{left}_{right}",
                        "pair_relation",
                        lambda s, left=left, right=right: (int(s[left] == s[right]),),
                        "pairwise_equality_indicator",
                        2,
                    )
                )
                probes.append(
                    Probe(
                        f"multiset_{left}_{right}",
                        "pair_relation",
                        lambda s, left=left, right=right: tuple(sorted((s[left], s[right]))),
                        "pairwise_unordered_multiset",
                        2,
                    )
                )
    if sigma >= 3:
        for left in range(coordinate_count):
            for mid in range(left + 1, coordinate_count):
                for right in range(mid + 1, coordinate_count):
                    probes.append(
                        Probe(
                            f"triple_residue_{left}_{mid}_{right}",
                            "triple_relation",
                            lambda s, left=left, mid=mid, right=right, modulus=modulus: ((s[left] + s[mid] + s[right]) % modulus,),
                            "triple_residue",
                            3,
                        )
                    )
    return tuple(probes)
