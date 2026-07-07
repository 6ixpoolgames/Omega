/-!
OmegaProper.Decision.AnswerableScope

Reachability-indexed answerable scope.

The formal object is deliberately named `AnswerableScope`, not
`Responsibility`: it records facts that are both controllable and foreclosable
from an agent/interface position. This is not blame, liability, moral
responsibility, agency, value, standing, identity, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace AnswerableScope

universe u v

/--
An answerable-scope frame supplies the two reach-indexed predicates needed by
the v0 bridge: what an agent can control and what it can foreclose.
-/
structure ScopeFrame (Agent : Type u) (Fact : Type v) where
  Controllable : Agent -> Fact -> Prop
  Foreclosable : Agent -> Fact -> Prop

/--
The facts in an agent's answerable scope are exactly those both controllable
and foreclosable from that agent/interface position.
-/
def InScope (F : ScopeFrame Agent Fact) (agent : Agent) (fact : Fact) : Prop :=
  F.Controllable agent fact /\ F.Foreclosable agent fact

/-- If a fact is not controllable, it is not in answerable scope. -/
theorem not_inScope_of_not_controllable
    (F : ScopeFrame Agent Fact)
    {agent : Agent}
    {fact : Fact}
    (hNot : Not (F.Controllable agent fact)) :
    Not (InScope F agent fact) := by
  intro hScope
  exact hNot hScope.1

/-- If a fact is not foreclosable, it is not in answerable scope. -/
theorem not_inScope_of_not_foreclosable
    (F : ScopeFrame Agent Fact)
    {agent : Agent}
    {fact : Fact}
    (hNot : Not (F.Foreclosable agent fact)) :
    Not (InScope F agent fact) := by
  intro hScope
  exact hNot hScope.2

/--
Past-fact exclusion, in the minimal reach reading: a fact with no controllable
reach-image is outside answerable scope.
-/
theorem past_facts_not_answerable
    (F : ScopeFrame Agent Fact)
    {agent : Agent}
    {fact : Fact}
    (hNoReach : Not (F.Controllable agent fact)) :
    Not (InScope F agent fact) :=
  not_inScope_of_not_controllable F hNoReach

/--
Answerable scope is monotone in the two reach predicates: enlarging
controllable and foreclosable sets cannot remove an already answerable fact.
-/
theorem scope_monotone_in_reach
    {F G : ScopeFrame Agent Fact}
    {agent : Agent}
    {fact : Fact}
    (hControl :
      forall f, F.Controllable agent f -> G.Controllable agent f)
    (hForeclose :
      forall f, F.Foreclosable agent f -> G.Foreclosable agent f)
    (hScope : InScope F agent fact) :
    InScope G agent fact := by
  exact ⟨hControl fact hScope.1, hForeclose fact hScope.2⟩

end AnswerableScope
end Decision
end OmegaProper
