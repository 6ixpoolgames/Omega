from itertools import product

import numpy as np
import pytest

from omega_v2.finite.multiway_composition import (
    audit_factorization,
    audit_projection,
    audit_square,
)
from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw


def law4(matrix, clock="continuous"):
    return FiniteContinuationLaw(tuple(product((0, 1), repeat=2)), matrix, clock=clock)


def test_independent_ctmc_and_discrete_product_factorize():
    q = np.array([[-1., 1.], [2., -2.]])
    law = law4(np.kron(q, np.eye(2)) + np.kron(np.eye(2), 3*q))
    audit = audit_factorization(law, ((0,), (1,)))
    assert audit.holds and audit.max_error == 0 and len(audit.local_laws) == 2
    k = np.array([[.7, .3], [.2, .8]])
    assert audit_factorization(law4(np.kron(k, k), "discrete"), ((0,), (1,))).holds


def test_contextual_gate_has_diamond_but_not_rate_independence():
    q = np.array([[-2., 1., 1., 0.], [1., -2., 0., 1.],
                  [1., 0., -8., 7.], [0., 1., 7., -8.]])
    law = law4(q)
    square = audit_square(law, (0, 0), (1, 0), (0, 1))
    assert square.two_orders_exist and not square.rate_preserving
    audit = audit_factorization(law, ((0,), (1,)))
    assert not audit.holds and audit.marginal_error == 6


def test_shared_coin_has_matching_marginals_but_fails_product_law():
    kernel = np.tile([.5, 0, 0, .5], (4, 1))
    audit = audit_factorization(law4(kernel, "discrete"), ((0,), (1,)))
    assert not audit.holds and audit.marginal_error == 0 and audit.max_error == .25


def test_exclusion_and_enabling_do_not_gain_an_independence_certificate():
    token = FiniteContinuationLaw(((0, 0), (1, 0), (0, 1)),
                                  ((-2, 1, 1), (0, 0, 0), (0, 0, 0)), clock="continuous")
    assert not audit_factorization(token, ((0,), (1,))).cartesian
    assert not audit_square(token, (0, 0), (1, 0), (0, 1)).two_orders_exist
    chain = law4([[-1, 0, 1, 0], [0, -1, 0, 1], [0, 0, -1, 1], [0, 0, 0, 0]])
    assert not audit_factorization(chain, ((0,), (1,))).holds


@pytest.mark.parametrize("blocks", [((0,),), ((0,), (0,)), ((0,), (2,)), ((), (0, 1))])
def test_factorization_rejects_omitting_or_duplicating_physical_coordinates(blocks):
    with pytest.raises(ValueError):
        audit_factorization(law4(np.zeros((4, 4))), blocks)


def test_projected_frame_is_markov_only_if_hidden_context_does_not_change_its_law():
    q = np.array([[-1., 1.], [1., -1.]])
    independent = law4(np.kron(q, np.eye(2)) + np.kron(np.eye(2), q))
    audit = audit_projection(independent, lambda state: state[0])
    assert audit.markov and np.allclose(audit.projected_law.operator, q)
    gated = law4([[-2, 1, 1, 0], [1, -2, 0, 1], [1, 0, -8, 7], [0, 1, 7, -8]])
    audit = audit_projection(gated, lambda state: state[1])
    assert not audit.markov and audit.projected_law is None and audit.max_error == 6
    constant = audit_projection(independent, lambda state: ())
    assert constant.markov and constant.projected_law.operator[0, 0] == 0
