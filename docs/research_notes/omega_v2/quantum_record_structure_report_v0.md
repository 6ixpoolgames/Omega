# Quantum record-structure follow-up v0 — results

2026-10-02. Frozen finite quantum calculation; no fitted score or ethical ranking.

**The follow-up separates three things that the correlation profile conflates:
how many independent distinctions are recorded, where a distinction can be read,
and the correlations produced while that distinction spreads.** Keeping physical
labels is necessary for routing, but insufficient to turn fragment-versus-rest
mutual information into a general access comparison.

The strongest counterexample is the four-qubit environment. Its labelled
fragment:complement profile increases everywhere after mixing, while information
about the original source becomes much harder to obtain locally. This is a
failure of interpreting profile dominance as improvement in every form of
access. It does not by itself decide which complete continuation is lusher.

## Frozen scope and apparatus

The [protocol](quantum_record_structure_protocol_v0.md) was written and hashed
before implementation or results:

`1dec4d4067a456a24a61d14fd0e071951405f9518225f4eac30aea7d6cd41bcd`

Panel A uses the same three independent source qubits and nine blank registers
in both preparations. It changes the routing: broadcast one source to three
receivers, or route a different source to each receiver. Both execute three
CNOTs through the same declared serial bus. Both then execute the same three
local relay CNOTs, followed by the same three pair-controlled Toffoli operations
into a third output bank. The source bank, blanks, permitted links, primitive
counts and clock times match. Independent content was not added to one variant.

Panel B transfers one source record into a four-qubit environment, then executes
eight layers of frozen nearest-neighbour CZ and local rotation gates. A matched
echo control alternates a layer with its inverse. Each layer in either control
costs eight rotations, three CZ gates and eleven serial time units. The echo
restores the localized record after even layers. Every intermediate layer is
retained, including its temporary spreading. The angles were fixed before the
run; no circuits or seeds were selected for a desired outcome.

The environment is a finite driven quantum chain. It is not claimed to be a
thermal reservoir; the bill is a circuit-resource vector, not Landauer heat.
The input source remains in the full model and supplies the reference for
information measurements. The recovery apparatus has no connection to it.

Both panels use the physical source laws P(0)=0.8 and P(0)=0.5. Boundary-channel
Choi states are computed separately in Panel A, and contracted with those laws
and coherent |+> and |+i> preparations. Bell probe weights are not substituted
for the physical law. Panel B reports actual-state versions of the entropy
profile, not a new multi-time Choi calculation.

## 1. Copies versus independent records: a real tradeoff

For fair sources, the receiver bank gives:

| Observation at the receiver cut | Broadcast | Plural |
|---|---:|---:|
| Joint recorded content | 1 bit | 3 bits |
| Receivers holding the first source | 3 | 1 |
| Receivers holding each other source | 0 | 1 each |
| I(fragment : other receivers), every proper nonempty split | 1 bit | 0 bits |

For P(0)=0.8, the content values are 0.721928 and 2.165784 bits. The full source
bank has 2.165784 bits in both arrangements throughout. The difference concerns
what the receiver bank holds and where it holds it, not new global information.

Thus the proposed content prediction is confirmed under its independence
assumptions. Exact copies have constant joint content as their number increases;
there is no universal log-N content law for perfect copies. Their distribution
of access changes: more receivers hold the same source. Source-to-location
delivery profiles cross. If the receivers are pooled mathematically, the plural
bank preserves all three sources, including the one broadcast elsewhere.

The record-only mutual-information profile prefers copies because it measures
correlation among receivers. Independent records have no such correlation. This
is not a numerical defect. It is a precise reason that the profile cannot be
read as joint distinct content.

## 2. Further composition changes the comparison

The next three CNOTs deliver the receiver records faithfully to local downstream
registers. Then each Toffoli records the AND of two adjacent downstream bits.
The same primitives act in both worlds; no purpose or utility is assigned to
their outputs.

| Source law | Broadcast joint content in final bank | Plural joint content in final bank |
|---|---:|---:|
| P(0)=0.5 | 1.000000 | 2.000000 |
| P(0)=0.8 | 0.721928 | 0.674394 |

For the biased source, broadcasting synchronizes the pair controls, whereas
independent inputs rarely satisfy both. The final bank's entropy order reverses
between the two frozen source laws. This is a fact about this specified physical
composition. It is not a verdict that synchronized copies are generally better,
or that an AND bank is a definition of construction. Upstream records remain
in the full state; final-bank entropy is not total field content.

The full labelled Choi profiles cross in all three cuts. Comparing broadcast
minus plural, the counts of larger/smaller/tied fragment values are:

| Cut | Larger | Smaller | Tied |
|---|---:|---:|---:|
| Receivers, t=3 | 54 | 188 | 268 |
| Local delivery, t=6 | 286 | 84 | 140 |
| Pair-controlled outputs, t=9 | 392 | 96 | 22 |

There is also an informative boundary effect: at the receiver cut, size-averaged
Choi correlations favor plurality (except tied singletons and their complements).
After the faithful local delivery they favor broadcasting at every size, despite
unchanged classical source delivery to the corresponding output bank. The
quantum channels are different: intermediate records outside the chosen output
boundary retain correlations and dephase parts of the reduced channel. This is
not a harmless renaming. It shows why a boundary-channel Choi profile must not
be identified with the complete field or with its classical readable content.

## 3. Global retention survives while local access declines

For the fair source, at the eighth layer boundary, both controls retain exactly
one bit about the original source in the entire four-qubit environment. Their
local structure differs substantially:

| Quantity at matched time and gate count | Echo: localized again | Spreading |
|---|---:|---:|
| Best single-qubit source information, quantum upper bound | 1.000000 | 0.091593 |
| Mean single-qubit source information, quantum upper bound | 0.250000 | 0.057852 |
| Best single-qubit source information, fixed Z readout | 1.000000 | 0.076947 |
| Best single-qubit ideal binary guess success | 1.000000 | 0.673486 |
| Entire bath's source information, quantum upper bound | 1.000000 | 1.000000 |
| Entire bath's source information under local Z readout | 1.000000 | 0.300191 |

Here the source is classical. I(source:fragment) is its Holevo information,
an upper bound on information obtainable from that fragment. The optimal binary
guess figure assumes arbitrary measurement on the fragment and is explicitly
an ideal ceiling. The local Z figure uses the declared readout. These are not
three interchangeable notions of physically available access.

The distribution across fragment sizes is also retained. In the spreading case,
the best two-qubit fragment has 0.507617 source bits and the best three-qubit
fragment 0.914131; the full environment has one. No small-fragment-zero rule was
imposed. Local information partly revives between some depths. For example, the
largest singleton value at depth four is 0.071116, and at depth eight it is
0.091593. Eight layers are not an asymptotic mixing claim.

With the biased source, the best singleton at depth eight carries 0.057709 bits,
while the full bath retains 0.721928. Its single-fragment minimum-error guessing
ceiling equals the 0.8 prior-only baseline at that depth. That does not imply
zero information: a binary error objective can favor always guessing the more
likely source even when a fragment contains some information.

## 4. The unchanged correlation profile goes up

For the fair source at depth eight, the mean singleton-versus-rest correlation
inside the bath is **0 for the echo and 1.653701 bits for spreading**. All 14
nontrivial labelled fragment:complement values are larger after spreading.

Including the source reference does not resolve this: of the 30 nontrivial
fragment:complement values on source plus bath, spreading raises 28 and leaves
two tied. None decreases. Meanwhile the source-to-single-fragment information
has fallen as shown above.

This is stronger than the earlier size-averaging problem. The labels remain,
but each fragment's information with everything else mixes information about
the source with other quantum correlations. Those correlations are real and
remain in the object. They cannot simply be counted as improvement in every
physical access relation.

Consequently, retaining all labels does not make this particular profile a
complete description of access. The experiment does not authorize subtracting
entanglement, suppressing noise, or declaring spreading intrinsically worse.
It exposes the unresolved comparison between different structural changes.

## 5. Recovery has a physical witness and an explicit bill

An inverse circuit, using only the bath and a blank output register, recovers
the source exactly. It never consults the retained original source. Undoing
all eight layers requires 64 rotations and 24 nearest-neighbour CZ operations,
then one CNOT to deliver the recovered bit: **89 additional serial steps**.
The echo at the same forward-time boundary needs only the final readout CNOT
for this witness.

At spreading depths zero, two, four and eight, the complete inverse witnesses
cost 1, 23, 45 and 89 extra steps respectively, each recovering all source
information with unit raw bit agreement within numerical tolerance. Every
partial inverse is recorded too. Recovery information need not rise monotonically
at each intermediate step, and raw bit agreement is not an optimal guessing
probability: some intermediate records are approximately inverted.

These are exhibited procedures, not proofs of minimum recovery time. The run
did not search all decoders or show that the optimal cost must grow at this rate.

## 6. Names versus structure

Consistently renaming the full preparation/gate/observation graph and reversing
the numerical basis order preserves the resulting physical states and mapped
record profiles. Broadcast and plural apparatuses are not isomorphic: their
source-to-receiver incidence differs.

The identity/SWAP control includes both an external source record and a fixed
downstream reader. These physical attachments distinguish the relevant input
and output roles. The two complete apparatuses are not isomorphic; the source
anchor and downstream reader share one bit in the identity case and zero in
the swapped case. This confirms the intended relational rule without assigning
content to arbitrary register names. These are validation controls with known
answers, not discoveries about a general isomorphism classification.

## Consequence for the programme

This follow-up supports keeping distinct content, distributed readability,
composition and recovery inside the quantum continuation representation. It
does not supply a single measure of their combined extent. In particular:

- Greater recorded content need not mean greater local redundancy.
- A copied distinction can have further consequences at additional locations.
- A globally retained distinction can become locally difficult to retrieve.
- Larger labelled fragment:rest correlations do not entail improvement in
  every source-to-frame access relation.

The source-specific observations here are calibration probes, not a privileged
class of valuers or requirements defining lushness. A general comparison must
account for the physical relations among frames without treating an arbitrary
choice of source, output bank or reader as the whole field. Nothing in this run
establishes that all those relations can already be aggregated into a principled
volume-like comparison. No preferred sign, correction factor, or diversity bonus
has been supplied to force agreement.

## Verification and reproduction

```powershell
& '.venv/Scripts/python.exe' -m omega_v2.validation.quantum_record_structure_v0
& '.venv/Scripts/python.exe' -m pytest tests/test_quantum_record_structure.py tests/test_quantum_frame_profile.py -q
& '.venv/Scripts/python.exe' -m ruff check omega_v2/experiments/quantum_record_structure_v0.py omega_v2/validation/quantum_record_structure_v0.py tests/test_quantum_record_structure.py
```

**35 targeted tests passed: 16 new checks plus the previous 19 quantum checks.
Lint passed.** Validation includes independently derived full Boolean output
laws, a dense quantum-gate and partial-trace comparison, coherent Choi
contractions, full-state inverse restoration, conserved spectra, resource
accounting, and relational isomorphism controls.

Maximum probability/matrix errors were below 1.8e-15; the largest source/bath
information conservation error was 1.03e-14 bits. Small negative information
values and guessing probabilities infinitesimally above one in raw data are
floating-point residuals. Positive physical probabilities were not filtered.

Initial test collection found the already-declared NetworkX dependency absent
from the local environment. NetworkX 3.7 was installed and verified by the
successful tests. Two lint issues were fixed before running the experiment.
The frozen contract and candidate were unchanged. No numerical outcome required
a repair, and no favorable circuit was selected after viewing results.
The final relational audit added the complete source density matrices to the
preparation nodes and a check that different source laws cannot be identified
by renaming. The calculation was rerun with the final source hashes; the
reported physical results were unchanged.

- [Protocol](quantum_record_structure_protocol_v0.md)
- [Full evidence: matrices, gates, laws, profiles, bills and hashes](../validation_results/quantum_record_structure_v0/20261002/evidence.json)
- [Compact numerical summary](../validation_results/quantum_record_structure_v0/20261002/summary.json)
- [Verification record](../validation_results/quantum_record_structure_v0/20261002/verification.json)

No full-repository test-suite claim, commit, push, or migration. This is one
finite, explicitly engineered apparatus and one deterministic mixing sequence.
It is not an independently authored empirical test, a generic thermal bath,
an open-ended constructor, or a demonstrated ethical bridge.
