# Dynamic Continuation Profiles Protocol v0

Status: preregistration / post-freeze quarantined finite pilot

Scope: finite action-labelled transition systems, bounded behavioral types,
alternating-simulation capability profiles, transition deformation, and a
bridge into the retained lushness/diversity profile instrument

Provenance: successor experiment to
`docs/research_notes/omega_v2/lushness_diversity_report_v0.md`; the frozen Omega
checkpoint `cc4c89c` and its retained verdicts are unchanged

Claim boundary: not value, valuerhood, standing, agency, autonomy, patienthood,
universal lushness, thermodynamic law, moral licensing, paperclipper defeat, or
Omega validation

## Purpose

The predecessor pilot used declared strings such as `persistence`,
`correction`, and `translation` as continuation attributes. This pilot tests
whether a nontrivial finite attribute basis can instead be derived from exact
transition dynamics.

The target is deliberately classical:

```text
finite behavior unfolding
+ duplicate-insensitive powerset structure
+ alternating simulation
+ a finite declared comparison basis
```

The project-specific role is to connect this behavioral basis to
duplicate-resistant continuation profiles without treating the resulting
profiles as value.

## Exact Finite Object

Use a finite control system:

```text
S = (X, A, Step, Atom)

Step(x, a, y):
  action a can produce successor y from x

Atom(x):
  the admitted positive observation atoms true at x
```

Only enabled actions occur in the behavioral object. An action is enabled when
it has at least one successor.

For horizon zero:

```text
B_0(x) = Atom(x)
```

For the successor step:

```text
Outcome_h(x, a) =
  { B_h(y) | Step(x, a, y) }

B_(h+1)(x) =
  (Atom(x),
   { Outcome_h(x, a) | a is enabled at x })
```

Both braces denote sets.

Consequences fixed before the run:

```text
duplicate bisimilar outcomes under one action do not multiply the type;
effect-equivalent duplicate actions do not multiply the type;
controller alternatives remain outside environment outcomes;
state and action identifiers do not enter the type;
positive atoms do enter the type and remain declared interface content.
```

Action identity is used while assembling each outcome set, including the
same-action merge across unresolved models. The resulting v0 type quotients
effect-equivalent actions. Typed action meanings or action costs are outside
scope and would require certified action atoms in a later version.

## Capability Refinement

Write:

```text
x <=_h z
```

when `z` can match every controller option available at `x` through horizon
`h`, while every outcome of the matching option at `z` is matched by an
outcome of the original option at `x`.

The bounded recursion is:

```text
x <=_0 z
  iff Atom(x) is a subset of Atom(z)

x <=_(h+1) z
  iff Atom(x) is a subset of Atom(z)
  and for every enabled action at x
      there exists an enabled action at z
      such that for every z-successor under that action
          there exists an x-successor under the original action
          with x' <=_h z'.
```

This is the v0 alternating-simulation direction:

```text
x <=_h z means z weakly refines x.
```

It is not ordinary path inclusion and it does not allow a different controller
action to be selected after the environment outcome is known.

## Derived Capability Profile

For an explicit finite comparison basis `U`, define:

```text
Cap_h(x ; U) =
  { fingerprint(B_h(u)) | u in U and u <=_h x }
```

The fingerprint is computed from the structural behavioral type, not from a
state identifier.

This profile is:

```text
finite;
duplicate-resistant;
relative to a declared horizon, positive atom grammar, and comparison basis;
ordered by ordinary profile inclusion.
```

The comparison basis is an instrumentation boundary. This pilot does not claim
that one finite basis exhausts every possible continuation capability.

For a jointly realizable trajectory family, the v0 marginal bridge takes the
union of its member capability profiles. Higher-order joint capabilities
derived from coupled product dynamics are left for a successor experiment.

## Dynamic Deformation

For an oriented transition from `x` to `y`, compare `Cap_h(x;U)` and
`Cap_h(y;U)`:

```text
EXPANSION:
  the successor profile strictly includes the predecessor profile

CONTRACTION:
  the predecessor profile strictly includes the successor profile

EQUIVALENT:
  the profiles are equal

MIXED:
  the profiles are incomparable
```

This is a non-scalar finite deformation classification. It does not identify
the physical thermodynamic arrow and does not say which direction is valuable.

## Preregistered Cases

### D1 — Duplicate outcome invariance

Compare one successor branch with two state-distinct but behaviorally
equivalent successor branches under the same action.

Required:

```text
raw edge count changes;
bounded behavioral type does not;
derived capability profile does not.
```

### D2 — Effect-equivalent action invariance

Add a second action with the same bounded outcome type.

Required:

```text
raw action count changes;
bounded behavioral type does not.
```

### D3 — Novel branch strictness

Add a controller option reaching a genuinely new persistent labeled behavior.

Required:

```text
the extension strictly refines the base at the declared horizon;
the derived profile strictly expands.
```

### D4 — Delayed divergence

Construct two roots with equal short-horizon types that diverge later.

Required:

```text
the first separating horizon is reported exactly;
no earlier horizon is reported as separating.
```

### D5 — Action/outcome quantifier control

Compare:

```text
choice:
  one action guarantees good;
  another action reaches bad.

risk:
  one action may reach good or bad.
```

Required:

```text
flattened successor unions are equal;
the nested behavioral types differ;
choice strictly refines risk.
```

This case fails if controller choice is flattened into environment
nondeterminism.

### D6 — Transition deformation

Retain finite edges witnessing all four verdicts:

```text
EXPANSION
CONTRACTION
EQUIVALENT
MIXED
```

The verdicts must be obtained from the same declared basis and horizon.

### D7 — Presentation control

Retain:

```text
a structural relabeling that preserves behavioral types and profiles;
an unsound abstraction that merges a positive-atom distinction and changes the
  behavioral type.
```

The negative case is not licensed as a lens.

### D8 — Switching/adaptive control

Reuse the retained learnable-ambiguity geometry.

Required:

```text
switching dynamics are built with one action evaluated across every unresolved
  model;
adaptive dynamics are built over the sound information-state lift;
the comparison uses the same positive physical-state atoms;
the adaptive start strictly refines the switching start at some retained finite
  horizon, or the case is reported as non-separating rather than forced.
```

## Negative Controls

The retained run must also check:

```text
state relabeling invariance;
action relabeling invariance;
duplicate branch idempotence;
effect-equivalent action idempotence;
atom-respect failure remains visible;
flat successor equality does not imply control-type equality;
profile identifiers contain no state or action tokens;
ordinary path/edge counts are not promoted as the primary order.
```

## Verdict Table

```text
retained:
  D1-D7 pass, the adaptive case is reported honestly, and every negative
  control passes.

reduces:
  the derived profile adds no distinction beyond raw counts in the retained
  fixtures.

confounded:
  identifiers, duplicate tokens, or flattened action/outcome quantifiers drive
  a verdict.

ill-posed:
  the finite behavioral recursion or comparison direction cannot be specified
  consistently.
```

The adaptive case may return `non-separating-at-retained-horizon` without
invalidating D1-D7. It may not be rewritten after the run to force separation.

## Kill Conditions

Stop and report rather than promote the instrument if:

```text
a duplicate bisimilar branch changes the behavioral type;
state or action identifiers change a verdict under bijective relabeling;
the robust comparison chooses actions after observing outcomes;
positive atom inclusion is silently replaced by equality or omitted;
an unsound abstraction is reported as invariant;
the bridge treats a behavioral fingerprint as standing or value;
the implementation requires rewriting the frozen corridor stack.
```

## Expected Artifacts

```text
omega/adapters/finite_relational/dynamic_continuation_profiles.py
omega/validation/finite_relational_dynamic_continuation_profiles.py
tests/test_finite_relational_dynamic_continuation_profiles.py
docs/research_notes/omega_v2/dynamic_continuation_profiles_report_v0.md
docs/research_notes/validation_results/dynamic_continuation_profiles_v0/<run>/
```

## Remaining Debt Even on Success

Success would not derive:

```text
the correct process boundary;
operational identity or reidentification;
which positive atoms identify correction, ancestry, or standing;
valuerhood;
joint capability emergence from coupled product dynamics;
an infinite-horizon or atemporal limit;
why a controller must prefer profile expansion;
value or moral license.
```

The strongest licensed result would be:

> A finite, duplicate-resistant continuation-capability profile can be derived
> from action-labelled dynamics relative to an explicit horizon, positive atom
> grammar, and comparison basis.
