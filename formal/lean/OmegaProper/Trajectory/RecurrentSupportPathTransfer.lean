import OmegaProper.Trajectory.RecurrentSupportTransfer

/-!
OmegaProper.Trajectory.RecurrentSupportPathTransfer

Path-level transfer contracts for recurrent supports.

`RecurrentSupportTransfer` uses edge preservation: every old internal support
edge must remain available after the dynamics change. This file records a
weaker sufficient contract: old internal paths must be replaceable by new
internal paths. Edges may be rerouted.

The contract still requires safety transfer, no exits from the declared
support, and changed-dynamics successors, because recurrence includes safety,
closure, strong connectivity, and one-step sustaining.

This does not define identity, agency, deformer structure, value, alignment,
or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportPathTransfer

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentSupportTransfer
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/-- Append two internal paths inside the same declared support. -/
def internalPathAppend
    {D : Dyn.{w}}
    {C : D.State -> Prop}
    {x y z : D.State}
    (p : InternalPath D C x y)
    (q : InternalPath D C y z) :
    InternalPath D C x z :=
  match p with
  | InternalPath.refl _hx =>
      q
  | InternalPath.step hx hy hEdge rest =>
      InternalPath.step hx hy hEdge (internalPathAppend rest q)

/-- Old internal paths are replaceable by new internal paths. -/
def InternalPathsPreservedOn
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C : X -> Prop) : Prop :=
  forall x y,
    InternalPath (dynFromNext Next0) C x y ->
      InternalPath (dynFromNext Next1) C x y

/--
Each old internal edge is replaceable by a new internal path.

This is a useful sufficient condition for `InternalPathsPreservedOn`, weaker
than preserving each edge as an edge.
-/
def InternalEdgesPathPreservedOn
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C : X -> Prop) : Prop :=
  forall x y,
    C x ->
    C y ->
    Next0 x y ->
      InternalPath (dynFromNext Next1) C x y

/-- The changed dynamics has an internal successor for every support member. -/
def SuccessorsAvailableOn
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : X -> Prop) : Prop :=
  ClassHasSuccessorIn (dynFromNext Next) C

/--
Same-support path-level transfer contract.

Compared to `RecurrentSupportTransferContract`, this replaces edge
preservation with path preservation and separately requires changed-dynamics
successors.
-/
def RecurrentSupportPathTransferContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe0 safe1 : X -> Prop)
    (C : X -> Prop) : Prop :=
  SafeTransfersOn C safe0 safe1 /\
    NoNewExitsFrom Next1 C /\
    InternalPathsPreservedOn Next0 Next1 C /\
    SuccessorsAvailableOn Next1 C

def internalPathTransferOfEdgePaths
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C : X -> Prop}
    {x y : X}
    (hEdges : InternalEdgesPathPreservedOn Next0 Next1 C)
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    InternalPath (dynFromNext Next1) C x y :=
  match hPath with
  | InternalPath.refl hx =>
      InternalPath.refl hx
  | InternalPath.step hx hy hEdge rest =>
      internalPathAppend
        (hEdges _ _ hx hy hEdge)
        (internalPathTransferOfEdgePaths hEdges rest)

theorem internalPathsPreserved_of_edgePathPreserved
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C : X -> Prop}
    (hEdges : InternalEdgesPathPreservedOn Next0 Next1 C) :
    InternalPathsPreservedOn Next0 Next1 C := by
  intro x y hPath
  exact internalPathTransferOfEdgePaths hEdges hPath

theorem internalPathsPreserved_of_edgesPreserved
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C : X -> Prop}
    (hEdges : InternalEdgesPreservedOn Next0 Next1 C) :
    InternalPathsPreservedOn Next0 Next1 C := by
  exact internalPathsPreserved_of_edgePathPreserved
    (by
      intro x y hx hy hEdge
      exact internalPath_single_step hx hy (hEdges x y hx hy hEdge))

theorem recurrentViableClass_transfer_of_path_contract
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {safe0 safe1 C : X -> Prop}
    (hRec : RecurrentViableClass (dynFromNext Next0) safe0 C)
    (hContract :
      RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentViableClass (dynFromNext Next1) safe1 C := by
  exact And.intro
    (by
      intro x hx
      exact hContract.left x hx (hRec.left x hx))
    (And.intro
      (by
        intro x y hx hStep
        exact hContract.right.left x y hx hStep)
      (And.intro
        (by
          intro x y hx hy
          exact hContract.right.right.left x y
            (hRec.right.right.left x y hx hy))
        hContract.right.right.right))

theorem supportsMergeSeparatedPair_transfer_of_paths
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x y)
    (hPaths : InternalPathsPreservedOn Next0 Next1 C) :
    SupportsMergeSeparatedPair S Next1 C x y := by
  exact And.intro
    hSupport.left
    (And.intro
      hSupport.right.left
      (And.intro
        (hPaths x y hSupport.right.right.left)
        (And.intro
          (hPaths y x hSupport.right.right.right.left)
          hSupport.right.right.right.right)))

theorem recurrentSupportCarries_transfers_of_path_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hContract :
      RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportCarries S Next1 safe1 C x y := by
  exact And.intro
    (recurrentViableClass_transfer_of_path_contract hCarry.left hContract)
    (supportsMergeSeparatedPair_transfer_of_paths
      hCarry.right
      hContract.right.right.left)

theorem recurrentSupportIntegrity_of_path_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hContract :
      RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportIntegrityUnder
      S
      Next0
      Next1
      safe0
      safe1
      C
      C
      x
      y := by
  intro hCarry
  exact recurrentSupportCarries_transfers_of_path_contract hCarry hContract

theorem edgeTransferContract_implies_pathTransferContract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    (hRec : RecurrentViableClass (dynFromNext Next0) safe0 C)
    (hContract : RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C := by
  exact And.intro
    hContract.left
    (And.intro
      hContract.right.left
      (And.intro
        (internalPathsPreserved_of_edgesPreserved hContract.right.right)
        (by
          intro x hx
          match hRec.right.right.right x hx with
          | Exists.intro y hy =>
              exact Exists.intro y
                (And.intro
                  hy.left
                  (hContract.right.right x y hx hy.left hy.right)))))

/-! ## Tiny rerouting witness -/

inductive RerouteState where
  | left
  | mid
  | right
  deriving DecidableEq

def rerouteClass (_x : RerouteState) : Prop :=
  True

def rerouteSafe (_x : RerouteState) : Prop :=
  True

/--
Baseline dynamics has direct return edge `right -> left` and a side path
through `mid`.
-/
def directReturnNext : RerouteState -> RerouteState -> Prop
  | RerouteState.left, RerouteState.right => True
  | RerouteState.right, RerouteState.left => True
  | RerouteState.left, RerouteState.mid => True
  | RerouteState.mid, RerouteState.left => True
  | _, _ => False

/-- Rerouted dynamics replaces `right -> left` with `right -> mid -> left`. -/
def reroutedReturnNext : RerouteState -> RerouteState -> Prop
  | RerouteState.left, RerouteState.right => True
  | RerouteState.right, RerouteState.mid => True
  | RerouteState.mid, RerouteState.left => True
  | _, _ => False

inductive RerouteContext where
  | ctx
  deriving DecidableEq

def rerouteConsequenceSystem : ConsequenceSystem where
  Fragment := RerouteState
  Context := RerouteContext
  Outcome := RerouteState
  consequence := fun _ x => x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

theorem reroute_left_separated_right :
    ConsequenceSeparated
      rerouteConsequenceSystem
      RerouteState.left
      RerouteState.right := by
  exists RerouteContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem direct_path_left_mid :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.left
      RerouteState.mid := by
  exact internalPath_single_step trivial trivial trivial

theorem direct_path_left_right :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact internalPath_single_step trivial trivial trivial

theorem direct_path_mid_left :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.mid
      RerouteState.left := by
  exact internalPath_single_step trivial trivial trivial

theorem direct_path_mid_right :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.mid
      RerouteState.right := by
  exact internalPathAppend
    direct_path_mid_left
    direct_path_left_right

theorem direct_path_right_left :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.right
      RerouteState.left := by
  exact internalPath_single_step trivial trivial trivial

theorem direct_path_right_mid :
    InternalPath
      (dynFromNext directReturnNext)
      rerouteClass
      RerouteState.right
      RerouteState.mid := by
  exact internalPathAppend
    direct_path_right_left
    direct_path_left_mid

theorem directReturn_stronglyConnected :
    ClassStronglyConnected
      (dynFromNext directReturnNext)
      rerouteClass := by
  intro x y hx _hy
  cases x <;> cases y
  case left.left =>
    exact InternalPath.refl hx
  case left.mid =>
    exact direct_path_left_mid
  case left.right =>
    exact direct_path_left_right
  case mid.left =>
    exact direct_path_mid_left
  case mid.mid =>
    exact InternalPath.refl hx
  case mid.right =>
    exact direct_path_mid_right
  case right.left =>
    exact direct_path_right_left
  case right.mid =>
    exact direct_path_right_mid
  case right.right =>
    exact InternalPath.refl hx

theorem directReturn_recurrent :
    RecurrentViableClass
      (dynFromNext directReturnNext)
      rerouteSafe
      rerouteClass := by
  exact And.intro
    (by
      intro x _hx
      trivial)
    (And.intro
      (by
        intro x y _hx _hStep
        trivial)
      (And.intro
        directReturn_stronglyConnected
        (by
          intro x _hx
          cases x
          case left =>
            exact Exists.intro RerouteState.right (And.intro trivial trivial)
          case mid =>
            exact Exists.intro RerouteState.left (And.intro trivial trivial)
          case right =>
            exact Exists.intro RerouteState.left (And.intro trivial trivial))))

theorem directReturn_supports_left_right :
    SupportsMergeSeparatedPair
      rerouteConsequenceSystem
      directReturnNext
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        direct_path_left_right
        (And.intro
          direct_path_right_left
          (separated_implies_mergeSeparated
            reroute_left_separated_right))))

theorem directReturn_recurrentSupportCarries_left_right :
    RecurrentSupportCarries
      rerouteConsequenceSystem
      directReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro
    directReturn_recurrent
    directReturn_supports_left_right

theorem rerouted_edgePathPreserved :
    InternalEdgesPathPreservedOn
      directReturnNext
      reroutedReturnNext
      rerouteClass := by
  intro x y _hx _hy hEdge
  cases x <;> cases y
  case left.left =>
    exact False.elim hEdge
  case left.mid =>
    exact internalPathAppend
      (internalPath_single_step trivial trivial trivial :
        InternalPath
          (dynFromNext reroutedReturnNext)
          rerouteClass
          RerouteState.left
          RerouteState.right)
      (internalPath_single_step trivial trivial trivial :
        InternalPath
          (dynFromNext reroutedReturnNext)
          rerouteClass
          RerouteState.right
          RerouteState.mid)
  case left.right =>
    exact internalPath_single_step trivial trivial trivial
  case mid.left =>
    exact internalPath_single_step trivial trivial trivial
  case mid.mid =>
    exact False.elim hEdge
  case mid.right =>
    exact False.elim hEdge
  case right.left =>
    exact internalPathAppend
      (internalPath_single_step trivial trivial trivial :
        InternalPath
          (dynFromNext reroutedReturnNext)
          rerouteClass
          RerouteState.right
          RerouteState.mid)
      (internalPath_single_step trivial trivial trivial :
        InternalPath
          (dynFromNext reroutedReturnNext)
          rerouteClass
          RerouteState.mid
          RerouteState.left)
  case right.mid =>
    exact False.elim hEdge
  case right.right =>
    exact False.elim hEdge

theorem rerouted_pathTransfer_contract :
    RecurrentSupportPathTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass := by
  exact And.intro
    (by
      intro x _hx _hSafe
      trivial)
    (And.intro
      (by
        intro x y _hx _hStep
        trivial)
      (And.intro
        (internalPathsPreserved_of_edgePathPreserved
          rerouted_edgePathPreserved)
        (by
          intro x _hx
          cases x
          case left =>
            exact Exists.intro RerouteState.right (And.intro trivial trivial)
          case mid =>
            exact Exists.intro RerouteState.left (And.intro trivial trivial)
          case right =>
            exact Exists.intro RerouteState.mid (And.intro trivial trivial))))

theorem rerouted_not_internalEdgesPreserved :
    Not (InternalEdgesPreservedOn
      directReturnNext
      reroutedReturnNext
      rerouteClass) := by
  intro hEdges
  exact hEdges
    RerouteState.right
    RerouteState.left
    trivial
    trivial
    trivial

theorem rerouted_not_edgeTransfer_contract :
    Not (RecurrentSupportTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass) := by
  intro hContract
  exact rerouted_not_internalEdgesPreserved hContract.right.right

theorem rerouted_preserves_recurrentSupport_by_path_contract :
    RecurrentSupportCarries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact recurrentSupportCarries_transfers_of_path_contract
    directReturn_recurrentSupportCarries_left_right
    rerouted_pathTransfer_contract

theorem path_transfer_strictly_relaxes_edge_transfer_witness :
    Not (RecurrentSupportTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass) /\
    RecurrentSupportPathTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass /\
    RecurrentSupportCarries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro
    rerouted_not_edgeTransfer_contract
    (And.intro
      rerouted_pathTransfer_contract
      rerouted_preserves_recurrentSupport_by_path_contract)

end RecurrentSupportPathTransfer
end Trajectory
end OmegaProper
