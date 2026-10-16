"""Adapters from existing classical laws to the reusable multiway core.

Native states and weights are kept at their declared physical resolution. Event
names are not synthesized: unresolved channels remain ``None``.
"""

from __future__ import annotations

import inspect
from collections.abc import Hashable
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
from itertools import product
from pathlib import Path

import numpy as np

from omega_v2.finite.lattice_chemistry import LatticeChemistry, State
from omega_v2.finite.lattice_compartment import CompartmentChemistry, LocalState
from omega_v2.finite.lattice_history_atlas import canonical_state, rule_dependencies
from omega_v2.finite.multiway import Incidence, NativeStep
from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw


def _json_value(value):
    """Convert supported native scalar/tuple values to JSON without pickle."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("JSON object keys must be strings")
        return {key: _json_value(item) for key, item in value.items()}
    raise TypeError(f"Unsupported JSON state value: {type(value).__name__}")


def _tuple_tree(value):
    """Restore JSON arrays as immutable native tuples."""
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuple_tree(item) for key, item in value.items()}
    return value


def _prefix_incidence(index: int, incidence: Incidence | None) -> Incidence | None:
    if incidence is None:
        return None
    return Incidence(
        frozenset((index, item) for item in incidence.reads),
        frozenset((index, item) for item in incidence.writes),
        incidence.locality,
    )


def _prefix_channel(index: int, channel: Hashable | None) -> Hashable | None:
    return None if channel is None else ("component", index, channel)


class TableAdapter:
    """Expose a finite native K or Q row-by-row, ignoring preparation metadata."""

    def __init__(self, law: FiniteContinuationLaw):
        if not isinstance(law, FiniteContinuationLaw):
            raise TypeError("law must be a FiniteContinuationLaw")
        self.law = law
        self.clock = law.clock
        self._index = {state: i for i, state in enumerate(law.states)}

    @classmethod
    def from_device(cls, device) -> TableAdapter:
        """Adapt only a device's complete transition rows, never its initial mix."""
        return cls(FiniteContinuationLaw.from_device(device))

    @property
    def identity(self) -> dict:
        return {
            "type": "finite-continuation-table",
            "schema": 1,
            "clock": self.clock,
            "states": _json_value(self.law.states),
            "operator": self.law.operator.tolist(),
        }

    def canonical(self, state):
        native = tuple(state)
        if native not in self._index:
            raise ValueError("state must be a declared native state")
        return native

    def key(self, state):
        return self.canonical(state)

    def encode(self, state):
        return _json_value(self.canonical(state))

    def decode(self, value):
        return self.canonical(_tuple_tree(value))

    def steps(self, state):
        source = self._index[self.canonical(state)]
        row = self.law.operator[source]
        for target_index, weight in enumerate(row):
            weight = float(weight)
            if self.clock == "continuous":
                # A generator diagonal is holding/escape bookkeeping, not an
                # event. Zero and self transitions do not create event branches.
                if target_index == source or weight <= 0.0:
                    continue
            elif weight <= 0.0:
                continue
            yield NativeStep(self.law.states[target_index], weight)


class ProductAdapter:
    """Compose component laws without serializing synchronous updates.

    A discrete step is one simultaneous tuple of component outcomes. A
    continuous step changes exactly one component, as for a Kronecker sum.
    Component indices namespace supplied incidences/channels; they do not
    create an event identity when the component supplied none.
    """

    def __init__(self, adapters):
        self.adapters = tuple(adapters)
        if len(self.adapters) < 2:
            raise ValueError("ProductAdapter needs at least two component adapters")
        if any(getattr(adapter, "clock", None) not in ("discrete", "continuous")
               for adapter in self.adapters):
            raise ValueError("every component must declare a supported clock")
        clocks = {adapter.clock for adapter in self.adapters}
        if len(clocks) != 1:
            raise ValueError("product components must use the same clock")
        self.clock = clocks.pop()

    @property
    def identity(self) -> dict:
        return {
            "type": "classical-product",
            "schema": 1,
            "clock": self.clock,
            "components": [_json_value(adapter.identity) for adapter in self.adapters],
        }

    def canonical(self, state):
        state = tuple(state)
        if len(state) != len(self.adapters):
            raise ValueError("product state must have one state per component")
        return tuple(adapter.canonical(part) for adapter, part in zip(
            self.adapters, state, strict=True))

    def key(self, state):
        state = self.canonical(state)
        return tuple(adapter.key(part) for adapter, part in zip(
            self.adapters, state, strict=True))

    def encode(self, state):
        state = self.canonical(state)
        return {"components": [adapter.encode(part) for adapter, part in zip(
            self.adapters, state, strict=True)]}

    def decode(self, value):
        if not isinstance(value, dict) or set(value) != {"components"}:
            raise ValueError("encoded product state must contain components")
        parts = value["components"]
        if len(parts) != len(self.adapters):
            raise ValueError("encoded product has the wrong component count")
        return self.canonical(tuple(adapter.decode(part) for adapter, part in zip(
            self.adapters, parts, strict=True)))

    @staticmethod
    def _bundle(parts):
        supplied = [(i, step) for i, step in parts if step.channel is not None]
        channels = tuple(_prefix_channel(i, step.channel) for i, step in supplied)
        channel = channels[0] if len(channels) == 1 else (channels or None)
        incidences = [(i, step.incidence) for i, step in parts if step.incidence is not None]
        incidence = None
        if len(incidences) == len(parts):
            reads = frozenset((i, item) for i, inc in incidences for item in inc.reads)
            writes = frozenset((i, item) for i, inc in incidences for item in inc.writes)
            # A combined locality label would overstate what the parts establish.
            localities = {inc.locality for _, inc in incidences}
            locality = localities.pop() if len(localities) == 1 else "unspecified"
            incidence = Incidence(reads, writes, locality)
        return channel, incidence

    def steps(self, state):
        state = self.canonical(state)
        if self.clock == "continuous":
            for i, (adapter, part) in enumerate(zip(self.adapters, state, strict=True)):
                for step in adapter.steps(part):
                    target = list(state)
                    target[i] = adapter.canonical(step.target)
                    channel = _prefix_channel(i, step.channel)
                    incidence = _prefix_incidence(i, step.incidence)
                    yield NativeStep(tuple(target), step.weight, channel, incidence)
            return

        component_rows = [tuple(adapter.steps(part)) for adapter, part in zip(
            self.adapters, state, strict=True)]
        if any(not row for row in component_rows):
            return
        for simultaneous in product(*component_rows):
            target = tuple(adapter.canonical(step.target) for adapter, step in zip(
                self.adapters, simultaneous, strict=True))
            weight = float(np.prod([step.weight for step in simultaneous]))
            parts = tuple(enumerate(simultaneous))
            channel, incidence = self._bundle(parts)
            yield NativeStep(target, weight, channel, incidence)


class LatticeAdapter:
    """Full native state, with optional resolution of catalytic physical routes.

    Without route resolution, same-target propensities aggregate into the exact
    state-path law. With it, the participating template's physical positions
    distinguish native pathways. This is an adapter resolution, not extra state,
    a semantic catalyst bonus, or evidence for an unmodeled microscopic bath.
    """

    def __init__(self, model: LatticeChemistry, *, resolve_routes=False):
        if type(model) not in (LatticeChemistry, CompartmentChemistry):
            raise TypeError("use a dedicated adapter for physics beyond the two known lattice models")
        self.model = deepcopy(model)
        if not isinstance(resolve_routes, bool):
            raise TypeError("resolve_routes must be boolean")
        self.resolve_routes = resolve_routes
        self.clock = "continuous"
        self._local = isinstance(model, CompartmentChemistry)

    @property
    def identity(self) -> dict:
        configuration = {"parameters": asdict(self.model.p)}
        if self._local:
            configuration.update({"reservoir": asdict(self.model.reservoir),
                                  "resolved_volumes": list(self.model.volumes)})
        return {
            "type": "lattice-chemistry-local" if self._local else "lattice-chemistry-shared",
            "schema": 1,
            "clock": self.clock,
            "resolve_routes": self.resolve_routes,
            "configuration": _json_value(configuration),
            "implementation": {
                module.__name__: sha256(Path(module.__file__).read_bytes()).hexdigest()
                for module in {inspect.getmodule(LatticeChemistry),
                               inspect.getmodule(CompartmentChemistry),
                               inspect.getmodule(canonical_state),
                               inspect.getmodule(rule_dependencies.__globals__["dependencies"])}
            },
        }

    def _state_object(self, state):
        if isinstance(state, (State, LocalState)):
            if isinstance(state, LocalState) != self._local:
                raise ValueError("state and reservoir resolution disagree")
            return state.copy()
        state = tuple(state)
        positions, internal, bonds = state[:3]
        if self._local:
            if len(state) != 5:
                raise ValueError("local lattice state must include F and W by compartment")
            return LocalState([tuple(pos) for pos in positions], list(internal),
                              {tuple(pair) for pair in bonds}, list(state[3]), list(state[4]))
        if len(state) != 4:
            raise ValueError("shared lattice state must include its fuel count")
        return State([tuple(pos) for pos in positions], list(internal),
                     {tuple(pair) for pair in bonds}, state[3])

    def canonical(self, state):
        native = self._state_object(state)
        try:
            self.model.validate(native)
        except AssertionError as error:
            raise ValueError("invalid native lattice configuration") from error
        canonical, _ = canonical_state(native)
        return canonical.key()

    def key(self, state):
        return self.canonical(state)

    def encode(self, state):
        native = self._state_object(self.canonical(state))
        record = native.record()
        # Shared records use `fuel`; local records additionally retain each
        # compartment's complete F/W allocation, never only the total.
        return _json_value({"kind": "local" if self._local else "shared", **record})

    def decode(self, value):
        if not isinstance(value, dict) or value.get("kind") != ("local" if self._local else "shared"):
            raise ValueError("encoded lattice state has the wrong state kind")
        positions = [tuple(pos) for pos in value["positions"]]
        internal = list(value["internal"])
        bonds = {tuple(pair) for pair in value["bonds"]}
        if self._local:
            native = LocalState(positions, internal, bonds, list(value["fuels"]),
                                list(value["wastes"]))
        else:
            native = State(positions, internal, bonds, value["fuel"])
        return self.canonical(native)

    def steps(self, state):
        native = self._state_object(self.canonical(state))
        for event in self.model.events(native):
            rate = float(event.rate)
            if rate <= 0.0:
                continue
            after = native.copy()
            self.model.apply(after, event)
            target = self.canonical(after)
            # Dependency records are optional structural evidence from the
            # current rule implementation. They do not prove independent
            # events, complete physical locality, or a counterfactual cause.
            reads, writes = rule_dependencies(self.model, native, event)
            incidence = Incidence(frozenset(reads), frozenset(writes),
                                  "source-canonical rule dependencies; effective chemistry")
            channel = None
            if self.resolve_routes and event.catalyst:
                channel = ("template_at", tuple(sorted(native.positions[i]
                                                      for i in event.catalyst)))
            yield NativeStep(target, rate, channel=channel, incidence=incidence)
