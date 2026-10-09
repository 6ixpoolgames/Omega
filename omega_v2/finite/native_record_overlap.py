"""Audit coherence/classical limits of physically anchored record overlap."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.coherent_reference import recorded_hops
from omega_v2.finite.quantum_extent import decoherence_matrix, effective_number, expand_history
from omega_v2.finite.quantum_readers import cnot, projectors
from omega_v2.finite.spatial_futuresfield import hopping, spatial_setup


def reduced_pure(state, keep, width):
    """Partial trace of an unnormalized pure vector over the complement."""
    keep = tuple(keep)
    if len(set(keep)) != len(keep) or any(i < 0 or i >= width for i in keep):
        raise ValueError("Invalid retained sites")
    other = tuple(i for i in range(width) if i not in keep)
    amplitudes = state.reshape((2,) * width).transpose(keep + other).reshape(2**len(keep), -1)
    return amplitudes @ amplitudes.conj().T


def analyze_records(psi, stages, keep, width):
    rows, _ = expand_history(psi, stages)
    final = psi.copy()
    for u, _ in stages:
        final = u @ final
    actual = reduced_pure(final, keep, width)
    overlap = sum(reduced_pure(row, keep, width) for row in rows)
    d = decoherence_matrix(rows)
    metrics = {
        "overlap_extent": effective_number(np.linalg.eigvalsh(overlap)),
        "actual_record_rank_extent": effective_number(np.linalg.eigvalsh(actual)),
        "record_basis_breadth": effective_number(actual.diagonal().real),
        "history_spectral_control": effective_number(np.linalg.eigvalsh(d)),
        "history_diagonal_breadth": effective_number(d.diagonal().real),
        "history_offdiagonal_max": float(np.max(abs(d-np.diag(d.diagonal())))),
        "actual_vs_overlap_max": float(np.max(abs(actual-overlap))),
        "amplitude_error": float(np.max(abs(rows.sum(axis=0)-final))),
        "actual_trace_error": float(abs(np.trace(actual)-1)),
        "overlap_trace_error": float(abs(np.trace(overlap)-1)),
        "global_purity_error": float(abs(np.vdot(final, final).real**2-1)),
    }
    return metrics, actual, overlap


def delayed_record_echo(refined):
    """Only actual record is after the complete echo; any middle cut is a query."""
    psi = np.array([1., 0., 0., 0.], dtype=complex)
    forward = np.kron(hopping(np.pi/4), np.eye(2))
    backward = np.kron(hopping(-np.pi/4), np.eye(2))
    final = cnot(0, 1, 2) @ backward
    stages = [(forward, projectors((0,), 2) if refined else [np.eye(4)]),
              (final, projectors((0,), 2))]
    return psi, stages


def record_copy_control():
    psi, _, stages = recorded_hops(2)
    state = psi.copy()
    for u, _ in stages:
        state = u @ state
    before_m = reduced_pure(state, (1, 2), 3)
    enlarged = np.kron(state, [1., 0., 0., 0.])
    copied = cnot(2, 4, 5) @ cnot(1, 3, 5) @ enlarged
    original_m = reduced_pure(copied, (1, 2), 5)
    all_records = reduced_pure(copied, (1, 2, 3, 4), 5)
    return {
        "before_original_memory_extent": effective_number(np.linalg.eigvalsh(before_m)),
        "after_original_memory_extent": effective_number(np.linalg.eigvalsh(original_m)),
        "after_all_memories_extent": effective_number(np.linalg.eigvalsh(all_records)),
        "before_record_basis_breadth": effective_number(before_m.diagonal().real),
        "after_original_basis_breadth": effective_number(original_m.diagonal().real),
        "after_all_records_basis_breadth": effective_number(all_records.diagonal().real),
        "global_purity_error": float(abs(np.vdot(copied, copied).real**2-1)),
    }


def overlap_controls():
    psi, stages = spatial_setup(np.pi/4, np.pi/6, np.pi/4, .37)
    metrics, actual, overlap = analyze_records(psi, stages, (1,), 2)
    eye_stages = [(np.eye(4), [np.eye(4)])] + stages
    _, ai, wi = analyze_records(psi, eye_stages, (1,), 2)
    enlarged = [(np.kron(u, np.eye(2)), [np.kron(p, np.eye(2)) for p in ps]) for u, ps in stages]
    mb, ab, wb = analyze_records(np.kron(psi, [1., 0.]), enlarged, (1, 2), 3)
    rng = np.random.default_rng(846)
    ws, _ = np.linalg.qr(rng.normal(size=(2, 2))+1j*rng.normal(size=(2, 2)))
    we, _ = np.linalg.qr(rng.normal(size=(2, 2))+1j*rng.normal(size=(2, 2)))
    w = np.kron(ws, we)
    rotated = [(w@u@w.conj().T, [w@p@w.conj().T for p in ps]) for u, ps in stages]
    _, ar, wr = analyze_records(w@psi, rotated, (1,), 2)
    product = [(np.kron(u, u), [np.kron(p, q) for p in ps for q in ps]) for u, ps in stages]
    mp, ap, wp = analyze_records(np.kron(psi, psi), product, (1, 3), 4)
    return {
        "identity_error": float(max(np.max(abs(ai-actual)), np.max(abs(wi-overlap)))),
        "blank_matrix_error": float(max(np.max(abs(ab-np.kron(actual, np.diag([1., 0.])))),
                                         np.max(abs(wb-np.kron(overlap, np.diag([1., 0.])))))),
        "blank_extent_error": float(abs(mb["overlap_extent"]-metrics["overlap_extent"])),
        "covariance_error": float(max(np.max(abs(ar-we@actual@we.conj().T)),
                                       np.max(abs(wr-we@overlap@we.conj().T)))),
        "product_matrix_error": float(max(np.max(abs(ap-np.kron(actual, actual))),
                                           np.max(abs(wp-np.kron(overlap, overlap))))),
        "product_extent_error": float(abs(mp["overlap_extent"]-metrics["overlap_extent"]**2)),
    }
