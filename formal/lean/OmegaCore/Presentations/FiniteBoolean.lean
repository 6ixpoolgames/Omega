import OmegaCore.DistTrans

/-!
OmegaCore.Presentations.FiniteBoolean

Boolean relation support presentation for Omega Primitive Calculus v0.

This is a support-inclusion presentation, not the only possible Boolean
distinction order. Events are predicates, `EventLe P Q` means every point
supporting `P` also supports `Q`, and support recovery means every `P`-source
has at least one relational successor in `Q`.

This module validates a worked presentation of the root calculus. It is not an
empirical adapter, Future Field Atlas semantics, compatibility semantics,
valuerhood, ethics, or Omega validation.
-/

namespace OmegaCore

namespace Presentations

namespace FiniteBoolean

universe u v w

/-- Boolean event predicates over a carrier type. -/
def Event (a : Type u) : Type u :=
  a -> Prop

/-- Binary relation between carrier types. -/
def Rel (a : Type u) (b : Type v) : Type (max u v) :=
  a -> b -> Prop

/-- Support-inclusion order for events. `EventLe P Q` means `Q` is at least as
broad as `P` as an acceptable support target. -/
def EventLe {a : Type u} (P Q : Event a) : Prop :=
  forall x, P x -> Q x

theorem eventLe_refl {a : Type u} (P : Event a) : EventLe P P := by
  intro x hP
  exact hP

theorem eventLe_trans {a : Type u} {P Q Z : Event a} :
    EventLe P Q -> EventLe Q Z -> EventLe P Z := by
  intro hPQ hQZ x hP
  exact hQZ x (hPQ x hP)

/-- Event preorder frame for support inclusion. -/
def EventFrame (a : Type u) : PreorderFrame (Event a) where
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

/-- Relation-induced support transport. -/
def supportTransport
    {a : Type u} {b : Type v}
    (R : Rel a b) :
    DistTransport (EventFrame a) (EventFrame b) where
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

/-- The identity relation induces the root identity transport, at relation
level, under support-inclusion event order. -/
theorem supportTransport_id_iff
    {a : Type u}
    (P Q : Event a) :
    (supportTransport (IdRel a)).rel P Q <->
      (DistTransport.id (EventFrame a)).rel P Q := by
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

/-- Relation-induced support transport is lax over relational composition. -/
theorem supportTransport_comp_subset
    {a : Type u} {b : Type v} {c : Type w}
    (R : Rel a b)
    (S : Rel b c) :
    DistTransport.Subset
      (DistTransport.compose (supportTransport R) (supportTransport S))
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

end FiniteBoolean

end Presentations

end OmegaCore
