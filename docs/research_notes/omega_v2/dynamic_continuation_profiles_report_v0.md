# Dynamic Continuation Profiles Report v0

Status: retained post-freeze finite pilot

Scope: finite action-labelled transition systems, duplicate-resistant bounded
behavior types, alternating-simulation capability profiles, transition
deformation, and a bridge into the retained lushness/diversity instrument

Claim boundary: not value, valuerhood, standing, agency, autonomy, patienthood,
universal lushness, thermodynamic law, moral licensing, paperclipper defeat, or
Omega validation

## Protocol

Preregistered protocol:

```text
docs/research_notes/omega_v2/dynamic_continuation_profiles_protocol_v0.md
```

Protocol commit:

```text
3727340 Preregister dynamic continuation profiles pilot
```

The protocol was committed before the adapter, fixtures, tests, validation
runner, or retained output existed.

## Formal Object

For a finite control system:

```text
S = (X, A, Step, Atom)
```

the retained bounded behavior type is:

```text
B_0(x) = Atom(x)

Outcome_h(x, a) =
  { B_h(y) | Step(x, a, y) }

B_(h+1)(x) =
  (Atom(x),
   { Outcome_h(x, a) | a is enabled at x })
```

The inner set retains environment outcomes under one action. The outer set
retains controller alternatives. Both levels are idempotent.

The bounded capability order is:

```text
x <=_h z
```

when `z` can match every controller option at `x`, with its environment
outcomes matched by outcomes of the original option through horizon `h`.

Relative to a finite comparison basis `U`, the derived profile is:

```text
Cap_h(x ; U) =
  { fingerprint(B_h(u)) | u in U and u <=_h x }
```

Thus the profile is a represented behavioral down-set, not a bag of paths or a
hand-authored list of semantic properties.

## Validation

Focused test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_finite_relational_dynamic_continuation_profiles.py -q
```

Result:

```text
20 passed
```

Full Python regression:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Result:

```text
453 passed
```

Pytest emitted one environment warning because the sandbox cannot create
`.pytest_cache`. No test failed.

Focused lint:

```powershell
.\.venv\Scripts\python.exe -m ruff check `
  omega\adapters\finite_relational\dynamic_continuation_profiles.py `
  omega\validation\finite_relational_dynamic_continuation_profiles.py `
  tests\test_finite_relational_dynamic_continuation_profiles.py
```

Result:

```text
all checks passed
```

Retained run:

```powershell
.\.venv\Scripts\python.exe -m `
  omega.validation.finite_relational_dynamic_continuation_profiles `
  --out-root `
  docs\research_notes\validation_results\dynamic_continuation_profiles_v0
```

Retained output:

```text
docs/research_notes/validation_results/dynamic_continuation_profiles_v0/20260731_021757/
```

Files:

```text
summary.json
case_results.csv
signatures.csv
deformations.csv
report.md
```

## Verdict

```text
retained
```

All preregistered finite cases and negative controls passed. The adaptive case
strictly separated rather than using the protocol's permitted non-separating
exit.

## Results

### Duplicate outcomes and actions

The duplicate-outcome fixture changes:

```text
edge count:
  2 -> 4
```

while preserving:

```text
root behavior type;
derived capability profile.
```

Adding a second effect-equivalent controller action changes the raw action
count while preserving the root behavior type.

The instrument therefore does not equate additional state, edge, or action
tokens with additional continuation capability.

### Novel branch

A new controller option reaching a persistent state with a new positive atom
gives:

```text
state order:
  extension strictly refines base

profile order:
  extension strictly refines base

represented strict surplus:
  one dynamic capability fingerprint
```

The surplus is generated from dynamics relative to the declared atom grammar,
horizon, and comparison basis. It is not a hand-authored `translation` or
`correction` string.

### Delayed divergence

The continuing and terminating roots have equal behavior types at:

```text
horizon 0;
horizon 1.
```

They first separate at:

```text
horizon 2.
```

This retains a computable finite separation-depth coordinate. It says when a
declared bounded observation of dynamics first distinguishes two roots. It is
not yet a phase transition, personhood threshold, or process-identity measure.

### Controller choice versus environment risk

The choice and risk systems expose the same flattened successor types:

```text
{good, bad}
```

but differ structurally:

```text
choice:
  safe -> {good}
  hazard -> {bad}

risk:
  gamble -> {good, bad}
```

The nested behavior type distinguishes them, and choice strictly refines risk.

This is the load-bearing quantifier result:

```text
exists controller action, then forall its possible outcomes
```

cannot be replaced by a flattened union of reachable outcomes.

### Dynamic deformation

One finite fixture retains all four profile-change verdicts along actual
transitions under one basis and horizon:

```text
EXPANSION
CONTRACTION
EQUIVALENT
MIXED
```

This supplies a non-scalar finite dynamics vocabulary:

```text
oriented transition
-> change in represented continuation-capability profile
```

No claim is made that physical thermodynamics generally causes profile
expansion, or that expansion is morally preferred.

### Presentation control

A bijective relabeling of state and action identifiers preserves:

```text
behavior type;
behavior fingerprint;
derived profile.
```

An abstraction that maps `good` and `bad` concrete states to one `good`
abstract state has one atom-respect failure and changes the hidden state's
behavior type. It is rejected rather than treated as an invariant lens.

### Switching versus adaptive ambiguity

The retained learnable-ambiguity system was translated in two ways:

```text
switching:
  each action is evaluated against the merged outcomes of every unresolved
  model.

adaptive:
  the same dynamics are evaluated over the sound information-state lift.
```

Both use only the physical-state atoms:

```text
safe;
requirement.
```

Information-state/model-set labels are excluded from the atom grammar.

The starts compare as:

```text
horizon 0:
  equivalent

horizon 1:
  equivalent

horizon 2:
  adaptive strictly refines switching

horizons 3 and 4:
  adaptive strictly refines switching
```

Sound-update truth-preservation failures:

```text
0
```

This gives the previously retained B2/B2.1 distinction a finite behavioral
signature: safe learning creates a controller option structure that the
switching system lacks, and the difference becomes visible at depth two.

### Lushness-profile bridge

Dynamic capability fingerprints were supplied directly as `Trajectory`
attributes to the retained jointly realizable-family instrument.

The bridge retains:

```text
duplicate dynamic trajectory:
  no family-profile increase

novel dynamic trajectory:
  strict family-profile increase
```

This partially pays the predecessor pilot's exogenous-attribute debt. It does
not eliminate declaration:

```text
the positive atom grammar remains declared;
the process/root selection remains declared;
the finite comparison basis remains declared;
the horizon remains declared.
```

## Negative Controls

All controls passed:

```text
state relabeling invariant;
action relabeling invariant;
duplicate branch idempotent;
effect-equivalent action idempotent;
atom-respect failure visible;
flattened successor equality does not imply control-type equality;
profile fingerprints exclude state and action tokens;
raw edge/action counts are not the primary order.
```

## What Landed

The pilot retains:

```text
exact finite control dynamics
-> bounded duplicate-resistant behavior types
-> bounded alternating-simulation preorder
-> finite represented capability down-sets
-> expansion/contraction/equivalence/mixed transition verdicts
-> dynamic attributes for the jointly realizable-family profile
```

The mathematical skeleton is classical finite behavior/simulation material.
The project-specific delta is the disciplined bridge from that skeleton into
certified continuation accounting while preserving action/outcome quantifiers
and presentation liabilities.

## Remaining Debt

The next dynamics layers remain open:

```text
process lift:
  derive behavior on reidentifiable trajectory-pattern states rather than
  hand-selected world-state roots.

joint product dynamics:
  derive higher-order capability surplus from a coupled realization rather than
  declaring joint attributes.

stabilization:
  relate bounded profiles across horizons and characterize the stabilized finite
  preorder.

presentation theorem:
  prove profile transport through the retained lens contract rather than only
  testing positive and negative fixtures.

infinite or atemporal limit:
  connect coherent bounded approximations to a full unfolding object.

normative bridge:
  establish standing and licensing assumptions, if possible, without treating
  capability expansion as value by definition.
```

The most direct successor is the **process lift**. A candidate pattern tracker
can be composed with exact world dynamics, after which persistence,
reconstruction, correction, and hidden divergence can be tested as properties
of the lifted dynamics. That still would not prove valuerhood, but it would
move the comparison root from an arbitrary world state toward the trajectory
object the rebuilt theory intends.

## Public Compression

A finite pilot derived duplicate-resistant continuation-capability profiles
from action-labelled dynamics. It distinguishes controller choice from
environment risk, classifies transitions without scalarization, and detects the
finite behavioral advantage of safe learning over switching ambiguity. The
result is a dynamics instrument, not a derivation of value or agency.
