# Explicit quantum eraser v0: protocol

2026-10-08. Written before execution. User requested the physical eraser test after the coherence-limit audit. No new extent formula is proposed.

Four qubits: signal/path S, marker M, possible leaked copy E, and signal outcome recorder R. Begin all zero, prepare S with H, mark with CNOT S->M. Leak strength lambda is controlled exp(-i lambda Y_E) conditioned on M=1, so leaked record overlap eta=cos(lambda). All degrees remain in the pure native state. Gates are ideal externally scheduled operations; no autonomous resource/energy claim.

Run six actual treatments:
1. Unmarked control (mark and leak absent).
2. Retain marking and any leak.
3. Reverse the original S->M marking, leaving any leaked copy E untouched.
4. Conditional eraser: H on M, then signal phase phi, signal H and actual CNOT S->R recording.
5. Delayed conditional eraser: the same H on M occurs after signal phase/recombination/recording into R.
6. Recover all: invert the leakage interaction, then invert marking before phase/recombination/recording.

All final R,M,E outcomes are retained. The marker's Z output after H implements an X-basis marker readout in the conditional eraser. Conditional subsets are always accompanied by their physical weights; no successful-subset renormalization is used as whole-system breadth.

Predeclared panel: lambda=0,pi/6,pi/4,pi/2 and phi=0,pi/2,pi,3pi/2; 96 exact profiles. Duplicate unmarked controls across lambda are explicit null checks.

Analytic expectations:
- Unmarked and full recovery: P(R=0)=(1+cos(phi))/2.
- Retained and either conditional eraser: P(R=0)=1/2.
- Reverse marking only: P(R=0)=(1+eta cos(phi))/2.
- Conditional eraser: P(M=m)=1/2; P(R=0|M=0/1)=(1+-eta cos(phi))/2. Weighted conditional mixture recovers unconditional1/2.
- Early and delayed marker readout operations commute with signal recombination/recording, giving the same full final state; no change to already recorded marginal R.

Report unconditional signal visibility, each conditional fringe visibility, signal/marker/leak joint Born distributions and breadth, conditional weights and chain-rule reconstruction. Also report conditional path-record trace distance on ME and distinguishability under the specified M-Z readout. An M-only unitary preserves optimal distinguishability of orthogonal marker states even when the chosen M readout erases which-path information; do not call this global branch merging.

History diagnostic: expand the source/path at the marked cut and final physical outputs, retaining full complex D; compare final-only expansion to show the same final Born law. Full common unitaries preserve the Gram matrix of the two path branch vectors before final projection. Check this explicitly. Fresh propagation from the complete marked present must reproduce the remaining evolution. Discarding E is never a physical deletion.

No expected universal lushness ranking or literal whole-history1->2->1 asserted. Distinguish coherent reversal from conditional quantum erasure and from reversing only one of several copies. Raw files ignored locally; no push.
