import numpy as np
import pytest
from omega_v2.testbed.bng_network import (
    Network, Reaction, arithmetic, enumerate_generator, history_bits, transition,
)


def test_identical_reactants_symmetry_once():
    r = Reaction((0, 0), (1,), 0.5)
    assert r.rate((2, 0)) == 1
    assert r.rate((3, 0)) == 3
    assert r.rate((1, 0)) == 0


def test_arithmetic_rejects_function_execution():
    with pytest.raises(ValueError): arithmetic("__import__('os')", {})


def test_duplicate_channels_and_state_cap():
    a = Network(['A', 'B'], (1, 0), [Reaction((0,), (1,), 2)])
    b = Network(['A', 'B'], (1, 0), [Reaction((0,), (1,), 1)] * 2)
    assert np.array_equal(enumerate_generator(a)[1], enumerate_generator(b)[1])
    with pytest.raises(RuntimeError): enumerate_generator(a, state_cap=1)


def test_exact_two_state_law_and_history():
    q = np.array([[-1., 1.], [1., -1.]])
    p = transition(q, 0.25)
    stay = (1 + np.exp(-0.5)) / 2
    assert p[0, 0] == pytest.approx(stay)
    h = -stay*np.log2(stay) - (1-stay)*np.log2(1-stay)
    assert history_bits(p, 8)[0] == pytest.approx(8*h)
    assert np.max(abs(p@p - transition(q, .5))) < 1e-12


def test_absorbing_history_has_no_branching():
    assert history_bits(np.eye(2), 100)[0] == 0


def test_population_conservation():
    n = Network(['A','AA'], (4,0), [Reaction((0,0),(1,),.5), Reaction((1,),(0,0),1)])
    states, q = enumerate_generator(n)
    assert all(a + 2*b == 4 for a,b in states)
    assert np.max(abs(q.sum(axis=1))) == 0


def test_reaction_order_preserves_law():
    reactions=[Reaction((0,), (1,), 2),Reaction((1,), (0,), 3)]
    n=Network(['A','B'],(1,0),reactions)
    r=Network(n.species,n.initial,list(reversed(reactions)))
    assert np.array_equal(enumerate_generator(n)[1],enumerate_generator(r)[1])
