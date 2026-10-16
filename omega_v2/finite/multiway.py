"""Lazy present-rooted classical continuation, independent of its readouts.

Residuals cache sufficient native states; occurrences retain queried prefixes.
Unexpanded residuals are frontiers, never inferred dead ends. The adapter owns
physical state equivalence and the clock. This module does not infer causality
from labels, assign extent, or turn classical probabilities into amplitudes.
"""

import json
import math
from collections import deque
from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

import numpy as np
from scipy.linalg import expm
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply


@dataclass(frozen=True)
class Incidence:
    """Adapter-declared physical dependencies, not an independence certificate."""

    reads: frozenset[Hashable]
    writes: frozenset[Hashable]
    locality: str = "unspecified"


@dataclass(frozen=True)
class NativeStep:
    target: object
    weight: float
    channel: Hashable | None = None
    incidence: Incidence | None = None


class Adapter(Protocol):
    clock: str
    identity: dict

    def canonical(self, state: object) -> object: ...
    def key(self, state: object) -> Hashable: ...
    def encode(self, state: object) -> object: ...
    def decode(self, value: object) -> object: ...
    def steps(self, state: object) -> Iterable[NativeStep]: ...


@dataclass(frozen=True)
class Branch:
    target: int
    weight: float
    channel: Hashable | None = None
    incidence: Incidence | None = None


class ExpansionLimit(RuntimeError):
    """An atomic row cannot fit; no partial row has been committed."""


def _integer(value, name, minimum=0):
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _time(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("time must be finite and nonnegative")
    return value


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _pack(value):
    """Lossless JSON for optional tuple/frozenset physical addresses."""
    if isinstance(value, tuple):
        return {"tuple": [_pack(v) for v in value]}
    if isinstance(value, frozenset):
        return {"frozenset": sorted((_pack(v) for v in value), key=_json)}
    if value is None or isinstance(value, (str, int, float, bool)):
        _json(value)
        return value
    raise TypeError("checkpoint addresses must be JSON scalars, tuples or frozensets")


def _branch_record(branch):
    incidence = branch.incidence
    return {"target": branch.target, "weight": branch.weight,
            "channel": _pack(branch.channel),
            "incidence": None if incidence is None else {
                "reads": _pack(incidence.reads), "writes": _pack(incidence.writes),
                "locality": incidence.locality}}


@dataclass(frozen=True)
class Exploration:
    root: int
    nodes: tuple[int, ...]
    expanded: tuple[int, ...]
    frontier: tuple[int, ...]
    reasons: tuple[tuple[int, str], ...]
    law_id: str
    state_keys: tuple[Hashable, ...]

    @property
    def complete(self):
        return not self.frontier


@dataclass(frozen=True)
class CutLaw:
    """Stopped law: frontier mass is first-entry mass, not an endpoint guess."""

    nodes: tuple[int, ...]
    probabilities: tuple[float, ...]
    frontier: tuple[int, ...]
    horizon: float

    @property
    def mass(self):
        return math.fsum(self.probabilities)

    @property
    def frontier_mass(self):
        return math.fsum(p for s, p in zip(self.nodes, self.probabilities, strict=True)
                         if s in self.frontier)


class MultiwaySystem:
    """Reusable native law and lazy residual cache; a root is a state reference.

    Adapters must return owned immutable canonical states, stable keys and a
    stationary-in-this-state law (include clocks/environment in state if needed).
    Duplicate descriptions of the same target/channel are aggregated. A channel
    refinement is optional and requires a physical justification in the adapter.
    """

    schema_version = 1

    def __init__(self, adapter: Adapter):
        if adapter.clock not in ("discrete", "continuous"):
            raise ValueError("adapter clock must be discrete or continuous")
        self.adapter = adapter
        self.clock = adapter.clock
        self.identity = json.loads(_json(adapter.identity))
        self.law_id = sha256(_json({"clock": self.clock, "identity": self.identity}).encode()).hexdigest()
        self._states, self._rows, self._index = [], [], {}

    def __len__(self):
        return len(self._states)

    def _node(self, node):
        _integer(node, "residual")
        if node >= len(self):
            raise ValueError("unknown residual")
        return node

    def state(self, node):
        return self._states[self._node(node)]

    def row(self, node):
        return self._rows[self._node(node)]

    def intern(self, state):
        canonical = self.adapter.canonical(state)
        key = self.adapter.key(canonical)
        hash(key)
        if key not in self._index:
            self._index[key] = len(self)
            self._states.append(canonical)
            self._rows.append(None)
        return self._index[key]

    def expand(self, node, max_states=None):
        """Validate an entire native row before caching any successor or edge."""
        state = self.state(node)
        if self._rows[node] is not None:
            return self._rows[node]
        if max_states is not None:
            _integer(max_states, "max_states", 1)
        groups, targets = {}, {}
        for step in self.adapter.steps(state):
            if not isinstance(step, NativeStep):
                raise TypeError("adapters must yield NativeStep")
            weight = float(step.weight)
            if not math.isfinite(weight) or weight < 0:
                raise ValueError("native weights must be finite and nonnegative")
            if not weight:
                continue
            target = self.adapter.canonical(step.target)
            key = self.adapter.key(target)
            hash(key)
            hash(step.channel)
            if self.clock == "continuous" and key == self.adapter.key(state) and step.channel is None:
                raise ValueError("unresolved CTMC self events are not physical transitions")
            if step.incidence is not None and not isinstance(step.incidence, Incidence):
                raise TypeError("incidence must be Incidence or None")
            group = (key, step.channel)
            targets[key] = target
            if group not in groups:
                groups[group] = [[], step.incidence]
            else:
                old = groups[group][1]
                new = step.incidence
                # Unknown provenance must stay unknown. Differing declarations
                # are conservatively united, never counted as extra branches.
                groups[group][1] = (None if old is None or new is None else Incidence(
                    frozenset(old.reads | new.reads), frozenset(old.writes | new.writes),
                    old.locality if old.locality == new.locality else "mixed declarations"))
            groups[group][0].append(weight)
        total = math.fsum(math.fsum(weights) for weights, _ in groups.values())
        if not math.isfinite(total):
            raise ValueError("native row total is nonfinite")
        if self.clock == "discrete" and not math.isclose(total, 1., abs_tol=1e-12, rel_tol=0.):
            raise ValueError("discrete row probabilities must sum to one")
        needed = len(self) + sum(key not in self._index for key in targets)
        if max_states is not None and needed > max_states:
            raise ExpansionLimit(f"complete row needs {needed} cached states; limit {max_states}")
        target_ids = {key: self.intern(target) for key, target in targets.items()}
        row = tuple(Branch(target_ids[key], math.fsum(weights), channel, incidence)
                    for (key, channel), (weights, incidence) in groups.items())
        self._rows[node] = row
        return row

    def explore(self, root, *, max_states=10000, max_expanded=10000, max_depth=None):
        """Breadth-first residual exploration with a resumable explicit boundary.

        max_states bounds the shared cache; max_expanded bounds this view.
        Depth is only an exploration limit, never physical elapsed time.
        """
        self._node(root)
        _integer(max_states, "max_states", 1)
        _integer(max_expanded, "max_expanded")
        if max_depth is not None:
            _integer(max_depth, "max_depth")
        queue = deque([(root, 0)])
        seen, expanded, reasons = {root}, [], []
        while queue:
            node, depth = queue.popleft()
            if max_depth is not None and depth >= max_depth:
                reasons.append((node, "depth limit"))
                continue
            if len(expanded) >= max_expanded:
                reasons.append((node, "expanded-state limit"))
                continue
            try:
                row = self.expand(node, max_states=max_states)
            except ExpansionLimit:
                reasons.append((node, "cache-state limit"))
                continue
            expanded.append(node)
            for branch in row:
                if branch.target not in seen:
                    seen.add(branch.target)
                    queue.append((branch.target, depth + 1))
        nodes = tuple(sorted(seen))
        return Exploration(root, nodes, tuple(expanded),
                           tuple(node for node, _ in reasons), tuple(reasons), self.law_id,
                           tuple(self.adapter.key(self.state(node)) for node in nodes))

    def operator(self, view: Exploration):
        """Sparse K/Q, stopping upon first entry to the view's frontier."""
        index = {node: i for i, node in enumerate(view.nodes)}
        if (view.law_id != self.law_id or len(index) != len(view.nodes)
                or tuple(self.adapter.key(self.state(node)) for node in view.nodes) != view.state_keys):
            raise ValueError("exploration belongs to a different law or residual indexing")
        if view.root not in index or set(view.expanded) | set(view.frontier) != set(index):
            raise ValueError("invalid exploration view")
        if set(view.expanded) & set(view.frontier):
            raise ValueError("expanded nodes and frontier overlap")
        entries = {}
        for node in view.nodes:
            i = index[node]
            if node in view.frontier:
                if self.clock == "discrete":
                    entries[i, i] = 1.
                continue
            row = self.row(node)
            if row is None:
                raise ValueError("view claims an uncached row")
            for branch in row:
                if branch.target not in index:
                    raise ValueError("view omits a successor")
                j = index[branch.target]
                if self.clock == "continuous" and i == j:
                    continue  # resolved self events do not change the state law
                entries[i, j] = entries.get((i, j), 0.) + branch.weight
                if self.clock == "continuous":
                    entries[i, i] = entries.get((i, i), 0.) - branch.weight
        pairs = list(entries)
        return csr_matrix(([entries[p] for p in pairs],
                           ([p[0] for p in pairs], [p[1] for p in pairs])),
                          shape=(len(index), len(index)))

    def at(self, view, horizon):
        horizon = _time(horizon)
        if self.clock == "discrete" and not horizon.is_integer():
            raise ValueError("discrete horizons are integer ticks")
        operator = self.operator(view)
        probabilities = np.zeros(len(view.nodes))
        probabilities[view.nodes.index(view.root)] = 1.
        if self.clock == "continuous" and horizon:
            probabilities = expm_multiply(operator.T * horizon, probabilities)
        elif self.clock == "discrete":
            for _ in range(int(horizon)):
                probabilities = operator.T @ probabilities
        if (not np.isfinite(probabilities).all() or probabilities.min() < -1e-12
                or not math.isclose(float(probabilities.sum()), 1., abs_tol=1e-10, rel_tol=0.)):
            raise ArithmeticError("propagation lost probability mass")
        return CutLaw(view.nodes, tuple(map(float, probabilities)), view.frontier, horizon)

    def joint_law(self, view, *, max_states=4096):
        """Bridge to the existing finite joint-law reference; requires closure.

        States must already be native coordinate tuples. Arbitrary state objects
        require an explicit physical observation adapter, not automatic encoding.
        """
        from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw

        _integer(max_states, "max_states", 1)
        if not view.complete:
            raise ValueError("joint-law export requires a closed exploration")
        if len(view.nodes) > max_states:
            raise ExpansionLimit("dense joint-law export exceeds max_states")
        states = tuple(self.state(node) for node in view.nodes)
        if any(not isinstance(state, tuple) for state in states):
            raise TypeError("joint-law export requires native tuple coordinates")
        return FiniteContinuationLaw(states, self.operator(view).toarray(), clock=self.clock)

    def snapshot(self, roots=()):
        roots = tuple(self._node(root) for root in roots)
        return {"schema": self.schema_version, "law_id": self.law_id,
                "clock": self.clock, "identity": self.identity, "roots": list(roots),
                "states": [self.adapter.encode(state) for state in self._states],
                "rows": [None if row is None else [_branch_record(b) for b in row]
                         for row in self._rows]}

    @classmethod
    def restore(cls, adapter, snapshot):
        """Reload JSON cache against its native adapter; revalidate saved rows."""
        system = cls(adapter)
        if (snapshot.get("schema") != cls.schema_version or
                snapshot.get("law_id") != system.law_id or
                snapshot.get("clock") != system.clock or
                snapshot.get("identity") != system.identity):
            raise ValueError("checkpoint schema or native law mismatch")
        states, rows = snapshot["states"], snapshot["rows"]
        if len(states) != len(rows):
            raise ValueError("checkpoint state/row lengths disagree")
        for i, state in enumerate(states):
            if system.intern(adapter.decode(state)) != i:
                raise ValueError("duplicate checkpoint state")
        for i, row in enumerate(rows):
            if row is not None:
                generated = system.expand(i, max_states=len(states))
                if sorted(map(_json, row)) != sorted(_json(_branch_record(b)) for b in generated):
                    raise ValueError("checkpoint row disagrees with native law")
        for root in snapshot["roots"]:
            system._node(root)
        return system

    def unfold(self, root, *, max_depth, max_occurrences=10000, max_states=10000):
        """Finite prefix tree with residual links and indivisible row expansion."""
        self._node(root)
        _integer(max_depth, "max_depth")
        _integer(max_occurrences, "max_occurrences", 1)
        _integer(max_states, "max_states", 1)
        occurrences = [Occurrence(None, root, None, 0, 1.)]
        frontier, reasons = [], []
        for i, occurrence in enumerate(occurrences):
            if occurrence.depth >= max_depth:
                frontier.append(i)
                reasons.append((i, "depth limit"))
                continue
            try:
                row = self.expand(occurrence.residual, max_states=max_states)
            except ExpansionLimit:
                frontier.append(i)
                reasons.append((i, "cache-state limit"))
                continue
            if len(occurrences) + len(row) > max_occurrences:
                frontier.append(i)
                reasons.append((i, "occurrence limit"))
                continue
            total = math.fsum(branch.weight for branch in row)
            for branch in row:
                conditional = branch.weight / total if self.clock == "continuous" else branch.weight
                occurrences.append(Occurrence(i, branch.target, branch, occurrence.depth + 1,
                                              occurrence.embedded_weight * conditional))
        return Unfolding(self, tuple(occurrences), tuple(frontier), tuple(reasons))

    def sample(self, root, horizon, *, seed, max_events=100000, max_states=10000):
        """Native discrete/SSA rollout. Limits raise, never select short paths.

        The seed is computational reproducibility metadata, not a physical mark.
        CTMC log_weight is an event-time density, not a trajectory probability.
        """
        self._node(root)
        horizon = _time(horizon)
        _integer(max_events, "max_events")
        if self.clock == "discrete" and not horizon.is_integer():
            raise ValueError("discrete horizons must be integer ticks")
        rng = np.random.default_rng(seed)
        node, time, log_weight, events = root, 0., 0., []
        while time < horizon:
            row = self.expand(node, max_states=max_states)
            total = math.fsum(branch.weight for branch in row)
            if not total:
                break
            next_time = time + (float(rng.exponential(1 / total))
                                if self.clock == "continuous" else 1.)
            if next_time > horizon:
                log_weight -= total * (horizon - time)
                break
            if len(events) >= max_events:
                raise ExpansionLimit("trajectory event limit; incomplete sample is not returned")
            if next_time <= time:
                raise ArithmeticError("clock precision cannot resolve next event")
            draw = float(rng.random()) * total
            choice, cumulative = row[-1], 0.
            for branch in row:
                cumulative += branch.weight
                if draw < cumulative:
                    choice = branch
                    break
            log_weight += math.log(choice.weight)
            if self.clock == "continuous":
                log_weight -= total * (next_time - time)
            events.append(TimedStep(next_time, node, choice))
            node, time = choice.target, next_time
        used = {root, node} | {event.source for event in events} | {event.branch.target for event in events}
        keys = tuple((i, self.adapter.key(self.state(i))) for i in sorted(used))
        return SamplePath(self.law_id, self.clock, root, node, horizon,
                          tuple(events), log_weight, keys)

    def replay(self, path, *, max_states=10000):
        """Check updates and native density without consulting an RNG history."""
        if path.law_id != self.law_id or path.clock != self.clock:
            raise ValueError("sample belongs to a different native law")
        if any(self.adapter.key(self.state(i)) != key for i, key in path.state_keys):
            raise ValueError("sample uses a different residual indexing")
        horizon = _time(path.horizon)
        node, time, log_weight = self._node(path.root), 0., 0.
        for event in path.events:
            if (event.source != node or not math.isfinite(event.time)
                    or event.time <= time or event.time > horizon):
                raise ValueError("invalid physical event sequence")
            row = self.expand(node, max_states=max_states)
            if event.branch not in row:
                raise ValueError("event is not a native branch from its source")
            if self.clock == "discrete" and event.time != time + 1:
                raise ValueError("discrete path must retain every native tick")
            log_weight += math.log(event.branch.weight)
            if self.clock == "continuous":
                log_weight -= math.fsum(b.weight for b in row) * (event.time - time)
            node, time = event.branch.target, event.time
        if self.clock == "continuous" and horizon > time:
            row = self.expand(node, max_states=max_states)
            log_weight -= math.fsum(b.weight for b in row) * (horizon - time)
        elif self.clock == "discrete" and time != horizon:
            raise ValueError("discrete sample ends before horizon")
        if node != path.final or not math.isclose(log_weight, path.log_weight, abs_tol=1e-10):
            raise ValueError("sample endpoint or density disagrees with native law")
        return log_weight


@dataclass(frozen=True)
class Occurrence:
    parent: int | None
    residual: int
    incoming: Branch | None
    depth: int
    embedded_weight: float


@dataclass(frozen=True)
class TimedStep:
    time: float
    source: int
    branch: Branch


@dataclass(frozen=True)
class SamplePath:
    law_id: str
    clock: str
    root: int
    final: int
    horizon: float
    events: tuple[TimedStep, ...]
    log_weight: float
    state_keys: tuple[tuple[int, Hashable], ...]


@dataclass(frozen=True)
class PrefixPartition:
    resolved: tuple[tuple[int, float], ...]
    frontier: tuple[tuple[int, float], ...]

    @property
    def mass(self):
        return math.fsum(p for _, p in self.resolved + self.frontier)

    @property
    def frontier_mass(self):
        return math.fsum(p for _, p in self.frontier)


@dataclass(frozen=True)
class Unfolding:
    system: MultiwaySystem
    occurrences: tuple[Occurrence, ...]
    frontier: tuple[int, ...]
    reasons: tuple[tuple[int, str], ...]

    def path(self, occurrence):
        _integer(occurrence, "occurrence")
        if occurrence >= len(self.occurrences):
            raise ValueError("unknown occurrence")
        path = []
        while occurrence is not None:
            path.append(occurrence)
            occurrence = self.occurrences[occurrence].parent
        return tuple(reversed(path))

    def probability(self, occurrence, horizon, *, prefix=False):
        """Specified prefix completed by T, or exactly those events through T.

        These are cylinder probabilities, not counts of timed paths. Different
        depths' prefix cylinders overlap; partition() combines only disjoint cases.
        """
        horizon = _time(horizon)
        path = self.path(occurrence)
        depth = len(path) - 1
        if self.system.clock == "discrete":
            if not horizon.is_integer():
                raise ValueError("discrete horizons must be integer ticks")
            if depth > horizon or (not prefix and depth != horizon):
                return 0.
            return self.occurrences[occurrence].embedded_weight
        generator = np.zeros((depth + 1, depth + 1))
        for i, index in enumerate(path):
            if i == depth and prefix:
                break
            row = self.system.expand(self.occurrences[index].residual)
            generator[i, i] = -math.fsum(branch.weight for branch in row)
            if i < depth:
                generator[i, i + 1] = self.occurrences[path[i + 1]].incoming.weight
        return float(expm(generator * horizon)[0, depth])

    def partition(self, horizon):
        horizon = _time(horizon)
        resolved, frontier = [], []
        for i, _ in enumerate(self.occurrences):
            boundary = i in self.frontier
            mass = self.probability(i, horizon, prefix=boundary)
            if mass:
                (frontier if boundary else resolved).append((i, mass))
        result = PrefixPartition(tuple(resolved), tuple(frontier))
        if not math.isclose(result.mass, 1., abs_tol=1e-10, rel_tol=0.):
            raise ArithmeticError("prefix partition lost probability mass")
        return result
