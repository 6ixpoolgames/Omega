import numpy as np
import pytest
from scipy.sparse import csr_matrix

from omega_v2.testbed.contracts import Event, RuleModule, WorldSpec
from omega_v2.testbed.analysis.shock_resilience import shock_readout, deadline_function_readout


def _fixture(mode='independent'):
    open_state = ((0, 1, 0, 0, 0), (0, 0, 0, 0, 0))
    closed_state = ((1, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    states = (open_state, closed_state)
    rate = 2. if mode == 'independent' else 1.

    def events(state):
        if state == open_state:
            return (Event('shock', 'shock_active', closed_state, rate, (0,),
                          increments={'shock_active_hits': 1., 'shock_events': 1.}),)
        return ()

    module = RuleModule('shocks', '1', events)
    world = WorldSpec('hand', '1', states, lambda s: None, lambda s: 0., {}, (module,),
                      {'shocks': {'mode': mode, 'hazard': 1., 'p': .5}})
    q = csr_matrix([[-rate, rate], [0., 0.]])
    return {'states': states, 'index': {s: i for i, s in enumerate(states)},
            'world': world, 'metadata': world.metadata, 'Q': q}, np.array([1., 0.])


def test_independent_shock_flux_exposure_and_open_closure_denominators():
    model, pi = _fixture()
    got = shock_readout(model, pi, np.array([False, True]))
    assert got['event_rate'] == pytest.approx(2.)
    assert got['expected_hits_per_time'] == pytest.approx(2.)
    assert got['exposed_expected'] == pytest.approx(1.)
    assert got['shock_event_closes_open_rate'] == pytest.approx(2.)
    assert got['shock_event_closes_open_rate_given_open'] == pytest.approx(2.)
    assert got['function_loss_event_flux_given_pre_active'] == pytest.approx(2.)
    assert got['function_loss_probability_per_event_given_pre_active'] == pytest.approx(1.)
    assert got['correlated_clock_rate'] is None


def test_correlated_event_probability_restores_identity_clock_channel():
    model, pi = _fixture('correlated')
    got = shock_readout(model, pi, np.array([False, True]))
    assert got['correlated_clock_rate'] == pytest.approx(2.)
    assert got['event_rate'] == pytest.approx(1.)
    assert got['shock_event_probability_per_clock_arrival'] == pytest.approx(.5)
    assert got['identity_probability_per_clock_arrival_stationary'] == pytest.approx(.5)
    assert got['function_loss_probability_per_clock_arrival_given_pre_active'] == pytest.approx(.5)


def test_one_of_two_active_lost_is_decrease_but_not_function_loss():
    before = ((0, 1, 0, 0, 0), (0, 1, 0, 0, 0))
    after = ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0))
    module = RuleModule('shocks', '1', lambda s: (
        (Event('shock', 'shock_active', after, 3., (0,),
               increments={'shock_active_hits': 1.}),) if s == before else ()))
    world = WorldSpec('hand', '1', (before, after), lambda s: None, lambda s: 0., {}, (module,),
                      {'shocks': {'mode': 'independent', 'hazard': 3., 'p': 1.}})
    model = {'states': (before, after), 'index': {before: 0, after: 1}, 'world': world}
    got = shock_readout(model, np.array([1., 0.]), np.array([False, False]))
    assert got['function_loss_event_flux_given_pre_active'] == pytest.approx(0.)
    assert got['any_active_decrease_event_flux_given_pre_active'] == pytest.approx(3.)
    assert got['function_loss_probability_per_event_given_pre_active'] == pytest.approx(0.)


def test_independent_event_probability_uses_palm_flux_ratio():
    one_active = ((0, 1, 0, 0, 0), (0, 0, 0, 0, 0))
    one_worn = ((1, 1, 0, 0, 0), (0, 1, 0, 0, 0))
    lost = ((1, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    survived = ((1, 0, 0, 0, 0), (0, 0, 0, 0, 0))
    # Distinguish the second pre-state in its nonfunctional fuel coordinate.
    one_worn = ((1, 1, 0, 1, 0), (0, 1, 0, 0, 0))
    survived = ((1, 0, 0, 1, 0), (0, 1, 0, 0, 0))
    states = (one_active, one_worn, lost, survived)

    def events(s):
        if s == one_active:
            return (Event('shock', 'shock_active', lost, 1., (0,)),)
        if s == one_worn:
            return (Event('shock', 'shock_worn', survived, 9., (0,)),)
        return ()

    module = RuleModule('shocks', '1', events)
    world = WorldSpec('hand', '1', states, lambda s: None, lambda s: 0., {}, (module,),
                      {'shocks': {'mode': 'independent', 'hazard': 1., 'p': 1.}})
    model = {'states': states, 'index': {s: i for i, s in enumerate(states)}, 'world': world}
    got = shock_readout(model, np.array([.5, .5, 0., 0.]), np.zeros(4, dtype=bool))
    assert got['function_loss_probability_per_event_given_pre_active'] == pytest.approx(.1)


def test_deadline_reports_function_loss_and_surviving_active_reserve():
    model, pi = _fixture()
    got = deadline_function_readout(model, pi, np.log(2.) / 2., np.array([False, True]))
    assert got['function_loss_probability'] == pytest.approx(.5)
    assert got['function_reserve_probability'] == pytest.approx(.5)
    assert got['function_survival_probability'] == pytest.approx(.5)
    assert got['expected_active_reserve'] == pytest.approx(.5)
    assert got['expected_active_reserve_given_function_survival'] == pytest.approx(1.)
    assert got['structural_closure_probability'] == pytest.approx(.5)
