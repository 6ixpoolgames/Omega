import ProtoOmega.Recoverability.Native

/-!
ProtoOmega.Recoverability.RecurrentNative

Finite-chain recoverability over Alpha-native recoverability models.
-/

namespace ProtoOmega
namespace Recoverability
namespace NativeModel

universe u v x y

/-- A finite composable chain of declared unfoldings. -/
inductive Chain (M : NativeModel.{u, v, x, y}) :
    M.C.Ctx -> M.C.Ctx -> Type (max (max (max (u+1) (v+1)) (x+1)) (y+1)) where
  | nil {X : M.C.Ctx} : Chain M X X
  | cons {X Y Z : M.C.Ctx} :
      M.C.Hom X Y -> Chain M Y Z -> Chain M X Z

namespace Chain

/-- Composite unfolding induced by a finite chain. -/
def toHom
    {M : NativeModel.{u, v, x, y}}
    {X Y : M.C.Ctx} :
    Chain M X Y -> M.C.Hom X Y
  | nil => M.C.id X
  | cons f rest => M.C.comp f (toHom rest)

@[simp]
theorem toHom_nil
    {M : NativeModel.{u, v, x, y}}
    {X : M.C.Ctx} :
    toHom (M := M) (X := X) (Y := X) Chain.nil = M.C.id X := rfl

@[simp]
theorem toHom_cons
    {M : NativeModel.{u, v, x, y}}
    {X Y Z : M.C.Ctx}
    (f : M.C.Hom X Y)
    (rest : Chain M Y Z) :
    toHom (M := M) (X := X) (Y := Z) (Chain.cons f rest) =
      M.C.comp f (toHom rest) := rfl

end Chain

/-- Stepwise recovery along a declared finite chain. -/
inductive RecoverChain
    (M : NativeModel.{u, v, x, y}) :
    {X Y : M.C.Ctx} ->
      Chain M X Y -> (M.frame X).Dist -> (M.frame Y).Dist -> Prop where
  | nil {X : M.C.Ctx} {d e : (M.frame X).Dist} :
      (M.order X).le d e -> RecoverChain M Chain.nil d e
  | step {X Y Z : M.C.Ctx}
      {f : M.C.Hom X Y} {rest : Chain M Y Z}
      {d : (M.frame X).Dist}
      {m : (M.frame Y).Dist}
      {e : (M.frame Z).Dist} :
      Recovers M f d m ->
      RecoverChain M rest m e ->
      RecoverChain M (Chain.cons f rest) d e

/-- Stepwise chain recovery is sound for the chain composite. -/
theorem recoverChain_sound
    (M : NativeModel.{u, v, x, y})
    {X Y : M.C.Ctx} {p : Chain M X Y}
    {d : (M.frame X).Dist} {e : (M.frame Y).Dist}
    (h : RecoverChain M p d e) :
    Recovers M (Chain.toHom p) d e := by
  induction h with
  | nil hle =>
      exact identity_recoverability M hle
  | step hstep _ ih =>
      exact compositional_recoverability M hstep ih

/-- One-step chains recover by the supplied step witness. -/
theorem recoverChain_one
    (M : NativeModel.{u, v, x, y})
    {X Y : M.C.Ctx}
    {f : M.C.Hom X Y}
    {d : (M.frame X).Dist}
    {e : (M.frame Y).Dist}
    (h : Recovers M f d e) :
    RecoverChain M (Chain.cons f Chain.nil) d e := by
  exact RecoverChain.step h (RecoverChain.nil ((M.order Y).le_refl e))

end NativeModel
end Recoverability
end ProtoOmega
