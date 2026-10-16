"""Exact present-rooted joint laws for finite classical Markov dynamics."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

_STOCHASTIC_TOL = 1e-12


@dataclass(frozen=True)
class Observation:
    """Observe the listed native coordinates at a physical time."""

    time: float
    region: tuple[int, ...]


def _projection(state: tuple[object, ...], region: tuple[int, ...]) -> tuple[object, ...]:
    return tuple(state[index] for index in region)


def _cell_count(shape: Iterable[int]) -> int:
    count = 1
    for width in shape:
        count *= width
    return count


@dataclass(frozen=True)
class JointLaw:
    """Dense joint distribution over the native outcomes at each observation."""

    root: tuple[object, ...]
    observations: tuple[Observation, ...]
    alphabets: tuple[tuple[tuple[object, ...], ...], ...]
    probabilities: np.ndarray
    clock: str

    def __post_init__(self) -> None:
        if len(self.observations) != len(self.alphabets):
            raise ValueError("observations and alphabets must have the same length")
        if self.clock not in ("discrete", "continuous"):
            raise ValueError("clock must be 'discrete' or 'continuous'")
        for observation, alphabet in zip(self.observations, self.alphabets, strict=True):
            if any(not isinstance(value, tuple) for value in alphabet):
                raise ValueError("alphabet outcomes must be local-state tuples")
            if len(set(alphabet)) != len(alphabet):
                raise ValueError("alphabet outcomes must be unique")
            if any(not isinstance(value, int) or isinstance(value, bool)
                   for value in observation.region):
                raise ValueError("observation regions must contain integer coordinates")
            if any(len(value) != len(observation.region) for value in alphabet):
                raise ValueError("alphabet outcomes must match their observation region")
        probabilities = np.array(self.probabilities, dtype=float, copy=True)
        expected_shape = tuple(len(alphabet) for alphabet in self.alphabets)
        if probabilities.shape != expected_shape:
            raise ValueError("probability table shape does not match its alphabets")
        if not np.isfinite(probabilities).all():
            raise ValueError("probability table must be finite")
        if np.any(probabilities < -_STOCHASTIC_TOL):
            raise ArithmeticError("probability table contains material negative mass")
        if not math.isfinite(float(np.sum(probabilities))):
            raise ArithmeticError("probability table has nonfinite total mass")
        if not math.isclose(float(np.sum(probabilities)), 1.0, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError("joint probability table must have total mass one")
        probabilities.setflags(write=False)
        object.__setattr__(self, "probabilities", probabilities)

    @property
    def mass(self) -> float:
        return float(np.sum(self.probabilities))

    def marginal(self, keep: Iterable[int]) -> JointLaw:
        indices = tuple(keep)
        if any(not isinstance(index, int) or isinstance(index, bool) for index in indices):
            raise ValueError("kept observation indices must be integers")
        if tuple(sorted(set(indices))) != indices:
            raise ValueError("kept observation indices must be increasing and unique")
        if any(index < 0 or index >= len(self.observations) for index in indices):
            raise ValueError("kept observation index is out of range")
        omitted = tuple(i for i in range(len(self.observations)) if i not in indices)
        probabilities = self.probabilities
        if omitted:
            probabilities = probabilities.sum(axis=omitted)
        return JointLaw(
            self.root,
            tuple(self.observations[i] for i in indices),
            tuple(self.alphabets[i] for i in indices),
            probabilities,
            self.clock,
        )

    def restrict(self, regions: Iterable[tuple[int, ...]]) -> JointLaw:
        """Marginalize each observed region to the requested physical coordinates."""
        selections = tuple(tuple(region) for region in regions)
        if len(selections) != len(self.observations):
            raise ValueError("provide one coordinate subset for every observation")
        probabilities = self.probabilities
        new_observations: list[Observation] = []
        new_alphabets: list[tuple[tuple[object, ...], ...]] = []
        for axis, (observation, alphabet, requested) in enumerate(
            zip(self.observations, self.alphabets, selections, strict=True)
        ):
            if any(not isinstance(i, int) or isinstance(i, bool) for i in requested):
                raise ValueError("restricted regions must contain integer coordinates")
            if len(set(requested)) != len(requested):
                raise ValueError("restricted coordinates must be unique")
            if any(i not in observation.region for i in requested):
                raise ValueError("restricted coordinates must belong to the observed region")
            positions = tuple(observation.region.index(i) for i in requested)
            projected_values = tuple(tuple(outcome[pos] for pos in positions) for outcome in alphabet)
            reduced_alphabet = tuple(dict.fromkeys(projected_values))
            target_index = {outcome: i for i, outcome in enumerate(reduced_alphabet)}
            moved = np.moveaxis(probabilities, axis, 0)
            reduced = np.zeros((len(reduced_alphabet),) + moved.shape[1:], dtype=float)
            for old_index, outcome in enumerate(projected_values):
                reduced[target_index[outcome]] += moved[old_index]
            probabilities = np.moveaxis(reduced, 0, axis)
            new_observations.append(Observation(observation.time, requested))
            new_alphabets.append(reduced_alphabet)
        return JointLaw(
            self.root, tuple(new_observations), tuple(new_alphabets), probabilities, self.clock
        )

    def probability(self, values: Iterable[tuple[object, ...]]) -> float:
        outcomes = tuple(tuple(value) for value in values)
        if len(outcomes) != len(self.observations):
            raise ValueError("provide one local-state tuple for every observation")
        location: list[int] = []
        for alphabet, outcome in zip(self.alphabets, outcomes, strict=True):
            try:
                location.append(alphabet.index(outcome))
            except ValueError:
                return 0.0
        return float(self.probabilities[tuple(location)])


class FiniteContinuationLaw:
    """Finite state space and reusable discrete kernel or continuous generator."""

    def __init__(self, states, operator, *, clock="discrete"):
        if clock not in ("discrete", "continuous"):
            raise ValueError("clock must be 'discrete' or 'continuous'")
        try:
            state_tuple = tuple(tuple(state) for state in states)
            state_set = set(state_tuple)
        except (TypeError, ValueError) as error:
            raise ValueError("states must be hashable tuples") from error
        if not state_tuple:
            raise ValueError("at least one state is required")
        if len(state_set) != len(state_tuple):
            raise ValueError("states must be unique")
        width = len(state_tuple[0])
        if any(len(state) != width for state in state_tuple):
            raise ValueError("all states must have equal width")
        try:
            matrix = np.array(operator, dtype=float, copy=True)
        except (TypeError, ValueError) as error:
            raise ValueError("operator must be a finite numeric matrix") from error
        n = len(state_tuple)
        if matrix.shape != (n, n) or not np.isfinite(matrix).all():
            raise ValueError("operator must be a finite square matrix matching states")
        if clock == "discrete":
            if np.any(matrix < 0.0):
                raise ValueError("stochastic matrix entries must be nonnegative")
            if not np.allclose(matrix.sum(axis=1), 1.0, rtol=0.0, atol=_STOCHASTIC_TOL):
                raise ValueError("each stochastic matrix row must sum to one")
        else:
            off_diagonal = matrix.copy()
            np.fill_diagonal(off_diagonal, 0.0)
            if np.any(off_diagonal < 0.0):
                raise ValueError("generator off-diagonal rates must be nonnegative")
            if np.any(np.diag(matrix) > 0.0):
                raise ValueError("generator diagonal entries must be nonpositive")
            if not np.allclose(matrix.sum(axis=1), 0.0, rtol=0.0, atol=_STOCHASTIC_TOL):
                raise ValueError("each generator row must sum to zero")
        matrix.setflags(write=False)
        self.states = state_tuple
        self.operator = matrix
        self.clock = clock
        self._state_index = {state: index for index, state in enumerate(state_tuple)}

    @classmethod
    def from_device(cls, device):
        """Adapt a finite device's target probabilities, ignoring event metadata."""
        states = tuple(tuple(state) for state in device.states)
        index = {state: i for i, state in enumerate(states)}
        if len(index) != len(states):
            raise ValueError("device states must be unique")
        kernel = np.zeros((len(states), len(states)), dtype=float)
        for source, outcomes in device.rows.items():
            source = tuple(source)
            if source not in index:
                raise ValueError("device row has an unknown source state")
            for outcome in outcomes:
                target = tuple(outcome.target)
                if target not in index:
                    raise ValueError("device outcome has an unknown target state")
                probability = float(outcome.probability)
                if not math.isfinite(probability) or probability < 0.0:
                    raise ValueError("device outcome probabilities must be finite and nonnegative")
                kernel[index[source], index[target]] += probability
        if len(device.rows) != len(states):
            raise ValueError("device must define an outcome row for every state")
        return cls(states, kernel, clock="discrete")

    def _transition(self, gap: float) -> np.ndarray:
        if self.clock == "discrete":
            return np.linalg.matrix_power(self.operator, int(gap))
        from scipy.linalg import expm

        transition = expm(self.operator * gap)
        if not np.isfinite(transition).all():
            raise ArithmeticError("continuous transition exponential is nonfinite")
        if not np.allclose(transition.sum(axis=1), 1.0, rtol=0.0, atol=1e-10):
            raise ArithmeticError("continuous transition exponential lost mass")
        if np.any(transition < -1e-10):
            raise ArithmeticError("continuous transition exponential has material negative mass")
        return transition

    def joint(self, root, observations, *, max_cells=1_000_000) -> JointLaw:
        """Compute a joint law, bounded by the main dense buffer estimate.

        ``max_cells`` covers the live state-bearing tensors and transition matrix.
        It is an allocation guard estimate; temporary storage inside NumPy/SciPy
        matrix operations is implementation-dependent and not included.
        """
        root = tuple(root)
        if root not in self._state_index:
            raise ValueError("root must be an exact declared state")
        if not isinstance(max_cells, int) or isinstance(max_cells, bool) or max_cells < 1:
            raise ValueError("max_cells must be a positive integer")
        axes = tuple(observations)
        previous_time = 0.0
        alphabets: list[tuple[tuple[object, ...], ...]] = []
        projections: list[tuple[tuple[object, ...], ...]] = []
        for observation in axes:
            if not isinstance(observation, Observation):
                raise TypeError("observations must be Observation instances")
            try:
                time = float(observation.time)
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError("observation times must be finite nonnegative numbers") from error
            if not math.isfinite(time) or time < 0.0 or time < previous_time:
                raise ValueError("observation times must be finite, nonnegative, and nondecreasing")
            if self.clock == "discrete" and not time.is_integer():
                raise ValueError("discrete-clock observation times must be integer ticks")
            if not isinstance(observation.region, tuple):
                raise TypeError("observation region must be a tuple of coordinate indices")
            region = observation.region
            if any(not isinstance(i, int) or isinstance(i, bool) for i in region):
                raise ValueError("region indices must be integers")
            if len(set(region)) != len(region) or any(i < 0 or i >= len(root) for i in region):
                raise ValueError("region indices must be unique and within the native state")
            projected = tuple(_projection(state, region) for state in self.states)
            alphabet = tuple(dict.fromkeys(projected))
            alphabets.append(alphabet)
            projections.append(projected)
            previous_time = time

        if not axes:
            return JointLaw(root, (), (), np.array(1.0), self.clock)

        native_count = len(self.states)
        tensor = np.zeros((native_count,), dtype=float)
        tensor[self._state_index[root]] = 1.0
        prefix_shape: tuple[int, ...] = ()
        previous_time = 0.0
        for observation, alphabet, projected in zip(axes, alphabets, projections, strict=True):
            time = float(observation.time)
            gap = time - previous_time
            next_shape = prefix_shape + (len(alphabet),)
            # Estimate the main live tensor, propagated copy, expanded state
            # tensor, and transition matrix. Library-internal temporaries are
            # outside this cell-count estimate.
            peak_cells = (
                _cell_count(prefix_shape + (native_count,))
                + _cell_count(prefix_shape + (native_count,))
                + _cell_count(next_shape + (native_count,))
                + native_count * native_count  # dense transition matrix
            )
            if peak_cells > max_cells:
                raise ValueError(
                    f"joint table or propagation workspace exceeds max_cells={max_cells}"
                )
            transition = self._transition(gap)
            propagated = tensor.reshape((-1, native_count)) @ transition
            if not np.isfinite(propagated).all():
                raise ArithmeticError("joint propagation produced nonfinite mass")
            if np.any(propagated < -_STOCHASTIC_TOL):
                raise ArithmeticError("joint propagation produced material negative mass")
            expanded = np.zeros(
                (propagated.shape[0], len(alphabet), native_count), dtype=float
            )
            alphabet_index = {outcome: i for i, outcome in enumerate(alphabet)}
            for state_index, outcome in enumerate(projected):
                expanded[:, alphabet_index[outcome], state_index] = propagated[:, state_index]
            tensor = expanded.reshape(next_shape + (native_count,))
            prefix_shape = next_shape
            previous_time = time

        probabilities = tensor.sum(axis=-1)
        return JointLaw(root, axes, tuple(alphabets), probabilities, self.clock)
