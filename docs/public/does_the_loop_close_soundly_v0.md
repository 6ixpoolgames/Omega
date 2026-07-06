# Does The Loop Close Soundly? v0

Status: public-facing bridge note
Scope: observer theory, NKS-adjacent bounded computation, and Omega's sound-update guardrail
Claim boundary: not consciousness, not agency, not selfhood, not value, not moral standing, not terminal metaphysics, not Omega validation

I have long been sympathetic to the New Kind of Science style of question:
what happens when simple bounded systems iterate, compress, observe, and act
inside a world they cannot fully survey?

Observer-theory language asks a nearby question:

```text
Where does the loop close?
```

Omega's answer is deliberately stricter:

```text
The important question is not only whether the loop closes.
It is whether the loop closes soundly.
```

## The Basic Move

A bounded observer does not see the world directly. It lives behind a boundary,
with a finite budget, using compressed presentations of what matters for its
future action.

That is not a defect; it is the normal condition of embedded computation.
But it creates a certification problem.

```text
boundedness forces compression;
compression forces presentation;
presentation requires soundness.
```

An observation/update/action loop can close in many ways. Some loops are
instruments: they sample and report. Some loops are controllers: observation
changes internal state, internal state changes action, and action changes what
will be observed next.

But loop closure alone is not enough. A loop can close falsely.

## Phantom Closure

Omega's adaptive-corridor layer studies finite worlds where the real world is
unknown but fixed. A learner keeps a set of possible models and updates that
set as evidence arrives.

The good update rule has a simple discipline:

```text
do not eliminate the true model when the true model could have produced the
evidence observed.
```

If that discipline fails, the loop may become confidently wrong. The update
can delete the actual world, keep only a flattering false model, and then choose
an action that is safe only in the false information state.

That is phantom closure:

```text
the loop closes;
the certification route closes;
but the closure depends on deleting the world that would refute it.
```

This is why Omega treats update soundness as part of the safety object, not as
an afterthought.

## Relation To NKS-Style Intuition

NKS makes it natural to take simple iterative systems seriously. Tiny rules can
generate rich behavior, and the observer's computational limits matter.

Omega accepts that lesson but adds a guardrail:

```text
rich generated behavior is not automatically a trustworthy map;
closed-loop behavior is not automatically agency;
observer-relative compression is not automatically sound.
```

The missing layer is certification. If a compressed interface is used to
justify action, it must preserve the consequence-bearing distinctions that the
justification relies on.

## The Current Omega Reading

The project currently has three relevant formal surfaces:

```text
sound update:
  a learner's information state must not eliminate live models without
  evidence that certifies the elimination.

recovery-aware gates:
  an action is rejected when it causes declared nonrecoverable loss under the
  true recovery frame.

reflection:
  if a believed recovery frame reflects into the true frame, believed licenses
  remain true; without reflection, phantom licenses can appear.
```

So the public compression is:

```text
Observer theory asks whether the loop closes.
Omega asks whether the loop closes soundly.
```

The difference matters because a bad loop can be worse than no loop. It can
turn bounded compression into counterfeit certainty.

## What This Does Not Claim

This note does not claim that loop closure is consciousness, agency, value,
selfhood, moral standing, or validation of Omega. It does not import terminal
metaphysics.

It is a narrower point:

```text
an observer/action loop is admissible only if its update rule preserves the
live consequence-bearing distinctions needed for the decisions it certifies.
```

That is where observer theory and Omega currently meet.
