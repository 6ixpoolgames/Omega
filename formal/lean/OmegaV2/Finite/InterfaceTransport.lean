import Mathlib.Data.Set.Basic

/-!
OmegaV2.Finite.InterfaceTransport

Feature-fiber transport across an exact equivalence of finite interface
presentations. This file does not define a process, agent, or preferred
factorization.
-/

namespace OmegaV2
namespace Finite

universe u v w

/-- Interfaces carrying one selected feature value. -/
def FeatureFiber
    {Interface : Type u}
    {Feature : Type v}
    (profile : Interface -> Feature)
    (value : Feature) :
    Set Interface :=
  {interface | profile interface = value}

/-- Unique identification inside the complete declared interface type. -/
def UniquelyIdentified
    {Interface : Type u}
    {Feature : Type v}
    (profile : Interface -> Feature)
    (value : Feature)
    (candidate : Interface) : Prop :=
  profile candidate = value /\
    forall other, profile other = value -> other = candidate

/--
An exact interface transport is a bijection that preserves the selected
feature profile.
-/
structure InterfaceEquivalence
    (Source : Type u)
    (Target : Type v)
    (Feature : Type w)
    (sourceProfile : Source -> Feature)
    (targetProfile : Target -> Feature) where
  toTarget : Source -> Target
  toSource : Target -> Source
  left_inv : forall source, toSource (toTarget source) = source
  right_inv : forall target, toTarget (toSource target) = target
  profile_preserved :
    forall source, targetProfile (toTarget source) = sourceProfile source

namespace InterfaceEquivalence

/-- Exact transport carries the complete source feature fiber to the target. -/
theorem image_featureFiber
    {Source : Type u}
    {Target : Type v}
    {Feature : Type w}
    {sourceProfile : Source -> Feature}
    {targetProfile : Target -> Feature}
    (transport :
      InterfaceEquivalence
        Source
        Target
        Feature
        sourceProfile
        targetProfile)
    (value : Feature) :
    transport.toTarget '' FeatureFiber sourceProfile value =
      FeatureFiber targetProfile value := by
  ext target
  constructor
  · intro hTarget
    rcases hTarget with ⟨source, hSource, rfl⟩
    exact (transport.profile_preserved source).trans hSource
  · intro hTarget
    refine ⟨transport.toSource target, ?_, transport.right_inv target⟩
    have hPreserved := transport.profile_preserved (transport.toSource target)
    rw [transport.right_inv target] at hPreserved
    exact hPreserved.symm.trans hTarget

/-- Unique identification transports across an exact interface equivalence. -/
theorem uniquelyIdentified_toTarget
    {Source : Type u}
    {Target : Type v}
    {Feature : Type w}
    {sourceProfile : Source -> Feature}
    {targetProfile : Target -> Feature}
    (transport :
      InterfaceEquivalence
        Source
        Target
        Feature
        sourceProfile
        targetProfile)
    {value : Feature}
    {candidate : Source}
    (hIdentified :
      UniquelyIdentified sourceProfile value candidate) :
    UniquelyIdentified
      targetProfile
      value
      (transport.toTarget candidate) := by
  constructor
  · exact (transport.profile_preserved candidate).trans hIdentified.1
  · intro other hOther
    have hPreserved :=
      transport.profile_preserved (transport.toSource other)
    rw [transport.right_inv other] at hPreserved
    have hSource :
        sourceProfile (transport.toSource other) = value :=
      hPreserved.symm.trans hOther
    have hSourceEq :
        transport.toSource other = candidate :=
      hIdentified.2 (transport.toSource other) hSource
    calc
      other = transport.toTarget (transport.toSource other) :=
        (transport.right_inv other).symm
      _ = transport.toTarget candidate := congrArg transport.toTarget hSourceEq

end InterfaceEquivalence

/--
A non-injective merge can erase a feature value that uniquely identifies a
source interface.
-/
theorem noninjective_merge_can_erase_identification :
    exists merge : Bool -> Unit,
      (Not (Function.Injective merge)) /\
      UniquelyIdentified (fun value : Bool => value) true true /\
      (Not (exists target : Unit,
        UniquelyIdentified (fun _ : Unit => false) true target)) := by
  refine ⟨fun _ => (), ?_, ?_, ?_⟩
  · simp [Function.Injective]
  · simp [UniquelyIdentified]
  · simp [UniquelyIdentified]

end Finite
end OmegaV2
