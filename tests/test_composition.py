import numpy as np
import pytest
from scipy.linalg import expm

from omega_v2.testbed.analysis.blocked_entropy import profile
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.composition import checked_lumping, compose_worlds
from omega_v2.testbed.contracts import Event, RuleModule
from omega_v2.testbed.resource_feedback import ResourceFeedbackParameters, build_world


def test_independent_composition_kernel_and_history_are_products():
    world = build_world()
    local = compile_world(world)
    combined = compile_world(compose_worlds({'left': world, 'right': world}))
    single = expm(local['Q'].toarray()*.25)
    joint = expm(combined['Q'].toarray()*.25)
    assert np.max(abs(joint-np.kron(single, single))) < 1e-12
    root = (1, 1, 0)
    a = profile(local['Q'], {'root': local['index'][root]}, .25, [1])
    b = profile(combined['Q'], {'root': combined['index'][(root, root)]}, .25, [1])
    assert b['bits']['1']['root'] == pytest.approx(2*a['bits']['1']['root'])
    assert b['rates']['root'] == pytest.approx(2*a['rates']['root'])


def test_heterogeneous_population_capacities_compose_without_rewriting_compiler():
    a = build_world()
    b = build_world(ResourceFeedbackParameters(apparatus_capacity=2, carrier_capacity=2))
    world = compose_worlds({'small': a, 'large': b})
    model = compile_world(world)
    assert len(world.states) == 16*36
    assert 'large.apparatus' in model['observables']
    with pytest.raises(RuntimeError):
        compose_worlds({'small': a, 'large': b}, max_states=100)


def test_lumping_rejects_hidden_unequal_continuation():
    q = np.array([[-1., 0., 1.], [0., -2., 2.], [0., 0., 0.]])
    with pytest.raises(ValueError, match='not a strong lumping'):
        checked_lumping(q, ['same', 'same', 'terminal'])
    q[1] = [0., -1., 1.]
    result = checked_lumping(q, ['same', 'same', 'terminal'])
    assert np.array_equal(result['Q'].toarray(), [[-1., 1.], [0., 0.]])
    assert 'entropy not retained' in result['scope']


def test_native_joint_carrier_transfer_has_explicit_support_and_conserves_energy():
    def events(state):
        for source, target in ((0, 1), (1, 0)):
            if state[source][2] == 1 and state[target][2] == 0:
                changed = [list(s) for s in state]
                changed[source][2] -= 1
                changed[target][2] += 1
                yield Event('joint-transfer', 'carrier-transfer', tuple(map(tuple, changed)),
                            .1, (0, 1), increments={'joint_carrier_transfers': 1.})
    world = build_world()
    coupling = RuleModule('exchange', '1', events,
                          requires=('left.charged-spent-carrier-pool',
                                    'right.charged-spent-carrier-pool'))
    joined = compose_worlds({'left': world, 'right': world}, (coupling,))
    model = compile_world(joined)
    for state in joined.states:
        for event in events(state):
            assert joined.energy(state) == joined.energy(event.target)
    assert np.any(model['flows']['joint_carrier_transfers'] > 0)
