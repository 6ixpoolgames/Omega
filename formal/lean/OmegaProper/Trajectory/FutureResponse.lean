import OmegaProper.Trajectory.Quotient

/-!
OmegaProper.Trajectory.FutureResponse

Abstract future-response sufficiency for trajectory windows.

The primary object here is a response function over evaluated windows. Factored
representations appear only as one way to induce such a response function. This
keeps the formal surface focused on preserving future-response behavior rather
than treating representation recovery as primitive.
-/

namespace OmegaProper
namespace Trajectory
namespace FutureResponse

open Quotient

universe u v e r q q2

/--
A declared future-response presentation over one-step relation windows.

`Close` is deliberately a predicate. Empirical adapters may instantiate it as
exact equality, a thresholded metric, a statistical acceptance relation, or some
other audited response comparison.
-/
structure FutureResponsePresentation (A : AlphaCore.Frame.{u, v}) where
  Env : Type e
  Response : Type r
  teacher : Env -> RelWindow A -> Response
  Close : Response -> Response -> Prop
  EvalEnv : Env -> Prop
  EvalWindow : RelWindow A -> Prop

/-- A candidate response model directly approximates the teacher function. -/
structure ResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A) where
  approx : P.Env -> RelWindow A -> P.Response

/-- The model approximates the declared teacher response on evaluated cells. -/
def ResponseSufficient {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (M : ResponseModel P) : Prop :=
  forall e w,
    P.EvalEnv e ->
    P.EvalWindow w ->
    P.Close (M.approx e w) (P.teacher e w)

/--
A factored response model. The factorization is secondary: it induces a
response model by encoding a window and then decoding the response from the
encoded representation.
-/
structure FactoredResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A) where
  Rep : Type q
  encode : RelWindow A -> Rep
  decode : P.Env -> Rep -> P.Response

/-- The response model induced by a factored response model. -/
def FactoredResponseModel.toResponseModel {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    (M : FactoredResponseModel P) : ResponseModel P where
  approx := fun e w => M.decode e (M.encode w)

/-- A factored model is sufficient when its induced response model is sufficient. -/
def FactoredResponseSufficient {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (M : FactoredResponseModel P) : Prop :=
  ResponseSufficient P M.toResponseModel

/-- A direct response model with no compression discipline. -/
def directResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (approx : P.Env -> RelWindow A -> P.Response) :
    ResponseModel P where
  approx := approx

/-- A constant response model, useful as a degenerate baseline. -/
def constantResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (response : P.Env -> P.Response) :
    ResponseModel P where
  approx := fun e _ => response e

/-- Raw window access as a response model, useful as a leakage/fingerprint baseline. -/
def rawWindowResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (predict : P.Env -> RelWindow A -> P.Response) :
    ResponseModel P where
  approx := predict

/-- A constant factored model with one representation value. -/
def constantFactoredResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (response : P.Env -> P.Response) :
    FactoredResponseModel.{u, v, q, e, r} P where
  Rep := ULift.{q} Unit
  encode := fun _ => ULift.up ()
  decode := fun e _ => response e

/-- Raw window access as a factored model. This is a guardrail baseline. -/
def rawWindowFactoredResponseModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (predict : P.Env -> RelWindow A -> P.Response) :
    FactoredResponseModel P where
  Rep := RelWindow A
  encode := fun w => w
  decode := predict

/--
`coarse` is coarser than `fine` when its representation factors through
`fine`. This relation is about the factorization only; response sufficiency is
checked separately.
-/
def FactoredModelCoarser {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    (fine : FactoredResponseModel.{u, v, q, e, r} P)
    (coarse : FactoredResponseModel.{u, v, q2, e, r} P) : Prop :=
  exists f : fine.Rep -> coarse.Rep,
    forall w, coarse.encode w = f (fine.encode w)

/-- Strict coarsening: factorization one way, but not back the other way. -/
def StrictlyFactoredCoarser {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    (fine : FactoredResponseModel.{u, v, q, e, r} P)
    (coarse : FactoredResponseModel.{u, v, q2, e, r} P) : Prop :=
  FactoredModelCoarser fine coarse /\ Not (FactoredModelCoarser coarse fine)

/-- The evaluated factorization is not constant on evaluated windows. -/
def NontrivialFactorization {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (M : FactoredResponseModel P) : Prop :=
  exists w1 w2,
    P.EvalWindow w1 /\
    P.EvalWindow w2 /\
    Not (M.encode w1 = M.encode w2)

/--
Minimality is relative to an admissibility predicate. This is where empirical
adapters can later enforce predeclaration, leakage discipline, feature
eligibility, or null-control requirements.
-/
def MinimalSufficientFactoredModel {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (Admissible : FactoredResponseModel.{u, v, q, e, r} P -> Prop)
    (M : FactoredResponseModel.{u, v, q, e, r} P) : Prop :=
  Admissible M /\
  FactoredResponseSufficient P M /\
  forall M',
    Admissible M' ->
    StrictlyFactoredCoarser M M' ->
    Not (FactoredResponseSufficient P M')

/--
The model assigns similar responses to the earlier and later evaluated windows.
This is response continuity, not identity and not representation recovery.
-/
def ResponseContinuation {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (M : ResponseModel P)
    (earlier later : RelWindow A) : Prop :=
  forall e,
    P.EvalEnv e ->
    P.EvalWindow earlier ->
    P.EvalWindow later ->
    P.Close (M.approx e later) (M.approx e earlier)

/-- Response continuation plus endpoint drift. -/
def DriftWithResponseContinuation {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (M : ResponseModel P)
    (earlier later : RelWindow A) : Prop :=
  Not (SameEndpoints earlier later) /\
  ResponseContinuation P M earlier later

/-- A candidate object, not a final ontology. -/
def MinimalFutureDeformerCandidate {A : AlphaCore.Frame.{u, v}}
    (P : FutureResponsePresentation A)
    (Admissible : FactoredResponseModel.{u, v, q, e, r} P -> Prop)
    (M : FactoredResponseModel.{u, v, q, e, r} P) : Prop :=
  MinimalSufficientFactoredModel P Admissible M /\
  NontrivialFactorization P M

theorem constant_sufficient_implies_teacher_close
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {response : P.Env -> P.Response}
    (hsym : forall {a b}, P.Close a b -> P.Close b a)
    (htrans : forall {a b c}, P.Close a b -> P.Close b c -> P.Close a c)
    (h : ResponseSufficient P (constantResponseModel P response))
    {e : P.Env} {w1 w2 : RelWindow A}
    (he : P.EvalEnv e)
    (hw1 : P.EvalWindow w1)
    (hw2 : P.EvalWindow w2) :
    P.Close (P.teacher e w1) (P.teacher e w2) := by
  have h1 : P.Close (response e) (P.teacher e w1) := h e w1 he hw1
  have h2 : P.Close (response e) (P.teacher e w2) := h e w2 he hw2
  exact htrans (hsym h1) h2

theorem raw_window_sufficient_of_exact_predict
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {predict : P.Env -> RelWindow A -> P.Response}
    (hrefl : forall r, P.Close r r)
    (hexact : forall e w,
      P.EvalEnv e ->
      P.EvalWindow w ->
      predict e w = P.teacher e w) :
    ResponseSufficient P (rawWindowResponseModel P predict) := by
  intro e w he hw
  change P.Close (predict e w) (P.teacher e w)
  rw [hexact e w he hw]
  exact hrefl (P.teacher e w)

theorem raw_window_factored_sufficient_of_exact_predict
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {predict : P.Env -> RelWindow A -> P.Response}
    (hrefl : forall r, P.Close r r)
    (hexact : forall e w,
      P.EvalEnv e ->
      P.EvalWindow w ->
      predict e w = P.teacher e w) :
    FactoredResponseSufficient P (rawWindowFactoredResponseModel P predict) := by
  exact raw_window_sufficient_of_exact_predict
    (P := P) (predict := predict) hrefl hexact

theorem minimal_sufficient_blocks_strictly_coarser
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {Admissible : FactoredResponseModel.{u, v, q, e, r} P -> Prop}
    {M M' : FactoredResponseModel.{u, v, q, e, r} P}
    (h : MinimalSufficientFactoredModel P Admissible M)
    (hAdm : Admissible M')
    (hStrict : StrictlyFactoredCoarser M M') :
    Not (FactoredResponseSufficient P M') := by
  exact h.right.right M' hAdm hStrict

theorem constant_factored_not_nontrivial
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {response : P.Env -> P.Response} :
    Not (NontrivialFactorization P (constantFactoredResponseModel P response)) := by
  intro h
  rcases h with ⟨w1, w2, _hw1, _hw2, hneq⟩
  exact hneq rfl

theorem constant_factored_not_minimal_future_deformer_candidate
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {Admissible : FactoredResponseModel.{u, v, q, e, r} P -> Prop}
    {response : P.Env -> P.Response} :
    Not (MinimalFutureDeformerCandidate P Admissible
      (constantFactoredResponseModel P response)) := by
  intro h
  exact constant_factored_not_nontrivial h.right

theorem constant_factored_strictly_coarser_of_nontrivial
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {M : FactoredResponseModel.{u, v, q, e, r} P}
    {response : P.Env -> P.Response}
    (hNon : NontrivialFactorization P M) :
    StrictlyFactoredCoarser M (constantFactoredResponseModel P response) := by
  constructor
  case left =>
    exists fun _ => ULift.up ()
    intro _w
    rfl
  case right =>
    intro hBack
    rcases hBack with ⟨f, hf⟩
    rcases hNon with ⟨w1, w2, _hw1, _hw2, hneq⟩
    have hsame :
        (constantFactoredResponseModel P response).encode w1 =
          (constantFactoredResponseModel P response).encode w2 := rfl
    have hEq : M.encode w1 = M.encode w2 := by
      calc
        M.encode w1 = f ((constantFactoredResponseModel P response).encode w1) := hf w1
        _ = f ((constantFactoredResponseModel P response).encode w2) := by rw [hsame]
        _ = M.encode w2 := (hf w2).symm
    exact hneq hEq

theorem minimal_candidate_rules_out_sufficient_constant
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {Admissible : FactoredResponseModel.{u, v, q, e, r} P -> Prop}
    {M : FactoredResponseModel.{u, v, q, e, r} P}
    {response : P.Env -> P.Response}
    (h : MinimalFutureDeformerCandidate P Admissible M)
    (hAdm : Admissible (constantFactoredResponseModel P response)) :
    Not (FactoredResponseSufficient P (constantFactoredResponseModel P response)) := by
  intro hConst
  exact minimal_sufficient_blocks_strictly_coarser h.left hAdm
    (constant_factored_strictly_coarser_of_nontrivial h.right) hConst

theorem raw_window_factored_not_minimal_when_coarser_sufficient
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {predict : P.Env -> RelWindow A -> P.Response}
    {Admissible : FactoredResponseModel.{u, v, u, e, r} P -> Prop}
    {coarse : FactoredResponseModel.{u, v, u, e, r} P}
    (hAdm : Admissible coarse)
    (hStrict :
      StrictlyFactoredCoarser
        (rawWindowFactoredResponseModel P predict) coarse)
    (hSuff : FactoredResponseSufficient P coarse) :
    Not (MinimalSufficientFactoredModel P Admissible
      (rawWindowFactoredResponseModel P predict)) := by
  intro hMin
  exact hMin.right.right coarse hAdm hStrict hSuff

theorem recovered_response_relevance_of_sufficient
    {A : AlphaCore.Frame.{u, v}}
    {P : FutureResponsePresentation A}
    {M : ResponseModel P}
    (htrans : forall {a b c}, P.Close a b -> P.Close b c -> P.Close a c)
    (hsuff : ResponseSufficient P M)
    {e : P.Env} {earlier later : RelWindow A}
    (he : P.EvalEnv e)
    (hearlier : P.EvalWindow earlier)
    (hlater : P.EvalWindow later)
    (hcont : ResponseContinuation P M earlier later) :
    P.Close (M.approx e later) (P.teacher e earlier) := by
  exact htrans
    (hcont e he hearlier hlater)
    (hsuff e earlier he hearlier)

/-! ## Tiny guardrail examples -/

def toyFutureResponsePresentation :
    FutureResponsePresentation twoFrame where
  Env := Unit
  Response := Unit
  teacher := fun _ _ => ()
  Close := fun _ _ => True
  EvalEnv := fun _ => True
  EvalWindow := fun _ => True

def toyConstantResponseModel :
    ResponseModel toyFutureResponsePresentation where
  approx := fun _ _ => ()

theorem response_continuation_does_not_imply_same_endpoints :
    ResponseContinuation toyFutureResponsePresentation toyConstantResponseModel
      loopA edgeAB /\
      Not (SameEndpoints loopA edgeAB) := by
  constructor
  case left =>
    intro _ _ _ _
    trivial
  case right =>
    intro h
    have ht : Two.a = Two.b := h.right
    cases ht

theorem shape_drift_with_response_continuation_toy :
    DriftWithResponseContinuation toyFutureResponsePresentation
      toyConstantResponseModel loopA edgeAB := by
  constructor
  case left =>
    exact response_continuation_does_not_imply_same_endpoints.right
  case right =>
    exact response_continuation_does_not_imply_same_endpoints.left

end FutureResponse
end Trajectory
end OmegaProper
