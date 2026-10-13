"""Named subsystem products and explicit native coupling modules.

No coarse-graining or entropy correction is performed by composition. Native
coupling rates and reverses are supplied by the physical adapter.
"""
from itertools import product
from math import prod

import numpy as np
from scipy.sparse import csr_matrix

from .analysis.finite_classes import _generator
from .contracts import Event, RuleModule, WorldSpec


def compose_worlds(subsystems, couplings=(), max_states=10000):
    """Compose local state tuples, additive energies and costed coupling events.

    Interaction-energy models must supply a new joint adapter; simply adding
    interaction energy here would invalidate the existing local rate laws.
    """
    names = tuple(subsystems)
    if not names or any(not isinstance(name, str) or not name or '.' in name for name in names):
        raise ValueError('Nonempty subsystem names without dots required')
    worlds = tuple(subsystems.values())
    count = prod(len(world.states) for world in worlds)
    if count > max_states:
        raise RuntimeError('State cap: composed physical space was not truncated')
    states = tuple(product(*(world.states for world in worlds)))

    def validate(state):
        if not isinstance(state, tuple) or len(state) != len(worlds):
            raise ValueError('One local state per named subsystem required')
        for world, local in zip(worlds, state):
            world.validate(local)

    def energy(state):
        return sum(world.energy(local) for world, local in zip(worlds, state))

    def lift(slot, name, module):
        def events(state):
            for event in module.events(state[slot]):
                target = list(state)
                target[slot] = event.target
                yield Event(f'{name}.{event.rule_id}', f'{name}.{event.family}',
                            tuple(target), event.rate, (slot,), event.work,
                            {f'{name}.{key}': value for key, value in event.increments.items()})
        return RuleModule(f'{name}.{module.id}', module.version, events,
                          tuple(f'{name}.{r}' for r in module.requires),
                          tuple(f'{name}.{r}' for r in module.provides))

    modules = tuple(lift(i, name, module) for i, (name, world) in enumerate(zip(names, worlds))
                    for module in world.modules) + tuple(couplings)
    observables = {f'{name}.{key}': (lambda state, i=i, fn=fn: fn(state[i]))
                   for i, (name, world) in enumerate(zip(names, worlds))
                   for key, fn in world.observables.items()}
    return WorldSpec('named-subsystem-composition', '1', states, validate, energy,
                     observables, modules,
                     {'fields': tuple(f'{name}.{field}' for name, world in zip(names, worlds)
                                      for field in world.metadata.get('fields', ())),
                      'subsystem_order': names,
                      'subsystems': {name: dict(world.metadata) for name, world in zip(names, worlds)},
                      'energy_composition': 'additive local energy; no undeclared interaction energy',
                      'couplings': [m.id for m in couplings],
                      'grain': 'full product physical states; no quotient'},
                     degeneracy=lambda state: prod(world.degeneracy(local) if world.degeneracy else 1.
                                                   for world, local in zip(worlds, state)))


def checked_lumping(Q, labels, tolerance=1e-10):
    """Return a macro generator only for a strong lumping of the native law.

    This certifies Markov macro dynamics, not preservation of fine-history entropy.
    """
    q = _generator(Q)
    if len(labels) != q.shape[0] or q.shape[0] != q.shape[1]:
        raise ValueError('One macro label per physical state required')
    unique = tuple(dict.fromkeys(labels))
    index = {label: i for i, label in enumerate(unique)}
    assignment = np.array([index[label] for label in labels])
    incidence = csr_matrix((np.ones(len(labels)), (np.arange(len(labels)), assignment)),
                           shape=(len(labels), len(unique)))
    totals = (q @ incidence).toarray()
    coarse = np.empty((len(unique), len(unique)))
    for i in range(len(unique)):
        members = totals[assignment == i]
        if np.max(abs(members-members[0])) > tolerance:
            raise ValueError('Projection is not a strong lumping of the native law')
        coarse[i] = members[0]
    return {'Q': csr_matrix(coarse), 'labels': unique,
            'scope': 'macro transition law only; fine conditional-history entropy not retained'}
