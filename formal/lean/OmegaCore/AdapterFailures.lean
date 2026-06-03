import OmegaCore.DistTrans

/-!
OmegaCore.AdapterFailures

Finite adapter-failure examples for Omega Primitive Calculus v0.

These examples show why theorem transfer requires the root laws. Raw relations
that fail source-weakening or target-strengthening closure are not valid
`DistTransport`s, and valid one-step transports still do not compose through an
assignment unless the normal-lax inclusion is satisfied.

This module does not define compatibility, process bundles, proto-valuers,
empirical adapters, Future Field Atlas semantics, ethics, or Omega validation.
-/

namespace OmegaCore

namespace AdapterFailures

/-- Source distinctions for the source-weakening failure. -/
inductive WeakSrc where
  | bot
  | a
  deriving DecidableEq

/-- Singleton target distinction for the source-weakening failure. -/
inductive OneTgt where
  | out
  deriving DecidableEq

/-- Source preorder with `bot <= a`. -/
def WeakSrcLe : WeakSrc -> WeakSrc -> Prop
  | WeakSrc.bot, _ => True
  | WeakSrc.a, WeakSrc.a => True
  | _, _ => False

/-- Singleton target preorder. -/
def OneTgtLe : OneTgt -> OneTgt -> Prop
  | OneTgt.out, OneTgt.out => True

theorem weakSrcLe_refl (x : WeakSrc) : WeakSrcLe x x := by
  cases x <;> simp [WeakSrcLe]

theorem weakSrcLe_trans {x y z : WeakSrc} :
    WeakSrcLe x y -> WeakSrcLe y z -> WeakSrcLe x z := by
  cases x <;> cases y <;> cases z <;> simp [WeakSrcLe]

theorem oneTgtLe_refl (x : OneTgt) : OneTgtLe x x := by
  cases x <;> simp [OneTgtLe]

theorem oneTgtLe_trans {a b c : OneTgt} :
    OneTgtLe a b -> OneTgtLe b c -> OneTgtLe a c := by
  cases a <;> cases b <;> cases c <;> simp [OneTgtLe]

def WeakSrcFrame : PreorderFrame WeakSrc where
  le := WeakSrcLe
  le_refl := weakSrcLe_refl
  le_trans := @weakSrcLe_trans

def OneTgtFrame : PreorderFrame OneTgt where
  le := OneTgtLe
  le_refl := oneTgtLe_refl
  le_trans := @oneTgtLe_trans

/-- Raw relation that carries `a` but not the weaker `bot`. -/
def RawPhi : WeakSrc -> OneTgt -> Prop
  | WeakSrc.a, OneTgt.out => True
  | _, _ => False

/-- Source-weakening can fail for a raw, non-closed relation. -/
theorem raw_source_weakening_failure :
    WeakSrcLe WeakSrc.bot WeakSrc.a /\
      RawPhi WeakSrc.a OneTgt.out /\
      Not (RawPhi WeakSrc.bot OneTgt.out) := by
  simp [WeakSrcLe, RawPhi]

/-- No valid `DistTransport` can have exactly the raw source-weakening-failing
relation. -/
theorem rawPhi_not_distTransport_exact :
    Not (exists Phi : DistTransport WeakSrcFrame OneTgtFrame,
      forall s t, Phi.rel s t <-> RawPhi s t) := by
  intro h
  cases h with
  | intro Phi hPhi =>
      have hRawA : RawPhi WeakSrc.a OneTgt.out := by
        simp [RawPhi]
      have hPhiA : Phi.rel WeakSrc.a OneTgt.out :=
        (hPhi WeakSrc.a OneTgt.out).mpr hRawA
      have hPhiBot : Phi.rel WeakSrc.bot OneTgt.out :=
        Phi.closed
          (by simp [WeakSrcFrame, WeakSrcLe])
          hPhiA
          (by simp [OneTgtFrame, OneTgtLe])
      have hRawBot : RawPhi WeakSrc.bot OneTgt.out :=
        (hPhi WeakSrc.bot OneTgt.out).mp hPhiBot
      exact (by simp [RawPhi] at hRawBot)

/-- Source distinction for the target-strengthening failure. -/
inductive OneSrc where
  | a
  deriving DecidableEq

/-- Target distinctions for the target-strengthening failure. -/
inductive StrongTgt where
  | out
  | top
  deriving DecidableEq

/-- Singleton source preorder. -/
def OneSrcLe : OneSrc -> OneSrc -> Prop
  | OneSrc.a, OneSrc.a => True

/-- Target preorder with `out <= top`. -/
def StrongTgtLe : StrongTgt -> StrongTgt -> Prop
  | StrongTgt.out, _ => True
  | StrongTgt.top, StrongTgt.top => True
  | _, _ => False

theorem oneSrcLe_refl (x : OneSrc) : OneSrcLe x x := by
  cases x <;> simp [OneSrcLe]

theorem oneSrcLe_trans {x y z : OneSrc} :
    OneSrcLe x y -> OneSrcLe y z -> OneSrcLe x z := by
  cases x <;> cases y <;> cases z <;> simp [OneSrcLe]

theorem strongTgtLe_refl (x : StrongTgt) : StrongTgtLe x x := by
  cases x <;> simp [StrongTgtLe]

theorem strongTgtLe_trans {a b c : StrongTgt} :
    StrongTgtLe a b -> StrongTgtLe b c -> StrongTgtLe a c := by
  cases a <;> cases b <;> cases c <;> simp [StrongTgtLe]

def OneSrcFrame : PreorderFrame OneSrc where
  le := OneSrcLe
  le_refl := oneSrcLe_refl
  le_trans := @oneSrcLe_trans

def StrongTgtFrame : PreorderFrame StrongTgt where
  le := StrongTgtLe
  le_refl := strongTgtLe_refl
  le_trans := @strongTgtLe_trans

/-- Raw relation that carries `out` but not the stronger target `top`. -/
def RawPsi : OneSrc -> StrongTgt -> Prop
  | OneSrc.a, StrongTgt.out => True
  | _, _ => False

/-- Target-strengthening can fail for a raw, non-closed relation. -/
theorem raw_target_strengthening_failure :
    StrongTgtLe StrongTgt.out StrongTgt.top /\
      RawPsi OneSrc.a StrongTgt.out /\
      Not (RawPsi OneSrc.a StrongTgt.top) := by
  simp [StrongTgtLe, RawPsi]

/-- No valid `DistTransport` can have exactly the raw
target-strengthening-failing relation. -/
theorem rawPsi_not_distTransport_exact :
    Not (exists Psi : DistTransport OneSrcFrame StrongTgtFrame,
      forall s t, Psi.rel s t <-> RawPsi s t) := by
  intro h
  cases h with
  | intro Psi hPsi =>
      have hRawOut : RawPsi OneSrc.a StrongTgt.out := by
        simp [RawPsi]
      have hPsiOut : Psi.rel OneSrc.a StrongTgt.out :=
        (hPsi OneSrc.a StrongTgt.out).mpr hRawOut
      have hPsiTop : Psi.rel OneSrc.a StrongTgt.top :=
        Psi.closed
          (by simp [OneSrcFrame, OneSrcLe])
          hPsiOut
          (by simp [StrongTgtFrame, StrongTgtLe])
      have hRawTop : RawPsi OneSrc.a StrongTgt.top :=
        (hPsi OneSrc.a StrongTgt.top).mp hPsiTop
      exact (by simp [RawPsi] at hRawTop)

/-- Singleton distinction fiber for the laxity failure. -/
inductive D0 where
  | d
  deriving DecidableEq

inductive D1 where
  | e
  deriving DecidableEq

inductive D2 where
  | z
  deriving DecidableEq

def D0Le : D0 -> D0 -> Prop
  | D0.d, D0.d => True

def D1Le : D1 -> D1 -> Prop
  | D1.e, D1.e => True

def D2Le : D2 -> D2 -> Prop
  | D2.z, D2.z => True

theorem d0Le_refl (x : D0) : D0Le x x := by
  cases x <;> simp [D0Le]

theorem d0Le_trans {a b c : D0} :
    D0Le a b -> D0Le b c -> D0Le a c := by
  cases a <;> cases b <;> cases c <;> simp [D0Le]

theorem d1Le_refl (x : D1) : D1Le x x := by
  cases x <;> simp [D1Le]

theorem d1Le_trans {a b c : D1} :
    D1Le a b -> D1Le b c -> D1Le a c := by
  cases a <;> cases b <;> cases c <;> simp [D1Le]

theorem d2Le_refl (x : D2) : D2Le x x := by
  cases x <;> simp [D2Le]

theorem d2Le_trans {a b c : D2} :
    D2Le a b -> D2Le b c -> D2Le a c := by
  cases a <;> cases b <;> cases c <;> simp [D2Le]

def D0Frame : PreorderFrame D0 where
  le := D0Le
  le_refl := d0Le_refl
  le_trans := @d0Le_trans

def D1Frame : PreorderFrame D1 where
  le := D1Le
  le_refl := d1Le_refl
  le_trans := @d1Le_trans

def D2Frame : PreorderFrame D2 where
  le := D2Le
  le_refl := d2Le_refl
  le_trans := @d2Le_trans

/-- First valid one-step transport. -/
def R01 : DistTransport D0Frame D1Frame where
  rel := fun _ _ => True
  closed := by
    intro _ _ _ _ _ _ _
    trivial

/-- Second valid one-step transport. -/
def R12 : DistTransport D1Frame D2Frame where
  rel := fun _ _ => True
  closed := by
    intro _ _ _ _ _ _ _
    trivial

/-- Declared composite transport that erases the composed support. It is a
valid closed transport because its relation is empty, but it cannot serve as
the lax composite of `R01` and `R12`. -/
def R02 : DistTransport D0Frame D2Frame where
  rel := fun _ _ => False
  closed := by
    intro _ _ _ _ _ h _
    exact False.elim h

/-- Local raw recoveries can exist while the declared composite recovery is
absent. -/
theorem raw_laxity_failure :
    R01.rel D0.d D1.e /\
      R12.rel D1.e D2.z /\
      Not (R02.rel D0.d D2.z) := by
  simp [R01, R12, R02]

/-- The declared composite transport fails the required normal-lax inclusion. -/
theorem laxity_subset_failure :
    Not (DistTransport.Subset (DistTransport.compose R01 R12) R02) := by
  intro hsub
  have hComp : (DistTransport.compose R01 R12).rel D0.d D2.z :=
    Exists.intro D1.e
      (And.intro
        (by simp [R01])
        (by simp [R12]))
  have hR02 : R02.rel D0.d D2.z :=
    hsub D0.d D2.z hComp
  exact (by simp [R02] at hR02)

end AdapterFailures

end OmegaCore
