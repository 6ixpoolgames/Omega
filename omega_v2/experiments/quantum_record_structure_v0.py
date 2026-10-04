"""Frozen routing, record-spreading and relational-invariance apparatus."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product

import networkx as nx
import numpy as np

from omega_v2.finite.quantum_profile import (
    Density,
    controlled_x,
    ensemble_density,
    single_gate,
)

PROTOCOL = "docs/research_notes/omega_v2/quantum_record_structure_protocol_v0.md"
PROTOCOL_SHA256 = "1dec4d4067a456a24a61d14fd0e071951405f9518225f4eac30aea7d6cd41bcd"
H = np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2)


@dataclass(frozen=True)
class Gate:
    op: str
    target: str
    controls: tuple[str, ...] = ()
    angle: float = 0.0

    def inverse(self):
        return Gate(self.op, self.target, self.controls, -self.angle)

    def renamed(self, mapping):
        return Gate(self.op, mapping[self.target], tuple(mapping[x] for x in self.controls),
                    self.angle)


def rotation(op, angle):
    c, s = np.cos(angle/2), np.sin(angle/2)
    if op == "RY":
        return np.array([[c, -s], [s, c]], dtype=complex)
    if op == "RZ":
        return np.diag([np.exp(-.5j*angle), np.exp(.5j*angle)])
    raise ValueError(f"unknown rotation {op}")


def apply_gate(labels, vector, gate):
    width = len(labels)
    target = labels.index(gate.target)
    if gate.op in ("CX", "CCX"):
        return controlled_x(vector, width, target,
                            {labels.index(c): 1 for c in gate.controls})
    if gate.op == "CZ":
        positions = [target, *[labels.index(c) for c in gate.controls]]
        return {basis: (-amp if all((basis >> (width-i-1)) & 1 for i in positions) else amp)
                for basis, amp in vector.items()}
    return single_gate(vector, width, target, rotation(gate.op, gate.angle))


def evolve(labels, ensemble, gates):
    result = []
    for weight, vector in ensemble:
        for gate in gates:
            vector = apply_gate(labels, vector, gate)
        result.append((weight, vector))
    return result


def initial_ensemble(labels, sources, preparation, references=None):
    """All unlisted physical registers start blank; references are virtual probes."""
    labels, sources = tuple(labels), tuple(sources)
    references = references or {}
    if references:
        vector = {0: 1+0j}
        for source in sources:
            ref = references[source]
            vector = single_gate(vector, len(labels), labels.index(ref), H)
            vector = controlled_x(vector, len(labels), labels.index(source),
                                  {labels.index(ref): 1})
        return [(1.0, vector)]
    values, vectors = np.linalg.eigh(np.asarray(preparation, complex))
    if min(values) < -1e-12 or abs(sum(values)-1) > 1e-12:
        raise ValueError("invalid source preparation")
    choices = [(float(v), vectors[:, i]) for i, v in enumerate(values) if v > 0]
    ensemble = []
    for selection in product(choices, repeat=len(sources)):
        vector, weight = {0: 1+0j}, 1.0
        for source, (probability, ket) in zip(sources, selection, strict=True):
            weight *= probability
            unitary = np.column_stack((ket, [-ket[1].conjugate(), ket[0].conjugate()]))
            vector = single_gate(vector, len(labels), labels.index(source), unitary)
        ensemble.append((weight, vector))
    return ensemble


def diagonal_source(p):
    return np.diag([p, 1-p]).astype(complex)


def routing_setup(mode, choi=False):
    if mode not in ("broadcast", "plural"):
        raise ValueError(mode)
    sources = tuple(f"S{i}" for i in range(3))
    labels = tuple(f"{bank}{i}" for bank in ("ISRDG" if choi else "SRDG") for i in range(3))
    gates = [Gate("CX", f"R{i}", ("S0" if mode == "broadcast" else f"S{i}",))
             for i in range(3)]
    gates += [Gate("CX", f"D{i}", (f"R{i}",)) for i in range(3)]
    gates += [Gate("CCX", f"G{i}", (f"D{i}", f"D{(i+1)%3}")) for i in range(3)]
    references = {source: f"I{i}" for i, source in enumerate(sources)} if choi else {}
    return labels, sources, gates, references


def routing_state(mode, cut, preparation, *, choi=False):
    if cut not in (3, 6, 9):
        raise ValueError("frozen routing cuts are 3, 6, 9")
    labels, sources, gates, references = routing_setup(mode, choi)
    ensemble = initial_ensemble(labels, sources, preparation, references)
    full = ensemble_density(labels, evolve(labels, ensemble, gates[:cut]))
    bank = {3: "R", 6: "D", 9: "G"}[cut]
    interface = (*references.values(), *sources, *(f"{bank}{i}" for i in range(3)))
    return full.partial(interface), full


def routing_bill(cut):
    return {"source_qubits": 3, "blank_qubits": 9, "CNOT": min(cut, 6),
            "Toffoli": max(0, cut-6), "elapsed_time": cut,
            "primitive_cost_model": "One common serial actuator; no energy minimization claim."}


def bath_layer(layer):
    gates = []
    for j in range(4):
        theta = float(np.pi*np.sqrt(2)*(layer+j+1) % (2*np.pi))
        phi = float(np.pi*np.sqrt(3)*(2*layer+j+1) % (2*np.pi))
        gates.extend([Gate("RY", f"E{j}", angle=theta), Gate("RZ", f"E{j}", angle=phi)])
    gates += [Gate("CZ", f"E{j+1}", (f"E{j}",)) for j in range(3)]
    return gates


def inverse(gates):
    return [g.inverse() for g in reversed(gates)]


def bath_setup():
    labels = ("X", "R", "E0", "E1", "E2", "E3", "D")
    # SWAP R,E0 = CNOT R->E0, E0->R, R->E0, all explicitly charged.
    gates = [Gate("CX", "R", ("X",)), Gate("CX", "E0", ("R",)),
             Gate("CX", "R", ("E0",)), Gate("CX", "E0", ("R",))]
    return labels, gates


def bath_layers(mode):
    if mode == "spreading":
        return [bath_layer(i) for i in range(1, 9)]
    if mode == "echo":
        return [gates for i in range(1, 5) for gates in (bath_layer(i), inverse(bath_layer(i)))]
    raise ValueError(mode)


def bath_start(p):
    labels, gates = bath_setup()
    ensemble = initial_ensemble(labels, ("X",), diagonal_source(p))
    return labels, evolve(labels, ensemble, gates)


def bath_bill(layer):
    return {"source_qubits": 1, "blank_qubits": 6, "initial_CNOT": 4,
            "rotations": 8*layer, "nearest_neighbour_CZ": 3*layer,
            "elapsed_time": 4+11*layer,
            "scope": "Driven finite chain; no thermal-reservoir or heat claim."}


def apparatus_graph(labels, sources, gates, observations, architecture=(), preparation=None):
    """Names are node keys only; incidence, preparations, time and cost are data."""
    graph = nx.DiGraph()
    preparation = diagonal_source(.8) if preparation is None else np.asarray(preparation, complex)
    for label in labels:
        graph.add_node(label, kind="qubit")
        state = preparation if label in sources else diagonal_source(1)
        prep_node = f"preparation:{label}"
        graph.add_node(prep_node, kind="preparation", density=tuple(state.flat))
        graph.add_edge(prep_node, label, kind="initializes")
    for i, gate in enumerate(gates):
        event = f"gate:{i}"
        graph.add_node(event, kind="gate", op=gate.op, angle=gate.angle, time=i+1, cost=1)
        graph.add_edge(gate.target, event, kind="target")
        for control in gate.controls:
            graph.add_edge(control, event, kind="control")
    for i, (time, registers) in enumerate(observations):
        observer = f"observation:{i}"
        graph.add_node(observer, kind="observation", time=time)
        for register in registers:
            graph.add_edge(register, observer, kind="observable")
    for i, (a, b) in enumerate(architecture):
        link = f"physical_link:{i}"
        graph.add_node(link, kind="physical_coupling")
        graph.add_edge(a, link, kind="endpoint")
        graph.add_edge(b, link, kind="endpoint")
    return graph


def isomorphic(a, b):
    return nx.is_isomorphic(a, b, node_match=lambda x, y: x == y,
                            edge_match=lambda x, y: x == y)


def rename_check(labels, sources, gates, preparation, observations, architecture=()):
    graph = apparatus_graph(labels, sources, gates, observations, architecture, preparation)
    graph_mapping = {node: f"arbitrary_{len(graph)-i}" for i, node in enumerate(graph.nodes)}
    renamed_graph = nx.relabel_nodes(graph, graph_mapping)
    mapping = {label: graph_mapping[label] for label in labels}
    reverse = {v: k for k, v in mapping.items()}
    renamed_labels = tuple(mapping[label] for label in reversed(labels))
    original = ensemble_density(labels, evolve(labels, initial_ensemble(labels, sources,
                                                                         preparation), gates))
    renamed = ensemble_density(renamed_labels, evolve(
        renamed_labels, initial_ensemble(renamed_labels, tuple(mapping[s] for s in sources),
                                         preparation), [g.renamed(mapping) for g in gates]))
    back = Density(tuple(reverse[x] for x in renamed.labels), renamed.entries).partial(labels)
    return {"graph_isomorphic": isomorphic(graph, renamed_graph),
            "full_state_error_after_mapping_back": original.distance_max(back),
            "node_mapping": graph_mapping}, original, back


def embedded_routes(swapped):
    labels = ("S0", "S1", "A", "R0", "R1", "D")
    gates = [Gate("CX", "A", ("S0",)),
             Gate("CX", "R0", ("S1" if swapped else "S0",)),
             Gate("CX", "R1", ("S0" if swapped else "S1",)),
             Gate("CX", "D", ("R0",))]
    ensemble = initial_ensemble(labels, ("S0", "S1"), diagonal_source(.5))
    state = ensemble_density(labels, evolve(labels, ensemble, gates))
    graph = apparatus_graph(labels, ("S0", "S1"), gates, [(4, ("A", "D"))],
                            preparation=diagonal_source(.5))
    return state, graph


def gate_rows(gates):
    return [{"time": i+1, **asdict(g)} for i, g in enumerate(gates)]
