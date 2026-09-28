"""Resource ordering, recurrent correction, permanent safety and retained faults."""

import inspect
import json
from fractions import Fraction as F

import pytest

from omega_v2.experiments import recovery_suppression_v0 as fixtures
from omega_v2.finite.model import FiniteDistribution as Law
from omega_v2.finite.recovery_dynamics import Chain, hitting_analysis
from omega_v2.finite.recovery_persistence import permanent_membership
from omega_v2.validation import recovery_suppression_v0 as runner


@pytest.fixture(scope="module")
def audit():
    return runner.run_audit()


def result(audit, world, program="suppress/idle"):
    return audit[0]["cases"][world]["programs"][program]


def test_registered_panel(audit):
    summary, evidence = audit
    assert summary["status"] == "PASS" and len(evidence) == 20
    assert all(g["passed"] for g in summary["gates"])
    assert all(len(case["programs"]) == 6 for case in summary["cases"].values())


@pytest.mark.parametrize("name,mean", [("recurring_s1", 5), ("recurring_s3", 7),
                                       ("recurring_cost2", 5), ("recurring_underfunded", 9),
                                       ("seal_failure_s1", 6), ("seal_failure_s3", 10)])
def test_registered_suppression_means(audit, name, mean):
    r = result(audit, name)
    assert r["first"]["probability"] == r["permanent_probability"] == 1
    assert r["first"]["mean"] == mean


def test_replenishment_cannot_pay_early_and_vectors_stay_separate(audit):
    r = result(audit, "recurring_underfunded")
    assert r["deadlines"][2]["expected_cost"] == (2, 4, 0)
    assert r["deadlines"][2]["stock_law"] == {1: F(1)}
    assert r["deadlines"][3]["ever_reset"] == F(1, 4)
    assert r["deadlines"][3]["stock_law"] == {2: F(1)}
    assert r["deadlines"][3]["expected_cost"] == (3, 4, 0)
    assert r["deadlines"][4]["expected_cost"] == (4, F(11, 2), 0)


def test_one_shot_hidden_and_maintained_protection_differ(audit):
    sealed = result(audit, "one_shot_s1")
    hidden = result(audit, "hide_only")
    fragile = result(audit, "seal_failure_s1")
    assert sealed["first"]["probability"] == 0
    assert sealed["deadlines"][30]["expected_cost"] == (30, 1, 0)
    assert hidden["first"]["probability"] == 1 and hidden["first"]["mean"] == 4
    assert fragile["deadlines"][2]["ever_reset"] == F(1, 8)
    assert result(audit, "seal_replenished")["first"]["probability"] == 0


def test_noise_can_bypass_protection_and_undo_correction(audit):
    r = result(audit, "recurring_noise")
    assert r["first"]["probability"] == 1 and r["first"]["mean"] == 24
    assert r["deadlines"][1]["first_sources"] == {
        "selected": F(0), "noise_assisted": F(1, 30), "external": F(1, 120)
    }
    assert r["corrected_step_survival"] == F(19, 20)
    assert r["corrected_spell_mean"] == 20 and r["permanent_probability"] == 0
    assert result(audit, "one_shot_noise")["first"]["probability"] == 1


def test_first_reset_survives_relapse_and_is_distinct_from_occupancy(audit):
    cycle = result(audit, "no_stock", "recover/revert")
    assert cycle["first"]["mean"] == 1
    assert cycle["deadlines"][1]["corrected"] == 1
    assert cycle["deadlines"][2]["corrected"] == 0
    assert cycle["deadlines"][2]["ever_reset"] == cycle["deadlines"][2]["ever_relapsed"] == 1
    assert cycle["deadlines"][2]["first_sources"]["selected"] == 1
    assert cycle["permanent_probability"] == 0
    spontaneous = result(audit, "spontaneous_relapse", "idle/idle")
    assert spontaneous["first"]["probability"] == 1
    assert spontaneous["deadlines"][30]["corrected"] == F(1, 2) * (1 - F(1, 2) ** 30)
    assert spontaneous["permanent_probability"] == 0


def test_current_proxy_objective_can_reward_a_reset_revert_cycle(audit):
    choices = audit[0]["cases"]["no_stock"]["choices"][6]
    assert choices["objective_J"] == {"value": F(1), "programs": ("recover/revert",)}
    assert choices["alive_never_reset"]["value"] == F(3, 4) ** 6
    assert "recover/revert" not in choices["alive_never_reset"]["programs"]


def test_dead_after_reset_is_retained_as_history_not_live_correction(audit):
    r = result(audit, "competing_death", "idle/idle")
    assert r["first"]["probability"] == F(3, 7)
    assert r["permanent_probability"] == 0
    assert r["death"]["probability"] == 1
    at_two = r["deadlines"][2]
    assert at_two["dead_after"] == F(3, 64)
    assert at_two["ever_reset"] > at_two["corrected"]
    suppressed = result(audit, "replenished_death")
    assert suppressed["first"]["probability"] == 0
    assert suppressed["death"]["probability"] == 1
    assert suppressed["deadlines"][30]["never_reset"] == F(3, 4) ** 30


def chain_from_rows(rows, initial):
    return Chain(tuple(rows), initial, {
        s: Law(tuple(((t, (1, 0, 0)), p) for t, p in targets.items())) for s, targets in rows.items()
    }, {s: s for s in rows}, frozenset())


def test_eventual_permanence_allows_a_transient_relapse_before_stabilizing():
    chain = chain_from_rows({"provisional": {"bad": F(1, 2), "stable": F(1, 2)},
                             "bad": {"stable": F(1)}, "stable": {"stable": F(1)}}, "provisional")
    safe = frozenset({"provisional", "stable"})
    r = permanent_membership(chain, safe)
    assert r["closed_safe"] == frozenset({"stable"})
    assert r["removed_layers"] == (frozenset({"provisional"}),)
    assert r["hitting"]["initial"]["probability"] == 1
    assert r["hitting"]["initial"]["mean"] == F(3, 2)
    assert hitting_analysis(chain, frozenset({"bad"}))["initial"]["probability"] == F(1, 2)


def test_corrected_recurrent_cycle_is_permanent_without_terminal_states():
    chain = chain_from_rows({"bad": {"a": F(1)}, "a": {"b": F(1)}, "b": {"a": F(1)}}, "bad")
    r = permanent_membership(chain, frozenset({"a", "b"}))
    assert r["closed_safe"] == frozenset({"a", "b"})
    assert r["hitting"]["initial"]["probability"] == 1
    assert not chain.terminals


def test_long_transient_safety_is_not_permanence():
    chain = chain_from_rows({"safe": {"safe": F(999, 1000), "bad": F(1, 1000)}, "bad": {"bad": F(1)}}, "safe")
    assert hitting_analysis(chain, frozenset({"safe"}))["initial"]["probability"] == 1
    r = permanent_membership(chain, frozenset({"safe"}))
    assert not r["closed_safe"] and r["hitting"]["initial"]["probability"] == 0
    with pytest.raises(ValueError, match="unknown safe"):
        permanent_membership(chain, frozenset({"absent"}))


def test_inputs_fail_closed_and_instrumentation_is_unobserved():
    with pytest.raises(ValueError, match="rational"):
        fixtures.Settings("bad", epsilon=0.1)
    with pytest.raises(ValueError, match="positive price"):
        fixtures.Settings("free", price=0)
    world = fixtures.build_world(fixtures.Settings("test", capacity=1, relapse=F(1, 4)))
    for program in world.programs:
        for state in world.states:
            assert program.observe(state) == (state.reference, state.dead)


MUTATIONS = {
    "free_recurring": ("purchase", "stock -= settings.price", "stock -= 0", "recurring_s1.stock_balance"),
    "early_replenishment": ("purchase", "stock = state.stock",
                            "stock = min(settings.capacity, state.stock + settings.replenish)",
                            "recurring_underfunded.suppress.first_mean"),
    "underfunded_protection": ("purchase", "return stock, sealed, protected, spent",
                               "return stock, sealed, protected or command == 'suppress', spent",
                               "no_stock.suppress.first_mean"),
    "hide_blocks_writer": ("transition", 'blocked = protected and settings.effect == "block"',
                           "blocked = protected", "hide_only.suppress.first_mean"),
    "no_seal_failure": ("transition", "if target.sealed:", "if target.sealed and False:",
                        "seal_failure_s1.suppress.first_mean"),
    "absorbing_correction": ("transition", "if state.dead:", "if state.dead or state.reference:",
                             "no_stock.recover/revert.alternating_reference"),
    "erase_reset_history": ("_relapse", "return replace(state, reference=False, relapsed=True)",
                            "return replace(state, reference=False, relapsed=True, first='none')",
                            "no_stock.history_preserved"),
}


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_mutants_fail_retained_runner(tmp_path, monkeypatch, mutation):
    function, old, new, expected_gate = MUTATIONS[mutation]
    source = inspect.getsource(getattr(fixtures, function))
    assert source.count(old) == 1
    namespace = dict(vars(fixtures))
    exec(compile(source.replace(old, new), f"<mutation:{mutation}>", "exec"), namespace)  # noqa: S102
    monkeypatch.setattr(fixtures, function, namespace[function])
    output = tmp_path / mutation
    assert runner.main(["--out-dir", str(output)]) == 1
    summary = json.loads((output / "summary.json").read_text())
    assert summary["status"] == "FAIL"
    assert expected_gate in {g["name"] for g in summary["gates"] if not g["passed"]}
    assert (output / "evidence.json").is_file()


def test_retained_artifacts_reproduce_and_refuse_overwrite(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    assert runner.main(["--out-dir", str(one)]) == runner.main(["--out-dir", str(two)]) == 0
    for filename in ("summary.json", "evidence.json", "report.md"):
        assert (one / filename).read_bytes() == (two / filename).read_bytes()
    provenance = json.loads((one / "provenance.json").read_text())
    assert set(provenance["source_sha256"]) == set(runner.SOURCES)
    with pytest.raises(FileExistsError):
        runner.retain(one)
