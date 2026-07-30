# Canonical Process Monitors Report v0

Status: retained post-freeze finite process-lift pilot

Scope: certified finite edge observations, deterministic Moore/safety
automata, canonical residual monitors, passive history lifts, bounded
process-relative profiles, and property-relative admissible actions

Claim boundary: not identity, selfhood, consciousness, will, agency,
valuerhood, standing, patienthood, intrinsic continuation relevance, moral
license, or Omega validation

## Protocol

Preregistered protocol:

```text
docs/research_notes/omega_v2/canonical_process_monitors_protocol_v0.md
```

Protocol commit:

```text
1ba3c28 Preregister behavioral logic and process monitors
```

The protocol was committed before the adapter, fixtures, tests, validation
runner, or retained output existed.

## Formal Objects

The certified finite observation interface is:

```text
observe(x, a, y) =
  (Atom(x), ActionClass(a), Atom(y)).
```

Raw state identifiers are excluded.

A property is presented as a complete deterministic Moore automaton:

```text
P = (Q, q0, Sigma, Update, Emit).
```

Safety properties additionally declare:

```text
SafeQ : Q -> Prop.
```

Reachable monitor states are quotiented by agreement of every future output
and, where present, future safety status. The result is the canonical minimal
deterministic presentation up to state renaming.

The passive lift is:

```text
(x,q) -a-> (y,q')
iff
x -a-> y
and
q' = Update(q, observe(x,a,y)).
```

Total deterministic update gives one lifted edge above every concrete edge
from a chosen fibre point. Induction gives unique lifting of finite concrete
paths.

Categorically:

```text
monitor:
  finite-set functor on the concrete path category

lift:
  category of elements

projection:
  discrete opfibration
```

The implementation proves and tests the elementary unique-lifting contract;
the categorical statement is its interpretation.

## Residue Tests

A nontrivial history residue requires:

```text
equal projected world behavior profiles;
equal current monitor emissions;
different future lifted capability profiles.
```

Matching current emissions prevents an injected monitor label from counting as
a result.

For a safety property, a corridor residue additionally requires:

```text
different property-relative admissible action classes.
```

Both predicates remain relative to the declared property.

## Validation

Focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\test_finite_relational_canonical_process_monitors.py -q
```

Result:

```text
11 passed
```

Full Python regression:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Result:

```text
472 passed
```

Pytest emitted one environment warning because the sandbox cannot create
`.pytest_cache`. No test failed.

Focused lint and format checks:

```powershell
.\.venv\Scripts\python.exe -m ruff check `
  omega\adapters\finite_relational\canonical_process_monitors.py `
  omega\validation\finite_relational_canonical_process_monitors.py `
  tests\test_finite_relational_canonical_process_monitors.py

.\.venv\Scripts\python.exe -m ruff format --check `
  omega\adapters\finite_relational\canonical_process_monitors.py `
  omega\validation\finite_relational_canonical_process_monitors.py `
  tests\test_finite_relational_canonical_process_monitors.py
```

Result:

```text
all checks passed
```

Retained run:

```powershell
.\.venv\Scripts\python.exe -m `
  omega.validation.finite_relational_canonical_process_monitors `
  --out-root `
  docs\research_notes\validation_results\canonical_process_monitors_v0
```

Retained output:

```text
docs/research_notes/validation_results/canonical_process_monitors_v0/20260731_040223/
```

## Verdict

```text
retained
```

All eight preregistered correctness and classification cases passed. The risky
finite result is:

```text
family-dependent
```

not family-core.

## Results

### Canonical monitor

The compact ancestry property has:

```text
5 states.
```

An equivalent redundant presentation has:

```text
6 states.
```

Both minimize to:

```text
5 states
```

with identical canonical payloads.

Predictive relevance is only relative to the ancestry property. Minimality does
not make that property intrinsically important.

### Unique lifting and projection conservation

The reachable ancestry lift contains:

```text
7 lifted states
10 lifted edges
```

with:

```text
unique step-lift failures: 0
audited path-lift failures: 0
```

When monitor emissions are excluded from lifted atoms, projection conservation
holds through every audited horizon from zero through three:

```text
projection-conservation failures: 0
```

The passive monitor therefore creates no physical controller option or
environment outcome in this finite product.

### Direct-emission control

A route-label monitor gives the two histories different current emitted facts.
Their emitted profiles differ, but they fail the nontrivial residue predicate:

```text
base profiles equal: true
current emissions equal: false
lifted profiles differ: true
history residue: false
```

This blocks direct label injection.

### Property-relative residue

The two route histories end at the same exact world state:

```text
hub.
```

Their projected world behavior profiles and current monitor emissions match
under all three declared properties.

The retained vector is:

```text
ancestry_match:
  history residue: true
  corridor residue: true
  admissible actions:
    alpha history -> {choose_alpha}
    beta history  -> {choose_beta}

completion:
  history residue: false
  corridor residue: false
  admissible actions:
    both histories -> {choose_alpha, choose_beta}

fixed_hazard:
  history residue: false
  corridor residue: false
  admissible actions:
    both histories -> {choose_alpha}
```

Therefore:

```text
family-core history residue: false
family-core corridor residue: false
classification: family-dependent
```

History can alter future obligations relative to a declared property. This run
does not retain a property-family-invariant process distinction.

### Symmetric copy

The symmetric copy branches have:

```text
equal world atoms;
equal action classes;
isomorphic continuations;
equal observed edge symbols;
equal canonical monitor states;
equal lifted profiles.
```

Verdict:

```text
unresolved
```

Raw state names cannot manufacture lineage.

## Evidence Classification

Instrument correctness:

```text
observation equivariance;
canonical minimization;
unique step and path lifting;
world-profile projection conservation;
direct-emission exclusion;
symmetric-copy non-separation.
```

Risky finite result:

```text
the per-property history/corridor residue vector;
the family-dependent classification;
the absence of a family-core residue.
```

The empty family-core result is retained rather than repaired away.

## What Landed

The finite process layer now has:

```text
declared finite trace property
-> canonical residual monitor
-> passive unique-lifting product
-> world-behavior conservation
-> property-relative history profile
-> property-relative continuation corridor
-> explicit family-dependence classification
```

This replaces arbitrary tracker design with a canonical monitor relative to a
declared finite-index property.

## Remaining Debt

The property family remains declared.

The pilot does not derive:

```text
which process properties deserve admission;
which process facts establish operational identity;
which history distinctions carry standing;
an unbounded monitor for arbitrary persistence properties;
a family-core residue beyond current-state behavior;
the joint product dynamics needed for generated non-flagness.
```

The copresheaf interpretation does not yet identify the process lift with a
realization presheaf. A genuine common object would require an explicit base
and compatibility law, plausibly:

```text
Context^op x Path(S) -> Set.
```

That is a later unification target, not a result of this pilot.

## Public Compression

A finite trace property induces a canonical passive memory state. The resulting
history lift has unique path lifting and cannot create physical capabilities,
but it can change future admissible actions relative to that property. In the
retained fixture the effect is ancestry-relative and does not survive the full
declared property family. Symmetric copies remain unresolved.
