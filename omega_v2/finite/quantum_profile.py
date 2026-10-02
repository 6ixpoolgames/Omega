"""Small exact quantum circuits and labelled entropy profiles.

Sparse support is a computational convenience: omitted matrix entries are zero,
not discarded outcomes. No truncation, sampling, or physical quotient is used.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

import numpy as np


def select_bits(value, positions, width):
    result = 0
    for position in positions:
        result = (result << 1) | ((value >> (width - position - 1)) & 1)
    return result


@dataclass
class Density:
    labels: tuple[str, ...]
    entries: dict[tuple[int, int], complex]

    def partial(self, keep):
        keep = tuple(keep)
        if len(set(keep)) != len(keep) or not set(keep) <= set(self.labels):
            raise ValueError("partial trace requires distinct existing labels")
        positions = [self.labels.index(label) for label in keep]
        discarded = [i for i, label in enumerate(self.labels) if label not in keep]
        width = len(self.labels)
        basis = {x for pair in self.entries for x in pair}
        maps = {x: (select_bits(x, positions, width),
                    select_bits(x, discarded, width)) for x in basis}
        entries = defaultdict(complex)
        for (row, col), value in self.entries.items():
            r, re = maps[row]
            c, ce = maps[col]
            if re == ce:
                entries[r, c] += value
        return Density(keep, dict(entries))

    def matrix(self):
        """Exact nonzero-support matrix; missing basis rows are zero eigenvalues."""
        basis = sorted({x for pair, v in self.entries.items() if v != 0 for x in pair})
        indices = {x: i for i, x in enumerate(basis)}
        result = np.zeros((len(basis), len(basis)), dtype=complex)
        for (r, c), value in self.entries.items():
            if value:
                result[indices[r], indices[c]] += value
        return result

    def trace(self):
        return float(sum(v.real for (r, c), v in self.entries.items() if r == c))

    def entropy(self):
        matrix = self.matrix()
        if not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=0):
            raise ValueError("non-Hermitian state")
        if not np.isclose(self.trace(), 1, atol=1e-12, rtol=0):
            raise ValueError("entropy requires a normalized state")
        eig = np.linalg.eigvalsh(matrix)
        if eig.min(initial=0) < -1e-12:
            raise ValueError("non-positive state")
        # Only rounding-scale negative eigenvalues are clipped. Positive weights
        # of any size remain in the entropy sum.
        eig = eig[eig > 0]
        return float(-np.dot(eig, np.log2(eig)))

    def distance_max(self, other):
        if self.labels != other.labels:
            raise ValueError("matrix comparison needs the same labelled basis")
        return float(max((abs(self.entries.get(k, 0) - other.entries.get(k, 0))
                          for k in self.entries.keys() | other.entries.keys()), default=0))

    def law(self):
        return {r: float(v.real) for (r, c), v in self.entries.items() if r == c and v.real > 0}


def ensemble_density(labels, ensemble):
    entries = defaultdict(complex)
    for weight, vector in ensemble:
        for r, a in vector.items():
            for c, b in vector.items():
                entries[r, c] += weight * a * b.conjugate()
    return Density(tuple(labels), dict(entries))


def single_gate(vector, width, target, gate):
    mask = 1 << (width - target - 1)
    result = defaultdict(complex)
    for basis, amplitude in vector.items():
        old = int(bool(basis & mask))
        for new in (0, 1):
            coefficient = gate[new, old]
            if coefficient:
                result[(basis & ~mask) | (new * mask)] += coefficient * amplitude
    return dict(result)


def controlled_x(vector, width, target, controls):
    """controls is a mapping of physical bit positions to required 0/1 values."""
    mask = 1 << (width - target - 1)
    result = {}
    for basis, amplitude in vector.items():
        active = all(((basis >> (width - c - 1)) & 1) == v for c, v in controls.items())
        result[basis ^ mask if active else basis] = amplitude
    return result


def swap(vector, width, a, b):
    ma, mb = 1 << (width-a-1), 1 << (width-b-1)
    return {basis ^ (ma | mb) if bool(basis & ma) != bool(basis & mb) else basis: amp
            for basis, amp in vector.items()}


def profile(state):
    """Full labelled F:complement profile, plus explicitly lossy size summaries."""
    n = len(state.labels)
    full_mask = (1 << n) - 1
    entropies = {0: 0.0, full_mask: state.entropy()}
    for mask in range(1, full_mask):
        keep = [name for i, name in enumerate(state.labels) if mask & (1 << i)]
        entropies[mask] = state.partial(keep).entropy()
    rows, grouped = [], defaultdict(list)
    for mask in range(1, full_mask):
        info = entropies[mask] + entropies[full_mask ^ mask] - entropies[full_mask]
        rows.append({"mask": mask, "entropy_bits": entropies[mask],
                     "mutual_information_bits": info})
        grouped[mask.bit_count()].append(info)
    return {
        "labels": state.labels, "mask_rule": "bit i selects labels[i]",
        "whole_entropy_bits": entropies[full_mask], "labelled_fragments": rows,
        "by_size": [{"k": k, "count": len(values), "min_bits": min(values),
                     "mean_bits": float(np.mean(values)), "max_bits": max(values)}
                    for k, values in sorted(grouped.items())],
    }


def mutual_information(state, a, b):
    if set(a) & set(b):
        raise ValueError("mutual information needs disjoint factors")
    return state.partial(a).entropy() + state.partial(b).entropy() - state.partial((*a, *b)).entropy()


def dephase(state):
    return Density(state.labels, {(r, c): v for (r, c), v in state.entries.items() if r == c})


def contract_inputs(choi, preparations):
    """Normalized Choi contraction d*Tr_I[(rho^T tensor 1)J].

    entries of rho have the same row/column indices as the input block of J;
    the transpose in the link rule is already accounted for by the trace.
    """
    inputs = list(preparations)
    out = [label for label in choi.labels if label not in inputs]
    input_positions = [choi.labels.index(label) for label in inputs]
    output_positions = [choi.labels.index(label) for label in out]
    width = len(choi.labels)
    result = defaultdict(complex)
    for (r, c), amplitude in choi.entries.items():
        factor = 2 ** len(inputs)
        for label, position in zip(inputs, input_positions, strict=True):
            ir, ic = (r >> (width-position-1)) & 1, (c >> (width-position-1)) & 1
            factor *= preparations[label][ir, ic]
        result[select_bits(r, output_positions, width),
               select_bits(c, output_positions, width)] += amplitude * factor
    return Density(tuple(out), dict(result))


def tensor(a, b):
    width = len(b.labels)
    return Density((*a.labels, *b.labels),
                   {((ar << width) | br, (ac << width) | bc): av*bv
                    for (ar, ac), av in a.entries.items() for (br, bc), bv in b.entries.items()})


def channel_choi(unitary, inputs, outputs):
    """Pure unitary channel Choi with input legs followed by output legs."""
    d = 2 ** len(inputs)
    if unitary.shape != (d, d) or len(outputs) != len(inputs):
        raise ValueError("unitary dimension does not match labels")
    vector = {(i << len(outputs)) | o: complex(unitary[o, i] / np.sqrt(d))
              for i in range(d) for o in range(d) if unitary[o, i] != 0}
    return ensemble_density((*inputs, *outputs), [(1.0, vector)])


def size_multisets(data):
    return {k: sorted(r["mutual_information_bits"] for r in data["labelled_fragments"]
                      if r["mask"].bit_count() == k)
            for k in range(1, len(data["labels"]))}


def record_diagnostics(actual, rounds):
    measured = dephase(actual)
    records = [name for name in actual.labels if name[0] in "RMDK"]
    results = []
    for j in range(1, rounds+1):
        source = f"S{j}"
        entropy = measured.partial([source]).entropy()
        infos = {r: mutual_information(measured, [source], [r]) for r in records}
        downstream = measured.partial([source, f"D{j}"])
        joint = downstream.law()
        results.append({
            "source": source, "source_entropy_bits": entropy,
            "single_record_information_bits": infos,
            "singleton_90_percent_readers": [r for r, v in infos.items() if v >= .9*entropy],
            "downstream_information_bits": infos[f"D{j}"],
            "downstream_source_joint_law": [joint.get(i, 0.0) for i in range(4)],
            "source_equal_downstream_probability": joint.get(0, 0)+joint.get(3, 0),
            "all_record_information_bits": mutual_information(measured, [source], records),
        })
    # Retain pairwise record correlations to attribute copying/common-cause effects.
    pairs = {f"{a}:{b}": mutual_information(measured, [a], [b])
             for a, b in combinations(records, 2)}
    return {"sources": results, "record_pair_information_bits": pairs}
