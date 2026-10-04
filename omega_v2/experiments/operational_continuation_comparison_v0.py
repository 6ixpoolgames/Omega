"""Five finite comparison cases and boundary controls; exact arithmetic."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from omega_v2.finite.model import ControlledMarkovSystem, FiniteDistribution, fraction_text
from omega_v2.finite.operational_continuation import (
    Experiment,
    achievement,
    emulate,
    evaluate,
    profile_verdict,
    project,
    reactive_teams,
)

PROTOCOL = "docs/research_notes/omega_v2/operational_continuation_comparison_protocol_v0.md"
TERMINATION_PROTOCOL = "docs/research_notes/omega_v2/operational_continuation_termination_protocol_v0.md"
BASE_REVISION = "506ef363a3f27ec4713617089f4f7f3caf8a7d9c"
F = Fraction
CERTAIN = F(1)


def _world(name, starts, actions, step, charge):
    """Exhaust the reachable state graph under every primitive joint command."""
    states = list(dict.fromkeys(starts))
    rows, costs = [], {}
    for state in states:
        for action in actions:
            law = FiniteDistribution.from_mapping(step(state, action))
            for target, probability in law.rows:
                if target not in states:
                    states.append(target)
                rows.append((state, action, target, probability))
                costs[state, action, target] = charge(state, action, target)
    return ControlledMarkovSystem(name, tuple(states), actions, tuple(rows)), costs


def bit_experiment(transmit: bool, *, horizon=2, budget=2) -> Experiment:
    def step(s, a):
        phase, bit, record, _guess = s
        if phase == 0:
            return {(1, bit, bit if a[0] == "send" else -1, -1): F(1)}
        if phase == 1:
            return {(2, bit, record, int(a[1]) if a[1] != "wait" else -1): F(1)}
        return {s: F(1)}

    system, costs = _world(
        "bit-transmission", [(0, b, -1, -1) for b in (0, 1)],
        tuple(product(("send", "wait"), ("wait", "0", "1"))), step,
        lambda s, a, _t: int(s[0] == 0 and a[0] == "send")
        + int(s[0] == 1 and a[1] != "wait"),
    )
    sender = {s: ("seen", s[1]) if s[0] == 0 else ("idle",) for s in system.states}
    receiver = {
        s: ("act", s[2]) if s[0] == 1 else ("idle",) for s in system.states
    }
    teams = reactive_teams((sender, receiver), (
        {o: (("send" if transmit else "wait"),) if o[0] == "seen" else ("wait",)
         for o in sender.values()},
        {o: ("0", "1") if o[0] == "act" else ("wait",) for o in receiver.values()},
    ))
    return Experiment(
        "revealed-bit" if transmit else "hidden-bit", system,
        {str(b): FiniteDistribution.point_mass((0, b, -1, -1)) for b in (0, 1)},
        teams, frozenset(s for s in system.states if s[0] == 2), costs, horizon, budget,
    )


def choice_experiment(mode: str) -> Experiment:
    if mode not in ("selector", "no_coin", "coin"):
        raise ValueError(mode)

    def step(s, a):
        phase, installed, _output = s
        if phase == 1:
            return {s: F(1)}
        if installed == "coin" or (a[0] == "toss" and installed == "selector"):
            return {(1, installed, b): F(1, 2) for b in (0, 1)}
        result = int(a[0]) if a[0] != "toss" else -1
        return {(1, installed, result): F(1)}

    system, costs = _world(
        "output-apparatus", [(0, m, -1) for m in ("selector", "no_coin", "coin")],
        tuple((a,) for a in ("0", "1", "toss")), step,
        lambda s, _a, _t: int(s[0] == 0),
    )
    observation = {s: "ready" if s[0] == 0 else "end" for s in system.states}
    available = {"selector": ("0", "1", "toss"), "no_coin": ("0", "1"), "coin": ("toss",)}
    teams = reactive_teams((observation,), ({"ready": available[mode], "end": ("0",)},))
    return Experiment(
        mode, system, {"trial": FiniteDistribution.point_mass((0, mode, -1))},
        teams, frozenset(s for s in system.states if s[0] == 1), costs, 1, 1,
    )


def repair_experiment(stock: int) -> Experiment:
    if stock not in (1, 2):
        raise ValueError(stock)

    def step(s, a):
        phase, tokens, _r1, _r2, _conflict = s
        if phase == 1:
            return {s: F(1)}
        needed = sum(a)
        if needed > tokens:
            return {(1, 0, 0, 0, 1): F(1)}  # collision consumes the contested token
        return {(1, tokens - needed, a[0], a[1], 0): F(1)}

    system, costs = _world(
        "shared-repair", [(0, b, 0, 0, 0) for b in (1, 2)],
        tuple(product((0, 1), repeat=2)), step, lambda s, _a, t: s[1] - t[1],
    )
    observation = {s: "ready" if s[0] == 0 else "end" for s in system.states}
    teams = reactive_teams(
        (observation, observation),
        ({"ready": (0, 1), "end": (0,)}, {"ready": (0, 1), "end": (0,)}),
    )
    return Experiment(
        f"repair-{stock}", system,
        {"trial": FiniteDistribution.point_mass((0, stock, 0, 0, 0))},
        teams, frozenset(s for s in system.states if s[0] == 1), costs, 1, 2,
    )


def build_experiment(build: bool, *, horizon=2, budget=2, setup=CERTAIN) -> Experiment:
    if not isinstance(setup, Fraction) or not 0 <= setup <= 1:
        raise ValueError("setup probability must be an exact probability")

    def step(s, a):
        phase, ready, stock, _output = s
        if phase == 0:
            if a[0] == "build":
                return {(1, 1, 1, 0): setup, (1, 0, 1, 0): 1 - setup}
            return {(1, 0, 2, 0): F(1)}
        if phase == 1:
            used = int(a[0] == "use" and stock > 0)
            return {(2, ready, stock - used, ready * used): F(1)}
        return {s: F(1)}

    system, costs = _world(
        "construction", [(0, 0, 2, 0)], tuple((a,) for a in ("build", "wait", "use")),
        step, lambda s, _a, t: s[2] - t[2],
    )
    observation = {s: ("prepare", "operate", "end")[s[0]] for s in system.states}
    teams = reactive_teams((observation,), ({
        "prepare": ("build" if build else "wait",),
        "operate": ("use", "wait"), "end": ("wait",),
    },))
    return Experiment(
        "build" if build else "wait", system,
        {"trial": FiniteDistribution.point_mass((0, 0, 2, 0))},
        teams, frozenset(s for s in system.states if s[0] == 2), costs, horizon, budget,
    )


def history_experiment(alarm: bool) -> Experiment:
    def step(s, a):
        if s == "start":
            return {"alarm" if a[0] == "alarm" else "clear": F(1)}
        return {"done": F(1)}

    system, costs = _world(
        "transient-signal", ["start"], tuple((a,) for a in ("alarm", "clear", "finish")),
        step, lambda s, _a, _t: int(s != "done"),
    )
    observation = {
        s: "choose" if s == "start" else "finish" for s in system.states
    }
    teams = reactive_teams((observation,), ({
        "choose": ("alarm" if alarm else "clear",), "finish": ("finish",),
    },))
    return Experiment(
        "alarm-history" if alarm else "clear-history", system,
        {"trial": FiniteDistribution.point_mass("start")},
        teams, frozenset({"done"}), costs, 2, 2,
    )


def partial_cutoff_experiment(*, horizon=2, budget=2) -> Experiment:
    """A fast terminal branch and a slow branch cut off before its final tick."""
    successors = {
        "start": {"done": F(1, 3), "slow1": F(2, 3)},
        "slow1": {"slow2": F(1)}, "slow2": {"done": F(1)}, "done": {"done": F(1)},
    }
    system, costs = _world(
        "partial-cutoff", ["start"], (("step",),), lambda s, _a: successors[s],
        lambda s, _a, _t: int(s != "done"),
    )
    observation = {s: s for s in system.states}
    teams = reactive_teams((observation,), ({s: ("step",) for s in system.states},))
    return Experiment(
        "partial-cutoff", system, {"trial": FiniteDistribution.point_mass("start")},
        teams, frozenset({"done"}), costs, horizon, budget,
    )


def terminal_stop_experiment() -> Experiment:
    """An expensive terminal self-loop must never be executed after stopping."""
    system, costs = _world(
        "terminal-stop", ["start"], (("step",),), lambda _s, _a: {"done": F(1)},
        lambda s, _a, _t: 1 if s == "start" else 7,
    )
    observation = {s: s for s in system.states}
    teams = reactive_teams((observation,), ({s: ("step",) for s in system.states},))
    return Experiment(
        "terminal-stop", system, {"trial": FiniteDistribution.point_mass("start")},
        teams, frozenset({"done"}), costs, 3, 1,
    )


def _termination_summary(evaluated):
    # Both fixtures declare exactly one team and one input. An inadmissible
    # team must produce failed gates, not an indexing error in the reporter.
    responses = next(iter(evaluated.laws.values()), {})
    law = responses.get("trial")
    rows = () if law is None else law.rows
    return {
        "admitted_policy_count": len(evaluated.laws),
        "total_mass": fraction_text(sum((p for _r, p in rows), F(0))),
        "completed_mass": fraction_text(sum((p for r, p in rows if not r.censored), F(0))),
        "censored_mass": fraction_text(sum((p for r, p in rows if r.censored), F(0))),
        "runs": sorted(
            [[r.path.end, fraction_text(p), r.elapsed, r.cost, r.censored] for r, p in rows]
        ),
    }


def _weights(inputs):
    # Explicitly registered fair preparation, not a prior over controller programs.
    return FiniteDistribution(tuple((q, F(1, len(inputs))) for q in inputs))


def _summary(evaluated, catalogue):
    return {
        "context": evaluated.experiment.name,
        "horizon": evaluated.experiment.horizon,
        "budget": evaluated.experiment.budget,
        "admitted_policy_count": len(evaluated.laws),
        "distinct_response_count": len(set(catalogue.signatures.values())),
        "rejected_over_budget": dict(evaluated.rejected),
        "projected_responses": {
            policy: {
                q: [{"response": repr(value), "probability": fraction_text(mass)}
                    for value, mass in sorted(rows, key=lambda row: repr(row[0]))]
                for q, rows in zip(catalogue.inputs, signature, strict=True)
            }
            for policy, signature in catalogue.signatures.items()
        },
    }


def compare_case(left, right, tasks, readout, frame):
    l, r = evaluate(left), evaluate(right)
    lp, rp = (achievement(e, _weights(left.preparations), tasks) for e in (l, r))
    lc, rc = (project(e, frame=frame, readout=readout) for e in (l, r))
    return {
        "frame": frame,
        "input_weights": {q: fraction_text(p) for q, p in _weights(left.preparations).rows},
        "left": _summary(l, lc), "right": _summary(r, rc),
        "left_profile": None if lp is None else {k: fraction_text(v) for k, v in lp.items()},
        "right_profile": None if rp is None else {k: fraction_text(v) for k, v in rp.items()},
        "achievement_order": "unavailable" if lp is None or rp is None else profile_verdict(lp, rp),
        "left_emulates_right": emulate(lc, rc),
        "right_emulates_left": emulate(rc, lc),
        "_evidence": (l, r),
    }


def run_experiment():
    """Known-case correctness gates; compute all observations before comparing."""
    cases = {
        "bit": compare_case(
            bit_experiment(True), bit_experiment(False),
            {"guess": lambda q, r: r.path.end[3] == int(q)},
            lambda _q, r: r.path.end[3], "bit-output",
        ),
        "choice": compare_case(
            choice_experiment("selector"), choice_experiment("coin"),
            {"zero": lambda _q, r: r.path.end[2] == 0,
             "one": lambda _q, r: r.path.end[2] == 1},
            lambda _q, r: r.path.end[2], "binary-output",
        ),
        "choice_without_coin": compare_case(
            choice_experiment("no_coin"), choice_experiment("coin"),
            {"zero": lambda _q, r: r.path.end[2] == 0,
             "one": lambda _q, r: r.path.end[2] == 1},
            lambda _q, r: r.path.end[2], "binary-output",
        ),
        "repair_marginals": compare_case(
            repair_experiment(2), repair_experiment(1),
            {"first": lambda _q, r: r.path.end[2] == 1,
             "second": lambda _q, r: r.path.end[3] == 1},
            lambda _q, r: r.path.end[2:4], "repair-output",
        ),
        "repair_joint": compare_case(
            repair_experiment(2), repair_experiment(1),
            {"first": lambda _q, r: r.path.end[2] == 1,
             "second": lambda _q, r: r.path.end[3] == 1,
             "both": lambda _q, r: r.path.end[2:4] == (1, 1)},
            lambda _q, r: r.path.end[2:4], "repair-output",
        ),
        "build_service": compare_case(
            build_experiment(True), build_experiment(False),
            {"service": lambda _q, r: r.path.end[3] == 1},
            lambda _q, r: r.path.end[3], "service-output",
        ),
        "build_savings": compare_case(
            build_experiment(True), build_experiment(False),
            {"service": lambda _q, r: r.path.end[3] == 1,
             "zero_expenditure": lambda _q, r: r.cost == 0},
            lambda _q, r: (r.path.end[3], r.cost), "service-and-cost",
        ),
        "history_endpoint": compare_case(
            history_experiment(True), history_experiment(False),
            {"complete": lambda _q, r: r.path.end == "done"},
            lambda _q, r: (r.path.end, r.elapsed, r.cost), "terminal-time-cost",
        ),
        "history_full": compare_case(
            history_experiment(True), history_experiment(False),
            {"alarm_occurred": lambda _q, r: "alarm" in r.path.states,
             "clear_occurred": lambda _q, r: "clear" in r.path.states},
            lambda _q, r: (r.path.states, r.elapsed, r.cost), "signal-history-time-cost",
        ),
    }
    hidden = evaluate(bit_experiment(False))
    branchwise = sum((
        F(1, 2) * max(
            sum((p for run, p in laws[q].rows if run.path.end[3] == int(q)), F(0))
            for laws in hidden.laws.values()
        ) for q in ("0", "1")
    ), F(0))
    build_bounds, controls = [], {}
    for horizon, budget in product((1, 2), (0, 1, 2)):
        evaluated = evaluate(build_experiment(True, horizon=horizon, budget=budget))
        controls[f"build_h{horizon}_b{budget}"] = evaluated
        profile = achievement(
            evaluated, _weights(("trial",)), {"service": lambda _q, r: r.path.end[3] == 1}
        )
        build_bounds.append({
            "horizon": horizon, "budget": budget,
            "service": None if profile is None else fraction_text(profile["service"]),
            "admitted_policies": len(evaluated.laws),
            "censored_mass_per_policy": {
                policy: fraction_text(sum((p for run, p in laws["trial"].rows if run.censored), F(0)))
                for policy, laws in evaluated.laws.items()
            },
        })
    controls["failed_setup"] = evaluate(build_experiment(True, setup=F(1, 2)))
    failed_setup = achievement(
        controls["failed_setup"], _weights(("trial",)),
        {"service": lambda _q, r: r.path.end[3] == 1},
    )["service"]
    termination_controls = {}
    for name, experiment in (
        ("partial_cutoff", partial_cutoff_experiment()),
        ("terminal_stop", terminal_stop_experiment()),
    ):
        controls[name] = evaluate(experiment)
        termination_controls[name] = _termination_summary(controls[name])
    passive = [
        profile_verdict({"E": F(p, 20), "not_E": 1 - F(p, 20)},
                        {"E": F(q, 20), "not_E": 1 - F(q, 20)})
        for p, q in product(range(21), repeat=2)
    ]
    expected_orders = {
        "bit": "left_strict", "choice": "left_strict", "choice_without_coin": "left_strict",
        "repair_marginals": "equivalent", "repair_joint": "left_strict",
        "build_service": "left_strict", "build_savings": "incomparable",
        "history_endpoint": "equivalent", "history_full": "incomparable",
    }
    gates = []

    def gate(name, observed, expected):
        gates.append({"name": name, "observed": observed, "expected": expected,
                      "passed": observed == expected})

    for name, expected in expected_orders.items():
        gate(f"{name}.achievement", cases[name]["achievement_order"], expected)
    expected_emulations = {
        "bit": ("holds", "fails"), "choice": ("holds", "fails"),
        "choice_without_coin": ("fails", "fails"),
        "repair_marginals": ("holds", "fails"), "repair_joint": ("holds", "fails"),
        "build_service": ("holds", "fails"), "build_savings": ("fails", "fails"),
        "history_endpoint": ("holds", "holds"), "history_full": ("fails", "fails"),
    }
    for name, expected in expected_emulations.items():
        for direction, status in zip(("left_emulates_right", "right_emulates_left"), expected):
            gate(f"{name}.{direction}", cases[name][direction]["status"], status)
    gate("hidden_guess", cases["bit"]["right_profile"]["guess"], "1/2")
    gate("revealed_guess", cases["bit"]["left_profile"]["guess"], "1")
    gate("invalid_branchwise_optimization", fraction_text(branchwise), "1")
    gate("failed_setup_keeps_failure", fraction_text(failed_setup), "1/2")
    gate("passive_equal_pairs", passive.count("equivalent"), 21)
    gate("passive_incomparable_pairs", passive.count("incomparable"), 420)
    gate("build_horizon_budget_profile", [r["service"] for r in build_bounds],
         [None, "0", "0", None, "0", "1"])
    partial = termination_controls["partial_cutoff"]
    gate("partial_cutoff.total_mass", partial["total_mass"], "1")
    gate("partial_cutoff.completed_mass", partial["completed_mass"], "1/3")
    gate("partial_cutoff.censored_mass", partial["censored_mass"], "2/3")
    gate("partial_cutoff.runs", partial["runs"],
         [["done", "1/3", 1, 1, False], ["slow2", "2/3", 2, 2, True]])
    terminal = termination_controls["terminal_stop"]
    gate("terminal_stop.runs", terminal["runs"], [["done", "1", 1, 1, False]])
    gate("terminal_stop.admissible", terminal["admitted_policy_count"], 1)
    return {
        "status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
        "protocol": PROTOCOL, "base_revision": BASE_REVISION,
        "supplemental_protocols": [TERMINATION_PROTOCOL],
        "claim_boundary": "Known finite acceptance cases; no value or lushness validation.",
        "cases": cases, "gates": gates, "build_bounds": build_bounds,
        "unsound_branchwise_guess": fraction_text(branchwise),
        "probabilistic_setup_success": fraction_text(failed_setup),
        "termination_controls": termination_controls,
        "_control_evidence": controls,
        "passive_counts": {v: passive.count(v) for v in (
            "equivalent", "left_strict", "right_strict", "incomparable"
        )},
    }
