"""Public known-answer controls for C1 and conventional bounded prediction."""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction

from omega_v2.experiments.operational_continuation_comparison_v0 import (
    _world,
    bit_experiment,
    build_experiment,
    history_experiment,
    partial_cutoff_experiment,
    repair_experiment,
    terminal_stop_experiment,
)
from omega_v2.finite.continuation_prediction import Interface, best_probability, compatible_range
from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import ControlledMarkovSystem, FiniteDistribution
from omega_v2.finite.operational_continuation import Experiment, reactive_teams

F = Fraction
PROTOCOL = "docs/research_notes/omega_v2/continuation_equivalence_audit_protocol_v0.md"


@dataclass(frozen=True)
class Case:
    experiment: Experiment
    interface: Interface


def case(e, atom) -> Case:
    return Case(e, Interface(tuple(c.observation_map for c in e.teams[0]),
                             {s: atom(s) for s in e.system.states}))


def response_case(mode: str) -> Case:
    if mode not in ("live", "replay", "lookup"):
        raise ValueError(mode)

    def step(s, action):
        if s[0] == "done":
            return {s: F(1)}
        command = action[0]
        output = 0 if mode == "replay" or (mode == "lookup" and command == 2) else command
        return {("done", output): F(1)}

    system, costs = _world(mode, [("ready", -1)], tuple((i,) for i in range(3)), step,
                           lambda s, _a, _t: int(s[0] == "ready"))
    observations = {s: s[0] for s in system.states}
    teams = reactive_teams((observations,), ({"ready": (0, 1, 2), "done": (0,)},))
    e = Experiment(mode, system, {"trial": FiniteDistribution.point_mass(("ready", -1))},
                   teams, frozenset(s for s in system.states if s[0] == "done"), costs, 1, 1)
    return case(e, lambda s: s[1] if s[0] == "done" else "ready")


def nuisance_extension(original: Case) -> Case:
    """Independent unobserved fair bit, refreshed every tick, with no cost."""
    e, interface = original.experiment, original.interface
    system = ControlledMarkovSystem(
        f"{e.system.system_id}-nuisance",
        tuple((s, bit) for s in e.system.states for bit in (0, 1)), e.system.actions,
        tuple(((s, bit), a, (t, next_bit), p / 2)
              for s, a, t, p in e.system.transitions for bit in (0, 1) for next_bit in (0, 1)),
    )
    observations = tuple({(s, bit): obs[s] for s, bit in system.states} for obs in interface.observations)
    teams = tuple(tuple(replace(c, observation_rows=tuple(observations[i].items()))
                        for i, c in enumerate(team)) for team in e.teams)
    extended = replace(
        e, name=f"{e.name}-nuisance", system=system, teams=teams,
        preparations={q: FiniteDistribution(tuple(((s, bit), p / 2)
                      for s, p in law.rows for bit in (0, 1))) for q, law in e.preparations.items()},
        terminals=frozenset((s, bit) for s in e.terminals for bit in (0, 1)),
        costs={((s, bit), a, (t, next_bit)): cost for (s, a, t), cost in e.costs.items()
               for bit in (0, 1) for next_bit in (0, 1)},
    )
    return Case(extended, Interface(observations, {(s, bit): interface.atoms[s] for s, bit in system.states}))


def seed_case(active: bool, *, horizon=2, budget=2) -> Case:
    def step(s, a):
        phase, ready, _out = s
        if phase == 0:
            return {(1, int(active and a[0] == "build"), 0): F(1)}
        if phase == 1:
            return {(2, ready, int(ready and a[0] == "use")): F(1)}
        return {s: F(1)}

    system, costs = _world("seed" if active else "inert", [(0, 0, 0)],
                           tuple((a,) for a in ("build", "use", "wait")), step,
                           lambda s, a, _t: int(s[0] != 2 and a[0] != "wait"))
    obs = {s: s[0] for s in system.states}
    teams = reactive_teams((obs,), ({0: ("build", "wait"), 1: ("use", "wait"), 2: ("wait",)},))
    e = Experiment(system.system_id, system, {"trial": FiniteDistribution.point_mass((0, 0, 0))},
                   teams, frozenset(s for s in system.states if s[0] == 2), costs, horizon, budget)
    return case(e, lambda s: s[2])


def memory_case() -> Case:
    def step(s, a):
        phase, bit, _guess = s
        if phase == 0:
            return {(1, bit, -1): F(1)}
        if phase == 1:
            return {(2, bit, a[0]): F(1)}
        return {s: F(1)}

    system, costs = _world("remember-bit", [(0, b, -1) for b in (0, 1)],
                           ((0,), (1,)), step, lambda s, _a, _t: int(s[0] != 2))
    obs = {s: ("seen", s[1]) if s[0] == 0 else ("act",) for s in system.states}
    observations = tuple(dict.fromkeys(obs.values()))
    controller = FiniteStateController(
        "remember", (0, 1), 0, tuple(obs.items()),
        tuple((m, o, o[1] if o[0] == "seen" else m) for m in (0, 1) for o in observations),
        tuple((m, o, m if o[0] == "act" else 0) for m in (0, 1) for o in observations),
    )
    e = Experiment("remember-bit", system,
                   {str(b): FiniteDistribution.point_mass((0, b, -1)) for b in (0, 1)},
                   ((controller,),), frozenset(s for s in system.states if s[0] == 2), costs, 2, 2)
    return case(e, lambda s: s[2])


def cost_distinction_case() -> Case:
    system, costs = _world("edge-cost-distinction", ["cheap", "dear"], (("step",),),
                           lambda _s, _a: {"done": F(1)},
                           lambda s, _a, _t: {"cheap": 1, "dear": 2, "done": 9}[s])
    obs = {s: "end" if s == "done" else "ready" for s in system.states}
    teams = reactive_teams((obs,), ({o: ("step",) for o in obs.values()},))
    e = Experiment("cost-distinction", system,
                   {s: FiniteDistribution.point_mass(s) for s in ("cheap", "dear")},
                   teams, frozenset({"done"}), costs, 1, 2)
    return case(e, lambda s: "end" if s == "done" else "ready")


def control_panel() -> dict[str, Case]:
    live = response_case("live")
    panel = {"live": live, "replay": response_case("replay"), "lookup": response_case("lookup"),
             "equivalent_mimic": nuisance_extension(live), "memory": memory_case()}
    for active in (True, False):
        for h, b in ((1, 2), (2, 1), (2, 2)):
            panel[f"{'seed' if active else 'inert'}_h{h}_b{b}"] = seed_case(active, horizon=h, budget=b)
    for transmit in (False, True):
        panel["revealed_bit" if transmit else "hidden_bit"] = case(bit_experiment(transmit), lambda s: s[3])
    for stock in (1, 2):
        panel[f"repair_{stock}"] = case(repair_experiment(stock), lambda s: s[2:4])
    panel["failed_setup"] = case(build_experiment(True, setup=F(1, 2)), lambda s: s[3])
    for alarm in (False, True):
        panel["alarm_history" if alarm else "clear_history"] = case(history_experiment(alarm), lambda s: s)
    panel["partial_cutoff"] = case(partial_cutoff_experiment(), lambda s: s)
    panel["terminal_stop"] = case(terminal_stop_experiment(), lambda s: s)
    panel["zero_horizon"] = replace(live, experiment=replace(live.experiment, horizon=0))
    panel["empty_admissible"] = replace(live, experiment=replace(live.experiment, budget=0))
    panel["zero_horizon_terminal"] = replace(live, experiment=replace(
        live.experiment, horizon=0, preparations={"trial": FiniteDistribution.point_mass(("done", 0))}
    ))
    panel["cost_distinction"] = cost_distinction_case()
    panel["nuisance_partial_cutoff"] = nuisance_extension(panel["partial_cutoff"])
    return panel


def identification_control() -> dict:
    models = {
        "always": {"baseline": F(1), "knockout_a": F(1), "knockout_b": F(1), "double": F(1)},
        "redundant": {"baseline": F(1), "knockout_a": F(1), "knockout_b": F(1), "double": F(0)},
    }
    evidence = {q: F(1) for q in ("baseline", "knockout_a", "knockout_b")}
    return {"models": models, "evidence": evidence,
            "limited": compatible_range(models, evidence, "double"),
            "expanded": compatible_range(models, {**evidence, "double": F(0)}, "double"),
            "inconsistent": compatible_range(models, {"baseline": F(0)}, "double")}


def known_answer_gates(predictions) -> tuple[list[dict], dict]:
    gates, witnesses = [], {}

    def gate(name, observed, expected):
        gates.append({"name": name, "observed": observed, "expected": expected, "passed": observed == expected})

    def score(name, task):
        inputs = next(iter(predictions[name].laws.values()), {"trial": None})
        weights = FiniteDistribution(tuple((q, F(1, len(inputs))) for q in inputs))
        result, witness = best_probability(predictions[name], weights, task)
        witnesses[name] = {"probability": result, "policy": witness}
        if result is None:
            valid = witness is None and not predictions[name].laws
        else:
            valid = witness in predictions[name].laws and result == sum((
                w * p for q, w in weights.rows for t, p in predictions[name].laws[witness][q].rows
                if task(q, t)
            ), F(0))
        gate(f"{name}.witness", valid, True)
        return result

    def command_law(name, command):
        # Controller ordering comes from the registered 0,1,2 menu.
        return predictions[name].laws[f"c0-{command}"]["trial"].pushforward(lambda t: t.atoms[-1]).mass_map

    gate("replay.passive_match", command_law("live", 0), command_law("replay", 0))
    gate("replay.intervention_separates", command_law("live", 1) != command_law("replay", 1), True)
    gate("lookup.development_match", all(command_law("live", i) == command_law("lookup", i) for i in (0, 1)), True)
    gate("lookup.public_probe_separates", command_law("live", 2) != command_law("lookup", 2), True)
    gate("equivalent_mimic.all_commands", all(command_law("live", i) == command_law("equivalent_mimic", i)
                                            for i in range(3)), True)
    for active in (True, False):
        for h, b in ((1, 2), (2, 1), (2, 2)):
            name = f"{'seed' if active else 'inert'}_h{h}_b{b}"
            gate(name, score(name, lambda _q, t: t.atoms[-1] == 1), F(int(active and h == 2 and b == 2)))
    for name, expected in (("hidden_bit", F(1, 2)), ("revealed_bit", F(1)), ("memory", F(1))):
        gate(name, score(name, lambda q, t: t.atoms[-1] == int(q)), expected)
    for stock in (1, 2):
        name = f"repair_{stock}"
        gate(name, score(name, lambda _q, t: t.atoms[-1] == (1, 1)), F(stock - 1))
    gate("failed_setup", score("failed_setup", lambda _q, t: t.atoms[-1] == 1), F(1, 2))
    gate("partial_cutoff", score("partial_cutoff", lambda _q, t: not t.censored), F(1, 3))
    gate("terminal_stop", score("terminal_stop", lambda _q, t: t.cost == 1 and t.elapsed == 1), F(1))
    gate("zero_horizon", score("zero_horizon", lambda _q, t: t.censored and t.cost == t.elapsed == 0), F(1))
    gate("zero_horizon_terminal", score("zero_horizon_terminal", lambda _q, t: not t.censored and t.cost == 0), F(1))
    gate("empty_admissible", score("empty_admissible", lambda _q, _t: True), None)
    for name, expected in (("alarm_history", F(1)), ("clear_history", F(0))):
        gate(name, score(name, lambda _q, t: "alarm" in t.atoms), expected)
    identification = identification_control()
    limited = identification["limited"]
    gate("identifiability.range", (limited["status"], limited["lower"], limited["upper"]), ("unknown", F(0), F(1)))
    gate("identifiability.expanded", identification["expanded"]["models"], ("redundant",))
    gate("identifiability.inconsistent", identification["inconsistent"]["status"], "inconsistent")
    return gates, {"controller_witnesses": witnesses, "identification": identification}
