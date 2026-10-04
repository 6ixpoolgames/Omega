# C1 and the bounded probabilistic quotient

Date: 2026-09-28. Mathematical audit and implementation scope.

Contract: [audit protocol](continuation_equivalence_audit_protocol_v0.md).
Parent: [draft prediction pilot](continuation_prediction_pilot_protocol_v0.md).

## Result

C1's proposed recurrence is the same bounded, cost-labeled probabilistic
partition refinement implemented by the conventional quotient. It adds no
distinct semantics within this model and interface. A different implementation
of the recurrence could still have engineering advantages; equivalence alone
says nothing about its speed or total storage.

The argument below is a mathematical induction, backed by exact executable
checks. It is not a machine-checked Lean theorem. It does not identify this
quotient with every possible notion of predictive equivalence, prove that it
is the smallest representation for an installed controller catalogue, or give
a general theorem about Omega cosmology or lushness.

## Definitions and partition equality

Fix a finite rational controlled Markov kernel K, a finite alphabet of joint
actions A, nonnegative integer transition costs c(s,a,t), terminal set T, and
one shared observation map o_i for each local controller. Fix a registered atom
map v. Let b(s) = (s in T, (o_i(s))_i, v(s)).

Define equivalence relations R_h on world states. At h = 0, states are related
exactly when their base labels agree. At h > 0, related terminal states have
equal base labels and stop. Two nonterminal states s and u are related exactly
when their base labels agree and, for every joint action a, every integer cost
d, and every R_(h-1) class C,

```text
sum { K(s,a,t) : t in C and c(s,a,t) = d }
 =
sum { K(u,a,t) : t in C and c(u,a,t) = d }.
```

C1's implementation builds nodes bottom-up. A node stores the base label and,
unless terminal or at depth zero, an exact distribution on (cost, child node)
for every action. Identical nodes at the same depth share one identifier.
The quotient implementation instead assigns blocks by pairwise comparison of
base labels and the mass vectors in the displayed equation. It does not call
C1's interning procedure. Both use exact rational arithmetic.

**Proposition.** For every h, C1 assigns two states the same node at depth h if
and only if they belong to the same R_h block.

**Proof.** At depth zero, both compare exactly b. Assume the correspondence at
depth h-1. For terminal states, both compare b and ignore future transitions.
For nonterminals, the induction hypothesis identifies C1 child identifiers with
R_(h-1) blocks, up to a bijective renaming. Equality of each action's finite
distribution on (cost, child identifier) is therefore exactly equality of the
mass vectors above. Both also require the same b. This proves both directions
at depth h. The induction covers every finite h.

Numeric identifiers depend on state enumeration. The audit compares pairwise
equivalence relations at every depth, never bare identifiers across builds.
It also checks a case with equal depth-zero labels but different edge costs:
merging those states at depth one is wrong.

## Controller and response preservation

Fix a deterministic finite-state controller for each local observer. Its action
and next memory depend only on its own present observation and memory. Every
team must use the declared observation interface. The existing Experiment type
permits different observation maps in different teams; this compiler rejects
such an input instead of silently selecting one team's interface.

**Proposition.** Starting with the same local memories and a state mapped to its
C1 node at depth h, full-model execution and graph execution have the same law
of registered atom histories, joint action histories, local observations and
memory histories, final accumulated cost, elapsed time, and censoring status.

**Proof.** At a terminal state both stop immediately, with no further action,
memory update, or charge. At a depth-zero nonterminal both return a censored
zero-step continuation. Otherwise the node's equal local observations and the
fixed local memories produce the same joint action and memory update in both
executions. For that action, the graph edge distribution is exactly the
full-model pushforward onto (cost, child class). Apply the induction hypothesis
to each child with the updated memories, then prepend the common current atom,
observations, memories, and action, and add the edge cost. Aggregation combines
only identical observable traces. Mixtures over initial preparations preserve
the equality by linearity. No conditioning on completion is performed.

Consequently, worst-case cost across every positive-probability branch of every
input is preserved. Rejecting an entire over-budget team therefore preserves
the admitted catalogue. Every measurable predicate of the retained trace has
the same probability. Maximizing its input-weighted probability over one whole
team also preserves the value and supplies a full-model-checkable team witness.
Choosing a different team after learning the input would change that problem.

The query layer receives atom values for grading, but those values are not
passed to controller policies. A private bit registered as a grading atom is
not thereby made available to the controller. Original state names are absent
from response traces unless explicitly registered as atoms.

## Scope and limits

This construction is a **sufficient behavioral quotient**, potentially finer
than response equivalence for an installed catalogue. It checks every modeled
action, including actions no installed team chooses. Its base labels also keep
terminal observations even though the stopping semantics never act on them.
Thus different graph nodes do not automatically establish an observable
separation under the installed teams. The decoy control uses actual command
witnesses; the equivalent mimic is checked by full response-law equality.

The full path evaluator supplies the answer key. C1 is queried by forward
traversal using only the compiled graph. The independently constructed quotient
uses that same traversal engine; this is construction diversity, not an
independent query engine. A separate recursive memoized predictor runs on the
original state kernel. Its cache key includes world state, remaining horizon,
and local memories; it caches full suffix laws, including all costs. It never
prunes against a remaining budget, so that budget is not required in its key.
It is not yet a task-specific monitor baseline for the future pilot.

These implementations and the public controls have the same author. Reusing
the existing full evaluator and writing different algorithms improves error
detection; it does not create independent experimental validation.

No algorithm here learns a world model. The double-knockout diagnostic takes
two explicitly supplied response tables as its hypothesis class. It reports
the exact compatible range within that class, not a distribution-free causal
confidence interval. Full-model prediction and inference from limited evidence
remain separate questions.

## Invariance

A bijective renaming of states and commands, with the same transformation of
the kernel, controller tables, costs, preparations, and readout decoder,
preserves the mass equations. Hence it preserves the induced partition and,
after decoding command names, the response laws.

For the tested nuisance extension, replace each state s by (s,z), with z a fair
unobserved bit independent at preparation and refreshed independently on each
transition. All labels, observations, costs, terminal flags, and controller
tables factor through s. Summing over the next z gives the original transition
mass. Induction therefore gives the pullback of each original R_h relation and
the same response laws. This argument depends on independence and absence of
effects on cost or control; arbitrary added variables need not be irrelevant.

## What follows

There is no additional Omega-specific mathematical structure to benchmark in
C1 as currently specified. The remaining empirical question is whether an
implementation of this standard construction helps on an honestly chosen
workload, after charging for extraction, decoding, caches, and every attempted
query. The public controls establish readiness to investigate that question;
they cannot answer it. The separately frozen generated-world pilot remains
pending the generator, task grammar, practical baselines, compute limits, and
independent evaluator arrangement described in the parent protocol.
