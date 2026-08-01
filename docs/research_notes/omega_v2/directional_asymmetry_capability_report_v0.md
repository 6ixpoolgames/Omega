# Directional Asymmetry and Operational Capability Report v0

Status: retained finite countermodels and matched-control result

Date: 2026-08-01

Protocol:
[Directional Asymmetry and Operational Capability Protocol v0](directional_asymmetry_capability_protocol_v0.md)

Protocol checkpoint:
`ff3850a` (`Preregister directional capability experiment`)

Retained run:
[20260801_111713](../validation_results/directional_asymmetry_capability_v0/20260801_111713/)

Provisional run:
[20260801_111132](../validation_results/directional_asymmetry_capability_v0/20260801_111132/)
triggered a scope-label correction during diff review. Its numerical results
are retained as audit history, but its shorter verdict failed to distinguish
pre-existing substrate bias from process-level asymmetry. The later run is
canonical.

## Result

The experiment separates three claims that had previously traveled together:

```text
sufficiency:
  rejected;

pre-existing substrate bias as a necessity for the declared operational
features:
  rejected;

unqualified enabling by an independent directional coordinate:
  rejected in the matched product control;

process-level asymmetry as a necessity:
  unresolved;

enabling through a declared physical coupling:
  unresolved.
```

No kill condition fired.

The result does not classify any system as Alpha-capable or as a valuer. It
shows that passive path-reversal asymmetry is not equivalent to the retained
operational controller features, and that those features do not require a
pre-biased primitive action family.

## Clean Machinery

The sprint adds a reusable finite-state controller interface and exact
closed-loop compiler:

```text
FiniteStateController;
ClosedLoopState;
compile_closed_loop;
closed_loop_initial_distribution;
reachable_closed_loop_states;
audit_operational_features.
```

The controller consumes a current world observation and current memory state,
selects one supplied world action, and updates its memory. Compilation produces
an exact one-action controlled Markov system over world-state/controller-memory
pairs.

The feature audit derives:

```text
reachable closed-loop states and records;
selected action support;
causal action influence;
record-sensitive selection;
and closed-loop persistence.
```

These are operational features. They are not a renamed valuer predicate.

## Passive Asymmetry Control

The reciprocal-support biased three-cycle retains:

```text
finite path horizon:
  3

path-reversal total variation:
  11/16

path support equal under reversal:
  true

closed-loop persistence:
  true

causal action influence:
  false

record-sensitive selection:
  false
```

There is one available action and one controller-memory state. The directional
signal therefore does not manufacture action choice or endogenous record use.

This refutes the universal sufficiency claim:

> Nonzero statistical directional asymmetry alone entails the declared
> operational selection features.

It does not show that directional resources cannot contribute when coupled to
a controller.

## Reversal-Paired Action Census

The generated finite class contains:

```text
states:
  3

permutations:
  6

stationary deterministic policies:
  6 * 2^3 = 48

manifest digest:
  f112cb529f12d2c5386e514120c6d3d72a8ba1a36dbba835a7fe9577a259a287
```

For each permutation `p`, the primitive actions are:

```text
forward:
  p

reverse:
  p^-1
```

Every primitive action is bijective. Every action pair satisfies the exact
reversal contract. Under a uniform initial law, every all-forward path law
agrees exactly with the explicitly reversed all-reverse law.

Across the 48 policies, 12 mixed policies induce a noninjective closed-loop
state map.

The first retained witness is:

```text
permutation:
  0 -> 1, 1 -> 2, 2 -> 0

policy:
  forward, forward, reverse

closed-loop targets:
  1, 2, 1

closed-loop image size:
  2
```

Each available transformation is reversible, but state-dependent selection
among them produces a many-to-one feedback map.

This rejects the universal precondition claim for the declared finite
operational notion:

> Functional noninvertibility under feedback requires a pre-biased primitive
> action family.

It does not establish microscopic thermodynamic irreversibility. A physical
adapter must account for controller state, memory writing, work, and discarded
degrees of freedom. The finite controlled model exposes the feedback
composition; it does not supply free physical erasure.

It also does not reject a possible necessity of asymmetry in the realized
closed-loop process. In the retained record-writing controller below, the
balanced substrate reference is directionally null while the finite
closed-loop path law is support-asymmetric. The controller has generated a new
effective directional structure at the modeled level.

## Matched Record-Sensitive Pair

The matched world contains two source branches, one shared decision state, and
two self-inverse branch actions. The controller records the source branch and
uses that record at the decision state.

A matched control has the same:

```text
state space;
action set;
transition support;
controller memory;
observation map;
record update;
initial world/record law;
capability horizon;
and branch-fidelity event.
```

It ignores the record only when selecting the return action.

The retained capability result in both the balanced and biased products is:

```text
record-sensitive selector branch fidelity:
  1

record-ignoring control branch fidelity:
  1/2

advantage:
  1/2

path-law deformation between the controllers:
  1/2

record-sensitive controller closed-loop reversal TV:
  1

record-sensitive controller closed-loop reverse support equal:
  false

causal action influence:
  true

record-sensitive selection:
  true

closed-loop persistence:
  true
```

The independent phase coordinate is then changed:

```text
balanced phase:
  clockwise 1/2, counterclockwise 1/2
  path-reversal TV = 0

biased phase:
  clockwise 3/4, counterclockwise 1/4
  path-reversal TV = 11/16
```

The operational feature signature, branch fidelity, and policy-deformation
distance remain unchanged.

The controller's closed-loop reversal TV is `1` in both products. This is not
reported as entropy production: the operational initial law is nonstationary,
and the controller-memory implementation is not a thermodynamically closed
model. It records that process-level asymmetry was not removed merely by making
the independent substrate phase balanced.

This rejects an unqualified enabling claim:

> Adding any directional asymmetry increases operational capability.

The control is intentionally separable. It leaves open whether a directional
resource coupled to sensing, memory, action, repair, or work budgets changes a
controller's attainable continuation profile.

## Dependency Surface

The retained quantities depend on:

```text
model:
  finite states;
  finite actions;
  exact transition kernel;

experiment:
  initial law;
  controller;
  finite horizon;

measurement:
  action involution;
  path-reversal operation;
  branch-fidelity event;

interpretation:
  operational feature definitions.
```

No result is declaration-free. The countermodels are uniform consequences of
their explicit finite inputs.

## Repricing

Statistical directional asymmetry should not be installed as a Boolean
criterion for Alpha-capability.

The retained evidence instead supports:

```text
directional asymmetry:
  an adapter-relative dynamical coordinate or potential resource;

pre-existing directional bias:
  not required for finite feedback selection to induce an effective
  noninvertible closed-loop map;

finite controller features:
  properties of closed-loop selection, memory, and consequence;

functional noninvertibility:
  something feedback can induce even when each supplied primitive action is
  bijective;

positive enabling:
  a future coupling claim that must name how the directional resource enters
  sensing, memory, work, recovery, or attainable control.
```

Whether every adequate process-level realization of those features carries
some directional asymmetry remains unresolved.

The next positive hypothesis must therefore be conditional. A suitable shape
is:

> Within a declared resource-coupled adapter, nonzero directional current
> expands or stabilizes a specified controller capability relative to an
> energy-, support-, and interface-matched null.

That hypothesis is not tested here.

## Validation

Focused command:

```text
python -m pytest tests/test_omega_v2_directional_asymmetry_capability.py -q
```

Focused result:

```text
10 passed
```

Retained-run command:

```text
python -m omega_v2.validation.directional_asymmetry_capability_v0 \
  --out-root docs/research_notes/validation_results/directional_asymmetry_capability_v0 \
  --horizon 3
```

Machine-readable outputs:

```text
summary.json;
case_results.csv;
passive_asymmetry.csv;
reversible_action_census.csv;
record_selector_comparison.csv;
report.md.
```

Full validation:

```text
Python:
  529 passed

OmegaV2 Lean:
  946 jobs passed

Ruff:
  all checks passed
```

## Claim Boundary

This sprint establishes finite exact countermodels and matched controls for
specified operational features.

It does not establish:

```text
Alpha;
valuerhood;
agency;
consciousness;
standing;
value;
moral license;
Omega compatibility;
thermodynamic realizability of the finite controllers;
or a physical arrow of time.
```
