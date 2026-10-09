# Quantum extent: interference first, breadth afterward

2026-10-07. Twenty-nine exact two-qubit profiles; no simulation sampling,
chemistry changes, gas comparison, or adoption of a universal extent.

## Result

The decoherence functional is a suitable interference-retaining carrier.
Neither diagonal history entropy nor its matrix spectral entropy automatically
measures effective output possibilities after interference. Recombining amplitudes
within physically specified output alternatives before applying perplexity works
for those alternatives. It does not yet define full coherent continuation extent.

The object is a complex matrix/kernel indexed by pairs of histories, not a fixed
three-vector or one complex number:

    v_a = C_a psi
    D_ab = <v_b|v_a> = Tr(C_a rho C_b^dagger)
    mu(A) = sum_{a,b in A} D_ab

The diagonal stores individual history weights; off-diagonals store interference.
The quantum measure mu is real and nonnegative but generally neither additive
nor monotone under inclusion. D retains complex information beyond mu's real
set weights. A Bloch three-vector suffices for one qubit density matrix, not for
general multiqubit/multitime continuation.

## Circuit and readouts

Initial universal toy state |00> includes signal S and marker E. Apply H_S,
controlled marker rotation with overlap eta, phase(phi) on S, then H_S. The
eraser rotates E by H before its final computational readout. Global evolution
stays unitary and pure; final probabilities refer to specified projectors. No
extra measurement-device dynamics or macroscopic decoherence is simulated.

Fine history indices resolve the intermediate S path and final outputs. These
intermediate projectors expand amplitudes; no intermediate measurement is
physically inserted. Complete sums recover the untouched unitary circuit.

Candidates:

- Diagonal: exp H(diag D). Drops interference; equivalent to the outcome
  distribution of the corresponding sequence of inserted projective measurements.
- Spectral: exp S(D), using trace D=1 for these exhaustive projective families.
  This is entropy of the history Gram matrix, not of the actual global state.
- Record: sum D coherently within each final alternative r, giving q_r. Check
  grouped off-diagonal entries vanish, then exp H(q). The code uses the sufficient
  medium-decoherence condition. It does not claim this is the weakest possible
  consistency condition. A general incompatible grouping is rejected.

| Physical circuit / final readout | Phase | Diagonal breadth | Spectral breadth | Record breadth |
|---|---:|---:|---:|---:|
| No marker; signal Z | 0 | 4 | 2 | 1 |
| No marker; signal Z | pi/2 | 4 | 2 | 2 |
| No marker; signal Z | pi | 4 | 2 | 1 |
| Partial marker eta=.5; signal Z | 0 | 4 | 3.509531 | 1.754765 |
| Perfect marker; signal Z only | any tested | 4 | 4 | 2 |
| Perfect marker; joint S,Z_E | any tested | 4 | 4 | 4 |
| Perfect marker; joint S,X_E eraser | 0 | 8 | 4 | 2 |
| Perfect marker; joint S,X_E eraser | pi/2 | 8 | 4 | 4 |
| Perfect marker; joint S,X_E eraser | pi | 8 | 4 | 2 |

Signal probabilities are ((1+eta*cos(phi))/2, (1-eta*cos(phi))/2).
For the perfect-marker eraser, each marker outcome has probability .5;
joint breadth is 2 exp H((cos^2(phi/2), sin^2(phi/2))). Conditional opposite
fringes are retained with their proper weights; the unconditioned signal is
uniform. No retrocausal change or deletion of unwanted outcomes is involved.

In particular, an eraser block's spectral eigenvalue is the sum of its fine
diagonal weights, NOT its coherently summed output probability. Confusing these
would falsely make spectral entropy agree with record breadth in this test.

## Representation and probability checks

For the same unmarked phase-zero circuit, endpoint-only amplitude expansion gives
(diagonal,spectral,record)=(1,1,1). Resolving an unmeasured intermediate Z gives
(4,2,1). Resolving Z then X gives (4,2,1) here, with additional zero histories.
Thus changing the calculational history family changes the first two summaries
without changing the circuit or final record law. It does not demonstrate a
change in physical possibility. No claim of invariance to arbitrary *physical*
intermediate measurements is made.

Explicit destructive-interference witness: one contribution to signal output1
has mu=.25; its union with the other contribution has mu=0. The full exhaustive
family has mu=1. Therefore ordinary monotone set-volume arithmetic cannot simply
be applied to mu. Effective breadth must be extracted with an additional rule.

Maximum direct-Born discrepancy: 2.22e-16. Maximum amplitude reconstruction
error: 1.11e-16. Trace and full-family normalization errors: 6.66e-16.
Global state effective rank remains1 throughout.

Five focused tests pass, including analytical phase/marker/eraser laws, quantum
grade-two additivity, rejection of a nondecoherent partition, consistent unitary
coordinate changes, history permutation, inert blank ancilla, identity checkpoint,
classical recovery and independent-product multiplicativity. Focused lint passes.
Tests distinguish changing the whole description's basis from changing a physical
reader relative to the state. An independent small-agent audit was corrected
against explicit branch-vector products before reporting these results.

## Recommendation and remaining problem

Keep the present quantum state and physical evolution intact; use D as the
finite-history interference carrier. Carry the declared physical alternatives
with it. Quantum measure theory is useful here because it encodes recombination
without treating fine coherent paths as independent classical branches.

Use record breadth as a calibrated readout, not a replacement of the user's
complete-future target by endpoint entropy. Where physical records retain full
history alternatives, it recovers full-history classical perplexity. Where paths
remain coherent, this test provides no canonical scalar for their total extent.
The full carrier retains that coherent structure even when a readout does not.

Next small test: two successive branching episodes with an explicit record
memory. Compare retained first records, coherent uncomputation of them, and
transfer into an explicit environment. Apply the same rule to joint future
records across cuts. This tests classical chain-rule recovery, distinction between
recombination and merely ignoring a record, and dependence on physical recording
architecture. Do not sum incompatible readout entropies or maximize over arbitrary
readers/ancillas. Which physically supplied family should define the universal
extent, or whether a coherent extension can avoid such a choice, remains open.

Sources: [Sorkin (1994)](https://arxiv.org/abs/gr-qc/9401003),
[Gell-Mann and Hartle (1990; archived 2019)](https://arxiv.org/abs/1905.05859).
The numbers above are from this probe, not claims attributed to those papers.

Code: `omega_v2/finite/quantum_extent.py`;
runner: `python -m omega_v2.validation.quantum_extent_v0`;
tests: `tests/test_quantum_extent.py`.
Raw results stay local at `results/local_runs/quantum_extent_v0/results.json`.
No commit or push requested/performed.
