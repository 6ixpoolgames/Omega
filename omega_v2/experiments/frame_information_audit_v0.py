"""Remember, erase, and explicitly retrieve a bit under one local interface."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from omega_v2.experiments.operational_continuation_comparison_v0 import _world
from omega_v2.finite.continuation_prediction import Interface, Prediction, Trace
from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.information_frames import audit_information_step, conditional_expectations
from omega_v2.finite.model import FiniteDistribution
from omega_v2.finite.operational_continuation import Experiment

F = Fraction
BLANK = -1
MEMORIES = (BLANK, 0, 1)
PROTOCOL = "docs/research_notes/omega_v2/frame_information_audit_protocol_v0.md"
WEIGHTS = FiniteDistribution((("0", F(1, 2)), ("1", F(1, 2))))


@dataclass(frozen=True)
class MemoryCase:
    experiment: Experiment
    interface: Interface


def memory_update(memory, observation):
    if observation[0] == "erase":
        return BLANK
    if observation[0] in ("show", "read") and observation[1] in (0, 1):
        return observation[1]
    return memory


def operation_cost(state, action, _target):
    if state[0] == "done":
        return 0
    return 2 if state[0] == "access" and action == ("retrieve",) else 1


def memory_case(mode: str, *, horizon=5, budget=6) -> MemoryCase:
    """Reset is mandatory in the installed apparatus, not an optional policy.

    State = (phase, private grading target, archive content, readout, guess).
    The archive may exist while its observation channel remains unavailable.
    """
    if mode not in ("remember", "erased", "sealed", "retrieve"):
        raise ValueError(mode)
    keep_memory = mode == "remember"
    has_archive, readable = mode in ("sealed", "retrieve"), mode == "retrieve"

    def step(state, action):
        phase, target, archive, _readout, _guess = state
        if phase == "show":
            successor = ("maintain", target, archive, BLANK, BLANK)
        elif phase == "maintain":
            successor = ("access", target, archive, BLANK, BLANK)
        elif phase == "access":
            successor = ("read", target, archive, archive if readable else BLANK, BLANK) if action == ("retrieve",) else (
                "guess", target, archive, BLANK, BLANK
            )
        elif phase == "read":
            successor = ("guess", target, archive, BLANK, BLANK)
        elif phase == "guess":
            successor = ("done", target, archive, BLANK,
                         int(action[0]) if action[0] in ("0", "1") else BLANK)
        else:
            successor = state
        return {successor: F(1)}

    starts = [("show", bit, bit if has_archive else BLANK, BLANK, BLANK) for bit in (0, 1)]
    actions = tuple((a,) for a in ("advance", "skip", "retrieve", "0", "1"))
    system, costs = _world(f"memory-{mode}", starts, actions, step, operation_cost)

    def observe(state):
        phase, target, _archive, readout, _guess = state
        if phase == "show":
            return "show", target
        if phase == "maintain":
            return ("keep" if keep_memory else "erase",)
        if phase == "read":
            return "read", readout
        return (phase,)

    observation = {s: observe(s) for s in system.states}
    keys = tuple(dict.fromkeys(observation.values()))
    teams = []
    for route in ("skip", "retrieve"):
        for guesses in product((0, 1), repeat=3):
            table = dict(zip(MEMORIES, guesses, strict=True))
            controller = FiniteStateController(
                f"{route}:{''.join(str(x) for x in guesses)}", MEMORIES, BLANK,
                tuple(observation.items()),
                tuple((m, o, memory_update(m, o)) for m in MEMORIES for o in keys),
                tuple((m, o, route if o == ("access",) else str(table[m]) if o == ("guess",) else "advance")
                      for m in MEMORIES for o in keys),
            )
            teams.append((controller,))
    e = Experiment(
        f"{mode}_h{horizon}_b{budget}", system,
        {str(bit): FiniteDistribution.point_mass(start) for bit, start in enumerate(starts)},
        tuple(teams), frozenset(s for s in system.states if s[0] == "done"), costs, horizon, budget,
    )
    return MemoryCase(e, Interface((observation,), {s: (s[0], s[4]) for s in system.states}))


def control_panel() -> dict[str, MemoryCase]:
    return {"remember": memory_case("remember"), "erased": memory_case("erased"),
            "sealed": memory_case("sealed"), "retrieve": memory_case("retrieve"),
            "short_deadline": memory_case("retrieve", horizon=4),
            "low_budget": memory_case("retrieve", budget=5),
            "zero_budget": memory_case("retrieve", budget=0)}


def correct_guess(q: str, trace: Trace) -> bool:
    return not trace.censored and trace.atoms[-1] == ("done", int(q))


def mixture(prediction: Prediction, policy: str) -> FiniteDistribution:
    """One installed policy and one prior, including both hidden inputs."""
    responses = prediction.laws[policy]
    return FiniteDistribution(tuple(((q, trace), weight * p)
                                   for q, weight in WEIGHTS.rows for trace, p in responses[q].rows))


def accessible_at(outcome, step):
    _q, trace = outcome
    return trace.observations[0][step], trace.memories[0][step]


def history_at(outcome, step):
    _q, trace = outcome
    return trace.observations[0][:step + 1], trace.actions[:step], trace.memories[0][:step + 1]


def bit_readout(outcome):
    return F(int(outcome[0]))


def frame_diagnostics(prediction: Prediction) -> dict:
    """Use a fixed skip program; do not reselect it after observing the input."""
    law = mixture(prediction, "skip:001")
    before = lambda o: accessible_at(o, 1)
    after = lambda o: accessible_at(o, 2)
    return {
        "history_forward": audit_information_step(law, lambda o: history_at(o, 1),
                                                   lambda o: history_at(o, 2), bit_readout),
        "accessible_forward": audit_information_step(law, before, after, bit_readout),
        "accessible_reverse": audit_information_step(law, after, before, bit_readout),
        "history_after": conditional_expectations(law, lambda o: history_at(o, 2), bit_readout),
        "accessible_after": conditional_expectations(law, after, bit_readout),
    }


def read_diagnostics(prediction: Prediction) -> dict:
    law = mixture(prediction, "retrieve:001")
    return {"before_read": conditional_expectations(law, lambda o: accessible_at(o, 2), bit_readout),
            "after_read": conditional_expectations(law, lambda o: accessible_at(o, 4), bit_readout),
            "read_refinement": audit_information_step(law, lambda o: accessible_at(o, 2),
                                                       lambda o: accessible_at(o, 4), bit_readout)}
