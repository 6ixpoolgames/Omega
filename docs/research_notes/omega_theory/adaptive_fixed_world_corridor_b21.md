# Adaptive Fixed-World Corridor B2.1

Status: roadmap note / retained Python witness checkpoint / next theorem seam
Scope: finite unknown-but-fixed possibilistic ambiguity with observation-driven
model identification
Claim boundary: not landed Lean, not a fixed-world correspondence theorem, not
stochastic, not POMDP theory, not value, not agency, not valuerhood, not moral
standing, not Omega validation

## Purpose

The switching robust corridor is conservative because it treats every declared
model's successors as live at every step. That is correct for stepwise
adversarial ambiguity.

Unknown-but-fixed ambiguity is different:

```text
one model is actual for the whole run;
the controller may learn which model is actual from observations or transitions;
safe probing can refine the remaining model set.
```

B2.1 should define the corridor for this learnable case.

## Retained Pilot

The first finite Python witness pack has landed:

```text
omega/adapters/finite_relational/adaptive_fixed_world_corridor.py
omega/validation/finite_relational_adaptive_fixed_world_corridor.py
tests/test_adaptive_fixed_world_corridor.py
docs/research_notes/validation_results/finite_relational_adaptive_fixed_world_corridor_b21/20260705_175110/
```

The retained run has status `PASS` over three cases:

```text
learnable_ambiguity:
  start notin SwitchingRVK({m0,m1});
  (start, {m0,m1}) in AdaptiveKernel;
  (start, {m0,m1}) notin FrozenKnowledgeKernel;
  probe is epistemically load-bearing.

unlearnable_ambiguity:
  each singleton model admits the start;
  the full unknown model set does not;
  no safe shared identification action expands the corridor.

fake_update_phantom_corridor:
  a fabricating update drops the true model;
  the fake lifted kernel admits an inconsistent information state;
  the policy selected for the fake remaining model fails in the excluded true model.
```

The sound update rule has zero truth-preservation failures across the retained
cases:

```text
if i* remains possible and i* can produce the observed successor,
then i* remains possible after sound_update.
```

This pilot is not a theorem. It fixes the finite witness geometry before the
Lean correspondence theorem is attempted.

## Core Object

Let:

```text
M:
  finite nonempty model set.

X:
  finite state set.

A:
  finite action set.

Step_m x a y:
  model-indexed transition relation.

Obs:
  observation record from a transition or state.

K / Requirement:
  declared constraint and local requirement surfaces.
```

The information state is:

```text
InfoState := X x Set M
```

where the second component is the currently possible set of fixed models.

An update has the shape:

```text
update(models_remaining, x, a, observed_successor_or_output)
  =
{ m in models_remaining :
    Step_m x a y and observation_m(x,a,y) matches the observed record }
```

The adaptive predecessor should require one action that:

```text
is allowed at the current state;
is enabled in every remaining model;
keeps every possible observed successor inside the adaptive candidate set after
updating the remaining model set.
```

Then:

```text
AdaptiveKernel = gfp AdaptivePre
```

## Expected Theorem Shape

The target theorem is:

```text
There exists a policy that guarantees persistence in every unknown-but-fixed
model consistent with the initial information state
iff
the initial information state lies in AdaptiveKernel.
```

This is an adaptive safety-game / information-state theorem. It is not the same
as the switching RVK theorem.

## Relation To Existing Corridors

The triad is:

```text
KnownModelKernel(m):
  model is known.

SwitchingRVK(M):
  model may vary adversarially at each step.

AdaptiveKernel(x, M_remaining):
  model is fixed but initially unknown and learnable.
```

Expected relations:

```text
SwitchingRVK(M) gives a conservative lower bound for adaptive fixed-world
persistence.

AdaptiveKernel can strictly exceed SwitchingRVK.

When M_remaining is a singleton, AdaptiveKernel reduces to the known-model
kernel.
```

## Strictness Witness Target

The first retained witness is tiny:

```text
initial state s;
two models m0, m1;
one safe probe action p;
probe successor reveals whether m0 or m1 is actual;
after the reveal, action a0 is safe in m0 and action a1 is safe in m1.
```

The same state satisfies in the retained pilot:

```text
s notin SwitchingRVK({m0,m1})
(s, {m0,m1}) in AdaptiveKernel
```

Reading:

```text
some ambiguity is destructive;
some ambiguity is learnable.
```

## Certification Surface

The update rule is not free. Omega should require:

```text
model-identification soundness:
  observations used to remove models must reflect concrete distinctions.

no fabricated learning:
  a presentation may not make the model set appear smaller unless the
  corresponding concrete transition/output evidence supports it.

no hidden loss:
  a presentation may not hide model distinctions required for safe branching.
```

This is the project-specific bridge from classical adaptive safety games to the
existing presentation-soundness discipline.

The fake-update witness is the learning-layer analogue of phantom viability:
fabricated model elimination can make the corridor appear wider by removing the
world that would refute the action. Lossy updates that keep extra models are
expected to be conservative; over-eliminating updates are unsafe.

## Nonclaims

This note does not claim:

```text
the adaptive kernel has landed in Lean;
the fixed-world theorem is proved;
the observation interface is empirically valid;
all uncertainty is learnable;
learning is value;
agency;
identity;
valuerhood;
moral standing;
Omega validation.
```

## Public Compression

Switching ambiguity contracts the corridor. Fixed-world ambiguity can sometimes
be learned, refining the corridor instead. B2.1 is the information-state
kernel for that distinction.
