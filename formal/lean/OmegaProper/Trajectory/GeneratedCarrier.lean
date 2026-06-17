import OmegaProper.Trajectory.CarrierCertificate

/-!
OmegaProper.Trajectory.GeneratedCarrier

Generated carrier candidates.

This file gives a first principled alternative to arbitrary declared support.
Given an ambient predicate and a declared pair `x y`, the mutual-reach carrier
contains states that are mutually internally reachable with both endpoints
inside the ambient predicate.

This still does not define objecthood, identity, boundaries, agency, value,
deformer structure, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace GeneratedCarrier

open CarrierCertificate
open CarriedDistinction
open ConsequenceRelation
open PathCarriedDistinction
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- Internal paths are monotone in the class predicate. -/
def internalPath_mono_class
    {X : Type w}
    {Next : X -> X -> Prop}
    {C D : X -> Prop}
    (hSub : forall z, C z -> D z)
    {x y : X}
    (hPath : InternalPath (dynFromNext Next) C x y) :
    InternalPath (dynFromNext Next) D x y :=
  match hPath with
  | InternalPath.refl hx =>
      InternalPath.refl (hSub _ hx)
  | InternalPath.step hx hy hStep rest =>
      InternalPath.step
        (hSub _ hx)
        (hSub _ hy)
        hStep
        (internalPath_mono_class hSub rest)

/--
The generated mutual-reach carrier around endpoints `x` and `y` inside an
ambient predicate.

It contains exactly the states that remain in the ambient predicate and can
internally reach, and be reached from, both endpoints through ambient paths.
-/
def MutualReachCarrier
    {X : Type w}
    (Next : X -> X -> Prop)
    (Ambient : X -> Prop)
    (x y : X)
    (z : X) : Prop :=
  Ambient z /\
    InternalPath (dynFromNext Next) Ambient x z /\
    InternalPath (dynFromNext Next) Ambient z x /\
    InternalPath (dynFromNext Next) Ambient y z /\
    InternalPath (dynFromNext Next) Ambient z y

/-- The generated carrier is contained in its ambient predicate. -/
theorem mutualReachCarrier_sub_ambient
    {X : Type w}
    {Next : X -> X -> Prop}
    {Ambient : X -> Prop}
    {x y z : X}
    (h : MutualReachCarrier Next Ambient x y z) :
    Ambient z := by
  exact h.left

/--
If `x` and `y` are mutually reachable inside the ambient predicate, then `x`
belongs to the generated carrier.
-/
theorem mutualReachCarrier_contains_left
    {X : Type w}
    {Next : X -> X -> Prop}
    {Ambient : X -> Prop}
    {x y : X}
    (hx : Ambient x)
    (hxy : InternalPath (dynFromNext Next) Ambient x y)
    (hyx : InternalPath (dynFromNext Next) Ambient y x) :
    MutualReachCarrier Next Ambient x y x := by
  exact And.intro
    hx
    (And.intro
      (InternalPath.refl hx)
      (And.intro
        (InternalPath.refl hx)
        (And.intro
          hyx
          hxy)))

/--
If `x` and `y` are mutually reachable inside the ambient predicate, then `y`
belongs to the generated carrier.
-/
theorem mutualReachCarrier_contains_right
    {X : Type w}
    {Next : X -> X -> Prop}
    {Ambient : X -> Prop}
    {x y : X}
    (hy : Ambient y)
    (hxy : InternalPath (dynFromNext Next) Ambient x y)
    (hyx : InternalPath (dynFromNext Next) Ambient y x) :
    MutualReachCarrier Next Ambient x y y := by
  exact And.intro
    hy
    (And.intro
      hxy
      (And.intro
        hyx
        (And.intro
          (InternalPath.refl hy)
          (InternalPath.refl hy))))

/--
Any certified carrier contained in an ambient predicate lies inside the
generated mutual-reach carrier for its certified endpoints.

This is the basic canonicality fact: the generated carrier is not an arbitrary
support name; it contains every state of any already-certified carrier inside
the ambient region.
-/
theorem certified_carrier_sub_mutualReachCarrier
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C Ambient : S.Fragment -> Prop}
    {x y z : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y)
    (hSub : forall a, C a -> Ambient a)
    (hz : C z) :
    MutualReachCarrier Next Ambient x y z := by
  exact And.intro
    (hSub z hz)
    (And.intro
      (internalPath_mono_class hSub
        (hCert.left.right.right.left x z hCert.right.left hz))
      (And.intro
        (internalPath_mono_class hSub
          (hCert.left.right.right.left z x hz hCert.right.left))
        (And.intro
          (internalPath_mono_class hSub
            (hCert.left.right.right.left y z hCert.right.right.left hz))
          (internalPath_mono_class hSub
            (hCert.left.right.right.left z y hz hCert.right.right.left)))))

/--
If the generated carrier itself is recurrent viable and keeps the pair
merge-separated, then it becomes certified.

This keeps canonical generation separate from validation: generation proposes a
candidate, while recurrence and consequence checks certify it.
-/
theorem mutualReachCarrier_certificate_of_recurrent
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe Ambient : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hRec :
      RecurrentViableClass
        (dynFromNext Next)
        safe
        (MutualReachCarrier Next Ambient x y))
    (hx : MutualReachCarrier Next Ambient x y x)
    (hy : MutualReachCarrier Next Ambient x y y)
    (hSep : ConsequenceMergeSeparated S x y) :
    CarrierCertificate
      S
      Next
      safe
      (MutualReachCarrier Next Ambient x y)
      x
      y := by
  exact And.intro
    hRec
    (And.intro
      hx
      (And.intro
        hy
        (And.intro
          (hRec.right.right.left x y hx hy)
          (And.intro
            (hRec.right.right.left y x hy hx)
            hSep))))

/--
The two-state cycle certificate is contained in the mutual-reach carrier
generated inside its own class.
-/
theorem cycle_certificate_sub_generated
    {z : CycleState}
    (hz : cycleClass z) :
    MutualReachCarrier cycleNext cycleClass CycleState.left CycleState.right z := by
  exact certified_carrier_sub_mutualReachCarrier
    cycle_carrier_certificate
    (fun a ha => ha)
    hz

end GeneratedCarrier
end Trajectory
end OmegaProper
