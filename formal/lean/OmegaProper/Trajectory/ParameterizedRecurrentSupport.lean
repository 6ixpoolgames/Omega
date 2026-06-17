import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.ParameterizedRecurrentSupport

Parameterized finite recurrent-support witnesses.

The earlier recurrent-support loss/restoration witnesses use a two-state cycle.
This file generalizes the basic shape to every bounded finite cycle of size
`n + 2`, represented as the Nat support `{x | x <= n + 1}`.

The full dynamics walks forward and wraps from `n + 1` to `0`, so the declared
support is recurrent and carries the consequence distinction between `0` and
`1`. The broken dynamics keeps the forward path and endpoint viability, but
replaces the wrap with a terminal self-loop at `n + 1`; then `1` cannot return
to `0`, so recurrent carrying is lost.

This is still finite, local, and pair-relative. It does not define identity,
agency, deformer structure, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace ParameterizedRecurrentSupport

open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentViableClass
open SustainingViableClass

/-! ## Parameterized bounded cycle -/

/-- The support of the bounded cycle of size `n + 2`. -/
def boundedCycleSupport (n : Nat) (x : Nat) : Prop :=
  x <= n + 1

/-- All states in the bounded family are safe. -/
def boundedCycleSafe (_x : Nat) : Prop :=
  True

/--
Full bounded cycle dynamics: move forward until `n + 1`, then wrap to `0`.
-/
def boundedCycleNext (n : Nat) (x y : Nat) : Prop :=
  (x < n + 1 /\ y = x + 1) \/
    (x = n + 1 /\ y = 0)

abbrev boundedCycleDyn (n : Nat) : Dyn where
  State := Nat
  Next := boundedCycleNext n

/--
Broken bounded dynamics: move forward until `n + 1`, then remain at `n + 1`.

This preserves the forward path from `0` to `1` and endpoint viability, but it
removes the return path from `1` to `0`.
-/
def boundedBrokenNext (n : Nat) (x y : Nat) : Prop :=
  (x < n + 1 /\ y = x + 1) \/
    (x = n + 1 /\ y = n + 1)

abbrev boundedBrokenDyn (n : Nat) : Dyn where
  State := Nat
  Next := boundedBrokenNext n

/-! ## Consequence distinction between endpoints -/

inductive EndpointContext where
  | ctx
  deriving DecidableEq

inductive EndpointOutcome where
  | left
  | right
  | other
  deriving DecidableEq

def endpointOutcome : Nat -> EndpointOutcome
  | 0 => EndpointOutcome.left
  | 1 => EndpointOutcome.right
  | _ => EndpointOutcome.other

def endpointCompare : EndpointContext -> EndpointOutcome -> EndpointOutcome -> Prop
  | EndpointContext.ctx, a, b => a = b

/--
The parameterized family uses a fixed consequence test that separates endpoint
`0` from endpoint `1`.
-/
abbrev endpointConsequenceSystem : ConsequenceSystem where
  Fragment := Nat
  Context := EndpointContext
  Outcome := EndpointOutcome
  consequence := fun _ x => endpointOutcome x
  Compare := endpointCompare
  Evaluated := fun _ => True

theorem endpoint_zero_separated_one :
    ConsequenceSeparated endpointConsequenceSystem (0 : Nat) (1 : Nat) := by
  exists EndpointContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem endpoint_zero_mergeSeparated_one :
    ConsequenceMergeSeparated endpointConsequenceSystem (0 : Nat) (1 : Nat) := by
  exact separated_implies_mergeSeparated endpoint_zero_separated_one

/-! ## Internal path helpers -/

theorem internalPath_trans
    {D : Dyn}
    {C : D.State -> Prop}
    {x y z : D.State}
    (hxy : InternalPath D C x y)
    (hyz : InternalPath D C y z) :
    InternalPath D C x z := by
  induction hxy with
  | refl _hx =>
      exact hyz
  | step hx hy hStep _hRest ih =>
      exact InternalPath.step hx hy hStep (ih hyz)

theorem boundedCycle_step_forward
    {n x : Nat}
    (hx : x < n + 1) :
    boundedCycleNext n x (x + 1) := by
  exact Or.inl (And.intro hx rfl)

theorem boundedCycle_step_wrap
    (n : Nat) :
    boundedCycleNext n (n + 1) 0 := by
  exact Or.inr (And.intro rfl rfl)

theorem boundedBroken_step_forward
    {n x : Nat}
    (hx : x < n + 1) :
    boundedBrokenNext n x (x + 1) := by
  exact Or.inl (And.intro hx rfl)

theorem boundedBroken_step_terminal
    (n : Nat) :
    boundedBrokenNext n (n + 1) (n + 1) := by
  exact Or.inr (And.intro rfl rfl)

/--
Inside the bounded cycle, every ordered pair `i <= j` has the obvious forward
internal path along the line.
-/
theorem boundedCycle_path_up_to
    (n i j : Nat)
    (hij : i <= j)
    (hj : boundedCycleSupport n j) :
    InternalPath
      (dynFromNext (boundedCycleNext n))
      (boundedCycleSupport n)
      i
      j := by
  induction j generalizing i with
  | zero =>
      have hi0 : i = 0 := by omega
      subst hi0
      exact InternalPath.refl hj
  | succ j ih =>
      by_cases hEq : i = Nat.succ j
      case pos =>
        subst hEq
        exact InternalPath.refl hj
      case neg =>
        have hij' : i <= j := by omega
        have hjSupport : boundedCycleSupport n j := by
          unfold boundedCycleSupport at hj
          unfold boundedCycleSupport
          omega
        have hPath :
            InternalPath
              (dynFromNext (boundedCycleNext n))
              (boundedCycleSupport n)
              i
              j :=
          ih i hij' hjSupport
        have hStep :
            boundedCycleNext n j (j + 1) := by
          exact boundedCycle_step_forward (by
            unfold boundedCycleSupport at hj
            omega)
        have hOne :
            InternalPath
              (dynFromNext (boundedCycleNext n))
              (boundedCycleSupport n)
              j
              (j + 1) :=
          internalPath_single_step hjSupport hj hStep
        exact internalPath_trans hPath hOne

/--
The bounded cycle is internally path-connected: from any supported state to
any supported state, walk forward and wrap if needed.
-/
theorem boundedCycle_internalPath
    (n : Nat)
    {i j : Nat}
    (hi : boundedCycleSupport n i)
    (hj : boundedCycleSupport n j) :
    InternalPath
      (dynFromNext (boundedCycleNext n))
      (boundedCycleSupport n)
      i
      j := by
  cases Nat.le_total i j with
  | inl hij =>
      exact boundedCycle_path_up_to n i j hij hj
  | inr hji =>
      by_cases hEq : i = j
      case pos =>
        subst hEq
        exact InternalPath.refl hi
      case neg =>
        have hToLast :
            InternalPath
              (dynFromNext (boundedCycleNext n))
              (boundedCycleSupport n)
              i
              (n + 1) :=
          boundedCycle_path_up_to n i (n + 1) hi (by
            unfold boundedCycleSupport
            omega)
        have hWrap :
            InternalPath
              (dynFromNext (boundedCycleNext n))
              (boundedCycleSupport n)
              (n + 1)
              (0 : Nat) :=
          internalPath_single_step
            (by
              unfold boundedCycleSupport
              omega)
            (by
              unfold boundedCycleSupport
              omega)
            (boundedCycle_step_wrap n)
        have hFromZero :
            InternalPath
              (dynFromNext (boundedCycleNext n))
              (boundedCycleSupport n)
              (0 : Nat)
              j :=
          boundedCycle_path_up_to n (0 : Nat) j (by omega) hj
        exact internalPath_trans hToLast (internalPath_trans hWrap hFromZero)

/-! ## Full cycle recurrent carrying -/

theorem boundedCycle_classSafe
    (n : Nat) :
    ClassSafe boundedCycleSafe (boundedCycleSupport n) := by
  intro x hx
  trivial

theorem boundedCycle_classClosed
    (n : Nat) :
    ClassClosed (boundedCycleDyn n) (boundedCycleSupport n) := by
  intro x y hx hStep
  cases hStep with
  | inl hForward =>
      cases hForward with
      | intro hLt hyEq =>
          rw [hyEq]
          exact Nat.succ_le_of_lt hLt
  | inr hWrap =>
      cases hWrap with
      | intro _hxLast hyEq =>
          rw [hyEq]
          exact Nat.zero_le (n + 1)

theorem boundedCycle_stronglyConnected
    (n : Nat) :
    ClassStronglyConnected
      (dynFromNext (boundedCycleNext n))
      (boundedCycleSupport n) := by
  intro x y hx hy
  exact boundedCycle_internalPath n hx hy

theorem boundedCycle_hasSuccessor
    (n : Nat) :
    ClassHasSuccessorIn (boundedCycleDyn n) (boundedCycleSupport n) := by
  intro x hx
  by_cases hLt : x < n + 1
  case pos =>
    exact Exists.intro (x + 1)
      (And.intro
        (Nat.succ_le_of_lt hLt)
        (boundedCycle_step_forward hLt))
  case neg =>
    have hxLast : x = n + 1 := by
      exact Nat.le_antisymm hx (Nat.le_of_not_gt hLt)
    subst hxLast
    exact Exists.intro (0 : Nat)
      (And.intro
        (Nat.zero_le (n + 1))
        (boundedCycle_step_wrap n))

theorem boundedCycle_recurrent
    (n : Nat) :
    RecurrentViableClass
      (dynFromNext (boundedCycleNext n))
      boundedCycleSafe
      (boundedCycleSupport n) := by
  exact And.intro
    (boundedCycle_classSafe n)
    (And.intro
      (boundedCycle_classClosed n)
      (And.intro
        (boundedCycle_stronglyConnected n)
        (boundedCycle_hasSuccessor n)))

theorem boundedCycle_supports_zero_one
    (n : Nat) :
    SupportsMergeSeparatedPair
      endpointConsequenceSystem
      (boundedCycleNext n)
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact And.intro
    (by
      unfold boundedCycleSupport
      omega)
    (And.intro
      (by
        unfold boundedCycleSupport
        omega)
      (And.intro
        (boundedCycle_internalPath n
          (by
            unfold boundedCycleSupport
            omega)
          (by
            unfold boundedCycleSupport
            omega))
        (And.intro
          (boundedCycle_internalPath n
            (by
              unfold boundedCycleSupport
              omega)
            (by
              unfold boundedCycleSupport
              omega))
          endpoint_zero_mergeSeparated_one)))

theorem boundedCycle_recurrentSupportCarries_zero_one
    (n : Nat) :
    RecurrentSupportCarries
      endpointConsequenceSystem
      (boundedCycleNext n)
      boundedCycleSafe
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact And.intro
    (boundedCycle_recurrent n)
    (boundedCycle_supports_zero_one n)

/-! ## Broken family: viability and forward reachability remain, return fails -/

theorem boundedBroken_classClosed
    (n : Nat) :
    ClassClosed (boundedBrokenDyn n) (boundedCycleSupport n) := by
  intro x y hx hStep
  cases hStep with
  | inl hForward =>
      cases hForward with
      | intro hLt hyEq =>
          rw [hyEq]
          exact Nat.succ_le_of_lt hLt
  | inr hTerminal =>
      cases hTerminal with
      | intro _hxLast hyEq =>
          rw [hyEq]
          exact Nat.le_refl (n + 1)

theorem boundedBroken_hasSuccessor
    (n : Nat) :
    ClassHasSuccessorIn (boundedBrokenDyn n) (boundedCycleSupport n) := by
  intro x hx
  by_cases hLt : x < n + 1
  case pos =>
    exact Exists.intro (x + 1)
      (And.intro
        (Nat.succ_le_of_lt hLt)
        (boundedBroken_step_forward hLt))
  case neg =>
    have hxLast : x = n + 1 := by
      exact Nat.le_antisymm hx (Nat.le_of_not_gt hLt)
    subst hxLast
    exact Exists.intro (n + 1)
      (And.intro
        (by
          unfold boundedCycleSupport
          omega)
        (boundedBroken_step_terminal n))

theorem boundedBroken_closedSustaining
    (n : Nat) :
    ClosedSustainingViableClass
      (boundedBrokenDyn n)
      boundedCycleSafe
      (boundedCycleSupport n) := by
  exact And.intro
    (boundedCycle_classSafe n)
    (And.intro
      (boundedBroken_classClosed n)
      (boundedBroken_hasSuccessor n))

theorem boundedBroken_zero_viable
    (n : Nat) :
    Viable (boundedBrokenDyn n) boundedCycleSafe 0 := by
  exact closedSustainingClass_member_viable
    (boundedBroken_closedSustaining n)
    (by
      unfold boundedCycleSupport
      omega)

theorem boundedBroken_one_viable
    (n : Nat) :
    Viable (boundedBrokenDyn n) boundedCycleSafe 1 := by
  exact closedSustainingClass_member_viable
    (boundedBroken_closedSustaining n)
    (by
      unfold boundedCycleSupport
      omega)

theorem boundedBroken_zero_path_one
    (n : Nat) :
    InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact internalPath_single_step
    (by
      unfold boundedCycleSupport
      omega)
    (by
      unfold boundedCycleSupport
      omega)
    (boundedBroken_step_forward (Nat.succ_pos n))

/--
Internal paths preserve any predicate that every internal step preserves.
-/
theorem internalPath_preserves_stepInvariant
    {D : Dyn}
    {C P : D.State -> Prop}
    {x y : D.State}
    (hInvariant :
      forall a b,
        C a ->
        C b ->
        D.Next a b ->
        P a ->
        P b)
    (hx : P x)
    (hPath : InternalPath D C x y) :
    P y := by
  induction hPath with
  | refl _hMem =>
      exact hx
  | step hxMem hyMem hEdge _hRest ih =>
      exact ih (hInvariant _ _ hxMem hyMem hEdge hx)

def PositiveState (x : Nat) : Prop :=
  1 <= x

theorem boundedBrokenNext_preserves_positive
    (n : Nat) :
    forall a b,
      boundedCycleSupport n a ->
      boundedCycleSupport n b ->
      boundedBrokenNext n a b ->
      PositiveState a ->
      PositiveState b := by
  intro a b _ha _hb hStep hPos
  cases hStep with
  | inl hForward =>
      cases hForward with
      | intro _hLt hbEq =>
          rw [hbEq]
          unfold PositiveState at hPos
          unfold PositiveState
          omega
  | inr hTerminal =>
      cases hTerminal with
      | intro _hLast hbEq =>
          rw [hbEq]
          unfold PositiveState
          omega

theorem boundedBroken_no_path_one_zero
    (n : Nat) :
    Not (InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (1 : Nat)
      (0 : Nat)) := by
  intro hPath
  have hPositiveZero : PositiveState 0 :=
    internalPath_preserves_stepInvariant
      (boundedBrokenNext_preserves_positive n)
      (Nat.le_refl 1)
      hPath
  unfold PositiveState at hPositiveZero
  exact Nat.not_succ_le_zero 0 hPositiveZero

theorem boundedBroken_not_recurrentSupportCarries_zero_one
    (n : Nat) :
    Not (RecurrentSupportCarries
      endpointConsequenceSystem
      (boundedBrokenNext n)
      boundedCycleSafe
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat)) := by
  exact not_recurrentSupportCarries_if_reverse_path_missing
    (boundedBroken_no_path_one_zero n)

theorem boundedBroken_destroys_recurrent_support
    (n : Nat) :
    RecurrentSupportDestroyedUnder
      endpointConsequenceSystem
      (boundedCycleNext n)
      (boundedBrokenNext n)
      boundedCycleSafe
      boundedCycleSafe
      (boundedCycleSupport n)
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact recurrentSupportDestroyed_if_reverse_path_missing
    (boundedCycle_recurrentSupportCarries_zero_one n)
    (boundedBroken_no_path_one_zero n)

theorem parameterized_recurrent_support_loss_witness
    (n : Nat) :
    RecurrentSupportCarries
      endpointConsequenceSystem
      (boundedCycleNext n)
      boundedCycleSafe
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) /\
    Viable (boundedBrokenDyn n) boundedCycleSafe (0 : Nat) /\
    Viable (boundedBrokenDyn n) boundedCycleSafe (1 : Nat) /\
    InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) /\
    Not (InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (1 : Nat)
      (0 : Nat)) /\
    RecurrentSupportDestroyedUnder
      endpointConsequenceSystem
      (boundedCycleNext n)
      (boundedBrokenNext n)
      boundedCycleSafe
      boundedCycleSafe
      (boundedCycleSupport n)
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact And.intro
    (boundedCycle_recurrentSupportCarries_zero_one n)
    (And.intro
      (boundedBroken_zero_viable n)
      (And.intro
        (boundedBroken_one_viable n)
        (And.intro
          (boundedBroken_zero_path_one n)
          (And.intro
            (boundedBroken_no_path_one_zero n)
            (boundedBroken_destroys_recurrent_support n)))))

end ParameterizedRecurrentSupport
end Trajectory
end OmegaProper
