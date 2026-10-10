# Quantum frame-profile probe v0 — frozen protocol

Date: 2026-10-01. Status: bounded candidate test, not a lushness definition.
This protocol is written before the implementation and numerical results. Its
normalized-text SHA-256 will be embedded in the runner. The analytic controls
and proposed counterexamples are already known; this is not blinded discovery.

## Question and frozen readout

Does Opus's proposed process-correlation profile detect the changing record
couplings of a small quantum apparatus, and what does it omit?

For a normalized process Choi operator J, retain every labelled nonempty proper
fragment F and compute, in bits,

    I_J(F : complement F) = S(J_F) + S(J_complement F) - S(J).

Also report its minimum, mean and maximum at each fragment size. Size averages
are summaries of the labelled data, not a replacement for them. No noise is
removed, no physical branches are quotiented, and no fitted term repairs the
readout. No scalar lushness ordering is declared.

Choi input-reference legs are mathematical probe legs, not physical records.
Alongside J, compute the actual output law with independent source bits having
P(S=0)=0.8 (and the prespecified fair-source control 0.5). Record the classical
Z-readout mutual information from each source into every single output register,
the downstream channel, and the maximum number of disjoint singleton records
holding at least 90% of that source's entropy. This last number is explicitly a
restricted readable-record diagnostic, not general quantum redundancy.

## Common finite circuit

There are one or two rounds, each of duration five declared time units. Each
round receives a fresh source qubit S and five blank qubits R, M, D, K, E.
R is a record, M a relay, D the downstream register, K an auxiliary record,
and E an initially blank erasure bath. Outputs S,R,M,D,K leave the apparatus
after that round and are retained. E stays in the environment. Memory comprises
wire W, link L (initially zero), erasure switch e, alignment switch c, copy
switch p, and a common delay bit Q retained across both rounds. W,L,e,c,p are
classical registers. Q has a declared diagonal quantum state. All variants use
the following controlled circuit and differ only in initial preparation:

1. At round time 1, CNOT S->R; if p=1 also CNOT S->K.
2. At time 2, if e=1 SWAP R,E. The record is relocated, not destroyed globally.
3. At time 3, if W=1 and Q=0, CNOT R->M.
4. At time 4, if c=1 and e=0 set L=W=1. Also CNOT Q->K.
5. At time 5, if L=1, CNOT M->D.

The classical configuration update is part of the declared dynamics, with its
old value retained in the implementation's configuration history; it is not a
claim of cost-free logical erasure. Finite fresh blanks and fixed control slots
are charged in an apparatus bill. No thermodynamic minimum is inferred.

Preparations (W,e,c,p,P(Q=1)):

| Name | Preparation |
|---|---|
| intact | (1,0,1,0,0) |
| damaged | (0,0,1,0,0) |
| erased | (1,1,1,0,0) |
| cycling | (1,0,0,0,0) |
| photocopier | (1,0,1,1,0) |
| common_delay | (1,0,1,0,0.2) |

The last preparation has the same persistent random blockage in both rounds,
and records that common cause in K. It is a two-round delay/blockage control,
not a statement about eventual recovery. Copying and consequential noise are
real physical differences: higher profile values are observations, not automatic
failures or reasons to delete them.

This is a new, smaller quantum record-network analogue of the earlier ten-fuel
classical relay apparatus, not its exact quantization. There are no exponential
clocks and no unbounded continuation claim. Every round uses the same primitive
controlled operations. Unused outputs and bath qubits remain in the model.

## Quantum process and actual-law construction

For the Choi construction, put each fresh S in a Bell pair with reference I,
execute the common circuit in physical order, and trace only the declared
inaccessible E,Q environment. Retain legs I,S,R,M,D,K per round in their
physical/time-labelled order. This is the normalized Choi state of a sequential
memory channel (a comb), with a preparation slot each round and outgoing
registers that never re-enter. It is not a process tensor with arbitrary access
to every internal gate. The actual source states and any later instruments are
contracted with that comb; the Bell probe does not supply their physical law.

For actual laws, prepare independent diagonal source states directly and use
the same circuit, retaining the same physical outputs without I. Independently
contract the Choi operator against each tested source preparation and compare
the complete output density operator with direct evolution. Check the comb's
causal trace constraints. Include a coherent |+> preparation in this contraction
check, even though the fixed-source record statistics use diagonal preparations.
The model remains quantum: global phases/coherences are retained by the circuit,
and erasure keeps its bath. Z-readout statistics are only a declared diagnostic.

Retain the circuit, initial states, configuration history, actual joint output
laws, labelled Choi profiles, actual-state profiles and source/source-reader
diagnostics. Tracing E for the declared interface is not physical noise removal
from the underlying model. This interface is a bounded frame, not the ultimate
frame or a canonical partition of the universe.

## Analytic controls frozen before results

1. GHZ record: sqrt(0.8)|0000> + sqrt(0.2)|1111>. A nontrivial
   fragment versus its complement has 2 h2(0.8) mutual information. A designated
   system versus a proper nonempty environment fragment has h2(0.8); the full
   environment gives 2 h2(0.8). Distinguish these partitions.
2. Two-qubit identity versus SWAP channel: all size-indexed multisets of
   I(F:complement) agree, while physically labelled cross-channel pairs differ.
3. One-qubit identity versus Hadamard: all Choi fragment mutual informations
   agree, while fixed Z preparation/readout gives one versus zero bits for a
   fair source. This is a calibration of a bare-channel summary against a fixed
   physical reader, not a claim that the full reader-inclusive processes agree.
4. Temporal subdivision: one identity channel versus two connected identity
   channels have equal composed input-output Choi states. The two-open-slot
   comb has more legs and can have a different raw size profile. Join the
   channels by composition, not partial trace, and report both facts.
5. Retained bath: erased versus intact must preserve normalization of the full
   model. Where a record is swapped to E, E must retain the source information.

## Predictions, outcomes and interpretation

Expected operational calibration: intact transmits in both rounds, damaged
only in the second, erased and cycling never deliver source information to D.
The candidate might separate these, tie some, or rank them differently across
fragments. Publish all outcomes. Do not retrofit a sign or a preferred profile.
Photocopier and common-delay outcomes assess attribution: which extra
correlations are copies, which concern the shared blockage, and which convey
the source downstream? They are not exclusion rules for noise or copying.

Separating the four cases establishes finite sensitivity to these couplings.
It does not establish a complete measure of physical access, a generativity
measure, an ethical verdict, an infinite-object invariant, or uniqueness.
Profile collisions are diagnosed at the level of the summary and the declared
interface. Retaining the full comb beside the summary does not cure a collision.
No quantum-to-classical branch selection theorem is being tested here.

Use exact finite state evolution and deterministic enumeration (floating-point
linear algebra, no Monte Carlo); entropy tolerance 1e-10 bits, matrix/probability
tolerance 1e-12. Numerical/calculation errors may be fixed transparently without
altering this contract. Write targeted tests, an evidence file with source hashes
and environment, and a report. Keep existing work and do not commit or push.

## Sources

- Pollock et al., process tensors: https://arxiv.org/abs/1512.00589
- Chiribella et al., quantum networks/combs: https://arxiv.org/abs/0904.4483
- Zambon, limitations of Choi-derived process measures:
  https://arxiv.org/abs/2407.15712
- Le and Olaya-Castro, readable records versus quantum mutual information:
  https://arxiv.org/abs/1803.08936
