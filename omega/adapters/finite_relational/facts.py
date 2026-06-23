"""Backward-compatible finite relational facts facade.

The implementation is split by theory surface; this module re-exports the
legacy public names used by adapter code and downstream tests.
"""

from __future__ import annotations

from omega.adapters.finite_relational.facts_common import (
    Pair,
    binary_relation,
    function_merges,
    internal_edges,
    presentation_violations,
    reachable_pairs,
    ternary_relation,
)
from omega.adapters.finite_relational.facts_dynamics import (
    dynamic_edge_projection_exactness_facts,
    dynamic_path_lifting_facts,
    dynamic_presentation_equivariance_facts,
    dynamic_step_lifting_facts,
)
from omega.adapters.finite_relational.facts_language import (
    extendable_safe_prefix_count_facts,
    observed_extendable_safe_word_count_facts,
    observed_word_lifting_monotonicity_facts,
    safe_prefix_count_facts,
    viable_trajectory_count_comparison_facts,
    viable_trajectory_count_facts,
)
from omega.adapters.finite_relational.facts_presentation import (
    common_target_predicates,
    common_visible_pairs,
    nonfactorization_witnesses_for_predicate,
    predicate_is_constant,
    predicate_respects_presentation,
    presentation_fact_closure_facts,
    presentation_fact_derive_closure_facts,
)
from omega.adapters.finite_relational.facts_recovery import (
    bounded_recovery_facts,
    target_scramble_capacity_sensitivity_facts,
    target_scramble_sensitivity_facts,
    unrestricted_exact_recovery_facts,
)
from omega.adapters.finite_relational.facts_carrier import (
    carrier_certificate_facts,
    carrier_transfer_facts,
)

__all__ = [
    "Pair",
    "binary_relation",
    "bounded_recovery_facts",
    "carrier_certificate_facts",
    "carrier_transfer_facts",
    "common_target_predicates",
    "common_visible_pairs",
    "dynamic_edge_projection_exactness_facts",
    "dynamic_path_lifting_facts",
    "dynamic_presentation_equivariance_facts",
    "dynamic_step_lifting_facts",
    "extendable_safe_prefix_count_facts",
    "function_merges",
    "internal_edges",
    "nonfactorization_witnesses_for_predicate",
    "observed_extendable_safe_word_count_facts",
    "observed_word_lifting_monotonicity_facts",
    "predicate_is_constant",
    "predicate_respects_presentation",
    "presentation_fact_closure_facts",
    "presentation_fact_derive_closure_facts",
    "presentation_violations",
    "reachable_pairs",
    "safe_prefix_count_facts",
    "target_scramble_capacity_sensitivity_facts",
    "target_scramble_sensitivity_facts",
    "ternary_relation",
    "unrestricted_exact_recovery_facts",
    "viable_trajectory_count_comparison_facts",
    "viable_trajectory_count_facts",
]
