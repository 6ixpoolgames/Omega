"""Small native-clock Markov devices for exploratory extent comparisons.

These are logical calibration models, not replacements for the lattice chemistry.
One tick is a declared physical time unit. Read/write provenance is supplied by
the explicit update rules; it is not an identified counterfactual causal graph.
"""

from collections import defaultdict
from dataclasses import dataclass
from itertools import product

import numpy as np


@dataclass(frozen=True)
class Event:
    reads: tuple[int, ...]
    writes: tuple[int, ...]


@dataclass(frozen=True)
class Outcome:
    target: tuple[int, ...]
    probability: float
    events: tuple[Event, ...] = ()


@dataclass
class Device:
    name: str
    states: tuple[tuple[int, ...], ...]
    rows: dict[tuple[int, ...], tuple[Outcome, ...]]
    initial: dict[tuple[int, ...], float]
    description: str

    def arrays(self):
        index = {state: i for i, state in enumerate(self.states)}
        kernel = np.zeros((len(index), len(index)))
        initial = np.zeros(len(index))
        for state, mass in self.initial.items():
            initial[index[state]] = mass
        for state, outcomes in self.rows.items():
            for outcome in outcomes:
                kernel[index[state], index[outcome.target]] += outcome.probability
        return initial, kernel


def independent_flips(n, probability, name):
    states = tuple(product((0, 1), repeat=n))
    rows = {}
    for state in states:
        outcomes = []
        for flips in product((0, 1), repeat=n):
            mass = float(np.prod([probability if bit else 1-probability for bit in flips]))
            if mass == 0:
                continue
            target = tuple(a ^ b for a, b in zip(state, flips, strict=True))
            events = tuple(Event((i,), (i,)) for i, bit in enumerate(flips) if bit)
            outcomes.append(Outcome(target, mass, events))
        rows[state] = tuple(outcomes)
    return Device(name, states, rows, {(0,)*n: 1.0},
                  f'{n} independent reversible switches, flip probability {probability}/tick')


def deterministic_builder(kind):
    states = tuple(product((0, 1), repeat=3))
    rows = {}
    for state in states:
        if kind == 'parallel':
            target, reads = (1, 1, 1), ((0,), (1,), (2,))
        elif kind == 'chain':
            target = (1, state[1] | state[0], state[2] | state[1])
            reads = ((0,), (0, 1), (1, 2))
        elif kind == 'fork_join':
            target = (1, 1, state[2] | (state[0] & state[1]))
            reads = ((0,), (1,), (0, 1, 2))
        else:
            raise ValueError(kind)
        events = tuple(Event(reads[i], (i,)) for i in range(3) if state[i] != target[i])
        rows[state] = (Outcome(target, 1.0, events),)
    return Device(f'deterministic_{kind}', states, rows, {(0, 0, 0): 1.0},
                  'Synchronous irreversible binary register construction; no thermodynamic claim')


def reversible_gate(catalytic):
    states = tuple(product((0, 1), repeat=2))
    rows = {}
    for a, b in states:
        pa = 0.125
        pb = 0.4375 if catalytic and a else 0.0625
        rows[a, b] = (
            Outcome((1-a, b), pa, (Event((0,), (0,)),)),
            Outcome((a, 1-b), pb, (Event((0, 1) if catalytic else (1,), (1,)),)),
            Outcome((a, b), 1-pa-pb),
        )
    return Device('reversible_gate_on' if catalytic else 'reversible_gate_off', states, rows,
                  {(0, 0): 1.0}, 'Symmetric lazy kernel; gate accelerates BOTH bit-1 directions x7')


def token_resource(transport=None):
    # A single material token can be free or bound to either destination.
    bound_a, bound_b = (1, 0, -1), (0, 1, -1)
    if transport is None:
        free = (0, 0, -1)
        states = (free, bound_a, bound_b)
        edges = {free: [(bound_a, .0125), (bound_b, .0125)],
                 bound_a: [(free, .05)], bound_b: [(free, .05)]}
        initial = {free: 1.0}
        name = 'resource_shared'
    else:
        left, right = (0, 0, 0), (0, 0, 1)
        states = (left, right, bound_a, bound_b)
        edges = {left: [(right, transport), (bound_a, .025)],
                 right: [(left, transport), (bound_b, .025)],
                 bound_a: [(left, .05)], bound_b: [(right, .05)]}
        initial = {left: .5, right: .5}
        name = f'resource_local_{transport:g}'
    rows = {}
    for state in states:
        outcomes = []
        for target, probability in edges[state]:
            writes = tuple(i for i in range(3) if state[i] != target[i])
            outcomes.append(Outcome(target, probability, (Event((0, 1, 2), writes),)))
        outcomes.append(Outcome(state, 1-sum(item.probability for item in outcomes)))
        rows[state] = tuple(outcomes)
    return Device(name, states, rows, initial,
                  'One shared token; finite local transport is real dynamics, not renaming')


def reconvergent(branching=True):
    states = ((0,), (1,), (2,), (3,))
    event = (Event((0,), (0,)),)
    first = ((Outcome((1,), .5, event), Outcome((2,), .5, event)) if branching
             else (Outcome((1,), 1, event),))
    rows = {(0,): first,
            (1,): (Outcome((3,), 1, event),), (2,): (Outcome((3,), 1, event),),
            (3,): (Outcome((3,), 1),)}
    return Device('reconvergence' if branching else 'single_corridor', states, rows, {(0,): 1},
                  'Two distinct one-tick prefixes share the same absorbing residual after tick 2')


def ring(driven):
    states = tuple((i,) for i in range(3))
    forward, backward = (.7, .1) if driven else (.4, .4)
    event = (Event((0,), (0,)),)
    rows = {(i,): (Outcome(((i+1) % 3,), forward, event),
                   Outcome(((i-1) % 3,), backward, event), Outcome((i,), .2))
            for i in range(3)}
    return Device('ring_driven' if driven else 'ring_reversible', states, rows, {(0,): 1},
                  'Equal total move probability .8; driven case has stationary circulation')


def renamed(device):
    mapping = {s: tuple(reversed(s)) for s in device.states}
    n = len(device.states[0])
    rows = {}
    for state, outcomes in device.rows.items():
        rows[mapping[state]] = tuple(Outcome(mapping[o.target], o.probability,
            tuple(Event(tuple(n-1-i for i in e.reads), tuple(n-1-i for i in e.writes))
                  for e in o.events)) for o in outcomes)
    return Device(device.name+'_renamed', tuple(mapping[s] for s in reversed(device.states)),
                  rows, {mapping[s]: p for s, p in device.initial.items()},
                  'Consistent coordinate and state-enumeration relabeling')


def alias_encoding(device):
    # An extra serialized copy of a coordinate, not another physical register/event.
    mapping = {s: (*s, s[0]) for s in device.states}
    rows = {mapping[s]: tuple(Outcome(mapping[o.target], o.probability, o.events)
                            for o in outcomes) for s, outcomes in device.rows.items()}
    return Device(device.name+'_alias', tuple(mapping[s] for s in device.states), rows,
                  {mapping[s]: p for s, p in device.initial.items()},
                  'Injective redundant encoding only; native physical event ports unchanged')


def devices():
    base = [independent_flips(1, .5, 'gas_one'), independent_flips(2, .5, 'gas_two'),
            independent_flips(2, .05, 'slow_memory'),
            independent_flips(2, 0, 'static'),
            *(deterministic_builder(k) for k in ('parallel', 'chain', 'fork_join')),
            reversible_gate(False), reversible_gate(True), reconvergent(), reconvergent(False),
            token_resource(), token_resource(.01), token_resource(.45),
            ring(False), ring(True)]
    return base + [renamed(base[8]), alias_encoding(base[8])]


def history_profiles(device, horizon):
    """Exact finite-depth path enumeration, aggregated ONLY after retaining weights.

    Parent links follow last writers of read/write ports. Simultaneous events
    read the old state and have disjoint writes. This is provenance, not a proof
    that every resulting ideal is a full physically legal alternative history.
    """
    n = len(device.states[0])
    frontier = [(s, (-1,)*n, (), float(p), (s,)) for s, p in device.initial.items()]
    for _tick in range(horizon):
        next_frontier = []
        for state, writers, parents, mass, path in frontier:
            for outcome in device.rows[state]:
                if outcome.probability <= 0:
                    raise ValueError('Declare only positive native outcomes')
                new_writers, new_parents = list(writers), list(parents)
                touched = set()
                for event in outcome.events:
                    if touched.intersection(event.writes):
                        raise ValueError('Simultaneous conflicting writes')
                    touched.update(event.writes)
                    dependencies = {writers[i] for i in (*event.reads, *event.writes)
                                    if writers[i] >= 0}
                    new_parents.append(sum(1 << i for i in dependencies))
                    for i in event.writes:
                        new_writers[i] = len(new_parents)-1
                next_frontier.append((outcome.target, tuple(new_writers), tuple(new_parents),
                                      mass*outcome.probability, path+(outcome.target,)))
        frontier = next_frontier
    profiles = defaultdict(float)
    paths = defaultdict(float)
    endpoints = defaultdict(float)
    mean_events = 0.0
    for state, _, parents, mass, path in frontier:
        profiles[parents] += mass
        paths[path] += mass
        endpoints[state] += mass
        mean_events += mass*len(parents)
    return {'profiles': tuple((p, mask) for mask, p in profiles.items()),
            'mass': sum(profiles.values()), 'marked_histories': len(frontier),
            'state_histories': len(paths), 'mean_events': mean_events,
            'path_entropy': -sum(p*np.log(p) for p in paths.values()),
            'endpoints': endpoints}
