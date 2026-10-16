# Operational continuation comparison v0

Status: PASS
Passing acceptance gates: 40/40

Exact finite acceptance cases, not empirical validation of lushness or value.
Source hashes and revision are in provenance.json; complete paths, local
controller tables, costs and transition laws are in evidence.json.
Emulation witnesses and first differing inputs are in summary.json.

| Case / response frame | Achievement | Left emulates right | Right emulates left |
| --- | --- | --- | --- |
| bit | left_strict | holds | fails |
| choice | left_strict | holds | fails |
| choice_without_coin | left_strict | fails | fails |
| repair_marginals | equivalent | holds | fails |
| repair_joint | left_strict | holds | fails |
| build_service | left_strict | holds | fails |
| build_savings | incomparable | fails | fails |
| history_endpoint | equivalent | holds | holds |
| history_full | incomparable | fails | fails |

## Interpretive limits

All controller programmes are installed catalogue entries. Costs cover
declared operations, not apparatus manufacture. Output projections are
explicit; output emulation does not imply preservation of omitted costs
or history. No free policy randomization or hidden-input selector exists.
The comparison is finite response emulation, not a general online adapter
or a compositional resource-conversion theorem.

## Gates

- PASS bit.achievement: observed 'left_strict'; expected 'left_strict'
- PASS choice.achievement: observed 'left_strict'; expected 'left_strict'
- PASS choice_without_coin.achievement: observed 'left_strict'; expected 'left_strict'
- PASS repair_marginals.achievement: observed 'equivalent'; expected 'equivalent'
- PASS repair_joint.achievement: observed 'left_strict'; expected 'left_strict'
- PASS build_service.achievement: observed 'left_strict'; expected 'left_strict'
- PASS build_savings.achievement: observed 'incomparable'; expected 'incomparable'
- PASS history_endpoint.achievement: observed 'equivalent'; expected 'equivalent'
- PASS history_full.achievement: observed 'incomparable'; expected 'incomparable'
- PASS bit.left_emulates_right: observed 'holds'; expected 'holds'
- PASS bit.right_emulates_left: observed 'fails'; expected 'fails'
- PASS choice.left_emulates_right: observed 'holds'; expected 'holds'
- PASS choice.right_emulates_left: observed 'fails'; expected 'fails'
- PASS choice_without_coin.left_emulates_right: observed 'fails'; expected 'fails'
- PASS choice_without_coin.right_emulates_left: observed 'fails'; expected 'fails'
- PASS repair_marginals.left_emulates_right: observed 'holds'; expected 'holds'
- PASS repair_marginals.right_emulates_left: observed 'fails'; expected 'fails'
- PASS repair_joint.left_emulates_right: observed 'holds'; expected 'holds'
- PASS repair_joint.right_emulates_left: observed 'fails'; expected 'fails'
- PASS build_service.left_emulates_right: observed 'holds'; expected 'holds'
- PASS build_service.right_emulates_left: observed 'fails'; expected 'fails'
- PASS build_savings.left_emulates_right: observed 'fails'; expected 'fails'
- PASS build_savings.right_emulates_left: observed 'fails'; expected 'fails'
- PASS history_endpoint.left_emulates_right: observed 'holds'; expected 'holds'
- PASS history_endpoint.right_emulates_left: observed 'holds'; expected 'holds'
- PASS history_full.left_emulates_right: observed 'fails'; expected 'fails'
- PASS history_full.right_emulates_left: observed 'fails'; expected 'fails'
- PASS hidden_guess: observed '1/2'; expected '1/2'
- PASS revealed_guess: observed '1'; expected '1'
- PASS invalid_branchwise_optimization: observed '1'; expected '1'
- PASS failed_setup_keeps_failure: observed '1/2'; expected '1/2'
- PASS passive_equal_pairs: observed 21; expected 21
- PASS passive_incomparable_pairs: observed 420; expected 420
- PASS build_horizon_budget_profile: observed [None, '0', '0', None, '0', '1']; expected [None, '0', '0', None, '0', '1']
- PASS partial_cutoff.total_mass: observed '1'; expected '1'
- PASS partial_cutoff.completed_mass: observed '1/3'; expected '1/3'
- PASS partial_cutoff.censored_mass: observed '2/3'; expected '2/3'
- PASS partial_cutoff.runs: observed [['done', '1/3', 1, 1, False], ['slow2', '2/3', 2, 2, True]]; expected [['done', '1/3', 1, 1, False], ['slow2', '2/3', 2, 2, True]]
- PASS terminal_stop.runs: observed [['done', '1', 1, 1, False]]; expected [['done', '1', 1, 1, False]]
- PASS terminal_stop.admissible: observed 1; expected 1
