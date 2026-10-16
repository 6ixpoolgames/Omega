# Quantum extent: tiny exact comparison v0

Date: 2026-10-07. Exploratory protocol, written before executing this probe.

Question: which simple readout respects effective possibilities **after
interference**, while reducing to ordinary weighted breadth for orthogonally
recorded classical alternatives? This is not a claim to derive universal extent.

Use one signal qubit S, one explicit marker E, a pure present |00>, and exact
unitaries. The interferometer is H_S, optional controlled marker rotation,
phase(phi) on S, H_S. The marker states have overlap eta. Perfect recording is
eta=0; no recording eta=1. An eraser additionally rotates E by H before its
final Z readout. Retain all outcomes; no postselection.

Expand amplitudes into histories with intermediate Z_S projectors and final
orthogonal output projectors. Intermediate projectors are resolutions of the
identity in a calculation, not physical measurements. Their branch vectors
v_a=C_a|00> give D_ab=<v_b|v_a>. Sum amplitudes when removing a checkpoint.

Compare:

1. Diagonal history breadth exp H(diag D), which drops interference.
2. Spectral breadth exp S(D), where trace D=1 for these projective families.
3. Record breadth exp H(q), where q_r=sum_{a,b in r} D_ab, using a declared
   orthogonal final record partition. Verify the grouped matrix is diagonal;
   reject an incompatible partition rather than renormalizing it.

Cases: phase 0, pi/2, pi; partial marking eta=0,.5,1; perfect marker read in
Z or X; signal alone versus full joint records. Also compare endpoint-only
expansion, intermediate Z, and Z then X expansions of the same physical circuit.
These refinements must leave recombined output probabilities unchanged.

Controls: independent classical product; history permutation; consistent unitary
coordinate change; inert blank ancilla; identity checkpoint; quantum grade-two
sum rule; recovery of direct Born output from summed branch vectors. A deliberately
nondecoherent grouping must be rejected. Global pure-state entropy remains zero
throughout and is reported separately from entropy of D.

Expected discrimination: the interferometer's output probabilities depend on
phase even when diagonal and spectral fine-history summaries do not. Recording
and erasing need full joint-outcome accounting. No claim that final-record
breadth exhausts complete-future extent, or that arbitrary choices of readers
define one universal answer. No gas comparison in this probe.

References: Sorkin, Quantum Mechanics as Quantum Measure Theory (1994),
https://arxiv.org/abs/gr-qc/9401003 ; Gell-Mann and Hartle, Alternative Decohering
Histories in Quantum Mechanics (1990; archived 2019),
https://arxiv.org/abs/1905.05859 .
