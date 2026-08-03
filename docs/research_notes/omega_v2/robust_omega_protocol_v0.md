# Omega v2 May and Robust Realization Protocol v0

Status: preregistered construction, migration, and theorem-spine protocol

Date: 2026-08-03

Parent results:

```text
docs/research_notes/omega_v2/alpha_omega_foundation_report_v0.md
docs/research_notes/omega_v2/directional_asymmetry_capability_report_v0.md
```

## Purpose

Clean `omega_v2` currently implements finite dynamics, abstraction,
continuation, and controller machinery but does not contain the
witness-retaining realization object that carries Omega's May/Robust
distinction.

This sprint must:

```text
port the retained finite May-realization object into clean omega_v2;
define a finite witness-retaining Robust realization fiber;
connect the robust quantifier to deterministic finite policy/environment runs;
retain higher-order compatibility obstruction under the robust quantifier;
and prove the basic fiber and monotonicity laws in the clean OmegaV2 namespace.
```

This is a construction and migration sprint. The fixtures establish that the
implementation has the required expressive behavior; they are not reported as
empirical discoveries or novel general mathematics.

## Mathematical Contract

Supply finite sets:

```text
C:
  candidate patterns;

W:
  complete finite realization witnesses;

Pi:
  policies;

E:
  environment cases.
```

Supply:

```text
realizes : W -> C -> Prop;
outcome : Pi -> E -> W.
```

For a candidate family `G`, define:

```text
Real(G)
  = {w in W | every candidate in G is realized by w};

May(G)
  iff Real(G) is nonempty;

Secure_E(G)
  = {pi in Pi |
       for every environment e in E,
       outcome(pi, e) belongs to Real(G)};

Robust_E(G)
  iff Secure_E(G) is nonempty.
```

The executable robust fiber must retain, for every securing policy:

```text
the policy identifier;
the selected nonempty environment scope;
and the environment-to-run-witness map.
```

It must not reduce Robust compatibility to a Boolean.

## Exact v0 Semantics

An environment case is one complete deterministic finite scenario. Every
policy/environment pair produces exactly one finite run witness.

The policy and environment universes must be finite and nonempty. The selected
environment scope used by a Robust query must also be nonempty.

The deterministic total-outcome contract deliberately leaves out:

```text
randomized policies;
stochastic outcome thresholds;
nondeterministic inner run quantifiers;
partial observability;
partial policy/environment outcome tables;
infinite horizons;
and empirical model uncertainty.
```

No v0 result may silently alternate between:

```text
exists a successful run;
all positive-support runs succeed;
almost-sure success;
or success above a probability threshold.
```

## Clean Rebuild Boundary

Add the core implementation under:

```text
omega_v2/finite/realization.py
formal/lean/OmegaV2/Finite/Realization.lean
```

The implementation must not import the historical `omega` Python package or
historical Omega Lean namespaces. Historical May machinery is a parity oracle
and source of fixtures only.

The clean executable vocabulary should use:

```text
FiniteRealizationRelation;
CandidateRealizationClass;
MayRealizationFiber;
FiniteMayOmega;
PolicyEnvironmentRuns;
SecuringPolicyWitness;
RobustRealizationFiber;
FiniteOmega.
```

Names may be adjusted during implementation only to improve consistency or
legibility. The mathematical contract may not change after preregistration.

## Candidate Identity and Quotient Scope

The May object quotients exact duplicate candidate descriptions using their
complete incidence columns over the full declared witness universe.

The quotient is intentionally narrow:

```text
same complete finite realization signature:
  exact duplicate in this finite object;

same sampled behavior, public state, or bounded profile:
  not sufficient for identity.
```

Candidate classes are computed once over the complete witness universe. They
must not be recomputed when a smaller environment scope is selected for a
Robust query. This keeps candidate identities stable across environment
sensitivity comparisons.

The sprint does not define operational identity, lineage, redundancy, or
fungibility.

## Required Structural Laws

### Candidate-family antitonicity

If `small` is a subset of `large`, then:

```text
Real(large) is a subset of Real(small);
Secure_E(large) is a subset of Secure_E(small).
```

Therefore May and Robust compatibility are downward closed under candidate
removal.

### Environment-scope antitonicity

If `E_small` is a subset of `E_large`, then:

```text
Secure_E_large(G) is a subset of Secure_E_small(G).
```

Adding environment cases cannot create securing policies.

### Union law

For candidate families `left` and `right`:

```text
Real(left union right)
  = Real(left) intersect Real(right);

Secure_E(left union right)
  = Secure_E(left) intersect Secure_E(right).
```

### Robust implies May

For a nonempty environment scope:

```text
Robust_E(G) implies May(G).
```

The nonempty-scope hypothesis is load-bearing. An empty universal
quantification must not create vacuous Robust compatibility.

### Restriction

A witness or securing-policy witness for a larger candidate family restricts
to the same underlying witness for every smaller family. Identity and
composition of these restrictions must hold.

## Batch A: May Migration Parity

Port the retained shared-action hollow triangle:

```text
A:
  {a0, a1}

B:
  {a0, a2}

C:
  {a1, a2}
```

Required:

```text
Real({A,B}) = {a0};
Real({A,C}) = {a1};
Real({B,C}) = {a2};
Real({A,B,C}) = {};

all singletons May-compatible;
all pairs May-compatible;
triple not May-compatible;
three maximal faces;
no greatest face;
zero downward-closure failures;
zero restriction failures.
```

Adding `A_copy` with the same complete finite incidence column as `A` must:

```text
increase the raw candidate count;
leave the quotient candidate-class count unchanged;
and leave the complete structural May payload unchanged.
```

## Batch B: Deterministic Policy/Environment Adapter

Build finite deterministic controlled-system fixtures using the existing clean
v2 model and policy interfaces.

For every environment case:

```text
the state and action interfaces are fixed;
the transition kernel is deterministic;
the initial state is explicit;
the finite horizon is explicit;
and every declared policy produces exactly one finite path.
```

Convert those runs into the generic policy/environment realization table.

The experiment must cross-check the generated table against direct rollout.
Hand-authored outcome rows alone are insufficient for retaining the sprint.

## Batch C: Robust Fixtures

### May but not Robust

Retain a family with at least one complete realization witness but no single
policy whose run realizes that family in every environment case.

Required:

```text
May(G):
  true;

Robust_E(G):
  false.
```

### Robust positive control

Retain a family for which one policy secures the whole family in every
environment case. The robust fiber must retain the policy and all
environment-indexed run witnesses.

### Robust hollow triangle

Using one fixed candidate semantics, policy interface, and nonempty
environment scope, retain:

```text
Robust_E({A,B});
Robust_E({A,C});
Robust_E({B,C});
not Robust_E({A,B,C}).
```

Different pairs may have different securing policies. No policy may secure the
triple.

Also retain a positive control in which one additional policy really does
secure the triple across the same environment scope.

### Environment sensitivity

Use nested nonempty scopes:

```text
E_calm subset E_full
```

and retain a family such that:

```text
Robust_E_calm(G):
  true;

Robust_E_full(G):
  false.
```

Candidate classes and May fibers must remain fixed across the comparison.

### Duplicate candidate

Adding an exact candidate duplicate must not change:

```text
quotient candidate classes;
May compatibility support;
Robust compatibility support;
or securing-policy identities after quotienting the candidate family.
```

## Lean Theorem Spine

Add clean formal definitions corresponding to:

```text
Real;
MayCompatible;
Secure;
RobustCompatible;
candidate-family restriction.
```

Required theorems:

```text
real_antitone;
mayCompatible_downward;
real_union;

secure_candidate_antitone;
secure_environment_antitone;
robustCompatible_candidate_downward;
robustCompatible_environment_downward;
secure_union;
robustCompatible_implies_mayCompatible;

restrict_identity;
restrict_composition.
```

The formal implementation may represent a securing witness as a policy
together with its proof over the selected environment set. The executable
layer additionally retains explicit environment-to-run identifiers.

No `sorry`, `admit`, `axiom`, or placeholder theorem is permitted.

## Validation Outputs

Add:

```text
omega_v2/experiments/robust_omega_v0.py
omega_v2/validation/robust_omega_v0.py
tests/test_omega_v2_robust_omega.py
docs/research_notes/omega_v2/robust_omega_report_v0.md
```

Retain:

```text
summary.json;
case_results.csv;
candidate_classes.csv;
may_fibers.csv;
robust_fibers.csv;
policy_environment_runs.csv;
environment_sensitivity.csv;
report.md.
```

## Acceptance Criteria

The sprint is retained only if:

1. Clean May results reproduce the retained legacy fixture exactly.
2. The implementation imports no historical Omega package.
3. The policy/environment table is generated from deterministic finite runs.
4. Every policy/environment pair has exactly one run witness.
5. Robust fibers retain policy and environment-indexed run evidence.
6. Candidate and environment antitonicity checks report zero failures.
7. Every Robust-compatible family is May-compatible.
8. The May-not-Robust, Robust-positive, Robust-hollow-triangle, and
   environment-sensitivity controls all pass.
9. Exact candidate duplication leaves the quotient structure unchanged.
10. Lean checks with no placeholders.
11. Focused and full Python validation pass.
12. No maximal face is selected and no agency, valuer, or moral claim is
    emitted.

## Kill Conditions

Stop for audit rather than retain the sprint if:

```text
an empty environment scope is admitted;
the outcome table is partial or multivalued;
pair and triple fixtures use different policy interfaces or environment scopes;
Robust compatibility discards its securing policies or environment runs;
adding candidates creates realization witnesses or securing policies;
adding environment cases creates securing policies;
a Robust-compatible family is not May-compatible;
candidate classes change when only the selected environment scope changes;
an exact candidate duplicate changes the quotient payload;
the clean May fixture differs from the retained legacy result;
the controlled-system adapter and generic outcome table disagree;
or the result is interpreted as value, standing, agency, moral compatibility,
empirical robustness, or universal Omega.
```

## Claim Boundary

This sprint may establish:

```text
finite witness-retaining May realization;
finite witness-retaining Robust realization under exists-policy /
forall-deterministic-environment quantifiers;
higher-order incompatibility under both quantifier views;
and exact finite sensitivity to a declared environment scope.
```

It does not establish:

```text
the correct candidate patterns;
the correct policy class;
the correct environment class;
stochastic or empirical robustness;
operational identity;
valuerhood;
agency;
standing;
value;
moral license;
universal Omega;
or a preferred maximal realization.
```

## Public Compression

A family may be realizable somewhere without any single policy securing it
across a declared set of environments. Finite Omega therefore retains both the
complete May-realization fibers and the policies, environment cases, and runs
that witness Robust realization. Pairwise robust compatibility need not imply
joint robust compatibility.
