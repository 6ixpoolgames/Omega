"""Preregistered fixtures for finite controlled Markov abstraction v0."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from omega_v2.finite.abstraction import (
    abstract_policy,
    audit_actionwise_lumpability,
    audit_path_law_pushforward,
    audit_support_bisimulation,
    build_quotient_kernel,
    pushforward_initial_distribution,
)
from omega_v2.finite.continuation import audit_bounded_hit_transport
from omega_v2.finite.model import (
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
    FinitePath,
    StateAggregation,
    fraction_text,
)
from omega_v2.finite.path_laws import (
    ActionInvolution,
    abstract_path,
    audit_likelihood_ratio_sufficiency,
    compare_laws,
    event_probability,
    finite_path_law,
    pull_back_reversed_path_law,
    pushforward_path_law,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "finite_controlled_markov_abstraction_protocol_v0.md"
)


def exact_nontrivial_fixture() -> tuple[
    ControlledMarkovSystem[str, str],
    StateAggregation[str, str],
    DeterministicPolicy[str, str],
    FiniteDistribution[str],
]:
    """Two hidden copies per aggregate state with matching aggregate rows."""

    system = ControlledMarkovSystem(
        system_id="exact_nontrivial",
        states=("A0", "A1", "B0", "B1"),
        actions=("mix", "hold"),
        transitions=(
            ("A0", "mix", "A0", Fraction(1, 4)),
            ("A0", "mix", "B0", Fraction(3, 4)),
            ("A1", "mix", "A1", Fraction(1, 4)),
            ("A1", "mix", "B1", Fraction(3, 4)),
            ("B0", "mix", "A0", Fraction(1, 2)),
            ("B0", "mix", "B0", Fraction(1, 2)),
            ("B1", "mix", "A1", Fraction(1, 2)),
            ("B1", "mix", "B1", Fraction(1, 2)),
            ("A0", "hold", "A1", Fraction(1)),
            ("A1", "hold", "A0", Fraction(1)),
            ("B0", "hold", "B1", Fraction(1)),
            ("B1", "hold", "B0", Fraction(1)),
        ),
    )
    aggregation = StateAggregation(
        aggregation_id="drop_copy_index",
        source_states=system.states,
        target_states=("A", "B"),
        rows=(("A0", "A"), ("A1", "A"), ("B0", "B"), ("B1", "B")),
    )
    policy = DeterministicPolicy(
        policy_id="mix_until_B",
        rows=(("A0", "mix"), ("A1", "mix"), ("B0", "hold"), ("B1", "hold")),
    )
    initial = FiniteDistribution(
        rows=(("A0", Fraction(1, 2)), ("A1", Fraction(1, 2))),
    )
    return system, aggregation, policy, initial


def non_lumpable_fixture() -> tuple[
    ControlledMarkovSystem[str, str],
    StateAggregation[str, str],
]:
    """Representatives in block A disagree about transition mass to block B."""

    exact, aggregation, _policy, _initial = exact_nontrivial_fixture()
    replacement = {
        ("A1", "mix", "A1"): Fraction(3, 4),
        ("A1", "mix", "B1"): Fraction(1, 4),
    }
    transitions = tuple(
        (source, action, target, replacement.get((source, action, target), mass))
        for source, action, target, mass in exact.transitions
    )
    return (
        ControlledMarkovSystem(
            system_id="non_lumpable",
            states=exact.states,
            actions=exact.actions,
            transitions=transitions,
        ),
        aggregation,
    )


def biased_cycle_fixture() -> tuple[
    ControlledMarkovSystem[str, str],
    StateAggregation[str, str],
    DeterministicPolicy[str, str],
    FiniteDistribution[str],
]:
    """A reciprocal-support biased cycle collapsed to one aggregate state."""

    states = ("s0", "s1", "s2")
    transitions: list[tuple[str, str, str, Fraction]] = []
    for index, state in enumerate(states):
        transitions.extend(
            (
                (state, "advance", states[(index + 1) % 3], Fraction(3, 4)),
                (state, "advance", states[(index - 1) % 3], Fraction(1, 4)),
            )
        )
    system = ControlledMarkovSystem(
        system_id="biased_cycle",
        states=states,
        actions=("advance",),
        transitions=tuple(transitions),
    )
    aggregation = StateAggregation(
        aggregation_id="collapse_cycle",
        source_states=states,
        target_states=("cycle",),
        rows=tuple((state, "cycle") for state in states),
    )
    policy = DeterministicPolicy(
        policy_id="advance",
        rows=tuple((state, "advance") for state in states),
    )
    initial = FiniteDistribution(
        rows=tuple((state, Fraction(1, 3)) for state in states),
    )
    return system, aggregation, policy, initial


def sufficient_hidden_cycle_fixture() -> tuple[
    ControlledMarkovSystem[str, str],
    StateAggregation[str, str],
    DeterministicPolicy[str, str],
    FiniteDistribution[str],
]:
    """A biased cycle with independent symmetric hidden-state resampling."""

    macros = ("s0", "s1", "s2")
    states = tuple(f"{macro}:h{hidden}" for macro in macros for hidden in (0, 1))
    transitions: list[tuple[str, str, str, Fraction]] = []
    for macro_index, macro in enumerate(macros):
        clockwise = macros[(macro_index + 1) % 3]
        counterclockwise = macros[(macro_index - 1) % 3]
        for hidden in (0, 1):
            source = f"{macro}:h{hidden}"
            for target_hidden in (0, 1):
                transitions.extend(
                    (
                        (
                            source,
                            "advance",
                            f"{clockwise}:h{target_hidden}",
                            Fraction(3, 8),
                        ),
                        (
                            source,
                            "advance",
                            f"{counterclockwise}:h{target_hidden}",
                            Fraction(1, 8),
                        ),
                    )
                )
    system = ControlledMarkovSystem(
        system_id="biased_cycle_with_symmetric_hidden_coordinate",
        states=states,
        actions=("advance",),
        transitions=tuple(transitions),
    )
    aggregation = StateAggregation(
        aggregation_id="drop_symmetric_hidden_coordinate",
        source_states=states,
        target_states=macros,
        rows=tuple((state, state.split(":", maxsplit=1)[0]) for state in states),
    )
    policy = DeterministicPolicy(
        policy_id="advance",
        rows=tuple((state, "advance") for state in states),
    )
    initial = FiniteDistribution(
        rows=tuple((state, Fraction(1, len(states))) for state in states),
    )
    return system, aggregation, policy, initial


def _reversal_pair(
    system: ControlledMarkovSystem[str, str],
    policy: DeterministicPolicy[str, str],
    initial: FiniteDistribution[str],
    *,
    horizon: int,
) -> tuple[
    FiniteDistribution,
    FiniteDistribution,
]:
    forward = finite_path_law(system, policy, initial, horizon=horizon)
    reversed_comparison = pull_back_reversed_path_law(
        forward,
        ActionInvolution(rows=(("advance", "advance"),)),
    )
    return forward, reversed_comparison


def controlled_markov_abstraction_summary(*, horizon: int = 3) -> dict[str, Any]:
    if horizon < 1:
        raise ValueError("validation horizon must be positive")

    exact_system, exact_map, exact_policy, exact_initial = exact_nontrivial_fixture()
    exact_lumpability = audit_actionwise_lumpability(exact_system, exact_map)
    exact_quotient = build_quotient_kernel(exact_system, exact_map)
    exact_support = audit_support_bisimulation(exact_system, exact_quotient, exact_map)
    exact_path_transport = audit_path_law_pushforward(
        exact_system,
        exact_map,
        exact_policy,
        exact_initial,
        horizon=horizon,
    )
    exact_continuation = audit_bounded_hit_transport(
        exact_system,
        exact_map,
        exact_policy,
        ("B0", "B1"),
        horizon=2,
    )
    exact_concrete_law = finite_path_law(
        exact_system,
        exact_policy,
        exact_initial,
        horizon=horizon,
    )
    exact_pushed_law = pushforward_path_law(exact_concrete_law, exact_map)
    exact_quotient_law = finite_path_law(
        exact_quotient,
        abstract_policy(exact_system, exact_map, exact_policy),
        pushforward_initial_distribution(exact_initial, exact_map),
        horizon=horizon,
    )
    def abstract_hit_event(path: FinitePath[str, str]) -> bool:
        return "B" in path.states

    exact_event_pushed = event_probability(exact_pushed_law, abstract_hit_event)
    exact_event_quotient = event_probability(exact_quotient_law, abstract_hit_event)

    bad_system, bad_map = non_lumpable_fixture()
    bad_lumpability = audit_actionwise_lumpability(bad_system, bad_map)
    bad_quotient_refused = False
    bad_quotient_error = ""
    try:
        build_quotient_kernel(bad_system, bad_map)
    except ValueError as exc:
        bad_quotient_refused = True
        bad_quotient_error = str(exc)

    cycle_system, cycle_map, cycle_policy, cycle_initial = biased_cycle_fixture()
    cycle_lumpability = audit_actionwise_lumpability(cycle_system, cycle_map)
    cycle_quotient = build_quotient_kernel(cycle_system, cycle_map)
    cycle_support = audit_support_bisimulation(cycle_system, cycle_quotient, cycle_map)
    cycle_path_transport = audit_path_law_pushforward(
        cycle_system,
        cycle_map,
        cycle_policy,
        cycle_initial,
        horizon=horizon,
    )
    cycle_forward, cycle_reverse = _reversal_pair(
        cycle_system,
        cycle_policy,
        cycle_initial,
        horizon=horizon,
    )
    cycle_forward_abstract = pushforward_path_law(cycle_forward, cycle_map)
    cycle_reverse_abstract = pushforward_path_law(cycle_reverse, cycle_map)
    cycle_concrete_comparison = compare_laws(cycle_forward, cycle_reverse)
    cycle_abstract_comparison = compare_laws(
        cycle_forward_abstract,
        cycle_reverse_abstract,
    )
    cycle_sufficiency = audit_likelihood_ratio_sufficiency(
        cycle_forward,
        cycle_reverse,
        lambda path: abstract_path(path, cycle_map),
    )

    hidden_system, hidden_map, hidden_policy, hidden_initial = (
        sufficient_hidden_cycle_fixture()
    )
    hidden_lumpability = audit_actionwise_lumpability(hidden_system, hidden_map)
    hidden_quotient = build_quotient_kernel(hidden_system, hidden_map)
    hidden_support = audit_support_bisimulation(hidden_system, hidden_quotient, hidden_map)
    hidden_path_transport = audit_path_law_pushforward(
        hidden_system,
        hidden_map,
        hidden_policy,
        hidden_initial,
        horizon=horizon,
    )
    hidden_forward, hidden_reverse = _reversal_pair(
        hidden_system,
        hidden_policy,
        hidden_initial,
        horizon=horizon,
    )
    hidden_forward_abstract = pushforward_path_law(hidden_forward, hidden_map)
    hidden_reverse_abstract = pushforward_path_law(hidden_reverse, hidden_map)
    hidden_concrete_comparison = compare_laws(hidden_forward, hidden_reverse)
    hidden_abstract_comparison = compare_laws(
        hidden_forward_abstract,
        hidden_reverse_abstract,
    )
    hidden_sufficiency = audit_likelihood_ratio_sufficiency(
        hidden_forward,
        hidden_reverse,
        lambda path: abstract_path(path, hidden_map),
    )

    cycle_tv_data_processing = (
        cycle_abstract_comparison.total_variation
        <= cycle_concrete_comparison.total_variation
    )
    hidden_tv_data_processing = (
        hidden_abstract_comparison.total_variation
        <= hidden_concrete_comparison.total_variation
    )
    case_results = {
        "exact_nontrivial_lumpability": exact_lumpability.strongly_lumpable,
        "exact_quotient_support_bisimulation": exact_support.bisimilar,
        "exact_full_path_law_pushforward": exact_path_transport.commutes,
        "exact_path_event_preservation": exact_event_pushed == exact_event_quotient,
        "bounded_continuation_transport": exact_continuation.agrees,
        "non_lumpable_rejected_with_witness": (
            not bad_lumpability.strongly_lumpable
            and bool(bad_lumpability.witnesses)
            and bad_quotient_refused
        ),
        "support_bisimilar_weighted_loss": (
            cycle_support.bisimilar
            and cycle_lumpability.strongly_lumpable
            and cycle_path_transport.commutes
            and cycle_concrete_comparison.total_variation > 0
            and cycle_abstract_comparison.total_variation == 0
        ),
        "sufficient_nontrivial_quotient": (
            hidden_support.bisimilar
            and hidden_lumpability.strongly_lumpable
            and hidden_path_transport.commutes
            and hidden_sufficiency.sufficient
        ),
        "sufficient_quotient_retains_directionality": (
            hidden_concrete_comparison.total_variation
            == hidden_abstract_comparison.total_variation
            and hidden_concrete_comparison.total_variation > 0
        ),
        "finite_total_variation_data_processing": (
            cycle_tv_data_processing and hidden_tv_data_processing
        ),
    }
    kill_conditions = {
        "exact_quotient_depends_on_representative": (
            not exact_lumpability.strongly_lumpable
        ),
        "non_lumpable_quotient_constructed": not bad_quotient_refused,
        "path_transport_checked_only_on_selected_event": (
            not exact_path_transport.commutes
        ),
        "support_bisimulation_reported_as_weight_preservation": (
            cycle_concrete_comparison.total_variation
            == cycle_abstract_comparison.total_variation
        ),
        "lumpability_reported_as_microstatistic_preservation": (
            cycle_sufficiency.sufficient
        ),
        "finite_data_processing_violated": not (
            cycle_tv_data_processing and hidden_tv_data_processing
        ),
        "continuation_consumer_disagrees": not exact_continuation.agrees,
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "retained" if retained else "failed",
        "verdict": (
            "finite_exact_abstraction_machinery_retained"
            if retained
            else "kill_condition_or_case_failure"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "horizon": horizon,
        "case_results": case_results,
        "exact_nontrivial": {
            "lumpability": exact_lumpability.as_dict(),
            "support": exact_support.as_dict(),
            "path_transport": exact_path_transport.as_dict(),
            "continuation": exact_continuation.as_dict(),
            "path_event_probability_concrete_pushforward": fraction_text(
                exact_event_pushed
            ),
            "path_event_probability_quotient": fraction_text(exact_event_quotient),
            "quotient_state_count": len(exact_quotient.states),
            "quotient_transition_row_count": len(exact_quotient.transitions),
        },
        "non_lumpable": {
            "lumpability": bad_lumpability.as_dict(),
            "quotient_refused": bad_quotient_refused,
            "quotient_error": bad_quotient_error,
        },
        "directionality_loss": {
            "lumpability": cycle_lumpability.as_dict(),
            "support": cycle_support.as_dict(),
            "path_transport": cycle_path_transport.as_dict(),
            "concrete_comparison": cycle_concrete_comparison.as_dict(),
            "abstract_comparison": cycle_abstract_comparison.as_dict(),
            "total_variation_loss": fraction_text(
                cycle_concrete_comparison.total_variation
                - cycle_abstract_comparison.total_variation
            ),
            "likelihood_ratio_sufficiency": cycle_sufficiency.as_dict(),
            "data_processing_holds": cycle_tv_data_processing,
        },
        "sufficient_hidden_coordinate": {
            "lumpability": hidden_lumpability.as_dict(),
            "support": hidden_support.as_dict(),
            "path_transport": hidden_path_transport.as_dict(),
            "concrete_comparison": hidden_concrete_comparison.as_dict(),
            "abstract_comparison": hidden_abstract_comparison.as_dict(),
            "total_variation_loss": fraction_text(
                hidden_concrete_comparison.total_variation
                - hidden_abstract_comparison.total_variation
            ),
            "likelihood_ratio_sufficiency": hidden_sufficiency.as_dict(),
            "data_processing_holds": hidden_tv_data_processing,
        },
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite exact controlled Markov state aggregation only. The retained "
            "machinery does not validate an empirical model, unbounded or "
            "continuous dynamics, value, valuerhood, standing, agency, moral "
            "license, Omega compatibility, or a preferred physical orientation."
        ),
    }


def lumpability_rows(summary: dict[str, Any]) -> list[dict[str, object]]:
    return [
        {
            "case": "exact_nontrivial",
            "strongly_lumpable": summary["exact_nontrivial"]["lumpability"][
                "strongly_lumpable"
            ],
            "witness_count": summary["exact_nontrivial"]["lumpability"][
                "witness_count"
            ],
            "maximum_tv_discrepancy": summary["exact_nontrivial"]["lumpability"][
                "maximum_total_variation_discrepancy"
            ],
        },
        {
            "case": "non_lumpable",
            "strongly_lumpable": summary["non_lumpable"]["lumpability"][
                "strongly_lumpable"
            ],
            "witness_count": summary["non_lumpable"]["lumpability"]["witness_count"],
            "maximum_tv_discrepancy": summary["non_lumpable"]["lumpability"][
                "maximum_total_variation_discrepancy"
            ],
        },
        {
            "case": "directionality_loss",
            "strongly_lumpable": summary["directionality_loss"]["lumpability"][
                "strongly_lumpable"
            ],
            "witness_count": summary["directionality_loss"]["lumpability"][
                "witness_count"
            ],
            "maximum_tv_discrepancy": summary["directionality_loss"]["lumpability"][
                "maximum_total_variation_discrepancy"
            ],
        },
        {
            "case": "sufficient_hidden_coordinate",
            "strongly_lumpable": summary["sufficient_hidden_coordinate"][
                "lumpability"
            ]["strongly_lumpable"],
            "witness_count": summary["sufficient_hidden_coordinate"]["lumpability"][
                "witness_count"
            ],
            "maximum_tv_discrepancy": summary["sufficient_hidden_coordinate"][
                "lumpability"
            ]["maximum_total_variation_discrepancy"],
        },
    ]


def path_transport_rows(summary: dict[str, Any]) -> list[dict[str, object]]:
    return [
        {
            "case": case,
            **{
                key: value
                for key, value in summary[case]["path_transport"].items()
                if key != "mismatches"
            },
        }
        for case in (
            "exact_nontrivial",
            "directionality_loss",
            "sufficient_hidden_coordinate",
        )
    ]


def directionality_rows(summary: dict[str, Any]) -> list[dict[str, object]]:
    return [
        {
            "case": case,
            "concrete_total_variation": summary[case]["concrete_comparison"][
                "total_variation"
            ],
            "abstract_total_variation": summary[case]["abstract_comparison"][
                "total_variation"
            ],
            "total_variation_loss": summary[case]["total_variation_loss"],
            "sufficient": summary[case]["likelihood_ratio_sufficiency"]["sufficient"],
            "data_processing_holds": summary[case]["data_processing_holds"],
        }
        for case in ("directionality_loss", "sufficient_hidden_coordinate")
    ]


def continuation_rows(summary: dict[str, Any]) -> list[dict[str, object]]:
    continuation = summary["exact_nontrivial"]["continuation"]
    return [
        {
            "case": "bounded_hit_transport",
            "horizon": continuation["horizon"],
            "target_factors": continuation["target_factors"],
            "agrees": continuation["agrees"],
            "mismatch_count": continuation["mismatch_count"],
            "path_event_probability_concrete_pushforward": summary[
                "exact_nontrivial"
            ]["path_event_probability_concrete_pushforward"],
            "path_event_probability_quotient": summary["exact_nontrivial"][
                "path_event_probability_quotient"
            ],
        }
    ]
