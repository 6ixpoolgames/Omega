"""Finite contextual future-field and holonomy witnesses."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from omega.contextual_future_fields.kernel import (
    ContinuationProfile,
    OverlapKernel,
    declared_kernel_report,
    kernel_deformation_report,
    overlap_kernel_report,
)
from omega.contextual_future_fields.model import (
    Context,
    Transport,
    all_global_assignments,
    apply_transport_loop,
    distribution_to_json,
    fraction_dict,
    overlap,
    overlap_distributions_agree,
    overlap_supports_agree,
    project_profile,
    support_to_json,
    uniform_weights,
)

CLAIM_BOUNDARY = (
    "Finite contextual future-field pilots only. These witnesses do not claim "
    "quantum mechanics, Hilbert-space structure, value, agency, identity, "
    "valuerhood, moral standing, or Omega validation."
)


def parity_no_global_extension_witness() -> dict[str, Any]:
    """Return a support-level local-context witness with no global extension.

    The shape is the finite parity obstruction:

    * AB requires A = B;
    * BC requires B = C;
    * AC requires A != C.

    Each local context is nonempty. Each pair has matching support and uniform
    marginal distribution on its overlap. No global assignment satisfies all
    three local constraints.
    """

    contexts = (
        Context(
            name="AB_equal",
            variables=("A", "B"),
            allowed=((0, 0), (1, 1)),
        ),
        Context(
            name="BC_equal",
            variables=("B", "C"),
            allowed=((0, 0), (1, 1)),
        ),
        Context(
            name="AC_unequal",
            variables=("A", "C"),
            allowed=((0, 1), (1, 0)),
        ),
    )
    contexts = tuple(
        Context(
            name=context.name,
            variables=context.variables,
            allowed=context.allowed,
            weights=uniform_weights(context.allowed),
        )
        for context in contexts
    )
    overlap_rows: list[dict[str, Any]] = []
    for index, left in enumerate(contexts):
        for right in contexts[index + 1 :]:
            shared = overlap(left, right)
            overlap_rows.append(
                {
                    "left": left.name,
                    "right": right.name,
                    "overlap": list(shared),
                    "support_agrees": overlap_supports_agree(left, right),
                    "distribution_agrees": overlap_distributions_agree(left, right),
                    "left_support": support_to_json(left.restrict_support(shared)),
                    "right_support": support_to_json(right.restrict_support(shared)),
                    "left_distribution": distribution_to_json(
                        left.restrict_distribution(shared)
                    ),
                    "right_distribution": distribution_to_json(
                        right.restrict_distribution(shared)
                    ),
                }
            )

    global_assignments = all_global_assignments(
        contexts,
        variables=("A", "B", "C"),
        values=(0, 1),
    )
    context_rows = [
        {
            "name": context.name,
            "variables": list(context.variables),
            "allowed": [dict(zip(context.variables, values, strict=True)) for values in context.allowed],
            "weights": [
                {
                    "assignment": dict(zip(context.variables, values, strict=True)),
                    "mass": str(context.weights[values]) if context.weights else "0",
                }
                for values in context.allowed
            ],
        }
        for context in contexts
    ]
    decision_gate = {
        "local_contexts_nonempty": all(context.allowed for context in contexts),
        "overlap_supports_agree": all(row["support_agrees"] for row in overlap_rows),
        "overlap_distributions_agree": all(
            row["distribution_agrees"] for row in overlap_rows
        ),
        "no_global_extension": len(global_assignments) == 0,
    }
    return {
        "name": "parity_no_global_extension",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "description": (
            "Pairwise local contexts have nonempty sections and matching overlap "
            "support/distribution, but no global assignment satisfies all local "
            "constraints."
        ),
        "contexts": context_rows,
        "overlaps": overlap_rows,
        "global_assignments": global_assignments,
        "decision_gate": decision_gate,
        "non_claims": [
            "not sheaf cohomology",
            "not quantum contextuality",
            "not value arbitration",
            "not a moral incompatibility claim",
        ],
    }


def holonomy_witnesses() -> dict[str, Any]:
    """Return finite transport-loop holonomy witnesses."""

    lossy_profile = {
        "score": Fraction(1),
        "oversight": Fraction(1),
        "corrigibility": Fraction(1),
        "interpretability": Fraction(1),
    }
    lossy_transports = (
        Transport(
            name="A_to_B",
            source="A",
            target="B",
            coordinate_map={
                "score": "score_B",
                "oversight": "oversight_B",
                "corrigibility": "corrigibility_B",
                "interpretability": "interpretability_B",
            },
        ),
        Transport(
            name="B_to_C",
            source="B",
            target="C",
            coordinate_map={
                "score_B": "score_C",
                "oversight_B": "oversight_C",
                "corrigibility_B": "corrigibility_C",
                "interpretability_B": "interpretability_C",
            },
        ),
        Transport(
            name="C_to_A_visible",
            source="C",
            target="A",
            coordinate_map={
                "score_C": "score",
                "oversight_C": None,
                "corrigibility_C": "corrigibility",
                "interpretability_C": None,
            },
        ),
    )
    lossy = _loop_report(
        name="same_proxy_lossy_holonomy",
        initial_profile=lossy_profile,
        transports=lossy_transports,
        proxy_coordinates=("score",),
        continuation_coordinates=("oversight", "corrigibility", "interpretability"),
        interpretation=(
            "The visible score coordinate returns, but the composed loop drops "
            "oversight and interpretability continuation coordinates."
        ),
    )

    twist_profile = {
        "score": Fraction(1),
        "route_left": Fraction(1),
        "route_right": Fraction(0),
    }
    twist_transports = (
        Transport(
            name="A_to_B",
            source="A",
            target="B",
            coordinate_map={
                "score": "score_B",
                "route_left": "route_left_B",
                "route_right": "route_right_B",
            },
        ),
        Transport(
            name="B_to_C",
            source="B",
            target="C",
            coordinate_map={
                "score_B": "score_C",
                "route_left_B": "route_left_C",
                "route_right_B": "route_right_C",
            },
        ),
        Transport(
            name="C_to_A_twist",
            source="C",
            target="A",
            coordinate_map={
                "score_C": "score",
                "route_left_C": "route_right",
                "route_right_C": "route_left",
            },
        ),
    )
    twist = _loop_report(
        name="same_proxy_orientation_twist",
        initial_profile=twist_profile,
        transports=twist_transports,
        proxy_coordinates=("score",),
        continuation_coordinates=("route_left", "route_right"),
        interpretation=(
            "The visible score coordinate returns and total continuation "
            "thickness is preserved, but route orientation is swapped."
        ),
    )

    decision_gate = {
        "lossy_proxy_returns": lossy["proxy_returned"],
        "lossy_holonomy_nontrivial": lossy["holonomy_nontrivial"],
        "lossy_continuation_changed": bool(lossy["changed_continuation_coordinates"]),
        "twist_proxy_returns": twist["proxy_returned"],
        "twist_holonomy_nontrivial": twist["holonomy_nontrivial"],
        "twist_total_continuation_thickness_preserved": (
            twist["initial_continuation_thickness"]
            == twist["final_continuation_thickness"]
        ),
    }
    return {
        "name": "finite_transport_loop_holonomy",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "description": (
            "Finite transport loops where the visible proxy returns but the "
            "transported continuation profile is not the identity."
        ),
        "witnesses": [lossy, twist],
        "decision_gate": decision_gate,
        "non_claims": [
            "not complex phase",
            "not quantum holonomy",
            "not identity failure",
            "not value loss",
        ],
    }


def compatibility_thickness_kernel_witnesses() -> dict[str, Any]:
    """Return PSD and non-PSD finite compatibility-thickness controls."""

    profiles = (
        ContinuationProfile("alpha", frozenset({"a", "shared_ab"})),
        ContinuationProfile("beta", frozenset({"b", "shared_ab", "shared_bc"})),
        ContinuationProfile("gamma", frozenset({"c", "shared_bc"})),
    )
    overlap_kernel = OverlapKernel(
        profiles=profiles,
        atom_weights={
            "a": Fraction(1),
            "b": Fraction(1),
            "c": Fraction(1),
            "shared_ab": Fraction(1),
            "shared_bc": Fraction(1),
        },
    )
    overlap_report = overlap_kernel_report(
        name="certified_overlap_kernel",
        kernel=overlap_kernel,
        interpretation=(
            "Diagonal entries are profile thickness and off-diagonal entries "
            "are certified shared continuation atoms."
        ),
    )
    inconsistent = declared_kernel_report(
        name="inconsistent_declared_compatibility_kernel",
        labels=("alpha", "beta", "gamma"),
        matrix=(
            (Fraction(1), Fraction(1), Fraction(1)),
            (Fraction(1), Fraction(1), Fraction(0)),
            (Fraction(1), Fraction(0), Fraction(1)),
        ),
        interpretation=(
            "A symmetric nonnegative table can still fail to be a PSD/Gram "
            "compatibility kernel. Here alpha fully overlaps beta and gamma, "
            "while beta and gamma have zero overlap."
        ),
    )
    decision_gate = {
        "overlap_kernel_psd": bool(overlap_report["psd"]),
        "overlap_kernel_rank_positive": int(overlap_report["rank"]) > 0,
        "declared_kernel_symmetric": bool(inconsistent["symmetric"]),
        "declared_kernel_nonnegative_diagonal": bool(
            inconsistent["nonnegative_diagonal"]
        ),
        "declared_kernel_psd_fails": not bool(inconsistent["psd"]),
    }
    return {
        "name": "compatibility_thickness_kernel",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "description": (
            "Certified overlap data gives a PSD compatibility-thickness kernel; "
            "an arbitrary symmetric compatibility table need not."
        ),
        "certified_overlap": overlap_report,
        "non_psd_control": inconsistent,
        "decision_gate": decision_gate,
        "non_claims": [
            "not Hilbert space",
            "not density operator validation",
            "not Born rule",
            "not value measure",
        ],
    }


def density_deformation_witnesses() -> dict[str, Any]:
    """Return finite before/after kernel deformation controls."""

    before = OverlapKernel(
        profiles=(
            ContinuationProfile("left", frozenset({"left_private", "shared"})),
            ContinuationProfile("right", frozenset({"right_private", "shared"})),
        ),
        atom_weights={
            "left_private": Fraction(1),
            "right_private": Fraction(1),
            "shared": Fraction(1),
        },
    )
    after_offdiag_damage = OverlapKernel(
        profiles=(
            ContinuationProfile("left", frozenset({"left_private", "left_replacement"})),
            ContinuationProfile("right", frozenset({"right_private", "right_replacement"})),
        ),
        atom_weights={
            "left_private": Fraction(1),
            "right_private": Fraction(1),
            "left_replacement": Fraction(1),
            "right_replacement": Fraction(1),
        },
    )
    compatibility_damage = kernel_deformation_report(
        name="diagonal_preserved_compatibility_damage",
        before=before,
        after=after_offdiag_damage,
        interpretation=(
            "Own thickness stays fixed while shared compatibility thickness "
            "between profiles is removed."
        ),
    )

    diagonal_before = OverlapKernel(
        profiles=(
            ContinuationProfile("left", frozenset({"left_private", "shared"})),
            ContinuationProfile("right", frozenset({"right_private"})),
        ),
        atom_weights={
            "left_private": Fraction(1),
            "right_private": Fraction(1),
            "shared": Fraction(1),
        },
    )
    diagonal_after = OverlapKernel(
        profiles=(
            ContinuationProfile("left", frozenset({"left_private"})),
            ContinuationProfile("right", frozenset({"right_private"})),
        ),
        atom_weights={
            "left_private": Fraction(1),
            "right_private": Fraction(1),
        },
    )
    diagonal_thinning = kernel_deformation_report(
        name="diagonal_thickness_thinning_without_offdiag_change",
        before=diagonal_before,
        after=diagonal_after,
        interpretation=(
            "One profile loses thickness while off-diagonal compatibility is "
            "unchanged at zero."
        ),
    )
    decision_gate = {
        "compatibility_damage_psd_preserved": bool(
            compatibility_damage["psd_preserved"]
        ),
        "compatibility_damage_diagonal_preserved": bool(
            compatibility_damage["diagonal_preserved"]
        ),
        "compatibility_damage_off_diagonal_changed": not bool(
            compatibility_damage["off_diagonal_preserved"]
        ),
        "diagonal_thinning_psd_preserved": bool(diagonal_thinning["psd_preserved"]),
        "diagonal_thinning_diagonal_changed": not bool(
            diagonal_thinning["diagonal_preserved"]
        ),
        "diagonal_thinning_off_diagonal_preserved": bool(
            diagonal_thinning["off_diagonal_preserved"]
        ),
    }
    return {
        "name": "density_kernel_deformation",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "description": (
            "Finite before/after kernel comparisons separate diagonal thickness "
            "change from off-diagonal compatibility change."
        ),
        "witnesses": [compatibility_damage, diagonal_thinning],
        "decision_gate": decision_gate,
        "non_claims": [
            "not agency",
            "not value loss",
            "not a physical operator",
            "not a complete deformer theory",
        ],
    }


def contextual_future_field_summary() -> dict[str, Any]:
    no_global = parity_no_global_extension_witness()
    holonomy = holonomy_witnesses()
    kernel = compatibility_thickness_kernel_witnesses()
    deformation = density_deformation_witnesses()
    decision_gate = {
        "no_global_extension_witness_passes": no_global["status"] == "PASS",
        "holonomy_witnesses_pass": holonomy["status"] == "PASS",
        "compatibility_thickness_kernel_passes": kernel["status"] == "PASS",
        "density_deformation_witnesses_pass": deformation["status"] == "PASS",
    }
    return {
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "decision_gate": decision_gate,
        "artifacts": {
            "no_global_extension": no_global,
            "holonomy": holonomy,
            "compatibility_thickness_kernel": kernel,
            "density_deformation": deformation,
        },
        "public_read": (
            "Finite contextual future-field pilots show four pre-Hilbert facts: "
            "local compatibility data can fail to admit a global extension, and "
            "a loop can return a visible proxy while transporting a continuation "
            "profile nontrivially; certified overlap data gives a PSD "
            "compatibility-thickness kernel while arbitrary compatibility tables "
            "need not; and before/after kernel comparisons separate thickness "
            "change from compatibility change."
        ),
    }


def _loop_report(
    *,
    name: str,
    initial_profile: dict[str, Fraction],
    transports: tuple[Transport, ...],
    proxy_coordinates: tuple[str, ...],
    continuation_coordinates: tuple[str, ...],
    interpretation: str,
) -> dict[str, Any]:
    final_profile = apply_transport_loop(initial_profile, transports)
    proxy_initial = project_profile(initial_profile, proxy_coordinates)
    proxy_final = project_profile(final_profile, proxy_coordinates)
    continuation_initial = project_profile(initial_profile, continuation_coordinates)
    continuation_final = project_profile(final_profile, continuation_coordinates)
    changed_continuation = [
        coordinate
        for coordinate in continuation_coordinates
        if continuation_initial[coordinate] != continuation_final[coordinate]
    ]
    initial_thickness = sum(initial_profile.get(coord, Fraction(0)) for coord in continuation_coordinates)
    final_thickness = sum(final_profile.get(coord, Fraction(0)) for coord in continuation_coordinates)
    return {
        "name": name,
        "interpretation": interpretation,
        "initial_profile": fraction_dict(initial_profile),
        "final_profile": fraction_dict(final_profile),
        "proxy_coordinates": list(proxy_coordinates),
        "proxy_initial": proxy_initial,
        "proxy_final": proxy_final,
        "proxy_returned": proxy_initial == proxy_final,
        "continuation_coordinates": list(continuation_coordinates),
        "continuation_initial": continuation_initial,
        "continuation_final": continuation_final,
        "changed_continuation_coordinates": changed_continuation,
        "initial_continuation_thickness": str(initial_thickness),
        "final_continuation_thickness": str(final_thickness),
        "transport_identity_on_profile": final_profile == initial_profile,
        "holonomy_nontrivial": proxy_initial == proxy_final
        and final_profile != initial_profile,
        "transport_names": [transport.name for transport in transports],
        "transport_maps": [
            {
                "name": transport.name,
                "source": transport.source,
                "target": transport.target,
                "coordinate_map": dict(transport.coordinate_map),
            }
            for transport in transports
        ],
    }
