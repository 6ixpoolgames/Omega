from dataclasses import replace

import numpy as np

from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.reactive_lattice import (
    LatticeParameters,
    build_world,
    geometry,
    organized_root,
    reference_masks,
)


def test_dark_equilibrium_including_carrier_packet_and_catalysis():
    p = LatticeParameters(sites=4, monomers=2, supply=0., damage=0.)
    c = compile_world(build_world(p))
    weights = np.exp(-p.beta*c['energy'])
    weights /= weights.sum()
    flux = c['Q'].multiply(weights[:, None])
    assert np.max(abs((flux-flux.T).data)) < 1e-12
    assert np.max(abs(weights @ c['Q'])) < 1e-12


def test_no_particle_id_or_illegal_bond_multiplicity():
    g = list(geometry(4, 2))
    assert len(g) == 10  # six site pairs plus four nearest-neighbour bonds
    assert len(set(g)) == len(g)
    world = build_world(LatticeParameters(sites=4, monomers=2))
    assert len(world.states) == 10*4*3*2
    for state in world.states:
        for module in world.modules:
            for event in module.events(state):
                world.validate(event.target)
                assert event.target[0].bit_count() == 2


def test_contact_and_local_carrier_are_consequential():
    p = LatticeParameters(sites=7, monomers=6)
    world = build_world(p)
    chemistry = next(m for m in world.modules if m.id == 'chemistry')
    state = (63, 1, 2, 2, 0)
    target = (63, 1 | (1 << 2), 2, 0, 0)
    forward = next(e for e in chemistry.events(state) if e.target == target and e.family == 'paid_join')
    reverse = next(e for e in chemistry.events(target) if e.target == state and e.family == 'paid_reverse')
    assert forward.increments['assisted_join'] == 1.
    assert abs(forward.rate/reverse.rate-np.exp(p.beta)) < 1e-12
    distant = (63, 1, 5, 2, 0)
    assert not any(e.family == 'paid_join' and e.target[1] == target[1]
                   for e in chemistry.events(distant))


def test_exact_shell_temperature_cancellation_and_three_references():
    p = LatticeParameters(sites=4, monomers=2)
    c = compile_world(build_world(p))
    root = organized_root(p)
    refs = reference_masks(c, root)
    c2 = compile_world(build_world(replace(p, beta=.5)))
    refs2 = reference_masks(c2, root)
    for name, weights in refs.items():
        assert abs(weights.sum()-1) < 1e-12
        assert np.allclose(weights @ c['energy'], c['world'].energy(root))
        assert np.array_equal(weights, refs2[name])
    assert refs['thermal'][c['index'][root]] > 0
    assert all(s[1] == 0 for s, w in zip(c['states'], refs['unbound']) if w > 0)


def test_energy_accounting_and_nonempty_three_generation_geometry():
    p = LatticeParameters(sites=7, monomers=6)
    c = compile_world(build_world(p))
    assert any(s[1].bit_count() == 3 for s in c['states'])
    assert np.max(abs(c['Q'] @ c['energy']-c['flows']['drive_work']+c['flows']['bath_heat'])) < 1e-9
    assert c['metadata']['density'] == 6/7
