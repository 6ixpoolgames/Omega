"""Bound-constrained Holevo readout; ensemble/region selection stays explicit."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.coherent_reference import psd_eigenvalues, recorded_hops
from omega_v2.finite.native_record_overlap import delayed_record_echo, reduced_pure
from omega_v2.finite.quantum_eraser import eraser_setup
from omega_v2.finite.quantum_extent import effective_number, expand_history
from omega_v2.finite.quantum_readers import initial, projectors


def entropy(rho, tolerance=1e-12):
    values, _ = psd_eigenvalues(rho, tolerance)
    if not np.isclose(values.sum(), 1, atol=tolerance, rtol=0):
        raise ValueError("Normalized density required")
    positive = values[values > 0]
    return float(-np.dot(positive, np.log(positive)))


def holevo_extent(weights, states):
    weights = np.asarray(weights, dtype=float)
    if (weights.ndim != 1 or not np.isfinite(weights).all()
            or np.any(weights < 0) or not np.isclose(weights.sum(), 1, atol=1e-12, rtol=0)):
        raise ValueError("Normalized nonnegative probabilities required")
    states = [np.asarray(rho, dtype=complex) for rho in states]
    if len(states) != len(weights) or not states:
        raise ValueError("One density per probability required")
    if any(rho.shape != states[0].shape for rho in states):
        raise ValueError("Common output space required")
    conditional_entropy = sum(p * entropy(rho) for p, rho in zip(weights, states))
    average = sum(p * rho for p, rho in zip(weights, states))
    output_entropy = entropy(average)
    chi = output_entropy - conditional_entropy
    upper = float(np.log(effective_number(weights)))
    if chi < -1e-10 or chi > upper + 1e-10:
        raise ArithmeticError("Holevo bounds violated")
    return {
        "extent": float(np.exp(chi)), "chi": float(chi),
        "classical_upper": float(np.exp(upper)),
        "output_entropy": output_entropy,
        "mean_conditional_entropy": float(conditional_entropy),
        "bound_error": float(max(0., -chi, chi-upper)),
    }


def history_ensemble(psi, stages, keep, width):
    rows, labels = expand_history(psi, stages)
    weights = np.sum(abs(rows)**2, axis=1)
    states = []
    for p, row in zip(weights, rows):
        states.append(reduced_pure(row/np.sqrt(p), keep, width)
                      if p > 0 else np.eye(2**len(keep))/2**len(keep))
    result = holevo_extent(weights, states)
    actual = reduced_pure(rows.sum(axis=0), keep, width)
    average = sum(p * rho for p, rho in zip(weights, states))
    result["actual_vs_ensemble_max"] = float(np.max(abs(actual-average)))
    result["actual_output_entropy"] = entropy(actual)
    return result, rows, labels


def record_certificate(rows, record_projections):
    """Algebraic correlation only; native selection needs independent evidence."""
    if len(rows) != len(record_projections):
        raise ValueError("One proposed record cell per history required")
    final = rows.sum(axis=0)
    eye = np.eye(len(final))
    errors = [float(np.max(abs(sum(record_projections)-eye)))]
    for i, r in enumerate(record_projections):
        errors.extend([float(np.max(abs(r-r.conj().T))), float(np.max(abs(r@r-r))),
                       float(np.max(abs(r@final-rows[i])))])
        for s in record_projections[:i]:
            errors.append(float(np.max(abs(r@s))))
    return float(max(errors))


def recorded_profile(count):
    psi, _, stages = recorded_hops(count)
    width = count+1
    result, rows, _ = history_ensemble(psi, stages, tuple(range(1, width)), width)
    result["records"] = count
    result["record_certificate_error"] = record_certificate(
        rows, projectors(tuple(range(1, width)), width))
    refinement_error = 0.
    for n in range(1, count):
        parent = projectors(tuple(range(1, n+1)), width)
        children = projectors(tuple(range(1, n+2)), width)
        step = stages[n][0]
        for h, r in enumerate(parent):
            refinement_error = max(refinement_error, float(np.max(abs(
                children[2*h]+children[2*h+1]-step@r@step.conj().T))))
    result["refinement_error"] = refinement_error
    return result


def eraser_profile(mode, leak_angle):
    _, _, action, mark, leak = eraser_setup(mode, leak_angle)
    conditional = []
    for path in (0, 1):
        state = initial(4)
        if path:
            state = np.roll(state, 8)
        if mode != "unmarked":
            state = leak@mark@state
        conditional.append(action@state)
    result = {"mode": mode, "leak_angle": float(leak_angle)}
    for name, keep in (("marker", (1,)), ("environment", (2,)),
                       ("joint_record", (1, 2)), ("whole_conditional_system", (0, 1, 2, 3))):
        result[name] = holevo_extent([.5, .5], [reduced_pure(v, keep, 4)
                                               for v in conditional])
    return result


def echo_profiles():
    result = {}
    for refined in (False, True):
        psi, stages = delayed_record_echo(refined)
        metrics, rows, labels = history_ensemble(psi, stages, (1,), 2)
        memory = projectors((1,), 2)
        metrics["proposed_record_certificate_error"] = record_certificate(
            rows, [memory[label[-1]] for label in labels])
        result["refined" if refined else "endpoint"] = metrics
        if refined:
            grouped = np.array([sum((v for v, label in zip(rows, labels) if label[-1] == h),
                                    np.zeros(4, dtype=complex)) for h in (0, 1)])
            weights = np.sum(abs(grouped)**2, axis=1)
            states = [reduced_pure(v/np.sqrt(p), (1,), 2) if p > 0 else np.eye(2)/2
                      for p, v in zip(weights, grouped)]
            result["coherently_grouped"] = holevo_extent(weights, states)
            result["grouped_record_certificate_error"] = record_certificate(grouped, memory)
    return result


def ensemble_controls():
    a = np.diag([.7, .3]).astype(complex)
    v = np.array([1., 1.])/np.sqrt(2)
    b = np.outer(v, v)
    p = np.array([.3, .7])
    base = holevo_extent(p, [a, b])
    noise = np.diag([.2, .8])
    rng = np.random.default_rng(108)
    w, _ = np.linalg.qr(rng.normal(size=(2, 2))+1j*rng.normal(size=(2, 2)))
    product = holevo_extent(np.kron(p, p), [np.kron(x, y) for x in (a, b) for y in (a, b)])
    orthogonal = [np.kron(np.diag([1., 0.]), a), np.kron(np.diag([0., 1.]), a)]
    return {
        "base": base,
        "identical_mixed": holevo_extent(p, [a, a]),
        "orthogonal_mixed": holevo_extent(p, orthogonal),
        "common_mixed_ancilla_error": abs(holevo_extent(p, [np.kron(x, noise) for x in (a, b)])["extent"]-base["extent"]),
        "product_error": abs(product["extent"]-base["extent"]**2),
        "covariance_error": abs(holevo_extent(p, [w@x@w.conj().T for x in (a, b)])["extent"]-base["extent"]),
        "relabeling_error": abs(holevo_extent(p[::-1], [b, a])["extent"]-base["extent"]),
        "duplicate_label_error": abs(holevo_extent([.1, .2, .7], [a, a, b])["extent"]-base["extent"]),
    }
