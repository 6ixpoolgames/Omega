# Bridge Claims Ledger v0

Status: internal bridge-risk ledger
Scope: seam-crossing claims between Alpha, recovery, admissibility, viability, Gradient Ethics, and future valuer/Omega targets
Claim boundary: tracking artifact only; not theorem closure, not empirical validation, not Omega validation

## Purpose

The main project risk is now internal non-unification: strong local theorem
surfaces may fail to weld into one theory. This ledger tracks proposed bridge
claims explicitly.

Each bridge should record:

```text
source layer;
target layer;
current status;
missing theorem or pilot;
smallest witness;
falsifier;
non-claim boundary.
```

The goal is to prevent vocabulary from doing unearned unifying work.

## Status Labels

```text
LANDED:
  machine-checked theorem or retained adapter validation exists.

ACTIVE TARGET:
  theorem or pilot is near-term and concrete enough to work on.

PILOT TARGET:
  likely needs finite Python/adapter exploration before Lean.

SPECULATIVE:
  useful research direction, not yet claim-bearing.

BLOCKED BY ADMISSIBILITY:
  depends on a principled presentation/admissibility criterion.
```

## Ledger

| Bridge | Source Layer | Target Layer | Status | Missing Work | Smallest Witness / Positive Test | Falsifier / Negative Test | Non-Claim Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Support-exact recovery is the threshold-one endpoint of graded recovery. | Exact support recovery | Graded finite recovery | LANDED | None for finite deterministic channel layer. | `supportExactRecovery_iff_recoveryAt_one` in `Recovery/Deterministic.lean`. | A counterexample channel with support-exact recovery not matching success-one decoding. | Does not validate empirical channels, values, agency, or Omega. |
| Worst-case recovery implies prior-relative expected recovery. | Per-source threshold recovery | Declared-prior expected recovery | LANDED | None for finite deterministic prior layer. | `recoveryAt_implies_expectedRecoveryAt` in `Recovery/Prior.lean`. | A declared prior where every source is above threshold but expectation falls below threshold. | Does not make a prior empirical or moral. |
| Per-channel recovery does not imply robust ambiguity recovery. | Single-channel recovery | Uniform recovery over uncertainty | LANDED | None for two-channel finite witness. | `identity_flip_each_recoverable_not_robust` in `Recovery/Examples.lean`. | If every independently recoverable ambiguity set admitted one common decoder, this witness would fail. | Does not define model uncertainty as complete or empirical. |
| High expected recovery does not imply worst-case recovery. | Declared-prior expected recovery | Worst-case source guarantee | LANDED | None for finite skewed-prior witness. | `high_expected_not_worstCase_recovery` in `Recovery/Examples.lean`. | If expected threshold implied every source threshold. | Does not say expected recovery is useless; it separates axes. |
| Shared observation mass bounds graded deterministic recovery. | Consequence/observation confusion | Quantitative recovery obstruction | LANDED | None for deterministic finite channels. | `shared_observation_mass_blocks_recoveryAt` in `Recovery/ConfusionBound.lean`: two target-distinct sources sharing observation mass `epsilon` block threshold recovery above `1 - epsilon`. | A decoder exceeding the bound under the stated shared-mass conditions. | Does not cover randomized decoders or optimized observations unless separately proved. |
| Recovery failure persists under deterministic coarsening. | Observation refinement theorem | Irreversible loss / Gradient Ethics bridge | LANDED | Chain packaging can be added later if useful. | `Recovery/CoarseningPermanence.lean` proves deterministic, restricted, support-exact, robust, and randomized failure persistence under deterministic coarsening, with explicit decoder-class lifting assumptions where needed. | A deterministic coarsening that restores a failed unrestricted recovery threshold. | Does not cover new measurements, new side information, or non-deterministic observation changes. |
| Admissibility as fact/presentation closure. | Soundness and hidden-loss checks | Boundary-invariant facts | ACTIVE TARGET | Generic Galois closure, X2 coordinate, recovery, viability, carrier, stale/reflected, multi-presentation, transport-aware, failed-transport generated pilots, the first grid obstacle source-generator closure pilot, stochastic continuation hit-status closure, policy-conditioned hit-status closure, baseline graph/grid source parity, and observation-closure graph/grid parity are landed; still need broader closure stress tests. | The finite relational adapter now generates closure shrinkage cases for a derived carrier pair, transition-derived reachability status, transition/safety-derived viability status, bounded-recovery observation status, stale/reflected reach-status facts, row/column multi-presentation families, transported endpoint-role facts under a transfer contract, a failed-transfer label-closure control, a grid obstacle source-generator case where stale/reflected source-reach status removes the after-reachability fact from common target facts, a stochastic continuation case where stale/reflected hit-status removes an after-hit threshold fact, a policy-conditioned case with the same closure pattern under a deterministic policy, graph/grid parity cases for strict asymmetry and recurrent carrier certification, and an observation-closure graph/grid parity case with matching source-derived target closure payloads. | Honest admissibility families collapse all recovery/viability/carrier/transport facts to constants or empty visible-pair sets. | Does not prove a valuer, agency, carrier identity, or Omega object. |
| Sound transport preserves recovery/viability facts. | Presentation transport | Decomposition-invariance | ACTIVE TARGET | First adapter transport-closure and failed-transfer controls landed; still need formal transport-compatible fact preservation once the fact surface is fixed. | `generated_transport_fact_closure` certifies a carrier transfer and checks that lifted source/target role presentations preserve a transported endpoint-role fact. | `generated_failed_transport_fact_closure` preserves a transport-looking role fact under lifted labels while the carrier-transfer audit rejects transfer because target return structure is missing. | Does not claim all presentations are comparable or that transfer is identity. |
| Individual viability/carrying does not imply joint viability/carrying. | Single-process continuation | Compatibility / aggregation | LANDED | Extend toward robust stochastic setting. | Existing joint viability and joint recurrent-support counterexamples. | Pairwise facts always composing into joint facts. | Does not settle moral aggregation or anti-singleton claims. |
| Robust joint viability under correlated shocks. | Robust recovery / policy continuation | Distributed agency constraint | PILOT TARGET | Build finite stochastic controlled examples and then formalize stable statements. | Individually robust policies fail under shared resource/correlated shock constraints. | Joint robustness always follows from individual robustness under declared assumptions. | Does not prove distributed agency is always better. |
| Active maintenance of a transported invariant. | Recurrent support / policy dynamics | Vortical agency candidate | SPECULATIVE | Need invariant fact surface, perturbation family, closed-loop/open-loop distinction, and cost model. | Feedback policy preserves a nontrivial transported recovery/viability invariant where passive/open-loop policies fail. | Passive systems have the same invariant and cost profile as alleged active maintainers. | Do not call this agency/valuerhood until the invariant and controls are formalized. |
| ECHO / maintenance cost grades active preservation. | Cost accounting | Active-maintenance profile | SPECULATIVE | Define finite cost model and minimal excess cost per robust recovery margin. | Positive minimal excess cost required to maintain an invariant under perturbation. | Inefficient dissipation masquerades as agency; passive controls match active profile. | Cost is not value and not valuerhood by itself. |
| Omega as invariant closure or obstruction across presentations. | Admissibility lattice / transport graph | Omega-like target | BLOCKED BY ADMISSIBILITY | Need nontrivial finite invariant closure or holonomy before definitions. | Nonconstant continuation fact survives admissible presentation graph or shows coherent nontrivial holonomy. | Every honest admissibility family collapses to constants. | Do not claim Omega, terminal structure, or value-bearing substrate yet. |

## The Admissibility Problem

Current central open problem:

```text
derive an admissibility criterion for presentations that is neither so weak
that all invariant facts collapse to constants nor so strong that it hand-picks
the desired answer.
```

Near-term strategy:

```text
use soundness, hidden-loss, reflection, decoder-class, robust, and prior
guardrails to define finite satisfaction checks;
compute fact/presentation closures;
try to collapse the invariant closure adversarially before looking for a
positive invariant atlas.
```

## Update Rule

Add a row when a proposed bridge claim starts influencing implementation.
Promote a row only when the evidence changes:

```text
speculation -> pilot target -> active target -> landed
```

Do not promote because a name is compelling or a metaphor aligns.
