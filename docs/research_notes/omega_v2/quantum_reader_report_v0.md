# Physical reader alternatives and multitime record breadth

2026-10-07. Exact follow-up to quantum_extent_v0. User asks whether Z/X resolution
can itself be a weighted physical alternative, whether finest resolution suffices,
and whether an established construction fits better than a bespoke extent.

## Main result

Yes: include the setting mechanism, recording interactions and memory inside the
unitary physical model. Count its actual joint records with native Born weights.
Do not sum independently normalized results of hypothetical alternative experiments.
This removes an external setting distribution from the toy: the setting weights
come from the specified initial controller state. The controller's preparation
and recording couplings remain explicit adapter assumptions.

The complete quantum state is propagated, not a collapsed state or a probability
vector. Output probabilities summarize specified physical pointer records. These
finite ideal memory circuits do not derive real-world pointer states or irreversible
macroscopic decoherence from microscopic physics.

## Endogenous setting experiment

Three qubits C,S,M start with S=M=0 and C=sqrt(r)|0>+sqrt(1-r)|1>.
C=0 controls a Z recording interaction on S,M; C=1 controls X recording.
Z recording is CNOT S->M. X recording is H_S CNOT H_S, preserving X eigenstates.
The complete controlled unitary retains C; it does not replace C by an externally
sampled classical variable. For the recorded C,M alternatives the outcomes are

    p(Z,0)=r; p(Z,1)=0; p(X,0)=p(X,1)=(1-r)/2.

| r | Joint C,M breadth | M-only breadth |
|---:|---:|---:|
| .25 | 2.951152 | 1.937819 |
| .50 | 2.828427 | 1.754765 |
| .75 | 2.086779 | 1.457569 |

The joint entropy obeys H(C,M)=H(C)+(1-r)ln2 to 1.11e-16. At r=.5, joint
breadth is 2sqrt2, from probabilities (.5,0,.25,.25). No sum of two separate
unit-mass experiments and no extra structural weighting occurs.

Actually recording both observables sequentially is also possible. With S initially
0 and two blank memories, Z then X yields memory law (.5,.5,0,0), breadth2;
X then Z yields (.25,.25,.25,.25), breadth4. These are different physical
interactions, including disturbance, not two resolutions of one unchanged
joint classical state. Noncommuting sharp observables lack a common sharp
joint refinement: finer resolution within one commuting algebra does not
produce a universal classical partition encompassing all observables.

## Two-round history experiment

Four qubits S,M1,M2,E start at0000. H on S followed by CNOT S->M1 creates
the first record. Then retain M1, undo the recording via CNOT S->M1, or transfer
M1 into E via SWAP. Apply H on S and CNOT S->M2 for the next recording episode.
Keep the same full physical register space for all three cases.

| Treatment of first record | Final M1,M2,E breadth | M1,M2 only | Fine-history diagonal breadth | Fine-history spectral breadth |
|---|---:|---:|---:|---:|
| Retain | 4 | 4 | 4 | 4 |
| Coherently uncompute | 1 | 1 | 4 | 2 |
| Transfer into E | 4 | 2 | 4 | 4 |

For the multitime analysis resolve M1 immediately after its recording, then the
complete final pointer tuple. These inserted projectors only resolve amplitudes;
they do not add a physical collapse. Retained/transfer history families have zero
off-diagonal D. Their final records retain both branching episodes, and the
ordinary classical chain rule yields breadth4. In the uncomputed case the
history off-diagonals reach .25: the fine histories are not classical exclusive
alternatives at the final cut. Coherent recombination gives one final outcome.

This is a distinction between inverse unitary recording and record relocation.
The environment is explicit, so transfer is not global loss of the first
distinction. Coherent uncomputation returns this known prepared superposition
to its original blank configuration; it does not map arbitrary orthogonal
inputs to one state. No irreversible many-to-one global unitary is assumed.

The results are final/joint-record breadth, not proof that the entire history
has one unit of extent after uncomputation. The D object retains the intervening
coherent development. A globally consistent complete-history perplexity cannot
be obtained by permanently treating the first record as classical after it is
coherently undone. This is the remaining quantum extension question.

## Established extent neighbor: observational entropy

For projectors P_i, single-time observational entropy uses

    S_O = -sum_i p_i ln(p_i/V_i), V_i=Tr(P_i).

This is a genuine established probability-plus-volume construction. Here its
reference volume counts unresolved Hilbert dimensions; it is not automatically
the root-reachable extent. The qubit |0> gives expS_O=1 in rank-one Z resolution
and2 in equally fine rank-one X resolution. Finest rank alone does not choose a
basis. For the r=.5 joint reader record, expH=2.828427, but expS_O=5.656854 due
to unresolved S. Add one inert blank ancilla while leaving it unresolved and
expS_O=11.313708; record probabilities and expH stay unchanged. This is correct
for that Hilbert-trace reference measure, not a failure of observational entropy.
It shows that adopting it as reachable extent requires a justified reference
space, rather than importing ambient dimensions as accessible possibilities.

## Recommendation

Use the established closed-system histories framework as the carrier and explicit
quantum recording instruments as local realizations. Let physical setting
mechanisms belong to the process. Derive a compatible retained-record history law
where possible, and apply classical perplexity there. Retain D wherever later
coherent manipulation prevents a classical history law. Do not normalize away
controller weights or treat them as a free ensemble of imagined readers.

The principal open step is an extent/profiling rule across physically supplied
record/history algebras, or a coherent functional that dispenses with such a
choice while preserving the intended classical limit. This probe does not
establish a canonical answer. Next useful numerical extension would vary the
strength and redundancy of actual environmental recording, and compare its
finite-time stability with a fixed physically local recombination dynamics.
That would test environment selection rather than declaring all fine projectors
to be persistent branches. It would not make inaccessible global information
cease to exist.

Eight circuit cases and five observational comparisons; exact matrices <=16x16.
Nine combined focused tests pass (four new, five earlier), lint clean. Native
normalization error <=4.45e-16; no sampling uncertainty. Raw output ignored under
results/local_runs/quantum_readers_v0. No commit/push requested or performed.
Two Luna agents provided narrow primary-literature lookups; parent implemented
and tested the circuits. See quantum_extent_literature_map_2026-10-07.md for
the established neighboring constructions and their limits.
