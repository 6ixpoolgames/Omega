import OmegaCore.NormalLax

/-!
OmegaCore.Recurrent

Finite-chain recurrent recoverability for Omega Primitive Calculus v0.

This module validates the first recurrent-recoverability layer without adding
new ontology: repeated local recovery along a declared finite chain implies
recovery through the composite unfolding.
-/

namespace OmegaCore

universe u v w

namespace NormalLaxDistinctionTransport

/-- A finite composable chain of relational unfoldings. -/
inductive Chain (M : NormalLaxDistinctionTransport.{u, v, w}) :
    M.C.Ctx -> M.C.Ctx -> Type (max (max (u+1) (v+1)) (w+1)) where
  | nil {X : M.C.Ctx} : Chain M X X
  | cons {X Y Z : M.C.Ctx} :
      M.C.Rel X Y -> Chain M Y Z -> Chain M X Z

namespace Chain

/-- Composite unfolding induced by a finite chain. -/
def toHom
    {M : NormalLaxDistinctionTransport.{u, v, w}}
    {X Y : M.C.Ctx} :
    Chain M X Y -> M.C.Rel X Y
  | nil => M.C.id X
  | cons r rest => M.C.comp r (toHom rest)

@[simp]
theorem toHom_nil
    {M : NormalLaxDistinctionTransport.{u, v, w}}
    {X : M.C.Ctx} :
    toHom (M := M) (X := X) (Y := X) Chain.nil = M.C.id X := rfl

@[simp]
theorem toHom_cons
    {M : NormalLaxDistinctionTransport.{u, v, w}}
    {X Y Z : M.C.Ctx}
    (r : M.C.Rel X Y)
    (rest : Chain M Y Z) :
    toHom (M := M) (X := X) (Y := Z) (Chain.cons r rest) =
      M.C.comp r (toHom rest) := rfl

end Chain

/-- `RecoverChain M p d e` means `d` is carried stepwise along chain `p` into
`e`. The empty chain is identity recovery by refinement. -/
inductive RecoverChain
    (M : NormalLaxDistinctionTransport.{u, v, w}) :
    {X Y : M.C.Ctx} -> Chain M X Y -> M.Dist X -> M.Dist Y -> Prop where
  | nil {X : M.C.Ctx} {d e : M.Dist X} :
      (M.frame X).le d e -> RecoverChain M Chain.nil d e
  | step {X Y Z : M.C.Ctx}
      {r : M.C.Rel X Y} {rest : Chain M Y Z}
      {d : M.Dist X} {m : M.Dist Y} {e : M.Dist Z} :
      Recovers M r d m ->
      RecoverChain M rest m e ->
      RecoverChain M (Chain.cons r rest) d e

/-- Finite-chain recurrent recoverability is sound: local stepwise recovery
implies recovery through the composed unfolding. -/
theorem recoverChain_sound
    (M : NormalLaxDistinctionTransport.{u, v, w})
    {X Y : M.C.Ctx} {p : Chain M X Y}
    {d : M.Dist X} {e : M.Dist Y}
    (h : RecoverChain M p d e) :
    Recovers M (Chain.toHom p) d e := by
  induction h with
  | nil hle =>
      exact identity_recoverability M hle
  | step hstep _ ih =>
      exact compositional_recoverability M hstep ih

/-- One-step chains recover by the step witness. This is a small sanity lemma,
not a new ontology. -/
theorem recoverChain_one
    (M : NormalLaxDistinctionTransport.{u, v, w})
    {X Y : M.C.Ctx}
    {r : M.C.Rel X Y}
    {d : M.Dist X}
    {e : M.Dist Y}
    (h : Recovers M r d e) :
    RecoverChain M (Chain.cons r Chain.nil) d e := by
  exact RecoverChain.step h (RecoverChain.nil ((M.frame Y).le_refl e))

end NormalLaxDistinctionTransport

end OmegaCore
