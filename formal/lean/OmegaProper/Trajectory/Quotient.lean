import AlphaCore.Primitive

/-!
OmegaProper.Trajectory.Quotient

Presentation-level trajectory-window signatures.

This file intentionally does not derive recovery from Alpha asymmetry. Alpha
supplies the relational carrier for one-step windows; a `WindowSignature`
declares an observation and a directional recovery relation over observation
labels. Later bridge work can ask when such a recovery relation is induced by
substrate structure.
-/

namespace OmegaProper
namespace Trajectory
namespace Quotient

universe u v w

/-- A one-step relation window in an Alpha frame. -/
structure RelWindow (A : AlphaCore.Frame.{u, v}) where
  source : A.X
  target : A.X
  step : A.Rel source target

/-- Endpoint equality ignores the proof object witnessing the step. -/
def SameEndpoints {A : AlphaCore.Frame.{u, v}}
    (w1 w2 : RelWindow A) : Prop :=
  w1.source = w2.source /\ w1.target = w2.target

/-- A window is nontrivial when it is not a same-endpoint loop. -/
def NontrivialWindow {A : AlphaCore.Frame.{u, v}}
    (w : RelWindow A) : Prop :=
  Not (w.source = w.target)

/--
A declared signature over relation windows.

`recovers later earlier` is directional: the later label carries enough declared
signature information to recover the earlier label.
-/
structure WindowSignature (A : AlphaCore.Frame.{u, v}) where
  Label : Type w
  observe : RelWindow A -> Label
  recovers : Label -> Label -> Prop

/-- The recovery relation is reflexive on observed labels. -/
def ReflexiveRecovery {A : AlphaCore.Frame.{u, v}}
    (S : WindowSignature.{u, v, w} A) : Prop :=
  forall label : S.Label, S.recovers label label

/-- A later window recovers an earlier window under a declared signature. -/
def RecoveredWindow {A : AlphaCore.Frame.{u, v}}
    (S : WindowSignature.{u, v, w} A)
    (earlier later : RelWindow A) : Prop :=
  S.recovers (S.observe later) (S.observe earlier)

theorem same_window_recovers_of_reflexive
    {A : AlphaCore.Frame.{u, v}}
    {S : WindowSignature.{u, v, w} A}
    (h : ReflexiveRecovery S)
    (w : RelWindow A) :
    RecoveredWindow S w w := by
  exact h (S.observe w)

/-- The coarsest signature over windows: all windows have one label. -/
def coarseSignature (A : AlphaCore.Frame.{u, v}) :
    WindowSignature.{u, v, 0} A where
  Label := Unit
  observe := fun _ => ()
  recovers := fun _ _ => True

theorem coarse_signature_recovers_everything
    {A : AlphaCore.Frame.{u, v}}
    (earlier later : RelWindow A) :
    RecoveredWindow (coarseSignature A) earlier later := by
  trivial

/-- Endpoint signature: recovery requires exact equality of source/target endpoints. -/
def endpointSignature (A : AlphaCore.Frame.{u, v}) :
    WindowSignature.{u, v, u} A where
  Label := A.X × A.X
  observe := fun w => (w.source, w.target)
  recovers := fun later earlier => later = earlier

theorem endpoint_signature_recovers_iff_same_endpoints
    {A : AlphaCore.Frame.{u, v}}
    (earlier later : RelWindow A) :
    RecoveredWindow (endpointSignature A) earlier later <->
      SameEndpoints later earlier := by
  constructor
  · intro h
    change (later.source, later.target) = (earlier.source, earlier.target) at h
    exact And.intro (congrArg Prod.fst h) (congrArg Prod.snd h)
  · intro h
    change (later.source, later.target) = (earlier.source, earlier.target)
    exact Prod.ext h.left h.right

/-! ## Tiny finite examples -/

inductive Two where
  | a
  | b
  deriving DecidableEq

/-- A tiny frame with every relation allowed and no asymmetry witnesses. -/
def twoFrame : AlphaCore.Frame where
  X := Two
  Rel := fun _ _ => True
  Dist := Unit
  Sep := fun _ x y => Not (x = y)
  sep_irrefl := by
    intro _ x h
    exact h rfl
  sep_symm := by
    intro _ x y h hyx
    exact h hyx.symm
  Asym := fun _ _ _ => False
  asym_rel := by
    intro _ _ _ h
    cases h
  asym_sep := by
    intro _ _ _ h
    cases h

def loopA : RelWindow twoFrame where
  source := Two.a
  target := Two.a
  step := trivial

def edgeAB : RelWindow twoFrame where
  source := Two.a
  target := Two.b
  step := trivial

theorem recovery_does_not_imply_same_endpoints :
    RecoveredWindow (coarseSignature twoFrame) loopA edgeAB /\
      Not (SameEndpoints loopA edgeAB) := by
  constructor
  · exact coarse_signature_recovers_everything loopA edgeAB
  · intro h
    have ht : Two.a = Two.b := h.right
    cases ht

theorem strict_signature_can_fail_where_coarse_succeeds :
    RecoveredWindow (coarseSignature twoFrame) loopA edgeAB /\
      Not (RecoveredWindow (endpointSignature twoFrame) loopA edgeAB) := by
  constructor
  · exact coarse_signature_recovers_everything loopA edgeAB
  · intro h
    change (edgeAB.source, edgeAB.target) = (loopA.source, loopA.target) at h
    have ht : Two.b = Two.a := congrArg Prod.snd h
    cases ht

theorem loop_recovery_does_not_imply_nontrivial_window :
    RecoveredWindow (coarseSignature twoFrame) loopA loopA /\
      Not (NontrivialWindow loopA) := by
  constructor
  · exact coarse_signature_recovers_everything loopA loopA
  · intro h
    exact h rfl

theorem same_window_endpoint_recovers :
    RecoveredWindow (endpointSignature twoFrame) edgeAB edgeAB := by
  exact same_window_recovers_of_reflexive (S := endpointSignature twoFrame)
    (by intro label; rfl) edgeAB

end Quotient
end Trajectory
end OmegaProper
