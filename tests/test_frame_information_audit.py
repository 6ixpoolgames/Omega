"""Information cannot be recovered from an analyst's history without a channel."""

import inspect
import json
from fractions import Fraction
from itertools import product

import pytest

from omega_v2.experiments import frame_information_audit_v0 as fixtures
from omega_v2.finite import continuation_prediction as core
from omega_v2.finite.information_frames import audit_information_step, conditional_expectations
from omega_v2.finite.model import FiniteDistribution
from omega_v2.validation import frame_information_audit_v0 as runner

F = Fraction


@pytest.mark.parametrize("name,fixture", list(fixtures.control_panel().items()), ids=list(fixtures.control_panel()))
def test_all_predictors_preserve_complete_laws(name, fixture):
    e, interface = fixture.experiment, fixture.interface
    reference = core.reference_prediction(e, interface)
    c1, quotient = core.build_c1(e, interface), core.build_quotient(e, interface)
    assert core.same_partitions(c1.decoding, quotient.decoding), name
    for actual in (core.predict_graph(c1), core.predict_graph(quotient), core.predict_memoized(e, interface)):
        assert core.same_predictions(reference, actual), name


def test_erasure_merges_current_records_but_not_verification_histories():
    fixture = fixtures.memory_case("erased")
    e, interface = fixture.experiment, fixture.interface
    prediction = core.predict_graph(core.build_c1(e, interface))
    assert len(e.teams) == 16
    for team in e.teams:
        controller = team[0]
        assert all(controller.update(m, ("erase",)) == fixtures.BLANK for m in fixtures.MEMORIES)
        for phase in ("show", "erase"):
            actions = {a for _m, obs, a in controller.policy_rows if obs[0] == phase}
            assert actions == {"advance"}
    for policy, laws in prediction.laws.items():
        left, right = laws["0"].support[0], laws["1"].support[0]
        assert left.observations[0][0] != right.observations[0][0]
        assert fixtures.history_at(("0", left), 2) != fixtures.history_at(("1", right), 2)
        assert fixtures.accessible_at(("0", left), 2) == fixtures.accessible_at(("1", right), 2)
        assert left.memories[0][2] == right.memories[0][2] == fixtures.BLANK
        assert left.actions == right.actions, policy
    score, _witness = core.best_probability(prediction, fixtures.WEIGHTS, fixtures.correct_guess)
    assert score == F(1, 2)


@pytest.mark.parametrize("mode,remembers,reads", [
    ("remember", True, True), ("erased", False, False),
    ("sealed", False, False), ("retrieve", False, True),
])
def test_coherence_and_posteriors_obey_the_actual_information(mode, remembers, reads):
    fixture = fixtures.memory_case(mode)
    prediction = core.reference_prediction(fixture.experiment, fixture.interface)
    frame = fixtures.frame_diagnostics(prediction)
    forward = frame["accessible_forward"]
    assert forward["after_refines_before"] is remembers
    assert forward["tower_holds_for_readout"] is remembers
    assert frame["history_forward"]["after_refines_before"]
    assert frame["history_forward"]["tower_holds_for_readout"]
    assert frame["accessible_reverse"]["tower_holds_for_readout"]
    if not remembers:
        witness = forward["refinement_counterexample"]
        assert witness["left"][0] != witness["right"][0]
        assert {r["difference"] for r in forward["tower_rows"]} == {F(-1, 2), F(1, 2)}
        assert set(forward["after_cells"]) == {(("access",), fixtures.BLANK)}
    read = fixtures.read_diagnostics(prediction)
    assert {cell["mean"] for cell in read["after_read"].values()} == ({F(0), F(1)} if reads else {F(1, 2)})


def test_archive_existence_is_not_read_access_and_retrieval_is_charged():
    predictions = {}
    for mode in ("erased", "sealed", "retrieve"):
        fixture = fixtures.memory_case(mode)
        e = fixture.experiment
        predictions[mode] = core.reference_prediction(e, fixture.interface)
        for law in e.preparations.values():
            s = law.support[0]
            assert s[2] == (fixtures.BLANK if mode == "erased" else s[1])
    assert core.same_predictions(predictions["erased"], predictions["sealed"])
    assert not core.same_predictions(predictions["sealed"], predictions["retrieve"])
    for mode, prediction in predictions.items():
        for policy, laws in prediction.laws.items():
            expected = (5, 6) if policy.startswith("retrieve:") else (4, 4)
            assert {(t.elapsed, t.cost) for law in laws.values() for t in law.support} == {expected}, mode


def test_deadline_and_budget_fail_differently_without_conditioning_them_away():
    panel = fixtures.control_panel()
    predictions = {name: core.reference_prediction(panel[name].experiment, panel[name].interface)
                   for name in ("short_deadline", "low_budget", "zero_budget")}
    short = predictions["short_deadline"]
    assert len(short.laws) == 16 and not short.rejected
    for name, laws in short.laws.items():
        if name.startswith("retrieve:"):
            assert all(t.censored and t.cost == 5 and t.elapsed == 4 for law in laws.values() for t in law.support)
    low = predictions["low_budget"]
    assert len(low.laws) == len(low.rejected) == 8
    assert set(low.rejected.values()) == {6}
    assert all(policy.startswith("retrieve:") for policy in low.rejected)
    assert not predictions["zero_budget"].laws
    assert len(predictions["zero_budget"].rejected) == 16


def test_refinement_is_equivalent_to_tower_for_all_indicator_readouts():
    # All pairs of binary information maps on four atoms, under a nonuniform
    # exact law. Indicator readouts form a basis, unlike one constant probe.
    law = FiniteDistribution(tuple((i, F(i + 1, 10)) for i in range(4)))
    maps = list(product((0, 1), repeat=4))
    for before, after in product(maps, repeat=2):
        results = [audit_information_step(law, before.__getitem__, after.__getitem__,
                                         lambda i, atom=atom: F(int(i == atom))) for atom in range(4)]
        assert all(r["tower_holds_for_readout"] for r in results) == results[0]["after_refines_before"]


def test_accidentally_coherent_constant_readout_does_not_establish_refinement():
    law = FiniteDistribution(((0, F(1, 2)), (1, F(1, 2))))
    result = audit_information_step(law, lambda bit: bit, lambda _bit: "blank", lambda _bit: F(7))
    assert result["tower_holds_for_readout"]
    assert not result["after_refines_before"]
    assert result["refinement_counterexample"] is not None
    cells = conditional_expectations(law, lambda _bit: "blank", lambda bit: F(bit))
    assert cells == {"blank": {"mass": F(1), "mean": F(1, 2)}}
    with pytest.raises(TypeError, match="exact Fractions"):
        conditional_expectations(law, lambda bit: bit, lambda bit: float(bit))
    with pytest.raises(TypeError, match="exact Fractions"):
        conditional_expectations(FiniteDistribution(((0, 0.5), (1, 0.5))), lambda bit: bit, lambda bit: F(bit))


MUTATIONS = {
    "recover_old_memory": ("predictor", "predict_graph",
                           "c.action(m[-1], o) for c, m, o in zip(",
                           ("(c.action(next((old for old in reversed(m) if old in (0, 1)), m[-1]), o) "
                            "if o == ('guess',) else c.action(m[-1], o)) for c, m, o in zip("),
                           "erased.c1.best_guess"),
    "bypass_reset": ("fixture", "memory_update", "        return BLANK", "        return memory",
                     "erased.reference.best_guess"),
    "omit_retrieval_charge": ("fixture", "operation_cost",
                              'return 2 if state[0] == "access" and action == ("retrieve",) else 1',
                              "return 1", "low_budget.reference.best_guess"),
}


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_runner_rejects_targeted_mutants_and_retains_failure(tmp_path, monkeypatch, mutation):
    target, name, old, new, expected_gate = MUTATIONS[mutation]
    module = core if target == "predictor" else fixtures
    source = inspect.getsource(getattr(module, name))
    assert source.count(old) == 1
    namespace = dict(module.__dict__)
    exec(compile(source.replace(old, new), f"<mutation:{mutation}>", "exec"), namespace)  # noqa: S102
    monkeypatch.setattr(module, name, namespace[name])
    output = tmp_path / mutation
    assert runner.main(["--out-dir", str(output)]) == 1
    summary = json.loads((output / "summary.json").read_text())
    assert summary["status"] == "FAIL"
    assert expected_gate in {g["name"] for g in summary["gates"] if not g["passed"]}
    assert (output / "evidence.json").is_file()


def test_report_and_full_evidence_reproduce_and_refuse_overwrite(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    assert runner.main(["--out-dir", str(first)]) == runner.main(["--out-dir", str(second)]) == 0
    for name in ("summary.json", "evidence.json", "provenance.json", "report.md"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    evidence = json.loads((first / "evidence.json").read_text())
    assert set(evidence) == set(fixtures.control_panel())
    assert evidence["erased"]["frame_diagnostics"]["reference"]["erasure"]["accessible_forward"]["refinement_counterexample"]
    summary = json.loads((first / "summary.json").read_text())
    assert all(g["passed"] for g in summary["gates"])
    with pytest.raises(FileExistsError):
        runner.retain(first)
