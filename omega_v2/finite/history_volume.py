"""Finite observational implementation of the adopted normalized frame volume.

X is the complete state at two or three declared physical times. R is a
projection of that sampled history. Thus I(X;R)=H(R), and log2 V=H(R)-H(X).
These are historical views, not cost-free archives available at the final cut.
All coordinate subsets and joint content are retained. Coverage budgets are
observational footprints, not physical decoder or control costs.
"""

import numpy as np
from scipy.special import xlogy


def entropy(p):
    return float(-np.sum(xlogy(p, p)) / np.log(2))


class HistoryVolume:
    def __init__(self, values, coordinate_groups):
        self.values = np.asarray(values)
        self.n, self.d = self.values.shape
        if len(coordinate_groups) != self.d:
            raise ValueError("One declared resource group per coordinate required")
        self.full = (1 << self.d) - 1
        self.codes, self.widths, self.costs = [], [], []
        self.groups = tuple(coordinate_groups)
        self.group_count = max(self.groups) + 1
        for mask in range(self.full + 1):
            cols = [i for i in range(self.d) if mask & (1 << i)]
            codes = (
                np.unique(self.values[:, cols], axis=0, return_inverse=True)[1]
                if cols
                else np.zeros(self.n, dtype=int)
            )
            self.codes.append(codes)
            self.widths.append(int(codes.max()) + 1)
            self.costs.append(
                tuple(sum(self.groups[i] == g for i in cols) for g in range(self.group_count))
            )
        if self.widths[-1] != self.n:
            raise ValueError("Full coordinate tuple must distinguish physical states")
        self.costs = np.asarray(self.costs)
        self.full_inverse = np.argsort(self.codes[-1])
        self.parents, self.child_maps = {}, {}
        for mask in range(self.full):
            parent = min(
                (mask | (1 << i) for i in range(self.d) if not mask & (1 << i)),
                key=lambda p: self.widths[p],
            )
            self.parents[mask] = parent
            mapping = np.empty(self.widths[parent], dtype=int)
            mapping[self.codes[parent]] = self.codes[mask]
            self.child_maps[mask] = mapping
        self.refinement_masks = [mask for mask in range(self.full + 1) if mask.bit_count() <= 2]
        self._three_time = {}

    def pair_profile(self, p, kernel):
        joint = p[:, None] * kernel
        if joint.min() < 0 or abs(joint.sum() - 1) > 1e-9:
            raise ValueError("Invalid physical pair law; no clipping or renormalization")
        hfull = entropy(joint)
        retained = {self.full: joint[np.ix_(self.full_inverse, self.full_inverse)]}
        uses = np.bincount(list(self.parents.values()), minlength=self.full + 1)
        history, present, initial = (
            np.empty(self.full + 1),
            np.empty(self.full + 1),
            np.empty(self.full + 1),
        )
        # A subset is marginalized from an already-computed superset. This avoids
        # rereading the full n^2 pair table for every one of the 1,024 frames.
        for mask in range(self.full, -1, -1):
            if mask == self.full:
                matrix = retained[mask]
            else:
                parent, child = self.parents[mask], self.child_maps[mask]
                width = self.widths[mask]
                pair_codes = child[:, None] * width + child[None, :]
                matrix = np.bincount(
                    pair_codes.ravel(), weights=retained[parent].ravel(), minlength=width**2
                ).reshape(width, width)
                uses[parent] -= 1
                if uses[parent] == 0:
                    del retained[parent]
                if uses[mask]:
                    retained[mask] = matrix
            history[mask] = entropy(matrix)
            initial[mask] = entropy(matrix.sum(axis=1))
            present[mask] = entropy(matrix.sum(axis=0))
        if np.max(history - hfull) > 1e-9:
            raise ValueError("A projected history exceeds the full history")
        return {
            "whole_history_bits": hfull,
            "history_bits": history,
            "initial_bits": initial,
            "present_bits": present,
            "history_log2_volume": history - hfull,
            "present_log2_volume": present - hfull,
        }

    def three_cut_profile(self, p, step, key):
        """Temporal-refinement check on all one/two-coordinate frames and whole."""
        if key not in self._three_time:
            self._three_time[key] = {}
            for mask in self.refinement_masks:
                codes, width = self.codes[mask], self.widths[mask]
                groups = [np.flatnonzero(codes == k) for k in range(width)]
                future = np.column_stack([step[:, members].sum(axis=1) for members in groups])
                self._three_time[key][mask] = groups, future
        row_h = -np.sum(xlogy(step, step), axis=1) / np.log(2)
        whole = entropy(p) + float(p @ row_h) + float((p @ step) @ row_h)
        weighted = p[:, None] * step
        rows = []
        for mask in self.refinement_masks:
            groups, future = self._three_time[key][mask]
            incoming = np.vstack([weighted[members].sum(axis=0) for members in groups])
            h = 0.0
            for members in groups:
                # Each slice is P(R0, R1=current group, R2).
                h += entropy(incoming[:, members] @ future[members])
            rows.append({"mask": mask, "history_bits": h, "log2_volume": h - whole})
        rows.append({"mask": self.full, "history_bits": whole, "log2_volume": 0.0})
        return {"whole_history_bits": whole, "frames": rows}

    def envelope(self, profile):
        result = []
        ranges = [range(int(self.costs[:, i].max()) + 1) for i in range(self.group_count)]
        from itertools import product

        for budget in product(*ranges):
            allowed = np.flatnonzero(np.all(self.costs <= budget, axis=1))
            h = profile["history_bits"]
            best = int(allowed[np.argmax(h[allowed])])
            result.append(
                {
                    "coverage": list(budget),
                    "best_mask": best,
                    "history_bits": float(h[best]),
                    "log2_volume": float(h[best] - profile["whole_history_bits"]),
                    "volume": float(np.exp2(h[best] - profile["whole_history_bits"])),
                }
            )
        return result

    def content_catalog(self):
        """Information-equivalent views grouped, with every physical footprint kept."""
        groups = {}
        for mask, code in enumerate(self.codes):
            first = {}
            canonical = tuple(first.setdefault(int(c), len(first)) for c in code)
            groups.setdefault(canonical, []).append(mask)
        result = []
        for masks in groups.values():
            minimal = [
                mask
                for mask in masks
                if not any(
                    np.all(self.costs[other] <= self.costs[mask])
                    and np.any(self.costs[other] < self.costs[mask])
                    for other in masks
                )
            ]
            result.append({"masks": masks, "minimal_coverage_masks": minimal})
        return result
