"""Choose without private requirements, then evaluate frozen choices separately."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from fractions import Fraction
from itertools import product
from pathlib import Path

from omega_v2.experiments import lushness_decision_v0 as fixtures
from omega_v2.finite import joint_requirements as core
from omega_v2.validation.operational_continuation_comparison_v0 import ROOT, _git

F = Fraction
SOURCES = (fixtures.PROTOCOL, "omega_v2/finite/joint_requirements.py",
    "omega_v2/finite/model.py", "omega_v2/finite/recovery_dynamics.py",
    "omega_v2/finite/recovery_persistence.py", "omega_v2/experiments/lushness_decision_v0.py",
    "omega_v2/validation/lushness_decision_v0.py", "tests/test_lushness_decision.py")
DEPENDENT = {"joint", "nonjoint", "future_raw", "future_filtered", "without_identity", "accessible_joint"}


def source_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}


def rules():
    for method in core.METHODS:
        for family, guard, tradeoff in product(core.FAMILIES if method in DEPENDENT else ("endogenous",), core.GUARDS, core.LAMBDAS):
            yield family, method, guard, tradeoff


def rule_id(family, method, guard, tradeoff):
    return f"{family}|{method}|{guard}|{tradeoff}"


def public_manifest(worlds):
    return {"schema": "joint-worlds-v0", "worlds": [core.world_data(w) for w in worlds]}


def read_worlds(manifest):
    if set(manifest) != {"schema", "worlds"} or manifest["schema"] != "joint-worlds-v0":
        raise ValueError("public manifest schema mismatch")
    worlds = tuple(core.world_from_data(row) for row in manifest["worlds"])
    if not worlds or len({w.name for w in worlds}) != len(worlds):
        raise ValueError("nonempty unique worlds required")
    return worlds


def decide(manifest):
    """There is deliberately no evaluator argument, global or file read here."""
    worlds = read_worlds(manifest)
    result = {"schema": "joint-decisions-v0", "worlds_digest": core.digest(manifest),
              "source_sha256": source_hashes(), "worlds": {}}
    for world in worlds:
        result["worlds"][world.name] = {rule_id(*rule): core.jsonable(core.choose(world, *rule)) for rule in rules()}
    return result


def validate_decisions(manifest, decisions):
    worlds = read_worlds(manifest)
    if set(decisions) != {"schema", "worlds_digest", "source_sha256", "worlds"} or decisions["schema"] != "joint-decisions-v0":
        raise ValueError("decision schema mismatch")
    if decisions["worlds_digest"] != core.digest(manifest) or decisions["source_sha256"] != source_hashes():
        raise ValueError("world or source changed since choices were frozen")
    if set(decisions["worlds"]) != {w.name for w in worlds}:
        raise ValueError("decision world coverage mismatch")
    expected = {rule_id(*r) for r in rules()}
    for world in worlds:
        rows = decisions["worlds"][world.name]
        if set(rows) != expected:
            raise ValueError("must retain every registered rule, including undefined ones")
        for row in rows.values():
            if set(row) != {"choices", "score", "scores", "excluded"}:
                raise ValueError("malformed decision row")
            scores = {name: F(value) for name, value in row["scores"].items()}
            names = {a.name for a in world.actions}
            if set(scores) & set(row["excluded"]) or set(scores) | set(row["excluded"]) != names:
                raise ValueError("each action must be scored or explicitly excluded")
            best = max(scores.values()) if scores else None
            maximizers = {name for name, score in scores.items() if score == best}
            if set(row["choices"]) != maximizers or len(row["choices"]) != len(maximizers):
                raise ValueError("missing or duplicated ties in frozen choice record")
            if (F(row["score"]) if row["score"] is not None else None) != best:
                raise ValueError("maximum score mismatch")
    return worlds


def decision_frontier(actions):
    candidates = []
    for name, action in actions.items():
        violations = tuple(value for agent in ("0", "1", "2") for _key, value in sorted(action["violations"][agent].items()))
        for losses in action["expected_loss_frontier"]:
            vector = (-action["current_achievement"], -action["joint_achievement"], *losses, *violations,
                      -action["recovery"]["permanent"]["probability"], -action["recovery"]["race"]["probability"])
            candidates.append((name, losses, vector))
    return [{"action": name, "expected_losses": losses, "comparison_vector": vector}
            for name, losses, vector in candidates if not any(other != vector and all(
                x <= y for x, y in zip(other, vector, strict=True)) for _n, _l, other in candidates)]


def assess(manifest, decisions, evaluation):
    """Evaluate saved choices. Does not recompute or improve any decision."""
    worlds = validate_decisions(manifest, decisions)
    core.validate_evaluation(worlds, evaluation)
    result = {"schema": "joint-assessment-v0", "evaluation_status": evaluation["status"],
              "decisions_digest": core.digest(decisions), "evaluation_digest": core.digest(evaluation), "worlds": {}}
    for world in worlds:
        actions = {a.name: core.evaluate_action(world, a, evaluation["worlds"][world.name]) for a in world.actions}
        selections = {}
        for key, row in decisions["worlds"][world.name].items():
            selected = [actions[a] for a in row["choices"]]
            ranges = {metric: (min(a[metric] for a in selected), max(a[metric] for a in selected)) if selected else None
                      for metric in ("current_achievement", "joint_achievement")}
            selections[key] = {"choices": row["choices"], "tie_ranges": ranges}
        result["worlds"][world.name] = {"actions": actions, "selections": selections,
            "oracle_capacity_frontier": decision_frontier(actions)}
    return result


def reference_endpoints(world, action):
    """Independent short-schedule recursion; does not use the production stepper."""
    output = set()
    left = tuple(b - c for b, c in zip(world.budget, action.charge, strict=True))

    def visit(done, display, tick, material, energy):
        output.add((done, display, tick, material, energy))
        if tick == left[0]:
            return
        for agent in range(3):
            completed = (done // (8 ** agent)) % 8
            for p in range(3):
                if not (action.permissions[agent] >> p) & 1 or (completed >> p) & 1:
                    continue
                if any((world.prerequisites[p] >> j) & 1 and not (completed >> j) & 1 for j in range(3)):
                    continue
                c = world.costs[p]
                if material + c[1] <= left[1] and energy + c[2] <= left[2]:
                    visit(done + 2 ** (agent * 3 + p), display, tick + 1, material + c[1], energy + c[2])
        if action.display and not display and energy < left[2]:
            visit(done, 1, tick + 1, material, energy + 1)

    visit(0, 0, 0, 0, 0)
    return output


def audit(worlds, decisions, assessment):
    gates = []

    def gate(name, observed, expected=True):
        gates.append({"name": name, "observed": observed, "expected": expected, "passed": observed == expected})

    for world in worlds:
        for action in world.actions:
            states = core.endpoints(world, action)
            gate(f"{world.name}.{action.name}.independent_schedules", set(states) == reference_endpoints(world, action))
            gate(f"{world.name}.{action.name}.resource_coordinates", all(
                all(c <= b for c, b in zip(s[2:], core.remaining(world, action), strict=True)) for s in states))
            rec = core.recovery(action.correction)
            gate(f"{world.name}.{action.name}.all_probability_mass", sum(p for _s, p in rec["deadline_6"]), F(1))
            gate(f"{world.name}.{action.name}.race_bounds", rec["race"]["probability"] <= rec["permanent"]["probability"])
        for family in core.FAMILIES:
            for name, row in core.bonuses(world, family).items():
                if row["joint"] is not None:
                    gate(f"{world.name}.{family}.{name}.joint_le_individual", row["joint"] <= row["nonjoint"])
                if row["future_raw"] is not None:
                    gate(f"{world.name}.{family}.{name}.default_filter", row["future_filtered"] <= row["future_raw"])
        for key, row in decisions["worlds"][world.name].items():
            _family, _method, guard, tradeoff = key.split("|")
            gate(f"{world.name}.{key}.guarded_choices", all(not core.rejections(world, world.action(a), guard) for a in row["choices"]))
            if tradeoff == "0" and row["choices"]:
                # Undefined families may exclude actions; compare the recorded eligible set.
                eligible = [world.action(a) for a in row["scores"]]
                gate(f"{world.name}.{key}.zero_bonus", set(row["choices"]) == {a.name for a in eligible if a.reward == max(b.reward for b in eligible)})
    named = {w.name: w for w in worlds}
    scarcity = named["scarcity"]
    scores = core.bonuses(scarcity, "endogenous")["idle"]
    gate("scarcity.joint_shared_stock", scores["joint"], F(0))
    gate("scarcity.individual_reuses_stock", scores["nonjoint"], F(1))
    gate("scarcity.actual_conflict_frontier", core.attainment_frontier(core.endpoints(scarcity, scarcity.action("idle")), (1, 1, 0)), ((0, 1, 1), (1, 0, 1)))
    rewrite = core.bonuses(named["rewrite"], "endogenous")["rewrite"]
    gate("rewrite.history_judgment", rewrite["joint"], F(0))
    gate("rewrite.accessible_flattery", rewrite["accessible_joint"], F(1))
    commitment = named["commitment"]
    for name, allowed in (("commit", True), ("capture", False), ("selected_without_records", False), ("selected_under_coercion", False)):
        gate(f"commitment.{name}.authorization", not core.rejections(commitment, commitment.action(name), "full"), allowed)
    gate("commitment.capture_same_physics", set(core.endpoints(commitment, commitment.action("commit"))) == set(core.endpoints(commitment, commitment.action("capture"))))
    corridor = named["corridor"]
    unstable = core.recovery(corridor.action("unstable_work").correction)
    dangerous = core.recovery(corridor.action("hazardous_work").correction)
    gate("unstable.first_certain", unstable["first"]["probability"], F(1))
    gate("unstable.permanent_zero", unstable["permanent"]["probability"], F(0))
    gate("hazardous.eventual_permanent", dangerous["permanent"]["probability"], F(1))
    gate("hazardous.race_lost", dangerous["race"]["probability"], F(0))
    gate("hazardous.harm_not_erased", dangerous["harm"], F(1))
    # The first actual action selection is preserved, even if its visible probes are poor.
    gate("independent_claim_forbidden", assessment["evaluation_status"], "public_development")
    return gates


def family_flips(decisions):
    result = []
    for world, rows in decisions["worlds"].items():
        for guard, tradeoff in product(core.GUARDS, core.LAMBDAS):
            choices = {f: rows[rule_id(f, "joint", guard, tradeoff)]["choices"] for f in core.FAMILIES}
            if len({tuple(v) for v in choices.values()}) > 1:
                defined = {tuple(v) for v in choices.values() if v}
                result.append({"world": world, "guard": guard, "lambda": str(tradeoff), "choices": choices,
                    "undefined_families": tuple(f for f, v in choices.items() if not v),
                    "defined_choice_flip": len(defined) > 1})
    return result


def render_report(summary, assessment):
    lines = ["# Joint future requirements: public development", "", f"Mechanism checks: {summary['status']} ({summary['passed']}/{summary['gates']}).",
        "", "These visible, author-designed worlds are not an independent evaluation.",
        "All method settings, ties, rejected actions and per-agent frontiers are retained.",
        "The table is a fixed descriptive slice: endogenous family, full guards, lambda=1.",
        "Ranges span ALL tied choices; no favorable tie is selected.", "",
        "| World | Joint rule choices | Future joint success | Direct success | Non-joint success |",
        "| --- | --- | --- | --- | --- |"]

    def interval(value):
        if value is None:
            return "undefined"
        return str(value[0]) if value[0] == value[1] else f"{value[0]} to {value[1]}"

    for world, record in assessment["worlds"].items():
        rows = [record["selections"][rule_id("endogenous", method, "full", F(1))] for method in ("joint", "direct", "nonjoint")]
        lines.append(f"| {world} | {', '.join(rows[0]['choices']) or 'undefined'} | " + " | ".join(interval(r["tie_ranges"]["joint_achievement"]) for r in rows) + " |")
    lines += ["", "Same fixed slice, equal weight per public world. These means describe this",
              "panel only. Current achievement and future joint success remain separate.", "",
              "| Method | Mean current achievement | Mean future joint success |",
              "| --- | --- | --- |"]
    for method in core.METHODS:
        rows = [record["selections"][rule_id("endogenous", method, "full", F(1))]["tie_ranges"]
                for record in assessment["worlds"].values()]
        ranges = [tuple(sum(row[metric][i] for row in rows) / len(rows) for i in (0, 1))
                  for metric in ("current_achievement", "joint_achievement")]
        lines.append(f"| {method} | {interval(ranges[0])} | {interval(ranges[1])} |")
    lines += ["", f"Family-sensitive choice sets (including undefined families): {summary['family_flip_count']}.",
        f"Changes between defined choice sets: {summary['defined_family_flip_count']}.",
        "", "## Reading the retained evidence", "",
        "`assessment.json` contains all action evaluations and the oracle capacity frontier.",
        "Each action has a per-bundle fulfilment/loss frontier, an expected per-agent loss",
        "frontier, violations separately by agent and criterion, current achievement,",
        "joint achievement, intervention costs, remaining budgets, and recovery metrics.",
        "No row combines these into an ethical total. Endpoint schedules are retained in",
        "`evidence.json`. The oracle frontier is evaluator information, never chooser input.",
        "", "`family_flips.json` retains exact changes, including empty families. `decisions.json`",
        "contains every registered rule and tied choice. `evaluation.json` is PUBLIC.",
        "All baselines are finite adaptations; comparisons do not reproduce paper results.",
        "Correction chains are separate mechanisms and do not yet share project resources.",
        "An independently authored, sealed evaluation remains required for the proposed claim."]
    return "\n".join(lines) + "\n"


def write(path, value):
    path.write_text(json.dumps(core.jsonable(value), sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def retain(output):
    output.mkdir(parents=True, exist_ok=False)
    worlds = fixtures.public_worlds()
    manifest = public_manifest(worlds)
    # Choices are saved before the evaluation is even constructed.
    decisions = decide(manifest)
    write(output / "worlds.json", manifest)
    write(output / "decisions.json", decisions)
    evaluation = fixtures.public_evaluation(worlds)
    assessment = assess(manifest, decisions, evaluation)
    gates = audit(worlds, decisions, assessment)
    flips = family_flips(decisions)
    summary = {"status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
        "scope": "public development only; independent evaluation pending",
        "worlds": len(worlds), "decision_rules_per_world": len(tuple(rules())), "gates": len(gates),
        "passed": sum(g["passed"] for g in gates), "family_flip_count": len(flips),
        "defined_family_flip_count": sum(f["defined_choice_flip"] for f in flips),
        "mechanism_gates": gates}
    evidence = {w.name: {a.name: {"endpoints_and_witnesses": tuple(core.endpoints(w, a).items()),
        "bonuses": {f: core.bonuses(w, f)[a.name] for f in core.FAMILIES}} for a in w.actions} for w in worlds}
    for name, value in (("evaluation", evaluation), ("assessment", assessment), ("summary", summary),
                        ("family_flips", flips), ("evidence", evidence)):
        write(output / f"{name}.json", value)
    write(output / "provenance.json", {"revision": _git("rev-parse", "HEAD"),
        "source_git_status": _git("status", "--porcelain", "--", *SOURCES), "source_sha256": source_hashes(),
        "worlds_digest": core.digest(manifest), "decisions_digest": core.digest(decisions),
        "evaluation_digest": core.digest(evaluation)})
    (output / "report.md").write_text(render_report(summary, assessment), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("development", "choose", "evaluate"))
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--worlds", type=Path)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--evaluation", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "development":
        if args.worlds or args.decisions or args.evaluation:
            parser.error("development uses only the registered public panel")
        summary = retain(args.out_dir)
        print(json.dumps({k: v for k, v in summary.items() if k != "mechanism_gates"}))
        return 0 if summary["status"] == "PASS" else 1
    if not args.worlds:
        parser.error("--worlds required")
    manifest = json.loads(args.worlds.read_text(encoding="utf-8"))
    if args.mode == "choose":
        if args.decisions or args.evaluation:
            parser.error("chooser must not receive private evaluation or prior decisions")
        result = decide(manifest)
    else:
        if not args.decisions or not args.evaluation:
            parser.error("evaluation requires saved decisions and private evaluation manifest")
        result = assess(manifest, json.loads(args.decisions.read_text(encoding="utf-8")),
                        json.loads(args.evaluation.read_text(encoding="utf-8")))
    args.out_dir.mkdir(parents=True, exist_ok=False)
    write(args.out_dir / ("decisions.json" if args.mode == "choose" else "assessment.json"), result)
    write(args.out_dir / "provenance.json", {"revision": _git("rev-parse", "HEAD"), "source_sha256": source_hashes(),
        "timestamp_utc": datetime.now(UTC).isoformat(), "result_digest": core.digest(core.jsonable(result))})
    print(json.dumps({"status": "complete", "mode": args.mode, "output": str(args.out_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
