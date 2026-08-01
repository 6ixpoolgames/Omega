# Alpha-Omega Foundation Report v0

Status: retained executable foundation and theorem-spine fragment

Date: 2026-08-01

Protocol:
`docs/research_notes/omega_v2/alpha_omega_foundation_protocol_v0.md`

Theory handoff:
`docs/ALPHA_OMEGA_THEORY_PROPOSAL_HANDOFF_V0.md`

## Verdict

```text
retained
```

One finite adapter now derives:

```text
oriented finite path laws;
residual continuation laws;
action-labelled support;
support-only reachability and viability;
statistical path-law directionality;
functional presentation contracts;
candidate process feature profiles;
realization fibers;
restriction maps;
the May-compatibility complex;
maximal faces;
and explicit higher-order obstruction.
```

It does so without selecting a preferred candidate-process boundary, a
preferred maximal face, a valuer threshold, or a moral objective.

## Formal Layer

Formal files:

```text
formal/lean/OmegaProper/Foundation/SupportBlindness.lean
formal/lean/OmegaProper/Foundation/FunctionalLens.lean
formal/lean/OmegaProper/Foundation/RealizationFibers.lean
formal/lean/OmegaProper/Foundation.lean
```

Retained theorem families:

```text
SupportBlindness:
  mayPre_eq_of_supportEquivalent
  robustPre_eq_of_supportEquivalent
  supportEquivalent_preserves_reach
  supportEquivalent_preserves_viability

FunctionalLens:
  diamond_iff
  box_iff
  finitePath_forward
  finitePath_back
  reachable_predicate_iff

RealizationFibers:
  real_antitone
  mayCompatible_downward
  real_empty
  real_union
  restrict_identity
  restrict_composition
```

The support-blindness theorems do not require finite state spaces. The finite
Python harness supplies exact rational examples showing why the result matters.

The functional-lens theorem is deliberately bounded to one-step modal facts
and finite paths. It is not a full modal fixed-point invariance theorem.

The realization theorems retain the fiber itself. Compatibility is nonemptiness
of a derived fiber, not an independently declared edge.

## Executable Layer

Adapter:

```text
omega/adapters/finite_relational/alpha_omega_foundation.py
```

Validation:

```text
omega/validation/finite_relational_alpha_omega_foundation.py
```

Focused tests:

```text
tests/test_finite_relational_alpha_omega_foundation.py
```

The executable interface uses:

```text
FiniteControlledKernel:
  exact rational action-conditioned transition probabilities;

FinitePath:
  explicit state and action histories;

PathReversal:
  an explicit involutive action-reversal convention;

FunctionalPresentation:
  atom respect plus forward and back transition clauses;

FiniteStateController:
  finite internal record, observation, update, and policy;

FiniteRealizationSpace:
  witness-to-candidate incidence;

DecoratedMayOmega:
  exact-duplicate quotient, complete fibers, compatibility support, and
  maximal-face summaries.
```

## Retained Run

Command:

```powershell
.\.venv\Scripts\python.exe -m `
  omega.validation.finite_relational_alpha_omega_foundation `
  --out-root `
  docs\research_notes\validation_results\alpha_omega_foundation_v0
```

Retained output:

```text
docs/research_notes/validation_results/alpha_omega_foundation_v0/20260801_071021/
```

Machine-readable artifacts:

```text
summary.json
case_results.csv
directionality.csv
presentations.csv
process_profiles.csv
omega_fibers.csv
report.md
```

All ten preregistered case groups passed. No kill condition fired.

## Directional Path-Law Results

At horizon 3:

| Fixture | Reciprocal support | Total variation | Forward/reversed KL | Directional |
| --- | --- | ---: | ---: | --- |
| balanced three-cycle | yes | 0.0 | 0.0 | no |
| 3/4-biased three-cycle | yes | 0.6875 | 1.6479184330021646 | yes |

The biased cycle has the same clockwise and counterclockwise support as the
balanced cycle. Its directionality is in the path weights.

Conditioning the biased cycle after the live prefix `s0 -> s1` produced four
two-step residual paths, all beginning at `s1`, with exact total probability
one.

The finite nonreturn fixture retains:

```text
return by horizon 2:
  1/10

nonreturn by horizon 2:
  9/10

support-level return:
  possible
```

This separates statistical or functional nonreturn from support impossibility.

The controlled contraction fixture retains:

```text
preserve-policy path support:
  2

collapse-policy path support:
  1

collapse terminal:
  sink

robust live viability kernel:
  {open, left, right}
```

The support-asymmetric absorbing case has three reachability-irreversible
pairs. It remains a diagnostic control, not an Alpha-Omega requirement.

## Support Blindness

The balanced and biased cycle kernels have identical action-labelled support.

The finite harness exhaustively checked:

```text
all 8 state subsets;
may predecessor;
robust same-action predecessor;
robust support viability;
and bounded support reachability through horizons 0, 1, 2, and 3.
```

Observed failures:

```text
predecessor:
  0

viability:
  0

reachability:
  0
```

The same pair differs in path-reversal divergence. This is the retained
boundary:

> Equal support determines support-only continuation operators. It does not
> determine weighted path-law directionality.

## Presentation Contracts

Retained controls:

```text
exact state/action relabeling:
  isomorphism

duplicate-state quotient:
  functional bisimulation, not isomorphism

erased exact edge:
  forward failure

fabricated presented edge:
  back failure

changed declared atom:
  atom-respect failure
```

A sixth fixture maps the biased three-cycle to one presented self-loop. It
passes support bisimulation and changes the weighted directionality profile
from nonzero to zero.

This is not an inconsistency. It demonstrates that support bisimulation
certifies support facts only. Weighted path facts require a contract that
preserves and reflects the declared path observable. Ordinary probabilistic
lumping is not presumed sufficient: the one-block quotient is stochastically
lumpable at the presented state level while erasing microscopic
path-reversal divergence.

## Candidate Process Profiles

The feature audit separates:

| Fixture | Causal deformer | Endogenous record selector | Persistent closed loop |
| --- | --- | --- | --- |
| passive pattern | no | no | yes |
| effectful memoryless controller | yes | no | yes |
| record-sensitive selector | yes | yes | yes |
| passive pattern with injected `agent` atom | no | no | yes |

The injected label changes no process feature.

Every row explicitly records:

```text
valuer_declared:
  false
```

The result supports a graded candidate-process filtration. It does not settle
valuerhood.

## Decorated May-Omega

The retained source is the generated shared-action hollow triangle:

```text
A:
  {a0, a1}

B:
  {a0, a2}

C:
  {a1, a2}
```

The fibers are:

```text
Real({A,B}) = {a0}
Real({A,C}) = {a1}
Real({B,C}) = {a2}
Real({A,B,C}) = {}
```

Consequently:

```text
all singletons compatible:
  true

all pairs compatible:
  true

triple compatible:
  false

maximal faces:
  3

greatest face:
  none
```

Downward-closure failures: 0.

Restriction identity/composition failures: 0.

Adding `A_copy` with exactly the same finite realization signature changes the
raw candidate census from three to four but leaves:

```text
quotient candidate-class count:
  3

complete structural fiber payload:
  unchanged
```

This quotient is intentionally narrow. In the v0 realization object, a
candidate is nothing beyond its complete finite incidence column. The result
does not license merging operational processes because they currently share a
bounded behavior profile, public state, or sampled witness set. Identity,
lineage, redundancy, and fungibility remain open.

Capital Omega in this v0 construction is the entire decorated family-to-fiber
object. The three maximal faces are reported; none is selected.

## What This Pays

The sprint establishes a stable lower interface between:

```text
weighted dynamics;
support-only continuation;
presentation soundness;
candidate process analysis;
and compatibility with higher-order obstruction.
```

It also clears three declaration risks:

1. `certified presentation` is replaced at this layer by explicit standard
   clauses.
2. `compatibility` is derived from nonempty realization fibers.
3. `valuer` is not installed as a binary label before process evidence exists.

## Remaining Foundation Debt

The following remain open:

```text
path-observable preservation/reflection for weighted presentations;
the exact boundary between stochastic lumpability and path-law soundness;
active-controller presentation transport;
process-boundary robustness across a declared projection family;
infinite-horizon path measures and monitorability;
robust realization fibers with the full exists-policy/forall-environment
quantifier;
operational identity and lineage;
standing;
and the moral bridge.
```

The next mathematical leg should harden process projections and weighted
presentations before attaching recovery or NOLP to candidate processes.

## Claim Boundary

This sprint does not prove:

```text
value;
standing;
personhood;
consciousness;
moral agency;
thermodynamic universality;
a preferred physical orientation;
normative allegiance;
lushness as an imperative;
or Omega as a realized moral object.
```

## Public Compression

A finite controlled system can be read at two levels: its transition support
and its weighted path law. Equal support fixes support-only reachability and
viability but can hide directional path statistics. Standard forward/back
presentation clauses preserve bounded relational facts. Candidate processes
can then be graded by causal effect, endogenous record, and persistence, while
their joint realizability forms a witness-retaining compatibility complex that
may have several incomparable maximal faces and genuine higher-order
obstructions.
