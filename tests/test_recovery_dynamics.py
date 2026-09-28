"""Exact recovery probabilities, competing risks, cost vectors and mutants."""

import inspect
import json
from dataclasses import replace
from fractions import Fraction as F

import pytest

from omega_v2.experiments import recovery_dynamics_v0 as fixtures
from omega_v2.finite import recovery_dynamics as core
from omega_v2.finite.model import FiniteDistribution as Law
from omega_v2.validation import recovery_dynamics_v0 as runner


@pytest.fixture(scope="module")
def audit():
    return runner.run_audit()


def test_registered_panel_and_all_exact_checks(audit):
    summary, evidence = audit
    assert summary["status"] == "PASS"
    assert len(evidence) == len(summary["cases"]) == 14
    assert all(g["passed"] for g in summary["gates"])
    assert all(set(case["programs"]) == {"refuse", "recover"} for case in summary["cases"].values())


def test_slow_reset_is_certain_but_deadline_is_not_infinity(audit):
    summary, _ = audit
    result = summary["cases"]["open_noise_1000_m3"]["programs"]["refuse"]
    assert result["eventual"]["probability"] == 1
    assert result["eventual"]["mean"] == 8_004_002_000
    assert result["deadlines"][30]["live"] > F(999, 1000)
    assert result["eventual_causes"]["noise_assisted"]["probability"] == 1
    assert result["eventual_causes"]["selected"]["probability"] == 0


def test_death_is_competing_risk_not_successful_resistance(audit):
    summary, _ = audit
    r = summary["cases"]["competing_death"]["programs"]["refuse"]
    assert r["eventual"]["probability"] == F(3, 23)
    assert r["eventual"]["mean"] == "infinity"
    assert r["eventual"]["conditional_mean"] == F(80, 23)
    assert r["eventual_causes"]["dead"]["probability"] == F(20, 23)
    assert r["deadlines"][1]["live"] == F(57, 80)
    assert r["deadlines"][1]["reset_hazard"] == F(3, 80)
    assert r["deadlines"][1]["no_reset"] == F(77, 80)
    assert r["deadlines"][1]["expected_cost"] == (F(1), F(3, 80), F(0))


def test_ties_and_risk_set_exhaustion_are_explicit(audit):
    summary, _ = audit
    broken = summary["cases"]["broken_actuator"]
    assert broken["choices"][6]["objective_J"] == {"value": F(1), "programs": ("refuse", "recover")}
    assert not broken["possible_recovery_region"]
    result = summary["cases"]["open_noiseless"]["programs"]["recover"]
    assert result["deadlines"][1]["reset_hazard"] == 1
    assert result["deadlines"][2]["reset_hazard"] is None
    assert result["deadlines"][2]["risk_set_exhausted"]
    assert result["deadlines"][30]["expected_cost"] == (1, 1, 0)


def test_reachable_non_target_closed_class_has_infinite_unconditional_mean():
    chain = core.Chain(("start", "goal", "closed"), "start", {
        "start": Law(((("goal", (1, 2, 0)), F(1, 2)), (("closed", (1, 0, 0)), F(1, 2)))),
        "goal": Law.point_mass(("goal", (0, 0, 0))),
        "closed": Law.point_mass(("closed", (1, 0, 0))),
    }, {"start": "live", "goal": "selected", "closed": "live"}, frozenset({"goal"}))
    result = core.hitting_analysis(chain, frozenset({"goal"}))
    assert result["initial"] == {"probability": F(1, 2), "weighted_time": F(1, 2),
                                 "mean": "infinity", "conditional_mean": F(1)}
    assert result["possible"] == frozenset({"start", "goal"})
    assert result["almost_sure"] == frozenset({"goal"})
    assert all(v == (0, 0) for v in result["residuals"].values())
    assert core.propagate(chain, 5)[5]["expected_cost"] == (3, 1, 0)
    assert core.hitting_analysis(chain, frozenset())["initial"]["conditional_mean"] is None
    at_goal = core.hitting_analysis(replace(chain, initial="goal"), frozenset({"goal"}))
    assert at_goal["initial"]["mean"] == at_goal["initial"]["conditional_mean"] == 0


@pytest.mark.parametrize("probability", [F(0), F(1, 1000), F(1, 3), F(1)])
def test_geometric_chain_closed_form(probability):
    edges = {("start", (1, 0, 0)): 1 - probability, ("goal", (1, 0, 0)): probability}
    chain = core.Chain(("start", "goal"), "start", {
        "start": Law.from_mapping(edges), "goal": Law.point_mass(("goal", (0, 0, 0))),
    }, {"start": "live", "goal": "selected"}, frozenset({"goal"}))
    r = core.hitting_analysis(chain, frozenset({"goal"}))["initial"]
    assert r["probability"] == int(probability > 0)
    assert r["mean"] == (1 / probability if probability else "infinity")
    assert core.propagate(chain, 10)[10]["law"].probability("start") == (1 - probability) ** 10


def test_vector_costs_preserve_different_charges_on_same_successor():
    world = fixtures.build_world(fixtures.Settings("broken", working=False, epsilon=F(1, 10)))
    chain = fixtures.product_chain(world, world.programs[0])
    assert len(chain.rows[chain.initial].rows) == 2
    law = core.joint_cost_law(chain, 2).pushforward(lambda edge: edge[1])
    assert law.mass_map == {(2, 0, 0): F(361, 400), (2, 1, 0): F(19, 200), (2, 2, 0): F(1, 400)}
    paths = core.full_paths(chain, 2)
    assert len(paths.rows) == 4  # Distinguish energy on the first versus second tick.
    assert len(paths.pushforward(lambda p: p.states).rows) == 1


def test_invalid_probabilities_targets_and_terminal_costs_fail_closed():
    with pytest.raises(ValueError, match="rational"):
        fixtures.Settings("inexact", epsilon=0.1)
    world = fixtures.build_world(fixtures.Settings("simple"))
    chain = fixtures.product_chain(world, world.programs[1])
    with pytest.raises(ValueError, match="unknown target"):
        core.hitting_analysis(chain, frozenset({"missing"}))
    with pytest.raises(ValueError, match="horizon"):
        core.propagate(chain, -1)
    terminal = next(iter(chain.terminals))
    with pytest.raises(ValueError, match="terminal"):
        replace(chain, rows={**chain.rows, terminal: Law.point_mass((terminal, (1, 0, 0)))})
    with pytest.raises(ValueError, match="singular"):
        core._solve([[F(0)]], [F(1)])


MUTATIONS = {
    "dead_as_live": ("runner", "readouts", "kind = chain.outcomes[state]",
                     "kind = 'live' if chain.outcomes[state] == 'dead' else chain.outcomes[state]",
                     "competing_death.refuse.deadline_1.live_formula"),
    "restore_broken_actuator": ("fixtures", "transition", 'executed == "recover" and settings.working',
                               'executed == "recover"', "broken_actuator.refuse.eventual_reset"),
    "external_as_selected": ("fixtures", "transition", 'State(outcome="external")',
                             'State(outcome="selected")', "external_writer.refuse.writer_probability"),
    "discard_death_and_renormalize": ("core", "propagate", "        law = FiniteDistribution.from_mapping(masses)",
                                     """        masses = {s: p for s, p in masses.items() if chain.outcomes[s] != 'dead'}
        total = sum(masses.values(), F(0))
        law = FiniteDistribution.from_mapping({s: p / total for s, p in masses.items()})""",
                                     "competing_death.refuse.paths_1.marginal"),
}


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_mutants_fail_retained_runner(tmp_path, monkeypatch, mutation):
    module_name, name, old, new, failed_gate = MUTATIONS[mutation]
    module = {"runner": runner, "fixtures": fixtures, "core": core}[module_name]
    source = inspect.getsource(getattr(module, name))
    assert source.count(old) == 1
    namespace = dict(vars(module))
    exec(compile(source.replace(old, new), f"<mutation:{mutation}>", "exec"), namespace)  # noqa: S102
    monkeypatch.setattr(module, name, namespace[name])
    output = tmp_path / mutation
    assert runner.main(["--out-dir", str(output)]) == 1
    summary = json.loads((output / "summary.json").read_text())
    assert summary["status"] == "FAIL"
    assert failed_gate in {g["name"] for g in summary["gates"] if not g["passed"]}
    assert (output / "evidence.json").is_file()


def test_retained_artifacts_are_exact_reproducible_and_refuse_overwrite(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    assert runner.main(["--out-dir", str(one)]) == runner.main(["--out-dir", str(two)]) == 0
    for name in ("summary.json", "evidence.json", "report.md"):
        assert (one / name).read_bytes() == (two / name).read_bytes()
    provenance = json.loads((one / "provenance.json").read_text())
    assert set(provenance["source_sha256"]) == set(runner.SOURCES)
    with pytest.raises(FileExistsError):
        runner.retain(one)
