# Recurrent Support Integrity v0

Status: consolidation note
Scope: public facade for recurrent support carry/loss/transfer/restoration/rerouting/extension/successor handoff/budget/joint failure
Claim boundary: not identity, not agency, not deformer theory, not value, not Omega validation

## Purpose

This note introduces the consolidated recurrent-support integrity surface:

```text
formal/lean/OmegaProper/Trajectory/RecurrentSupportIntegrity.lean
```

The module is a facade. It does not add new ontology or new proof obligations.
It gathers the current recurrent-support story under one import:

```text
support carries a distinction;
support can lose carrying;
support can transfer carrying under contracts;
support can restore carrying after loss;
support can reroute carrying through replacement internal paths;
support can extend carrying into a larger declared support;
support can hand carrying to a translated successor distinction;
support has a first exact perturbation-budget floor;
individual carrying need not compose into joint carrying;
the one-way loss pattern holds in a bounded finite family.
```

## Public vocabulary

The facade gives short public aliases:

```text
Carries
IntegrityUnder
DestroyedUnder
EdgeTransferContract
PathTransferContract
ExtensionContract
SuccessorContract
```

These are wrappers around the existing definitions in:

```text
RecurrentSupportRobustness
RecurrentSupportTransfer
RecurrentSupportPathTransfer
```

The point is not to hide the detailed files. The point is to let readers see
the recurrent-support story as one layer instead of a scatter of exploratory
modules.

## Headline wrappers

The facade exposes the central results:

```text
carries_transfers_by_edge_contract
carries_transfers_by_path_contract
edge_contract_implies_path_contract
destroyed_blocks_integrity
carries_extends_by_contract
carries_successor_by_contract
two_state_cycle_carries_left_right
two_state_one_way_loss_witness
two_state_loss_and_restoration_witness
two_state_perturbation_budget_floor
individual_vs_joint_recurrent_support_witness
rerouted_path_transfer_strictness_witness
strict_support_extension_witness_public
successor_distinction_handoff_witness_public
bounded_family_one_way_loss_witness
```

The current strongest summary is:

```text
Endpoint viability and forward reachability are not enough.
Recurrent carrying needs return structure or replacement internal paths.
```

## Why this layer matters

The recurrent-support stack is the first finite local perturbation calculus in
the project. It shows:

```text
what carries a consequence distinction;
what destroys that carrying;
what contracts preserve it;
how rerouting can preserve it without exact edge identity;
how carrying can move into a larger support without same-support identity;
how carrying can move to a translated pair under an explicit relation;
how zero dynamic change cannot destroy carrying, while one return-edge removal
can destroy it;
how individual recurrent carrying under separate constraints can fail under a
shared joint constraint;
how the basic one-way-loss pattern generalizes across a finite family.
```

That is a real bridge from consequence-bearing distinction to support-level
continuation structure.

It is not a theory of selfhood or agent identity. The claims are about declared
supports, declared distinctions, and explicit recurrence/path contracts.

## Why the facade matters

The lower files were useful while the theory was being discovered:

```text
SupportUnderPerturbation
RecurrentSupportRobustness
IrreversibleRecurrentSupportLoss
RecurrentSupportTransfer
RecurrentSupportRestoration
RecurrentSupportPathTransfer
RecurrentSupportExtension
RecurrentSupportSuccessorDistinction
RecurrentSupportPerturbationBudget
JointRecurrentSupport
ParameterizedRecurrentSupport
```

But the public stack should not require a new reader to infer the story from
file names. `RecurrentSupportIntegrity` is the compressed import surface.

## Next extensions

The facade now includes first support-extension, lineage, successor-distinction,
perturbation-budget, and joint recurrent-support failure results. These are
still pair-relative and exact. The next formal targets remain:

1. General perturbation budgets:
   minimum cuts, repair budgets, and adapter-level probabilistic robustness.

2. Positive joint recurrent support contracts:
   conditions under which multiple supports remain jointly viable and carrying.

## Related notes

- [layer_a_theorem_spine_v0.md](layer_a_theorem_spine_v0.md)
- [recurrent_support_perturbation_floor_v0.md](recurrent_support_perturbation_floor_v0.md)
- [recurrent_support_perturbation_budget_v0.md](recurrent_support_perturbation_budget_v0.md)
- [joint_recurrent_support_v0.md](joint_recurrent_support_v0.md)
- [parameterized_recurrent_support_v0.md](parameterized_recurrent_support_v0.md)
- [recurrent_support_extension_v0.md](recurrent_support_extension_v0.md)
- [recurrent_support_lineage_v0.md](recurrent_support_lineage_v0.md)
- [recurrent_support_successor_distinction_v0.md](recurrent_support_successor_distinction_v0.md)
