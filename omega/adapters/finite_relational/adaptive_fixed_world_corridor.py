"""Finite adaptive fixed-world corridor witnesses.

This module keeps B2.1 exploratory: unknown-but-fixed ambiguity is represented
by a lifted information state ``(x, M)`` where ``M`` is the remaining set of
possible models. The adaptive kernel is the ordinary switching robust kernel of
that lifted system.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, TypeAlias, TypeVar

State: TypeAlias = str
Action: TypeAlias = str
ModelId: TypeAlias = str
Edge: TypeAlias = tuple[State, Action, State]
InfoState: TypeAlias = tuple[State, frozenset[ModelId]]
UpdateRule: TypeAlias = Callable[["AdaptiveCorridorCase", InfoState, Action, State], frozenset[ModelId]]
T = TypeVar("T")


@dataclass(frozen=True)
class FixedWorldModel:
    """One possibilistic model in an unknown-but-fixed ambiguity family."""

    model_id: ModelId
    transitions: tuple[Edge, ...]


@dataclass(frozen=True)
class AdaptiveCorridorCase:
    """Finite ambiguity case for adaptive fixed-world corridor diagnostics."""

    case_id: str
    states: tuple[State, ...]
    actions: tuple[Action, ...]
    models: tuple[FixedWorldModel, ...]
    safe_states: frozenset[State]
    requirement_states: frozenset[State]
    start: State
    description: str

    @property
    def model_ids(self) -> frozenset[ModelId]:
        return frozenset(model.model_id for model in self.models)


@dataclass(frozen=True)
class AdaptiveCorridorStudy:
    """Retained B2.1 witness study."""

    cases: tuple[AdaptiveCorridorCase, ...]
    diagnostics: tuple[dict[str, object], ...]

    def summary(self) -> dict[str, object]:
        return {
            "case_count": len(self.cases),
            "diagnostics": list(self.diagnostics),
            "learnable_case_count": sum(
                1 for diag in self.diagnostics if diag.get("learnable_gap") is True
            ),
            "unlearnable_case_count": sum(
                1 for diag in self.diagnostics if diag.get("unlearnable_gap") is True
            ),
            "fake_update_case_count": sum(
                1 for diag in self.diagnostics if diag.get("fake_update_failure") is True
            ),
            "truth_preservation_failure_count": sum(
                int(diag.get("sound_update_truth_preservation_failures", 0))
                for diag in self.diagnostics
            ),
        }


def successors(case: AdaptiveCorridorCase, model_id: ModelId, x: State, a: Action) -> frozenset[State]:
    model = _model_by_id(case, model_id)
    return frozenset(y for source, action, y in model.transitions if source == x and action == a)


def sound_update(case: AdaptiveCorridorCase, info: InfoState, a: Action, y: State) -> frozenset[ModelId]:
    """Keep exactly the remaining models that can explain the observed successor."""

    x, remaining = info
    return frozenset(model_id for model_id in remaining if y in successors(case, model_id, x, a))


def frozen_update(
    case: AdaptiveCorridorCase, info: InfoState, a: Action, y: State
) -> frozenset[ModelId]:
    """Disable learning while still rejecting impossible observations."""

    del case, a, y
    _x, remaining = info
    return remaining


def fake_drop_to_m0_update(
    case: AdaptiveCorridorCase, info: InfoState, a: Action, y: State
) -> frozenset[ModelId]:
    """Fabricating update used by the retained fake-corridor witness."""

    del info, a, y
    if "m0" in case.model_ids:
        return frozenset({"m0"})
    return frozenset()


def truth_preservation_failures(
    case: AdaptiveCorridorCase,
    update_rule: UpdateRule = sound_update,
) -> list[dict[str, object]]:
    """Return concrete updates that drop a true model able to produce the observation."""

    failures: list[dict[str, object]] = []
    for x in case.states:
        for remaining in _nonempty_subsets(case.model_ids):
            info = (x, remaining)
            for a in case.actions:
                for model_id in sorted(remaining):
                    for y in sorted(successors(case, model_id, x, a)):
                        updated = update_rule(case, info, a, y)
                        if model_id not in updated:
                            failures.append(
                                {
                                    "state": x,
                                    "remaining_models": sorted(remaining),
                                    "action": a,
                                    "true_model": model_id,
                                    "observed_successor": y,
                                    "updated_models": sorted(updated),
                                }
                            )
    return failures


def switching_kernel(
    case: AdaptiveCorridorCase,
    model_ids: frozenset[ModelId] | None = None,
) -> frozenset[State]:
    """Switching robust kernel on ordinary states for a model set."""

    models = case.model_ids if model_ids is None else model_ids

    def constraint(x: State) -> bool:
        return x in case.safe_states and x in case.requirement_states

    def action_successors(x: State, a: Action) -> frozenset[State] | None:
        if not _enabled_in_all(case, models, x, a):
            return None
        merged: set[State] = set()
        for model_id in models:
            merged.update(successors(case, model_id, x, a))
        return frozenset(merged)

    return _greatest_kernel(set(case.states), case.actions, constraint, action_successors)


def adaptive_kernel(
    case: AdaptiveCorridorCase,
    update_rule: UpdateRule = sound_update,
) -> frozenset[InfoState]:
    """Adaptive fixed-world kernel over lifted information states."""

    universe = {
        (x, remaining)
        for x in case.states
        for remaining in _nonempty_subsets(case.model_ids)
    }

    def constraint(info: InfoState) -> bool:
        x, remaining = info
        return bool(remaining) and x in case.safe_states and x in case.requirement_states

    def action_successors(info: InfoState, a: Action) -> frozenset[InfoState] | None:
        x, remaining = info
        if not _enabled_in_all(case, remaining, x, a):
            return None
        observed: set[State] = set()
        for model_id in remaining:
            observed.update(successors(case, model_id, x, a))
        lifted: set[InfoState] = set()
        for y in observed:
            updated = update_rule(case, info, a, y)
            if not updated:
                return None
            lifted.add((y, updated))
        return frozenset(lifted)

    return _greatest_kernel(universe, case.actions, constraint, action_successors)


def frozen_kernel(case: AdaptiveCorridorCase) -> frozenset[InfoState]:
    """Adaptive kernel with the observation update disabled."""

    return adaptive_kernel(case, frozen_update)


def preserving_actions(
    case: AdaptiveCorridorCase,
    info: InfoState,
    kernel: frozenset[InfoState],
    update_rule: UpdateRule,
) -> frozenset[Action]:
    """Actions whose lifted successors all remain inside a supplied kernel."""

    x, remaining = info
    actions: set[Action] = set()
    for a in case.actions:
        if not _enabled_in_all(case, remaining, x, a):
            continue
        observed: set[State] = set()
        for model_id in remaining:
            observed.update(successors(case, model_id, x, a))
        lifted: set[InfoState] = set()
        failed = False
        for y in observed:
            updated = update_rule(case, info, a, y)
            if not updated:
                failed = True
                break
            lifted.add((y, updated))
        if not failed and lifted and all(next_info in kernel for next_info in lifted):
            actions.add(a)
    return frozenset(actions)


def epistemically_load_bearing_actions(case: AdaptiveCorridorCase, info: InfoState) -> frozenset[Action]:
    """Actions preserving the adaptive kernel but not the frozen-knowledge kernel."""

    adaptive = adaptive_kernel(case)
    frozen = frozen_kernel(case)
    adaptive_actions = preserving_actions(case, info, adaptive, sound_update)
    frozen_actions = preserving_actions(case, info, frozen, frozen_update)
    return frozenset(action for action in adaptive_actions if action not in frozen_actions)


def generate_adaptive_fixed_world_corridor_study() -> AdaptiveCorridorStudy:
    cases = (
        _learnable_ambiguity_case(),
        _unlearnable_ambiguity_case(),
        _fake_update_case(),
    )
    diagnostics = tuple(_diagnose_case(case) for case in cases)
    return AdaptiveCorridorStudy(cases=cases, diagnostics=diagnostics)


def adaptive_fixed_world_corridor_summary() -> dict[str, object]:
    return generate_adaptive_fixed_world_corridor_study().summary()


def _diagnose_case(case: AdaptiveCorridorCase) -> dict[str, object]:
    all_models = case.model_ids
    start_info = (case.start, all_models)
    switching = switching_kernel(case)
    adaptive = adaptive_kernel(case)
    frozen = frozen_kernel(case)
    singleton_start_membership = {
        model_id: (case.start, frozenset({model_id})) in adaptive for model_id in sorted(all_models)
    }
    sound_failures = truth_preservation_failures(case)
    fake_failures = truth_preservation_failures(case, fake_drop_to_m0_update)
    fake_kernel = adaptive_kernel(case, fake_drop_to_m0_update)
    fake_bad_successor = "bad" in successors(case, "m1", "p1", "stay0")
    diag = {
        "case_id": case.case_id,
        "description": case.description,
        "start": case.start,
        "model_ids": sorted(all_models),
        "switching_kernel": sorted(switching),
        "adaptive_kernel": _format_info_states(adaptive),
        "frozen_kernel": _format_info_states(frozen),
        "start_in_switching_kernel": case.start in switching,
        "start_in_adaptive_kernel": start_info in adaptive,
        "start_in_frozen_kernel": start_info in frozen,
        "singleton_start_membership": singleton_start_membership,
        "epistemically_load_bearing_actions": sorted(
            epistemically_load_bearing_actions(case, start_info)
        ),
        "sound_update_truth_preservation_failures": len(sound_failures),
        "fake_update_truth_preservation_failures": len(fake_failures),
        "learnable_gap": (
            case.case_id == "learnable_ambiguity"
            and case.start not in switching
            and start_info in adaptive
            and start_info not in frozen
        ),
        "unlearnable_gap": (
            case.case_id == "unlearnable_ambiguity"
            and case.start not in switching
            and start_info not in adaptive
            and all(singleton_start_membership.values())
        ),
        "fake_update_failure": (
            case.case_id == "fake_update_phantom_corridor"
            and ("p1", frozenset({"m0"})) in fake_kernel
            and fake_bad_successor
            and any(
                failure["true_model"] == "m1"
                and failure["observed_successor"] == "p1"
                and failure["updated_models"] == ["m0"]
                for failure in fake_failures
            )
        ),
        "fake_kernel": _format_info_states(fake_kernel),
    }
    return diag


def _greatest_kernel(
    universe: set[T],
    actions: tuple[Action, ...],
    constraint: Callable[[T], bool],
    action_successors: Callable[[T, Action], frozenset[T] | None],
) -> frozenset[T]:
    current = {item for item in universe if constraint(item)}
    changed = True
    while changed:
        changed = False
        next_current: set[T] = set()
        for item in current:
            for action in actions:
                successors_for_action = action_successors(item, action)
                if successors_for_action and all(successor in current for successor in successors_for_action):
                    next_current.add(item)
                    break
        if next_current != current:
            current = next_current
            changed = True
    return frozenset(current)


def _enabled_in_all(
    case: AdaptiveCorridorCase, model_ids: frozenset[ModelId], x: State, a: Action
) -> bool:
    return bool(model_ids) and all(successors(case, model_id, x, a) for model_id in model_ids)


def _model_by_id(case: AdaptiveCorridorCase, model_id: ModelId) -> FixedWorldModel:
    for model in case.models:
        if model.model_id == model_id:
            return model
    raise KeyError(f"unknown model id: {model_id}")


def _nonempty_subsets(items: frozenset[str]) -> tuple[frozenset[str], ...]:
    ordered = tuple(sorted(items))
    subsets: list[frozenset[str]] = []
    for size in range(1, len(ordered) + 1):
        for combo in combinations(ordered, size):
            subsets.append(frozenset(combo))
    return tuple(subsets)


def _format_info_states(states: frozenset[InfoState]) -> list[str]:
    return sorted(f"{x}|{{{','.join(sorted(models))}}}" for x, models in states)


def _all_bad_edges(states: tuple[State, ...], actions: tuple[Action, ...]) -> list[Edge]:
    return [(state, action, "bad") for state in states for action in actions]


def _learnable_ambiguity_case() -> AdaptiveCorridorCase:
    states = ("s", "p0", "p1", "bad")
    actions = ("probe", "stay0", "stay1")
    return AdaptiveCorridorCase(
        case_id="learnable_ambiguity",
        states=states,
        actions=actions,
        models=(
            FixedWorldModel(
                "m0",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "probe"): "p0",
                            ("p0", "stay0"): "p0",
                        },
                    )
                ),
            ),
            FixedWorldModel(
                "m1",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "probe"): "p1",
                            ("p1", "stay1"): "p1",
                        },
                    )
                ),
            ),
        ),
        safe_states=frozenset({"s", "p0", "p1"}),
        requirement_states=frozenset({"s", "p0", "p1"}),
        start="s",
        description=(
            "A safe probe reveals the fixed model; switching ambiguity rejects "
            "the start, but the lifted adaptive kernel admits it."
        ),
    )


def _unlearnable_ambiguity_case() -> AdaptiveCorridorCase:
    states = ("s", "p0", "bad")
    actions = ("probe", "stay0", "stay1")
    return AdaptiveCorridorCase(
        case_id="unlearnable_ambiguity",
        states=states,
        actions=actions,
        models=(
            FixedWorldModel(
                "m0",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "stay0"): "s",
                            ("s", "probe"): "p0",
                            ("p0", "stay0"): "p0",
                        },
                    )
                ),
            ),
            FixedWorldModel(
                "m1",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "stay1"): "s",
                        },
                    )
                ),
            ),
        ),
        safe_states=frozenset({"s", "p0"}),
        requirement_states=frozenset({"s", "p0"}),
        start="s",
        description=(
            "Each singleton model has a safe sustaining action, but no shared "
            "safe action or safe probe exists before identification."
        ),
    )


def _fake_update_case() -> AdaptiveCorridorCase:
    states = ("s", "p0", "p1", "bad")
    actions = ("probe", "stay0", "stay1")
    return AdaptiveCorridorCase(
        case_id="fake_update_phantom_corridor",
        states=states,
        actions=actions,
        models=(
            FixedWorldModel(
                "m0",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "probe"): "p0",
                            ("p0", "stay0"): "p0",
                            ("p1", "stay0"): "p1",
                        },
                    )
                ),
            ),
            FixedWorldModel(
                "m1",
                tuple(
                    _override_edges(
                        _all_bad_edges(states, actions),
                        {
                            ("s", "probe"): "p1",
                            ("p1", "stay1"): "p1",
                        },
                    )
                ),
            ),
        ),
        safe_states=frozenset({"s", "p0", "p1"}),
        requirement_states=frozenset({"s", "p0", "p1"}),
        start="s",
        description=(
            "A fabricating update maps the m1-only observation p1 to m0, "
            "creating a fake corridor state whose m0 policy fails in true m1."
        ),
    )


def _override_edges(base_edges: list[Edge], overrides: dict[tuple[State, Action], State]) -> list[Edge]:
    return [
        (source, action, overrides.get((source, action), target))
        for source, action, target in base_edges
    ]
