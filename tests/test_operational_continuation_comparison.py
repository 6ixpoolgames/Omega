import inspect
import json
from dataclasses import replace
from fractions import Fraction
from itertools import product

import pytest

from omega_v2.experiments.operational_continuation_comparison_v0 import (
    bit_experiment,
    build_experiment,
    choice_experiment,
    history_experiment,
    partial_cutoff_experiment,
    repair_experiment,
    run_experiment,
    terminal_stop_experiment,
)
from omega_v2.finite import operational_continuation as core
from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import ControlledMarkovSystem, FiniteDistribution
from omega_v2.finite.operational_continuation import (
    achievement,
    emulate,
    evaluate,
    project,
    rollout,
)
from omega_v2.validation import operational_continuation_comparison_v0 as runner

F = Fraction


def binary(e):
    return project(evaluate(e), frame="binary", readout=lambda _q, r: r.path.end[2])


def test_all_registered_cases_and_bounds():
    result = run_experiment()
    assert result["status"] == "PASS", [g for g in result["gates"] if not g["passed"]]
    assert result["passive_counts"] == {
        "equivalent": 21, "incomparable": 420, "left_strict": 0, "right_strict": 0
    }


def test_hidden_input_cannot_select_a_different_controller():
    hidden, revealed = map(evaluate, (bit_experiment(False), bit_experiment(True)))
    h, r = (
        project(e, frame="bit", readout=lambda _q, run: run.path.end[3])
        for e in (hidden, revealed)
    )
    for signature in h.signatures.values():
        assert signature[0] == signature[1]
    result = emulate(h, r)
    assert result["status"] == "fails"
    assert result["failures"]
    # Each rejected source has a real input that breaks its proposed emulation.
    for target, sources in result["failures"].items():
        for source, input_id in sources.items():
            i = h.inputs.index(input_id)
            assert h.signatures[source][i] != r.signatures[target][i]


def test_transmission_does_not_act_before_arrival_and_costs_a_token():
    experiment = bit_experiment(True, horizon=1)
    for team in experiment.teams:
        for q in experiment.preparations:
            law = rollout(experiment, team, q)
            for run in law.support:
                assert run.path.end[3] == -1
                assert run.censored and run.cost == 1 and run.elapsed == 1
                assert run.observations[1] == (("idle",),)


def test_private_memory_is_used_when_observation_disappears():
    e = bit_experiment(False)
    sender, _receiver = e.teams[0]
    observations = tuple(
        (s, ("seen", s[1]) if s[0] == 0 else ("act",))
        for s in e.system.states
    )
    keys = tuple(dict.fromkeys(o for _s, o in observations))
    remembering = FiniteStateController(
        "remembering", (0, 1), 0, observations,
        tuple((m, o, o[1] if o[0] == "seen" else m) for m, o in product((0, 1), keys)),
        tuple((m, o, "wait" if o[0] == "seen" else str(m))
              for m, o in product((0, 1), keys)),
    )
    e = replace(e, teams=((sender, remembering),))
    for q in ("0", "1"):
        run = rollout(e, e.teams[0], q).support[0]
        assert run.path.end[3] == int(q)
        assert run.memories[1] == (0, int(q), int(q))


def test_no_free_policy_randomization():
    selector, coin, without = map(binary, (
        choice_experiment("selector"), choice_experiment("coin"), choice_experiment("no_coin")
    ))
    assert emulate(selector, coin)["status"] == "holds"
    assert emulate(without, coin)["status"] == "fails"


def test_emulation_preorder_and_retained_witnesses():
    selector, coin, no_coin = (
        choice_experiment("selector"), choice_experiment("coin"), choice_experiment("no_coin")
    )
    zero = replace(no_coin, teams=(no_coin.teams[0],))
    catalogues = tuple(map(binary, (selector, coin, no_coin, zero)))
    for a, b, c in product(catalogues, repeat=3):
        assert emulate(a, a)["status"] == "holds"
        ab, bc = emulate(a, b), emulate(b, c)
        if ab["status"] == bc["status"] == "holds":
            assert emulate(a, c)["status"] == "holds"
        for target, source in ab["witnesses"].items():
            assert a.signatures[source] == b.signatures[target]


def test_resource_collision_is_kept_as_a_failed_run():
    e = repair_experiment(1)
    runs = [run for team in e.teams for run in rollout(e, team, "trial").support]
    assert {r.path.end[2:4] for r in runs} == {(0, 0), (0, 1), (1, 0)}
    collision = next(r for r in runs if r.path.end[4])
    assert collision.cost == 1 and collision.path.end[1] == 0
    assert not collision.censored


def test_failure_mass_not_conditioned_away_and_budget_not_averaged():
    e = build_experiment(True, setup=F(1, 2))
    evaluated = evaluate(e)
    using = next(
        laws["trial"] for laws in evaluated.laws.values()
        if any(r.path.end[3] == 1 for r in laws["trial"].support)
    )
    assert sum(p for _r, p in using.rows) == 1
    assert sum(p for r, p in using.rows if r.path.end[3] == 1) == F(1, 2)
    # One expensive failure makes the whole policy inadmissible, even if its
    # expected cost would fit. Never retain and renormalize the cheap branch.
    costs = dict(e.costs)
    for (s, a, t) in costs:
        if s[0] == 1 and a == ("use",) and s[1] == 0:
            costs[s, a, t] = 3
    costly_failure = evaluate(replace(e, costs=costs, budget=3))
    assert costly_failure.rejected and len(costly_failure.laws) == 1
    assert set(costly_failure.rejected.values()) == {4}


def test_unavailable_catalogue_is_not_zero_or_vacuous_dominance():
    e = evaluate(build_experiment(True, budget=0))
    assert not e.laws
    assert achievement(e, FiniteDistribution.point_mass("trial"), {"any": lambda _q, _r: True}) is None
    c = project(e, frame="empty", readout=lambda _q, _r: 0)
    assert emulate(c, c)["status"] == "unavailable"


def test_terminal_projection_does_not_preserve_history():
    a, b = map(evaluate, (history_experiment(True), history_experiment(False)))
    terminal = lambda _q, r: (r.path.end, r.cost, r.elapsed)
    history = lambda _q, r: r.path.states
    assert emulate(
        project(a, frame="terminal", readout=terminal),
        project(b, frame="terminal", readout=terminal),
    )["status"] == "holds"
    assert emulate(
        project(a, frame="history", readout=history),
        project(b, frame="history", readout=history),
    )["status"] == "fails"


def test_mixed_completion_and_cutoff_keep_unconditional_mass_and_histories():
    e = partial_cutoff_experiment()
    law = rollout(e, e.teams[0], "trial")
    assert len(law.rows) == 2
    by_end = {run.path.end: (run, mass) for run, mass in law.rows}
    fast, fast_mass = by_end["done"]
    slow, slow_mass = by_end["slow2"]
    assert (fast_mass, slow_mass) == (F(1, 3), F(2, 3))
    assert fast.path.states == ("start", "done")
    assert (fast.elapsed, fast.cost, fast.censored) == (1, 1, False)
    assert fast.observations == (("start",),)
    assert fast.memories == ((0, 0),)
    assert slow.path.states == ("start", "slow1", "slow2")
    assert (slow.elapsed, slow.cost, slow.censored) == (2, 2, True)
    assert slow.observations == (("start", "slow1"),)
    assert slow.memories == ((0, 0, 0),)
    assert achievement(evaluate(e), FiniteDistribution.point_mass("trial"), {
        "completed": lambda _q, r: not r.censored,
        "unfinished": lambda _q, r: r.censored,
    }) == {"completed": F(1, 3), "unfinished": F(2, 3)}

    # The unfinished branch is a delayed completion, not an absorbing failure.
    longer = partial_cutoff_experiment(horizon=3, budget=3)
    completed = rollout(longer, longer.teams[0], "trial")
    assert all(r.path.end == "done" and not r.censored for r in completed.support)
    assert {(r.elapsed, r.cost): p for r, p in completed.rows} == {
        (1, 1): F(1, 3), (3, 3): F(2, 3)
    }


def test_terminal_stop_prevents_later_actions_memory_updates_and_charges():
    e = terminal_stop_experiment()
    assert e.costs["done", ("step",), "done"] == 7
    law = rollout(e, e.teams[0], "trial")
    assert len(law.rows) == 1
    run, mass = law.rows[0]
    assert mass == 1
    assert run.path.states == ("start", "done")
    assert run.path.actions == (("step",),)
    assert (run.elapsed, run.cost, run.censored) == (1, 1, False)
    assert run.observations == (("start",),)
    assert run.memories == ((0, 0),)
    evaluated = evaluate(e)
    assert len(evaluated.laws) == 1 and not evaluated.rejected


@pytest.mark.parametrize("mutation,failed_gate", [
    ("condition_on_completion", "partial_cutoff.completed_mass"),
    ("continue_after_terminal", "terminal_stop.admissible"),
])
def test_termination_controls_reject_targeted_mutants(tmp_path, monkeypatch, mutation, failed_gate):
    source = inspect.getsource(core.rollout)
    if mutation == "condition_on_completion":
        original = "    return FiniteDistribution.from_mapping(paths)"
        replacement = """    finished = {run: p for run, p in paths.items() if not run.censored}
    if finished:
        total = sum(finished.values(), Fraction(0))
        paths = {run: p / total for run, p in finished.items()}
    return FiniteDistribution.from_mapping(paths)"""
    else:
        original = """            if state in experiment.terminals:
                extended[run] = extended.get(run, Fraction(0)) + mass
                continue
"""
        replacement = ""
    assert source.count(original) == 1, "mutation must replace exactly one intended code block"
    namespace = dict(core.__dict__)
    mutated = compile(source.replace(original, replacement), f"<mutation:{mutation}>", "exec")
    exec(mutated, namespace)  # noqa: S102 - isolated mutation of trusted local test target
    monkeypatch.setattr(core, "rollout", namespace["rollout"])

    out_dir = tmp_path / mutation
    assert runner.main(["--out-dir", str(out_dir)]) == 1
    summary = json.loads((out_dir / "summary.json").read_text())
    assert summary["status"] == "FAIL"
    supplemental = ("partial_cutoff.", "terminal_stop.")
    original_gates = [g for g in summary["gates"] if not g["name"].startswith(supplemental)]
    assert len(original_gates) == 34 and all(g["passed"] for g in original_gates)
    failures = {g["name"] for g in summary["gates"] if not g["passed"]}
    assert failed_gate in failures


def test_relabeling_and_controller_aliases_preserve_response():
    e = choice_experiment("selector")
    state_names = {s: f"s{i}" for i, s in enumerate(e.system.states)}
    action_names = {a[0]: f"a{i}" for i, a in enumerate(e.system.actions)}
    actions = {a: (action_names[a[0]],) for a in e.system.actions}
    system = ControlledMarkovSystem(
        "renamed", tuple(state_names.values()), tuple(actions.values()),
        tuple((state_names[s], actions[a], state_names[t], p)
              for s, a, t, p in e.system.transitions),
    )
    teams = tuple((replace(
        team[0],
        observation_rows=tuple((state_names[s], o) for s, o in team[0].observation_rows),
        policy_rows=tuple((m, o, action_names[a]) for m, o, a in team[0].policy_rows),
    ),) for team in e.teams)
    renamed = replace(
        e, system=system, teams=teams,
        preparations={q: law.pushforward(state_names.__getitem__) for q, law in e.preparations.items()},
        terminals=frozenset(state_names[s] for s in e.terminals),
        costs={(state_names[s], actions[a], state_names[t]): cost for (s, a, t), cost in e.costs.items()},
    )
    inverse = {v: k for k, v in state_names.items()}
    target = project(evaluate(renamed), frame="binary",
                     readout=lambda _q, r: inverse[r.path.end][2])
    assert binary(e).signatures == target.signatures
    duplicate = (replace(e.teams[0][0], controller_id="alias"),)
    aliased = binary(replace(e, teams=e.teams + (duplicate,)))
    assert set(aliased.signatures.values()) == set(binary(e).signatures.values())


def test_incompatible_frames_and_invalid_models_are_refused():
    c = binary(choice_experiment("selector"))
    for altered in (replace(c, frame="other"), replace(c, budget=2),
                    replace(c, horizon=2), replace(c, inputs=("other",))):
        with pytest.raises(ValueError, match="matched"):
            emulate(c, altered)
    e = bit_experiment(False)
    with pytest.raises(ValueError, match="cover exactly"):
        replace(e, costs={})
    with pytest.raises(ValueError, match="observation"):
        replace(e, teams=((e.teams[0][0], replace(
            e.teams[0][1], observation_rows=e.teams[0][1].observation_rows[:-1]
        )),))
    with pytest.raises(ValueError, match="budget"):
        replace(e, budget=-1)
    with pytest.raises(ValueError, match="exact Fractions"):
        achievement(evaluate(e), FiniteDistribution((("0", 0.5), ("1", 0.5))),
                    {"any": lambda _q, _r: True})


def test_artifacts_reproduce_and_refuse_overwrite(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    runner.retain(first)
    runner.retain(second)
    for filename in ("summary.json", "evidence.json", "provenance.json", "report.md"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    evidence = json.loads((first / "evidence.json").read_text())
    assert evidence["bit"]["right"]["programs"]
    assert evidence["bit"]["right"]["laws"]
    with pytest.raises(FileExistsError):
        runner.retain(first)


def test_failed_gate_causes_nonzero_exit_and_is_retained(tmp_path, monkeypatch):
    result = run_experiment()
    result["gates"][0]["passed"] = False
    monkeypatch.setattr(runner, "run_experiment", lambda: result)
    assert runner.main(["--out-dir", str(tmp_path / "failed")]) == 1
    retained = json.loads((tmp_path / "failed" / "summary.json").read_text())
    assert retained["status"] == "FAIL"
