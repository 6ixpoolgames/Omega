import OmegaProper.Trajectory.PredicateFixpoint

/-!
OmegaProper.Foundation.SupportBlindness

Support-only continuation operators cannot distinguish two weighted dynamics
once their positive action-labelled support relations agree.

This theorem is independent of finiteness and transition weights. The Python
foundation adapter supplies finite rational kernels and exhibits two kernels
with equal support but different path-law directionality.

This file does not define value, standing, agency, or Omega proper.
-/

namespace OmegaProper
namespace Foundation
namespace SupportBlindness

open Trajectory.PredicateFixpoint

universe u v

/-- Positive action-labelled transition support. -/
abbrev Support (State : Type u) (Action : Type v) :=
  State -> Action -> State -> Prop

/-- Pointwise equality of two action-labelled support relations. -/
def SupportEquivalent
    {State : Type u}
    {Action : Type v}
    (left right : Support State Action) : Prop :=
  forall x action y, left x action y <-> right x action y

/-- May predecessor: some action has some successor in the candidate set. -/
def MayPre
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (candidate : State -> Prop) :
    State -> Prop :=
  fun x =>
    exists action y,
      support x action y /\ candidate y

/--
Robust same-action predecessor: one enabled action keeps every supported
successor in the candidate set.
-/
def RobustPre
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (candidate : State -> Prop) :
    State -> Prop :=
  fun x =>
    exists action,
      (exists y, support x action y) /\
      forall y, support x action y -> candidate y

theorem mayPre_eq_of_supportEquivalent
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (candidate : State -> Prop) :
    MayPre left candidate = MayPre right candidate := by
  funext x
  apply propext
  constructor
  · intro hx
    match hx with
    | Exists.intro action ha =>
        match ha with
        | Exists.intro y hy =>
            exact Exists.intro action
              (Exists.intro y
                (And.intro
                  ((hSupport x action y).mp hy.left)
                  hy.right))
  · intro hx
    match hx with
    | Exists.intro action ha =>
        match ha with
        | Exists.intro y hy =>
            exact Exists.intro action
              (Exists.intro y
                (And.intro
                  ((hSupport x action y).mpr hy.left)
                  hy.right))

theorem robustPre_eq_of_supportEquivalent
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (candidate : State -> Prop) :
    RobustPre left candidate = RobustPre right candidate := by
  funext x
  apply propext
  constructor
  · intro hx
    match hx with
    | Exists.intro action ha =>
        exact Exists.intro action
          (And.intro
            (match ha.left with
              | Exists.intro y hy =>
                  Exists.intro y ((hSupport x action y).mp hy))
            (by
              intro y hy
              exact ha.right y ((hSupport x action y).mpr hy)))
  · intro hx
    match hx with
    | Exists.intro action ha =>
        exact Exists.intro action
          (And.intro
            (match ha.left with
              | Exists.intro y hy =>
                  Exists.intro y ((hSupport x action y).mpr hy))
            (by
              intro y hy
              exact ha.right y ((hSupport x action y).mp hy)))

/-- Least-fixed-point support reachability operator. -/
def reachOp
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (target : State -> Prop)
    (candidate : State -> Prop) :
    State -> Prop :=
  fun x => target x \/ MayPre support candidate x

/-- Greatest-fixed-point robust support viability operator. -/
def viabilityOp
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (safe : State -> Prop)
    (candidate : State -> Prop) :
    State -> Prop :=
  fun x => safe x /\ RobustPre support candidate x

/-- Support-only least-fixed-point reachability. -/
def Reach
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (target : State -> Prop) :
    State -> Prop :=
  lfp (reachOp support target)

/-- Support-only greatest-fixed-point robust viability. -/
def Viable
    {State : Type u}
    {Action : Type v}
    (support : Support State Action)
    (safe : State -> Prop) :
    State -> Prop :=
  gfp (viabilityOp support safe)

theorem reachOp_eq_of_supportEquivalent
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (target : State -> Prop) :
    reachOp left target = reachOp right target := by
  funext candidate x
  have hMay :
      MayPre left candidate x = MayPre right candidate x :=
    congrFun (mayPre_eq_of_supportEquivalent hSupport candidate) x
  exact propext (by
    constructor
    · intro hx
      cases hx with
      | inl hTarget =>
          exact Or.inl hTarget
      | inr hStep =>
          exact Or.inr (hMay.mp hStep)
    · intro hx
      cases hx with
      | inl hTarget =>
          exact Or.inl hTarget
      | inr hStep =>
          exact Or.inr (hMay.mpr hStep))

theorem viabilityOp_eq_of_supportEquivalent
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (safe : State -> Prop) :
    viabilityOp left safe = viabilityOp right safe := by
  funext candidate x
  have hRobust :
      RobustPre left candidate x = RobustPre right candidate x :=
    congrFun (robustPre_eq_of_supportEquivalent hSupport candidate) x
  exact propext (by
    constructor
    · intro hx
      exact And.intro hx.left (hRobust.mp hx.right)
    · intro hx
      exact And.intro hx.left (hRobust.mpr hx.right))

/--
Equal action-labelled support implies equal support-only reachability for every
target predicate.
-/
theorem supportEquivalent_preserves_reach
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (target : State -> Prop) :
    Reach left target = Reach right target := by
  unfold Reach
  rw [reachOp_eq_of_supportEquivalent hSupport target]

/--
Equal action-labelled support implies equal support-only robust viability for
every safe predicate.
-/
theorem supportEquivalent_preserves_viability
    {State : Type u}
    {Action : Type v}
    {left right : Support State Action}
    (hSupport : SupportEquivalent left right)
    (safe : State -> Prop) :
    Viable left safe = Viable right safe := by
  unfold Viable
  rw [viabilityOp_eq_of_supportEquivalent hSupport safe]

end SupportBlindness
end Foundation
end OmegaProper
