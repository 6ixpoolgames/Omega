"""Frozen minimal recovery worlds with complete two-table controller catalogues."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import FiniteDistribution
from omega_v2.finite.recovery_dynamics import ZERO_COST, Chain, possible_targets

F = Fraction
ZERO_PROBABILITY = F(0)
PROTOCOL = "docs/research_notes/omega_v2/recovery_dynamics_protocol_v0.md"
RESET = frozenset({"selected", "noise_assisted", "external"})
OUTCOMES = ("live", "selected", "noise_assisted", "external", "dead")
ACTIONS = ("refuse", "recover")


@dataclass(frozen=True)
class Settings:
    name: str
    m: int = 1
    epsilon: F = ZERO_PROBABILITY
    writer: F = ZERO_PROBABILITY
    death: F = ZERO_PROBABILITY
    channel: str = "open"
    working: bool = True

    def __post_init__(self):
        if type(self.m) is not int or self.m < 1:
            raise ValueError("positive consecutive-step requirement needed")
        if any(not isinstance(p, F) or not 0 <= p <= 1 for p in (self.epsilon, self.writer, self.death)):
            raise ValueError("exact rational noise, writer and death probabilities required")
        if self.channel not in ("open", "sealed", "mismatch") or type(self.working) is not bool:
            raise ValueError("declared channel and actuator required")


@dataclass(frozen=True)
class State:
    progress: int = 0
    assisted: bool = False
    outcome: str = "live"

    @property
    def register(self):
        return 0 if self.outcome in RESET else 1


def transition(settings, state, intended):
    if state.outcome != "live":
        return FiniteDistribution.point_mass((state, ZERO_COST))
    masses = {}

    def add(target, cost, probability):
        edge = (target, cost)
        masses[edge] = masses.get(edge, F(0)) + probability

    add(State(outcome="dead"), (1, 0, 0), settings.death)
    add(State(outcome="external"), (1, 0, 1), (1 - settings.death) * settings.writer)
    for executed in ACTIONS:
        p = settings.epsilon / 2 + (1 - settings.epsilon) * int(executed == intended)
        p *= (1 - settings.death) * (1 - settings.writer)
        if executed == "recover" and settings.working:
            assisted = state.assisted or intended != executed
            if state.progress + 1 == settings.m:
                target = State(outcome="noise_assisted" if assisted else "selected")
            else:
                target = State(state.progress + 1, assisted)
        else:
            target = State()
        add(target, (1, int(executed == "recover"), 0), p)
    return FiniteDistribution.from_mapping(masses)


@dataclass(frozen=True)
class World:
    settings: Settings
    states: tuple
    kernels: dict
    programs: tuple


def build_world(settings: Settings):
    states, kernels = [State()], {}
    for state in states:
        for command in ACTIONS:
            law = transition(settings, state, command)
            kernels[state, command] = law
            for (target, _cost), _p in law.rows:
                if target not in states:
                    states.append(target)
    observations = {s: (s.register, settings.channel if s.outcome == "live" else "stopped") for s in states}
    programs = []
    for command in ACTIONS:
        obs = tuple(dict.fromkeys(observations.values()))
        programs.append(FiniteStateController(
            command, (0,), 0, tuple(observations.items()), tuple((0, o, 0) for o in obs),
            tuple((0, o, command if o[1] != "stopped" else "refuse") for o in obs),
        ))
    return World(settings, tuple(states), kernels, tuple(programs))


def product_chain(world: World, controller: FiniteStateController):
    states = [(State(), controller.initial_memory)]
    rows = {}
    for state, memory in states:
        observed = controller.observe(state)
        command = controller.action(memory, observed)
        updated = controller.update(memory, observed)
        if state.outcome != "live":
            law = FiniteDistribution.point_mass(((state, memory), ZERO_COST))
        else:
            law = world.kernels[state, command].pushforward(lambda edge, updated=updated: ((edge[0], updated), edge[1]))
        rows[state, memory] = law
        for (target, _cost), _p in law.rows:
            if target not in states:
                states.append(target)
    return Chain(tuple(states), states[0], rows, {s: s[0].outcome for s in states},
                 frozenset(s for s in states if s[0].outcome != "live"))


def possible_recovery(world):
    successors = {s: {t for a in ACTIONS for (t, _c), _p in world.kernels[s, a].rows} for s in world.states}
    return possible_targets(world.states, successors, frozenset(s for s in world.states if s.outcome in RESET))


def control_panel():
    settings = [Settings("open_noiseless"), Settings("open_three_noiseless", m=3),
                Settings("sealed_noiseless", channel="sealed"), Settings("immutable_record", channel="mismatch")]
    settings.extend(Settings(f"open_noise_{denominator}_m{m}", epsilon=F(1, denominator), m=m)
                    for denominator in (1000, 100, 10) for m in (1, 3))
    settings.extend([Settings("sealed_noise", epsilon=F(1, 10), m=3, channel="sealed"),
                     Settings("broken_actuator", epsilon=F(1, 10), working=False),
                     Settings("external_writer", writer=F(1, 4)),
                     Settings("competing_death", epsilon=F(1, 10), death=F(1, 4))])
    return {setting.name: build_world(setting) for setting in settings}
