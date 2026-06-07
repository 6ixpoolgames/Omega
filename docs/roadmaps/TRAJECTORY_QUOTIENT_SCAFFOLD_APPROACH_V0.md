# Trajectory Quotient Scaffold Approach v0

Status: working note for `codex-trajectory-quotient-scaffold`

Scope: near-term formal approach before implementing the next Lean layer

Claim boundary: this note does not define valuerhood, validate Omega, or make
empirical claims. It defines the next formal object and the safeguards around
boundary recovery.

## Current Objective

The next formal objective is to build the smallest layer above Alpha that can
talk about non-exact process persistence without assuming self, identity, or
valuerhood.

The target is:

```text
trajectory windows
-> declared signatures / quotients
-> recoverable pattern continuity
-> nontrivial continuation
-> joint persistence / compatibility failure examples
```

This is a scaffold for future process-bundle and valuer-trajectory work. It is
not a claim that any current object is a valuer.

## First-Principles Derivation

The layer must arise from the current primitive stack:

```text
Alpha primitives:
  relation
  distinction
  asymmetry
```

Minimal derivation:

```text
relation -> trajectories
  A trajectory is an iterated relation through time.

distinction -> signatures / quotients
  A boundary is a declared distinction over states or trajectory windows.

asymmetry -> recovery transport
  A later window may carry enough structure to recover an earlier signature.
```

The central rule is:

```text
identity by declared recoverable quotient,
not quotient by assumed identity.
```

## Boundary Position

The boundary is not primitive and not self-evident.

We do not say:

```text
this is the same self
```

We say:

```text
under this declared signature / quotient / recovery rule,
this later trajectory window recovers the earlier process-relevant pattern.
```

A process-bundle is therefore a modeling object:

```text
a family of trajectory windows linked by declared recoverability
```

not an ontological self.

## Borrowed Mathematical Machinery

The project should borrow established tools rather than invent a custom identity
theory.

Use the smallest layer first:

```text
observation maps / signatures
equivalence relations / quotients
tolerance relations
pseudometric thresholds
observational equivalence
simulation / bisimulation
approximate bisimulation
decoder / statistical decision layers
```

Recommended order:

```text
Pass 1:
  declared signature map + recovery relation

Pass 2:
  threshold / pseudometric recovery

Pass 3:
  simulation or approximate bisimulation for dynamic pattern preservation

Pass 4:
  statistical decoder recovery for empirical high-dimensional signatures
```

The first Lean pass should not require heavy probability, topology, or measure
theory.

## Minimal Formal Object

The smallest object is:

```text
State
Rel : State -> State -> Prop
Trajectory
Window
Signature : Window -> Label
Recovers : Label -> Label -> Prop
```

Then:

```text
RecoveredWindow(w1, w2) :=
  Recovers(Signature(w1), Signature(w2))
```

Exact equality is only a special case:

```text
WindowEquality(w1, w2) -> RecoveredWindow(w1, w2)
```

The converse should fail:

```text
RecoveredWindow(w1, w2) does not imply WindowEquality(w1, w2)
```

This gives non-exact pattern recovery without importing self-identity.

## 3P Anti-Self-Validation Rule

A declared quotient can self-validate if chosen because it makes persistence
true. The 3P rule is:

```text
Principled:
  every quotient comes from a named substrate role or relational test family

Parsimonious:
  the quotient uses the fewest features needed for that role

Predictive / revelatory:
  the quotient must make predictions, fail in controls, and separate from
  post-hoc optimized quotients
```

Every quotient should eventually have a manifest:

```text
quotient_id
source_role
feature_map
window_rule
label_set
derivation_rule
predeclared_before_scoring
allowed_information
forbidden_information
expected_failures
fakeout_controls
```

## Quotient Sources

Alpha alone does not derive one true quotient. It constrains admissible quotient
sources.

Initial quotient families:

```text
observational quotient:
  same declared observation signature

future-predictive quotient:
  same reachable continuation profile up to horizon H

action / viability quotient:
  same viable action-continuation profile
```

Compare each against:

```text
identity quotient
constant quotient
too-loose quotient
too-strict quotient
random / shuffled quotient
optimized post-hoc quotient
```

The truth-bearing object is the gap pattern across this quotient panel, not a
single success row.

## Lessons From COM / Multifield Work

The early COM/fiber and multifield branches are useful as warnings.

Reusable lessons:

```text
quotients worked better than exact state identity;
loose continuity overcalled persistence;
<= H reachability produced easy persistence fakeouts;
exact-H and horizon-filtration diagnostics were necessary;
stasis and clock-like persistence needed flatline / nontriviality flags;
cheap bypass edges defeated intended asymmetry;
pairwise persistence did not imply joint persistence;
cap censoring could masquerade as compatibility;
random controls could mimic intended degradation;
hand-designed quotients were useful but dangerous.
```

Therefore the new scaffold should include:

```text
exact-H or explicit time-step recovery
nontrivial continuation
loss and irreversible-loss conditions
joint persistence checks
fakeout controls
declared-vs-existence-vs-optimized quotient separation
```

## First Lean Acceptance Criteria

A useful first Lean pass should define and check:

```text
finite trajectories from relation;
trajectory windows;
signature maps over windows;
declared recovery relation over signature labels;
RecoveredWindow;
BundlePersists over a finite list of windows;
exact window equality implies recovery under identity signature;
signature recovery does not imply exact state/window equality;
two signatures can disagree about recovery;
loose signature can recover everything;
strict signature can fail where coarse signature succeeds;
stasis-like signature persistence does not imply nontrivial continuation;
singleton persistence does not imply joint persistence.
```

Blocked in the first pass:

```text
valuer detection
value detection
identity detection
agency claims
Omega validation
empirical trajectory atlas
probabilistic/statistical high-dimensional recovery
```

## Intended Output

The first deliverable should be a small Lean scaffold, likely:

```text
formal/lean/Omega/Trajectory/Quotient.lean
```

or, if namespacing requires less disruption:

```text
formal/lean/OmegaProper/Trajectory/Quotient.lean
```

It should be wired into the active umbrella only after it compiles without
`sorry`, `admit`, or new axioms.

## Strategic Read

This is the minimal path from primitive roles to recoverable process-boundary
talk:

```text
relation supplies paths;
distinction supplies declared quotient signatures;
asymmetry supplies directional recovery;
trajectory quotient recovery supplies non-exact process continuity;
viability and compatibility can then be added without assuming selfhood.
```

If this layer fails or becomes too permissive, that is useful information. It
means the project should update the objective before building a trajectory atlas.
