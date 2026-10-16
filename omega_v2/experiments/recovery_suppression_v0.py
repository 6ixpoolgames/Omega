"""Paid suppression and correction that can relapse: frozen finite worlds."""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import product

from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import FiniteDistribution
from omega_v2.finite.recovery_dynamics import ZERO_COST, Chain

F = Fraction
ZERO = F(0)
QUARTER = F(1, 4)
PROTOCOL = "docs/research_notes/omega_v2/recovery_suppression_protocol_v0.md"
PROXY_COMMANDS = ("idle", "suppress", "recover")
REFERENCE_COMMANDS = ("idle", "revert")


@dataclass(frozen=True)
class Settings:
    name: str
    capacity: int = 0
    price: int = 1
    replenish: int = 0
    mode: str = "recurring"
    effect: str = "block"
    epsilon: F = ZERO
    writer: F = QUARTER
    relapse: F = ZERO
    maintenance: F = ZERO
    death: F = ZERO

    def __post_init__(self):
        if any(type(x) is not int or x < 0 for x in (self.capacity, self.price, self.replenish)) or not self.price:
            raise ValueError("integer capacity/rate and positive price required")
        if self.mode not in ("recurring", "one_shot") or self.effect not in ("block", "hide"):
            raise ValueError("unknown suppression mode/effect")
        if any(not isinstance(x, F) or not 0 <= x <= 1 for x in (
            self.epsilon, self.writer, self.relapse, self.maintenance, self.death
        )):
            raise ValueError("exact rational probabilities required")
        if self.mode == "recurring" and self.maintenance:
            raise ValueError("maintenance applies only to persistent seals")


@dataclass(frozen=True)
class State:
    stock: int
    reference: bool = False
    sealed: bool = False
    first: str = "none"
    relapsed: bool = False
    dead: bool = False


def outcome(state):
    if state.dead:
        return "dead_before" if state.first == "none" else "dead_after"
    if state.reference:
        return "corrected"
    return "never_reset" if state.first == "none" else "proxy_after"


def purchase(settings, state, command):
    stock = state.stock
    sealed = state.sealed if settings.mode == "one_shot" else False
    protected, spent = sealed, 0
    if command == "suppress" and (settings.mode == "recurring" or not sealed) and stock >= settings.price:
        stock -= settings.price
        spent = settings.price
        protected = True
        sealed = settings.mode == "one_shot"
    return stock, sealed, protected, spent


def _reset(state, source):
    return replace(state, reference=True, first=source if state.first == "none" else state.first)


def _relapse(state):
    return replace(state, reference=False, relapsed=True)


def transition(settings, state, intended):
    if state.dead:
        return FiniteDistribution.point_mass((state, ZERO_COST))
    menu = REFERENCE_COMMANDS if state.reference else PROXY_COMMANDS
    if intended not in menu:
        raise ValueError("command not in the current register menu")
    masses = {}

    def add(target, charge, p):
        edge = (target, charge)
        masses[edge] = masses.get(edge, ZERO) + p

    def finish(target, charge, p):
        target = replace(target, stock=min(settings.capacity, target.stock + settings.replenish))
        if target.sealed:
            add(replace(target, sealed=False), charge, p * settings.maintenance)
            add(target, charge, p * (1 - settings.maintenance))
        else:
            add(target, charge, p)

    add(replace(state, dead=True), (1, 0, 0), settings.death)
    for executed in menu:
        p = (1 - settings.death) * (settings.epsilon / len(menu) + (1 - settings.epsilon) * int(executed == intended))
        if state.reference:
            chance = F(1) if executed == "revert" else settings.relapse
            finish(_relapse(state), (1, 0, 0), p * chance)
            finish(state, (1, 0, 0), p * (1 - chance))
            continue
        stock, sealed, protected, spent = purchase(settings, state, executed)
        next_state = replace(state, stock=stock, sealed=sealed)
        if executed == "recover":
            source = "selected" if executed == intended else "noise_assisted"
            finish(_reset(next_state, source), (1, spent, 1), p)
        else:
            blocked = protected and settings.effect == "block"
            writer = ZERO if blocked else settings.writer
            finish(_reset(next_state, "external"), (1, spent, 0), p * writer)
            finish(next_state, (1, spent, 0), p * (1 - writer))
    return FiniteDistribution.from_mapping(masses)


@dataclass(frozen=True)
class World:
    settings: Settings
    initial: State
    states: tuple
    kernels: dict
    programs: tuple


def build_world(settings):
    initial = State(settings.capacity)
    states, kernels = [initial], {}
    for state in states:
        menu = ("idle",) if state.dead else REFERENCE_COMMANDS if state.reference else PROXY_COMMANDS
        for command in menu:
            law = transition(settings, state, command)
            kernels[state, command] = law
            for (target, _cost), _p in law.rows:
                if target not in states:
                    states.append(target)
    observations = {s: (s.reference, s.dead) for s in states}
    obs = tuple(dict.fromkeys(observations.values()))
    programs = tuple(FiniteStateController(
        f"{proxy}/{reference}", (0,), 0, tuple(observations.items()),
        tuple((0, o, 0) for o in obs),
        tuple((0, o, "idle" if o[1] else reference if o[0] else proxy) for o in obs),
    ) for proxy, reference in product(PROXY_COMMANDS, REFERENCE_COMMANDS))
    return World(settings, initial, tuple(states), kernels, programs)


def product_chain(world, controller):
    states, rows = [(world.initial, controller.initial_memory)], {}
    for state, memory in states:
        if state.dead:
            law = FiniteDistribution.point_mass(((state, memory), ZERO_COST))
        else:
            obs = controller.observe(state)
            command, updated = controller.action(memory, obs), controller.update(memory, obs)
            law = world.kernels[state, command].pushforward(lambda edge, updated=updated: ((edge[0], updated), edge[1]))
        rows[state, memory] = law
        for (target, _cost), _p in law.rows:
            if target not in states:
                states.append(target)
    return Chain(tuple(states), states[0], rows, {s: outcome(s[0]) for s in states},
                 frozenset(s for s in states if s[0].dead))


def control_panel():
    settings = [
        Settings("no_stock"), Settings("recurring_s1", capacity=1), Settings("recurring_s3", capacity=3),
        Settings("recurring_cost2", capacity=3, price=2),
        Settings("recurring_replenished", capacity=1, replenish=1),
        Settings("recurring_underfunded", capacity=3, price=2, replenish=1),
        Settings("one_shot_s1", capacity=1, mode="one_shot"),
        Settings("one_shot_s3", capacity=3, mode="one_shot"),
        Settings("seal_failure_s1", capacity=1, mode="one_shot", maintenance=F(1, 2)),
        Settings("seal_failure_s3", capacity=3, mode="one_shot", maintenance=F(1, 2)),
        Settings("seal_failure_certain", capacity=3, mode="one_shot", maintenance=F(1)),
        Settings("seal_replenished", capacity=1, mode="one_shot", maintenance=F(1, 2), replenish=1),
        Settings("hide_only", capacity=1, mode="one_shot", effect="hide"),
        Settings("recurring_noise", capacity=1, replenish=1, epsilon=F(1, 10)),
        Settings("one_shot_noise", capacity=1, mode="one_shot", epsilon=F(1, 10)),
        Settings("spontaneous_relapse", relapse=F(1, 4)),
        Settings("noisy_relapse", epsilon=F(1, 10), relapse=F(1, 4)),
        Settings("finite_stock_relapse", capacity=3, relapse=F(1, 4)),
        Settings("competing_death", death=F(1, 4)),
        Settings("replenished_death", capacity=1, replenish=1, death=F(1, 4)),
    ]
    return {s.name: build_world(s) for s in settings}
