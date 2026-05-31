from __future__ import annotations

from dataclasses import dataclass

from omega.rfs_mb0_future_landscape.substrate import LandscapeSystem, State

from . import INSTRUMENT_NAME, INSTRUMENT_VERSION


CLAIM_BOUNDARY = (
    "instrumentation only: scans finite future-field topology; no Omega, agency, "
    "identity, valuerhood, value, candidate-promotion, holdout, or graph-causality claim"
)


@dataclass(frozen=True)
class ConditionSpec:
    condition_id: str
    group_id: str
    seed: int
    substrate_family: str
    substrate_variant: str
    substrate_id: str
    boundary_control: str
    role: str
    base_m: int
    effective_m: int
    core_rank_k: int
    macro_invariant_kind: str
    macro_invariant_beta: float
    perturbation_family: str
    perturbation_strength: float


@dataclass(frozen=True)
class EdgeAnatomy:
    source_state: State
    target_state: State
    candidate_rank: int
    candidate_energy: float
    selected_flag: int
    core_flag: int
    fringe_flag: int
    baseline_selected_flag: int
    perturbation_changed_flag: int


@dataclass(frozen=True)
class GeneratedCondition:
    spec: ConditionSpec
    system: LandscapeSystem
    candidate_anatomy: dict[tuple[State, State], EdgeAnatomy]
    selected_edge_keys: frozenset[tuple[State, State]]
    baseline_edge_keys: frozenset[tuple[State, State]]


@dataclass(frozen=True)
class ScanTask:
    scan_id: str
    condition: GeneratedCondition
    start_index: int
    start_state: State
    horizon_max: int
    horizon_schedule: tuple[int, ...]
    max_frontier_nodes_per_horizon: int
    max_frontier_edges_per_step: int


@dataclass
class RawScan:
    scan_id: str
    spec: ConditionSpec
    start_index: int
    start_state: State
    horizon_schedule: tuple[int, ...]
    horizon_max: int
    frontiers: dict[int, frozenset[State]]
    step_edges: dict[int, tuple[tuple[State, State], ...]]
    node_rows: list[dict[str, object]]
    edge_rows: list[dict[str, object]]


@dataclass
class MappedScan:
    raw: RawScan
    profile_rows: list[dict[str, object]]
    membership_rows: list[dict[str, object]]
    boundary_rows: list[dict[str, object]]


@dataclass
class ScanBundle:
    mapped: MappedScan
    errors: list[dict[str, object]]


def instrument_metadata() -> dict[str, object]:
    return {
        "instrument_name": INSTRUMENT_NAME,
        "instrument_version": INSTRUMENT_VERSION,
        "claim_boundary": CLAIM_BOUNDARY,
    }

