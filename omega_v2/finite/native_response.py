"""Native-event response profiles, retaining every declared frame and rate."""

import numpy as np

from omega_v2.finite.continuation_readout import projection


class NativeResponse:
    def __init__(self, model):
        self.model = model
        self.columns = model.frame_columns()
        self.frames = {
            mask: projection(model.values, cols)[1] for mask, cols in self.columns.items()
        }
        self._cache = {}

    def contrasts(self, lag):
        if lag not in self._cache:
            k = self.model.evolution(lag)[0]
            arrays = []
            for frame in self.frames.values():
                future = np.asarray((frame.T @ k.T).T)
                contrasts = np.zeros_like(self.model.rates)
                for c, rates in enumerate(self.model.rates):
                    x = np.flatnonzero(rates)
                    contrasts[c, x] = 0.5 * np.abs(
                        future[x] - future[self.model.targets[c, x]]
                    ).sum(axis=1)
                arrays.append(contrasts)
            self._cache[lag] = np.asarray(arrays)
        return self._cache[lag]

    def profiles(self, p, lag):
        flux = self.model.rates * p
        rates = flux.sum(axis=1)
        weights = np.divide(flux, rates[:, None], out=np.zeros_like(flux), where=rates[:, None] > 0)
        return {
            "lag": lag,
            "reaction_rates": rates.tolist(),
            "event_present": (rates > 0).tolist(),
            "reaction_response_tv": np.einsum("mcx,cx->mc", self.contrasts(lag), weights).tolist(),
        }
