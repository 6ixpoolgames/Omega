# Finite Controlled Markov Abstraction Protocol v0

Status: preregistered executable and theorem-spine protocol

Date: 2026-08-01

Parent result:
`docs/research_notes/omega_v2/alpha_omega_foundation_report_v0.md`

## Question

For a finite controlled Markov system and a surjective state map, which exact
stochastic claims survive state aggregation?

The sprint must separate four established notions:

```text
support simulation or bisimulation:
  qualitative transition facts;

action-aware strong lumpability:
  representative-independent transition probabilities between aggregate states;

finite path-law pushforward:
  equality between the aggregated concrete path law and the quotient path law;

statistical sufficiency for a selected comparison:
  no loss of the information used by that comparison.
```

The result must be executable machinery, not only a hierarchy of definitions.

## Terminology

`Presentation soundness` may be used as umbrella prose only. Formal results and
validation output must name the property actually checked:

```text
support simulation;
support bisimulation;
action-aware strong lumpability;
quotient-kernel construction;
path-law pushforward;
finite path-event preservation;
likelihood-ratio sufficiency.
```

No new generic certificate type is introduced.

## Exact v0 Scope

Supply:

```text
a finite controlled Markov kernel with exact rational probabilities;
a finite common action alphabet;
a surjective state map q : X -> Y;
a stationary deterministic policy on X;
an abstract policy on Y;
an exact initial distribution;
a finite path horizon;
and selected finite path events or comparisons.
```

The controlled kernel is total for every state-action pair. Therefore action
availability is fixed in v0. General action abstraction and partial action
availability are out of scope.

The concrete policy must factor through the state map:

```text
policy_X(x) = policy_Y(q(x)).
```

## Action-Aware Strong Lumpability

For concrete states `x1` and `x2` in the same aggregate state, every action
must induce the same probability on every aggregate target:

```text
q(x1) = q(x2)

implies

sum { K(x1, a, z) | q(z) = y }
  =
sum { K(x2, a, z) | q(z) = y }
```

for every action `a` and abstract state `y`.

The executable checker must return exact rational discrepancies and concrete
witnesses:

```text
source aggregate;
left and right concrete representatives;
action;
target aggregate;
left mass;
right mass;
absolute discrepancy.
```

A failed check must not construct a quotient kernel.

## Quotient Kernel

When action-aware strong lumpability holds, construct the quotient kernel by
aggregating any concrete representative's transition probabilities over target
fibers. The result must:

```text
be independent of representative choice;
contain an exact normalized row for every aggregate-state/action pair.
```

State observations and predicates are not fields of the stochastic kernel.
They are separate maps whose factorization through `q` must be audited before
using them in an abstract claim. This prevents stochastic state aggregation
from silently choosing semantics for a merged state.

## Finite Path Laws

Map a concrete controlled path to an abstract path by applying `q` to every
state and retaining the common action labels.

For a factored policy and the pushed-forward initial distribution, test and
formally justify:

```text
pushforward(concrete finite path law)
  =
finite path law(quotient kernel).
```

The executable audit must compare every abstract path mass exactly and return
path-level witnesses on disagreement.

Any event expressed as a set of abstract finite paths then has equal concrete
preimage probability and abstract probability. The implementation must expose
event-probability operations rather than hard-code one event.

## Quantitative Information Loss

For two finite laws `P` and `Q` on the same concrete path space, aggregate both
through the same path map.

Compute exactly:

```text
TV(P, Q);
TV(q_* P, q_* Q);
TV loss.
```

The validation must enforce finite data processing:

```text
TV(q_* P, q_* Q) <= TV(P, Q).
```

KL divergence may be computed as a floating-point diagnostic. It is not part
of the exact theorem acceptance criteria.

Also audit the standard finite sufficiency condition for the selected
two-law comparison:

```text
within every aggregate path fiber, the likelihood ratio P(path) / Q(path)
is constant wherever the ratio is defined.
```

This is a sufficient condition for retaining all information used to
distinguish the two laws. It is not renamed as an Omega-specific property.

## Practical Extension Point

When exact lumpability fails, report the largest total-variation discrepancy
between aggregate successor distributions of representatives in one fiber.

This number is retained for a later approximate-abstraction theorem. v0 does
not claim that it is already a complete real-system error bound.

Future empirical adapters will additionally require:

```text
a model or confidence set;
a reachable operating domain;
a finite horizon;
a declared observable family;
and an explicit error tolerance.
```

## Clean Rebuild Boundary

This sprint is a clean implementation intended to serve as a migration
template. Historical Omega modules are evidence and algorithm sources only.
The new implementation must not import from the existing `omega` package.

Use:

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
    controlled_markov_abstraction_v0.py
```

The eventual successor repository may rename the root package. The internal
module boundaries should migrate without redesign.

### Finite model

`omega_v2.finite.model` owns:

```text
finite controlled Markov systems;
exact rational distributions;
stationary deterministic policies;
finite controlled paths;
and finite state maps.
```

### Path laws

`omega_v2.finite.path_laws` owns:

```text
finite path-law enumeration;
path probability;
path-law pushforward over an explicit path map;
finite event probability;
total-variation distance;
and likelihood-ratio sufficiency audits.
```

### State aggregation

`omega_v2.finite.abstraction` owns:

```text
action-aware strong-lumpability checks;
exact failure witnesses;
maximum representative discrepancy;
quotient-kernel construction;
policy factorization;
state-predicate factorization;
and finite path-law commutation audits.
```

### Continuation

`omega_v2.finite.continuation` owns:

```text
bounded target-hit probabilities;
safe-through-horizon probabilities;
and concrete/quotient continuation comparisons.
```

### Required generic operations

Expose generic operations corresponding to:

```text
audit_actionwise_lumpability
build_quotient_kernel
pushforward_initial_distribution
abstract_path
pushforward_path_law
audit_path_law_pushforward
finite_path_event_probability
total_variation_distance
audit_likelihood_ratio_sufficiency
```

The existing Foundation v0 exact kernel/path implementation and the older
agency-diamond strong-lumpability checker may be mined for tests, algorithms,
and failure controls. They are not dependencies of the clean implementation.

## Fixture Ladder

### Exact nontrivial quotient

At least two concrete states must merge into each of two or more abstract
states. Concrete rows may differ within fibers while their aggregate rows
match.

Required:

```text
action-aware strong lumpability passes;
the quotient kernel normalizes exactly;
path-law pushforward passes;
a bounded continuation event agrees between concrete and quotient systems.
```

### Non-lumpable state aggregation

Two concrete representatives in one source fiber have different aggregate
successor probabilities.

Required:

```text
the checker fails;
an exact witness is returned;
the quotient constructor refuses to proceed;
the maximum discrepancy is positive.
```

### Support-level abstraction that loses weighted directionality

Collapse the biased reciprocal-support cycle to one aggregate state.

Required:

```text
support bisimulation passes;
action-aware strong lumpability passes;
aggregate path-law pushforward passes;
concrete path-reversal total variation is positive;
aggregate path-reversal total variation is zero.
```

This demonstrates that lumpability preserves the aggregate Markov process,
not every microscopic path statistic.

### Sufficient nontrivial quotient

Use a biased cycle with an independent symmetric hidden coordinate and drop
only the hidden coordinate.

Required:

```text
action-aware strong lumpability passes;
path-law pushforward passes;
likelihood-ratio sufficiency passes;
the selected path-reversal total variation is retained exactly.
```

## Downstream Consumer

The sprint is not retained until an existing continuation calculation consumes
the quotient.

Use a bounded target-hit event whose target is a union of state fibers. Compare:

```text
the exact concrete event probability;
the exact quotient event probability.
```

They must agree under the exact nontrivial quotient.

This is a finite exact result. It does not validate an empirical transition
model.

## Lean Theorem Spine

Use a fresh formal namespace:

```text
formal/lean/OmegaV2/Finite/ControlledMarkov.lean
formal/lean/OmegaV2/Finite/Abstraction.lean
formal/lean/OmegaV2/Finite/Continuation.lean
formal/lean/OmegaV2.lean
```

The new namespace must not import historical Omega formal modules. Mathlib is
the only required dependency.

Required formal content:

```text
aggregate target-block mass;
action-aware lumpability;
representative independence of aggregate mass;
policy factorization;
one-step aggregate expectation transport;
finite-horizon transport for at least one declared continuation observable.
```

The preferred continuation observable is bounded target-hit probability for a
target predicate that factors through `q`, because the existing
`Recovery.HitWithin` implementation can consume it.

Full measure-theoretic path spaces, general Markov categories, continuous state
spaces, and KL formalization are out of scope.

## Validation Outputs

Add:

```text
omega_v2/validation/controlled_markov_abstraction_v0.py
tests/test_finite_relational_controlled_markov_abstraction.py
docs/research_notes/omega_v2/finite_controlled_markov_abstraction_report_v0.md
```

Retain:

```text
summary.json;
lumpability.csv;
path_transport.csv;
directionality_loss.csv;
continuation_events.csv;
report.md.
```

## Acceptance Criteria

The sprint is retained only if:

1. The checker and quotient builder are generic reusable functions.
2. Failed lumpability returns an exact concrete witness.
3. Quotient rows normalize exactly.
4. The exact path-law pushforward fixture passes.
5. The support-level directionality-loss fixture passes.
6. The sufficient nontrivial quotient retains the selected statistic.
7. Finite total-variation data processing holds in every retained case.
8. A bounded continuation calculation consumes the quotient and agrees exactly.
9. Lean checks with no `sorry`, `admit`, or new axioms.
10. Focused and full repository tests pass.

## Kill Conditions

Stop for audit rather than force retention if:

```text
the clean finite model cannot remain independent of historical Omega modules;
the clean package must import historical Omega implementation modules;
action availability is silently changed by aggregation;
the quotient depends on representative choice after the checker passes;
path-law equality is tested only on a hand-selected path;
support bisimulation is reported as preserving weighted facts;
strong lumpability is reported as preserving microscopic path statistics;
the checker is fixture-specific rather than reusable;
or any real-system guarantee is inferred from a finite exact fixture.
```

## Claim Boundary

This sprint may establish finite exact state-aggregation machinery and bounded
stochastic continuation transport.

It does not establish:

```text
empirical model validity;
unbounded stochastic equivalence;
continuous-system abstraction;
value;
valuerhood;
standing;
agency;
moral license;
Omega compatibility;
or a preferred physical orientation.
```
