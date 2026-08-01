# Finite Controlled Markov Abstraction v0 Validation

Status: retained
Verdict: finite_exact_abstraction_machinery_retained
Protocol: `docs/research_notes/omega_v2/finite_controlled_markov_abstraction_protocol_v0.md`
Finite path horizon: 3

## Case Results

- exact_nontrivial_lumpability: True
- exact_quotient_support_bisimulation: True
- exact_full_path_law_pushforward: True
- exact_path_event_preservation: True
- bounded_continuation_transport: True
- non_lumpable_rejected_with_witness: True
- support_bisimilar_weighted_loss: True
- sufficient_nontrivial_quotient: True
- sufficient_quotient_retains_directionality: True
- finite_total_variation_data_processing: True

## Exact Nontrivial Quotient

- Action-aware strong lumpability: True
- Support bisimulation: True
- Full path-law pushforward: True
- Bounded target-hit transport: True
- Path-event mass, pushed concrete / quotient: 63/64 / 63/64

## Rejected Aggregation

- Action-aware strong lumpability: False
- Exact witness count: 2
- Maximum representative TV discrepancy: 1/2
- Quotient construction refused: True

## Weighted Directionality Loss

- Support bisimulation: True
- Strong lumpability: True
- Full path-law pushforward: True
- Concrete / aggregate total variation: 11/16 / 0
- Likelihood-ratio sufficiency: False
- Data processing holds: True

## Sufficient Hidden-Coordinate Quotient

- Strong lumpability / full path-law pushforward: True / True
- Concrete / aggregate total variation: 11/16 / 11/16
- Likelihood-ratio sufficiency: True
- Data processing holds: True

## Kill Conditions

- exact_quotient_depends_on_representative: False
- non_lumpable_quotient_constructed: False
- path_transport_checked_only_on_selected_event: False
- support_bisimulation_reported_as_weight_preservation: False
- lumpability_reported_as_microstatistic_preservation: False
- finite_data_processing_violated: False
- continuation_consumer_disagrees: False

## Claim Boundary

Finite exact controlled Markov state aggregation only. The retained machinery does not validate an empirical model, unbounded or continuous dynamics, value, valuerhood, standing, agency, moral license, Omega compatibility, or a preferred physical orientation.
