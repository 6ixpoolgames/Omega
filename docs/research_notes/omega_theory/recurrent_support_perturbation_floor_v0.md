# Recurrent Support Perturbation Floor v0

Status: formal checkpoint note
Scope: finite local perturbation discipline for recurrently carried consequence distinctions
Claim boundary: not agency, not identity, not deformer theory, not value, not Omega validation

## Thesis

Layer A now has a first finite local perturbation calculus for recurrently
carried consequence distinctions: support, loss, preservation, restoration, and
rerouting.

The word "local" matters. These are pair-relative, support-relative, finite
witnesses and transfer contracts. They do not prove a global theory of
recoverability, identity, agency, valuerhood, or Omega proper.

The core lesson is:

```text
endpoint viability is not enough;
forward reachability is not enough;
recurrently carrying a consequence distinction needs return structure
or replacement internal paths.
```

## Formal ingredients

The checkpoint is distributed across the following Lean modules:

```text
OmegaProper/Trajectory/SupportUnderPerturbation.lean
OmegaProper/Trajectory/RecurrentSupportRobustness.lean
OmegaProper/Trajectory/IrreversibleRecurrentSupportLoss.lean
OmegaProper/Trajectory/RecurrentSupportTransfer.lean
OmegaProper/Trajectory/RecurrentSupportRestoration.lean
OmegaProper/Trajectory/RecurrentSupportPathTransfer.lean
```

The supporting stack is:

```text
consequence-bearing distinction;
reachability and viability;
recurrent viable class;
support carrying a merge-separated pair;
loss when recurrence is broken;
positive transfer under explicit contracts;
restoration when recurrence is repaired;
path-level transfer when old edges are replaced by new internal paths.
```

## What the loss witness shows

The finite one-way dynamics witness shows that weaker facts can survive while
recurrent carrying fails.

In the broken cycle:

```text
the endpoints remain viable;
the forward path remains;
the declared distinction is still present as endpoints;
but the return structure is gone.
```

Therefore the support no longer recurrently carries the consequence
distinction. This is the important guardrail:

```text
viability of endpoints plus one-way reachability does not imply
recurrent support carrying.
```

This is a small finite theorem-level version of the broader warning that a
system can look safe under weak continuation summaries while losing the
structure that carried a declared distinction.

## What the transfer contracts show

`RecurrentSupportTransfer` gives an edge-level sufficient contract. If changed
dynamics preserve safety on the support, introduce no new exits from the
declared support, and preserve the original internal support edges, then the
recurrent support carrying transfers.

This is intentionally conservative. It is a sufficient condition, not a
necessary condition.

`RecurrentSupportPathTransfer` weakens the brittle edge requirement into a
path-replacement contract. The old internal edge need not literally survive if
the changed dynamics provide a replacement internal path. This is the first
formal rerouting discipline in the recurrent-support stack.

## What restoration means here

The restoration witness completes the small perturbation triptych:

```text
full cycle:
  recurrently carries the distinction;

broken one-way cycle:
  endpoints and forward reachability survive,
  but recurrent carrying is lost;

repaired cycle:
  the return structure is restored,
  and recurrent carrying returns.
```

This should not be read as identity restoration, object persistence, or
selfhood. It says only that a declared support again satisfies the explicit
recurrent-carrying predicate after the relevant recurrence is repaired.

## Strict viability is still not solved

This layer does not solve the general problem that strict viability can be too
strong, too brittle, or too local. It begins a repair route by asking more
precise questions:

```text
Does the declared support still recurrently carry the declared distinction?
If not, can the carrying be restored by repairing return structure?
If exact edges are lost, can internal replacement paths preserve recurrence?
Which explicit transfer obligations are doing the work?
```

This avoids saying "the same thing persisted." The claims are about declared
supports, declared distinctions, and explicit recurrence or rerouting
contracts.

## Same-support limitation

The current positive transfer results are same-declared-support results. They
show that a support can retain or regain recurrent carrying under changes to
dynamics when explicit support-relative contracts hold.

They do not yet cover:

```text
support extension, where C transfers into a larger D;
support lineage, where C hands off to a distinct D;
successor distinctions, where the exact pair is not preserved but a translated
  distinction is;
joint recurrent support across multiple coupled supports.
```

Those are the next natural extensions.

## Gradient Ethics bridge

For the Gradient Ethics program, the checkpoint is useful because it separates
weak reachability from recurrent carrying.

If alignment is eventually framed as staying inside a viability corridor, this
layer says the corridor cannot be checked only by endpoint viability or forward
reachability. Some consequence-bearing distinctions require recurrent return
structure or admissible rerouting. A presentation or perturbation that hides
the loss of that return structure can make the corridor look intact while the
carrying structure has already failed.

The current result is still local and finite, but it is the first clean bridge
from:

```text
this distinction matters under consequence
```

to:

```text
this support can carry, lose, restore, or reroute that mattering across
recurrent continuation.
```

## Next targets

The nearest extensions should proceed in this order:

1. Support extension:
   show when a support `C` transfers into a larger support `D`.

2. Support lineage:
   show when one declared support hands off recurrent carrying to another.

3. Successor distinctions:
   show when the exact same pair is not preserved, but a translated
   consequence distinction is.

4. Perturbation budget:
   measure the minimum edge or path removals needed to destroy recurrent
   carrying.

5. Joint recurrent support:
   ask when multiple recurrent supports can remain viable and carrying
   together.

6. Parameterized cycles and rings:
   generalize the two-state cycle witnesses to finite families.

## Earned milestone sentence

The safe summary is:

```text
Layer A now has a first finite local perturbation calculus for recurrently
carried consequence distinctions: support, loss, preservation, restoration,
and rerouting.
```

Anything stronger should remain future work.
