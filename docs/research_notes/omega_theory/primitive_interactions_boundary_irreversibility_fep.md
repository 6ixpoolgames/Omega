# Primitive Interactions, Boundary, Irreversibility, and FEP

Theory note on how the primitive stack may need to be sharpened for reachable-futures substrate design

## Status

This is a working theory note.

It records a conceptual update that emerged during the RFS0 strict reachable-futures reset.

The current empirical issue is that strict viability remains too easy for some controls to satisfy. The first RFS0 strict small smoke showed that exact finite reachability, finite-horizon viability kernels, capture basins, perturbation recovery, and future-space contraction are computable and cheap. It also showed that a sparse strict viable object can survive in some structured regimes. But shuffled-admissibility and random-edge controls remained too strong, meaning the current strict viability filter is not yet discriminating enough.

The likely missing ingredient is cost.

> Viability without a cost of maintenance is too weak. Persistent distinction should not be free.

This note develops that point from the primitive stack and connects it to FEP/ECHO/TELOS-style thermodynamic boundedness.

## Current problem

The RFS0 strict filter currently asks whether a state has reachable futures that remain admissible, recoverable, and non-collapsing under a formal filter.

That is already better than raw reachability.

But it is still mostly logical/topological viability:

```text
Can the state continue?
Can it return to K_strict?
Does it retain reachable futures?
```

It is not yet energetic or metabolic viability:

```text
Can the state afford to continue?
Can it pay the cost of maintaining its boundary?
Can it recover without exhausting its slack?
Does its organization persist under dissipation?
```

This matters because if continuation is cheap, too many structures remain viable. Random or shuffled controls can accidentally satisfy the filter because the substrate permits persistence without requiring the structure to pay for itself.

The next substrate extension should therefore make viable persistence costed.

## Does this change the three primitives?

Short answer:

```text
No, but it changes what the primitives must compose into before they become empirically useful.
```

The three primitive terms remain:

```text
distinction
asymmetry
relation
```

But the current work suggests that the empirical substrate needs a fourth design condition:

```text
boundedness / cost
```

This should not yet be promoted to a primitive on the same level. It is better understood as a physical admissibility condition: persistent relations must operate under finite slack, dissipation, and irreversible loss.

The three primitives give the logical floor for future structure. Cost makes future structure selective.

```text
distinction:
  differences can exist

relation:
  differences can propagate across transformation

asymmetry:
  related differences can have non-equivalent future consequences

boundedness / cost:
  maintaining, transmitting, repairing, or reversing those differences consumes limited slack
```

## Primitive interactions

A useful way to sharpen the stack is to ask what happens when the primitives are applied to each other.

This should be treated as provisional algebra, not final metaphysics.

### Relation applied to distinction

```text
relation(distinction)
  -> propagation / memory / causal continuity of difference
```

A distinction by itself is just a difference. A relation carries that difference across transformation. This is the minimal form of memory or persistence:

```text
A_t differs from B_t
A_t is causally related to A_{t+1}
therefore the A/B distinction can propagate into the future
```

Without relation, distinctions do not become histories.

### Asymmetry applied to distinction

```text
asymmetry(distinction)
  -> consequential distinction / selection-relevant difference
```

A distinction matters dynamically when the distinguished alternatives lead to non-equivalent consequences.

```text
A and B are different.
If both lead to the same future possibility space, the distinction is dynamically inert.
If A opens futures that B closes, the distinction is consequential.
```

This is where difference becomes selection-relevant.

### Asymmetry applied to relation

```text
asymmetry(relation)
  -> directionality / channeled causality / irreversible tendency
```

Relation is causal connection. But causal connections need not be symmetric.

A relation can be reversible:

```text
A -> B
B -> A
```

or directionally asymmetric:

```text
A -> B
B -/-> A
```

Asymmetry applied to relation gives channeled causality: causal flow can have preferred directions, losses, costs, or one-way transformations.

With boundedness, this becomes irreversibility:

```text
irreversibility = asymmetric relation under bounded recovery
```

A relation is irreversible relative to a system when reversal is impossible or unaffordable within that system's resource, time, or transformation bounds.

### Distinction applied to relation

```text
distinction(relation)
  -> boundary / interface / Markov-blanket-like separation
```

A boundary is not merely a line between things. It is a distinction over relations.

Inside the boundary:

```text
relations are dense, mutually constraining, or self-maintaining
```

Across the boundary:

```text
relations are filtered, mediated, or selectively coupled
```

Outside the boundary:

```text
relations do not participate in the same organized causal continuity
```

This is the bridge to Markov blanket language: a boundary mediates internal/external coupling. In FEP terms, a self-organizing system persists by maintaining such a boundary-like separation while acting through it.

## Boundary as maintained distinction over relations

The key move is:

> Boundary is distinction over relation.

A boundary says not merely that two regions differ, but that causal relations are organized differently within, across, and outside that distinction.

This matters because a value-bearing or agent-like process is not just a state. It is a bounded organization of relations that persists through change.

The boundary is therefore the first place where FEP-style thinking attaches to the primitive stack.

A persistent system must preserve a distinction between itself and its environment. But that distinction is not free. It must be maintained against dissipation, perturbation, and mixing.

Thus:

```text
boundary:
  maintained distinction over relations

metabolic cost:
  cost of preserving that relational distinction against dissipation

repair:
  cost of restoring that distinction after perturbation

irreversibility:
  losses that cannot be restored within the available budget/horizon
```

## Irreversibility: primitive or derived?

Irreversibility is probably not a primitive in the same sense as distinction, asymmetry, and relation.

Reason:

```text
relation can be reversible or irreversible
```

So relation is more general.

Irreversibility is better treated as a physically loaded form of asymmetric relation:

```text
relation:
  causal continuity between distinctions

asymmetric relation:
  causal continuity with non-equivalent direction or consequence

costed relation:
  causal continuity whose maintenance, reversal, or repair consumes bounded slack

irreversible relation:
  costed relation whose reversal is impossible or unavailable within the horizon
```

This hierarchy preserves minimality while explaining why irreversibility is empirically essential.

It is not the first primitive, but it may be the first physical selector.

## How FEP enters

The Free Energy Principle is relevant here not merely as a slogan about minimizing surprise, but as a substrate principle for bounded persistence.

For the current project, the FEP-relevant idea is:

> A persistent system is a bounded pattern of relations that must maintain its boundary against dissipative dynamics.

In primitive-interaction terms:

```text
distinction(relation):
  boundary / Markov-blanket-like separation

asymmetry(relation):
  dissipative, directional, costly causal flow

relation(distinction):
  persistence of organized difference across time

boundedness:
  finite slack available to maintain, repair, or reverse relational loss
```

A system persists when it can keep its internal/external distinction within viable bounds by spending work, using repair/re-entry pathways, and avoiding irreversible collapse.

This gives a tighter bridge from the primitive stack to ECHO/TELOS:

```text
ECHO:
  sustained information / organized structure has a thermodynamic feasibility envelope

TELOS:
  persistence is dynamic, not free; it must continue against degradation

FEP:
  bounded systems maintain their organization by acting through a boundary under uncertainty and dissipation

RFS0-E:
  model this minimally as costed viable reachability
```

## Implication for viability

The current viability concept must be sharpened.

Old RFS0 viability:

```text
A future is viable if it remains reachable and admissible.
```

Thermodynamically bounded viability:

```text
A future is viable if it remains reachable and admissible after paying the cost
of maintaining the distinctions and relations that make it a continuing system.
```

This means a viable state is not merely one with outgoing transitions.

It must also have enough slack to:

```text
maintain boundary/integrity
perform transformations
repair perturbations
avoid irreversible loss
preserve future reachability without exhausting itself
```

This may explain why prior filters were too weak. They represented reachability and some recovery, but they did not sufficiently represent the cost of maintaining the boundary conditions that make recovery meaningful.

## Implication for asymmetry

Asymmetry becomes much sharper under cost.

Without cost:

```text
many actions differ, but not enough to filter futures strongly
```

With cost:

```text
some actions expand futures but spend too much slack
some preserve slack but shrink option-space
some repair damage but consume future budget
some create local persistence by exporting cost elsewhere
some maintain boundary cheaply
some allow boundary decay and require expensive repair later
```

Cost converts path non-equivalence into hard viability pressure.

> Cost makes asymmetry bite.

## Implication for pseudo-Omega / capture regimes

Pseudo-Omega-like behavior becomes clearer when cost is represented.

A locally viable / globally degrading capture regime is often a structure that preserves itself by exporting cost, consuming shared slack, or degrading another system's boundary/recovery conditions.

In a toy substrate this could look like:

```text
A remains viable by consuming shared free-energy budget
A repairs its boundary by increasing B's disorder/debt
A expands its reachable futures while reducing the total viable future budget
A preserves local integrity while closing recovery routes for other components
```

Without cost accounting, these can look like ordinary reachability changes.

With cost accounting, they become visible as local viability purchased by broader loss.

## Implication for RFS0-E

The next substrate extension should be costed viability.

Working title:

```text
RFS0-E: Energetic / Metabolic Boundedness Smoke
```

Core question:

```text
Does adding a naive energy / negentropy budget make strict viability more
discriminating and reduce random/shuffled control leakage?
```

### Minimal cost model

Start with the simplest possible baseline:

```text
state includes energy/slack E

each transition costs c_step

E_{t+1} = E_t - c_step

K_strict_energy = K_strict + E >= 0
```

This turns viability from:

```text
can I continue?
```

into:

```text
can I continue for H steps within budget?
```

This is not a full FEP model. It is a baseline metabolic tax.

### Better cost ladder

RFS0-E should ideally be designed as a ladder:

```text
E0: uniform step cost
  every transition costs the same amount

E1: action cost
  different transformation classes have different costs

E2: maintenance cost
  boundary/integrity decays unless paid for

E3: repair cost
  recovery after perturbation consumes budget

E4: entropy/debt cost
  cheap actions create future maintenance burden

E5: boundary / blanket cost
  preserving system/environment distinction consumes slack
```

Do not implement all at once unless cheap. The conceptual design should leave room for the ladder.

### Expected effects

Predictions:

```text
uniform step cost:
  should reduce overly permissive viability and some shuffled-control leakage

maintenance / repair cost:
  should improve separation more strongly, because random edges will not reliably preserve the budget-integrity loop

boundary cost:
  should make recoverability more meaningful by tying it to preservation of self/environment distinction
```

### Strict viability with cost

A costed strict set might require:

```text
K_strict_costed =
  K_strict
  + energy/slack nonnegative
  + boundary/integrity above threshold
  + maintenance debt bounded
  + recovery path can be paid for
```

Recovery becomes:

```text
Recoverable_strict_costed(x) =
  perturb(x) can reach K_strict_costed within Hr
  without exhausting budget or crossing entropy/debt limits
```

## Revised primitive stack

A more complete working stack:

```text
1. Distinction
   Difference can exist.

2. Relation
   Differences can be causally connected across transformation.

3. Asymmetry
   Related differences can have non-equivalent future consequences.

4. Boundary
   A distinction over relations: inside / outside / across.

5. Boundedness / cost
   Maintaining boundary and reversing losses consumes limited slack.

6. Irreversibility
   Asymmetric relation under bounded recovery.

7. Viable persistence
   A bounded relational organization maintains itself through irreversible flow.

8. Recoverability
   The organization can return to viability after perturbation.

9. Compatibility
   Multiple viable organizations preserve rather than erase one another's futures.
```

This does not replace the original primitive story. It extends it into the physical substrate needed for empirical testing.

## Caution

This note should not be read as final ontology.

Open questions:

```text
Is boundedness/cost a derived physical condition or a fourth primitive?
Is irreversibility merely asymmetric relation under bounds, or should it be promoted?
How close should the RFS substrate be to formal FEP rather than a simple costed transition system?
How should boundary be represented without smuggling agency into the substrate?
```

For now, the conservative position is:

```text
irreversibility is not minimal;
it is the thermodynamic sharpening of asymmetry inside relation.

boundary is distinction over relation;
FEP enters when that boundary must be maintained under dissipative flow.
```

## Bottom line

The primitive stack becomes empirically useful only when relation is costed.

Distinction and relation generate possible propagation. Asymmetry makes propagated distinctions consequential. Boundary distinguishes which relations belong to a persistent organization. Cost and irreversibility make persistence selective.

For reachable-futures testing, this suggests the next substrate should not merely ask what futures remain reachable, but what futures remain reachable after paying the metabolic cost of maintaining the boundary and repairing perturbation.
