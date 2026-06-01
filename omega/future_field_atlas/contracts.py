from __future__ import annotations

from dataclasses import asdict, dataclass

from omega.rfs_mb0_future_landscape.substrate import LandscapeSystem, State

from . import INSTRUMENT_NAME, INSTRUMENT_VERSION
from .util import canonical_json, stable_hash


CLAIM_BOUNDARY = (
    "instrumentation only: scans finite future-field topology; no Omega, agency, "
    "identity, valuerhood, value, candidate-promotion, holdout, or graph-causality claim"
)


@dataclass(frozen=True)
class StateSpaceSpec:
    state_space_id: str
    coordinate_set_id: str
    coordinate_count: int
    symbol_domain_id: str
    alphabet_size: int
    state_count: int
    state_id_schema: str
    metric_id: str
    adjacency_rule_id: str
    state_space_params_json: str


@dataclass(frozen=True)
class TransformationLawSpec:
    law_id: str
    law_family: str
    candidate_successor_rule_id: str
    candidate_successor_params_json: str
    energy_function_id: str
    energy_params_json: str
    admissibility_predicate_id: str
    invariant_observable_id: str
    invariant_params_json: str
    asymmetry_term_id: str
    roughness_term_id: str
    stochastic_flag: int
    seed_policy: str
    law_params_json: str
    macro_invariant_kind: str
    macro_invariant_beta: float


@dataclass(frozen=True)
class SelectionOperatorSpec:
    selection_operator_id: str
    operator_family: str
    operator_params_json: str
    base_out_degree: int
    effective_out_degree: int
    retained_rank_set: tuple[int, ...]
    removed_rank_set: tuple[int, ...]
    stochastic_flag: int
    seed_policy: str


@dataclass(frozen=True)
class ObservableSpec:
    observable_set_id: str
    observable_family: str
    rank_boundary_k: int
    feature_map_ids: tuple[str, ...]
    observable_params_json: str


@dataclass(frozen=True)
class FrontierScanSpec:
    frontier_scan_id: str
    frontier_expansion_rule_id: str
    horizon_schedule_id: str
    horizon_schedule: tuple[int, ...]
    horizon_max: int
    node_artifact_retention_policy: str
    edge_artifact_retention_policy: str
    frontier_scan_params_json: str
    max_frontier_nodes_per_horizon: int
    max_frontier_edges_per_step: int


@dataclass(frozen=True)
class ConditionSpec:
    condition_id: str
    group_id: str
    seed: int
    substrate_id: str
    state_space: StateSpaceSpec
    transformation_law: TransformationLawSpec
    selection_operator: SelectionOperatorSpec
    observable: ObservableSpec

    @property
    def rank_boundary_k(self) -> int:
        return self.observable.rank_boundary_k

    @property
    def macro_invariant_kind(self) -> str:
        return self.transformation_law.macro_invariant_kind

    @property
    def macro_invariant_beta(self) -> float:
        return self.transformation_law.macro_invariant_beta


@dataclass(frozen=True)
class EdgeAnatomy:
    source_state: State
    target_state: State
    candidate_rank: int
    candidate_energy: float
    selected_flag: int
    reference_selected_flag: int
    rank_offset_from_boundary: int
    perturbation_changed_flag: int

    @property
    def inside_rank_boundary_flag(self) -> int:
        return int(self.rank_offset_from_boundary <= 0)

    @property
    def outside_rank_boundary_flag(self) -> int:
        return int(self.rank_offset_from_boundary > 0)


@dataclass(frozen=True)
class GeneratedCondition:
    spec: ConditionSpec
    system: LandscapeSystem
    candidate_anatomy: dict[tuple[State, State], EdgeAnatomy]
    selected_edge_keys: frozenset[tuple[State, State]]
    reference_edge_keys: frozenset[tuple[State, State]]


@dataclass(frozen=True)
class ScanTask:
    scan_id: str
    condition: GeneratedCondition
    frontier_scan: FrontierScanSpec
    start_index: int
    start_state: State

    @property
    def horizon_max(self) -> int:
        return self.frontier_scan.horizon_max

    @property
    def horizon_schedule(self) -> tuple[int, ...]:
        return self.frontier_scan.horizon_schedule

    @property
    def max_frontier_nodes_per_horizon(self) -> int:
        return self.frontier_scan.max_frontier_nodes_per_horizon

    @property
    def max_frontier_edges_per_step(self) -> int:
        return self.frontier_scan.max_frontier_edges_per_step


@dataclass
class RawScan:
    scan_id: str
    spec: ConditionSpec
    frontier_scan: FrontierScanSpec
    start_index: int
    start_state: State
    frontiers: dict[int, frozenset[State]]
    step_edges: dict[int, tuple[tuple[State, State], ...]]
    node_rows: list[dict[str, object]]
    edge_rows: list[dict[str, object]]

    @property
    def horizon_max(self) -> int:
        return self.frontier_scan.horizon_max

    @property
    def horizon_schedule(self) -> tuple[int, ...]:
        return self.frontier_scan.horizon_schedule

    @property
    def max_frontier_nodes_per_horizon(self) -> int:
        return self.frontier_scan.max_frontier_nodes_per_horizon

    @property
    def max_frontier_edges_per_step(self) -> int:
        return self.frontier_scan.max_frontier_edges_per_step


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


def spec_payload(spec: object) -> dict[str, object]:
    return asdict(spec)  # type: ignore[arg-type]


def spec_canonical_json(spec: object) -> str:
    return canonical_json(spec_payload(spec))


def spec_digest(spec: object) -> str:
    return stable_hash(spec_canonical_json(spec), length=20)
