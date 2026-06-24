import OmegaProper.BaselineWitnesses.FactorizationCriterion
import OmegaProper.Recovery.TargetPostprocessing

/-!
OmegaProper.Recovery.Nonreflection

Recovering or preserving a deterministic post-processing of a declared target
does not by itself certify the original finer target.

The positive direction lives in `TargetPostprocessing`: fine target recovery
entails recovery of every deterministic coarsening. This module records the
generic negative pattern: if the coarsening merges two fine target values that
occur on the carrier, then the fine target does not factor through the coarse
target.
-/

namespace OmegaProper
namespace Recovery

open BaselineWitnesses.NonFactorization
open BaselineWitnesses.FactorizationCriterion

universe u v w

/--
A deterministic target post-processing collapses a fine target distinction that
actually occurs on the carrier.
-/
def FineDistinctionCollapsedBy
    {X : Type u} {D : Type v} {E : Type w}
    (fine : X -> D)
    (map : D -> E) : Prop :=
  exists x y, Not (fine x = fine y) /\ map (fine x) = map (fine y)

/--
If a post-processing merges two realized fine target values, the coarse target
cannot determine the fine target.
-/
theorem nonFactorization_of_postprocess_collision
    {X : Type u} {D : Type v} {E : Type w}
    {fine : X -> D}
    {map : D -> E}
    {x y : X}
    (hFine : Not (fine x = fine y))
    (hCoarse : map (fine x) = map (fine y)) :
    NonFactorization (targetPostprocess map fine) fine := by
  exact nonFactorization_of_same_summary_different_target
    (by
      unfold targetPostprocess
      exact hCoarse)
    hFine

/--
A realized collapsed fine distinction is exactly a non-factorization witness:
the fine target cannot be reconstructed as a function of the coarse target.
-/
theorem collapsedFineDistinction_nonFactorization
    {X : Type u} {D : Type v} {E : Type w}
    {fine : X -> D}
    {map : D -> E}
    (h : FineDistinctionCollapsedBy fine map) :
    NonFactorization (targetPostprocess map fine) fine := by
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact nonFactorization_of_postprocess_collision
            hy.left hy.right

/--
If a coarsening collapses a realized fine distinction, the fine target is not
constant on coarse-target fibers.
-/
theorem collapsedFineDistinction_blocks_fiberConstant
    {X : Type u} {D : Type v} {E : Type w}
    {fine : X -> D}
    {map : D -> E}
    (h : FineDistinctionCollapsedBy fine map) :
    Not (FiberConstant (targetPostprocess map fine) fine) := by
  exact nonFactorization_blocks_fiberConstant
    (collapsedFineDistinction_nonFactorization h)

/--
If a coarsening collapses a realized fine distinction, the fine target does not
factor through the coarse target.
-/
theorem collapsedFineDistinction_blocks_factorization
    {X : Type u} {D : Type v} {E : Type w}
    {fine : X -> D}
    {map : D -> E}
    (h : FineDistinctionCollapsedBy fine map) :
    Not (FactorsThrough (targetPostprocess map fine) fine) := by
  exact nonFactorization_blocks_factorization
    (collapsedFineDistinction_nonFactorization h)

/--
Any claimed reconstruction of the fine target from the coarse target rules out
a realized post-processing collision.
-/
theorem factorsThrough_blocks_postprocess_collision
    {X : Type u} {D : Type v} {E : Type w}
    {fine : X -> D}
    {map : D -> E}
    (hFactor : FactorsThrough (targetPostprocess map fine) fine) :
    Not (FineDistinctionCollapsedBy fine map) := by
  intro hCollapse
  exact collapsedFineDistinction_blocks_factorization hCollapse hFactor

end Recovery
end OmegaProper
