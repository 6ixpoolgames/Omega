"""Exact local conserved-observable selection and history readout probes."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from omega_v2.finite.quantum_extent import (
    evaluate,
    expand_history,
    grouped_matrix,
)
from omega_v2.finite.quantum_readers import H, cnot, initial, local_gate, observational_extent

PAULI = (
    np.array([[0, 1], [1, 0]], complex),
    np.array([[0, -1j], [1j, 0]], complex),
    np.diag([1, -1]).astype(complex),
)


def axis_operator(axis):
    axis = np.asarray(axis, float)
    if not np.isclose(np.linalg.norm(axis), 1):
        raise ValueError("A physical Bloch axis must have unit norm")
    return sum(a * p for a, p in zip(axis, PAULI, strict=True))


def axis_projectors(axis, width, signal=0):
    operator = local_gate(axis_operator(axis), signal, width)
    eye = np.eye(2**width)
    return [(eye + operator)/2, (eye - operator)/2]


def conserved_axes(generators, width, signal=0):
    """Exact local commutant; numerical rank tolerance only, no decoherence cutoff."""
    columns = []
    for pauli in PAULI:
        observable = local_gate(pauli, signal, width)
        commutators = np.concatenate([(observable @ g - g @ observable).ravel()
                                     for g in generators])
        columns.append(np.concatenate([commutators.real, commutators.imag]))
    matrix = np.column_stack(columns)
    _, singular, vh = np.linalg.svd(matrix, full_matrices=False)
    tolerance = 1e-11 * max(1.0, float(singular[0]))
    rank = int(np.count_nonzero(singular > tolerance))
    axes = vh[rank:]
    return {"dimension": 3-rank, "singular_values": singular.tolist(),
            "axes": axes.tolist(), "residual": float(np.linalg.norm(matrix @ axes.T))}


def branch_metrics(psi, stages):
    result, matrix = evaluate(psi, stages)
    off = matrix - np.diag(np.diag(matrix))
    result["offdiagonal_frobenius"] = float(np.linalg.norm(off))
    state = psi.copy()
    for unitary, _ in stages:
        state = unitary @ state
    result["observational_extent"] = observational_extent(state, stages[-1][1])
    return result, matrix


def single_axis_setup(g, copies, angle=0.0):
    """A=(sin(angle),0,cos(angle)); same aligned preparation/recombiner convention."""
    width = copies+1
    axis = [np.sin(angle), 0, np.cos(angle)]
    rotation = expm(-.5j*angle*PAULI[1])
    source = rotation @ H @ np.array([1, 0])
    psi = np.kron(source, initial(copies))
    a = local_gate(axis_operator(axis), 0, width)
    generator = sum(g * a @ local_gate(PAULI[1], j, width) for j in range(1, width))
    unitary = expm(-1j*generator)
    recombiner = local_gate(H @ rotation.conj().T, 0, width)
    stages = [(unitary, axis_projectors(axis, width)),
              (recombiner, axis_projectors([0, 0, 1], width))]
    return psi, generator, stages, axis, rotation


def single_axis_case(g, copies, angle=0.0):
    psi, generator, stages, axis, rotation = single_axis_setup(g, copies, angle)
    result, _ = branch_metrics(psi, stages)
    selection = conserved_axes([generator], copies+1)
    conditional = []
    for index in [0, 1]:
        source = rotation[:, index]
        state = stages[0][0] @ np.kron(source, initial(copies))
        environment = source.conj() @ state.reshape(2, -1)
        conditional.append(environment)
    overlap = np.vdot(conditional[1], conditional[0])
    evolved = (stages[0][0] @ psi).reshape(2, -1)
    source_rho = evolved @ evolved.conj().T
    pointer_rho = rotation.conj().T @ source_rho @ rotation
    rho_difference = (np.outer(conditional[0], conditional[0].conj())
                      - np.outer(conditional[1], conditional[1].conj()))
    trace_distance = float(np.abs(np.linalg.eigvalsh(rho_difference)).sum()/2)
    result.update(
        coupling=g, copies=copies, angle=angle, selection=selection,
        conditional_overlap_real=float(overlap.real),
        conditional_overlap_imag=float(overlap.imag),
        relative_source_coherence=float(2*abs(pointer_rho[0, 1])),
        environment_trace_distance=trace_distance,
        ideal_discrimination_error=(1-trace_distance)/2,
        analytic_overlap_error=float(abs(overlap-np.cos(2*g)**copies)),
        analytic_coherence_error=float(abs(2*abs(pointer_rho[0, 1])-abs(overlap))),
    )
    if selection["dimension"] == 1:
        result["selected_axis_alignment"] = float(abs(np.dot(selection["axes"][0], axis)))
    return result


def competing_case(ratio, mode):
    width = 3
    g = np.pi/8
    hz = g*local_gate(PAULI[2], 0, width) @ local_gate(PAULI[1], 1, width)
    hx = ratio*g*local_gate(PAULI[0], 0, width) @ local_gate(PAULI[1], 2, width)
    if mode == "ZX":
        generators = [hz, hx]
        unitaries = [expm(-1j*hz), expm(-1j*hx)]
    elif mode == "XZ":
        generators = [hx, hz]
        unitaries = [expm(-1j*hx), expm(-1j*hz)]
    elif mode == "simultaneous":
        generators = [hz+hx]
        # Two cuts within the same physical duration1, not two duration1 pulses.
        half = expm(-.5j*(hz+hx))
        unitaries = [half, half]
    else:
        raise ValueError("Unknown physical pulse order")
    psi = np.kron(H @ np.array([1, 0]), initial(2))
    readouts = {}
    for name, axis in [("Z", [0, 0, 1]), ("X", [1, 0, 0])]:
        parts = axis_projectors(axis, width)
        result, _ = branch_metrics(psi, [(u, parts) for u in unitaries])
        readouts[name+name] = result
    return {"ratio": ratio, "mode": mode,
            "physical_duration": 1 if mode == "simultaneous" else 2,
            "selection": conserved_axes(generators, width),
            "segment_dimensions": [conserved_axes([g], width)["dimension"] for g in generators],
            "readouts": readouts}


def representation_controls():
    psi, generator, stages, _, _ = single_axis_setup(np.pi/8, 1, .37)
    result, original = branch_metrics(psi, stages)
    errors = {}
    rotation = local_gate(expm(-.41j*PAULI[1]), 0, 2)
    rotated_stages = [(rotation @ u @ rotation.conj().T,
                       [rotation @ p @ rotation.conj().T for p in parts]) for u, parts in stages]
    _, rotated = branch_metrics(rotation @ psi, rotated_stages)
    errors["consistent_coordinate_change"] = float(np.max(abs(rotated-original)))
    swap = cnot(0, 1, 2) @ cnot(1, 0, 2) @ cnot(0, 1, 2)
    renamed = [(swap @ u @ swap, [swap @ p @ swap for p in parts]) for u, parts in stages]
    _, renamed_d = branch_metrics(swap @ psi, renamed)
    errors["site_permutation"] = float(np.max(abs(renamed_d-original)))
    renamed_selection = conserved_axes([swap @ generator @ swap], 2, signal=1)
    errors["renamed_selection_axis"] = float(1-abs(np.dot(
        renamed_selection["axes"][0], conserved_axes([generator], 2)["axes"][0])))
    half = expm(-.5j*generator)
    subdivided = [(half @ half, stages[0][1]), stages[1]]
    _, subdivided_d = branch_metrics(psi, subdivided)
    errors["time_subdivision"] = float(np.max(abs(subdivided_d-original)))
    identity_result, identity_d = branch_metrics(psi, [(np.eye(4), [np.eye(4)])]+stages)
    errors["identity_checkpoint"] = float(np.max(abs(identity_d-original)))
    blank_stages = [(np.kron(u, np.eye(2)), [np.kron(p, np.eye(2)) for p in parts])
                    for u, parts in stages]
    blank_result, blank_d = branch_metrics(np.kron(psi, [1, 0]), blank_stages)
    errors["blank_ancilla_D"] = float(np.max(abs(blank_d-original)))
    refinements = {}
    for name, axis in [("native", [np.sin(.37), 0, np.cos(.37)]),
                       ("competing", [np.cos(.37), 0, -np.sin(.37)])]:
        fine_stages = [(half, axis_projectors(axis, 2)), (half, stages[0][1]), stages[1]]
        fine_result, fine_d = branch_metrics(psi, fine_stages)
        _, labels = expand_history(psi, fine_stages)
        groups = [[i for i, label in enumerate(labels) if label[1:] == (a, y)]
                  for a in range(2) for y in range(2)]
        errors[name+"_refinement_coarsening"] = float(np.max(abs(grouped_matrix(fine_d, groups)-original)))
        refinements[name] = {"fine_spectral_breadth": fine_result["spectral_breadth"],
                             "coarse_spectral_breadth": result["spectral_breadth"],
                             "record_breadth": fine_result["record_breadth"]}
    # Actual independent physical product, including independent native preparations.
    product_stages = [(np.kron(u, u), [np.kron(a, b) for a in parts for b in parts])
                      for u, parts in stages]
    product_result, _ = branch_metrics(np.kron(psi, psi), product_stages)
    errors["product_spectral"] = abs(product_result["spectral_breadth"]-result["spectral_breadth"]**2)
    errors["product_records"] = abs(product_result["record_breadth"]-result["record_breadth"]**2)
    current = stages[0][0] @ psi
    rerooted, _ = branch_metrics(current, [stages[1]])
    errors["exact_present_reroot_record_law"] = float(np.max(abs(
        np.array(rerooted["record_probabilities"])-result["record_probabilities"])))
    return {"errors": errors, "refinements": refinements,
            "original": result, "blank": blank_result,
            "identity": identity_result,
            "rerooted_spectral_breadth": rerooted["spectral_breadth"]}


def physical_orientation_control():
    """Rotate coupling while holding the actual root and output reader fixed."""
    result = {}
    for name, axis in [("Z", [0, 0, 1]), ("X", [1, 0, 0])]:
        generator = (np.pi/4)*np.kron(axis_operator(axis), PAULI[1])
        parts = axis_projectors([0, 0, 1], 2)
        readout, _ = branch_metrics(initial(2), [(expm(-1j*generator), parts)])
        result[name] = {"selection": conserved_axes([generator], 2), "readout": readout}
    return result


def environment_preparation_control():
    """Same H, environment prepared unable/able to record. Supplementary diagnostic."""
    generator = (np.pi/4)*np.kron(PAULI[2], PAULI[1])
    unitary = expm(-1j*generator)
    recombiner = local_gate(H, 0, 2)
    parts = axis_projectors([0, 0, 1], 2)
    results = {}
    for name, environment in [("Z_blank", np.array([1, 0])),
                               ("Y_eigenstate", np.array([1, 1j])/np.sqrt(2))]:
        psi = np.kron(H @ np.array([1, 0]), environment)
        readout, _ = branch_metrics(psi, [(unitary, parts), (recombiner, parts)])
        env_states = [expm(-1j*sign*np.pi/4*PAULI[1]) @ environment for sign in [1, -1]]
        overlap = abs(np.vdot(env_states[0], env_states[1]))
        readout["conditional_overlap_magnitude"] = float(overlap)
        difference = (np.outer(env_states[0], env_states[0].conj())
                      - np.outer(env_states[1], env_states[1].conj()))
        readout["environment_trace_distance"] = float(np.abs(np.linalg.eigvalsh(difference)).sum()/2)
        results[name] = readout
    return results
