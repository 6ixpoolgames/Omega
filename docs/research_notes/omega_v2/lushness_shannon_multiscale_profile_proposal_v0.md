# Shannon and multiscale-profile lushness proposal v0

Date: 2026-10-01.

Status: recorded proposal, not adopted as the definition of lushness. No
implementation, simulation, proof-assistant verification, or empirical result
accompanies this note. The user requested that this proposal be logged before
returning to the narrower continuation-field formalization.

Provenance: an Opus proposal pasted by the user into the ongoing field-first
discussion, followed by Codex's mathematical assessment. Statements attributed
to the proposal below are distinct from retained results and open claims.

Related work: [continuation field candidate](continuation_field_candidate_v0.md)
and [finite concurrent contract](finite_concurrent_continuation_contract_v0.md).
The current discussion retains physical noise, uses the existing frame
construction for probability weighting, and treats lushness volume as the
intended comparison. A distance metric is not a prerequisite for every possible
volume measure; the earlier candidate's blanket metric requirement is too broad.

## 1. Proposed construction

Opus proposes the following specialization:

1. Represent a finite continuation window by jointly distributed classical
   variables X_1,...,X_n, associated with the adapter's finest space-time cells.
   Use the existing frame-conditioned probability law.
2. Take configurations up to structural isomorphism as carriers. Treat only
   genuinely redundant presentations of independent developments as identical.
   This requires retaining physically consequential time, location and context.
3. Use Shannon entropy H as log-volume, with effective volume V = 2^H when H
   is measured in bits. The proposed exclusive-alternative composition rule is
   H(branch label) + sum_r p_r H(continuation conditional on r). Independent
   effective volumes consequently multiply.
4. Construct Yeung's signed information atoms a_S for nonempty sets of parts S.
   For unit-scale parts, retain the degree profile

   C(k) = sum_{S: |S| >= k} a_S, for k = 1,...,n.

5. Compare systems by pointwise dominance of C(k), with crossing profiles left
   incomparable. No scalar tie-break is proposed.
6. Retain conditional continuation entropy and record-continuation mutual
   information as companion diagnostics.

The proposal starts with full permutation symmetry of the parts, intentionally
discarding their geometry and causal order in the degree profile. It suggests
restoring that information if the profile fails to distinguish persistence
from arbitrary correlation. It proposes growth of redundant information across
horizons as a candidate interpretation of generativity.

## 2. Claimed justification and its status

The proposal claims that harmless redescription, cut independence and linear
probability weighting force Shannon entropy through Faddeev's theorem. The
theorem does characterize entropy, up to scale, for continuous symmetric
functions of finite probability distributions satisfying its precise grouping
axiom. Applying this to log-volume is a candidate axiom choice. The project's
more general commitments have not been shown to imply that grouping axiom or
the reduction from structured physical fields to bare probability vectors.

The proposal further claims that permutation invariance makes C(k) the complete
set of nonprivileging readouts. This is false in general. Degree totals suffice
for invariant linear combinations of the atoms, but do not retain every
permutation-invariant property of their arrangement. The counterexample below
already lies inside a finite classical model.

The claims that atom signs settle physical readability, that growing redundant
mass constitutes generativity, and that frame cardinality removes the need to
represent decoding and interaction apparatus remain unsupported.

The proposed dismissal of information geometry is also not established:
parameters can describe physical configurations or couplings without a chosen
agent, and there is no general reduction of Fisher volume to channel capacity.
This does not establish Fisher volume as a suitable lushness measure either.

## 3. Retained identities and limitations

For unit-scale parts, the profile has the identities

- C(1) = H(X_1,...,X_n), which is log effective volume, not V itself.
- sum_{k=1}^n C(k) = sum_i H(X_i).
- sum_{k=2}^n C(k) = sum_i H(X_i) - H(X_1,...,X_n), the total correlation.

Consequently, two systems with the same sum of marginal entropies cannot have
strict pointwise profile dominance: equal total area plus coordinatewise
inequality forces coordinatewise equality. This limits the proposed comparison
in an important class of matched comparisons, rather than making the profile
an invalid dependency descriptor.

### A. Same profile, different dependency structure

Use six parts and six independent fair bits. Associate one bit with each edge
of a graph and store that bit at both endpoints. Compare a six-cycle with two
disjoint triangles. Each part holds two bits; each independent bit contributes
one degree-two information atom. Both profiles are

    C = (6, 6, 0, 0, 0, 0).

The first dependency graph is connected; the second consists of two independent
components. No renaming identifies them. Thus the profile discards a structural
distinction that nonprivileging permits. This is a hand-worked counterexample,
not a simulation result.

### B. Signed atoms and profile dominance

For three independent fair bits, C = (3,0,0). For three copies of one fair bit,
C = (1,1,1). Both have area three and neither dominates the other.

For independent fair A and B with C = A XOR B, the three-variable profile is
(2,2,-1). Pair-only information atoms are positive even though every pair of
variables is independent; the negative triple atom is part of the accounting.
Signed atoms therefore cannot generally be interpreted as independent packets
of information physically readable by exactly their named parts.

## 4. Physical scope and open obligations

- The degree profile does not retain distances, directions, communication
  mechanisms, durations or resource competition merely by being calculated on
  space-time variables. Those relations must remain in the underlying field.
- Attaching the full field to the profile preserves data for diagnosis; it does
  not make a comparison based solely on C(k) sensitive to the discarded data.
- A cell partition, resolution, horizon and actual conditioning frame must be
  specified. Renaming parts must be distinguished from changing physical
  factorization or adding actual record copies.
- Ordinary I-measure uses jointly distributed classical variables. Quantum
  histories and incompatible operations need a justified restriction or extension.
- Physical fluctuation is retained. A failed ranking is not grounds for deleting
  noise, selecting a favorable Hill order or adding an organization bonus.
- No connection to value, ethical protections, or the ultimate-frame ordering
  has been established by this proposal.

## 5. Disposition

Retain as a precisely calculable entropy-profile candidate or baseline within a
declared finite classical model. Do not promote its uniqueness or completeness
claims to programme axioms. No proposed automaton pre-check was run in this task.

The narrower field-first direction still owes an explicit volume functional.
Retaining a complete causal representation and naming candidate geometric tools
does not supply that functional. The next formalization work should state a
single finite construction and its unresolved choices without claiming that
the general volume problem has already been solved.

## References

- [Baez, Fritz and Leinster, A Characterization of Entropy in Terms of Information Loss](https://math.ucr.edu/home/baez/information_loss.pdf), including Faddeev's theorem.
- [Yeung, A New Outlook on Shannon's Information Measures](https://doi.org/10.1109/18.79902).
- [Allen, Stacey and Bar-Yam, Multiscale Information Theory and the Marginal Utility of Information](https://necsi.edu/multiscale-information-theory-and-the-marginal-utility-of-information), Entropy 19:273 (2017).
- [Authors' preprint, An Information-Theoretic Formalism for Multiscale Structure in Complex Systems](https://arxiv.org/abs/1409.4708).
