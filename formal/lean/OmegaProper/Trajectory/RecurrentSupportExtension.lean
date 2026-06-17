import OmegaProper.Trajectory.RecurrentSupportPathTransfer

/-!
OmegaProper.Trajectory.RecurrentSupportExtension

Support-extension transfer for recurrent supports carrying consequence
distinctions.

The previous transfer layers are same-support contracts: a declared support
`C` carries before and the same declared support `C` carries after. This file
adds a conservative moving-support step: carrying can transfer from `C` into a
larger or different declared support `D` when old internal paths in `C` are
replaceable by new internal paths in `D`, and `D` is recurrent viable under the
new dynamics.

This is a sufficient contract, not a recoverability or identity theorem. It
does not define agency, deformer structure, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportExtension

open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportPathTransfer
open RecurrentSupportRobustness
open RecurrentSupportTransfer
open RecurrentViableClass
open SustainingViableClass

universe w k o

/--
Old internal paths in support `C` are replaceable by new internal paths inside
support `D`.
-/
def InternalPathsPreservedInto
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C D : X -> Prop) : Prop :=
  forall x y,
    C x ->
    C y ->
    InternalPath (dynFromNext Next0) C x y ->
      InternalPath (dynFromNext Next1) D x y

/--
Each old internal edge in `C` is replaceable by a new internal path inside
`D`.
-/
def InternalEdgesPathPreservedInto
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C D : X -> Prop) : Prop :=
  forall x y,
    C x ->
    C y ->
    Next0 x y ->
      InternalPath (dynFromNext Next1) D x y

/--
Support-extension transfer contract.

`C` is the source support and `D` is the target support. The contract requires:

* every source support member lies in the target support;
* the target support is recurrent viable under the changed dynamics;
* old internal source paths are replaceable by target-support paths.
-/
def RecurrentSupportExtensionContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe1 : X -> Prop)
    (C D : X -> Prop) : Prop :=
  SupportSub C D /\
    RecurrentViableClass (dynFromNext Next1) safe1 D /\
    InternalPathsPreservedInto Next0 Next1 C D

def internalPathExtendOfEdgePaths
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    {x y : X}
    (hSub : SupportSub C D)
    (hEdges : InternalEdgesPathPreservedInto Next0 Next1 C D)
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    InternalPath (dynFromNext Next1) D x y :=
  match hPath with
  | InternalPath.refl hx =>
      InternalPath.refl (hSub _ hx)
  | InternalPath.step hx hy hEdge rest =>
      internalPathAppend
        (hEdges _ _ hx hy hEdge)
        (internalPathExtendOfEdgePaths hSub hEdges rest)

theorem internalPathsPreservedInto_of_edgePaths
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    (hSub : SupportSub C D)
    (hEdges : InternalEdgesPathPreservedInto Next0 Next1 C D) :
    InternalPathsPreservedInto Next0 Next1 C D := by
  intro x y _hx _hy hPath
  exact internalPathExtendOfEdgePaths hSub hEdges hPath

theorem supportsMergeSeparatedPair_extends_of_paths
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x y)
    (hSub : SupportSub C D)
    (hPaths : InternalPathsPreservedInto Next0 Next1 C D) :
    SupportsMergeSeparatedPair S Next1 D x y := by
  exact And.intro
    (hSub x hSupport.left)
    (And.intro
      (hSub y hSupport.right.left)
      (And.intro
        (hPaths x y
          hSupport.left
          hSupport.right.left
          hSupport.right.right.left)
        (And.intro
          (hPaths y x
            hSupport.right.left
            hSupport.left
            hSupport.right.right.right.left)
          hSupport.right.right.right.right)))

theorem recurrentSupportCarries_extends_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hContract : RecurrentSupportExtensionContract Next0 Next1 safe1 C D) :
    RecurrentSupportCarries S Next1 safe1 D x y := by
  exact And.intro
    hContract.right.left
    (supportsMergeSeparatedPair_extends_of_paths
      hCarry.right
      hContract.left
      hContract.right.right)

theorem recurrentSupportIntegrity_of_extension_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hContract : RecurrentSupportExtensionContract Next0 Next1 safe1 C D) :
    RecurrentSupportIntegrityUnder S Next0 Next1 safe0 safe1 C D x y := by
  intro hCarry
  exact recurrentSupportCarries_extends_of_contract hCarry hContract

theorem sameSupportPathContract_implies_extensionContract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    (hRec : RecurrentViableClass (dynFromNext Next0) safe0 C)
    (hContract : RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportExtensionContract Next0 Next1 safe1 C C := by
  exact And.intro
    (by
      intro x hx
      exact hx)
    (And.intro
      (recurrentViableClass_transfer_of_path_contract hRec hContract)
      (by
        intro x y _hx _hy hPath
        exact hContract.right.right.left x y hPath))

/-! ## Finite strict-extension witness -/

/-- Source support containing only the two endpoint states. -/
def endpointRerouteClass : RerouteState -> Prop
  | RerouteState.left => True
  | RerouteState.mid => False
  | RerouteState.right => True

/-- Source dynamics: the two endpoint states form a direct cycle. -/
def endpointCycleNext : RerouteState -> RerouteState -> Prop
  | RerouteState.left, RerouteState.right => True
  | RerouteState.right, RerouteState.left => True
  | _, _ => False

theorem endpointReroute_sub_rerouteClass :
    SupportSub endpointRerouteClass rerouteClass := by
  intro x _hx
  trivial

theorem endpointCycle_recurrent :
    RecurrentViableClass
      (dynFromNext endpointCycleNext)
      rerouteSafe
      endpointRerouteClass := by
  exact And.intro
    (by
      intro x hx
      cases x <;> trivial)
    (And.intro
      (by
        intro x y hx hStep
        cases x <;> cases y <;> trivial)
      (And.intro
        (by
          intro x y hx hy
          cases x <;> cases y
          case left.left =>
            exact InternalPath.refl hx
          case left.mid =>
            exact False.elim hy
          case left.right =>
            exact internalPath_single_step hx hy trivial
          case mid.left =>
            exact False.elim hx
          case mid.mid =>
            exact False.elim hx
          case mid.right =>
            exact False.elim hx
          case right.left =>
            exact internalPath_single_step hx hy trivial
          case right.mid =>
            exact False.elim hy
          case right.right =>
            exact InternalPath.refl hx)
        (by
          intro x hx
          cases x
          case left =>
            exact Exists.intro RerouteState.right (And.intro trivial trivial)
          case mid =>
            exact False.elim hx
          case right =>
            exact Exists.intro RerouteState.left (And.intro trivial trivial))))

theorem endpointCycle_supports_left_right :
    SupportsMergeSeparatedPair
      rerouteConsequenceSystem
      endpointCycleNext
      endpointRerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        (internalPath_single_step trivial trivial trivial)
        (And.intro
          (internalPath_single_step trivial trivial trivial)
          (separated_implies_mergeSeparated
            reroute_left_separated_right))))

theorem endpointCycle_recurrentSupportCarries_left_right :
    RecurrentSupportCarries
      rerouteConsequenceSystem
      endpointCycleNext
      rerouteSafe
      endpointRerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro endpointCycle_recurrent endpointCycle_supports_left_right

theorem endpointCycle_edges_preserved_into_rerouted :
    InternalEdgesPathPreservedInto
      endpointCycleNext
      reroutedReturnNext
      endpointRerouteClass
      rerouteClass := by
  intro x y _hx _hy hEdge
  cases x <;> cases y
  case left.left =>
    exact False.elim hEdge
  case left.mid =>
    exact False.elim hEdge
  case left.right =>
    exact internalPath_single_step trivial trivial trivial
  case mid.left =>
    exact False.elim hEdge
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

theorem endpointCycle_extends_into_rerouted_contract :
    RecurrentSupportExtensionContract
      endpointCycleNext
      reroutedReturnNext
      rerouteSafe
      endpointRerouteClass
      rerouteClass := by
  exact And.intro
    endpointReroute_sub_rerouteClass
    (And.intro
      rerouted_preserves_recurrentSupport_by_path_contract.left
      (internalPathsPreservedInto_of_edgePaths
        endpointReroute_sub_rerouteClass
        endpointCycle_edges_preserved_into_rerouted))

theorem endpointCycle_extends_into_rerouted_carrying :
    RecurrentSupportCarries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact recurrentSupportCarries_extends_of_contract
    endpointCycle_recurrentSupportCarries_left_right
    endpointCycle_extends_into_rerouted_contract

theorem strict_support_extension_witness :
    ProperSupportSub endpointRerouteClass rerouteClass /\
    RecurrentSupportCarries
      rerouteConsequenceSystem
      endpointCycleNext
      rerouteSafe
      endpointRerouteClass
      RerouteState.left
      RerouteState.right /\
    RecurrentSupportExtensionContract
      endpointCycleNext
      reroutedReturnNext
      rerouteSafe
      endpointRerouteClass
      rerouteClass /\
    RecurrentSupportCarries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact And.intro
    (And.intro
      endpointReroute_sub_rerouteClass
      (Exists.intro RerouteState.mid (And.intro trivial id)))
    (And.intro
      endpointCycle_recurrentSupportCarries_left_right
      (And.intro
        endpointCycle_extends_into_rerouted_contract
        endpointCycle_extends_into_rerouted_carrying))

end RecurrentSupportExtension
end Trajectory
end OmegaProper
