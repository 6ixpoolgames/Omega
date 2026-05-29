from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MatrixKey:
    matrix_family: str
    condition_id: str
    actual_control_name: str
    proxy_level: str
    probe_key: str
    flow_mode: str
    horizon_band: str


@dataclass
class MatrixCounts:
    contexts: int
    item_counts: Counter[str]
    pair_counts: Counter[tuple[str, str]]
    raw_item_mass: int
    dropped_context_items: int
    syndrome_positive_contexts: Counter[str]
    context_items: list[tuple[str, tuple[str, ...]]]
    item_edge_counts: Counter[str]
    item_edge_samples: dict[str, list[str]]

    @classmethod
    def empty(cls) -> MatrixCounts:
        return cls(0, Counter(), Counter(), 0, 0, Counter(), [], Counter(), defaultdict(list))


@dataclass
class SpectralMatrix:
    key: MatrixKey
    matrix_id: str
    items: list[str]
    matrix: np.ndarray
    eigvals: np.ndarray
    eigvecs: np.ndarray
    item_mass_covered: int
    item_mass_total: int
    dropped_item_count: int
    dropped_item_mass: int
    contexts: int
    syndrome_positive_contexts: Counter[str]
