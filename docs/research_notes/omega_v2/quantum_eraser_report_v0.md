# Explicit quantum eraser v0: results

2026-10-08. User-requested exact comparison of coherent reversal, conditional quantum erasure and leaked records. Ninety-six profiles, six targeted tests, no proposed new lushness scalar.

## Main result

Physical which-path correlations determine the interference available in each declared continuation/readout. Coherent reversal restores unconditional interference only to the extent that no distinguishing copy is left outside the reversed interaction. Conditional erasure restores opposite conditional fringes; keeping both outcomes leaves the signal marginal unchanged. Delaying the conditional eraser until after signal recording gives the same joint final state in this model.

This is consistent with quantum erasure, not an empirical discovery of new quantum physics. It calibrates the finite Omega adapter and rules out treating conditional erasure as a universal reduction of possibility count.

## Native system

Four explicitly retained qubits: signal/path S, marker M, leaked record E, signal outcome recorder R. All begin in 0. Prepare S with H; marking is CNOT S->M. Leakage is exp(-i lambda Y_E) controlled by M=1, with conditional leaked-state overlap eta=cos(lambda).

The signal undergoes phase phi, H recombination, then actual CNOT S->R recording. Output distributions retain every final R,M,E outcome; S is also physically present but is a redundant copy of R at this final cut. No postselection mass is discarded. The marker readout is specified as Z after any marker Hadamard, implementing X reading of the original marker.

These are ideal scheduled gates with explicit environment, not an autonomous or thermodynamically complete apparatus. Only the small circuit analogue of quantum erasure is simulated, not the experimental optics of [Kim et al., A Delayed Choice Quantum Eraser](https://arxiv.org/abs/quant-ph/9903047). That experiment resolves opposite-phase interference in coincidence subsets; its interpretation should not be replaced by backwards alteration of a signal record.

Predeclared phases: 0,pi/2,pi,3pi/2. Leakage actions: 0,pi/6,pi/4,pi/2. Six treatments including the unmarked control produce96 profiles; unmarked repetitions across leakage settings are null controls.

## Interference and physical reversal

Visibility is (max P(R=0)-min P(R=0))/(max P(R=0)+min P(R=0)) across the four phase points. They include the exact extrema of these sinusoidal laws.

| Treatment | No leaked copy | Partial leak lambda=pi/4 | Orthogonal leaked copy lambda=pi/2 |
|---|---:|---:|---:|
| Unmarked | 1 | 1 | 1 |
| Retain marking | 0 | 0 | 0 |
| Reverse original marker only | 1 | 0.707107 | 0 |
| Conditional eraser, all outcomes retained | 0 | 0 | 0 |
| Reverse leak interaction and marking | 1 | 1 | 1 |

The unmarked control omits both marking and leakage. Reversing all records means applying the actual inverse leakage gate before the inverse marking gate, while E is accessible. It is not tracing out or declaring E irrelevant.

After marker-only reversal, the marker is blank but the leaked copy has residual path distinguishability sin(lambda). The signal visibility is cos(lambda). Thus full leakage leaves no signal interference even though the original marker has been physically reset. Joint recovery makes the record states coincide and restores the full fringe.

## Conditional eraser and weights

Hadamard on M followed by its specified Z readout gives

\[
P(M=0)=P(M=1)=\tfrac12,
\]

\[
P(R=0\mid M=0)=\frac{1+\eta\cos\phi}{2},\qquad
P(R=0\mid M=1)=\frac{1-\eta\cos\phi}{2}.
\]

The weighted sum is P(R=0)=1/2 for every phase. The two conditional visibilities are eta:1 without leakage,0.866025 at lambda=pi/6,0.707107 at pi/4, and0 with an orthogonal inaccessible copy. Here inaccessible means not included in the erasing operation; E remains in the full state and the final joint output table.

At phi=0 without leakage, either conditioned subset has one signal outcome, but its weight is only1/2. The unconditioned signal breadth is2 and full output breadth is2. There is no whole-system collapse to one from selecting a subset. The entropy chain rule H(R,M)=H(M)+sum_m P(m)H(R|m) holds to4.45e-16.

An M-only Hadamard does not map its two orthogonal conditional states to the same state. Their optimal trace-distance distinguishability remains1; the chosen Z readout now has zero which-path distinguishability. This is why the eraser's conditional fringes do not imply global branch merging. These trace-distance diagnostics are not a new operational control budget or a lushness reward.

## Early versus delayed erasure

The early eraser acts on M before signal recombination and copying into R. The delayed version acts on M after that actual recording. Since these operations act on disjoint registers, the full final vectors agree exactly for every tested phase and leak setting. The already-recorded R marginal is unchanged by the delayed marker operation to1.67e-16.

Conditional correlations can be read later without changing earlier marginal statistics. The full circuit provides this directly; no retrocausal rule or replacement of the sufficient present is needed.

## Final output breadth is a readout, not the whole-history extent

At phi=0:

| Treatment | Leakage | Signal breadth | Joint R,M,E breadth |
|---|---|---:|---:|
| Unmarked | absent | 1 | 1 |
| Retained | absent | 2 | 4 |
| Coherent marker reversal | absent | 1 | 1 |
| Conditional eraser | absent | 2 | 2 |
| Marker reversal only | orthogonal copy | 2 | 4 |
| Conditional eraser | orthogonal copy | 2 | 8 |
| Reverse all records | orthogonal copy | 1 | 1 |

The eight joint outcomes in the copied conditional-eraser case arise in the specified physical output basis, including the complementary marker readout. They are not evidence of a generativity advantage or an intrinsic quantum extent8. Likewise, final breadth1 after reversal does not establish that the entire original-root coherent development has extent1.

The full global state stays pure in every treatment. Phase changes can change output breadth even with full coherence. Purity therefore does not select the output breadth or solve the whole-development extent question.

## Coherent-history checks

The runner expands the path at the marked cut and the final physical outputs, retaining the full complex decoherence matrix. Final-only and intermediate-resolved descriptions agree on the native final Born law to2.23e-16. The same common remaining unitary preserves inner products of the marked path branch vectors to1.67e-16; coherent reversal does not make orthogonal complete vectors literally identical. Interference at later output projections is retained through their cross terms.

Fresh propagation from the complete marked present equals propagation from the original root. It includes E; an environmentally reduced summary would be a different, potentially insufficient present.

## Consequence for the extent programme

The physical field correctly supports recording, partial recoherence, complete recoherence when all relevant records are reversed, and conditional fringe recovery with conserved mixture weights. A candidate measure must distinguish all of these from mathematical checkpoint insertion.

The user's coherent-one/classical-breadth limits can remain proposed boundary conditions for a specified continuation geometry. They cannot be implemented by replacing the whole process with a conditioned signal, global purity, or the blankness of one local marker. The original-root object retains the complete marking/erasure dynamics; a fresh root uses the actual coherent present after those operations.

This panel supplies a small fixed calibration suite for a future extent construction. It does not choose a canonical reference measure or establish the full original-root quantity follows1->2->1.

## Artifacts and validation

Source: omega_v2/finite/quantum_eraser.py. Runner: python -m omega_v2.validation.quantum_eraser_v0. Six targeted tests and Ruff passed. Maximum numerical check error1.34e-15. All96profiles obey analytic signal/conditional laws and normalization. Raw JSON remains ignored at results/local_runs/quantum_eraser_v0/results.json. No commit or push.
