"""Bounded spectral pilot for finite agency-diamond systems.

This module treats spectrum as a detector coordinate. It deliberately includes
negative controls where complex phase appears without control and reflexive
maintenance appears without complex phase.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import numpy as np

from omega.agency_diamond.examples import canonical_battery
from omega.agency_diamond.metrics import evaluate_system
from omega.agency_diamond.model import ControlledSystem, validate_system
from omega.agency_diamond.strictness import own_maintenance_joint_effect_strictness


CLAIM_BOUNDARY = (
    "Finite deterministic spectral pilot only. The transfer operator is the "
    "nominal live-policy sub-Markov matrix restricted to declared viable states. "
    "These spectra are detector coordinates, not agency, identity, value, "
    "valuerhood, phase ontology, lushness, or Omega validation."
)


@dataclass(frozen=True)
class SpectralProfile:
    system_id: str
    family: str
    scenario: str
    states: tuple[str, ...]
    matrix: tuple[tuple[Fraction, ...], ...]
    eigenvalues: tuple[complex, ...]
    spectral_radius: float
    spectral_gap_from_radius: float | None
    complex_mode_count: int
    max_abs_imaginary: float
    nonzero_phase_angles: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "system_id": self.system_id,
            "family": self.family,
            "scenario": self.scenario,
            "states": list(self.states),
            "matrix": [[str(value) for value in row] for row in self.matrix],
            "eigenvalues": [_complex_to_json(value) for value in self.eigenvalues],
            "spectral_radius": round(self.spectral_radius, 12),
            "spectral_gap_from_radius": (
                None
                if self.spectral_gap_from_radius is None
                else round(self.spectral_gap_from_radius, 12)
            ),
            "complex_mode_count": self.complex_mode_count,
            "max_abs_imaginary": round(self.max_abs_imaginary, 12),
            "nonzero_phase_angles": [
                round(angle, 12) for angle in self.nonzero_phase_angles
            ],
        }


def live_policy_spectral_profile(
    system: ControlledSystem,
    *,
    scenario: str | None = None,
) -> SpectralProfile:
    """Compute the nominal live-policy sub-Markov spectrum over viable states."""

    validate_system(system)
    scenario = scenario or system.nominal_scenario
    if scenario not in system.scenarios:
        raise ValueError(f"undeclared scenario: {scenario}")
    states = tuple(sorted(system.viable_states))
    matrix = _live_policy_submarkov_matrix(system, scenario=scenario, states=states)
    numeric = np.array([[float(value) for value in row] for row in matrix], dtype=float)
    eigenvalues = tuple(np.linalg.eigvals(numeric))
    magnitudes = sorted((abs(value) for value in eigenvalues), reverse=True)
    radius = magnitudes[0] if magnitudes else 0.0
    gap = None if len(magnitudes) < 2 else radius - magnitudes[1]
    nonzero_phase_angles = tuple(
        float(np.angle(value))
        for value in eigenvalues
        if abs(value) > 1e-9 and abs(float(np.angle(value))) > 1e-9
    )
    return SpectralProfile(
        system_id=system.system_id,
        family=system.family,
        scenario=scenario,
        states=states,
        matrix=matrix,
        eigenvalues=eigenvalues,
        spectral_radius=float(radius),
        spectral_gap_from_radius=None if gap is None else float(gap),
        complex_mode_count=sum(1 for value in eigenvalues if abs(value.imag) > 1e-9),
        max_abs_imaginary=max((abs(value.imag) for value in eigenvalues), default=0.0),
        nonzero_phase_angles=nonzero_phase_angles,
    )


def spectral_pilot_summary(*, horizon: int = 3) -> dict[str, Any]:
    """Run the bounded spectral pilot over the canonical deterministic battery."""

    systems = canonical_battery()
    profiles = [live_policy_spectral_profile(system) for system in systems]
    metrics = {
        system.system_id: evaluate_system(system, horizon=horizon).as_dict()
        for system in systems
    }
    strictness = own_maintenance_joint_effect_strictness(horizon=1)
    by_id = {profile.system_id: profile for profile in profiles}
    driven_metric = metrics["driven_cycle"]
    self_restoring_metric = metrics["self_restoring_controller"]
    decision_gate = {
        "own_maintenance_joint_effect_strictness_passes": strictness["status"]
        == "PASS",
        "spectra_computed_for_all_systems": len(profiles) == len(systems),
        "driven_cycle_has_complex_phase": by_id[
            "driven_cycle"
        ].complex_mode_count
        > 0,
        "driven_cycle_has_no_control": driven_metric["control_reach_count"] == 0,
        "self_restoring_has_reflexive_advantage": (
            self_restoring_metric["reflexive_advantage"] is not None
            and self_restoring_metric["reflexive_advantage"] != "0"
        ),
        "self_restoring_has_no_complex_phase": by_id[
            "self_restoring_controller"
        ].complex_mode_count
        == 0,
    }
    decision_gate["complex_phase_not_sufficient_for_deformer_profile"] = (
        decision_gate["driven_cycle_has_complex_phase"]
        and decision_gate["driven_cycle_has_no_control"]
    )
    decision_gate["reflexive_profile_not_dependent_on_complex_phase"] = (
        decision_gate["self_restoring_has_reflexive_advantage"]
        and decision_gate["self_restoring_has_no_complex_phase"]
    )
    return {
        "name": "agency_diamond_spectral_pilot",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "horizon": horizon,
        "decision_gate": decision_gate,
        "strictness": strictness,
        "profiles": [profile.as_dict() for profile in profiles],
        "metric_rows": metrics,
        "public_read": (
            "Nominal live-policy spectra are useful detector coordinates, but "
            "the first finite pilot demotes complex spectral phase: a driven "
            "cycle has complex phase without control, while the self-restoring "
            "controller has reflexive maintenance without complex phase."
        ),
    }


def _live_policy_submarkov_matrix(
    system: ControlledSystem,
    *,
    scenario: str,
    states: tuple[str, ...],
) -> tuple[tuple[Fraction, ...], ...]:
    index = {state: i for i, state in enumerate(states)}
    rows: list[list[Fraction]] = [
        [Fraction(0) for _ in states]
        for _ in states
    ]
    for row_index, state in enumerate(states):
        action = system.live_policy[system.observe[state]]
        target = system.transition[scenario][state][action]
        if target in index:
            rows[row_index][index[target]] = Fraction(1)
    return tuple(tuple(row) for row in rows)


def _complex_to_json(value: complex) -> dict[str, float]:
    return {
        "real": round(float(value.real), 12),
        "imag": round(float(value.imag), 12),
        "abs": round(abs(value), 12),
        "angle": round(float(np.angle(value)), 12) if abs(value) > 1e-9 else 0.0,
    }
