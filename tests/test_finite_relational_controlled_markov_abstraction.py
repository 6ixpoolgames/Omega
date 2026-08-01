from fractions import Fraction
from pathlib import Path

import pytest

from omega_v2.experiments.controlled_markov_abstraction_v0 import (
    biased_cycle_fixture,
    controlled_markov_abstraction_summary,
    exact_nontrivial_fixture,
    non_lumpable_fixture,
    sufficient_hidden_cycle_fixture,
)
from omega_v2.finite.abstraction import (
    abstract_policy,
    audit_actionwise_lumpability,
    audit_path_law_pushforward,
    audit_policy_factorization,
    audit_predicate_factorization,
    audit_support_bisimulation,
    build_quotient_kernel,
    pushforward_initial_distribution,
)
from omega_v2.finite.continuation import (
    audit_bounded_hit_transport,
    bounded_hit_probability,
    safe_through_horizon_probability,
)
from omega_v2.finite.model import (
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
)
from omega_v2.finite.path_laws import (
    ActionInvolution,
    abstract_path,
    audit_likelihood_ratio_sufficiency,
    event_probability,
    finite_path_law,
    pull_back_reversed_path_law,
    pushforward_path_law,
    total_variation_distance,
)
from omega_v2.validation.controlled_markov_abstraction_v0 import (
    render_report,
    run_controlled_markov_abstraction_v0,
)


def test_clean_package_is_independent_of_historical_omega() -> None:
    package_root = Path("omega_v2")
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in package_root.rglob("*.py")
    )
    assert "from omega." not in source
    assert "import omega." not in source


def test_finite_distribution_requires_exact_normalization() -> None:
    with pytest.raises(ValueError, match="sum exactly to one"):
        FiniteDistribution(rows=(("left", Fraction(1, 3)), ("right", Fraction(1, 3))))

    law = FiniteDistribution(rows=(("left", Fraction(1, 2)), ("right", Fraction(1, 2))))
    pushed = law.pushforward(lambda _outcome: "merged")
    assert pushed == FiniteDistribution.point_mass("merged")


def test_controlled_system_requires_every_state_action_row() -> None:
    with pytest.raises(ValueError, match="must be nonempty"):
        ControlledMarkovSystem(
            system_id="partial",
            states=("s",),
            actions=("a", "b"),
            transitions=(("s", "a", "s", Fraction(1)),),
        )


def test_exact_nontrivial_aggregation_is_lumpable_and_builds_quotient() -> None:
    system, aggregation, policy, _initial = exact_nontrivial_fixture()
    audit = audit_actionwise_lumpability(system, aggregation)
    quotient = build_quotient_kernel(system, aggregation)

    assert audit.strongly_lumpable
    assert audit.maximum_total_variation_discrepancy == 0
    assert quotient.states == ("A", "B")
    assert quotient.distribution("A", "mix").mass_map == {
        "A": Fraction(1, 4),
        "B": Fraction(3, 4),
    }
    assert abstract_policy(system, aggregation, policy).action_map == {
        "A": "mix",
        "B": "hold",
    }


def test_non_lumpable_aggregation_returns_exact_witness_and_refuses_quotient() -> None:
    system, aggregation = non_lumpable_fixture()
    audit = audit_actionwise_lumpability(system, aggregation)

    assert not audit.strongly_lumpable
    assert audit.witnesses
    assert audit.maximum_total_variation_discrepancy == Fraction(1, 2)
    witness = audit.witnesses[0]
    assert {witness.left_mass, witness.right_mass} == {
        Fraction(1, 4),
        Fraction(3, 4),
    }
    with pytest.raises(ValueError, match="not action-wise strongly lumpable"):
        build_quotient_kernel(system, aggregation)


def test_policy_factorization_is_checked_separately() -> None:
    system, aggregation, _policy, _initial = exact_nontrivial_fixture()
    split_policy = DeterministicPolicy(
        policy_id="split_A",
        rows=(("A0", "mix"), ("A1", "hold"), ("B0", "hold"), ("B1", "hold")),
    )
    audit = audit_policy_factorization(system, aggregation, split_policy)

    assert not audit.factors
    assert len(audit.witnesses) == 1
    with pytest.raises(ValueError, match="does not factor"):
        abstract_policy(system, aggregation, split_policy)


def test_predicate_factorization_blocks_mixed_state_labels() -> None:
    _system, aggregation, _policy, _initial = exact_nontrivial_fixture()
    factors = audit_predicate_factorization(
        aggregation,
        lambda state: state.startswith("B"),
    )
    mixed = audit_predicate_factorization(
        aggregation,
        lambda state: state.endswith("0"),
    )

    assert factors.factors
    assert not mixed.factors
    assert len(mixed.witnesses) == 2


def test_full_finite_path_law_pushforward_commutes() -> None:
    system, aggregation, policy, initial = exact_nontrivial_fixture()
    audit = audit_path_law_pushforward(
        system,
        aggregation,
        policy,
        initial,
        horizon=3,
    )

    assert audit.commutes
    assert audit.total_variation == 0
    assert not audit.mismatches
    assert audit.concrete_path_count > audit.abstract_path_count


def test_abstract_path_event_probability_is_preserved() -> None:
    system, aggregation, policy, initial = exact_nontrivial_fixture()
    quotient = build_quotient_kernel(system, aggregation)
    concrete = finite_path_law(system, policy, initial, horizon=3)
    pushed = pushforward_path_law(concrete, aggregation)
    abstract = finite_path_law(
        quotient,
        abstract_policy(system, aggregation, policy),
        pushforward_initial_distribution(initial, aggregation),
        horizon=3,
    )

    assert event_probability(pushed, lambda path: "B" in path.states) == event_probability(
        abstract,
        lambda path: "B" in path.states,
    )


def test_bounded_continuation_consumer_agrees_on_exact_quotient() -> None:
    system, aggregation, policy, _initial = exact_nontrivial_fixture()
    audit = audit_bounded_hit_transport(
        system,
        aggregation,
        policy,
        ("B0", "B1"),
        horizon=2,
    )

    assert audit.target_factors
    assert audit.agrees
    assert not audit.mismatches
    assert bounded_hit_probability(
        system,
        policy,
        ("B0", "B1"),
        start="A0",
        horizon=2,
    ) == Fraction(15, 16)


def test_nonfactoring_target_is_not_transported() -> None:
    system, aggregation, policy, _initial = exact_nontrivial_fixture()
    audit = audit_bounded_hit_transport(
        system,
        aggregation,
        policy,
        ("B0",),
        horizon=2,
    )

    assert not audit.target_factors
    assert not audit.agrees


def test_safe_through_horizon_is_a_real_weighted_consumer() -> None:
    system, _aggregation, policy, _initial = exact_nontrivial_fixture()
    assert safe_through_horizon_probability(
        system,
        policy,
        ("A0", "A1"),
        start="A0",
        horizon=2,
    ) == Fraction(1, 16)


def test_support_bisimulation_and_lumpability_do_not_preserve_micro_directionality() -> None:
    system, aggregation, policy, initial = biased_cycle_fixture()
    quotient = build_quotient_kernel(system, aggregation)
    support = audit_support_bisimulation(system, quotient, aggregation)
    transport = audit_path_law_pushforward(
        system,
        aggregation,
        policy,
        initial,
        horizon=3,
    )
    forward = finite_path_law(system, policy, initial, horizon=3)
    reverse = pull_back_reversed_path_law(
        forward,
        ActionInvolution(rows=(("advance", "advance"),)),
    )
    concrete_tv = total_variation_distance(forward, reverse)
    abstract_tv = total_variation_distance(
        pushforward_path_law(forward, aggregation),
        pushforward_path_law(reverse, aggregation),
    )

    assert support.bisimilar
    assert audit_actionwise_lumpability(system, aggregation).strongly_lumpable
    assert transport.commutes
    assert concrete_tv == Fraction(11, 16)
    assert abstract_tv == 0


def test_hidden_coordinate_quotient_is_sufficient_for_directionality() -> None:
    system, aggregation, policy, initial = sufficient_hidden_cycle_fixture()
    forward = finite_path_law(system, policy, initial, horizon=3)
    reverse = pull_back_reversed_path_law(
        forward,
        ActionInvolution(rows=(("advance", "advance"),)),
    )
    sufficiency = audit_likelihood_ratio_sufficiency(
        forward,
        reverse,
        lambda path: abstract_path(path, aggregation),
    )
    concrete_tv = total_variation_distance(forward, reverse)
    abstract_tv = total_variation_distance(
        pushforward_path_law(forward, aggregation),
        pushforward_path_law(reverse, aggregation),
    )

    assert audit_actionwise_lumpability(system, aggregation).strongly_lumpable
    assert sufficiency.sufficient
    assert concrete_tv == abstract_tv == Fraction(11, 16)


def test_total_variation_obeys_data_processing_in_retained_fixtures() -> None:
    for fixture in (biased_cycle_fixture, sufficient_hidden_cycle_fixture):
        system, aggregation, policy, initial = fixture()
        forward = finite_path_law(system, policy, initial, horizon=3)
        reverse = pull_back_reversed_path_law(
            forward,
            ActionInvolution(rows=(("advance", "advance"),)),
        )
        assert total_variation_distance(
            pushforward_path_law(forward, aggregation),
            pushforward_path_law(reverse, aggregation),
        ) <= total_variation_distance(forward, reverse)


def test_preregistered_summary_retains_all_cases_without_kill_condition() -> None:
    summary = controlled_markov_abstraction_summary(horizon=3)

    assert summary["status"] == "retained"
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert summary["non_lumpable"]["quotient_refused"]
    assert (
        summary["directionality_loss"]["likelihood_ratio_sufficiency"]["sufficient"]
        is False
    )
    assert (
        summary["sufficient_hidden_coordinate"]["likelihood_ratio_sufficiency"][
            "sufficient"
        ]
        is True
    )


def test_preregistered_summary_is_deterministic() -> None:
    assert controlled_markov_abstraction_summary(
        horizon=3
    ) == controlled_markov_abstraction_summary(horizon=3)


def test_validation_writes_machine_readable_artifacts(tmp_path: Path) -> None:
    result = run_controlled_markov_abstraction_v0(
        out_root=tmp_path,
        horizon=3,
    )
    run_root = Path(result["run_root"])

    assert result["status"] == "retained"
    assert (run_root / "summary.json").exists()
    assert (run_root / "lumpability.csv").exists()
    assert (run_root / "path_transport.csv").exists()
    assert (run_root / "directionality_loss.csv").exists()
    assert (run_root / "continuation_events.csv").exists()
    assert (run_root / "report.md").exists()
    assert "Weighted Directionality Loss" in render_report(result)
