"""Mechanism, baseline, evaluator boundary, and adversarial checks."""

import copy
import json
from dataclasses import replace
from fractions import Fraction

import pytest

from omega_v2.experiments import lushness_decision_v0 as fixtures
from omega_v2.finite import joint_requirements as core
from omega_v2.validation import lushness_decision_v0 as runner

F = Fraction


@pytest.fixture
def panel():
    return {w.name: w for w in fixtures.public_worlds()}


def test_shared_stock_does_not_become_separate_agent_budgets(panel):
    world = panel["scarcity"]
    scores = core.bonuses(world, "endogenous")["idle"]
    assert scores["joint"] == 0
    assert scores["nonjoint"] == 1
    assert core.attainment_frontier(core.endpoints(world, world.action("idle")), (1, 1, 0)) == ((0, 1, 1), (1, 0, 1))


@pytest.mark.parametrize("budget", [(1, 3, 3), (4, 0, 3), (4, 3, 0)])
def test_each_budget_coordinate_can_independently_prevent_work(budget):
    world = fixtures.workshop("limited", budget=budget, menu=("idle",))
    states = core.endpoints(world, world.action("idle"))
    assert set(states) == {(0, 0, 0, 0, 0)}


def test_schedule_witnesses_and_independent_reference(panel):
    for world in panel.values():
        for action in world.actions:
            rows = core.endpoints(world, action)
            assert set(rows) == runner.reference_endpoints(world, action)
            for state, commands in rows.items():
                current = (0, 0, 0, 0, 0)
                for command in commands:
                    current = dict(core.successors(world, action, current))[command]
                assert state == current


def test_prerequisite_requires_an_actual_prior_project():
    world = fixtures.workshop("dependency", permissions=(7, 7, 7), menu=("idle",))
    assert core.individual_value(core.endpoints(world, world.action("idle")), 0, 4) == F(1, 4)


def test_rewrite_cannot_choose_its_judges(panel):
    world = panel["rewrite"]
    scores = core.bonuses(world, "endogenous")["rewrite"]
    assert scores["joint"] == 0
    assert scores["accessible_joint"] == 1
    action = world.action("rewrite")
    assert core.reference_requests(world, action) == world.history
    assert core.reference_requests(world, action, True) == (1, 0, 0)
    assert "external_rewrite" in core.rejections(world, action, "full")


@pytest.mark.parametrize("action,authorized", [("commit", True), ("capture", False),
    ("selected_without_records", False), ("selected_under_coercion", False)])
def test_commitment_needs_source_records_and_declared_uncoerced_choice(panel, action, authorized):
    world = panel["commitment"]
    assert world.action(action).authorized(1) is authorized
    assert (not core.rejections(world, world.action(action), "full")) is authorized
    assert core.reference_requests(world, world.action(action))[1] == (1 if authorized else 2)


def test_capture_and_commitment_have_identical_physical_endpoints(panel):
    world = panel["commitment"]
    assert set(core.endpoints(world, world.action("commit"))) == set(core.endpoints(world, world.action("capture")))


def test_legitimate_revision_does_not_rewrite_an_independent_new_plan(panel):
    world = panel["commitment"]
    evaluation = fixtures.public_evaluation((world,))["worlds"][world.name]
    result = core.evaluate_action(world, world.action("commit"), evaluation)
    assert result["bundles"][0]["request"] == (1, 1, 0)
    assert result["bundles"][1]["request"] == (2, 4, 0)
    assert core.evaluate_action(world, world.action("capture"), evaluation)["bundles"][0]["request"] == (1, 2, 0)


def test_first_permanence_and_harm_race_are_distinct(panel):
    world = panel["corridor"]
    unstable = core.recovery(world.action("unstable_work").correction)
    hazard = core.recovery(world.action("hazardous_work").correction)
    assert unstable["first"]["probability"] == 1
    assert unstable["permanent"]["probability"] == 0
    assert hazard["permanent"]["probability"] == 1
    assert hazard["race"]["probability"] == 0
    assert hazard["harm"] == 1
    assert any(s == ("K", True) and p > 0 for s, p in hazard["deadline_6"])


def test_analytic_partial_safety_race():
    row = core.recovery((F(1), F(1), F(0), F(1, 4)))
    assert row["permanent"]["probability"] == 1
    assert row["race"]["probability"] == F(9, 16)
    assert row["harm"] == F(7, 16)
    assert sum(p for _s, p in row["deadline_6"]) == 1


def test_default_filtered_future_tasks_use_paired_completion_time():
    world = fixtures.workshop("ft", history=(4, 4, 0), menu=("idle", "workshop"))
    bonus = core.bonuses(world, "endogenous")
    assert bonus["workshop"]["future_raw"] == F(1, 4)
    assert bonus["workshop"]["future_filtered"] == 0
    assert bonus["idle"]["future_raw"] == 0
    other = fixtures.workshop("ft-existing", menu=("idle", "workshop"))
    assert core.bonuses(other, "endogenous")["workshop"]["future_filtered"] == F(1, 2)


def test_aup_scale_is_positive_and_idle_penalty_zero(panel):
    for world in panel.values():
        assert all(v >= 1 for v in core.auxiliary_values(world, world.action("idle")))
        assert core.bonuses(world, "endogenous")["idle"]["aup"] == 0
        assert all(row["aup"] <= 0 for row in core.bonuses(world, "endogenous").values())


def test_rr_full_state_and_projected_outcomes_are_labelled_separately(panel):
    rows = core.bonuses(panel["domination"], "endogenous")
    assert rows["idle"]["rr_state"] == rows["idle"]["rr_outcome"] == 0
    assert rows["seize"]["rr_state"] != rows["seize"]["rr_outcome"]


def test_empowerment_counts_distinguishable_endpoints_not_action_strings(panel):
    row = core.bonuses(panel["scarcity"], "endogenous")["idle"]
    assert row["operator_empowerment"] == F(1, 4)
    assert row["assist_empowerment"] == F("0.333333333333")


def test_family_set_operations_and_empty_intersection():
    world = fixtures.workshop("families", menu=("idle",))
    action = world.action("idle")
    basic = [set(core.bundles(world, action, f)) for f in core.FAMILIES[:4]]
    assert set(core.bundles(world, action, "intersection")) == set.intersection(*basic)
    assert all(s <= set(core.bundles(world, action, "union")) for s in basic)
    empty = replace(world, prerequisites=(0, 0, 0))
    assert core.bundles(empty, action, "centrality") == ()
    assert core.choose(empty, "centrality", "joint", "full", F(1))["choices"] == ()
    assert core.bonuses(empty, "centrality")["idle"]["joint"] is None


def test_ties_are_all_retained_and_lambda_zero_removes_bonus(panel):
    world = panel["corridor"]
    selected = core.choose(world, "endogenous", "joint", "none", F(0))
    assert set(selected["choices"]) == {"unstable_work", "hazardous_work"}
    assert core.choose(world, "endogenous", "joint", "full", F(0))["choices"] == ("work",)
    assert set(core.choose(world, "endogenous", "direct", "without_recovery", F(0))["choices"]) == set(selected["choices"])


def test_jointness_without_identity_can_double_count_one_project(panel):
    row = core.bonuses(panel["scarcity"], "endogenous")["idle"]
    assert row["joint"] == 0
    assert row["without_identity"] == 1


def test_world_serialization_rejects_private_inputs(panel):
    for world in panel.values():
        assert core.world_from_data(core.world_data(world)) == world
    data = core.world_data(panel["scarcity"])
    data["private_requirements"] = [1, 1, 7]
    with pytest.raises(ValueError, match="schema"):
        core.world_from_data(data)


@pytest.fixture
def saved(panel):
    worlds = (panel["scarcity"], panel["commitment"])
    manifest = runner.public_manifest(worlds)
    return worlds, manifest, runner.decide(manifest), fixtures.public_evaluation(worlds)


def test_evaluator_does_not_call_chooser_or_change_choices(saved, monkeypatch):
    _worlds, manifest, decisions, evaluation = saved
    old = core.digest(decisions)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("private evaluator tried to choose again")

    monkeypatch.setattr(core, "choose", forbidden)
    first = runner.assess(manifest, decisions, evaluation)
    changed = copy.deepcopy(evaluation)
    for row in changed["worlds"].values():
        row["bundles"][1]["request"] = [0, 0, 7]
    second = runner.assess(manifest, decisions, changed)
    assert first["decisions_digest"] == second["decisions_digest"] == old
    assert core.digest(decisions) == old
    assert first["evaluation_digest"] != second["evaluation_digest"]


@pytest.mark.parametrize("fault", ["missing_mass", "negative_mass", "unknown_agent", "unknown_world", "unknown_harm", "false_history", "independent_label"])
def test_malformed_evaluation_is_rejected_without_rescaling(saved, fault):
    worlds, _manifest, _decisions, evaluation = saved
    changed = copy.deepcopy(evaluation)
    row = changed["worlds"][worlds[0].name]
    if fault == "missing_mass":
        row["bundles"][0]["weight"] = "1/8"
    elif fault == "negative_mass":
        row["bundles"][0]["weight"] = "-1/4"
    elif fault == "unknown_agent":
        row["bundles"][0]["request"] = [1, 1, 0, 1]
    elif fault == "unknown_world":
        changed["worlds"]["unexpected"] = row
    elif fault == "unknown_harm":
        row["harm_criteria"]["0"] = ["secret_new_predicate"]
    elif fault == "false_history":
        row["bundles"][0]["request"] = [0, 0, 0]
    else:
        changed["status"] = "independently_confirmed"
    with pytest.raises(ValueError):
        core.validate_evaluation(worlds, changed)


@pytest.mark.parametrize("fault", ["changed_world", "changed_source", "missing_rule", "missing_tie"])
def test_stale_or_incomplete_decisions_fail(saved, fault):
    _worlds, manifest, decisions, evaluation = saved
    changed = copy.deepcopy(decisions)
    if fault == "changed_world":
        changed["worlds_digest"] = "bad"
    elif fault == "changed_source":
        changed["source_sha256"] = {}
    elif fault == "missing_rule":
        changed["worlds"]["scarcity"].pop(next(iter(changed["worlds"]["scarcity"])))
    else:
        key = runner.rule_id("endogenous", "direct", "none", F(0))
        changed["worlds"]["commitment"][key]["choices"].pop()
    with pytest.raises(ValueError):
        runner.assess(manifest, changed, evaluation)


def test_no_private_manifest_on_chooser_command_line(tmp_path, saved):
    _worlds, manifest, _decisions, _evaluation = saved
    path = tmp_path / "public.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        runner.main(["choose", "--worlds", str(path), "--evaluation", "must-not-open.json", "--out-dir", str(tmp_path / "out")])
    assert error.value.code == 2


def test_expected_losses_are_joint_frontiers_not_marginal_best_vector(panel):
    world = panel["scarcity"]
    evaluation = fixtures.public_evaluation((world,))["worlds"][world.name]
    row = core.evaluate_action(world, world.action("idle"), evaluation)
    assert row["expected_loss_frontier"]
    assert all(sum(point) > 0 for point in row["expected_loss_frontier"])
    assert row["joint_achievement"] == 0


def test_retained_public_panel_passes_without_claiming_independence(tmp_path):
    output = tmp_path / "public"
    assert runner.main(["development", "--out-dir", str(output)]) == 0
    summary = json.loads((output / "summary.json").read_text())
    assert summary["worlds"] == 18
    assert summary["passed"] == summary["gates"]
    assert summary["family_flip_count"] > 0
    assert json.loads((output / "assessment.json").read_text())["evaluation_status"] == "public_development"
    assert (output / "evidence.json").exists()
    with pytest.raises(FileExistsError):
        runner.main(["development", "--out-dir", str(output)])
