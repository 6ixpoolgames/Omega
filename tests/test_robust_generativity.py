from math import comb, exp

import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

from omega_v2.testbed.analysis.class_queries import (
    ClassQueries,
    occupation_distribution,
    pulse_kernel,
    reward_integral,
)
from omega_v2.testbed.analysis.finite_classes import analyze, finite_history_bits
from omega_v2.testbed.analysis.generativity_depth import (
    FAILURE,
    LINK1,
    LINK2,
    SUCCESS,
    WAIT,
    any_start_update,
    compile_monitor,
    detected_chain_profile,
    initial_distribution,
    initial_update,
)
from omega_v2.testbed.analysis.generativity_robustness import (
    closure_targets,
    depth_profile,
    lifted_pulse,
    pulse_readout,
)
from omega_v2.testbed.compiler import compile_world, sample_events
from omega_v2.testbed.contracts import Event
from omega_v2.testbed.robust_generativity import (
    MECHANISMS,
    GenerativityParameters,
    build_world,
    matched_roots,
    physical_readouts,
)


def events(world, state, family=None):
    return [e for m in world.modules for e in m.events(state) if family is None or e.family == family]


@pytest.mark.parametrize('capacity', [4, 6, 8])
@pytest.mark.parametrize('rho', [0., .05])
def test_inventory_enumeration_and_finite_kernel_gate(capacity, rho):
    w = build_world(GenerativityParameters(capacity=capacity, irreversible_fraction=rho))
    assert len(w.states) == 18*comb(capacity+(4 if rho else 3), 4 if rho else 3)
    if capacity == 8 and rho:
        from omega_v2.testbed.analysis.blocked_entropy import sampled_kernel
        with pytest.raises(MemoryError):
            sampled_kernel(csr_matrix((len(w.states), len(w.states))), .25, max_kernel_bytes=160*1024**2)


@pytest.mark.parametrize('mechanism', MECHANISMS)
@pytest.mark.parametrize('alpha', [.5, 1.])
def test_full_packet_and_bank_dark_detailed_balance(mechanism, alpha):
    p = GenerativityParameters(capacity=3, feedback_exponent=alpha, supply_rate=0., damage_rate=0.)
    c = compile_world(build_world(p, mechanism))
    weights = np.array([c['world'].degeneracy(s)*exp(-p.beta*c['world'].energy(s)) for s in c['states']])
    weights /= weights.sum()
    flux = c['Q'].multiply(weights[:, None])
    error = flux-flux.T
    assert max(abs(error.data), default=0.) < 1e-12


def test_saturated_capture_has_all_reverse_origins_and_bank_debits():
    p = GenerativityParameters(capacity=4)
    w = build_world(p)
    t = (8, 0, 1, 0, 0, 0)
    reverse = events(w, t, 'reverse_assisted_capture')
    assert {e.target[0] for e in reverse} == set(range(3, 9))
    for e in reverse:
        forward = next(f for f in events(w, e.target, 'assisted_capture') if f.target == t)
        assert forward.rate/e.rate == pytest.approx(exp(-p.beta*(w.energy(t)-w.energy(e.target))))
        assert e.increments['reverse_capture_bank_debit'] == .5*(8-e.target[0])
    # Full-bank overflow is not an unrecorded self-event: the packet changes.
    full = events(w, (8, 1, 1, 0, 0, 0), 'assisted_capture')[0]
    assert full.target == t and full.increments['captured_energy'] == 0.


def test_mechanism_cuts_preserve_basals_and_remove_both_link_directions():
    p = GenerativityParameters(capacity=4)
    for mechanism in MECHANISMS:
        w = build_world(p, mechanism)
        base = build_world(p)
        for state in ((8, 1, 1, 1, 0, 0), (4, 1, 1, 1, 1, 0)):
            for family in ('paid_basal_B', 'reverse_basal_B', 'basal_capture', 'packet_inflow', 'damage_A'):
                assert events(w, state, family) == events(base, state, family)
        if mechanism.startswith('cut_') and mechanism != 'cut_assisted_capture':
            link = mechanism[4:]
            assert not any(e.family in ('paid_assisted_'+link, 'reverse_assisted_'+link)
                           for state in w.states for e in events(w, state))


def test_native_parent_increases_target_propensity_for_both_shapes():
    for alpha in (.5, 1.):
        w = build_world(GenerativityParameters(capacity=6, feedback_exponent=alpha))
        # Keep precursor fixed while replacing a non-parent C by parent A.
        s, t = (8, 1, 1, 0, 2, 0), (8, 1, 2, 0, 1, 0)
        lo = sum(e.rate for e in events(w, s) if e.family.startswith('paid_') and e.target[3] == 1)
        hi = sum(e.rate for e in events(w, t) if e.family.startswith('paid_') and e.target[3] == 1)
        assert hi > lo > 0


def test_sink_constant_hazard_material_and_independent_energy_ledgers():
    p = GenerativityParameters(capacity=4, irreversible_fraction=.25)
    c = compile_world(build_world(p))
    for state in ((8, 1, 1, 1, 1, 0), (0, 0, 2, 0, 0, 1)):
        damage = [e for e in events(c['world'], state) if e.family.startswith(('damage_', 'sink_'))]
        assert sum(e.rate for e in damage) == pytest.approx(p.damage_rate*sum(state[2:5]))
        assert all(e.target[5] >= state[5] for e in damage)
    total = sum(c['observables'][name] for name in ('A', 'B', 'C', 'precursor', 'unavailable'))
    assert max(abs(c['Q'] @ total)) < 1e-10
    mu = matched_roots(c)['seed']
    final, occ = occupation_distribution(c['Q'], mu, 4.)
    ledger = physical_readouts(c, final, occ, mu)
    assert abs(ledger['bank_balance_residual']) < 1e-9
    assert abs(ledger['energy_balance_residual']) < 1e-9
    assert c['world'].energy((6, 1, 1, 0, 0, 0)) == c['world'].energy((8, 1, 0, 0, 0, 0))
    masks = closure_targets(c)
    assert np.array_equal(masks['loop']['mask'], np.array([p.capacity-s[5] < 3 for s in c['states']]))
    assert np.array_equal(masks['expanded']['mask'], np.array([p.capacity-s[5] < 4 for s in c['states']]))


def ev(family, target):
    return Event(family, family, target, 1., tuple(range(6)))


def test_depth_requires_native_assisted_descendants_and_never_restarts():
    s0, s1, s2, s3 = (8, 1, 1, 0, 0, 0), (4, 1, 1, 1, 0, 0), (0, 1, 1, 1, 1, 0), (1, 0, 2, 1, 1, 0)
    assert initial_update(WAIT, s0, ev('paid_assisted_A_to_B', s1)) == LINK1
    assert initial_update(LINK1, s1, ev('paid_assisted_B_to_C', s2)) == LINK2
    charged = (5, 0, 1, 1, 1, 0)
    assert initial_update(LINK2, s2, ev('assisted_capture', charged)) == LINK2
    assert initial_update(LINK2, charged, ev('paid_assisted_C_to_A', s3)) == SUCCESS
    assert initial_update(WAIT, s0, ev('paid_basal_B', s1)) == FAILURE
    assert initial_update(FAILURE, s0, ev('paid_assisted_A_to_B', s1)) == FAILURE
    assert initial_update(LINK1, s1, ev('thermal_build_B', (4, 1, 1, 2, 0, 0))) == FAILURE
    assert initial_update(LINK2, s2, ev('damage_C', (0, 1, 1, 1, 0, 0))) == FAILURE
    assert any_start_update(LINK2, s2, ev('paid_assisted_C_to_A', s3)) == (WAIT, 1.)
    assert any_start_update(LINK1, s1, ev('damage_B', s0)) == (WAIT, 0.)


@pytest.mark.parametrize('mode', ['initial_seed', 'any_start'])
def test_monitor_is_neutral_and_pulse_projection_preserves_physics(mode):
    c = compile_world(build_world(GenerativityParameters(capacity=3)))
    m = compile_monitor(c, mode)
    mu = matched_roots(c)['seed']
    lifted = initial_distribution(c, m, mu)
    endpoint = expm_multiply(m['Q'].T*2., lifted)
    assert np.allclose(endpoint @ m['projection'], expm_multiply(c['Q'].T*2., mu), atol=1e-12)
    assert m['projection_residual'] < 1e-12 and not m['entropy_eligible']
    if mode == 'initial_seed':
        kernel, release = pulse_kernel(c)
        lift = lifted_pulse(c, m)
        assert np.max(abs((lift @ m['projection']-m['projection'] @ kernel).data), initial=0.) < 1e-12
        assert np.allclose(kernel @ c['energy']-c['energy'], -release)
        joint = depth_profile(c, m, lifted, startup=1., horizon=2., pulse=True)
        assert joint['depth_and_retained_expansion'] == 0.  # M3 cannot retain four.
        assert 0 <= joint['depth_by_deadline'] <= 1


@pytest.mark.parametrize('Q', [
    [[-2., 2.], [3., -3.]],
    [[-2., 1., 1., 0.], [0., -1., 0., 1.], [0., 0., 0., 0.], [0., 0., 0., 0.]],
    [[-1., .4, .6, 0., 0.], [0., -2., 2., 0., 0.], [0., 3., -3., 0., 0.],
     [0., 0., 0., -4., 4.], [0., 0., 0., 1., -1.]],
])
def test_sparse_class_entropy_matches_independent_dense_solver(Q):
    q = csr_matrix(Q)
    queries = ClassQueries(q)
    for cadence in (.125, .5):
        s = queries.sampled(cadence)
        dense = analyze(q, cadence)
        assert np.allclose(s['rate'], dense['rate_per_step']/cadence, atol=1e-10)
        assert np.allclose(queries.limiting_offset(s), dense['offset'], atol=1e-10)
        for steps in (0, 1, 8, 32):
            assert np.allclose(queries.finite(s, steps*cadence), finite_history_bits(dense['P'], steps), atol=1e-10)


def test_sparse_class_solver_on_real_irreversible_chemistry():
    c = compile_world(build_world(GenerativityParameters(capacity=2, irreversible_fraction=.25)))
    queries = ClassQueries(c['Q'])
    s = queries.sampled(.25)
    dense = analyze(c['Q'], .25)
    assert len(queries.classes) == 1 and len(queries.transient) > 0
    assert np.allclose(queries.finite(s, 2.), finite_history_bits(dense['P'], 8), atol=1e-8)
    assert np.allclose(queries.limiting_offset(s), dense['offset'], atol=1e-6)


def test_rare_state_normalization_does_not_amplify_poisson_error():
    c = compile_world(build_world(GenerativityParameters(capacity=6)))
    queries = ClassQueries(c['Q'])
    sampled = queries.sampled(.25)
    assert sampled['poisson_residual'] < 1e-8
    assert np.allclose(queries.finite(sampled, 2.), finite_history_bits(sampled['P'], 8), atol=1e-8)


def test_initial_bath_and_recycled_packets_do_not_become_external_funding():
    c = compile_world(build_world(GenerativityParameters(capacity=3, supply_rate=0., beta=1.)))
    mu = matched_roots(c)['seed']
    final, occ = occupation_distribution(c['Q'], mu, 32.)
    r = physical_readouts(c, final, occ, mu)
    assert r['captured_energy'] > 0. and r['packet_bath_import'] > 0.
    assert r['drive_work'] == 0.
    assert r['external_funding_spent_lower_bound'] == 0.


def test_ongoing_detector_counts_completions_without_overlapping_restarts():
    c = compile_world(build_world(GenerativityParameters(capacity=4)))
    mu = matched_roots(c)['seed']
    primary = compile_monitor(c)
    start = initial_distribution(c, primary, mu)
    final = expm_multiply(primary['Q'].T*8., start).reshape((-1, 5))
    initial_seed_success = final[:, SUCCESS].sum()
    ongoing = compile_monitor(c, 'any_start')
    readout = detected_chain_profile(ongoing, initial_distribution(c, ongoing, mu), 8.)
    assert initial_seed_success > 0.
    assert readout['expected_detected_nonoverlapping_chains'] >= initial_seed_success-1e-12
    assert readout['detected_chain_rate'] == readout['expected_detected_nonoverlapping_chains']/8.
    assert not readout['is_population_generation_rate']


def test_sampler_uses_the_same_physics_and_recovery_does_not_condition_away_failure():
    p = GenerativityParameters(capacity=3)
    c = compile_world(build_world(p))
    mu = matched_roots(c)['seed']
    target = c['observables']['A']
    exact = expm_multiply(c['Q'].T*2., mu) @ target
    rng = np.random.default_rng(71)
    samples = [sample_events(c['world'], (6, 1, 1, 0, 0, 0), 2., rng)[0][2] for _ in range(1500)]
    assert abs(np.mean(samples)-exact) < 5*np.std(samples, ddof=1)/np.sqrt(len(samples))+.005
    recovery = pulse_readout(c, mu, pulse_time=1., delays=(2.,))
    result = recovery['delays']['2.0']
    assert result['pre_function_and_endpoint_recovery'] <= recovery['pre_function_probability']+1e-12
    _, time = reward_integral(c['Q'], mu, c['observables']['loop'], 2.)
    assert 0 <= time <= 2
