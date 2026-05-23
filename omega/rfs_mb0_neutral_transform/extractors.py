from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .substrate import NeutralSystem, State, block_relation_mu, block_relation_nu

Signature = tuple[object, ...]


@dataclass(frozen=True)
class Candidate:
    name: str
    coordinate_block: tuple[int, ...]
    signature: Callable[[State], Signature]


def extract_candidates(system: NeutralSystem) -> tuple[Candidate, Candidate]:
    if system.extractor_mode == "permissive":
        return (
            Candidate("mu", (0, 1, 4), lambda _state: ("all",)),
            Candidate("nu", (2, 3, 4), lambda _state: ("all",)),
        )
    if system.extractor_mode == "strict":
        return (
            Candidate("mu", tuple(range(len(system.initial_state))), lambda state: tuple(state)),
            Candidate("nu", tuple(range(len(system.initial_state))), lambda state: tuple(state)),
        )
    return (
        Candidate("mu", (0, 1, 4), lambda state: tuple(block_relation_mu(state))),
        Candidate("nu", (2, 3, 4), lambda state: tuple(block_relation_nu(state))),
    )


def continuity_predicate(candidate: Candidate, initial: State) -> Callable[[State], bool]:
    initial_signature = candidate.signature(initial)
    return lambda state: candidate.signature(state) == initial_signature

