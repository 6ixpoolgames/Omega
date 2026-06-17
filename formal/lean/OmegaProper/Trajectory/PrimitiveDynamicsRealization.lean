import OmegaProper.Trajectory.GeneratedCarrier
import OmegaProper.Trajectory.PrimitiveConsequenceExposure

/-!
OmegaProper.Trajectory.PrimitiveDynamicsRealization

Bridge from Alpha-native primitive paths to adapter dynamics.

This file does not claim that Alpha derives dynamics. It defines realization
contracts under which relation-generated primitive paths are realized as
adapter transition paths.
-/

namespace OmegaProper
namespace Trajectory
namespace PrimitiveDynamicsRealization

open CarrierCertificate
open GeneratedCarrier
open PathCarriedDistinction
open PrimitiveConsequenceExposure
open RecurrentViableClass

universe u v k o

/--
An adapter transition relation realizes primitive relation when every Alpha
relation edge is also an adapter transition edge.
-/
def DynamicsRealizesPrimitiveRel
    (A : AlphaCore.Frame.{u, v})
    (Next : A.X -> A.X -> Prop) : Prop :=
  forall {x y : A.X}, A.Rel x y -> Next x y

/--
If adapter dynamics realize primitive relation, then primitive paths become
internal paths in the top carrier.
-/
theorem primitivePath_realized_as_internalPath_top
    {A : AlphaCore.Frame.{u, v}}
    {Next : A.X -> A.X -> Prop}
    (hRealize : DynamicsRealizesPrimitiveRel A Next)
    {x y : A.X}
    (hPath : AlphaCore.Frame.PrimitivePath A x y) :
    InternalPath (dynFromNext Next) (fun _ : A.X => True) x y := by
  induction hPath with
  | refl x =>
      exact InternalPath.refl trivial
  | step hRel hRest ih =>
      exact InternalPath.step
        trivial
        trivial
        (hRealize hRel)
        ih

theorem primitiveMutualReach_realized_as_roundTrip_top
    {A : AlphaCore.Frame.{u, v}}
    {Next : A.X -> A.X -> Prop}
    (hRealize : DynamicsRealizesPrimitiveRel A Next)
    {x y : A.X}
    (hMutual : AlphaCore.Frame.PrimitiveMutualReach A x y) :
    InternalPath (dynFromNext Next) (fun _ : A.X => True) x y /\
      InternalPath (dynFromNext Next) (fun _ : A.X => True) y x := by
  exact And.intro
    (primitivePath_realized_as_internalPath_top hRealize hMutual.left)
    (primitivePath_realized_as_internalPath_top hRealize hMutual.right)

/--
Primitive mutual-reach carriers become generated mutual-reach carriers once
primitive relation is realized by adapter dynamics.
-/
theorem primitiveMutualReachCarrier_realized_as_generatedCarrier_top
    {A : AlphaCore.Frame.{u, v}}
    {Next : A.X -> A.X -> Prop}
    (hRealize : DynamicsRealizesPrimitiveRel A Next)
    {x y z : A.X}
    (hCarrier : AlphaCore.Frame.PrimitiveMutualReachCarrier A x y z) :
    MutualReachCarrier Next (fun _ : A.X => True) x y z := by
  exact And.intro
    trivial
    (And.intro
      (primitivePath_realized_as_internalPath_top hRealize hCarrier.left)
      (And.intro
        (primitivePath_realized_as_internalPath_top hRealize hCarrier.right.left)
        (And.intro
          (primitivePath_realized_as_internalPath_top hRealize hCarrier.right.right.left)
          (primitivePath_realized_as_internalPath_top hRealize hCarrier.right.right.right))))

/--
Primitive mutual reach plus consequence exposure certifies the top carrier,
provided the adapter supplies recurrence/safety for that carrier.
-/
theorem primitiveMutualReach_certificate_of_realization_exposure
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSeed.AlphaConsequenceSystem.{u, v, k, o} A}
    {Next : A.X -> A.X -> Prop}
    {safe : A.X -> Prop}
    {x y : A.X}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (hRealize : DynamicsRealizesPrimitiveRel A Next)
    (hRec :
      RecurrentViableClass
        (dynFromNext Next)
        safe
        (fun _ : A.X => True))
    (hMutual : AlphaCore.Frame.PrimitiveMutualReach A x y)
    (hApart : AlphaCore.Frame.PrimitiveApart A x y) :
    CarrierCertificate
      S.toConsequenceSystem
      Next
      safe
      (fun _ : A.X => True)
      x
      y := by
  exact And.intro
    hRec
    (And.intro
      trivial
      (And.intro
        trivial
        (And.intro
          (primitivePath_realized_as_internalPath_top hRealize hMutual.left)
          (And.intro
            (primitivePath_realized_as_internalPath_top hRealize hMutual.right)
            (hExpose x y hApart)))))

/--
An asymmetry witness becomes a certified recurrent carrier fact when:

* consequence exposes primitive apartness;
* adapter dynamics realize primitive relation;
* the reverse primitive path exists; and
* the adapter supplies recurrence/safety for the top carrier.
-/
theorem asymmetryWitness_certificate_of_realization_exposure_reversePath
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSeed.AlphaConsequenceSystem.{u, v, k, o} A}
    {Next : A.X -> A.X -> Prop}
    {safe : A.X -> Prop}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (hRealize : DynamicsRealizesPrimitiveRel A Next)
    (hRec :
      RecurrentViableClass
        (dynFromNext Next)
        safe
        (fun _ : A.X => True))
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A)
    (hBack : AlphaCore.Frame.PrimitivePath A w.y w.x) :
    CarrierCertificate
      S.toConsequenceSystem
      Next
      safe
      (fun _ : A.X => True)
      w.x
      w.y := by
  exact primitiveMutualReach_certificate_of_realization_exposure
    hExpose
    hRealize
    hRec
    (And.intro
      (AlphaCore.Frame.asymmetry_implies_primitivePath w.asym)
      hBack)
    (AlphaCore.Frame.asymmetryWitness_implies_primitiveApart w)

end PrimitiveDynamicsRealization
end Trajectory
end OmegaProper
