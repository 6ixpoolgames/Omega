# Omega v2 May and Robust Realization Report v0

Status: retained finite construction and theorem spine

Date: 2026-08-03

Protocol:
[Omega v2 May and Robust Realization Protocol v0](robust_omega_protocol_v0.md)

Protocol checkpoint:
`5404f36` (`Preregister Omega v2 realization core`)

Retained run:
[20260803_014236](../validation_results/robust_omega_v0/20260803_014236/)

## Verdict

The clean `omega_v2` package now retains two distinct finite realization
objects:

```text
May(G):
  some witness realizes every candidate in G;

Robust_E(G):
  one policy produces a realizing witness for every environment in the
  declared nonempty scope E.
```

The construction verdict is:

```text
finite_may_and_robust_realization_core_retained
```

All 15 preregistered construction and rejection cases passed. No kill
condition fired.

This is a construction and migration result, not a discovery claim about the
correct candidate, policy, or environment classes.

## Quantifier Contract

The executable Robust object fixes:

```text
exists one policy;
for every environment in a declared nonempty finite scope;
there is exactly one deterministic finite run;
that run jointly realizes every candidate in the family.
```

Formally:

```text
Real(G) =
  {w | every candidate in G is realized by w}

Secure_E(G) =
  {pi | for every e in E, outcome(pi, e) is in Real(G)}

May(G) iff Real(G) is nonempty

Robust_E(G) iff Secure_E(G) is nonempty
```

The implementation rejects an empty environment scope and rejects a selected
transition row with more than one positive-probability successor. Randomized
policies, stochastic environments, nondeterministic runs, and infinite
horizons remain out of scope.

## Clean Implementation

The core lives in:

```text
omega_v2/finite/realization.py
formal/lean/OmegaV2/Finite/Realization.lean
```

It imports no historical Omega package. The finite Python object retains:

```text
candidate realization classes;
complete May witness fibers;
complete securing-policy fibers;
and the environment-indexed run witness for each securing policy.
```

The controlled-system adapter in
`omega_v2/experiments/robust_omega_v0.py` generates the complete
policy/environment outcome table by executing deterministic finite
`ControlledMarkovSystem` rollouts. The generic realization core consumes that
table without depending on the Markov implementation.

No maximal face is selected.

## May Migration

The retained hollow-triangle fixture reproduces the historical May payload
exactly:

```text
Real({A,B}) = {history:a0}
Real({A,C}) = {history:a1}
Real({B,C}) = {history:a2}
Real({A,B,C}) = empty
```

The clean and historical structural digests are identical:

```text
b79cd2f3be3a4b98047055a0776bfe4411109ca0502678d75d14bc00560e8e28
```

The fixture has three maximal faces and no greatest face. Adding an exact
duplicate candidate changes the raw candidate count from three to four but
leaves the quotient count, fibers, maximal faces, and structural digest
unchanged.

## May Does Not Imply Robust

The environment-sensitivity fixture retains a direct separation:

```text
May({A,B}):
  true

Robust_calm({A,B}):
  true, secured by policy_fragile

Robust_{calm,stress}({A,B}):
  false
```

Only the selected environment scope changes. The candidate realization
classes remain fixed.

This establishes that existence of a realizing witness does not supply one
policy that secures realization across a declared environment scope.

## Robust Hollow Triangle

The deterministic controlled-system fixture uses one policy interface and one
environment scope for every family. It retains:

```text
Robust({A,B}):
  true, secured by policy_ab

Robust({A,C}):
  true, secured by policy_ac

Robust({B,C}):
  true, secured by policy_bc

Robust({A,B,C}):
  false
```

Each pair policy carries its generated run witness under both `north` and
`south`. No policy secures the triple. Thus pairwise Robust compatibility does
not imply joint Robust compatibility.

The positive control adds `policy_abc` under the same state, action, and
environment interfaces. That policy secures the triple in both environments,
so the harness also detects a genuinely Robust family when one is present.

## Structural Laws

The executable audit reports zero failures for:

```text
candidate antitonicity;
environment antitonicity;
Robust implies May over a nonempty environment scope;
May witness restriction;
Robust witness restriction;
identity of restriction;
composition of restriction;
candidate duplicate invariance;
and policy/environment rollout replay.
```

Environment antitonicity has the expected direction: enlarging the environment
scope can remove securing policies but cannot create them.

## Lean Spine

The clean `OmegaV2` formal root now retains:

```text
Real
MayCompatible
Secure
RobustCompatible

real_antitone
mayCompatible_downward
real_union

secure_candidate_antitone
secure_environment_antitone
robustCompatible_candidate_downward
robustCompatible_environment_downward
secure_union
robustCompatible_implies_mayCompatible

restrictReal
restrictReal_identity
restrictReal_composition
restrictSecure
restrictSecure_identity
restrictSecure_composition
```

`lake build OmegaV2` completes with 947 jobs and no `sorry`, `admit`, `axiom`,
or placeholder theorem in the new module.

## Validation

Canonical commands:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_omega_v2_robust_omega.py -q

.\.venv\Scripts\python.exe -m omega_v2.validation.robust_omega_v0 \
  --out-root docs\research_notes\validation_results\robust_omega_v0

powershell -ExecutionPolicy Bypass \
  -File scripts\setup\invoke_lake.ps1 build OmegaV2
```

The retained run includes:

```text
summary.json
case_results.csv
candidate_classes.csv
may_fibers.csv
robust_fibers.csv
policy_environment_runs.csv
environment_sensitivity.csv
report.md
```

## Kill Conditions

All preregistered kill conditions are false:

```text
empty environment scope admitted:
  false

partial outcome table admitted:
  false

multivalued outcome table admitted:
  false

generated run table mismatch:
  false

candidate or environment antitonicity failure:
  false

Robust without May:
  false

candidate duplicate changed quotient payload:
  false

Robust witness evidence discarded:
  false

pair/triple scope mismatch:
  false

legacy May parity failure:
  false
```

## Claim Boundary

This sprint establishes finite, deterministic, witness-retaining May and
Robust realization under the stated quantifiers. It also establishes
higher-order incompatibility under each view and exact sensitivity to a
declared environment scope.

It does not establish:

```text
the correct candidate patterns;
the correct policy class;
the correct environment class;
stochastic or empirical robustness;
operational identity;
agency;
valuerhood;
standing;
value;
moral license;
universal Omega;
or a preferred maximal realization.
```

## Public Compression

A family may be realizable somewhere without any single policy securing it
across a declared set of environments. Finite Omega therefore retains both
the complete May-realization fibers and the policies, environment cases, and
runs that witness Robust realization. Pairwise robust compatibility need not
imply joint robust compatibility.

## Next Debt

The clean realization core now exists. The next live questions are not another
May construction. They are:

```text
which candidate-process predicates survive an independence audit;
how stochastic or adversarial environment semantics alter Robust fibers;
and whether the declared policy/environment interfaces can be derived from
causal process structure rather than supplied by a fixture.
```

Those questions require separate protocols. This report does not answer them.
