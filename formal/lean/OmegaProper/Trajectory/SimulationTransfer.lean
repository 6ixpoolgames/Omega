import OmegaProper.Trajectory.GeneratedCarrier
import OmegaProper.Trajectory.RecurrentSupportPathTransfer

/-!
OmegaProper.Trajectory.SimulationTransfer

Map-based simulation transfer for carrier certificates.

The previous transfer files give direct sufficient contracts: preserve edges,
or preserve paths, on declared supports. This file adds a more principled
transfer surface. A map `f` simulates old internal edges by new internal paths,
keeps images inside the target carrier, and preserves merge separation of the
declared pair. Under a recurrent target carrier, carrier certificates transfer
to the mapped endpoints.

This is still a sufficient-condition layer. It does not define identity,
agency, deformer structure, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SimulationTransfer

open CarrierCertificate
open CarriedDistinction
open ConsequenceRelation
open DistinctionSupport
open GeneratedCarrier
open PathCarriedDistinction
open RecurrentSupportPathTransfer
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- Images of old carrier states lie in the target carrier. -/
def ImageInCarrier
    {X : Type w}
    (f : X -> X)
    (C D : X -> Prop) : Prop :=
  forall x, C x -> D (f x)

/--
Each old internal edge is simulated by a new internal path between mapped
endpoints.
-/
def InternalEdgeSimulatedByPath
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C D : X -> Prop)
    (f : X -> X) : Prop :=
  forall x y,
    C x ->
    C y ->
    Next0 x y ->
      InternalPath (dynFromNext Next1) D (f x) (f y)

/--
Old internal paths are simulated by new internal paths between mapped
endpoints.
-/
def InternalPathSimulated
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C D : X -> Prop)
    (f : X -> X) : Prop :=
  forall x y,
    InternalPath (dynFromNext Next0) C x y ->
      InternalPath (dynFromNext Next1) D (f x) (f y)

def internalPathSimulatedOfEdges
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    {f : X -> X}
    (hImage : ImageInCarrier f C D)
    (hStep : InternalEdgeSimulatedByPath Next0 Next1 C D f)
    {x y : X}
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    InternalPath (dynFromNext Next1) D (f x) (f y) :=
  match hPath with
  | InternalPath.refl hx =>
      InternalPath.refl (hImage _ hx)
  | InternalPath.step hx hy hEdge rest =>
      internalPathAppend
        (hStep _ _ hx hy hEdge)
        (internalPathSimulatedOfEdges hImage hStep rest)

/-- Edge-to-path simulation gives path simulation. -/
theorem internalPathSimulated_of_edgeSimulation
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    {f : X -> X}
    (hImage : ImageInCarrier f C D)
    (hStep : InternalEdgeSimulatedByPath Next0 Next1 C D f) :
    InternalPathSimulated Next0 Next1 C D f := by
  intro x y hPath
  exact internalPathSimulatedOfEdges hImage hStep hPath

/-- Merge separation of the declared pair is preserved by the map. -/
def MergeSeparationPreservedByMap
    (S : ConsequenceSystem.{w, k, o})
    (f : S.Fragment -> S.Fragment) : Prop :=
  forall x y,
    ConsequenceMergeSeparated S x y ->
      ConsequenceMergeSeparated S (f x) (f y)

/--
Map-based simulation transfer contract.

This contract is more principled than same-support edge preservation: it asks
for a map from old carrier states to target carrier states, edge-to-path
simulation under that map, target recurrence, and preservation of the declared
merge separation.
-/
def CarrierMapSimulationContract
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (f : S.Fragment -> S.Fragment) : Prop :=
  ImageInCarrier f C D /\
    InternalEdgeSimulatedByPath Next0 Next1 C D f /\
    RecurrentViableClass (dynFromNext Next1) safe1 D /\
    MergeSeparationPreservedByMap S f

theorem carrierMapSimulation_pathSimulation
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe1 : S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {f : S.Fragment -> S.Fragment}
    (hContract :
      CarrierMapSimulationContract S Next0 Next1 safe1 C D f) :
    InternalPathSimulated Next0 Next1 C D f := by
  exact internalPathSimulated_of_edgeSimulation
    hContract.left
    hContract.right.left

/--
Carrier certificates transfer through a map-based simulation contract.

The target endpoints are `f x` and `f y`; no identity of endpoints is assumed.
-/
theorem certificate_transfers_by_map_simulation
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 : S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {f : S.Fragment -> S.Fragment}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next0 safe0 C x y)
    (hContract :
      CarrierMapSimulationContract S Next0 Next1 safe1 C D f) :
    CarrierCertificate S Next1 safe1 D (f x) (f y) := by
  have hPaths :
      InternalPathSimulated Next0 Next1 C D f :=
    carrierMapSimulation_pathSimulation hContract
  exact And.intro
    hContract.right.right.left
    (And.intro
      (hContract.left x hCert.right.left)
      (And.intro
        (hContract.left y hCert.right.right.left)
        (And.intro
          (hPaths x y hCert.right.right.right.left)
          (And.intro
            (hPaths y x hCert.right.right.right.right.left)
            (hContract.right.right.right
              x
              y
              hCert.right.right.right.right.right)))))

/-! ## Tiny identity-simulation witness -/

theorem cycle_identity_simulation_contract :
    CarrierMapSimulationContract
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleClass
      cycleClass
      (fun x => x) := by
  exact And.intro
    (by
      intro x hx
      exact hx)
    (And.intro
      (by
        intro x y hx hy hStep
        exact internalPath_single_step hx hy hStep)
      (And.intro
        cycleClass_recurrent_fromNext
        (by
          intro x y hSep
          exact hSep)))

theorem cycle_certificate_transfers_by_identity_simulation :
    CarrierCertificate
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact certificate_transfers_by_map_simulation
    cycle_carrier_certificate
    cycle_identity_simulation_contract

/-! ## Relation-based simulation transfer -/

/-- A related target representative lies inside the target carrier. -/
def RelatedInCarrier
    {X : Type w}
    (R : X -> X -> Prop)
    (D : X -> Prop)
    (x x' : X) : Prop :=
  D x' /\ R x x'

/--
Each old internal edge is simulated from any related target representative by
a new internal path ending at some related representative of the old target.
-/
def InternalEdgeRelatedByPath
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C D : X -> Prop)
    (R : X -> X -> Prop) : Prop :=
  forall x x' y,
    C x ->
    D x' ->
    R x x' ->
    C y ->
    Next0 x y ->
      exists y',
        D y' /\
        R y y' /\
        InternalPath (dynFromNext Next1) D x' y'

/-- Merge separation is preserved across related representatives. -/
def MergeSeparationPreservedByRelation
    (S : ConsequenceSystem.{w, k, o})
    (R : S.Fragment -> S.Fragment -> Prop) : Prop :=
  forall x y x' y',
    R x x' ->
    R y y' ->
    ConsequenceMergeSeparated S x y ->
      ConsequenceMergeSeparated S x' y'

/--
Relation-based simulation transfer contract.

This is more general than the map-based contract: one old state may have many
related target representatives.
-/
def CarrierRelationSimulationContract
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (R : S.Fragment -> S.Fragment -> Prop) : Prop :=
  RecurrentViableClass (dynFromNext Next1) safe1 D /\
    InternalEdgeRelatedByPath Next0 Next1 C D R /\
    MergeSeparationPreservedByRelation S R

/-- The graph relation induced by a map. -/
def GraphRelation
    {X : Type w}
    (f : X -> X) : X -> X -> Prop :=
  fun x x' => f x = x'

/--
Map-based simulation is a special case of relation-based simulation, using the
graph relation of the map.
-/
theorem mapSimulationContract_as_relationSimulationContract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe1 : S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {f : S.Fragment -> S.Fragment}
    (hContract :
      CarrierMapSimulationContract S Next0 Next1 safe1 C D f) :
    CarrierRelationSimulationContract
      S
      Next0
      Next1
      safe1
      C
      D
      (GraphRelation f) := by
  exact And.intro
    hContract.right.right.left
    (And.intro
      (by
        intro x x' y hx hx' hRel hy hStep
        subst x'
        exact Exists.intro (f y)
          (And.intro
            (hContract.left y hy)
            (And.intro rfl
              (hContract.right.left x y hx hy hStep))))
      (by
        intro x y x' y' hxRel hyRel hSep
        subst x'
        subst y'
        exact hContract.right.right.right x y hSep))

def internalPathRelatedOfEdges
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    {R : X -> X -> Prop}
    (hStep : InternalEdgeRelatedByPath Next0 Next1 C D R)
    {x x' y : X}
    (hx' : RelatedInCarrier R D x x')
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    exists y',
      D y' /\
      R y y' /\
      InternalPath (dynFromNext Next1) D x' y' :=
  match hPath with
  | InternalPath.refl _hx =>
      Exists.intro x'
        (And.intro
          hx'.left
          (And.intro hx'.right (InternalPath.refl hx'.left)))
  | InternalPath.step hx hy hEdge rest =>
      match hStep x x' _ hx hx'.left hx'.right hy hEdge with
      | Exists.intro _ hy' =>
          match internalPathRelatedOfEdges hStep
              (And.intro hy'.left hy'.right.left)
              rest with
          | Exists.intro z' hz' =>
              Exists.intro z'
                (And.intro
                  hz'.left
                  (And.intro
                    hz'.right.left
                    (internalPathAppend hy'.right.right hz'.right.right)))

/--
Old internal paths simulate to target internal paths between related
representatives.
-/
theorem internalPath_related_of_edgeSimulation
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C D : X -> Prop}
    {R : X -> X -> Prop}
    (hStep : InternalEdgeRelatedByPath Next0 Next1 C D R)
    {x x' y : X}
    (hx' : RelatedInCarrier R D x x')
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    exists y',
      D y' /\
      R y y' /\
      InternalPath (dynFromNext Next1) D x' y' := by
  exact internalPathRelatedOfEdges hStep hx' hPath

/--
A carrier certificate transfers through a relation-based simulation to some
related target representative of the right endpoint.

The left target representative `x'` is supplied. The theorem constructs a
related `y'` and certifies the mapped pair `x'/y'`.
-/
theorem certificate_transfers_by_relation_simulation_exists
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 : S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {R : S.Fragment -> S.Fragment -> Prop}
    {x x' y : S.Fragment}
    (hCert : CarrierCertificate S Next0 safe0 C x y)
    (hx' : RelatedInCarrier R D x x')
    (hContract :
      CarrierRelationSimulationContract S Next0 Next1 safe1 C D R) :
    exists y',
      RelatedInCarrier R D y y' /\
      CarrierCertificate S Next1 safe1 D x' y' := by
  match internalPath_related_of_edgeSimulation
      hContract.right.left
      hx'
      (certificate_forward_path hCert) with
  | Exists.intro y' hy' =>
      match internalPath_related_of_edgeSimulation
          hContract.right.left
          (And.intro hy'.left hy'.right.left)
          (certificate_reverse_path hCert) with
      | Exists.intro xBack hxBack =>
          have hBackToStart :
              InternalPath (dynFromNext Next1) D xBack x' :=
            hContract.left.right.right.left xBack x' hxBack.left hx'.left
          have hReverse :
              InternalPath (dynFromNext Next1) D y' x' :=
            internalPathAppend hxBack.right.right hBackToStart
          have hSep :
              ConsequenceMergeSeparated S x' y' :=
            hContract.right.right
              x
              y
              x'
              y'
              hx'.right
              hy'.right.left
              (certificate_mergeSeparated hCert)
          exact Exists.intro y'
            (And.intro
              (And.intro hy'.left hy'.right.left)
              (And.intro
                hContract.left
                (And.intro
                  hx'.left
                  (And.intro
                    hy'.left
                    (And.intro
                      hy'.right.right
                      (And.intro
                        hReverse
                        hSep))))))

/-! ## Tiny identity-relation simulation witness -/

theorem cycle_identity_relation_simulation_contract :
    CarrierRelationSimulationContract
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleClass
      cycleClass
      (fun x y => x = y) := by
  exact And.intro
    cycleClass_recurrent_fromNext
    (And.intro
      (by
        intro x x' y hx hx' hRel hy hStep
        subst x'
        exact Exists.intro y
          (And.intro
            hy
            (And.intro rfl (internalPath_single_step hx hy hStep))))
      (by
        intro x y x' y' hxRel hyRel hSep
        subst x'
        subst y'
        exact hSep))

theorem cycle_certificate_transfers_by_identity_relation_simulation_exists :
    exists y',
      RelatedInCarrier
        (fun x y => x = y)
        cycleClass
        CycleState.right
        y' /\
      CarrierCertificate
        cycleConsequenceSystem
        cycleNext
        cycleSafe
        cycleClass
        CycleState.left
        y' := by
  exact certificate_transfers_by_relation_simulation_exists
    cycle_carrier_certificate
    (And.intro trivial rfl)
    cycle_identity_relation_simulation_contract

end SimulationTransfer
end Trajectory
end OmegaProper
