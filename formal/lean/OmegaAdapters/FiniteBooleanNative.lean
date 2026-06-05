import ProtoOmega.Presentation.Native
import ProtoOmega.Transport.Native

/-!
OmegaAdapters.FiniteBooleanNative

Finite Boolean support presentation.

Events are predicates over finite or arbitrary carrier types. The event order is
support inclusion, and a binary relation induces a native transport by
existential forward-image support recovery.

This module now exposes the Boolean adapter at two levels:

* presentation-native: event/separation/order/transport structures that do not
  claim full Alpha substrate contact;
* Alpha-frame compatible: the older event frame and `NativeTransport` surface
  kept for downstream modules.
-/

namespace OmegaAdapters
namespace FiniteBooleanNative

universe u v w

/-- Boolean event predicates over a carrier type. -/
def Event (a : Type u) : Type u :=
  a -> Prop

/-- Binary relation between carrier types. -/
def Rel (a : Type u) (b : Type v) : Type (max u v) :=
  a -> b -> Prop

/-- Event distinctions separate points when the predicate differs. -/
def EventSep {a : Type u} (P : Event a) (x y : a) : Prop :=
  (P x /\ Not (P y)) \/ (P y /\ Not (P x))

theorem eventSep_irrefl {a : Type u} (P : Event a) (x : a) :
    Not (EventSep P x x) := by
  intro h
  cases h with
  | inl hleft => exact hleft.right hleft.left
  | inr hright => exact hright.right hright.left

theorem eventSep_symm {a : Type u} (P : Event a) (x y : a) :
    EventSep P x y -> EventSep P y x := by
  intro h
  cases h with
  | inl hleft => exact Or.inr hleft
  | inr hright => exact Or.inl hright

/-- Presentation-native Boolean event separation. -/
def eventSepPresentation (a : Type u) :
    ProtoOmega.Presentation.SepPresentation.{u, u} where
  X := a
  Dist := Event a
  Sep := EventSep
  sep_irrefl := eventSep_irrefl
  sep_symm := eventSep_symm

/-- Presentation-native Boolean event distinctions, forgetting carrier
separation data. -/
def eventDistPresentation (a : Type u) :
    ProtoOmega.Presentation.DistPresentation.{u} :=
  (eventSepPresentation a).toDistPresentation

/-- Alpha frame whose distinctions are Boolean events. The adapter relation is
external to the frame and appears in `supportTransport`. -/
def EventAlphaFrame (a : Type u) : AlphaCore.Frame.{u, u} where
  X := a
  Rel := fun _ _ => False
  Dist := Event a
  Sep := EventSep
  sep_irrefl := eventSep_irrefl
  sep_symm := eventSep_symm
  Asym := fun _ _ _ => False
  asym_rel := by
    intro _ _ _ h
    cases h
  asym_sep := by
    intro _ _ _ h
    cases h

/-- Support-inclusion order for events. `EventLe P Q` means that `Q` is at
least as broad as `P` as an acceptable support target. -/
def EventLe {a : Type u} (P Q : Event a) : Prop :=
  forall x, P x -> Q x

theorem eventLe_refl {a : Type u} (P : Event a) : EventLe P P := by
  intro x hP
  exact hP

theorem eventLe_trans {a : Type u} {P Q Z : Event a} :
    EventLe P Q -> EventLe Q Z -> EventLe P Z := by
  intro hPQ hQZ x hP
  exact hQZ x (hPQ x hP)

/-- Presentation-native event order. -/
def eventPresentationOrder (a : Type u) :
    ProtoOmega.Presentation.DistOrder (eventDistPresentation a) where
  le := EventLe
  le_refl := eventLe_refl
  le_trans := @eventLe_trans a

/-- Event preorder over the Alpha-native Boolean event frame. -/
def eventOrder (a : Type u) :
    ProtoOmega.Transport.DistOrder (EventAlphaFrame a) where
  le := EventLe
  le_refl := eventLe_refl
  le_trans := @eventLe_trans a

/-- Existential forward-image support recovery.

Every source point satisfying `P` has at least one `R`-successor satisfying
`Q`. This is possibility/support recovery, not universal preservation. -/
def SupportRecovers
    {a : Type u} {b : Type v}
    (R : Rel a b)
    (P : Event a)
    (Q : Event b) : Prop :=
  forall x, P x -> exists y, R x y /\ Q y

/-- Relation-induced presentation-native support transport. -/
def supportPresentationTransport
    {a : Type u} {b : Type v}
    (R : Rel a b) :
    ProtoOmega.Presentation.Transport
      (eventPresentationOrder a) (eventPresentationOrder b) where
  rel := SupportRecovers R
  closed := by
    intro P' P Q Q' hSource hRec hTarget
    intro x hP'
    cases hRec x (hSource x hP') with
    | intro y hy =>
        exact Exists.intro y
          (And.intro hy.left (hTarget y hy.right))

/-- Relation-induced native support transport. -/
def supportTransport
    {a : Type u} {b : Type v}
    (R : Rel a b) :
    ProtoOmega.Transport.NativeTransport (eventOrder a) (eventOrder b) where
  rel := SupportRecovers R
  closed := by
    intro P' P Q Q' hSource hRec hTarget
    intro x hP'
    cases hRec x (hSource x hP') with
    | intro y hy =>
        exact Exists.intro y
          (And.intro hy.left (hTarget y hy.right))

/-- Identity relation. -/
def IdRel (a : Type u) : Rel a a :=
  fun x y => x = y

/-- The identity relation induces presentation-level identity transport under
support-inclusion event order. -/
theorem supportPresentationTransport_id_iff
    {a : Type u}
    (P Q : Event a) :
    (supportPresentationTransport (IdRel a)).rel P Q <->
      (ProtoOmega.Presentation.Transport.id (eventPresentationOrder a)).rel P Q := by
  constructor
  case mp =>
    intro hRec x hP
    cases hRec x hP with
    | intro y hy =>
        rw [hy.left]
        exact hy.right
  case mpr =>
    intro hLe x hP
    exact Exists.intro x
      (And.intro rfl (hLe x hP))

/-- The identity relation induces the native identity transport, at relation
level, under support-inclusion event order. -/
theorem supportTransport_id_iff
    {a : Type u}
    (P Q : Event a) :
    (supportTransport (IdRel a)).rel P Q <->
      (ProtoOmega.Transport.NativeTransport.id (eventOrder a)).rel P Q := by
  constructor
  case mp =>
    intro hRec x hP
    cases hRec x hP with
    | intro y hy =>
        rw [hy.left]
        exact hy.right
  case mpr =>
    intro hLe x hP
    exact Exists.intro x
      (And.intro rfl (hLe x hP))

/-- Relational composition. `RelComp R S` means `S` after `R`. -/
def RelComp
    {a : Type u} {b : Type v} {c : Type w}
    (R : Rel a b)
    (S : Rel b c) : Rel a c :=
  fun x z => exists y, R x y /\ S y z

/-- Relation-induced presentation-native support transport is lax over
relational composition. -/
theorem supportPresentationTransport_comp_subset
    {a : Type u} {b : Type v} {c : Type w}
    (R : Rel a b)
    (S : Rel b c) :
    ProtoOmega.Presentation.Transport.Subset
      (ProtoOmega.Presentation.Transport.compose
        (supportPresentationTransport R) (supportPresentationTransport S))
      (supportPresentationTransport (RelComp R S)) := by
  intro P Z hComp
  intro x hP
  cases hComp with
  | intro Q hQ =>
      cases hQ.left x hP with
      | intro y hy =>
          cases hQ.right y hy.right with
          | intro z hz =>
              exact Exists.intro z
                (And.intro
                  (Exists.intro y (And.intro hy.left hz.left))
                  hz.right)

/-- Relation-induced native support transport is lax over relational
composition. -/
theorem supportTransport_comp_subset
    {a : Type u} {b : Type v} {c : Type w}
    (R : Rel a b)
    (S : Rel b c) :
    ProtoOmega.Transport.NativeTransport.Subset
      (ProtoOmega.Transport.NativeTransport.compose
        (supportTransport R) (supportTransport S))
      (supportTransport (RelComp R S)) := by
  intro P Z hComp
  intro x hP
  cases hComp with
  | intro Q hQ =>
      cases hQ.left x hP with
      | intro y hy =>
          cases hQ.right y hy.right with
          | intro z hz =>
              exact Exists.intro z
                (And.intro
                  (Exists.intro y (And.intro hy.left hz.left))
                  hz.right)

/-- Source carrier for the changed-carrier example. -/
inductive Start where
  | s
  deriving DecidableEq

/-- Middle carrier for the changed-carrier example. -/
inductive Middle where
  | m
  deriving DecidableEq

/-- End carrier for the changed-carrier example. -/
inductive Finish where
  | f
  deriving DecidableEq

def StartEvent : Event Start
  | Start.s => True

def MiddleEvent : Event Middle
  | Middle.m => True

def FinishEvent : Event Finish
  | Finish.f => True

def StartToMiddle : Rel Start Middle
  | Start.s, Middle.m => True

def MiddleToFinish : Rel Middle Finish
  | Middle.m, Finish.f => True

/-- First local support recovery in the changed-carrier example. -/
theorem changed_carrier_first_step :
    (supportTransport StartToMiddle).rel StartEvent MiddleEvent := by
  intro x hX
  cases x
  exact Exists.intro Middle.m
    (And.intro
      (by simp [StartToMiddle])
      (by simp [MiddleEvent]))

/-- Second local support recovery in the changed-carrier example. -/
theorem changed_carrier_second_step :
    (supportTransport MiddleToFinish).rel MiddleEvent FinishEvent := by
  intro x hX
  cases x
  exact Exists.intro Finish.f
    (And.intro
      (by simp [MiddleToFinish])
      (by simp [FinishEvent]))

/-- End-to-end support recovery across changed carrier types. No literal state
identity is shared across `Start`, `Middle`, and `Finish`. -/
theorem changed_carrier_composite_recovery :
    (supportTransport (RelComp StartToMiddle MiddleToFinish)).rel
      StartEvent FinishEvent := by
  exact supportTransport_comp_subset StartToMiddle MiddleToFinish
    StartEvent FinishEvent
    (Exists.intro MiddleEvent
      (And.intro changed_carrier_first_step changed_carrier_second_step))

end FiniteBooleanNative
end OmegaAdapters
