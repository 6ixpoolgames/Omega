# Finite Controlled Markov Abstraction Report v0

Status: retained exact finite machinery and theorem spine

Date: 2026-08-01

Protocol:
[Finite Controlled Markov Abstraction Protocol v0](finite_controlled_markov_abstraction_protocol_v0.md)

Retained run:
[20260801_075028](../validation_results/controlled_markov_abstraction_v0/20260801_075028/)

Foundation checkpoint:
`34fe13e` (`Add Alpha-Omega foundation v0`)

Protocol checkpoint:
`7f3b224` (`Preregister controlled Markov abstraction v0`)

## Result

The sprint retained a clean, executable finite state-aggregation layer for
controlled Markov systems.

Given:

```text
an exact rational controlled Markov system;
a surjective state aggregation;
a stationary deterministic policy;
an exact initial distribution;
and a finite horizon;
```

the implementation can:

```text
check action-aware strong lumpability;
return exact witnesses when it fails;
measure the largest representative discrepancy;
construct the quotient kernel when it passes;
check policy and predicate factorization separately;
push finite path laws through the state aggregation;
compare the pushed concrete law with the quotient law;
measure total-variation information loss;
audit finite likelihood-ratio sufficiency;
and transport bounded target-hit probabilities.
```

All preregistered cases passed. No kill condition fired.

## Clean Rebuild

This implementation does not import the historical `omega` Python package.
The older Foundation and agency-diamond modules were used only as sources of
fixtures, algorithms, and negative controls.

The candidate migration structure is:

```text
omega_v2/
  finite/
    model.py
    path_laws.py
    abstraction.py
    continuation.py
  experiments/
    controlled_markov_abstraction_v0.py
  validation/
    artifacts.py
    controlled_markov_abstraction_v0.py
```

The formal counterpart is:

```text
formal/lean/OmegaV2/
  Finite/
    ControlledMarkov.lean
    Abstraction.lean
    Continuation.lean
formal/lean/OmegaV2.lean
```

`OmegaV2` imports Mathlib but no historical Omega formal namespace.

The root package and namespace names may change in the successor repository.
The internal separation between dynamics, path laws, state aggregation,
continuation observables, experiments, and validation should not need to
change.

## Terminology

The formal and executable layers do not use `presentation soundness` as one
undifferentiated property.

They distinguish:

```text
support simulation and bisimulation;
action-aware strong lumpability;
policy factorization;
state-predicate factorization;
finite path-law pushforward;
and likelihood-ratio sufficiency for a selected two-law comparison.
```

This is the terminology required to state what an abstraction actually
preserves.

## Executable Interface

### Exact finite dynamics

[`omega_v2/finite/model.py`](../../../omega_v2/finite/model.py) defines:

```text
FiniteDistribution;
ControlledMarkovSystem;
DeterministicPolicy;
FinitePath;
StateAggregation.
```

Transition probabilities and all validation comparisons use exact rational
arithmetic.

The stochastic system contains dynamics only. State observations, predicates,
and interpretations remain separate data.

### Path laws

[`omega_v2/finite/path_laws.py`](../../../omega_v2/finite/path_laws.py) supplies:

```text
finite_path_law;
path_probability;
abstract_path;
pushforward_path_law;
event_probability;
total_variation_distance;
kl_divergence;
audit_likelihood_ratio_sufficiency.
```

Total variation is exact. KL divergence is retained only as a floating-point
diagnostic.

### State aggregation

[`omega_v2/finite/abstraction.py`](../../../omega_v2/finite/abstraction.py)
supplies:

```text
audit_actionwise_lumpability;
build_quotient_kernel;
audit_policy_factorization;
abstract_policy;
audit_predicate_factorization;
audit_support_bisimulation;
pushforward_initial_distribution;
audit_path_law_pushforward.
```

A failed lumpability audit returns the concrete representatives, action,
aggregate target, exact left and right masses, and their discrepancy. The
quotient constructor refuses to proceed.

### Continuation consumer

[`omega_v2/finite/continuation.py`](../../../omega_v2/finite/continuation.py)
supplies:

```text
bounded_hit_probability;
safe_through_horizon_probability;
audit_bounded_hit_transport.
```

The target predicate must be constant on each aggregation fiber. This
requirement is checked independently of stochastic lumpability.

## Lean Results

The clean formal namespace proves:

### Controlled Markov kernel

```text
oneStep_nonneg;
hitWithin_nonneg.
```

### State aggregation

```text
blockMass_nonneg;
blockMass_representative_independent;
blockMass_sum_one;
weighted_sum_fiberwise;
oneStep_transport.
```

The quotient kernel is constructed as an exact normalized controlled Markov
kernel.

### Continuation transport

```text
hitWithin_transport.
```

Under:

```text
action-aware strong lumpability;
policy factorization;
and target-predicate factorization;
```

the concrete and quotient bounded target-hit probabilities agree at every
finite horizon.

The executable layer additionally checks equality of the complete enumerated
finite path laws. A general formal path-distribution datatype and pushforward
theorem remain a possible later extension; the retained theorem spine already
proves the one-step and bounded-continuation consumers used in this sprint.

## Retained Cases

### Exact nontrivial quotient

The concrete system has four states:

```text
A0, A1, B0, B1
```

and the state aggregation drops the copy index:

```text
A0, A1 -> A
B0, B1 -> B.
```

Concrete transitions differ within fibers, but every representative induces
the same aggregate transition row for every action.

Results at path horizon 3:

```text
action-aware strong lumpability: true
support bisimulation: true
concrete path count: 8
quotient path count: 4
full path-law pushforward TV: 0
selected path-event mass, concrete pushforward: 63/64
selected path-event mass, quotient: 63/64
```

The bounded probability of hitting `B` within two steps from either `A`
representative is:

```text
15/16
```

and agrees with the quotient computation.

### Rejected state aggregation

One representative in aggregate state `A` assigns:

```text
3/4
```

to aggregate state `B`, while the other assigns:

```text
1/4.
```

Results:

```text
action-aware strong lumpability: false
exact witness count: 2
maximum representative TV discrepancy: 1/2
quotient construction refused: true
```

This is the first retained practical error quantity for a later approximate
state-aggregation theorem. v0 does not treat it as a complete real-system error
bound.

### Support-level abstraction loses weighted directionality

The biased reciprocal-support three-cycle is collapsed to one aggregate state.

Results:

```text
support bisimulation: true
action-aware strong lumpability: true
full aggregate path-law pushforward: true
concrete forward/reversed path TV: 11/16
aggregate forward/reversed path TV: 0
likelihood-ratio sufficiency: false
```

There is no contradiction. Strong lumpability preserves the aggregate Markov
process. The microscopic path-reversal comparison does not factor through this
aggregation.

### Sufficient hidden-coordinate quotient

The second directional fixture adds an independent symmetric hidden coordinate
to the biased cycle and then removes only that coordinate.

Results:

```text
concrete path count: 384
aggregate path count: 24
action-aware strong lumpability: true
full path-law pushforward: true
likelihood-ratio sufficiency: true
concrete forward/reversed path TV: 11/16
aggregate forward/reversed path TV: 11/16
```

This provides the positive control missing from the Foundation v0
counterexample: a nontrivial state aggregation can preserve the selected
directionality comparison when the removed coordinate carries no information
for distinguishing the two laws.

## Data Processing

Both retained two-law comparisons satisfy:

```text
TV(aggregate P, aggregate Q) <= TV(P, Q).
```

The collapsed-cycle fixture is strict:

```text
0 < 11/16.
```

The sufficient hidden-coordinate fixture is equality:

```text
11/16 = 11/16.
```

This sprint checks the inequality exactly in the retained finite cases. A
general Lean proof of total-variation data processing is not yet included.

## Practical Applicability

The implementation is exact finite laboratory machinery. Its interfaces were
chosen so a later empirical adapter can supply:

```text
a learned model or confidence set;
a reachable operating domain;
a finite horizon;
a declared observable family;
and an explicit tolerance.
```

The current lumpability audit already returns a maximum representative
discrepancy. The next practical theorem would bound finite-horizon observable
error in terms of that discrepancy and model uncertainty.

No such empirical guarantee is claimed here.

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaV2
.\.venv\Scripts\python.exe -m pytest tests\test_finite_relational_controlled_markov_abstraction.py -q
.\.venv\Scripts\python.exe -m omega_v2.validation.controlled_markov_abstraction_v0
```

Retained validation:

```text
Lean: 946 jobs passed
focused Python tests: 18 passed
full Python suite: 519 passed
historical AlphaOmega regression build: 1173 jobs passed
preregistered executable cases: 10 passed
kill conditions: 0 fired
```

The retained run contains:

```text
summary.json;
lumpability.csv;
path_transport.csv;
directionality_loss.csv;
continuation_events.csv;
report.md.
```

## Remaining Debt

The next formal and implementation debts are:

```text
general finite path-distribution pushforward in Lean;
general total-variation data processing in Lean;
finite-horizon error bounds for approximate aggregation;
partial action availability and action abstraction;
nonstationary or randomized policies;
ambiguity sets and explicit exists-policy / forall-disturbance compatibility;
and empirical model-conformance adapters.
```

The robust compatibility object remains separate and unbuilt.

## Claim Boundary

This sprint establishes finite exact controlled Markov state-aggregation
machinery and bounded stochastic continuation transport.

It does not establish:

```text
empirical model validity;
unbounded or continuous stochastic equivalence;
value;
valuerhood;
standing;
agency;
moral license;
Omega compatibility;
or a preferred physical orientation.
```

## Public Compression

A state aggregation may be exact for the aggregate Markov process while
discarding a microscopic directional statistic. Exact transport requires
naming the stochastic object being preserved: transition blocks, finite path
events, or the information used by a selected comparison.
