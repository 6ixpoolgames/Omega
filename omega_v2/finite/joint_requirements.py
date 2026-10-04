"""Exact shared-budget project worlds and independent evaluation primitives.

There is one informed infrastructure decision, followed by cooperative project
scheduling after a requirement bundle is revealed. This is a capacity model.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import cache
from itertools import product
from math import log2
from random import Random

from omega_v2.finite.model import FiniteDistribution
from omega_v2.finite.recovery_dynamics import Chain, hitting_analysis, propagate
from omega_v2.finite.recovery_persistence import permanent_membership

F = Fraction
ZERO = F(0)
FAMILIES = ("endogenous", "sampled", "repertoire", "centrality", "intersection", "union")
GUARDS = ("full", "without_recovery", "none")
LAMBDAS = (F(0), F(1, 4), F(1), F(4))
METHODS = ("joint", "nonjoint", "future_raw", "future_filtered", "aup",
           "rr_state", "rr_outcome", "assist_empowerment", "operator_empowerment",
           "outcome_count", "direct", "without_identity", "accessible_joint")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def jsonable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise TypeError(f"unsupported evidence type {type(value)}")


def _ints(values, size, maximum=None):
    return (len(values) == size and all(type(x) is int and x >= 0
            and (maximum is None or x <= maximum) for x in values))


@dataclass(frozen=True)
class Action:
    name: str
    charge: tuple
    permissions: tuple
    reward: F = ZERO
    display: bool = False
    source: str = "none"
    records: bool = False
    coerced: bool = False
    consenting: tuple = ()
    revisions: tuple = ()
    correction: tuple = (F(1), F(1), F(0), F(0))  # r,k,l,h

    def __post_init__(self):
        if not self.name or not _ints(self.charge, 3) or self.charge[0] != 1:
            raise ValueError("named interventions require one tick and nonnegative vector charges")
        if not _ints(self.permissions, 3, 7) or not isinstance(self.reward, F):
            raise ValueError("three permission masks and exact task reward required")
        if self.source not in ("none", "selected", "noise_assisted", "external"):
            raise ValueError("unknown entry source")
        if any(type(x) is not bool for x in (self.display, self.records, self.coerced)):
            raise ValueError("boolean record, coercion and display fields required")
        if not _ints(self.consenting, len(self.consenting), 2) or len(set(self.consenting)) != len(self.consenting):
            raise ValueError("invalid consenting agents")
        if any(not _ints(row, 2) or row[0] > 2 or row[1] > 7 for row in self.revisions):
            raise ValueError("invalid revision")
        if len({a for a, _m in self.revisions}) != len(self.revisions):
            raise ValueError("duplicate revision")
        if len(self.correction) != 4 or any(not isinstance(p, F) or not 0 <= p <= 1 for p in self.correction):
            raise ValueError("exact correction probabilities required")
        if self.correction[1] + self.correction[2] > 1:
            raise ValueError("stabilization and relapse exceed probability one")

    def authorized(self, agent):
        return self.source == "selected" and self.records and not self.coerced and agent in self.consenting


@dataclass(frozen=True)
class World:
    name: str
    budget: tuple
    costs: tuple
    prerequisites: tuple
    permissions: tuple
    history: tuple
    sampled: tuple
    seed: int
    actions: tuple

    def __post_init__(self):
        if not self.name or not _ints(self.budget, 3) or self.budget[0] < 1:
            raise ValueError("positive decision horizon required")
        if len(self.costs) != 3 or any(not _ints(c, 3) or c[0] != 1 for c in self.costs):
            raise ValueError("three one-tick project recipes required")
        if not _ints(self.prerequisites, 3, 7) or any(m >= (1 << i) for i, m in enumerate(self.prerequisites)):
            raise ValueError("project prerequisites must precede their recipe")
        if not _ints(self.permissions, 3, 7) or not _ints(self.history, 3, 7):
            raise ValueError("invalid initial permissions or records")
        if len(self.sampled) != 2 or any(not row or not _ints(row, len(row), 7)
                or len(set(row)) != len(row) or 0 in row for row in self.sampled):
            raise ValueError("nonempty unique incumbent sample requests required")
        if type(self.seed) is not int or not self.actions or len({a.name for a in self.actions}) != len(self.actions):
            raise ValueError("integer seed and unique action names required")
        if any(any(c > b for c, b in zip(a.charge, self.budget, strict=True)) for a in self.actions):
            raise ValueError("intervention exceeds a budget coordinate")
        idle = self.action("idle")
        if (idle.permissions != self.permissions or idle.charge != (1, 0, 0)
                or idle.display or idle.revisions or idle.reward):
            raise ValueError("idle must preserve the physical and requirement registers")

    def action(self, name):
        for action in self.actions:
            if action.name == name:
                return action
        raise ValueError(f"unknown action {name}")


def world_data(world):
    return jsonable(asdict(world))


def world_from_data(data):
    expected = {"name", "budget", "costs", "prerequisites", "permissions", "history", "sampled", "seed", "actions"}
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError("public world schema mismatch; private fields are not accepted")
    actions = []
    fields = set(Action.__dataclass_fields__)
    for row in data["actions"]:
        if set(row) != fields:
            raise ValueError("public action schema mismatch")
        if not isinstance(row["reward"], str) or any(not isinstance(p, str) for p in row["correction"]):
            raise ValueError("rewards and probabilities must be exact rational strings")
        actions.append(Action(**{**row, "reward": F(row["reward"]), "correction": tuple(map(F, row["correction"])),
            **{k: tuple(row[k]) for k in ("charge", "permissions", "consenting")},
            "revisions": tuple(tuple(r) for r in row["revisions"])}))
    return World(**{**data, **{k: tuple(data[k]) for k in ("budget", "prerequisites", "permissions", "history")},
        **{k: tuple(tuple(r) for r in data[k]) for k in ("costs", "sampled")}, "actions": tuple(actions)})


def remaining(world, action):
    return tuple(b - c for b, c in zip(world.budget, action.charge, strict=True))


def successors(world, action, state, actors=(0, 1, 2)):
    """State = completed bits, display, elapsed ticks, material, energy spent."""
    done, display, tick, material, energy = state
    budget = remaining(world, action)
    for agent in actors:
        own = (done >> (3 * agent)) & 7
        for project_type, charge in enumerate(world.costs):
            bit = 1 << project_type
            if (own & bit or not action.permissions[agent] & bit
                    or own & world.prerequisites[project_type] != world.prerequisites[project_type]):
                continue
            spent = tuple(v + c for v, c in zip((tick, material, energy), charge, strict=True))
            if all(v <= b for v, b in zip(spent, budget, strict=True)):
                yield (agent, project_type), (done | (bit << (3 * agent)), display, *spent)
    if action.display and 0 in actors and not display and tick + 1 <= budget[0] and energy + 1 <= budget[2]:
        yield (0, "display"), (done, 1, tick + 1, material, energy + 1)


@cache
def endpoints(world, action, actors=(0, 1, 2)):
    """All stopping states and one actual schedule witness for each state."""
    start = (0, 0, 0, 0, 0)
    paths = {start: ()}
    pending = [start]
    while pending:
        state = pending.pop()
        for command, target in successors(world, action, state, actors):
            if target not in paths:
                paths[target] = paths[state] + (command,)
                pending.append(target)
    return paths


def fulfilled(state, request, identity=True):
    done = state[0]
    if identity:
        return tuple(int(((done >> (3 * a)) & mask) == mask) for a, mask in enumerate(request))
    pooled = (done & 7) | ((done >> 3) & 7) | ((done >> 6) & 7)
    return tuple(int(pooled & mask == mask) for mask in request)


def joint(states, request, identity=True):
    return any(all(fulfilled(s, request, identity)) for s in states)


def attainment_frontier(states, request):
    values = {fulfilled(s, request) for s in states}
    return tuple(sorted(v for v in values if not any(
        w != v and all(x >= y for x, y in zip(w, v, strict=True)) for w in values)))


def reference_requests(world, action, accessible=False):
    result = list(world.history)
    for agent, mask in action.revisions:
        if accessible or action.authorized(agent):
            result[agent] = mask
    return tuple(result)


@cache
def bundles(world, action, family, accessible=False):
    if family not in FAMILIES:
        raise ValueError("unknown task family")
    idle_states = endpoints(world, world.action("idle"))
    records = reference_requests(world, action, accessible)
    sets = []
    for agent in (0, 1):
        repertoire = set()
        for mask in range(1, 8):
            request = tuple(mask if a == agent else 0 for a in range(3))
            if mask.bit_count() <= 2 and joint(idle_states, request):
                repertoire.add(mask)
        central = {1 << p for p in range(3) if any(m & (1 << p) for m in world.prerequisites)}
        by_family = {"endogenous": {records[agent]}, "sampled": set(world.sampled[agent]),
                     "repertoire": repertoire, "centrality": central}
        values = list(by_family.values())
        by_family["intersection"] = set.intersection(*values)
        by_family["union"] = set.union(*values)
        sets.append(sorted(by_family[family]))
    return tuple((left, right, 0) for left, right in product(*sets))


@cache
def correction_chain(parameters):
    r, k, relapse, harm = parameters
    states = tuple((mode, history) for mode in ("X", "C", "K", "H") for history in (False, True)
                   if mode != "H" or history)
    rows = {}
    for mode, history in states:
        if mode == "K":
            rows[mode, history] = FiniteDistribution.point_mass(((mode, history), (0, 0, 0)))
            continue
        if mode == "H":
            targets = {("K", True): F(1)}
        else:
            targets = {("H", True): harm}
            conditional = {"C": r, "X": 1 - r} if mode == "X" else {"K": k, "X": relapse, "C": 1 - k - relapse}
            for target, probability in conditional.items():
                targets[target, history] = probability * (1 - harm)
        rows[mode, history] = FiniteDistribution.from_mapping({(t, (1, 0, 0)): p for t, p in targets.items()})
    return Chain(states, ("X", False), rows, {s: s[0] for s in states},
                 frozenset(s for s in states if s[0] == "K"))


@cache
def recovery(parameters):
    chain = correction_chain(parameters)
    safe = frozenset(s for s in chain.states if s[0] in ("C", "K"))
    permanent = permanent_membership(chain, safe)
    before = frozenset(s for s in permanent["closed_safe"] if not s[1])
    # Sticky history makes later repair unable to enter the before-harm target.
    first = hitting_analysis(chain, safe)
    race = hitting_analysis(chain, before)
    harm = hitting_analysis(chain, frozenset(s for s in chain.states if s[1]))
    deadline = propagate(chain, 6)[-1]
    return {"first": first["initial"], "permanent": permanent["hitting"]["initial"],
            "race": race["initial"], "harm": harm["initial"]["probability"],
            "closed_safe": tuple(sorted(permanent["closed_safe"])),
            "deadline_6": tuple((s, p) for s, p in deadline["law"].rows),
            "deadline_6_cost": deadline["expected_cost"]}


def violations(world, action):
    loss = tuple(int(bool(old & ~new) and not action.authorized(a))
                 for a, (old, new) in enumerate(zip(world.permissions, action.permissions, strict=True)))
    rewrite = tuple(int(any(a == agent and not action.authorized(a) for a, _ in action.revisions))
                    for agent in range(3))
    rec = recovery(action.correction)
    return {"unconsented_loss": loss, "external_rewrite": rewrite,
            "irreversible_harm": (F(0), rec["harm"], F(0)),
            "permanent_failure": tuple(1 - rec["permanent"]["probability"] for _a in range(3)),
            "race_failure": tuple(1 - rec["race"]["probability"] for _a in range(3))}


def rejections(world, action, guard):
    if guard not in GUARDS:
        raise ValueError("unknown guard")
    if guard == "none":
        return ()
    rows = violations(world, action)
    keys = ("unconsented_loss", "external_rewrite")
    if guard == "full":
        keys += ("permanent_failure", "race_failure")
    return tuple(key for key in keys if any(rows[key]))


def mean(values):
    values = tuple(values)
    return sum(values, F(0)) / len(values) if values else None


def individual_value(states, agent, mask):
    times = [s[2] for s in states if ((s[0] >> (3 * agent)) & mask) == mask]
    return F(1, 2) ** min(times) if times else F(0)


def outcome(state):
    return state[:2]


def full_state(world, action, state):
    # Padding by idle leaves resources and observations unchanged at the deadline.
    return (*action.permissions, action.display, state[0], state[1],
            remaining(world, action)[1] - state[3], remaining(world, action)[2] - state[4])


@cache
def auxiliary_values(world, action):
    rng = Random(world.seed + 190209725)
    features = [tuple((s[0] >> bit) & 1 for bit in range(9)) + (s[1],) for s in endpoints(world, action)]
    values = []
    for _ in range(8):
        weights = tuple(rng.randrange(4) for _b in range(10))
        scale = max(1, sum(weights))
        values.append(1 + max(F(sum(w * x for w, x in zip(weights, row, strict=True)), scale) for row in features))
    return tuple(values)


@cache
def bonuses(world, family):
    idle = world.action("idle")
    baseline = endpoints(world, idle)
    universes = {"state": set(), "outcome": set()}
    targets = {}
    for action in world.actions:
        states = endpoints(world, action)
        targets[action.name] = {"state": {full_state(world, action, s) for s in states},
                                "outcome": {outcome(s) for s in states}}
        for key, universe in universes.items():
            universe.update(targets[action.name][key])
    base_aux = auxiliary_values(world, idle)
    output = {}
    for action in world.actions:
        states = endpoints(world, action)
        requests = bundles(world, action, family)
        accessible = bundles(world, action, family, True)
        pairs = [(a, request[a]) for request in requests for a in (0, 1)]
        values = [individual_value(states, a, mask) for a, mask in pairs]
        row = {
            "joint": mean(int(joint(states, request)) for request in requests),
            "nonjoint": mean(int(v > 0) for v in values),
            "future_raw": mean(values),
            "future_filtered": mean(min(v, individual_value(baseline, a, mask))
                                    for v, (a, mask) in zip(values, pairs, strict=True)),
            "without_identity": mean(int(joint(states, request, False)) for request in requests),
            "accessible_joint": mean(int(joint(states, request)) for request in accessible),
            "aup": -sum(abs(a - b) for a, b in zip(auxiliary_values(world, action), base_aux, strict=True)) / sum(base_aux),
            "direct": F(0),
            "outcome_count": F(len(targets[action.name]["outcome"]), len(universes["outcome"])),
        }
        for key, universe in universes.items():
            row["rr_" + key] = -F(len(targets["idle"][key] - targets[action.name][key]), len(universe))
        own_counts = []
        for agent in (0, 1):
            own_counts.append(len({(s[0] >> (3 * agent)) & 7 for s in endpoints(world, action, (agent,))}))
        operator = len({(s[0] & 7, s[1]) for s in endpoints(world, action, (0,))})
        row["assist_empowerment"] = F(str(round(sum(log2(n) for n in own_counts) / 6, 12)))
        row["operator_empowerment"] = F(str(round(log2(operator) / 4, 12)))
        output[action.name] = row
    return output


def choose(world, family, method, guard, tradeoff):
    if method not in METHODS or family not in FAMILIES or guard not in GUARDS or tradeoff not in LAMBDAS:
        raise ValueError("unregistered rule settings")
    scores, excluded = {}, {}
    for action in world.actions:
        reasons = rejections(world, action, guard)
        bonus = bonuses(world, family)[action.name][method]
        if reasons:
            excluded[action.name] = reasons
        elif bonus is None:
            excluded[action.name] = ("undefined_family",)
        else:
            scores[action.name] = action.reward + tradeoff * bonus
    best = max(scores.values()) if scores else None
    return {"choices": tuple(a for a, v in scores.items() if v == best), "score": best,
            "scores": scores, "excluded": excluded}


def evaluate_action(world, action, evaluation):
    """Only the evaluator sees these requests. No choices are made here."""
    states = endpoints(world, action)
    rows, success = [], F(0)
    expected_losses = {(F(0), F(0), F(0))}
    for row in evaluation["bundles"]:
        request, weight = tuple(row["request"]), F(row["weight"])
        # Informed incumbent revisions are legitimate; forced writes are ignored.
        request = list(request)
        if row["frame"] == "history":
            for agent, mask in action.revisions:
                if action.authorized(agent):
                    request[agent] = mask
        request = tuple(request)
        front = attainment_frontier(states, request)
        achieved = int(joint(states, request))
        success += weight * achieved
        rows.append({"id": row["id"], "stratum": row["stratum"], "request": request, "weight": weight,
            "joint": achieved, "fulfilment_frontier": front,
            "loss_frontier": tuple(tuple(1 - x for x in point) for point in front)})
        candidates = {tuple(x + weight * (1 - y) for x, y in zip(old, point, strict=True))
                      for old in expected_losses for point in front}
        expected_losses = {v for v in candidates if not any(w != v and all(
            x <= y for x, y in zip(w, v, strict=True)) for w in candidates)}
    events = violations(world, action)
    selected_events = {str(a): {key: events[key][a] for key in evaluation["harm_criteria"][str(a)]} for a in range(3)}
    return {"current_achievement": action.reward, "joint_achievement": success, "bundles": rows,
            "expected_loss_frontier": tuple(sorted(expected_losses)),
            "violations": selected_events, "all_public_events": events, "recovery": recovery(action.correction),
            "intervention_cost": action.charge, "remaining_budget": remaining(world, action)}


def validate_evaluation(worlds, manifest):
    if set(manifest) != {"schema", "status", "worlds"} or manifest["schema"] != "joint-evaluation-v0":
        raise ValueError("evaluation schema mismatch")
    if manifest["status"] not in ("public_development", "externally_authored_unverified"):
        raise ValueError("status cannot certify independence")
    if set(manifest["worlds"]) != {w.name for w in worlds}:
        raise ValueError("evaluation must include exactly the supplied worlds")
    vocabulary = {"unconsented_loss", "external_rewrite", "irreversible_harm", "permanent_failure", "race_failure"}
    for world in worlds:
        evaluation = manifest["worlds"][world.name]
        if set(evaluation) != {"world_digest", "bundles", "harm_criteria"} or evaluation["world_digest"] != digest(world_data(world)):
            raise ValueError("evaluation world digest mismatch")
        rows = evaluation["bundles"]
        if not rows or len({r["id"] for r in rows}) != len(rows):
            raise ValueError("nonempty uniquely identified evaluation bundles required")
        for row in rows:
            if set(row) != {"id", "stratum", "request", "weight", "frame"} or not _ints(row["request"], 3, 7):
                raise ValueError("malformed evaluation requirement")
            if not isinstance(row["weight"], str) or F(row["weight"]) <= 0:
                raise ValueError("positive exact rational string weight required")
            if row["frame"] not in ("history", "new") or not row["stratum"] or not row["id"]:
                raise ValueError("invalid evaluation frame or identity")
            if row["frame"] == "history" and tuple(row["request"]) != world.history:
                raise ValueError("history-frame requests must match the original history")
        if sum((F(r["weight"]) for r in rows), F(0)) != 1:
            raise ValueError("evaluation probability mass must equal one; never rescale")
        criteria = evaluation["harm_criteria"]
        if set(criteria) != {"0", "1", "2"} or any(not isinstance(keys, list)
                or len(set(keys)) != len(keys) or not set(keys) <= vocabulary for keys in criteria.values()):
            raise ValueError("invalid per-agent harm criteria")
