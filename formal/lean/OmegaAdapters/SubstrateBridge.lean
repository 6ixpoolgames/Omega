import ProtoOmega.Presentation.Native

/-!
OmegaAdapters.SubstrateBridge

Explicit bridge objects between an Alpha frame and a presentation.

Presentation-native adapters can define distinction, separation, order, and
transport laws without claiming that they were induced by a substrate's
primitive relation/asymmetry structure. These bridge objects make substrate
contact a separate proof obligation.
-/

namespace OmegaAdapters

universe u v w z p q

/-- A presentation is soundly exposed by an Alpha frame when presentation
separation pulls back to Alpha separation through declared carrier and
distinction maps. -/
structure SubstrateBridge
    (A : AlphaCore.Frame.{u, v})
    (P : ProtoOmega.Presentation.SepPresentation.{w, z}) where
  carrier_map : A.X -> P.X
  dist_map : P.Dist -> A.Dist
  sep_sound :
    forall (d : P.Dist) (x y : A.X),
      P.Sep d (carrier_map x) (carrier_map y) ->
      A.Sep (dist_map d) x y

/-- A relation presentation is soundly exposed by one Alpha frame when support
between exposed presentation points implies the substrate relation between the
underlying Alpha points. -/
structure RelationBridge
    (A : AlphaCore.Frame.{u, v})
    (P : ProtoOmega.Presentation.SepPresentation.{w, z})
    (Q : ProtoOmega.Presentation.SepPresentation.{p, q})
    (K : P.X -> Q.X -> Prop) where
  source : SubstrateBridge A P
  target : SubstrateBridge A Q
  support_sound :
    forall x y : A.X,
      K (source.carrier_map x) (target.carrier_map y) ->
      A.Rel x y

/-- The separation presentation obtained from an Alpha frame is bridged by the
identity maps. -/
def alphaFrameSelfBridge
    (A : AlphaCore.Frame.{u, v}) :
    SubstrateBridge A (AlphaCore.Frame.toSepPresentation A) where
  carrier_map := fun x => x
  dist_map := fun d => d
  sep_sound := by
    intro d x y h
    exact h

/-- The relation of an Alpha frame bridges its own separation presentation. -/
def alphaFrameRelBridge
    (A : AlphaCore.Frame.{u, v}) :
    RelationBridge A
      (AlphaCore.Frame.toSepPresentation A)
      (AlphaCore.Frame.toSepPresentation A)
      A.Rel where
  source := alphaFrameSelfBridge A
  target := alphaFrameSelfBridge A
  support_sound := by
    intro x y h
    exact h

end OmegaAdapters
