# Generated Continuation Dynamics Report v0

Status: retained post-freeze constructive witness and exhaustive finite
distribution audit

Scope: exact shared-action product kernels, dynamically derived compatibility
complexes, and bounded deformation verdicts over declared exhaustive
three-state system classes

Claim boundary: not thermodynamics, an arrow-of-time theorem, physical degrees
of freedom, value, valuerhood, agency, standing, identity, moral license,
lushness, or Omega validation

## Protocol

Preregistered protocol:

```text
docs/research_notes/omega_v2/generated_continuation_dynamics_protocol_v0.md
```

Protocol commit:

```text
627b04b Preregister generated continuation dynamics audit
```

The protocol fixed both exhaustive manifests, the primary weighting rule,
controls, evidence classes, and kill conditions before generator code or
outputs existed.

## Formal Objects

### Generated compatibility

For a component family `F`, the exact shared-action product uses one action for
every component:

```text
(x_i)_(i in F) -a-> (y_i)_(i in F)
iff
each component i takes its a-labelled transition.
```

The family is jointly realizable exactly when its all-live state belongs to:

```text
K_F = gfp X.
  { s in Safe_F |
    exists one shared action a,
    every a-successor of s remains in X }.
```

The compatibility complex and its maximal faces are derived from these kernel
memberships. They are not supplied as adapter data.

### Generated deformation

Each generated finite system has:

```text
3 states;
2 total deterministic actions;
one optional positive atom at each state.
```

For each exact structural edge and horizon `h in {0,1,2}`, source and target
behavior signatures are compared under bounded alternating refinement:

```text
EXPANSION;
CONTRACTION;
EQUIVALENT;
MIXED.
```

The primary distribution counts each distinct `(source,target)` edge once per
system. Action-labelled edge counts are retained only as a diagnostic.

## Validation

Focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\test_finite_relational_generated_continuation_dynamics.py -q
```

Initial focused result:

```text
12 passed
```

Full Python regression:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Result:

```text
484 passed
```

Pytest emitted one environment warning because the sandbox cannot create
`.pytest_cache`. No test failed.

Additional retained-stack validation:

```text
finite relational adapter smoke:       109 passed
finite relational adversarial audit:    36 cases passed
baseline witness smoke:                 13 witnesses passed
baseline witness family smoke:          13 families passed
Ruff check and format:                  passed
```

Retained run:

```powershell
.\.venv\Scripts\python.exe -m `
  omega.validation.finite_relational_generated_continuation_dynamics `
  --out-root `
  docs\research_notes\validation_results\generated_continuation_dynamics_v0
```

Retained output:

```text
docs/research_notes/validation_results/generated_continuation_dynamics_v0/20260731_142523/
```

## Verdict

```text
retained
```

All fifteen preregistered cases passed.

## Generated Non-Flagness

The exact manifest contains:

```text
216 assignments;
24 hollow assignments;
102 filled assignments;
24 filled assignments matching the retained hollow control panel;
0 downward-closure failures;
0 kernel/intersection correspondence failures.
```

For this generated family:

```text
all-live in K_F
iff
the allowed-action sets of every component in F have nonempty intersection.
```

If a common action exists, it gives a safe self-loop at the all-live state. If
no common action exists, every shared action sends at least one component to
`dead`, so the all-live state is removed at the first predecessor iteration.
The exhaustive run checks this correspondence for every family in every
assignment.

The lexicographically first hollow assignment is:

```text
A permits {a0,a1}
B permits {a0,a2}
C permits {a1,a2}
```

Its pairwise common actions are:

```text
A,B -> a0
A,C -> a1
B,C -> a2
```

Every singleton and pair has a nonempty shared-action continuation kernel. The
triple does not:

```text
K_A       = 1
K_B       = 1
K_C       = 1
K_AB      = 1
K_AC      = 1
K_BC      = 1
K_ABC     = 0
```

The derived maximal faces are:

```text
{A,B}
{A,C}
{B,C}
```

so the complete one-skeleton does not fill the triangle.

### Matched filled control

The retained control is:

```text
A permits {a0,a1}
B permits {a0,a2}
C permits {a0,a3}
```

It matches the hollow witness on:

```text
action alphabet size;
component count;
per-component allowed-action counts;
all three pairwise common-action counts;
singleton kernel sizes;
pair kernel sizes;
complete one-skeleton.
```

The common action `a0` keeps the triple viable:

```text
K_ABC = 1.
```

Its sole maximal face is `{A,B,C}`.

### Quantifier control

Allowing each component to choose a different action makes the hollow triple
viable. This is the invalid control:

```text
exists a_A;
exists a_B;
exists a_C
```

rather than the retained:

```text
exists one shared a.
```

The same-action quantifier is therefore load-bearing.

### Constructive result

This is a finite counterexample to:

```text
pairwise continuation compatibility
implies
joint continuation compatibility.
```

The result is now generated by exact dynamics. It repairs the old
hand-declared hollow-triangle limitation. It does not show that non-flagness is
common in physical or moral systems.

## Deformation Manifest

The exact system manifest contains:

```text
complete systems:   5,832
reversible subset:    288
absorbing subset:     440
```

The subsets overlap the complete class. The retained manifest digest is:

```text
e0009b05e1837657012be9d9162bef10ef05e0a2522caa3c2026541129402c86
```

## Structural-Edge Distributions

| Class | h | Expansion | Contraction | Mixed | Equivalent |
|---|---:|---:|---:|---:|---:|
| complete | 0 | 0.166667 | 0.166667 | 0.000000 | 0.666667 |
| complete | 1 | 0.148148 | 0.148148 | 0.088889 | 0.614815 |
| complete | 2 | 0.137654 | 0.138066 | 0.111111 | 0.613169 |
| reversible | 0 | 0.166667 | 0.166667 | 0.000000 | 0.666667 |
| reversible | 1 | 0.141667 | 0.141667 | 0.116667 | 0.600000 |
| reversible | 2 | 0.125000 | 0.133333 | 0.141667 | 0.600000 |
| absorbing | 0 | 0.142570 | 0.142570 | 0.000000 | 0.714859 |
| absorbing | 1 | 0.138554 | 0.152610 | 0.036145 | 0.672691 |
| absorbing | 2 | 0.138554 | 0.152610 | 0.036145 | 0.672691 |

No class supports universal forward expansion.

The absorbing class has a finite contraction excess at horizons one and two:

```text
contraction: 304 / 1,992 structural edges
expansion:   276 / 1,992 structural edges
```

This is a result about the declared absorbing generator. Absorption is not
thermodynamic entropy, and no physical arrow follows.

The complete and reversible classes are exactly balanced at horizons zero and
one under primary structural-edge weighting. Small differences appear at
horizon two. Mixed verdicts appear only after dynamic continuation structure
enters the signatures.

## Weighting Result

Action-edge weighting is not invariant under behaviorally redundant action
duplication.

The retained duplicate-action control has:

```text
baseline action counts:
  expansion 3
  equivalent 3

after duplicating a0:
  expansion 5
  equivalent 4
```

The structural behavior signatures and structural-edge verdicts are unchanged.

The weighting choice can also alter the apparent direction. For the complete
class at horizon two:

```text
structural edges:
  contraction 0.138066
  expansion   0.137654

action edges:
  contraction 0.120370
  expansion   0.139918
```

Thus a claim about expansion bias requires a declared, duplication-resistant
measure over transitions or trajectories. Raw action-edge census is not such a
measure.

## Other Controls

```text
component/action relabeling:
  compatibility preserved;

state/action/atom relabeling:
  deformation verdicts preserved at h = 0,1,2;

deadlock:
  a component with no safe action fails singleton compatibility;

reverse edge:
  an absent reverse transition is not synthesized or classified;

classifier:
  all four deformation verdicts remain present in retained controls;

derived-face bridge:
  the existing CompatibilityStructure consumes the generated maximal faces
  exactly.
```

## Evidence Classification

Generator correctness:

```text
GN1, GN2, GN5 through GN8;
DD1, DD3 through DD7.
```

Constructive strictness:

```text
GN3 generated non-flagness;
GN4 matched filled control.
```

Risky generated result:

```text
DD2 per-class, per-horizon deformation distributions.
```

The generated distribution is the first non-fixture deformation census in this
post-freeze branch. It does not supply its own physical sampling measure.

## What Landed

The post-freeze stack now contains:

```text
exact finite dynamics
-> bounded behavior signatures
-> deformation classifier
-> exhaustive generator classes
-> generator-relative verdict distributions

and:

component continuation systems
-> exact shared-action products
-> robust continuation kernels
-> derived compatibility complex
-> generated higher-order obstruction.
```

## Remaining Debt

The next arrow-facing layer requires an orientation and measure not supplied
here:

```text
micro/macro state model;
independently defined entropy or entropy-production coordinate;
certified coarse-graining;
trajectory or occupancy measure resistant to duplicate presentation;
comparison of verdict distributions conditional on that orientation.
```

The admissible-projections problem also remains:

```text
the machinery can derive consequences relative to a grammar and presentation;
it does not derive which grammars or projections deserve admission.
```

## Public Compression

Exact shared-action dynamics generate a hollow compatibility triangle: every
pair can persist while the triple cannot. Separately, exhaustive finite-system
classes contain expansion, contraction, mixed, and equivalent transitions,
with no universal forward-expansion law. Even the sign of a small aggregate
bias can depend on how transitions are weighted, so a thermodynamic claim
requires an independently justified orientation and measure.
