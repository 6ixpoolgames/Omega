"""Exact law preservation, adversarial controls, and instrument mutations."""

import inspect
import json
from dataclasses import replace
from fractions import Fraction
from itertools import product

import pytest

from omega_v2.experiments.continuation_equivalence_audit_v0 import (
    Case,
    control_panel,
    cost_distinction_case,
    memory_case,
    nuisance_extension,
    response_case,
)
from omega_v2.finite import continuation_prediction as core
from omega_v2.finite.model import ControlledMarkovSystem, FiniteDistribution
from omega_v2.finite.operational_continuation import Experiment, reactive_teams
from omega_v2.validation import continuation_equivalence_audit_v0 as runner

F = Fraction


@pytest.mark.parametrize("name,fixture", list(control_panel().items()), ids=list(control_panel()))
def test_full_laws_and_all_depth_partitions(name, fixture):
    e, interface = fixture.experiment, fixture.interface
    c1, quotient = core.build_c1(e, interface), core.build_quotient(e, interface)
    assert core.same_partitions(c1.decoding, quotient.decoding), name
    reference = core.reference_prediction(e, interface)
    for actual in (core.predict_graph(c1), core.predict_graph(quotient), core.predict_memoized(e, interface)):
        assert core.same_predictions(actual, reference), name


@pytest.mark.parametrize("terminal,visible", list(product((False, True), repeat=2)))
def test_exhaustive_two_state_kernel_census(terminal, visible):
    # All 81 two-state/two-action kernels with masses in {0,1/2,1}, for each
    # registered terminal/atom variant. This is a census of this tiny class,
    # not a sample of unfamiliar workshops or an independent evaluation.
    states, actions = ("a", "b"), ((0,), (1,))
    obs = {s: "blind" for s in states}
    teams = reactive_teams((obs,), ({"blind": (0, 1)},))
    interface = core.Interface((obs,), {s: s if visible else "same" for s in states})
    for probabilities in product((F(0), F(1, 2), F(1)), repeat=4):
        transitions = tuple((s, a, t, mass) for (s, a), p in zip(product(states, actions), probabilities, strict=True)
                            for t, mass in (("a", p), ("b", 1 - p)) if mass)
        e = Experiment(
            "tiny-census", ControlledMarkovSystem("census", states, actions, transitions),
            {s: FiniteDistribution.point_mass(s) for s in states}, teams,
            frozenset({"b"}) if terminal else frozenset(),
            {(s, a, t): int(t == "b") + a[0] for s, a, t, _p in transitions}, 3, 6,
        )
        c1, quotient = core.build_c1(e, interface), core.build_quotient(e, interface)
        assert core.same_partitions(c1.decoding, quotient.decoding)
        reference = core.reference_prediction(e, interface)
        assert core.same_predictions(core.predict_graph(c1), reference)
        assert core.same_predictions(core.predict_graph(quotient), reference)
        assert core.same_predictions(core.predict_memoized(e, interface), reference)


def test_costs_are_distinctions_and_budget_applies_to_the_whole_team():
    fixture = cost_distinction_case()
    e, interface = fixture.experiment, fixture.interface
    graph = core.build_c1(e, interface)
    assert graph.decoding[0]["cheap"] == graph.decoding[0]["dear"]
    assert graph.decoding[1]["cheap"] != graph.decoding[1]["dear"]
    limited = replace(e, budget=1)
    expected = core.reference_prediction(limited, interface)
    assert expected.rejected == {"c0-0": 2} and not expected.laws
    for result in (core.predict_graph(core.build_c1(limited, interface)), core.predict_memoized(limited, interface)):
        assert core.same_predictions(result, expected)
    partial = control_panel()["partial_cutoff"]
    partial = replace(partial, experiment=replace(partial.experiment, budget=1))
    result = core.predict_graph(core.build_c1(partial.experiment, partial.interface))
    assert not result.laws and result.rejected == {"c0-0": 2}


def test_memory_is_used_and_memo_cache_shares_suffixes():
    fixture = memory_case()
    e, interface = fixture.experiment, fixture.interface
    correct = core.predict_graph(core.build_c1(e, interface))
    controller = e.teams[0][0]
    broken = replace(controller, update_rows=tuple((m, o, 0) for m, o, _n in controller.update_rows))
    faulty = replace(e, teams=((broken,),))
    assert not core.same_predictions(correct, core.predict_graph(core.build_c1(faulty, interface)))
    c = response_case("live")
    duplicated = replace(c.experiment, preparations={**c.experiment.preparations,
                         "alias": c.experiment.preparations["trial"]})
    original = core.predict_memoized(c.experiment, c.interface)
    extra = core.predict_memoized(duplicated, c.interface)
    assert original.cache_entries == extra.cache_entries > 0


def renamed(fixture):
    e, interface = fixture.experiment, fixture.interface
    states = {s: f"renamed-state-{i}" for i, s in enumerate(reversed(e.system.states))}
    local_actions = tuple({a[i]: f"renamed-action-{a[i]}" for a in e.system.actions}
                          for i in range(len(e.system.actions[0])))
    actions = {a: tuple(local_actions[i][v] for i, v in enumerate(a)) for a in e.system.actions}
    observations = tuple({states[s]: o for s, o in obs.items()} for obs in interface.observations)
    system = ControlledMarkovSystem("renamed", tuple(states.values()), tuple(reversed(tuple(actions.values()))),
                                    tuple((states[s], actions[a], states[t], p)
                                          for s, a, t, p in reversed(e.system.transitions)))
    teams = tuple(tuple(replace(c, observation_rows=tuple(observations[i].items()),
                               policy_rows=tuple((m, o, local_actions[i][a]) for m, o, a in c.policy_rows))
                        for i, c in enumerate(team)) for team in e.teams)
    changed = replace(e, system=system, teams=teams,
                      costs={(states[s], actions[a], states[t]): cost for (s, a, t), cost in e.costs.items()},
                      terminals=frozenset(states[s] for s in e.terminals),
                      preparations={q: law.pushforward(states.__getitem__) for q, law in e.preparations.items()})
    return Case(changed, core.Interface(observations, {states[s]: atom for s, atom in interface.atoms.items()})), states, actions


@pytest.mark.parametrize("name", ["live", "memory", "hidden_bit", "partial_cutoff"])
def test_relabeling_and_independent_nuisance_are_true_invariances(name):
    fixture = control_panel()[name]
    changed, states, actions = renamed(fixture)
    original = core.build_c1(fixture.experiment, fixture.interface)
    altered = core.build_c1(changed.experiment, changed.interface)
    pulled_back = tuple({s: partition[states[s]] for s in states} for partition in altered.decoding)
    assert core.same_partitions(original.decoding, pulled_back)
    prediction = core.predict_graph(altered)
    inverse_actions = {new: old for old, new in actions.items()}
    normalized = core.Prediction({p: {q: law.pushforward(lambda t: replace(
        t, actions=tuple(inverse_actions[a] for a in t.actions)
    )) for q, law in laws.items()} for p, laws in prediction.laws.items()}, prediction.rejected)
    assert core.same_predictions(core.predict_graph(original), normalized)
    extended = nuisance_extension(fixture)
    graph = core.build_c1(extended.experiment, extended.interface)
    assert core.same_predictions(core.predict_graph(original), core.predict_graph(graph))
    assert [len(layer) for layer in original.layers] == [len(layer) for layer in graph.layers]


def test_interfaces_fail_closed_and_empty_catalogue_is_unavailable():
    fixture = response_case("live")
    e, interface = fixture.experiment, fixture.interface
    with pytest.raises(ValueError, match="atoms"):
        core.build_c1(e, replace(interface, atoms={}))
    with pytest.raises(ValueError, match="observation"):
        core.build_c1(e, replace(interface, observations=()))
    incompatible = replace(e.teams[0][0], observation_rows=tuple((s, "ready") for s in e.system.states),
                           policy_rows=((0, "ready", 0),), update_rows=((0, "ready", 0),))
    with pytest.raises(ValueError, match="share"):
        core.build_c1(replace(e, teams=((incompatible,),)), interface)
    empty = replace(e, teams=())
    prediction = core.predict_graph(core.build_c1(empty, interface))
    assert core.best_probability(prediction, FiniteDistribution.point_mass("trial"), lambda _q, _t: True) == (None, None)


def test_control_panel_and_accounting_pass():
    summary, evidence = runner.run_audit()
    assert summary["status"] == "PASS"
    assert all(g["passed"] for g in summary["gates"])
    graph = evidence["live"]["graphs"]["c1"]
    assert runner.serialized_bytes(graph) > runner.serialized_bytes(graph.layers)
    assert core.cost_record(7, 11)["total_cpu_ns"] == 18
    with pytest.raises(ValueError):
        core.cost_record(-1, 11)
    with pytest.raises(TypeError):
        runner.encode(object())


MUTATIONS = {
    "hidden_input_selection": ("best_probability", "    return scores[witness], witness", """    oracle = sum((weight * max(sum((p for t, p in laws[q].rows if task(q, t)), F(0))
                  for laws in prediction.laws.values()) for q, weight in weights.rows), F(0))
    return oracle, witness""", "c1.hidden_bit"),
    "lost_joint_constraint": ("predict_graph", "                        label = graph.layers[h - 1][target].label",
                             """                        label = graph.layers[h - 1][target].label
                        if action == (1, 1) and label.atom == (0, 0):
                            label = replace(label, atom=(1, 1))""", "repair_1.c1_exact"),
    "condition_on_completion": ("predict_graph", "            laws[q] = FiniteDistribution.from_mapping(masses)",
                                """            completed = {t: p for t, p in masses.items() if not t.censored}
            if completed:
                total = sum(completed.values(), F(0))
                masses = {t: p / total for t, p in completed.items()}
            laws[q] = FiniteDistribution.from_mapping(masses)""", "partial_cutoff.c1_exact"),
    "omit_extraction_cost": ("cost_record", "extraction_cpu_ns + prediction_cpu_ns", "prediction_cpu_ns",
                             "cost_accounting.synthetic_nonzero_extraction"),
    "erase_edge_cost": ("build_c1", "key = (e.costs[s, action, t], decoding[h - 1][t])",
                         "key = (0, decoding[h - 1][t])", "cost_distinction.partitions"),
}


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_runner_rejects_targeted_mutants_and_retains_failure(tmp_path, monkeypatch, mutation):
    name, old, new, failed_gate = MUTATIONS[mutation]
    source = inspect.getsource(getattr(core, name))
    assert source.count(old) == 1
    namespace = {**core.__dict__, "replace": replace}
    exec(compile(source.replace(old, new), f"<mutation:{mutation}>", "exec"), namespace)  # noqa: S102
    monkeypatch.setattr(core, name, namespace[name])
    # This one function is imported by the known-answer grader. Keep that
    # binding consistent when deliberately breaking the tested implementation.
    if name == "best_probability":
        monkeypatch.setattr("omega_v2.experiments.continuation_equivalence_audit_v0.best_probability", namespace[name])
    out_dir = tmp_path / mutation
    assert runner.main(["--out-dir", str(out_dir)]) == 1
    summary = json.loads((out_dir / "summary.json").read_text())
    assert summary["status"] == "FAIL"
    failures = {g["name"] for g in summary["gates"] if not g["passed"]}
    assert failed_gate in failures
    assert (out_dir / "evidence.json").is_file()


def test_artifacts_reproduce_semantics_and_refuse_overwrite(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    assert runner.main(["--out-dir", str(one)]) == runner.main(["--out-dir", str(two)]) == 0
    assert (one / "evidence.json").read_bytes() == (two / "evidence.json").read_bytes()
    assert (one / "report.md").read_bytes() == (two / "report.md").read_bytes()
    provenance = json.loads((one / "provenance.json").read_text())
    assert set(provenance["source_sha256"]) == set(runner.SOURCES)
    with pytest.raises(FileExistsError):
        runner.retain(one)
