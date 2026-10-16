"""Small versioned contracts for finite classical adapters and readouts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping

State = tuple


@dataclass(frozen=True)
class Event:
    rule_id: str
    family: str
    target: State
    rate: float
    support: tuple[int, ...]
    work: float = 0.0
    increments: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleModule:
    id: str
    version: str
    events: Callable[[State], Iterable[Event]]
    requires: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorldSpec:
    id: str
    version: str
    states: tuple[State, ...]
    validate: Callable[[State], None]
    energy: Callable[[State], float]
    observables: Mapping[str, Callable[[State], float]]
    modules: tuple[RuleModule, ...]
    metadata: Mapping = field(default_factory=dict)
    degeneracy: Callable[[State], float] | None = None


@dataclass(frozen=True)
class ControllerSpec:
    id: str
    version: str
    observation: str
    responses: tuple
    memory: str = "none"
    execution: str = "native reversible gate channels"


@dataclass(frozen=True)
class MeasurementSpec:
    id: str = "sampled-count-history"
    version: str = "1"
    cadence: float = 0.25
    grain: str = "complete declared physical count state"
    max_dense_bytes: int = 768 * 1024**2


@dataclass(frozen=True)
class ExperimentSpec:
    id: str
    version: str
    status: str
    world: Mapping
    controllers: Mapping
    measurement: Mapping
    queries: Mapping
    analysis: Mapping
    limits: Mapping

    def require_scientific_freeze(self):
        if self.status != "frozen_before_scientific_ranking":
            raise ValueError("Scientific execution requires a frozen protocol")
