# Quantum record-structure follow-up v0 — frozen protocol

2026-10-02. Freeze this file before implementation/results and embed its
normalized-text SHA-256. This is a finite diagnostic follow-up, not a new
definition of lushness or an independently blinded discovery experiment.

## Questions and restrictions

Distinguish joint content, distribution of access, and downstream composition
without changing the underlying source supply. Also distinguish a localized
environmental record from the same record spread by local quantum interactions.
Apply the previous mutual-information candidate unchanged. No noise filtering,
physical-outcome quotient, preferred-sign coefficient, or scalar winner.

Register names are coordinates. Consistent renaming/reindexing of preparation,
gate incidence, observation boundaries, times and costs must preserve the
results. A rewiring with external attachments fixed is a different process.
No equivalence under arbitrary physical permutations or basis rotations is
assumed. Isomorphism tests apply to the complete declared finite apparatus.

## Panel A: one source bank, two routing preparations

Both variants start with three independent qubits S0,S1,S2, each in
diag(p,1-p), p in {0.8,0.5}, and nine blank qubits R0..2,D0..2,G0..2.
The three source qubits remain in the full model in both variants. There is no
extra entropy supplied to the plural variant. All gates use a declared common
serial actuator; each primitive occupies one time unit. A selectable source to
receiver bus supplies every S_i -> R_j pair. This is a finite hardware model,
not a claim that arbitrary nonlocal gates have equal physical energy cost.

The same selectable coupling architecture permits two initial route settings:

- Broadcast: CNOT S0 -> Ri, i=0,1,2.
- Plural: CNOT Si -> Ri, i=0,1,2.

There are exactly three active CNOTs in either setting. Record the cut at t=3.
Then, identically in both settings:

- CNOT Ri -> Di in i order, cut t=6.
- Toffoli Di,D_(i+1 mod 3) -> Gi in i order, cut t=9.

All controls are ordinary circuit operations, not assigned values or achievement
labels. The last bank exposes further consequences of joint input structure.
Its AND response is a declared calibration device, not a general constructor or
a preferred task. No conclusion about open-ended generativity follows from it.
Each variant has the same source preparation, blanks, architecture, gate counts,
primitive schedule and duration. Cost stays a vector: source/blank counts,
CNOT count, Toffoli count, elapsed time. No minimum-energy claim.

At each cut, retain the entire state and the actual joint output law. For the
current output bank B=R,D,G, report H(B), all labelled I(B_F:B_complement), the
source-to-single-register information matrix, source-to-pooled-bank information,
and the maximum number of disjoint singleton records containing at least 90%
of each source's entropy. Joint pooling is a mathematical frame observation;
it does not assert free physical collection or decoding of separated records.

Also compute the original Choi candidate for the boundary channel from the three
source inputs to S plus the current bank B, with virtual references I0..2:
I(F:complement F) for all 510 nontrivial fragments of these nine labelled legs.
Intermediate registers outside the interface are traced, retained in the full
circuit, and available only according to their declared connections. These are
boundary channels with input preparation slots, not a process tensor granting
arbitrary intervention at every internal gate. Verify contractions against direct
evolution for both diagonal preparations and |+> and |+i> on all inputs.

Analytic predictions already known: at the R cut broadcast has H(R)=h2(p),
plural H(R)=3h2(p). Broadcast has inter-fragment record information h2(p),
plural zero. For source-specific delivery to individual receivers the profiles
cross, while the pooled plural bank retains all three sources. No dimension or
lushness ranking is preregistered. All Choi comparisons and downstream laws are
to be reported, including ties or reversals.

## Panel B: spreading a retained record with matched controls

One source X in diag(p,1-p), p in {0.8,0.5}; blank record R; four blank bath
registers E0..3; blank decoder output D. CNOT X->R then SWAP R,E0 (three CNOTs)
resets R and places the record in E0. This costs four CNOT steps. X remains a
reference in the full physical model but has no further path to the recovery
apparatus. Do not call this a thermal reservoir or infer a Landauer heat bill.

Define a deterministic family of bath unitaries U_l, l=1..8. In increasing j,
apply R_y(theta_lj), then R_z(phi_lj) to E_j, where

    theta_lj = pi * sqrt(2) * (l+j+1) modulo 2*pi
    phi_lj   = pi * sqrt(3) * (2*l+j+1) modulo 2*pi.

Then apply CZ to adjacent pairs (0,1),(1,2),(2,3) in that order. Each U_l uses
eight local rotations plus three nearest-neighbour CZ gates, 11 serial steps.
The angles, order and maximum depth are frozen without looking at outcomes.

Two controls on the same four-qubit chain:

- Spreading: U1,U2,...,U8.
- Echo: U1,U1^-1,U2,U2^-1,U3,U3^-1,U4,U4^-1.

An inverse reverses the gate order and angles. Both use the same register count,
gate-type counts and duration at every numbered layer boundary. The echo is
localized only after even layers. Retain every boundary l=0..8 so its intermediate
delocalization is not erased by the summary. It is an active control with its own
cost, not an idle environment being claimed to have done the same work.

At each boundary and every nonempty bath fragment F, report:

- I(X:E_F), with X classical: Holevo information, an upper bound on information
  extractable by measuring that fragment, not a claim of a free optimal decoder;
- information about X in the actual local Z readout of that fragment;
- minimum-error binary discrimination success from the Helstrom formula,
  explicitly an unconstrained measurement ceiling, with prior-only baseline;
- the unchanged fragment:complement candidate on the whole bath marginal and
  on the X-plus-bath state, alongside the full source/record/bath/output state.

Retain min/mean/max across every fragment size as well as every labelled result.
Do not replace the actual source distribution by channel-capacity optimization.
Do not require small-fragment information to vanish or decrease monotonically.
Generic finite mixing may leave appreciable local information and may revive it.

At spreading depths 0,2,4,8, implement a recovery witness: physically undo the
completed layers in reverse order, then copy E0 to D. Record the D information
after undoing each possible suffix length, using a fresh diagnostic copy of the
same pre-readout state for each prefix. Charge all inverse gates plus that final
readout CNOT. The original X is never used to decode. This is one explicit
recovery strategy and cost certificate; it does not prove a minimum recovery
time, nor assert that no cheaper local decoder exists.

Known controls: global source/bath distinguishability survives the unitaries;
the echo restores the localized record after even layers; the full inverse
recovers it. The informative outcomes are the finite local access profiles,
their relation to the proposed summary, and how the declared recovery unfolds.

## Relational invariance and validation

Represent the apparatus with preparation nodes, physical register nodes, timed
gate nodes, directed control/target incidence, observation attachments and cost
attributes. Consistently rename all of these and permute the numerical basis;
verify graph isomorphism and matching states/profile entries after mapping back.
Broadcast and plural must not become isomorphic by a mere name change.

An embedded identity-versus-SWAP calibration uses two independent sources, an
additional record of the first source, and a downstream reader of the first
receiver. These attachments physically distinguish the input/output roles.
The two routes have matched gate counts but different anchor-to-reader laws;
test complete-apparatus non-isomorphism. In this control source entropy is one
bit. It is an analytic hygiene check, not discovery of routing physics.

Use the previously checked finite quantum helper without changing its entropy
functional. Exact finite enumeration with floating-point linear algebra; no
Monte Carlo, seed search or fitting. Probability/matrix tolerance 1e-11 and
entropy/information tolerance 1e-9. Check positivity, normalization, dense/sparse
agreement on representative states, channel trace constraints, actual-source
contraction, full-state spectrum preservation, inverse recovery, and relabelling.
Validation mistakes may be fixed without altering the candidate or this freeze.

Export machine-readable matrices, gates, probabilities, resource bills, labelled
profiles, protocol/source hashes and a report. Keep prior artifacts intact.
Work on the current branch without commit, push or migration.
