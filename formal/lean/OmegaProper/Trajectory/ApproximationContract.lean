/-!
OmegaProper.Trajectory.ApproximationContract

Generic sound/complete approximation contracts.

This is the abstract-interpretation-shaped core beneath the current profile
abstraction layer: abstract claims are sound when they imply exact claims, and
complete when all exact claims are represented abstractly.
-/

namespace OmegaProper
namespace Trajectory
namespace ApproximationContract

universe u

/-- An abstract claim relation is sound for an exact claim relation. -/
def SoundApprox
    {I : Type u}
    (Exact Abstract : I -> Prop) : Prop :=
  forall i, Abstract i -> Exact i

/-- An abstract claim relation is complete for an exact claim relation. -/
def CompleteApprox
    {I : Type u}
    (Exact Abstract : I -> Prop) : Prop :=
  forall i, Exact i -> Abstract i

/-- Exactness is soundness plus completeness. -/
def ExactApprox
    {I : Type u}
    (Exact Abstract : I -> Prop) : Prop :=
  SoundApprox Exact Abstract /\ CompleteApprox Exact Abstract

theorem soundApprox_exact_of_abstract
    {I : Type u}
    {Exact Abstract : I -> Prop}
    (hSound : SoundApprox Exact Abstract)
    {i : I}
    (hAbs : Abstract i) :
    Exact i := by
  exact hSound i hAbs

theorem completeApprox_abstract_of_exact
    {I : Type u}
    {Exact Abstract : I -> Prop}
    (hComplete : CompleteApprox Exact Abstract)
    {i : I}
    (hExact : Exact i) :
    Abstract i := by
  exact hComplete i hExact

theorem exactApprox_sound
    {I : Type u}
    {Exact Abstract : I -> Prop}
    (h : ExactApprox Exact Abstract) :
    SoundApprox Exact Abstract := by
  exact h.left

theorem exactApprox_complete
    {I : Type u}
    {Exact Abstract : I -> Prop}
    (h : ExactApprox Exact Abstract) :
    CompleteApprox Exact Abstract := by
  exact h.right

/-- The empty abstract claim relation is always sound. -/
theorem empty_soundApprox
    {I : Type u}
    (Exact : I -> Prop) :
    SoundApprox Exact (fun _ => False) := by
  intro _i h
  cases h

/-- The empty abstract relation is incomplete whenever some exact fact exists. -/
theorem empty_not_completeApprox_of_exact
    {I : Type u}
    {Exact : I -> Prop}
    {i : I}
    (hExact : Exact i) :
    Not (CompleteApprox Exact (fun _ => False)) := by
  intro hComplete
  exact hComplete i hExact

/-- The total abstract claim relation is always complete. -/
theorem total_completeApprox
    {I : Type u}
    (Exact : I -> Prop) :
    CompleteApprox Exact (fun _ => True) := by
  intro _i _hExact
  trivial

/-- The total abstract relation is unsound whenever some claimed fact is false. -/
theorem total_not_soundApprox_of_not_exact
    {I : Type u}
    {Exact : I -> Prop}
    {i : I}
    (hNotExact : Not (Exact i)) :
    Not (SoundApprox Exact (fun _ => True)) := by
  intro hSound
  exact hNotExact (hSound i trivial)

end ApproximationContract
end Trajectory
end OmegaProper
