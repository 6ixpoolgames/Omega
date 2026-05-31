from __future__ import annotations

from dataclasses import dataclass

from omega.rfs_mb0_future_landscape.substrate import LandscapeSystem, State

from . import INSTRUMENT_NAME, INSTRUMENT_VERSION


CLAIM_BOUNDARY = (
    "instrumentation only: scans finite future-field topology; no Omega, agency, "
    "identity, valuerhood, value, candidate-promotion, holdout, or graph-causality claim"
)


@dataclass(frozen=True)
class StateSpaceSpec:
    state_space_id: str
    coordinate_count: int
    alphabet_size: int
    state_count: int


@dataclass(frozen=True)
class TransformationLawSpec:
    law_id: str
    law_family: str
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
    core_rank_k: int
    retained_rank_set: tuple[int, ...]
    removed_rank_set: tuple[int, ...]
    stochastic_flag: int
    seed_policy: str
    implementation_family: str


@dataclass(frozen=True)
class ObservableSpec:
    observable_set_id: str
    observable_family: str
    observable_params_json: str


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
    human_label: str
    legacy_boundary_control_alias: str
    legacy_role_alias: str

    @property
    def substrate_family(self) -> str:
        return self.transformation_law.law_family

    @property
    def substrate_variant(self) -> str:
        return self.human_label

    @property
    def boundary_control(self) -> str:
        return self.legacy_boundary_control_alias

    @property
    def role(self) -> str:
        return self.legacy_role_alias

    @property
    def base_m(self) -> int:
        return self.selection_operator.base_out_degree

    @property
    def effective_m(self) -> int:
        return self.selection_operator.effective_out_degree

    @property
    def core_rank_k(self) -> int:
        return self.selection_operator.core_rank_k

    @property
    def macro_invariant_kind(self) -> str:
        return self.transformation_law.macro_invariant_kind

    @property
    def macro_invariant_beta(self) -> float:
        return self.transformation_law.macro_invariant_beta

    @property
    def perturbation_family(self) -> str:
        return "none" if self.selection_operator.operator_family == "rank_prefix" else self.selection_operator.operator_family

    @property
    def perturbation_strength(self) -> float:
        return 0.0 if self.selection_operator.operator_family == "rank_prefix" else 1.0


@dataclass(frozen=True)
class EdgeAnatomy:
    source_state: State
    target_state: State
    candidate_rank: int
    candidate_energy: float
    selected_flag: int
    baseline_selected_flag: int
    rank_offset_from_core_boundary: int
    perturbation_changed_flag: int

    @property
    def core_flag(self) -> int:
        return int(self.rank_offset_from_core_boundary <= 0)

    @property
    def fringe_flag(self) -> int:
        return int(self.rank_offset_from_core_boundary > 0)


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
    max_frontier_nodes_per_horizon: int
    max_frontier_edges_per_step: int
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
