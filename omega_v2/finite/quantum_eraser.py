"""Explicit reversal, conditional erasure and leakage, with all outcomes kept."""

from __future__ import annotations

import numpy as np

from omega_v2.finite.native_record_overlap import reduced_pure
from omega_v2.finite.quantum_extent import effective_number, evaluate
from omega_v2.finite.quantum_readers import H, cnot, initial, local_gate, projectors

MODES = ("unmarked", "retain", "reverse_marker", "eraser_early", "eraser_delayed", "reverse_all")


def controlled_y(control, target, angle, width=4):
    y = np.array([[0., -1j], [1j, 0.]])
    rotate = np.cos(angle)*np.eye(2)-1j*np.sin(angle)*y
    p0, p1 = projectors((control,), width)
    return p0 + p1 @ local_gate(rotate, target, width)


def eraser_setup(mode, leak_angle=0., phase=0.):
    if mode not in MODES:
        raise ValueError("Unknown eraser treatment")
    mark = cnot(0, 1, 4)
    leak = controlled_y(1, 2, leak_angle)
    prefix = local_gate(H, 0, 4)
    if mode != "unmarked":
        prefix = leak @ mark @ prefix
    marker_action = np.eye(16, dtype=complex)
    if mode == "reverse_marker":
        marker_action = mark
    elif mode == "reverse_all":
        marker_action = mark @ leak.conj().T
    elif mode in ("eraser_early", "eraser_delayed"):
        marker_action = local_gate(H, 1, 4)
    signal = cnot(0, 3, 4) @ local_gate(H, 0, 4) @ local_gate(np.diag([1., np.exp(1j*phase)]), 0, 4)
    remaining = marker_action @ signal if mode == "eraser_delayed" else signal @ marker_action
    return prefix, remaining, marker_action, mark, leak


def trace_distance(a, b):
    return float(np.sum(abs(np.linalg.eigvalsh(a-b)))/2)


def eraser_case(mode, leak_angle=0., phase=0.):
    prefix, remaining, marker_action, mark, leak = eraser_setup(mode, leak_angle, phase)
    psi = initial(4)
    marked = prefix @ psi
    final = remaining @ marked
    outputs = projectors((3, 1, 2), 4)
    result, _ = evaluate(psi, [(prefix, projectors((0,), 4)), (remaining, outputs)])
    probability = np.array(result["record_probabilities"]).reshape(2, 2, 2)
    signal = probability.sum(axis=(1, 2))
    marker = probability.sum(axis=(0, 2))
    conditional = []
    log_conditional = 0.
    for m in range(2):
        if marker[m] > 1e-12:
            p = probability[:, m, :].sum(axis=1)/marker[m]
            conditional.append(p.tolist())
            log_conditional += marker[m]*np.log(effective_number(p))
        else:
            conditional.append(None)
    endpoint_only, _ = evaluate(psi, [(remaining @ prefix, outputs)])
    branch_rows = np.array([p @ marked for p in projectors((0,), 4)])
    evolved_rows = np.array([remaining @ v for v in branch_rows])
    gram_error = float(np.max(abs(branch_rows@branch_rows.conj().T-evolved_rows@evolved_rows.conj().T)))

    path_records = []
    marker_path_laws = []
    for path in [0, 1]:
        state = initial(4)
        if path:
            state = np.zeros(16, dtype=complex)
            state[8] = 1
        if mode != "unmarked":
            state = leak @ mark @ state
        state = marker_action @ state
        path_records.append(reduced_pure(state, (1, 2), 4))
        marker_path_laws.append(reduced_pure(state, (1,), 4).diagonal().real)
    # In delayed mode compare actual R marginal immediately before marker H.
    before_delayed = final if mode != "eraser_delayed" else marker_action.conj().T @ final
    r_before = reduced_pure(before_delayed, (3,), 4)
    r_after = reduced_pure(final, (3,), 4)
    eta = np.cos(leak_angle)
    expected_p0 = .5
    if mode in ("unmarked", "reverse_all"):
        expected_p0 = (1+np.cos(phase))/2
    elif mode == "reverse_marker":
        expected_p0 = (1+eta*np.cos(phase))/2
    conditional_error = 0.
    if mode in ("eraser_early", "eraser_delayed"):
        conditional_error = max(abs(conditional[m][0]-(1+(-1)**m*eta*np.cos(phase))/2) for m in range(2))
    rm = probability.sum(axis=2)
    result.update(
        mode=mode, leak_angle=leak_angle, phase=phase, signal_probabilities=signal.tolist(),
        marker_weights=marker.tolist(), conditional_signal=conditional,
        signal_breadth=effective_number(signal), marker_breadth=effective_number(marker),
        signal_marker_breadth=effective_number(rm.ravel()),
        conditional_geometric_signal_breadth=float(np.exp(log_conditional)),
        path_record_trace_distance=trace_distance(*path_records),
        specified_marker_readout_path_tv=float(np.sum(abs(marker_path_laws[0]-marker_path_laws[1]))/2),
        unconditional_formula_error=float(abs(signal[0]-expected_p0)),
        conditional_formula_error=float(conditional_error),
        total_probability_error=float(abs(probability.sum()-1)),
        joint_entropy_chain_error=float(abs(np.log(effective_number(rm.ravel()))-np.log(effective_number(marker))-log_conditional)),
        branch_inner_product_error=gram_error,
        final_only_born_error=float(np.max(abs(np.array(endpoint_only["record_probabilities"])-probability.ravel()))),
        reroot_error=float(np.max(abs(remaining @ marked - remaining @ prefix @ psi))),
        delayed_signal_marginal_error=float(np.max(abs(r_after-r_before))),
        global_purity_error=float(abs(np.vdot(final, final).real**2-1)),
    )
    return result, final
