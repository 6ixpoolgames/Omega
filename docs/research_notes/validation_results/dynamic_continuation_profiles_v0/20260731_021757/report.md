# Dynamic Continuation Profiles v0 Report

Status: PASS
Verdict: retained
Protocol: `docs/research_notes/omega_v2/dynamic_continuation_profiles_protocol_v0.md`

## Case Results

- duplicate_outcome: True
- duplicate_action: True
- novel_branch: True
- delayed_divergence: True
- action_outcome_quantifier: True
- deformation: True
- presentation: True
- switching_adaptive: True
- lushness_bridge: True

## Duplicate Resistance

- Raw edge count changes: True
- Root behavior types equal: True
- Derived profiles equal: True
- Effect-equivalent duplicate action is idempotent: True

## Novelty And Horizon

- Novel branch strictly refines base: True
- Strict new represented capabilities: 1
- First delayed-divergence separation depth: 2

## Controller And Environment Quantifiers

- Flattened successor unions equal: True
- Nested behavior types equal: False
- Choice strictly refines risk: True

## Dynamic Deformation

- expansion: expansion
- contraction: contraction
- equivalent: equivalent
- mixed: mixed

## Presentation Control

- State relabeling preserves behavior type/profile: True/True
- Action relabeling preserves behavior type/profile: True/True
- Atom-respect failures in unsound merge: 1
- Unsound abstraction rejected: True

## Switching And Adaptive Dynamics

- Status: adaptive-strictly-refines-switching
- First strict adaptive horizon: 2
- Sound-update truth-preservation failures: 0
- Information-state atoms excluded: True

## Lushness Instrument Bridge

- Duplicate family profile remains equal: True
- Novel family profile is strict: True
- Attributes are dynamic fingerprints: True

## Negative Controls

- state_relabeling_invariant: True
- action_relabeling_invariant: True
- duplicate_branch_idempotent: True
- effect_equivalent_action_idempotent: True
- atom_respect_failure_visible: True
- flat_union_not_control_type: True
- profile_identifiers_exclude_state_action_tokens: True
- raw_counts_not_primary: True
- negative_controls_pass: True

## Interpretation

Primary instrument: bounded behavioral down-sets under alternating simulation.
Bridge: dynamic fingerprints populate the retained jointly realizable family profile without hand-named attributes.
Remaining debt: positive atoms, process boundaries, comparison basis, and horizon remain explicit instrumentation inputs.

## Claim Boundary

This finite pilot does not prove value, valuerhood, standing, agency, autonomy, patienthood, universal lushness, thermodynamic law, moral licensing, paperclipper defeat, or Omega validation.
