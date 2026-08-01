# Directional Asymmetry and Operational Capability Protocol v0

Status: preregistered finite countermodel and matched-control protocol

Date: 2026-08-01

Parent result:
[Finite Controlled Markov Abstraction Report v0](finite_controlled_markov_abstraction_report_v0.md)

## Question

Does statistical directional asymmetry, by itself, determine the operational
features currently proposed as ingredients of an Alpha-capable process?

The sprint separates three hypotheses:

```text
sufficiency:
  nonzero finite path-reversal asymmetry entails operational selection;

necessity:
  operational selection or functional deformation requires a directionally
  biased substrate;

unqualified enabling:
  adding an independent directional bias increases the retained operational
  capability profile.
```

These hypotheses must receive separate verdicts. A result against one is not a
result against the others.

## Claim Boundary

The experiment audits finite operational features only. It does not define or
detect:

```text
Alpha;
valuerhood;
agency;
consciousness;
will;
standing;
value;
moral license;
Omega compatibility;
or a physical arrow of time.
```

In particular, `operational capability` below is a feature vector, not a
Boolean classification of a process.

## Supplied Inputs

Each case supplies:

```text
a finite exact controlled Markov system;
an explicit action-reversal involution;
an exact initial law;
a finite horizon;
a finite-state controller where applicable;
and declared finite events used to measure functional performance.
```

The transition dynamics are model inputs. This sprint does not derive them.

## Derived Quantities

### Directional statistic

For an explicitly paired forward and reverse experiment, compute:

```text
finite path law P_H;
reverse law expressed on forward path coordinates P_H^R;
TV(P_H, P_H^R);
and support equality.
```

Nonzero total variation is the exact finite directional detector used in this
protocol. KL may be reported as a diagnostic but is not an acceptance
criterion.

### Operational feature profile

For a finite-state controller, derive:

```text
causal action influence:
  a selected action has a different successor law from an available
  alternative at a reachable closed-loop state;

record-sensitive selection:
  the same world state is reachable with different controller records and the
  selected action changes with the record;

closed-loop persistence:
  the reachable closed-loop support graph contains a cycle;

policy deformation:
  a record-sensitive controller and a matched record-ignoring controller
  induce different finite closed-loop path laws;

branch fidelity:
  the probability that the controller returns to the branch recorded before a
  shared decision state.
```

All features are relative to the supplied model, controller, initial support,
event, and horizon.

## Fixture A: Passive Biased Cycle

Use the retained reciprocal-support biased three-cycle with one available
action and a singleton controller.

Required:

```text
finite path-reversal total variation is positive;
the closed loop persists;
causal action influence is false;
record-sensitive selection is false.
```

This is the sufficiency control. If retained, it refutes the claim that
directional asymmetry alone entails operational selection.

## Fixture B: Reversal-Paired Action Census

Enumerate all three-state deterministic permutation dynamics of the form:

```text
forward action: p;
reverse action: p^-1;
```

for every permutation `p`, and enumerate every stationary deterministic policy
over the two actions.

For each permutation, verify that the all-forward and all-reverse path
experiments agree after explicit path reversal under a uniform initial law.

Classify each mixed policy by:

```text
whether both actions are used;
whether the actions have different effects;
whether the induced closed-loop state map is injective;
and the size of its image.
```

Required:

```text
the generator is exhaustive and deterministic;
every primitive action is a bijection;
every forward/reverse constant-policy pair has zero directional distance after
explicit reversal;
and at least one mixed policy induces a noninjective closed-loop map.
```

This is a finite necessity countermodel. It can show that selection among
reversal-paired primitive transformations can generate functional
noninvertibility. It does not establish thermodynamic realizability of the
controller or erase the cost of its implementation.

## Fixture C: Matched Record-Sensitive Pair

Build a finite world with:

```text
two source branches;
one shared decision state;
two self-inverse branch actions;
a controller record that remembers the source branch;
and a matched controller with the same record update that ignores the record
when acting at the decision state.
```

Take the product with a three-state phase process.

Balanced case:

```text
phase moves in either direction with probability 1/2;
path-reversal total variation is zero under the declared reference experiment.
```

Biased case:

```text
phase moves clockwise with probability 3/4 and counterclockwise with
probability 1/4;
path-reversal total variation is positive.
```

The phase coordinate is independent of the controller-facing world coordinate.
The two cases must otherwise have:

```text
the same states;
the same actions;
the same action availability;
the same controller;
the same observations and record updates;
the same initial world/record law;
and the same branch-fidelity event.
```

Required:

```text
the record-sensitive controller has causal influence;
record-sensitive selection is present;
the reachable closed loop persists;
its branch fidelity exceeds the matched record-ignoring controller;
and adding the independent directional bias leaves the operational feature
profile and branch-fidelity advantage unchanged.
```

This is a matched control against an unqualified enabling claim. It does not
test directional resources coupled to controller operation.

## Verdicts

Report:

```text
sufficiency:
  retained or rejected;

necessity:
  retained or rejected for the declared operational features;

independent enabling:
  retained or rejected in the matched product control;

coupled enabling:
  unresolved in v0.
```

The overall result must not compress these verdicts into `Alpha present` or
`Alpha absent`.

## Machine-Readable Outputs

Add:

```text
summary.json;
case_results.csv;
passive_asymmetry.csv;
reversible_action_census.csv;
record_selector_comparison.csv;
report.md.
```

The generated census must include a stable manifest digest.

## Acceptance Criteria

The sprint is retained only if:

1. The finite-state controller and closed-loop compiler are reusable v2
   machinery.
2. The clean implementation imports no historical `omega` package.
3. Directionality is computed from an explicit reverse experiment.
4. The passive biased control separates directional asymmetry from operational
   selection.
5. The reversal-paired census is exhaustive for its declared finite class.
6. A generated policy witness produces functional noninvertibility from
   bijective reversal-paired primitive actions.
7. The balanced and biased record-controller cases differ only in the phase
   probabilities.
8. The matched pair reports unchanged operational features rather than
   interpreting a planted independent bias as useful.
9. Focused and full Python validation pass.
10. No result is described as a valuer, moral, or Omega verdict.

## Kill Conditions

Stop for audit rather than retain the result if:

```text
the passive control receives a synthetic controller feature from a label;
the forward/reverse census comparison omits the action involution;
an allegedly reversible primitive action is not bijective;
the generated census is sampled rather than exhaustive;
the balanced and biased matched cases change controller structure, action
availability, or the branch-fidelity event;
directionality is inferred from graph arrows without comparing path laws;
functional noninvertibility is reported as microscopic thermodynamic
irreversibility;
an independent-product null is reported as disproving every possible coupled
enabling mechanism;
or the experiment emits an Alpha or valuerhood classification.
```

## Expected Repricing

If all required controls retain, the strongest licensed conclusion is:

> Finite statistical directional asymmetry is neither sufficient for the
> declared operational selection features nor necessary for finite feedback to
> induce functional noninvertibility. Adding an independent directional
> coordinate does not improve those features. Any positive enabling claim must
> therefore specify the coupling through which the directional resource enters
> controller operation.

This is a boundary result, not a completed account of Alpha-capable dynamics.

## Post-Run Scope Clarification

Added after the preregistered run during implementation review:

The necessity hypothesis in this protocol concerns a **pre-existing
directionally biased substrate**. It does not ask whether the realized
controller/world closed loop itself acquires directional asymmetry. The latter
question remains separate and unresolved. The retained report and canonical
validation run use hypothesis labels that preserve this distinction.
