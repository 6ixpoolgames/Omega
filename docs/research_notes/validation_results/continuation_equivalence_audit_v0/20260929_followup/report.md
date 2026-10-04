# Bounded continuation graph equivalence audit v0

Status: PASS
Gates: 379/379

Public development controls. No independent experiment, novelty, efficiency,
or lushness result. Exact predictions, models, graphs, and certificates are
in evidence.json. Timings and whole-representation bytes are in summary.json.

| Case | States | Horizon | Classes by depth |
| --- | --- | --- | --- |
| live | 4 | 1 | [4, 4] |
| replay | 2 | 1 | [2, 2] |
| lookup | 3 | 1 | [3, 3] |
| equivalent_mimic | 8 | 1 | [4, 4] |
| memory | 8 | 2 | [5, 5, 5] |
| seed_h1_b2 | 6 | 1 | [4, 5] |
| seed_h2_b1 | 6 | 2 | [4, 5, 5] |
| seed_h2_b2 | 6 | 2 | [4, 5, 5] |
| inert_h1_b2 | 3 | 1 | [3, 3] |
| inert_h2_b1 | 3 | 2 | [3, 3, 3] |
| inert_h2_b2 | 3 | 2 | [3, 3, 3] |
| hidden_bit | 18 | 2 | [8, 8, 8] |
| revealed_bit | 18 | 2 | [8, 8, 8] |
| repair_1 | 10 | 1 | [5, 6] |
| repair_2 | 10 | 1 | [5, 6] |
| failed_setup | 9 | 2 | [4, 5, 5] |
| clear_history | 4 | 2 | [4, 4, 4] |
| alarm_history | 4 | 2 | [4, 4, 4] |
| partial_cutoff | 4 | 2 | [4, 4, 4] |
| terminal_stop | 2 | 3 | [2, 2, 2, 2] |
| zero_horizon | 4 | 0 | [4] |
| empty_admissible | 4 | 1 | [4, 4] |
| zero_horizon_terminal | 4 | 0 | [4] |
| cost_distinction | 3 | 1 | [2, 3] |
| later_input_over_budget | 3 | 1 | [2, 3] |
| memory_only | 5 | 2 | [5, 5, 5] |
| nuisance_partial_cutoff | 8 | 2 | [4, 4, 4] |

One unreplicated timing per method/case; CPU clock resolution may report zero.
Extraction and prediction are charged; serialization, grading, and writing
evidence are outside method timings. Cache entry counts are not peak memory.
No primary baseline, hardware cap, task workload, or independent test set is frozen.

## Gates

- PASS live.c1_exact
- PASS live.c1_accounting
- PASS live.quotient_exact
- PASS live.quotient_accounting
- PASS live.memoized_exact
- PASS live.partitions
- PASS replay.c1_exact
- PASS replay.c1_accounting
- PASS replay.quotient_exact
- PASS replay.quotient_accounting
- PASS replay.memoized_exact
- PASS replay.partitions
- PASS lookup.c1_exact
- PASS lookup.c1_accounting
- PASS lookup.quotient_exact
- PASS lookup.quotient_accounting
- PASS lookup.memoized_exact
- PASS lookup.partitions
- PASS equivalent_mimic.c1_exact
- PASS equivalent_mimic.c1_accounting
- PASS equivalent_mimic.quotient_exact
- PASS equivalent_mimic.quotient_accounting
- PASS equivalent_mimic.memoized_exact
- PASS equivalent_mimic.partitions
- PASS memory.c1_exact
- PASS memory.c1_accounting
- PASS memory.quotient_exact
- PASS memory.quotient_accounting
- PASS memory.memoized_exact
- PASS memory.partitions
- PASS seed_h1_b2.c1_exact
- PASS seed_h1_b2.c1_accounting
- PASS seed_h1_b2.quotient_exact
- PASS seed_h1_b2.quotient_accounting
- PASS seed_h1_b2.memoized_exact
- PASS seed_h1_b2.partitions
- PASS seed_h2_b1.c1_exact
- PASS seed_h2_b1.c1_accounting
- PASS seed_h2_b1.quotient_exact
- PASS seed_h2_b1.quotient_accounting
- PASS seed_h2_b1.memoized_exact
- PASS seed_h2_b1.partitions
- PASS seed_h2_b2.c1_exact
- PASS seed_h2_b2.c1_accounting
- PASS seed_h2_b2.quotient_exact
- PASS seed_h2_b2.quotient_accounting
- PASS seed_h2_b2.memoized_exact
- PASS seed_h2_b2.partitions
- PASS inert_h1_b2.c1_exact
- PASS inert_h1_b2.c1_accounting
- PASS inert_h1_b2.quotient_exact
- PASS inert_h1_b2.quotient_accounting
- PASS inert_h1_b2.memoized_exact
- PASS inert_h1_b2.partitions
- PASS inert_h2_b1.c1_exact
- PASS inert_h2_b1.c1_accounting
- PASS inert_h2_b1.quotient_exact
- PASS inert_h2_b1.quotient_accounting
- PASS inert_h2_b1.memoized_exact
- PASS inert_h2_b1.partitions
- PASS inert_h2_b2.c1_exact
- PASS inert_h2_b2.c1_accounting
- PASS inert_h2_b2.quotient_exact
- PASS inert_h2_b2.quotient_accounting
- PASS inert_h2_b2.memoized_exact
- PASS inert_h2_b2.partitions
- PASS hidden_bit.c1_exact
- PASS hidden_bit.c1_accounting
- PASS hidden_bit.quotient_exact
- PASS hidden_bit.quotient_accounting
- PASS hidden_bit.memoized_exact
- PASS hidden_bit.partitions
- PASS revealed_bit.c1_exact
- PASS revealed_bit.c1_accounting
- PASS revealed_bit.quotient_exact
- PASS revealed_bit.quotient_accounting
- PASS revealed_bit.memoized_exact
- PASS revealed_bit.partitions
- PASS repair_1.c1_exact
- PASS repair_1.c1_accounting
- PASS repair_1.quotient_exact
- PASS repair_1.quotient_accounting
- PASS repair_1.memoized_exact
- PASS repair_1.partitions
- PASS repair_2.c1_exact
- PASS repair_2.c1_accounting
- PASS repair_2.quotient_exact
- PASS repair_2.quotient_accounting
- PASS repair_2.memoized_exact
- PASS repair_2.partitions
- PASS failed_setup.c1_exact
- PASS failed_setup.c1_accounting
- PASS failed_setup.quotient_exact
- PASS failed_setup.quotient_accounting
- PASS failed_setup.memoized_exact
- PASS failed_setup.partitions
- PASS clear_history.c1_exact
- PASS clear_history.c1_accounting
- PASS clear_history.quotient_exact
- PASS clear_history.quotient_accounting
- PASS clear_history.memoized_exact
- PASS clear_history.partitions
- PASS alarm_history.c1_exact
- PASS alarm_history.c1_accounting
- PASS alarm_history.quotient_exact
- PASS alarm_history.quotient_accounting
- PASS alarm_history.memoized_exact
- PASS alarm_history.partitions
- PASS partial_cutoff.c1_exact
- PASS partial_cutoff.c1_accounting
- PASS partial_cutoff.quotient_exact
- PASS partial_cutoff.quotient_accounting
- PASS partial_cutoff.memoized_exact
- PASS partial_cutoff.partitions
- PASS terminal_stop.c1_exact
- PASS terminal_stop.c1_accounting
- PASS terminal_stop.quotient_exact
- PASS terminal_stop.quotient_accounting
- PASS terminal_stop.memoized_exact
- PASS terminal_stop.partitions
- PASS zero_horizon.c1_exact
- PASS zero_horizon.c1_accounting
- PASS zero_horizon.quotient_exact
- PASS zero_horizon.quotient_accounting
- PASS zero_horizon.memoized_exact
- PASS zero_horizon.partitions
- PASS empty_admissible.c1_exact
- PASS empty_admissible.c1_accounting
- PASS empty_admissible.quotient_exact
- PASS empty_admissible.quotient_accounting
- PASS empty_admissible.memoized_exact
- PASS empty_admissible.partitions
- PASS zero_horizon_terminal.c1_exact
- PASS zero_horizon_terminal.c1_accounting
- PASS zero_horizon_terminal.quotient_exact
- PASS zero_horizon_terminal.quotient_accounting
- PASS zero_horizon_terminal.memoized_exact
- PASS zero_horizon_terminal.partitions
- PASS cost_distinction.c1_exact
- PASS cost_distinction.c1_accounting
- PASS cost_distinction.quotient_exact
- PASS cost_distinction.quotient_accounting
- PASS cost_distinction.memoized_exact
- PASS cost_distinction.partitions
- PASS later_input_over_budget.c1_exact
- PASS later_input_over_budget.c1_accounting
- PASS later_input_over_budget.quotient_exact
- PASS later_input_over_budget.quotient_accounting
- PASS later_input_over_budget.memoized_exact
- PASS later_input_over_budget.partitions
- PASS memory_only.c1_exact
- PASS memory_only.c1_accounting
- PASS memory_only.quotient_exact
- PASS memory_only.quotient_accounting
- PASS memory_only.memoized_exact
- PASS memory_only.partitions
- PASS nuisance_partial_cutoff.c1_exact
- PASS nuisance_partial_cutoff.c1_accounting
- PASS nuisance_partial_cutoff.quotient_exact
- PASS nuisance_partial_cutoff.quotient_accounting
- PASS nuisance_partial_cutoff.memoized_exact
- PASS nuisance_partial_cutoff.partitions
- PASS reference.replay.passive_match
- PASS reference.replay.intervention_separates
- PASS reference.lookup.development_match
- PASS reference.lookup.public_probe_separates
- PASS reference.equivalent_mimic.all_commands
- PASS reference.seed_h1_b2.witness
- PASS reference.seed_h1_b2
- PASS reference.seed_h2_b1.witness
- PASS reference.seed_h2_b1
- PASS reference.seed_h2_b2.witness
- PASS reference.seed_h2_b2
- PASS reference.inert_h1_b2.witness
- PASS reference.inert_h1_b2
- PASS reference.inert_h2_b1.witness
- PASS reference.inert_h2_b1
- PASS reference.inert_h2_b2.witness
- PASS reference.inert_h2_b2
- PASS reference.hidden_bit.witness
- PASS reference.hidden_bit
- PASS reference.revealed_bit.witness
- PASS reference.revealed_bit
- PASS reference.memory.witness
- PASS reference.memory
- PASS reference.repair_1.witness
- PASS reference.repair_1
- PASS reference.repair_2.witness
- PASS reference.repair_2
- PASS reference.failed_setup.witness
- PASS reference.failed_setup
- PASS reference.partial_cutoff.witness
- PASS reference.partial_cutoff
- PASS reference.terminal_stop.witness
- PASS reference.terminal_stop
- PASS reference.zero_horizon.witness
- PASS reference.zero_horizon
- PASS reference.zero_horizon_terminal.witness
- PASS reference.zero_horizon_terminal
- PASS reference.empty_admissible.witness
- PASS reference.empty_admissible
- PASS reference.later_input_over_budget.rejected
- PASS reference.later_input_over_budget.no_admitted
- PASS reference.memory_only.input_0
- PASS reference.memory_only.input_1
- PASS reference.alarm_history.witness
- PASS reference.alarm_history
- PASS reference.clear_history.witness
- PASS reference.clear_history
- PASS reference.identifiability.range
- PASS reference.identifiability.expanded
- PASS reference.identifiability.inconsistent
- PASS reference.equivalent_mimic_full_invariance
- PASS reference.nuisance_partial_cutoff_full_invariance
- PASS c1.replay.passive_match
- PASS c1.replay.intervention_separates
- PASS c1.lookup.development_match
- PASS c1.lookup.public_probe_separates
- PASS c1.equivalent_mimic.all_commands
- PASS c1.seed_h1_b2.witness
- PASS c1.seed_h1_b2
- PASS c1.seed_h2_b1.witness
- PASS c1.seed_h2_b1
- PASS c1.seed_h2_b2.witness
- PASS c1.seed_h2_b2
- PASS c1.inert_h1_b2.witness
- PASS c1.inert_h1_b2
- PASS c1.inert_h2_b1.witness
- PASS c1.inert_h2_b1
- PASS c1.inert_h2_b2.witness
- PASS c1.inert_h2_b2
- PASS c1.hidden_bit.witness
- PASS c1.hidden_bit
- PASS c1.revealed_bit.witness
- PASS c1.revealed_bit
- PASS c1.memory.witness
- PASS c1.memory
- PASS c1.repair_1.witness
- PASS c1.repair_1
- PASS c1.repair_2.witness
- PASS c1.repair_2
- PASS c1.failed_setup.witness
- PASS c1.failed_setup
- PASS c1.partial_cutoff.witness
- PASS c1.partial_cutoff
- PASS c1.terminal_stop.witness
- PASS c1.terminal_stop
- PASS c1.zero_horizon.witness
- PASS c1.zero_horizon
- PASS c1.zero_horizon_terminal.witness
- PASS c1.zero_horizon_terminal
- PASS c1.empty_admissible.witness
- PASS c1.empty_admissible
- PASS c1.later_input_over_budget.rejected
- PASS c1.later_input_over_budget.no_admitted
- PASS c1.memory_only.input_0
- PASS c1.memory_only.input_1
- PASS c1.alarm_history.witness
- PASS c1.alarm_history
- PASS c1.clear_history.witness
- PASS c1.clear_history
- PASS c1.identifiability.range
- PASS c1.identifiability.expanded
- PASS c1.identifiability.inconsistent
- PASS c1.equivalent_mimic_full_invariance
- PASS c1.nuisance_partial_cutoff_full_invariance
- PASS quotient.replay.passive_match
- PASS quotient.replay.intervention_separates
- PASS quotient.lookup.development_match
- PASS quotient.lookup.public_probe_separates
- PASS quotient.equivalent_mimic.all_commands
- PASS quotient.seed_h1_b2.witness
- PASS quotient.seed_h1_b2
- PASS quotient.seed_h2_b1.witness
- PASS quotient.seed_h2_b1
- PASS quotient.seed_h2_b2.witness
- PASS quotient.seed_h2_b2
- PASS quotient.inert_h1_b2.witness
- PASS quotient.inert_h1_b2
- PASS quotient.inert_h2_b1.witness
- PASS quotient.inert_h2_b1
- PASS quotient.inert_h2_b2.witness
- PASS quotient.inert_h2_b2
- PASS quotient.hidden_bit.witness
- PASS quotient.hidden_bit
- PASS quotient.revealed_bit.witness
- PASS quotient.revealed_bit
- PASS quotient.memory.witness
- PASS quotient.memory
- PASS quotient.repair_1.witness
- PASS quotient.repair_1
- PASS quotient.repair_2.witness
- PASS quotient.repair_2
- PASS quotient.failed_setup.witness
- PASS quotient.failed_setup
- PASS quotient.partial_cutoff.witness
- PASS quotient.partial_cutoff
- PASS quotient.terminal_stop.witness
- PASS quotient.terminal_stop
- PASS quotient.zero_horizon.witness
- PASS quotient.zero_horizon
- PASS quotient.zero_horizon_terminal.witness
- PASS quotient.zero_horizon_terminal
- PASS quotient.empty_admissible.witness
- PASS quotient.empty_admissible
- PASS quotient.later_input_over_budget.rejected
- PASS quotient.later_input_over_budget.no_admitted
- PASS quotient.memory_only.input_0
- PASS quotient.memory_only.input_1
- PASS quotient.alarm_history.witness
- PASS quotient.alarm_history
- PASS quotient.clear_history.witness
- PASS quotient.clear_history
- PASS quotient.identifiability.range
- PASS quotient.identifiability.expanded
- PASS quotient.identifiability.inconsistent
- PASS quotient.equivalent_mimic_full_invariance
- PASS quotient.nuisance_partial_cutoff_full_invariance
- PASS memoized.replay.passive_match
- PASS memoized.replay.intervention_separates
- PASS memoized.lookup.development_match
- PASS memoized.lookup.public_probe_separates
- PASS memoized.equivalent_mimic.all_commands
- PASS memoized.seed_h1_b2.witness
- PASS memoized.seed_h1_b2
- PASS memoized.seed_h2_b1.witness
- PASS memoized.seed_h2_b1
- PASS memoized.seed_h2_b2.witness
- PASS memoized.seed_h2_b2
- PASS memoized.inert_h1_b2.witness
- PASS memoized.inert_h1_b2
- PASS memoized.inert_h2_b1.witness
- PASS memoized.inert_h2_b1
- PASS memoized.inert_h2_b2.witness
- PASS memoized.inert_h2_b2
- PASS memoized.hidden_bit.witness
- PASS memoized.hidden_bit
- PASS memoized.revealed_bit.witness
- PASS memoized.revealed_bit
- PASS memoized.memory.witness
- PASS memoized.memory
- PASS memoized.repair_1.witness
- PASS memoized.repair_1
- PASS memoized.repair_2.witness
- PASS memoized.repair_2
- PASS memoized.failed_setup.witness
- PASS memoized.failed_setup
- PASS memoized.partial_cutoff.witness
- PASS memoized.partial_cutoff
- PASS memoized.terminal_stop.witness
- PASS memoized.terminal_stop
- PASS memoized.zero_horizon.witness
- PASS memoized.zero_horizon
- PASS memoized.zero_horizon_terminal.witness
- PASS memoized.zero_horizon_terminal
- PASS memoized.empty_admissible.witness
- PASS memoized.empty_admissible
- PASS memoized.later_input_over_budget.rejected
- PASS memoized.later_input_over_budget.no_admitted
- PASS memoized.memory_only.input_0
- PASS memoized.memory_only.input_1
- PASS memoized.alarm_history.witness
- PASS memoized.alarm_history
- PASS memoized.clear_history.witness
- PASS memoized.clear_history
- PASS memoized.identifiability.range
- PASS memoized.identifiability.expanded
- PASS memoized.identifiability.inconsistent
- PASS memoized.equivalent_mimic_full_invariance
- PASS memoized.nuisance_partial_cutoff_full_invariance
- PASS cost_accounting.synthetic_nonzero_extraction
- PASS edge_cost.base_equal
- PASS edge_cost.depth_one_separates
- PASS equivalent_mimic.partition_invariance
- PASS nuisance_partial_cutoff.partition_invariance
- PASS interface.c1.reject_incompatible
- PASS interface.quotient.reject_incompatible
- PASS interface.reference.reject_incompatible
- PASS interface.memoized.reject_incompatible
