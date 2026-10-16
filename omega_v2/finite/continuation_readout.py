"""Declared-frame diagnostics of an actual finite joint Markov law.

No average over frames, optimized input, noise quotient or signed value score.
"""

import numpy as np
from scipy.sparse import csr_matrix

from omega_v2.finite.local_flow import entropy, mutual


def projection(values, columns):
    n = len(values)
    if columns:
        _, codes = np.unique(values[:, columns], axis=0, return_inverse=True)
    else:
        codes = np.zeros(n, dtype=int)
    matrix = csr_matrix((np.ones(n), (np.arange(n), codes)), shape=(n, int(codes.max()) + 1))
    return codes, matrix


class ContinuationReadout:
    def __init__(self, model, frame_columns):
        self.model = model
        self.frames = {
            mask: projection(model.values, columns) for mask, columns in frame_columns.items()
        }
        self.single = [projection(model.values, [i])[1] for i in range(model.values.shape[1])]
        self.rest = [
            projection(model.values, [j for j in range(model.values.shape[1]) if j != i])[1]
            for i in range(model.values.shape[1])
        ]
        self._cache = {}

    def prepare(self, lag):
        if lag in self._cache:
            return self._cache[lag]
        k = self.model.evolution(lag)[0]
        futures, response = {}, []
        for mask, (_, frame) in self.frames.items():
            future = np.asarray((frame.T @ k.T).T)
            futures[mask] = future
            contrast = np.zeros_like(self.model.rates)
            for c, rates in enumerate(self.model.rates):
                active = np.flatnonzero(rates)
                contrast[c, active] = 0.5 * np.abs(
                    future[active] - future[self.model.targets[c, active]]
                ).sum(axis=1)
            response.append(contrast)
        rest_futures = [np.asarray((frame.T @ k.T).T) for frame in self.rest]
        self._cache[lag] = futures, np.asarray(response), rest_futures
        return self._cache[lag]

    def profiles(self, p, lag):
        futures, contrast, rest_futures = self.prepare(lag)
        flux = self.model.rates * p
        rates = flux.sum(axis=1)
        weights = np.divide(flux, rates[:, None], out=np.zeros_like(flux), where=rates[:, None] > 0)
        response = np.einsum("mcx,cx->mc", contrast, weights)
        held = []
        for future in futures.values():
            joint = p[:, None] * future
            held.append([mutual(single.T @ joint) for single in self.single])
        incremental = []
        for rest, future in zip(self.rest, rest_futures, strict=True):
            joint = p[:, None] * future
            # Xi plus X_rest determines the full present. No bipartite-jump assumption.
            incremental.append(mutual(joint) - mutual(rest.T @ joint))
        return {
            "lag": lag,
            "held_bits": held,
            "incremental_prediction_bits": incremental,
            "reaction_response_tv": response.tolist(),
            "reaction_rates": rates.tolist(),
            "event_present": (rates > 0).tolist(),
            "present_entropy_bits": entropy(p),
        }
