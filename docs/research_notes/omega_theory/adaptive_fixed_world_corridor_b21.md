# Adaptive Fixed-World Corridor B2.1

Status: Lean policy-correspondence and strictness checkpoint / retained Python witness checkpoint / next theorem seam
Scope: finite unknown-but-fixed possibilistic ambiguity with observation-driven
model identification
Claim boundary: not a full fixed-world correspondence theorem, not stochastic,
not POMDP theory, not value, not agency, not valuerhood, not moral standing,
not Omega validation

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

The learnable, unlearnable, and fake-update phantom cases now also have Lean
strictness witnesses. The fake-update witness remains deliberately outside
`soundUpdate`: it formalizes what goes wrong when model elimination is
fabricated rather than certified.

## Interpretation: Certified Learning And Deception Surface

B2.1 is the first place where the corridor stack has an explicit epistemic
state. The remaining-model set is not just a diagnostic label; it is a register
field that the dynamics update.

That makes update soundness load-bearing:

```text
sound update:
  evidence never eliminates a true model that could have produced the observed
  successor.

fabricated update:
  the true model can be deleted from the register, making a false information
  state look safe.
```

The fake-update witness is therefore the learning-layer analogue of phantom
viability. Its structure is:

```text
true world:
  the model actually governing the run.

fake world:
  the model retained by the corrupted update.

trust-fake action:
  safe in the fake world, unsafe in the excluded true world.

phantom corridor:
  the lifted kernel admits the corrupted information state, but the action
  selected from that state fails in the true model.
```

This is an anti-deception certification surface in a narrow technical sense:
the theorem stack can distinguish sound evidence-processing from an update
that excludes the actual world and then certifies behavior only in the flattering
remaining model. It is not a general theory of deception, intent, adversarial
manipulation, or agency. It is the finite corridor anatomy of a corrupted
model-identification update.

The positive side is equally important. The extracted `adaptiveKernelPolicy`
is the repo's first certified learner surface in the fixed-point sense:

```text
it acts on information states;
it may probe;
it soundly updates the remaining model set;
it branches on learned information;
and it remains inside the adaptive corridor exactly where the kernel says a
guaranteeing policy exists.
```

This does not make the policy an agent, valuer, or moral subject. It is a toy
shielded learner: a small formal object that can learn which fixed model it is
in without using an update rule that lies to itself about the corridor.

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

## Landed Lean Core

The information-state lift has landed in:

```text
formal/lean/OmegaProper/Decision/AdaptiveFixedWorld.lean
```

It defines:

```text
InfoState:
  current state plus remaining possible models.

soundUpdate:
  keeps exactly the remaining models that can produce the observed successor.

liftedDecision:
  ordinary DecisionStructure over InfoState.

liftedAllowed:
  allowed at the concrete state and enabled in every remaining model.

AdaptiveKernel:
  RobustCorridor(liftedDecision, liftedAllowed, liftedRequirement).
```

The core reduction is definitionally explicit:

```text
AdaptiveKernel = RobustCorridor of the lifted information-state system.
```

The Lean file also proves the first update-soundness lemma:

```text
if a model was possible and produced the observed successor,
then soundUpdate keeps that model possible.
```

It also proves the first lifted-step invariants:

```text
liftedStep_remaining_sub:
  a lifted step never invents a model that was not previously possible.

liftedStep_remaining_nonempty:
  every lifted step leaves at least one possible model.

liftedStep_possible_iff_soundUpdate:
  the next possible-model predicate is exactly soundUpdate for the observed
  successor.
```

The finite play-correspondence lemmas now landed as well:

```text
LiftedReach:
  finite policy-following reachability in the lifted information-state system.

FixedModelReach:
  finite reachability through concrete steps of one fixed model.

SoundFixedWorldReach:
  finite reach generated by one actual model with sound information updates.

liftedReach_remaining_sub:
  finite lifted reach never invents models.

soundFixedWorldReach_preserves_trueModel:
  an initially possible actual model remains possible after finite sound
  fixed-world reach.

soundFixedWorldReach_to_liftedReach:
  sound fixed-world reach induces lifted reach.

liftedStep_terminalModel_realizes_step:
  any model possible after a lifted step realizes that observed transition.

liftedReach_terminalModel_realizes_fixedModelReach:
  if model i remains possible at the end of a finite lifted reach, then i
  realizes the concrete state transitions of that reach.
```

The finite-model stabilization layer also landed:

```text
possibleFinset:
  a finite view of an InfoState's remaining possible models, without changing
  the core predicate representation.

descending_nonempty_finset_has_persistent_member:
  a descending nonempty sequence of finite subsets of a finite model type has
  one model that remains present forever.

InfiniteLiftedTrace:
  an infinite lifted trace with explicitly recorded actions.

infiniteLiftedTrace_has_fixedModelRealizer:
  every infinite lifted trace whose information states remain nonempty has one
  fixed model that realizes every observed concrete transition.
```

The policy-level fixed-point correspondence has also landed:

```text
AdaptivePolicy:
  stationary policy over information states.

AdaptivePolicyKernel:
  closed-loop guarantee kernel for one adaptive policy on the lifted system.

AdaptivePolicyGuarantees:
  fixed-point reading of that policy guaranteeing from an information state.

exists_adaptivePolicyGuarantees_iff_adaptiveKernel:
  some stationary information-state policy guarantees exactly from
  AdaptiveKernel states.
```

The finite-bad-prefix assembly has also landed:

```text
FiniteAdaptivePolicyTrace:
  finite policy-following trace in the lifted information-state system.

AdaptiveBadInfo:
  outside lifted constraint, lifted requirement, or lifted allowedness.

AdaptiveDeadlocked:
  no lifted successor exists for the policy action.

BadFiniteAdaptiveTrace:
  bad information state along the trace or deadlock at the endpoint.

AdaptiveTrajectoryGuarantees:
  no finite lifted bad prefix.

adaptivePolicyGuarantee_iff_adaptiveTrajectoryGuarantees:
  fixed-point policy guarantee iff finite-bad-prefix guarantee.

exists_adaptiveTrajectoryGuarantees_iff_adaptiveKernel:
  some stationary adaptive policy has no finite lifted bad prefixes exactly
  from AdaptiveKernel states.

adaptivePolicyKernel_soundFixedWorldReach_closed:
  sound finite fixed-world reach from a policy-kernel state remains inside the
  policy kernel.
```

This is still below a full trajectory/maximal fixed-world correspondence
theorem: it proves the finite-refutation safety semantics over the lifted
information-state system, and the fixed-model realizer extracts one concrete
model for nonempty infinite lifted traces. It does not yet package maximal
fixed-world trajectory semantics as a standalone object.

## Assembly Status

The landed finite-bad-prefix theorem gives the current clean statement:

```text
There exists a stationary adaptive policy with no finite lifted bad prefixes
iff
the initial information state lies in AdaptiveKernel.
```

This is an adaptive safety-game / information-state theorem. It is not the same
as the switching RVK theorem.

The remaining optional packaging target is:

```text
package a trajectory-level/maximal fixed-world persistence semantics and prove
that it matches the finite-refutation/lifted-kernel theorem.
```

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

## Landed Strictness Witnesses

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

The Lean witness file is:

```text
formal/lean/OmegaProper/Decision/AdaptiveFixedWorldExamples.lean
```

It proves:

```text
W_learnable_adaptive_strictness:
  the concrete start is outside switching RVK while the information-state start
  is inside AdaptiveKernel.

W_unlearnable_adaptive_exclusion:
  unsafe/unavailable identification does not put the full unknown information
  state inside AdaptiveKernel.

W_fake_update_phantom_corridor:
  a fake information state that has dropped the true model can lie inside
  AdaptiveKernel, while the action selected for the fake remaining model exits
  the declared constraint in the excluded true model.
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
the full fixed-world iff theorem is proved;
the trajectory/maximal fixed-world semantics is fully packaged;
fake-update is part of the sound lifted update relation;
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
