# Quantum frame-profile probe v0 — results

2026-10-01. Exact finite calculation on the current Omega research branch.

**The proposed labelled correlation profile detects the four arrangements and
their different recovery histories. It is useful as a diagnostic. It is not yet
a complete lushness comparison.** Size averaging hides which physical couplings
changed; recorded blockage can raise every size average while source delivery
falls. Independent controls also show that even the labelled entropy profile
can miss distinctions relevant to a fixed physical reader.

These are results about a frozen, small circuit and a specific readout. They do
not reject the substrate motivation, erase consequential noise, or establish an
ethical ranking. The known-answer controls are validation, not independent
empirical discovery. No fitted correction was added.

## What was actually run

The [protocol](quantum_frame_profile_protocol_v0.md) was saved and hashed before
implementation and calculation:

`769a83462ed7eead9e85973273546f265b1815437619eb19aedfbd6e448acd2e`

One common controlled circuit ran for one or two rounds, with record, relay,
downstream, auxiliary-record and erasure-bath qubits. Preparation switches made
it intact, initially damaged, record-erasing, or unable to install its output
link (the cycling label inherited from the earlier analogue). Additional
preparations copied a source into an extra register, or introduced a shared
20% blockage recorded in the auxiliary registers. The same blockage persisted
through both rounds. Every new blank, source qubit, control slot and physical
round was listed in the bill. This is a two-round circuit with discrete times,
not the earlier ten-fuel stochastic net and not an asymptotic model.

The process is a sequential quantum memory channel, with source-preparation
slots and outgoing registers at each round. Its normalized Choi state has six
legs per round: a virtual input reference and five physical outputs. All 62
nontrivial fragments at one round, and all 4,094 at two rounds, were retained
with their physical/time labels. For each,

\[
P_J(F)=I_J(F:\bar F)=S(J_F)+S(J_{\bar F})-S(J).
\]

The full underlying circuit retains its bath and delay memory. Their partial
trace specifies this bounded interface; it does not remove physical noise from
the underlying model. No quotient, noise filter or optimizing chooser was used.
The Choi probe's virtual references are explicitly distinguished from physical
records and frame-conditioned source probabilities.

Actual output states were separately evolved for source probabilities 0.8/0.2
and 0.5/0.5, plus coherent `|+>` and `|+i>` preparations. Contraction of the Choi
process with those preparations reproduced direct evolution. The report below
uses the 0.8/0.2 physical law, whose source entropy is 0.721928 bits. All other
prespecified results are retained in the evidence.

## The four arrangements are distinguishable

The two downstream columns give mutual information between the actual source
and the downstream register under their declared Z readout. They are operational
calibration facts, not substitute utility scores. The Choi columns are the mean
of F:complement information over single-leg fragments, shown only as compact
summaries; the calculation retains all labelled fragments.

| Preparation | Downstream, round 1 | Downstream, round 2 | Choi singleton mean, H=5 | Choi singleton mean, H=10 |
|---|---:|---:|---:|---:|
| Intact | 0.721928 | 0.721928 | 1.666667 | 1.666667 |
| Damaged, then repaired | 0 | 0.721928 | 1.000000 | 1.333333 |
| Erased record | 0 | 0 | 0.333333 | 0.333333 |
| Cycling / output link absent | 0 | 0 | 1.333333 | 1.333333 |
| Photocopier | 0.721928 | 0.721928 | 2.000000 | 2.000000 |
| Common blockage | 0.489924 | 0.489924 | 1.687447 | 1.710638 |

All numbers are bits. These are different quantities: a Choi singleton's
information with the rest is not the information a physical record contains
about a specified source.

The full labelled Choi profiles separate all four base preparations at both
horizons. Intact is componentwise no smaller than damaged, erased and cycling
in this example. At two rounds, damaged and cycling cross: damaged is larger
on 224 fragments, smaller on 480, and tied on 3,390. Repair restores a later
downstream connection, while cycling preserves other earlier records. The
profile records that difference without declaring a scalar winner.

In particular, the two-round singleton means of damaged and cycling tie. For
every other fragment size, cycling's mean is larger. Averaging across locations
cannot tell the reader that one apparatus has restored its downstream link and
the other still has none. Their labelled data and actual process laws can.

In the erased preparation, each bath qubit retains all 0.721928 bits about its
source. The output-frame loss is a relocation of access in this model, not an
annihilation of information in the whole. The coherent Choi construction also
retains the distinction: the full one-round state is pure, while tracing the
erasure bath leaves interface entropy one bit.

## What the two pumps do

**Copying adds correlated records.** It raises the labelled Choi profile on
252 of the 4,094 two-round fragments and leaves the rest tied with intact.
Each source has four disjoint singleton readers holding at least 90% of its
entropy, versus three for intact. Downstream source information is unchanged.
This is real additional distribution of an existing record, with a physical
register and a controlled operation. It does not demonstrate a new kind of
continuation or recursive generativity, but is not dismissed as fake structure.

**Shared blockage raises the size averages while reducing source delivery.**
At two rounds, every fragment-size mean is larger than intact's. For example,
the six-leg mean rises from 3.939394 to 4.437469 bits. Yet each downstream
register carries only 0.489924 source bits, down from 0.721928. The auxiliary
records carry the common cause: I(K1:K2)=0.721928 bits under the actual law.
They carry zero information about either independent source.

The labelled Choi profiles expose both changes. Relative to intact, blockage
has lower values on 256 fragments, higher values on 3,742, and ties on 96.
For instance, I(D1:rest) falls from 2 to 1.770951, while I(K1:rest) rises from
zero to 0.721928. Thus the size profile suggests an across-the-board increase
where the labelled profile records a tradeoff between different couplings.

This is not an argument that consequential randomness must count negatively.
The additional common-cause correlations and the impaired source channel both
belong to the field. The current profile does not supply a principled rule for
their comparison as lushness. Removing one of them to force the desired verdict
would evade the experiment.

## What the analytic controls establish

1. **Partition matters.** In the biased four-qubit GHZ record, every nontrivial
   F:complement value is 1.443856 bits. A designated system versus one proper
   environmental fragment gives 0.721928; versus its whole environment gives
   1.443856. The proposed readout cannot inherit a readable-record plateau from
   a different partition merely by using the word access.
2. **Size profiles lose routing.** Two-qubit identity and SWAP have identical
   multisets at every fragment size. The physically labelled I1-to-O1 mutual
   information is two bits for identity and zero for SWAP. This is a collision
   of the size summary, not of the complete Choi processes.
3. **Even labelled entropy profiles are incomplete.** One-qubit identity and
   Hadamard have the same complete nontrivial Choi fragment profile: two bits.
   With the frozen fair Z encoder and Z reader, they deliver one and zero
   classical bits respectively. A freely available compensating rotation could
   remove that difference, but none is included in this fixed-reader test.
   This compares bare-channel summaries with a declared reader; the complete
   reader-and-preparation-inclusive processes need not share a profile.
4. **Composition is not counting time legs.** Two identity stages, joined by
   the channel link product, reproduce the one-stage input-output Choi state.
   The two-open-slot comb has four legs and a two-leg mean of 2.666667 bits;
   the original two-leg channel has no corresponding family of extra ports.
   Opening a slot changes the intervention interface. A passive subdivision
   must be joined back up before comparison. This is a boundary obligation,
   not evidence that physical identity evolution manufactures lushness.

These controls constrain what the profile can claim. In particular, quantum
mutual information on a normalized Choi operator is a correlation diagnostic,
not automatically the amount a bounded physical reader can extract, nor a
monotone under all allowed process transformations.

## What this advances and what remains

The previous timing-volume summary was systematically blind to record/relay
coupling. This candidate is sensitive to that coupling on a quantum circuit,
and retains both recorded randomness and finite recovery delays. That is a
concrete improvement in the readout, demonstrated on a new analogue rather
than a rerun of the identical classical dynamics.

The stronger claim remains unearned: neither the size profile nor the full
labelled mutual-information profile is established as the extent of accessible
quantum continuation. The size summary loses causal location; entropy data can
also lose distinctions relevant to a constrained instrument. A complete comb
retained beside those statistics does not repair their omissions.

Keep the quantum process representation and these profiles as diagnostics.
The next specification should require a comparison to retain how physical
interfaces compose and which transformations connect their records. It must
also say how those relations are compared as extent; naming a richer object
alone is insufficient. This experiment supplies concrete witnesses for that
obligation. It does not justify another coefficient, a noise quotient, or an
ethical verdict from summed correlations.

This finite circuit does not test open-ended construction, irreversible harm
in general, all instruments, quantum field factorization, a unique branch basis,
an ultimate-frame limit, or a relation to every potential valuer. Its switches
and operations are declared model physics, not derived from AlphaCore. The
redelivery result is a two-round repair witness, not permanent-correction or
asymptotic robustness evidence.

## Reproduction and verification

From the repository root, using its existing Python environment:

```powershell
& '.venv/Scripts/python.exe' -m omega_v2.validation.quantum_frame_profile_v0
& '.venv/Scripts/python.exe' -m pytest tests/test_quantum_frame_profile.py -q
& '.venv/Scripts/python.exe' -m ruff check omega_v2/finite/quantum_profile.py omega_v2/experiments/quantum_frame_profile_v0.py omega_v2/validation/quantum_frame_profile_v0.py tests/test_quantum_frame_profile.py
```

Nineteen targeted tests passed; lint passed. Tests include an independent dense
partial-trace/Schmidt calculation, closed-form complete classical output laws,
coherent Choi contractions, comb causality, retained bath information and the
analytic controls. Maximum errors: normalization 6.67e-16; causal trace
1.12e-16; physical-source contraction 3.34e-16. Reported near-zero negative
mutual informations in raw data are floating-point residuals, not negative
physical information. No Monte Carlo estimator or parameter search was used.

- [Full evidence, labelled profiles, states, bills and source hashes](../validation_results/quantum_frame_profile_v0/20261001/evidence.json)
- [Compact numerical summary](../validation_results/quantum_frame_profile_v0/20261001/summary.json)
- [Verification record](../validation_results/quantum_frame_profile_v0/20261001/verification.json)

No full-repository test-suite claim, push, commit, or successor-repository
migration is made.

The representation uses the process/comb framework of
[Pollock et al.](https://arxiv.org/abs/1512.00589) and
[Chiribella et al.](https://arxiv.org/abs/0904.4483). The distinctions between
quantum mutual information and readable records are developed by
[Le and Olaya-Castro](https://arxiv.org/abs/1803.08936). Caution about treating
Choi-derived quantities as general process monotones is supported by
[Zambon](https://arxiv.org/abs/2407.15712); this run does not reproduce that paper's
particular counterexample.
