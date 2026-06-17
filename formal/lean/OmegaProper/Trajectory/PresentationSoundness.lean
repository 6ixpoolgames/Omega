/-!
OmegaProper.Trajectory.PresentationSoundness

Generic presentation soundness as forbidden-merge avoidance.

Many local definitions in the trajectory stack have this same shape: a
presentation, quotient, summary, or coarse view is sound when its kernel does
not identify pairs that some declared relation marks as forbidden to merge.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationSoundness

universe u v

/-- The kernel relation of a presentation-like map. -/
def Kernel {X : Type u} {Q : Type v} (present : X -> Q) :
    X -> X -> Prop :=
  fun x y => present x = present y

/-- A presentation erases a pair when both elements land in the same fiber. -/
def PairErased
    {X : Type u}
    {Q : Type v}
    (present : X -> Q)
    (x y : X) : Prop :=
  present x = present y

/--
Generic soundness: the presentation kernel is disjoint from a declared
forbidden-merge relation.
-/
def SoundPresentationBy
    {X : Type u}
    {Q : Type v}
    (Forbidden : X -> X -> Prop)
    (present : X -> Q) : Prop :=
  forall x y, present x = present y -> Not (Forbidden x y)

/-- A pair remains visible under a presentation when it is not erased. -/
def PairVisible
    {X : Type u}
    {Q : Type v}
    (present : X -> Q)
    (x y : X) : Prop :=
  Not (PairErased present x y)

/-- A forbidden-pair relation has at least one forbidden pair. -/
def HasForbiddenPair
    {X : Type u}
    (Forbidden : X -> X -> Prop) : Prop :=
  exists x y, Forbidden x y

/--
Kernel-containment spelling: every identified pair avoids the forbidden
relation.
-/
def KernelAvoids
    {X : Type u}
    {Q : Type v}
    (Forbidden : X -> X -> Prop)
    (present : X -> Q) : Prop :=
  forall x y, Kernel present x y -> Not (Forbidden x y)

theorem soundPresentationBy_iff_kernelAvoids
    {X : Type u}
    {Q : Type v}
    (Forbidden : X -> X -> Prop)
    (present : X -> Q) :
    SoundPresentationBy Forbidden present <->
      KernelAvoids Forbidden present := by
  rfl

theorem soundPresentationBy_blocks_forbidden_kernel
    {X : Type u}
    {Q : Type v}
    {Forbidden : X -> X -> Prop}
    {present : X -> Q}
    (hSound : SoundPresentationBy Forbidden present)
    {x y : X}
    (hForbidden : Forbidden x y) :
    Not (present x = present y) := by
  intro hErased
  exact hSound x y hErased hForbidden

theorem forbidden_kernel_blocks_soundPresentationBy
    {X : Type u}
    {Q : Type v}
    {Forbidden : X -> X -> Prop}
    {present : X -> Q}
    {x y : X}
    (hErased : present x = present y)
    (hForbidden : Forbidden x y) :
    Not (SoundPresentationBy Forbidden present) := by
  intro hSound
  exact soundPresentationBy_blocks_forbidden_kernel hSound hForbidden hErased

theorem forbiddenPair_visible_under_soundPresentationBy
    {X : Type u}
    {Q : Type v}
    {Forbidden : X -> X -> Prop}
    {present : X -> Q}
    (hSound : SoundPresentationBy Forbidden present)
    {x y : X}
    (hForbidden : Forbidden x y) :
    PairVisible present x y := by
  exact soundPresentationBy_blocks_forbidden_kernel hSound hForbidden

theorem constantPresentation_not_sound_of_forbiddenPair
    {X : Type u}
    {Forbidden : X -> X -> Prop}
    (h : HasForbiddenPair Forbidden) :
    Not (SoundPresentationBy Forbidden (fun _ : X => ())) := by
  intro hSound
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hForbidden =>
          exact hSound x y rfl hForbidden

/--
A map preserves forbidden pairs when forbidden source pairs map to forbidden
target pairs.
-/
def ForbiddenPreservingMap
    {X : Type u}
    {Y : Type v}
    (ForbiddenX : X -> X -> Prop)
    (ForbiddenY : Y -> Y -> Prop)
    (f : X -> Y) : Prop :=
  forall x y, ForbiddenX x y -> ForbiddenY (f x) (f y)

/--
Sound presentations pull back along maps that preserve forbidden pairs.
-/
theorem pullback_soundPresentationBy
    {X : Type u}
    {Y : Type v}
    {Q : Type _}
    {ForbiddenX : X -> X -> Prop}
    {ForbiddenY : Y -> Y -> Prop}
    {f : X -> Y}
    {present : Y -> Q}
    (hMap : ForbiddenPreservingMap ForbiddenX ForbiddenY f)
    (hSound : SoundPresentationBy ForbiddenY present) :
    SoundPresentationBy ForbiddenX (fun x => present (f x)) := by
  intro x y hEq hForbidden
  exact hSound (f x) (f y) hEq (hMap x y hForbidden)

/--
If a forbidden relation is contained in another one, soundness for the larger
relation implies soundness for the smaller one.
-/
theorem soundPresentationBy_mono_forbidden
    {X : Type u}
    {Q : Type v}
    {ForbiddenSmall ForbiddenLarge : X -> X -> Prop}
    {present : X -> Q}
    (hSub : forall x y, ForbiddenSmall x y -> ForbiddenLarge x y)
    (hSound : SoundPresentationBy ForbiddenLarge present) :
    SoundPresentationBy ForbiddenSmall present := by
  intro x y hEq hForbidden
  exact hSound x y hEq (hSub x y hForbidden)

end PresentationSoundness
end Trajectory
end OmegaProper
