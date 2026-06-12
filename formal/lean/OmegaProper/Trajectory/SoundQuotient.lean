import OmegaProper.Trajectory.ConsequenceRelation

/-!
OmegaProper.Trajectory.SoundQuotient

Standard quotient-language compression for the consequence layer.

This file does not introduce a new consequence system. It repackages the
existing merge/identification guardrail in familiar terms: a quotient is sound
when its kernel identifies only consequence-identifiable fragments.
-/

namespace OmegaProper
namespace Trajectory
namespace SoundQuotient

open ConsequenceRelation

universe w k o q

/-- The kernel relation of a quotient-like map. -/
def KernelRelation {X : Type w} {Q : Type q} (quot : X -> Q) :
    X -> X -> Prop :=
  fun x y => quot x = quot y

/--
A quotient-like map is sound when every pair in its kernel is consequence
identifiable.
-/
def SoundQuotient (S : ConsequenceSystem.{w, k, o})
    {Q : Type q}
    (quot : S.Fragment -> Q) : Prop :=
  forall x y, quot x = quot y -> ConsequenceIdentifiable S x y

/--
Kernel-containment spelling of sound quotient: every identified pair belongs
to the exact consequence-identifiability relation.
-/
def KernelContainedInIdentifiability (S : ConsequenceSystem.{w, k, o})
    {Q : Type q}
    (quot : S.Fragment -> Q) : Prop :=
  forall x y, KernelRelation quot x y -> ConsequenceIdentifiable S x y

/--
The sound quotient condition is exactly kernel containment in consequence
identifiability.
-/
theorem soundQuotient_iff_kernelContainedInIdentifiability
    (S : ConsequenceSystem.{w, k, o})
    {Q : Type q}
    (quot : S.Fragment -> Q) :
    SoundQuotient S quot <->
      KernelContainedInIdentifiability S quot := by
  rfl

/--
Sound quotients are consequence-respecting identification relations when read
through their kernels.
-/
theorem soundQuotient_identificationRespectsConsequences
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {quot : S.Fragment -> Q}
    (hSound : SoundQuotient S quot) :
    IdentificationRespectsConsequences S (KernelRelation quot) := by
  intro x y hxy
  exact hSound x y hxy

/--
A sound quotient cannot identify a merge-separated pair.
-/
theorem soundQuotient_blocks_mergeSeparated_kernel
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {quot : S.Fragment -> Q}
    (hSound : SoundQuotient S quot)
    {x y : S.Fragment}
    (hSep : ConsequenceMergeSeparated S x y) :
    Not (quot x = quot y) := by
  intro hxy
  exact mergeSeparated_blocks_identifiable hSep (hSound x y hxy)

/--
If a quotient identifies a merge-separated pair, it is not sound.
-/
theorem mergeSeparated_kernel_blocks_soundQuotient
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {quot : S.Fragment -> Q}
    {x y : S.Fragment}
    (hxy : quot x = quot y)
    (hSep : ConsequenceMergeSeparated S x y) :
    Not (SoundQuotient S quot) := by
  intro hSound
  exact soundQuotient_blocks_mergeSeparated_kernel hSound hSep hxy

/--
Directional separation also blocks a sound quotient's kernel.
-/
theorem soundQuotient_blocks_separated_kernel
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {quot : S.Fragment -> Q}
    (hSound : SoundQuotient S quot)
    {x y : S.Fragment}
    (hSep : ConsequenceSeparated S x y) :
    Not (quot x = quot y) := by
  exact soundQuotient_blocks_mergeSeparated_kernel hSound
    (separated_implies_mergeSeparated hSep)

end SoundQuotient
end Trajectory
end OmegaProper
